"""
ASTROPATH ESP32-CAM Module (esp32_camera.py)
Real-time video streaming from ESP32-CAM boards over WiFi
Supports multiple camera frames, JPEG capture, and resolution switching

Compatible Boards:
  - ESP32-CAM (OV2640 camera)
  - ESP32-S3-CAM (higher performance)
  - M5StickV / Sipeed MaixPy (alternative options)

Requirements:
  - ESP32-CAM board with WiFi enabled
  - MicroPython firmware or standard Arduino firmware
  - Camera streaming server running on ESP32 (e.g., CameraWebServer.ino)
"""

import urllib.request
import urllib.error
import cv2
import numpy as np
import threading
import time
import logging
from typing import Optional, Tuple
from datetime import datetime
from queue import Queue

logger = logging.getLogger(__name__)


class ESP32Camera:
    """
    Connect to and stream video from ESP32-CAM boards
    Handles MJPEG stream parsing and frame extraction
    """
    
    def __init__(self,
                 host: str = "192.168.1.100",
                 port: int = 80,
                 mjpeg_path: str = "/stream",
                 timeout: float = 10.0,
                 resolution: str = "1024x768"):
        """
        Initialize ESP32-CAM connection
        
        Args:
            host (str): IP address of ESP32-CAM (e.g., "192.168.1.100")
            port (int): Port number (default 80 for HTTP)
            mjpeg_path (str): Stream endpoint (usually /stream or /jpg or /mjpeg)
            timeout (float): Connection timeout in seconds
            resolution (str): "1024x768", "800x600", "640x480", etc.
        """
        self.host = host
        self.port = port
        self.mjpeg_path = mjpeg_path
        self.timeout = timeout
        self.resolution = resolution
        
        self.url = f"http://{host}:{port}{mjpeg_path}"
        self.connected = False
        self.stream = None
        self.current_frame = None
        self.frame_queue = Queue(maxsize=5)
        
        self._thread = None
        self._stop_event = threading.Event()
        
        logger.info(f"ESP32Camera initialized: {self.url}")
    
    def connect(self) -> bool:
        """
        Establish connection to ESP32-CAM stream
        
        Returns:
            bool: True if successfully connected, False otherwise
        """
        try:
            logger.info(f"Connecting to ESP32-CAM at {self.url}...")
            
            # Set timeout for urlopen
            self.stream = urllib.request.urlopen(
                self.url,
                timeout=self.timeout
            )
            
            self.connected = True
            logger.info(f"Connected to ESP32-CAM: {self.host}:{self.port}")
            
            # Start frame reading thread
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._read_stream, daemon=True)
            self._thread.start()
            
            return True
        
        except urllib.error.URLError as e:
            self.connected = False
            logger.error(f"Failed to connect to ESP32-CAM: {e}")
            return False
        except Exception as e:
            self.connected = False
            logger.error(f"Unexpected error connecting to ESP32-CAM: {e}")
            return False
    
    def _read_stream(self):
        """
        Background thread: Parse MJPEG stream and extract frames
        """
        if not self.stream:
            logger.warning("Stream not initialized")
            return
        
        bytes_buffer = b''
        
        try:
            while not self._stop_event.is_set():
                # Read chunk from stream
                chunk = self.stream.read(4096)
                if not chunk:
                    logger.warning("Stream ended (no more data)")
                    break
                
                bytes_buffer += chunk
                
                # Look for JPEG boundaries
                start_marker = b'\xff\xd8'  # JPEG start
                end_marker = b'\xff\xd9'    # JPEG end
                
                start_idx = bytes_buffer.find(start_marker)
                end_idx = bytes_buffer.find(end_marker)
                
                # Extract complete JPEG
                if start_idx >= 0 and end_idx > start_idx:
                    jpeg_data = bytes_buffer[start_idx:end_idx + 2]
                    bytes_buffer = bytes_buffer[end_idx + 2:]
                    
                    # Decode JPEG to frame
                    frame_array = np.frombuffer(jpeg_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        self.current_frame = frame
                        
                        # Put in queue if not full
                        try:
                            self.frame_queue.put_nowait(frame)
                        except:
                            pass  # Queue full, drop frame
        
        except Exception as e:
            logger.error(f"Error reading stream: {e}")
        
        finally:
            self.connected = False
            logger.info("Stream reading thread stopped")
    
    def get_frame(self, use_queue: bool = False) -> Optional[np.ndarray]:
        """
        Get latest frame from camera
        
        Args:
            use_queue (bool): If True, get oldest queued frame; if False, get latest
        
        Returns:
            np.ndarray: Frame as numpy array or None if no frame available
        """
        if use_queue:
            try:
                return self.frame_queue.get_nowait()
            except:
                return None
        else:
            return self.current_frame
    
    def capture_frame(self, filepath: str) -> bool:
        """
        Capture and save current frame as JPEG
        
        Args:
            filepath (str): Path to save image
        
        Returns:
            bool: True if successful, False otherwise
        """
        frame = self.get_frame()
        if frame is None:
            logger.warning("No frame available to capture")
            return False
        
        try:
            cv2.imwrite(filepath, frame)
            logger.info(f"Frame captured: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
            return False
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current frame resolution"""
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            return (w, h)
        return (0, 0)
    
    def set_resolution(self, resolution: str) -> bool:
        """
        Change ESP32-CAM resolution (requires control endpoint)
        
        Common resolutions:
          - "FRAMESIZE_UXGA" (1600x1200)
          - "FRAMESIZE_SXGA" (1280x1024)
          - "FRAMESIZE_XGA" (1024x768)
          - "FRAMESIZE_SVGA" (800x600)
          - "FRAMESIZE_VGA" (640x480)
          - "FRAMESIZE_CIF" (400x296)
          - "FRAMESIZE_QVGA" (320x240)
          - "FRAMESIZE_HQVGA" (240x176)
          - "FRAMESIZE_QQVGA" (160x120)
        
        Args:
            resolution (str): Resolution string
        
        Returns:
            bool: True if successful
        """
        try:
            # This requires a control endpoint on ESP32 (varies by firmware)
            control_url = f"http://{self.host}:{self.port}/control?var=framesize&val={resolution}"
            response = urllib.request.urlopen(control_url, timeout=5)
            self.resolution = resolution
            logger.info(f"Resolution changed to: {resolution}")
            return True
        except Exception as e:
            logger.warning(f"Failed to change resolution: {e}")
            return False
    
    def disconnect(self):
        """Close ESP32-CAM connection and stop threads"""
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
        
        self.connected = False
        logger.info("ESP32-CAM disconnected")
    
    def is_connected(self) -> bool:
        """Check connection status"""
        return self.connected
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class MultiCameraController:
    """
    Manage multiple ESP32-CAM devices for multi-angle coverage
    """
    
    def __init__(self):
        self.cameras = {}
        logger.info("MultiCameraController initialized")
    
    def add_camera(self, name: str, host: str, port: int = 80, mjpeg_path: str = "/stream") -> bool:
        """
        Add ESP32-CAM to controller
        
        Args:
            name (str): Unique camera identifier
            host (str): IP address of camera
            port (int): HTTP port
            mjpeg_path (str): Stream endpoint
        
        Returns:
            bool: True if successfully added and connected
        """
        try:
            camera = ESP32Camera(host=host, port=port, mjpeg_path=mjpeg_path)
            if camera.connect():
                self.cameras[name] = camera
                logger.info(f"Camera '{name}' added: {host}:{port}")
                return True
            else:
                logger.error(f"Failed to connect camera '{name}'")
                return False
        except Exception as e:
            logger.error(f"Error adding camera '{name}': {e}")
            return False
    
    def get_frame(self, camera_name: str) -> Optional[np.ndarray]:
        """Get frame from specific camera"""
        if camera_name in self.cameras:
            return self.cameras[camera_name].get_frame()
        return None
    
    def get_all_frames(self) -> dict:
        """Get frames from all connected cameras"""
        frames = {}
        for name, camera in self.cameras.items():
            frame = camera.get_frame()
            if frame is not None:
                frames[name] = frame
        return frames
    
    def disconnect_all(self):
        """Disconnect all cameras"""
        for name, camera in self.cameras.items():
            camera.disconnect()
        self.cameras.clear()
        logger.info("All cameras disconnected")
    
    def __len__(self):
        return len(self.cameras)


# ==================== Standalone Testing ====================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Connect to single ESP32-CAM
    print("ESP32-CAM Test (Press Ctrl+C to stop)...\n")
    
    try:
        # Change to your ESP32-CAM IP address
        camera = ESP32Camera(
            host="192.168.1.100",  # Update this!
            port=80,
            mjpeg_path="/stream"
        )
        
        if camera.connect():
            frame_count = 0
            
            while frame_count < 30:
                frame = camera.get_frame()
                
                if frame is not None:
                    frame_count += 1
                    print(f"Frame {frame_count}: {frame.shape}")
                    
                    # Display frame (optional)
                    # cv2.imshow("ESP32-CAM Stream", frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                    
                    # Save every 10th frame
                    if frame_count % 10 == 0:
                        camera.capture_frame(f"esp32_frame_{frame_count}.jpg")
                
                time.sleep(0.1)
            
            camera.disconnect()
            print("\nTest completed")
        
        else:
            print("Failed to connect to ESP32-CAM")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        camera.disconnect()
