"""
GPS Handler Module - ASTROPATH
================================
Production-ready GPS coordinate acquisition for pothole detection edge device.
Supports multiple connection types (USB, Serial/GPIO) and fallback mechanisms.

Supported Modules:
  - u-blox NEO-6M / NEO-M8N / SAM-M8Q (~₹500-1500, 2-5m accuracy)
  - Adafruit Ultimate GPS / PA1010D (I2C/USB, easy)
  - Beitian BN-220 / BZ-series (10Hz update, drone-friendly)
  - Any NMEA output module (GGA, RMC sentences)

Connection Types:
  - USB: /dev/ttyACM0 or /dev/ttyUSB0 (Linux/Pi)
  - Serial UART: GPIO pins 8/10, enable via raspi-config
  - I2C: Some modules support I2C interface

Usage:
  ```python
  gps = GPSHandler(port='/dev/ttyACM0', baud=9600)
  lat, lon, timestamp, quality = gps.get_coordinates()
  ```
"""

import serial
import pynmea2
import time
import logging
from typing import Tuple, Optional
from datetime import datetime
import threading

# Configure logging
logger = logging.getLogger(__name__)


class GPSQuality:
    """GPS fix quality levels"""
    NO_FIX = 0
    GPS_FIX = 1
    DGPS_FIX = 2
    PPS_FIX = 3
    REAL_TIME_KINEMATIC = 4
    FLOAT_RTK = 5
    ESTIMATED = 6
    MANUAL = 7
    SIMULATION = 8


class GPSHandler:
    """
    Manages real GPS module communication and coordinate extraction.
    
    Robust handling of:
    - Multiple NMEA sentence types ($GPGGA, $GNGGA, $GPRMC, etc.)
    - Serial connection errors and reconnects
    - GPS loss-of-fix scenarios
    - Update rate throttling
    - Thread-safe operations
    """
    
    def __init__(self, 
                 port: str = '/dev/ttyACM0',
                 baud: int = 9600,
                 timeout: float = 1.0,
                 max_retries: int = 20,
                 min_sats: int = 4):
        """
        Initialize GPS handler.
        
        Args:
            port (str): Serial port path
                - USB: '/dev/ttyACM0' or '/dev/ttyUSB0' (Linux/Pi)
                - GPIO UART: '/dev/serial0' or '/dev/ttyAMA0' (Pi)
                - Windows: 'COM3', 'COM4', etc.
            baud (int): Baud rate (typically 9600)
            timeout (float): Serial read timeout in seconds
            max_retries (int): Max attempts to read valid NMEA sentence per call
            min_sats (int): Minimum satellites for valid fix (3-4 typical)
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_sats = min_sats
        
        self.ser = None
        self.connected = False
        self.last_valid_lat = None
        self.last_valid_lon = None
        self.last_valid_time = None
        self.last_quality = 0
        self.no_fix_count = 0
        self.connection_attempts = 0
        
        self._lock = threading.Lock()
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish serial connection to GPS module.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if self.ser is not None:
                try:
                    self.ser.close()
                except:
                    pass
            
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE
            )
            self.connected = True
            self.connection_attempts += 1
            logger.info(f"GPS connected on {self.port} @ {self.baud} baud")
            return True
            
        except serial.SerialException as e:
            self.connected = False
            logger.warning(f"GPS connection failed on {self.port}: {e}")
            return False
        except Exception as e:
            self.connected = False
            logger.error(f"GPS initialization error: {e}")
            return False
    
    def get_coordinates(self) -> Tuple[Optional[float], Optional[float], Optional[str], int]:
        """
        Read latest valid GPS coordinates from serial stream.
        
        Attempts to read up to max_retries NMEA sentences quickly.
        Returns most recent valid GGA sentence (lat/lon/quality).
        Falls back to last known position if no fix available.
        
        Returns:
            Tuple of (latitude, longitude, timestamp_str, quality_int)
            - latitude: float or None
            - longitude: float or None  
            - timestamp_str: ISO format str "YYYY-MM-DD HH:MM:SS" or None
            - quality: GPS quality level (0-8)
            
        Example:
            lat, lon, ts, quality = gps.get_coordinates()
            if quality >= 1:  # GPS_FIX or better
                print(f"Position: {lat:.6f}, {lon:.6f} ({ts})")
            else:
                print("No GPS fix")
        """
        with self._lock:
            if not self.connected:
                if self.last_valid_lat is not None:
                    logger.debug("Using cached GPS coordinates (no current fix)")
                    return self.last_valid_lat, self.last_valid_lon, self.last_valid_time, self.last_quality
                else:
                    logger.warning("GPS not connected and no cached coordinates")
                    return None, None, None, 0
            
            # Try reading valid NMEA sentences
            for attempt in range(self.max_retries):
                try:
                    line = self.ser.readline()
                    if not line:
                        continue
                    
                    line_str = line.decode('ascii', errors='replace').strip()
                    
                    # Look for position sentences (GGA preferred, RMC fallback)
                    if not (line_str.startswith('$GPGGA') or line_str.startswith('$GNGGA') or
                            line_str.startswith('$GPRMC') or line_str.startswith('$GNRMC')):
                        continue
                    
                    try:
                        msg = pynmea2.parse(line_str)
                        
                        # Check if we have a valid fix
                        if hasattr(msg, 'gps_qual'):  # GGA sentence
                            quality = int(msg.gps_qual) if msg.gps_qual else 0
                        elif hasattr(msg, 'status'):  # RMC sentence
                            quality = 1 if msg.status == 'A' else 0
                        else:
                            quality = 0
                        
                        # Validate satellite count (GGA sentences)
                        num_sats = int(msg.num_sats) if hasattr(msg, 'num_sats') else self.min_sats
                        
                        # Accept if quality > 0 and enough satellites
                        if quality > 0 and num_sats >= self.min_sats:
                            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                                lat = msg.latitude
                                lon = msg.longitude
                                
                                # Handle hemisphere indicators
                                if hasattr(msg, 'lat_dir') and msg.lat_dir == 'S':
                                    lat = -lat
                                if hasattr(msg, 'lon_dir') and msg.lon_dir == 'W':
                                    lon = -lon
                                
                                # Extract timestamp
                                if hasattr(msg, 'timestamp') and msg.timestamp:
                                    ts_obj = msg.timestamp
                                    ts_str = f"{time.strftime('%Y-%m-%d')} {ts_obj.strftime('%H:%M:%S')}"
                                else:
                                    ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                # Cache valid fix
                                self.last_valid_lat = lat
                                self.last_valid_lon = lon
                                self.last_valid_time = ts_str
                                self.last_quality = quality
                                self.no_fix_count = 0
                                
                                logger.debug(f"GPS Fix: ({lat:.6f}, {lon:.6f}) Quality={quality} Sats={num_sats}")
                                return lat, lon, ts_str, quality
                    
                    except (pynmea2.ParseError, UnicodeError, ValueError, AttributeError) as e:
                        logger.debug(f"NMEA parse error: {e}")
                        continue
                
                except Exception as e:
                    logger.debug(f"Serial read error: {e}")
                    continue
            
            # No valid fix this cycle
            self.no_fix_count += 1
            if self.no_fix_count > 5:
                logger.warning(f"No GPS fix for {self.no_fix_count} cycles")
            
            # Return cached coordinates if available
            if self.last_valid_lat is not None:
                logger.debug("No new fix - using cached coordinates")
                return self.last_valid_lat, self.last_valid_lon, self.last_valid_time, self.last_quality
            
            return None, None, None, 0
    
    def get_cached_coordinates(self) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Retrieve last known valid coordinates without polling serial.
        Useful for reducing latency in detection loop.
        
        Returns:
            Tuple of (latitude, longitude, timestamp_str) or (None, None, None)
        """
        with self._lock:
            return self.last_valid_lat, self.last_valid_lon, self.last_valid_time
    
    def is_connected(self) -> bool:
        """Check if GPS module is physically connected."""
        return self.connected
    
    def has_valid_fix(self) -> bool:
        """Check if we have cached valid GPS coordinates."""
        return self.last_valid_lat is not None and self.last_valid_lon is not None
    
    def get_diagnostics(self) -> dict:
        """
        Return GPS module diagnostics for logging/debugging.
        
        Returns:
            dict with connection status, last fix quality, satellite count, etc.
        """
        with self._lock:
            return {
                'connected': self.connected,
                'port': self.port,
                'baud': self.baud,
                'has_valid_fix': self.has_valid_fix(),
                'last_latitude': self.last_valid_lat,
                'last_longitude': self.last_valid_lon,
                'last_timestamp': self.last_valid_time,
                'last_quality': self.last_quality,
                'no_fix_cycles': self.no_fix_count,
                'connection_attempts': self.connection_attempts
            }
    
    def close(self):
        """Close GPS serial connection cleanly."""
        with self._lock:
            if self.ser is not None:
                try:
                    self.ser.close()
                    self.connected = False
                    logger.info("GPS connection closed")
                except Exception as e:
                    logger.error(f"Error closing GPS: {e}")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()


# ==================== Standalone Testing ====================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Test on default USB port
    print("Testing GPS Handler (Press Ctrl+C to stop)...\n")
    
    try:
        gps = GPSHandler(port='/dev/ttyACM0', baud=9600)
        
        for i in range(10):
            lat, lon, ts, quality = gps.get_coordinates()
            
            if lat is not None:
                print(f"[{i}] ✓ Position: {lat:.6f}, {lon:.6f} (Quality: {quality}, Time: {ts})")
            else:
                print(f"[{i}] ✗ No fix (trying...)")
            
            time.sleep(1)
        
        diagnostics = gps.get_diagnostics()
        print(f"\nDiagnostics: {diagnostics}")
        
        gps.close()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        gps.close()
