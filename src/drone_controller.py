"""
ASTROPATH - Drone Controller Module
Handles drone video streaming, telemetry, and ground coordinate projection
"""

import cv2
import numpy as np
import logging
import time
import math
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)


class DroneController:
    """Controller for drone video streaming and telemetry"""
    
    def __init__(self, stream_url=None, telemetry_source='simulation'):
        """
        Initialize drone controller
        
        Args:
            stream_url: Video stream URL (RTSP, UDP, HTTP, or file path)
            telemetry_source: 'mavlink', 'manual', or 'simulation'
        """
        self.stream_url = stream_url or config.DRONE_STREAM_URL
        self.telemetry_source = telemetry_source or config.DRONE_TELEMETRY_SOURCE
        
        self.cap = None
        self.connected = False
        
        # Telemetry data
        self.telemetry = {
            'latitude': 17.6599,  # Default: Solapur
            'longitude': 75.9064,
            'altitude': config.DRONE_DEFAULT_ALTITUDE,
            'heading': 0.0,
            'speed': 0.0,
            'timestamp': datetime.now()
        }
        
        # Camera parameters
        self.camera_params = {
            'fov_h': config.DRONE_CAMERA_FOV_HORIZONTAL,
            'fov_v': config.DRONE_CAMERA_FOV_VERTICAL,
            'resolution': config.DRONE_CAMERA_RESOLUTION,
            'gimbal_angle': config.DRONE_GIMBAL_ANGLE
        }
        
        logger.info(f"Drone controller initialized: {self.stream_url}")
    
    def connect(self):
        """Connect to drone video stream"""
        try:
            logger.info(f"Connecting to drone stream: {self.stream_url}")
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                logger.error("Failed to open video stream")
                return False
            
            self.connected = True
            
            # Get actual resolution
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.camera_params['resolution'] = (width, height)
            
            logger.info(f"✓ Connected to drone stream ({width}x{height})")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from drone"""
        if self.cap:
            self.cap.release()
        self.connected = False
        logger.info("Disconnected from drone")
    
    def is_connected(self):
        """Check if connected to drone"""
        return self.connected and self.cap is not None and self.cap.isOpened()
    
    def read_frame(self):
        """
        Read a frame from drone video stream
        
        Returns:
            (success, frame) tuple
        """
        if not self.is_connected():
            return False, None
        
        return self.cap.read()
    
    def get_telemetry(self):
        """
        Get current drone telemetry
        
        Returns:
            Dictionary with telemetry data
        """
        if self.telemetry_source == 'mavlink':
            return self._get_mavlink_telemetry()
        elif self.telemetry_source == 'simulation':
            return self._get_simulated_telemetry()
        else:
            return self.telemetry
    
    def _get_mavlink_telemetry(self):
        """Get telemetry from MAVLink (real drone)"""
        try:
            # Import MAVLink library
            from pymavlink import mavutil
            
            # Connect to MAVLink (if not already connected)
            if not hasattr(self, 'mav_connection'):
                self.mav_connection = mavutil.mavlink_connection(
                    config.DRONE_MAVLINK_CONNECTION
                )
                logger.info("Connected to MAVLink")
            
            # Request data stream
            self.mav_connection.mav.request_data_stream_send(
                self.mav_connection.target_system,
                self.mav_connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                1, 1
            )
            
            # Get latest position
            msg = self.mav_connection.recv_match(
                type='GLOBAL_POSITION_INT',
                blocking=False
            )
            
            if msg:
                self.telemetry = {
                    'latitude': msg.lat / 1e7,
                    'longitude': msg.lon / 1e7,
                    'altitude': msg.relative_alt / 1000.0,
                    'heading': msg.hdg / 100.0,
                    'speed': math.sqrt(msg.vx**2 + msg.vy**2) / 100.0,
                    'timestamp': datetime.now()
                }
            
            return self.telemetry
            
        except ImportError:
            logger.warning("pymavlink not installed, using simulation")
            return self._get_simulated_telemetry()
        except Exception as e:
            logger.error(f"MAVLink error: {e}")
            return self.telemetry
    
    def _get_simulated_telemetry(self):
        """Get simulated telemetry (for testing)"""
        # Simulate slight movement
        self.telemetry['timestamp'] = datetime.now()
        # Could add small random variations here for testing
        return self.telemetry
    
    def set_telemetry(self, lat, lon, alt, heading=0, speed=0):
        """Manually set telemetry (for testing or manual input)"""
        self.telemetry = {
            'latitude': lat,
            'longitude': lon,
            'altitude': alt,
            'heading': heading,
            'speed': speed,
            'timestamp': datetime.now()
        }
    
    def pixel_to_ground_coords(self, pixel_x, pixel_y, frame_width, frame_height):
        """
        Convert pixel coordinates to ground GPS coordinates
        
        Args:
            pixel_x: X pixel coordinate
            pixel_y: Y pixel coordinate
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
            
        Returns:
            (latitude, longitude) of ground position
        """
        telemetry = self.get_telemetry()
        altitude = telemetry['altitude']
        drone_lat = telemetry['latitude']
        drone_lon = telemetry['longitude']
        heading = math.radians(telemetry['heading'])
        
        # Calculate ground coverage
        fov_h = math.radians(self.camera_params['fov_h'])
        fov_v = math.radians(self.camera_params['fov_v'])
        
        # Ground width and height covered
        ground_width = 2 * altitude * math.tan(fov_h / 2)
        ground_height = 2 * altitude * math.tan(fov_v / 2)
        
        # Normalize pixel coordinates to -0.5 to 0.5
        norm_x = (pixel_x / frame_width) - 0.5
        norm_y = (pixel_y / frame_height) - 0.5
        
        # Calculate offset in meters
        offset_x = norm_x * ground_width
        offset_y = norm_y * ground_height
        
        # Rotate by heading
        rotated_x = offset_x * math.cos(heading) - offset_y * math.sin(heading)
        rotated_y = offset_x * math.sin(heading) + offset_y * math.cos(heading)
        
        # Convert to lat/lon offset
        # Approximate: 1 degree latitude ≈ 111,320 meters
        # 1 degree longitude ≈ 111,320 * cos(latitude) meters
        lat_offset = rotated_y / 111320.0
        lon_offset = rotated_x / (111320.0 * math.cos(math.radians(drone_lat)))
        
        ground_lat = drone_lat + lat_offset
        ground_lon = drone_lon + lon_offset
        
        return ground_lat, ground_lon
    
    def get_ground_coverage(self):
        """
        Calculate ground area coverage
        
        Returns:
            (width_meters, height_meters) of ground coverage
        """
        altitude = self.get_telemetry()['altitude']
        fov_h = math.radians(self.camera_params['fov_h'])
        fov_v = math.radians(self.camera_params['fov_v'])
        
        ground_width = 2 * altitude * math.tan(fov_h / 2)
        ground_height = 2 * altitude * math.tan(fov_v / 2)
        
        return ground_width, ground_height
    
    def plan_survey_mission(self, start_lat, start_lon, area_width, area_length, 
                           altitude=None, overlap=None):
        """
        Plan grid survey mission
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            area_width: Survey area width in meters
            area_length: Survey area length in meters
            altitude: Flight altitude (uses default if None)
            overlap: Overlap percentage (uses default if None)
            
        Returns:
            List of waypoints [(lat, lon, alt), ...]
        """
        altitude = altitude or config.DRONE_SURVEY_ALTITUDE
        overlap = overlap or config.DRONE_SURVEY_OVERLAP
        
        # Calculate grid spacing
        ground_width, ground_height = self.get_ground_coverage()
        spacing_width = ground_width * (1 - overlap / 100)
        spacing_length = ground_height * (1 - overlap / 100)
        
        # Calculate number of passes
        num_passes_width = int(area_width / spacing_width) + 1
        num_passes_length = int(area_length / spacing_length) + 1
        
        waypoints = []
        
        for i in range(num_passes_length):
            for j in range(num_passes_width):
                # Calculate offset
                offset_x = j * spacing_width
                offset_y = i * spacing_length
                
                # Convert to lat/lon
                lat = start_lat + (offset_y / 111320.0)
                lon = start_lon + (offset_x / (111320.0 * math.cos(math.radians(start_lat))))
                
                waypoints.append((lat, lon, altitude))
        
        logger.info(f"Planned mission: {len(waypoints)} waypoints")
        return waypoints


def test_drone_connection(url):
    """Test drone video stream connection"""
    print(f"\n🚁 Testing drone connection: {url}\n")
    
    drone = DroneController(stream_url=url)
    
    if not drone.connect():
        print("❌ Connection failed")
        return False
    
    print("✓ Connected successfully")
    
    # Test frame reading
    ret, frame = drone.read_frame()
    if ret and frame is not None:
        h, w = frame.shape[:2]
        print(f"✓ Frame received: {w}x{h}")
        
        # Show telemetry
        telemetry = drone.get_telemetry()
        print(f"\nTelemetry:")
        print(f"  Position: ({telemetry['latitude']:.6f}, {telemetry['longitude']:.6f})")
        print(f"  Altitude: {telemetry['altitude']:.1f}m")
        print(f"  Heading: {telemetry['heading']:.1f}°")
        
        # Show ground coverage
        gw, gh = drone.get_ground_coverage()
        print(f"\nGround Coverage:")
        print(f"  {gw:.1f}m × {gh:.1f}m")
    else:
        print("❌ Failed to receive frame")
        drone.disconnect()
        return False
    
    drone.disconnect()
    print("\n✓ Test successful")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = input("Enter drone stream URL: ").strip()
    
    if test_url:
        test_drone_connection(test_url)
    else:
        print("Usage: python drone_controller.py <stream_url>")
