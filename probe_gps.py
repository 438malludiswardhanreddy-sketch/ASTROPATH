"""
probe_gps.py
Quick probe: print first NMEA sentences from a serial GPS port and show GPSHandler diagnostics.
"""
import argparse
import serial
import time
from src.gps_handler import GPSHandler

parser = argparse.ArgumentParser(description='Probe GPS serial port and print NMEA lines')
parser.add_argument('--port', default='COM4')
parser.add_argument('--baud', type=int, default=9600)
parser.add_argument('--count', type=int, default=10)
parser.add_argument('--timeout', type=float, default=1.0)
args = parser.parse_args()

print(f"Probing port: {args.port} @ {args.baud} baud, printing up to {args.count} NMEA lines")

# Try reading raw NMEA sentences
try:
    ser = serial.Serial(args.port, args.baud, timeout=args.timeout)
    print(f"Opened serial port {args.port}")
except Exception as e:
    print(f"Failed to open serial port {args.port}: {e}")
    ser = None

nmea_printed = 0
start = time.time()
if ser:
    try:
        while nmea_printed < args.count and (time.time() - start) < (args.count * args.timeout + 5):
            line = ser.readline()
            if not line:
                continue
            try:
                s = line.decode('ascii', errors='replace').strip()
            except Exception:
                s = repr(line)
            if s.startswith('$'):
                nmea_printed += 1
                print(f"[{nmea_printed}] {s}")
    except KeyboardInterrupt:
        print('\nProbe interrupted by user')
    finally:
        ser.close()
        print('Serial closed')

# Now instantiate GPSHandler to show diagnostics
try:
    gps = GPSHandler(port=args.port, baud=args.baud, timeout=args.timeout)
    print('\nGPSHandler diagnostics:')
    diag = gps.get_diagnostics()
    for k, v in diag.items():
        print(f"  {k}: {v}")
    # Try one immediate coordinate read
    lat, lon, ts, q = gps.get_coordinates()
    print(f"\nImmediate get_coordinates -> lat: {lat}, lon: {lon}, time: {ts}, quality: {q}")
    gps.close()
except Exception as e:
    print(f"Failed to use GPSHandler: {e}")

print('\nProbe complete')
