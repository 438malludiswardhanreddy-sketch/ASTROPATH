"""
ASTROPATH - Battery & Weather Monitor
Monitors battery status, rain, wind, and handles safety overrides.
"""

import logging

logger = logging.getLogger("ASTROPATH_Safety")

class BatteryWeatherMonitor:
    """Monitors battery capacity, weather parameters, and issues safety flags."""
    def __init__(self, initial_battery=100.0, wind_speed=12.0, rain_rate=0.0):
        self.battery = initial_battery
        self.wind_speed = wind_speed  # Knots
        self.rain_rate = rain_rate  # mm/hour

    def update_sensors(self, step):
        """Simulates changes in battery and weather as time progresses."""
        # Standard battery drain per step
        self.battery -= 4.5
        
        # Simulate dynamic environmental changes at specific steps
        if step == 5:
            self.wind_speed = 28.5  # Critical Wind Threshold
            logger.warning("💨 Wind speed sensor reporting high gust: 28.5 knots!")
        elif step == 7:
            self.wind_speed = 12.0
            self.rain_rate = 18.0   # Heavy Rain Threshold
            logger.warning("🌧️ Rain rate sensor reporting heavy downpour: 18.0 mm/h!")
        elif step == 8:
            self.rain_rate = 0.0
            self.battery = 12.0     # Critical Battery Threshold
            logger.warning("🔋 Battery capacity dropped to critical levels: 12.0%!")
            
        return {
            'battery': self.battery,
            'wind_speed': self.wind_speed,
            'rain_rate': self.rain_rate
        }


class SafetyDecisionEngine:
    """Analyse diagnostic data and override flight controller states in case of safety breaches."""
    def __init__(self):
        # Threshold constants
        self.min_battery_threshold = 15.0  # %
        self.max_wind_threshold = 25.0     # knots
        self.max_rain_threshold = 15.0     # mm/h

    def assess_safety(self, battery_status):
        """Determines if safety overrides are required."""
        bat = battery_status['battery']
        wind = battery_status['wind_speed']
        rain = battery_status['rain_rate']
        
        if bat < self.min_battery_threshold:
            logger.critical("⚠️ SAFETY INTERVENTION: Critical Low Battery!")
            return "OVERRIDE_RTH_BATTERY"
        elif wind > self.max_wind_threshold:
            logger.critical("⚠️ SAFETY INTERVENTION: High wind velocity limit exceeded!")
            return "OVERRIDE_STABILISE_WIND"
        elif rain > self.max_rain_threshold:
            logger.critical("⚠️ SAFETY INTERVENTION: Extreme precipitation detected!")
            return "OVERRIDE_STABILISE_RAIN"
            
        return "NORMAL"
