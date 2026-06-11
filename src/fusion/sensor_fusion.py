"""
ASTROPATH - Sensor Fusion Engine
Uses a 3D Kalman Filter to fuse noisy GPS, Altimeter, and IMU data.
"""

import logging

logger = logging.getLogger("ASTROPATH_Fusion")

class SensorFusionEngine:
    """Fuses noisy GPS, Altimeter, and IMU data using a simplified Kalman Filter."""
    def __init__(self, initial_lat, initial_lon, initial_alt):
        # State estimation [lat, lon, alt]
        self.state = [initial_lat, initial_lon, initial_alt]
        # Estimation Covariance
        self.P = [1e-8, 1e-8, 0.1]
        # Measurement uncertainty
        self.R = [5e-9, 5e-9, 0.09]  # GPS and altimeter variance
        # Process uncertainty
        self.Q = [1e-10, 1e-10, 0.01]

    def fuse(self, raw_measurements):
        """Performs Predict and Correct steps of the Kalman Filter."""
        gps = raw_measurements['gps']
        alt = raw_measurements['altimeter']['alt']
        
        # Predict (Simplified: assuming near constant position + process noise Q)
        for i in range(3):
            self.P[i] += self.Q[i]
            
        # Correct (Update step using measurement models)
        # 0: Latitude
        k_lat = self.P[0] / (self.P[0] + self.R[0])
        self.state[0] = self.state[0] + k_lat * (gps['lat'] - self.state[0])
        self.P[0] = (1 - k_lat) * self.P[0]
        
        # 1: Longitude
        k_lon = self.P[1] / (self.P[1] + self.R[1])
        self.state[1] = self.state[1] + k_lon * (gps['lon'] - self.state[1])
        self.P[1] = (1 - k_lon) * self.P[1]
        
        # 2: Altitude
        k_alt = self.P[2] / (self.P[2] + self.R[2])
        self.state[2] = self.state[2] + k_alt * (alt - self.state[2])
        self.P[2] = (1 - k_alt) * self.P[2]
        
        return {
            'lat': self.state[0],
            'lon': self.state[1],
            'alt': self.state[2]
        }
