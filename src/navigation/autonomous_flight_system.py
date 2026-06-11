"""
ASTROPATH - Autonomous Flight System Simulation
Implements the end-to-end software architecture including:
1. Mission Planner (Destination Input)
2. Flight Controller & Sensor Suite (GPS, IMU, Altimeter)
3. Sensor Fusion Engine (Kalman Filter)
4. Environment Perception Layer (Bird, Wire, Tree, Pothole Detection)
5. Threat Assessment & Obstacle Classification
6. Dynamic Path Planning AI (Route Optimisation, Re-routing, Emergency Landing)
7. Battery & Weather Safety Decision Engine
8. Target Delivery Control
"""

import math
import time
import random
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import modularised architecture components
from src.fusion.sensor_fusion import SensorFusionEngine
from src.battery.battery_monitor import BatteryWeatherMonitor, SafetyDecisionEngine

# Configure logging for professional terminal output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ASTROPATH_Core")

class MissionPlanner:
    """Ingests mission destinations and generates reference navigation routes."""
    def __init__(self, start_coords=(17.6599, 75.9064), target_coords=(17.6682, 75.9125)):
        self.start_coords = start_coords
        self.target_coords = target_coords
        logger.info(f"Mission Planner initialized. Start: {start_coords} | Target: {target_coords}")

    def generate_waypoints(self, num_points=10, cruise_alt=15.0):
        """Generates linear segment waypoints from start to target coordinates."""
        waypoints = []
        lat_step = (self.target_coords[0] - self.start_coords[0]) / (num_points - 1)
        lon_step = (self.target_coords[1] - self.start_coords[1]) / (num_points - 1)
        
        for i in range(num_points):
            lat = self.start_coords[0] + (lat_step * i)
            lon = self.start_coords[1] + (lon_step * i)
            # Takeoff at waypoint 0, cruise otherwise, land at final
            alt = 0.0 if i == 0 else (0.0 if i == num_points - 1 else cruise_alt)
            waypoints.append({'lat': lat, 'lon': lon, 'alt': alt})
            
        logger.info(f"Generated {len(waypoints)} mission waypoints successfully.")
        return waypoints


class SensorSuite:
    """Simulates physical sensor outputs with realistic noise/errors."""
    def __init__(self, true_lat, true_lon, true_alt):
        self.true_lat = true_lat
        self.true_lon = true_lon
        self.true_alt = true_alt
        
        # Noise parameters (Standard Deviations)
        self.gps_noise_std = 0.00005  # ~5 meters offset
        self.altimeter_noise_std = 0.3  # ~30 cm offset
        self.imu_gyro_noise_std = 0.02  # rad/s offset

    def read_sensors(self, true_lat, true_lon, true_alt, velocity):
        """Reads noisy sensors based on the actual true physical state of the drone."""
        self.true_lat = true_lat
        self.true_lon = true_lon
        self.true_alt = true_alt
        
        # Add normal Gaussian noise
        noisy_lat = self.true_lat + random.normalvariate(0, self.gps_noise_std)
        noisy_lon = self.true_lon + random.normalvariate(0, self.gps_noise_std)
        noisy_alt = self.true_alt + random.normalvariate(0, self.altimeter_noise_std)
        
        # Simulating IMU readings
        noisy_pitch = random.normalvariate(0, 2.0)  # degrees
        noisy_roll = random.normalvariate(0, 2.0)
        noisy_yaw_rate = velocity * 0.05 + random.normalvariate(0, self.imu_gyro_noise_std)
        
        return {
            'gps': {'lat': noisy_lat, 'lon': noisy_lon},
            'altimeter': {'alt': noisy_alt},
            'imu': {'pitch': noisy_pitch, 'roll': noisy_roll, 'yaw_rate': noisy_yaw_rate}
        }


# SensorFusionEngine is imported from src.fusion.sensor_fusion


class EnvironmentPerceptionLayer:
    """Simulates AI vision perception models detecting birds, wires, trees, and potholes."""
    def __init__(self):
        self.labels = ["Bird", "Wire", "Tree", "Pothole"]

    def process_camera_frame(self, drone_alt, step):
        """Returns detected objects with class names, confidence levels, and spatial offsets."""
        detections = []
        
        # Condition simulation depending on simulated progress step
        if step == 2:
            # Simulate a tree branches blocking the path
            detections.append({'label': 'Tree', 'confidence': 0.94, 'x_offset': 1.2, 'y_offset': 5.0})
        elif step == 4:
            # Simulate a low-hanging electrical wire hazard
            detections.append({'label': 'Wire', 'confidence': 0.89, 'x_offset': 0.1, 'y_offset': 3.5})
        elif step == 6:
            # Simulate a flock of birds crossing the flight vector
            detections.append({'label': 'Bird', 'confidence': 0.91, 'x_offset': -2.5, 'y_offset': 6.0})
            
        # Potholes can be scanned on the road throughout the cruise
        if 1 < step < 9 and random.random() < 0.4:
            detections.append({'label': 'Pothole', 'confidence': 0.96, 'x_offset': random.uniform(-3, 3), 'y_offset': random.uniform(2, 6)})
            
        return detections


class ThreatAssessment:
    """Classifies environmental detections and evaluates threat levels (0.0 to 1.0)."""
    @staticmethod
    def evaluate(detections):
        highest_threat = 0.0
        primary_threat_label = None
        
        for det in detections:
            label = det['label']
            confidence = det['confidence']
            y_dist = det['y_offset']  # Distance in front of drone in meters
            
            # Wires and Trees directly in front are high threats
            if label == 'Wire' and y_dist < 4.0:
                threat = 0.9 * confidence
            elif label == 'Tree' and y_dist < 6.0:
                threat = 0.75 * confidence
            elif label == 'Bird' and y_dist < 8.0:
                threat = 0.6 * confidence
            else:
                threat = 0.1  # Potholes are inspection targets, not collision threats
                
            if threat > highest_threat:
                highest_threat = threat
                primary_threat_label = label
                
        return highest_threat, primary_threat_label


# BatteryWeatherMonitor is imported from src.battery.battery_monitor


class DynamicPathPlanningAI:
    """Handles routing optimisations, obstacle bypasses, and emergency landing paths."""
    def __init__(self, default_alt=15.0):
        self.default_alt = default_alt

    def compute_bypass(self, drone_pos, threat_label, raw_waypoint):
        """Calculates a local 3D detour to bypass trees, wires, or birds."""
        logger.info(f"🔄 Re-routing Engine activated due to: {threat_label} obstacle.")
        
        detour = {}
        if threat_label == 'Tree':
            # Detour horizontally to the right
            detour['lat'] = raw_waypoint['lat'] + 0.00004
            detour['lon'] = raw_waypoint['lon'] + 0.00004
            detour['alt'] = self.default_alt
            logger.info("Detour Action: Lateral bypass (+4m North-East deviation).")
        elif threat_label == 'Wire':
            # Detour vertically (climb over wire)
            detour['lat'] = raw_waypoint['lat']
            detour['lon'] = raw_waypoint['lon']
            detour['alt'] = self.default_alt + 6.0  # Climb 6 meters higher
            logger.info("Detour Action: Vertical bypass (+6m climb profile).")
        else:
            # Slow down and wait for birds to pass
            detour['lat'] = drone_pos['lat']
            detour['lon'] = drone_pos['lon']
            detour['alt'] = self.default_alt
            logger.info("Detour Action: Hover-in-place state activated (wait for clearing).")
            
        return detour

    def find_safe_landing_spot(self, current_lat, current_lon):
        """Identifies a clear flat coordinate for an emergency landing."""
        logger.warning("🚨 Emergency Landing AI locating nearest safe landing zone (LZ)...")
        # Offset coordinates slightly to simulate nearby open park/roadway landing site
        lz_lat = current_lat + 0.00002
        lz_lon = current_lon - 0.00002
        logger.info(f"Safe LZ calculated at: ({lz_lat:.6f}, {lz_lon:.6f}). Beginning vertical descent.")
        return {'lat': lz_lat, 'lon': lz_lon, 'alt': 0.0}


# SafetyDecisionEngine is imported from src.battery.battery_monitor


class AutonomousFlightSystem:
    """The orchestration engine integrating all components to run simulated flights."""
    def __init__(self):
        # Instantiate architectural modules
        self.planner = MissionPlanner()
        self.sensor_suite = SensorSuite(17.6599, 75.9064, 0.0)
        self.fusion_engine = SensorFusionEngine(17.6599, 75.9064, 0.0)
        self.perception = EnvironmentPerceptionLayer()
        self.safety_engine = SafetyDecisionEngine()
        self.path_planner = DynamicPathPlanningAI()
        self.battery_weather = BatteryWeatherMonitor()
        
        # Drone physical state tracking
        self.true_state = {'lat': 17.6599, 'lon': 75.9064, 'alt': 0.0}
        self.fused_state = {'lat': 17.6599, 'lon': 75.9064, 'alt': 0.0}
        self.flight_mode = "TAKEOFF"
        self.velocity = 0.0

    def run_mission_loop(self):
        """Simulates the entire flight step-by-step, running diagnostic logs at each phase."""
        logger.info("=========================================================")
        logger.info("🚀 ASTROPATH AUTONOMIC FLIGHT MISSION STARTING")
        logger.info("=========================================================")
        
        waypoints = self.planner.generate_waypoints()
        
        for step in range(len(waypoints)):
            target_wp = waypoints[step]
            logger.info("")
            logger.info(f"--- [MISSION FLIGHT STEP {step + 1}/{len(waypoints)}] Mode: {self.flight_mode} ---")
            
            # 1. Update Battery and Weather Conditions
            conditions = self.battery_weather.update_sensors(step)
            logger.info(f"Monitor Stats - Battery: {conditions['battery']:.1f}% | Wind: {conditions['wind_speed']:.1f} kts | Rain: {conditions['rain_rate']:.1f} mm/h")
            
            # 2. Simulate True Flight Mechanics
            if self.flight_mode == "TAKEOFF":
                self.true_state['alt'] = 15.0
                self.velocity = 2.0
                self.flight_mode = "CRUISE"
                logger.info("Flight Controller: Takeoff complete. Holding altitude 15.0m.")
            elif self.flight_mode == "CRUISE":
                self.true_state['lat'] = target_wp['lat']
                self.true_state['lon'] = target_wp['lon']
                self.velocity = 5.0
            
            # 3. Read Sensors & Perform Kalman Sensor Fusion
            raw_sensors = self.sensor_suite.read_sensors(
                self.true_state['lat'], self.true_state['lon'], self.true_state['alt'], self.velocity
            )
            logger.debug(f"Raw GPS: ({raw_sensors['gps']['lat']:.6f}, {raw_sensors['gps']['lon']:.6f})")
            
            self.fused_state = self.fusion_engine.fuse(raw_sensors)
            logger.info(f"Sensor Fusion State: Lat: {self.fused_state['lat']:.6f} | Lon: {self.fused_state['lon']:.6f} | Alt: {self.fused_state['alt']:.2f}m")
            
            # 4. Perception Layer Processing (YOLO/Classifier)
            detections = self.perception.process_camera_frame(self.fused_state['alt'], step)
            if detections:
                logger.info(f"AI Vision Layer: Detected {len(detections)} objects.")
                for det in detections:
                    logger.info(f"  └─ Label: {det['label']} | Confidence: {det['confidence']*100:.1f}% | Spatial Offset: (x: {det['x_offset']}m, y: {det['y_offset']}m)")
            else:
                logger.info("AI Vision Layer: Scan clear. No environmental obstacles.")
                
            # 5. Threat Assessment & Path Planning
            threat_level, threat_label = ThreatAssessment.evaluate(detections)
            if threat_level > 0.5:
                logger.warning(f"Threat Assessment: Collision Risk Alert! Danger Score: {threat_level:.2f} [{threat_label}]")
                # Plan local bypass
                bypass_target = self.path_planner.compute_bypass(self.fused_state, threat_label, target_wp)
                self.true_state['lat'] = bypass_target['lat']
                self.true_state['lon'] = bypass_target['lon']
                self.true_state['alt'] = bypass_target['alt']
                logger.info(f"Autopilot Command: Adjusting heading/speed vectors to detours.")
                
            # 6. Safety Decision overrides
            safety_status = self.safety_engine.assess_safety(conditions)
            if safety_status != "NORMAL":
                if safety_status == "OVERRIDE_RTH_BATTERY":
                    self.flight_mode = "EMERGENCY_LANDING"
                    lz = self.path_planner.find_safe_landing_spot(self.fused_state['lat'], self.fused_state['lon'])
                    self.true_state = lz
                    logger.critical(f"Autopilot Override: Safety Decision Engine taking command. Navigating to Safe LZ.")
                elif safety_status in ["OVERRIDE_STABILISE_WIND", "OVERRIDE_STABILISE_RAIN"]:
                    logger.warning("Safety Decision Engine Override: Activating Auto-Stabilisation. Reducing velocity to 1.5m/s.")
                    self.velocity = 1.5
                    
            # 7. Check target delivery status
            if step == len(waypoints) - 1 and self.flight_mode != "EMERGENCY_LANDING":
                self.flight_mode = "DELIVERY"
                logger.info("🎯 Mission Target reached! Executing delivery container drop-off.")
                self.true_state['alt'] = 0.0
                self.flight_mode = "LANDED"
                
            if self.flight_mode == "EMERGENCY_LANDING" and self.true_state['alt'] == 0.0:
                logger.critical("🛑 Safety Override Landing Completed. System safe. Flight operations halted.")
                break
                
            time.sleep(0.1)  # Simulated tick delay
            
        if self.flight_mode == "LANDED":
            logger.info("=========================================================")
            logger.info("🏁 ASTROPATH MISSION COMPLETED SUCCESSFULLY")
            logger.info("=========================================================")
        else:
            logger.info("=========================================================")
            logger.critical("⚠️ MISSION ENDED VIA EMERGENCY SAFE LANDING OVERRIDE")
            logger.info("=========================================================")


if __name__ == "__main__":
    # Execute the flight simulator
    system = AutonomousFlightSystem()
    system.run_mission_loop()
