"""
test_gps.py - GPS Module Testing & Diagnostics
===============================================
Standalone utility to test GPS module before production deployment.
Validates connection, NMEA parsing, fix quality, and accuracy.

Usage:
  python test_gps.py              # Use default port /dev/ttyACM0
  python test_gps.py --port /dev/ttyUSB0 --baud 38400
  python test_gps.py --port COM3 --duration 30

For Raspberry Pi:
  - USB GPS: ls /dev/ttyACM* or /dev/ttyUSB*
  - GPIO UART: /dev/serial0 (after raspi-config enable)
"""

import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.gps_handler import GPSHandler, GPSQuality

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class GPSTestor:
    """GPS module testing and diagnostics utility."""
    
    def __init__(self, port: str, baud: int, duration: int = 60):
        """
        Initialize GPS test.
        
        Args:
            port: Serial port (e.g., '/dev/ttyACM0')
            baud: Baud rate (e.g., 9600)
            duration: Test duration in seconds
        """
        self.port = port
        self.baud = baud
        self.duration = duration
        self.gps = None
        
        self.stats = {
            'total_reads': 0,
            'valid_fixes': 0,
            'no_fix_reads': 0,
            'quality_dist': {},
            'positions': [],
            'errors': [],
            'start_time': None,
            'end_time': None
        }
    
    def run(self):
        """Execute GPS test sequence."""
        print("\n" + "="*70)
        print("  ASTROPATH GPS MODULE TEST")
        print("="*70)
        print(f"Port: {self.port} | Baud: {self.baud} | Duration: {self.duration}s")
        print("="*70 + "\n")
        
        # Test 1: Connection
        print("[TEST 1] GPS Connection")
        print("-" * 70)
        if not self._test_connection():
            print("❌ FAILED: Cannot connect to GPS module")
            return False
        
        # Test 2: NMEA Parsing & Valid Fixes
        print("\n[TEST 2] NMEA Parsing & Fix Acquisition")
        print("-" * 70)
        self._test_nmea_parsing()
        
        # Test 3: Statistics & Analysis
        print("\n[TEST 3] Statistics & Analysis")
        print("-" * 70)
        self._analyze_results()
        
        # Test 4: Diagnostics
        print("\n[TEST 4] Module Diagnostics")
        print("-" * 70)
        self._print_diagnostics()
        
        # Summary
        print("\n[SUMMARY]")
        print("-" * 70)
        self._print_summary()
        
        self.gps.close()
        print("\n" + "="*70)
        print("  TEST COMPLETE")
        print("="*70 + "\n")
        
        return True
    
    def _test_connection(self) -> bool:
        """Test GPS module connection."""
        try:
            self.gps = GPSHandler(port=self.port, baud=self.baud, timeout=2.0)
            
            if self.gps.is_connected():
                print(f"✓ Connected to {self.port} @ {self.baud} baud")
                return True
            else:
                print(f"✗ Connection failed")
                return False
        
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def _test_nmea_parsing(self):
        """Test NMEA parsing and fix acquisition."""
        self.stats['start_time'] = datetime.now()
        end_time = self.stats['start_time'] + timedelta(seconds=self.duration)
        
        print(f"Reading for {self.duration} seconds...\n")
        
        while datetime.now() < end_time:
            self.stats['total_reads'] += 1
            
            try:
                lat, lon, ts, quality = self.gps.get_coordinates()
                
                if lat is not None and lon is not None:
                    self.stats['valid_fixes'] += 1
                    quality_name = self._quality_name(quality)
                    
                    # Track quality distribution
                    if quality not in self.stats['quality_dist']:
                        self.stats['quality_dist'][quality] = 0
                    self.stats['quality_dist'][quality] += 1
                    
                    # Store position
                    self.stats['positions'].append({
                        'lat': lat,
                        'lon': lon,
                        'timestamp': ts,
                        'quality': quality
                    })
                    
                    print(f"[{self.stats['total_reads']:3d}] ✓ {lat:10.6f}, {lon:11.6f} | "
                          f"Quality: {quality_name:15s} | {ts}")
                else:
                    self.stats['no_fix_reads'] += 1
                    print(f"[{self.stats['total_reads']:3d}] ✗ No fix (waiting...)")
                
                time.sleep(0.5)
            
            except Exception as e:
                self.stats['errors'].append(str(e))
                logger.error(f"Read error: {e}")
                time.sleep(1)
        
        self.stats['end_time'] = datetime.now()
    
    def _analyze_results(self):
        """Analyze test results."""
        total_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        fix_rate = (self.stats['valid_fixes'] / self.stats['total_reads'] * 100) if self.stats['total_reads'] > 0 else 0
        
        print(f"Total reads: {self.stats['total_reads']}")
        print(f"Valid fixes: {self.stats['valid_fixes']}")
        print(f"No fix reads: {self.stats['no_fix_reads']}")
        print(f"Fix rate: {fix_rate:.1f}%")
        print(f"Test duration: {total_time:.1f}s")
        
        # Quality distribution
        if self.stats['quality_dist']:
            print(f"\nQuality Distribution:")
            for quality, count in sorted(self.stats['quality_dist'].items()):
                pct = (count / self.stats['valid_fixes'] * 100) if self.stats['valid_fixes'] > 0 else 0
                name = self._quality_name(quality)
                print(f"  {name:20s}: {count:3d} ({pct:5.1f}%)")
        
        # Position variance (if multiple fixes)
        if len(self.stats['positions']) > 1:
            positions = self.stats['positions']
            lats = [p['lat'] for p in positions]
            lons = [p['lon'] for p in positions]
            
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)
            
            print(f"\nPosition Variance (indicates movement or noise):")
            print(f"  Latitude range:  {lat_range:.8f}° ({lat_range * 111.32:.2f}m)")
            print(f"  Longitude range: {lon_range:.8f}° ({lon_range * 111.32 * 0.7:.2f}m)")
            
            # Average position
            avg_lat = sum(lats) / len(lats)
            avg_lon = sum(lons) / len(lons)
            print(f"  Average position: {avg_lat:.6f}, {avg_lon:.6f}")
        
        # Errors
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for err in self.stats['errors'][:5]:  # Show first 5
                print(f"  - {err}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")
    
    def _print_diagnostics(self):
        """Print GPS module diagnostics."""
        diag = self.gps.get_diagnostics()
        
        for key, value in diag.items():
            if isinstance(value, float):
                print(f"{key:25s}: {value:.6f}")
            else:
                print(f"{key:25s}: {value}")
    
    def _print_summary(self):
        """Print test summary and recommendations."""
        fix_rate = (self.stats['valid_fixes'] / self.stats['total_reads'] * 100) if self.stats['total_reads'] > 0 else 0
        
        print("\nTest Results:")
        print(f"  Fixes obtained: {self.stats['valid_fixes']}/{self.stats['total_reads']} ({fix_rate:.1f}%)")
        
        if fix_rate >= 80:
            print("  ✓ GPS module performing well - READY FOR PRODUCTION")
            return_code = 0
        elif fix_rate >= 50:
            print("  ⚠ GPS module working but inconsistent - CHECK ANTENNA/ENVIRONMENT")
            return_code = 1
        else:
            print("  ✗ GPS module unreliable - TROUBLESHOOT REQUIRED")
            return_code = 2
        
        print("\nRecommendations:")
        if fix_rate < 50:
            print("  - Check GPS antenna connection (should be on module or separate)")
            print("  - Move to area with clear sky view (avoid indoors/urban canyons)")
            print("  - Try different serial port: ls /dev/tty{ACM,USB}*")
            print("  - Check baud rate (common: 9600, 38400)")
            print("  - Verify module with manufacturer software first")
        
        if self.stats['errors']:
            print("  - Investigate serial read errors (try different cable)")
            print("  - Check power supply to GPS module (voltage adequate?)")
        
        return return_code
    
    @staticmethod
    def _quality_name(quality: int) -> str:
        """Convert quality code to human-readable name."""
        quality_names = {
            0: 'NO_FIX',
            1: 'GPS_FIX',
            2: 'DGPS_FIX',
            3: 'PPS_FIX',
            4: 'REAL_TIME_KINEMATIC',
            5: 'FLOAT_RTK',
            6: 'ESTIMATED',
            7: 'MANUAL',
            8: 'SIMULATION'
        }
        return quality_names.get(quality, f'UNKNOWN({quality})')


def main():
    """Parse arguments and run GPS test."""
    parser = argparse.ArgumentParser(
        description='Test and diagnose GPS module for ASTROPATH',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_gps.py                    # Default USB port
  python test_gps.py --port /dev/ttyUSB0 --baud 38400
  python test_gps.py --port /dev/serial0 --duration 120
  python test_gps.py --port COM3 --baud 9600  # Windows
        """
    )
    
    parser.add_argument('--port', 
                       default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud',
                       type=int,
                       default=9600,
                       help='Baud rate (default: 9600)')
    parser.add_argument('--duration',
                       type=int,
                       default=60,
                       help='Test duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    testor = GPSTestor(port=args.port, baud=args.baud, duration=args.duration)
    success = testor.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
