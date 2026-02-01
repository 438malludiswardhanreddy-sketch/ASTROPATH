# GPS Configuration Reference for ASTROPATH
## Complete Parameter Guide & API Documentation

---

## Overview

This document provides detailed reference for all GPS-related configuration options, API functions, and integration patterns in ASTROPATH.

---

## Configuration Parameters (config.py)

### Master Control

```python
GPS_ENABLED = False
```
- **Type**: `bool`
- **Default**: `False`
- **Description**: Master switch to enable/disable real GPS integration
- **When to set to True**: GPS module is physically connected and serial port verified
- **When to set to False**: Running without GPS hardware or using IP geolocation only

---

### Serial Connection

#### `GPS_PORT`

```python
GPS_PORT = '/dev/ttyACM0'
```

- **Type**: `str`
- **Default**: `'/dev/ttyACM0'`
- **Valid values**: 
  - **Linux/Raspberry Pi**:
    - `/dev/ttyACM0` - USB CDC device (most common)
    - `/dev/ttyUSB0` - USB FTDI/CH340 adapter
    - `/dev/serial0` - GPIO UART on Pi (after enabling in raspi-config)
    - `/dev/ttyAMA0` - Original Pi UART (deprecated)
  - **Windows**:
    - `COM3`, `COM4`, `COM5`, etc.
  - **macOS**:
    - `/dev/tty.usbserial-XXXXXX`
    - `/dev/tty.usbmodem-XXXXXX`

- **How to find**:
  ```bash
  # Linux/Pi
  ls /dev/tty* | grep -E 'ACM|USB|serial'
  
  # Windows (PowerShell)
  Get-PnPDevice -Class Ports
  
  # Before/After technique
  ls /dev/tty* > before.txt
  # ... plug GPS ...
  ls /dev/tty* > after.txt
  diff before.txt after.txt
  ```

- **Example**:
  ```python
  GPS_PORT = '/dev/ttyACM0'  # Linux/Pi USB
  GPS_PORT = '/dev/serial0'   # Pi GPIO UART
  GPS_PORT = 'COM3'           # Windows
  ```

---

#### `GPS_BAUD`

```python
GPS_BAUD = 9600
```

- **Type**: `int`
- **Default**: `9600`
- **Common values**:
  - `9600` - Most common for u-blox NEO-6M, NEO-M8N, Adafruit
  - `38400` - Some modules, higher throughput
  - `115200` - High-end modules
  - `4800` - Legacy modules (rare)

- **How to determine**: Check GPS module datasheet or try values sequentially

- **Example test**:
  ```bash
  python test_gps.py --port /dev/ttyACM0 --baud 9600
  python test_gps.py --port /dev/ttyACM0 --baud 38400
  python test_gps.py --port /dev/ttyACM0 --baud 115200
  ```

- **Module-specific defaults**:
  | Module | Default Baud | Alternatives |
  |--------|--------------|--------------|
  | NEO-6M | 9600 | 38400, 115200 |
  | NEO-M8N | 9600 | 38400 |
  | Adafruit Ultimate | 9600 | 115200 |
  | Beitian BN-220 | 9600 | 38400 |
  | PA1010D | 115200 | 9600 |

---

### Timing Parameters

#### `GPS_TIMEOUT`

```python
GPS_TIMEOUT = 1.0
```

- **Type**: `float`
- **Default**: `1.0`
- **Unit**: Seconds
- **Valid range**: `0.1` - `5.0`
- **Description**: Serial read timeout - maximum time to wait for NMEA sentence
- **Effect on performance**:
  - **Too low** (<0.5s): May miss valid sentences, causes errors
  - **Too high** (>2.0s): Slows down detection loop
  - **Optimal**: `1.0` seconds

- **Adjustment**:
  ```python
  GPS_TIMEOUT = 0.5   # Faster but may lose data (edge devices)
  GPS_TIMEOUT = 1.0   # Balanced (recommended)
  GPS_TIMEOUT = 2.0   # More time to receive (poor connection)
  ```

---

#### `GPS_MAX_RETRIES`

```python
GPS_MAX_RETRIES = 20
```

- **Type**: `int`
- **Default**: `20`
- **Valid range**: `5` - `100`
- **Description**: Maximum attempts to read valid NMEA sentence per `get_coordinates()` call

- **How it works**:
  - GPS handler tries to read up to 20 NMEA sentences
  - Stops early when valid GGA/RMC found
  - Helps handle serial noise and invalid sentences

- **Adjustment**:
  ```python
  GPS_MAX_RETRIES = 10   # Faster, fewer serial reads (drones)
  GPS_MAX_RETRIES = 20   # Balanced (recommended)
  GPS_MAX_RETRIES = 50   # More thorough, slower (robust)
  ```

---

### Validation Thresholds

#### `GPS_MIN_SATS`

```python
GPS_MIN_SATS = 4
```

- **Type**: `int`
- **Default**: `4`
- **Valid range**: `3` - `12`
- **Description**: Minimum satellites required for valid GPS fix

- **Accuracy vs. Satellites**:
  | Satellites | Fix Quality | Accuracy | Typical Use |
  |-----------|-------------|----------|------------|
  | 3 | 2D (lat/lon only) | ±50m | Emergency fallback |
  | 4 | 3D (lat/lon/alt) | ±10-20m | Standard (recommended) |
  | 5+ | 3D+ | ±2-5m | High accuracy |
  | 8+ | Excellent | ±1-3m | Professional |

- **Setting**:
  ```python
  GPS_MIN_SATS = 3   # Lower threshold, more fixes (urban areas)
  GPS_MIN_SATS = 4   # Balanced (recommended)
  GPS_MIN_SATS = 6   # Strict, high accuracy only
  ```

---

#### `GPS_MIN_QUALITY`

```python
GPS_MIN_QUALITY = 1
```

- **Type**: `int`
- **Default**: `1`
- **Valid range**: `0` - `8`
- **Description**: Minimum GPS fix quality level to accept coordinates

- **GPS Quality Levels** (from NMEA standard):
  | Value | Name | Meaning | Accuracy |
  |-------|------|---------|----------|
  | 0 | NO_FIX | No fix | N/A |
  | 1 | GPS_FIX | GPS standard fix | 2-5m ✓ Good |
  | 2 | DGPS_FIX | Differential GPS | 1-2m ✓ Better |
  | 3 | PPS_FIX | PPS fix | <1m ✓ Excellent |
  | 4 | RTK_FIXED | Real-Time Kinematic | <0.05m ✓ Excellent |
  | 5 | RTK_FLOAT | RTK float solution | 0.1-1m ✓ Excellent |
  | 6 | ESTIMATED | Estimated | variable |
  | 7 | MANUAL | Manual input | N/A |
  | 8 | SIMULATION | Simulator mode | N/A |

- **Setting**:
  ```python
  GPS_MIN_QUALITY = 1   # Accept GPS fixes (recommended)
  GPS_MIN_QUALITY = 2   # Require differential GPS (precise)
  GPS_MIN_QUALITY = 0   # Accept any fix (last resort)
  ```

---

### Fallback Behavior

#### `GPS_USE_CACHED_IF_NO_FIX`

```python
GPS_USE_CACHED_IF_NO_FIX = True
```

- **Type**: `bool`
- **Default**: `True`
- **Description**: Use last known position if GPS currently has no fix

- **Behavior**:
  - **True**: Detections use cached GPS position when no fresh fix available
  - **False**: Report no position if GPS cannot acquire fix right now

- **When to use**:
  ```python
  GPS_USE_CACHED_IF_NO_FIX = True   # Recommended (prevents data loss)
  GPS_USE_CACHED_IF_NO_FIX = False  # Only if fresh data required
  ```

---

#### `GPS_FALLBACK_TO_IP`

```python
GPS_FALLBACK_TO_IP = True
```

- **Type**: `bool`
- **Default**: `True`
- **Description**: Fall back to IP-based geolocation if GPS unavailable

- **Accuracy trade-off**:
  - **GPS**: 2-5m accuracy ✓ Preferred
  - **IP Geolocation**: 100-500m accuracy ⚠️ Fallback only
  - **No location**: Loss of detection data ✗ Worst case

- **When to use**:
  ```python
  GPS_FALLBACK_TO_IP = True   # Urban/indoor ops (recommended)
  GPS_FALLBACK_TO_IP = False  # Only use real GPS (mission-critical)
  ```

---

## GPSHandler Class API

### Initialization

```python
from src.gps_handler import GPSHandler

gps = GPSHandler(
    port='/dev/ttyACM0',      # Serial port
    baud=9600,                # Baud rate
    timeout=1.0,              # Read timeout
    max_retries=20,           # NMEA read attempts
    min_sats=4                # Minimum satellites
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `port` | str | '/dev/ttyACM0' | Serial port path |
| `baud` | int | 9600 | Baud rate |
| `timeout` | float | 1.0 | Read timeout (seconds) |
| `max_retries` | int | 20 | NMEA parse attempts |
| `min_sats` | int | 4 | Minimum satellites for fix |

---

### Methods

#### `get_coordinates()`

```python
lat, lon, timestamp, quality = gps.get_coordinates()
```

- **Returns**:
  - `latitude` (float or None): Latitude in decimal degrees
  - `longitude` (float or None): Longitude in decimal degrees
  - `timestamp` (str or None): ISO format "YYYY-MM-DD HH:MM:SS"
  - `quality` (int): GPS quality level (0-8)

- **Example**:
  ```python
  lat, lon, ts, quality = gps.get_coordinates()
  
  if lat is not None and quality >= 1:
      print(f"Position: {lat:.6f}, {lon:.6f} @ {ts}")
  else:
      print("No GPS fix")
  ```

- **Use in detection loop**:
  ```python
  # When pothole detected
  lat, lon, ts, quality = gps.get_coordinates()
  
  payload = {
      'latitude': lat or 0.0,
      'longitude': lon or 0.0,
      'gps_timestamp': ts,
      'severity': 'High',
      'confidence': 0.95
  }
  ```

---

#### `get_cached_coordinates()`

```python
lat, lon, timestamp = gps.get_cached_coordinates()
```

- **Returns**: Last known valid position without polling serial
- **Purpose**: Reduce latency in detection loop
- **Returns** `(None, None, None)` if no prior fix

- **Example**:
  ```python
  # Fast path: use cached position
  lat, lon, ts = gps.get_cached_coordinates()
  
  if lat is not None:
      print(f"Using cached: {lat:.6f}, {lon:.6f}")
  else:
      # Retry with fresh read
      lat, lon, ts, _ = gps.get_coordinates()
  ```

---

#### `is_connected()`

```python
if gps.is_connected():
    print("GPS module online")
```

- **Returns**: `bool` - True if serial connection established
- **Use**: Check connection status before detection starts

---

#### `has_valid_fix()`

```python
if gps.has_valid_fix():
    print("We have a cached GPS position")
```

- **Returns**: `bool` - True if cached position available
- **Use**: Verify GPS before starting detection

---

#### `get_diagnostics()`

```python
diag = gps.get_diagnostics()
print(diag)
```

- **Returns**: Dictionary with GPS statistics
  ```python
  {
      'connected': True,
      'port': '/dev/ttyACM0',
      'baud': 9600,
      'has_valid_fix': True,
      'last_latitude': 28.613459,
      'last_longitude': 77.209876,
      'last_timestamp': '2026-01-31 14:30:45',
      'last_quality': 1,
      'no_fix_cycles': 0,
      'connection_attempts': 1
  }
  ```

- **Use**: Logging, debugging, health monitoring

---

#### `close()`

```python
gps.close()
```

- **Purpose**: Cleanly close GPS connection
- **Call**: In finally block or on exit

- **Example**:
  ```python
  try:
      gps = GPSHandler(port='/dev/ttyACM0')
      # ... use GPS ...
  finally:
      gps.close()  # Always close
  ```

---

### Context Manager Usage

```python
with GPSHandler(port='/dev/ttyACM0') as gps:
    lat, lon, ts, quality = gps.get_coordinates()
    print(f"Position: {lat:.6f}, {lon:.6f}")

# GPS automatically closed
```

---

## Integration Patterns

### Pattern 1: Conditional GPS (Recommended)

```python
from src.gps_handler import GPSHandler
import config

# Initialize
gps = None
if config.GPS_ENABLED:
    try:
        gps = GPSHandler(
            port=config.GPS_PORT,
            baud=config.GPS_BAUD,
            timeout=config.GPS_TIMEOUT
        )
        if gps.is_connected():
            print("✓ GPS ready")
    except Exception as e:
        print(f"✗ GPS failed: {e}")
        gps = None

# In detection loop
if gps:
    lat, lon, ts, quality = gps.get_coordinates()
    if lat is not None:
        payload['latitude'] = lat
        payload['longitude'] = lon

# Cleanup
if gps:
    gps.close()
```

---

### Pattern 2: With Fallback

```python
def get_position():
    """Get position with fallback chain"""
    
    # Try GPS first
    if gps and gps.has_valid_fix():
        lat, lon, _ = gps.get_cached_coordinates()
        if lat is not None:
            return lat, lon, 'GPS'
    
    # Try fresh GPS read
    if gps:
        lat, lon, _, quality = gps.get_coordinates()
        if lat is not None and quality >= config.GPS_MIN_QUALITY:
            return lat, lon, 'GPS'
    
    # Fallback to IP
    if config.GPS_FALLBACK_TO_IP:
        lat, lon = get_geolocation()  # IP-based
        if lat is not None:
            return lat, lon, 'IP'
    
    # Last resort
    return None, None, 'NONE'

# Usage
lat, lon, source = get_position()
print(f"Position: {lat}, {lon} (from {source})")
```

---

### Pattern 3: Error-Resistant

```python
def safe_get_gps():
    """GPS with comprehensive error handling"""
    
    try:
        if not config.GPS_ENABLED:
            return None, None
        
        if not gps:
            return None, None
        
        # Try getting coordinates
        lat, lon, ts, quality = gps.get_coordinates()
        
        # Validate result
        if lat is None or lon is None:
            logger.warning("GPS returned None coordinates")
            return None, None
        
        if quality < config.GPS_MIN_QUALITY:
            logger.debug(f"GPS quality {quality} below threshold {config.GPS_MIN_QUALITY}")
            if config.GPS_USE_CACHED_IF_NO_FIX:
                cached_lat, cached_lon, _ = gps.get_cached_coordinates()
                return cached_lat, cached_lon
            return None, None
        
        # Sanity check coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.error(f"Invalid coordinates: {lat}, {lon}")
            return None, None
        
        return lat, lon
    
    except Exception as e:
        logger.error(f"GPS error: {e}", exc_info=True)
        return None, None
```

---

## Payload Format (Cloud Integration)

### Standard Detection Payload with GPS

```json
{
  "latitude": 28.613459,
  "longitude": 77.209876,
  "gps_timestamp": "2026-01-31 14:30:45",
  "gps_quality": 1,
  "gps_source": "GPS",
  
  "pothole_severity": "High",
  "confidence": 0.92,
  "area_pixels": 15000,
  
  "image_path": "/detections/pothole_20260131-143045.jpg",
  "timestamp": "2026-01-31 14:30:45",
  "device_id": "astropath-pi-001",
  
  "source": "drone",
  "drone_id": "DJI-M300",
  "altitude": 50.5
}
```

---

## Testing & Validation

### Standalone Test

```bash
python test_gps.py --port /dev/ttyACM0 --duration 60
```

### Validation Checklist

- [ ] `test_gps.py` shows > 80% fix rate
- [ ] Coordinates within ±5m (verify on Google Maps)
- [ ] Timestamps consistent
- [ ] Quality = 1 or higher
- [ ] Diagnostics show proper connection

---

## Performance Optimization

### For Edge Devices (Raspberry Pi Zero)

```python
# Reduce overhead
GPS_TIMEOUT = 0.5          # Faster reads
GPS_MAX_RETRIES = 10       # Fewer attempts
GPS_MIN_SATS = 3           # Allow 2D fixes

# Use cached more aggressively
GPS_USE_CACHED_IF_NO_FIX = True

# Example optimized config
gps = GPSHandler(
    port='/dev/serial0',
    baud=9600,
    timeout=0.5,
    max_retries=10,
    min_sats=3
)
```

### For High-Accuracy Drone

```python
# Increase accuracy
GPS_MIN_SATS = 6           # Require more satellites
GPS_MIN_QUALITY = 2        # Require DGPS or better

# Allow longer timeouts
GPS_TIMEOUT = 2.0
GPS_MAX_RETRIES = 50
```

---

## Troubleshooting Reference

| Issue | Check | Solution |
|-------|-------|----------|
| No GPS fixes | Satellite visibility | Move to open area |
| High variance | Antenna quality | Use external SMA antenna |
| Baud rate errors | Module specifications | Try common rates: 9600, 38400 |
| Permission denied | User permissions | `sudo usermod -a -G dialout pi` |
| Port not found | Device detection | Verify with `ls /dev/tty*` |

---

## Code Examples

### Complete Detection with GPS

```python
from src.gps_handler import GPSHandler
from src.detect_edge import EdgeDetectionPipeline
import config

# Setup
pipeline = EdgeDetectionPipeline()  # GPS auto-initialized if enabled
gps = pipeline.gps

# Detection loop
detections = pipeline.process_frame(frame)

for det in detections:
    # Get GPS coordinates
    if gps:
        lat, lon, ts, quality = gps.get_coordinates()
    else:
        lat, lon, ts, quality = None, None, None, 0
    
    # Build payload
    payload = {
        'latitude': lat,
        'longitude': lon,
        'gps_timestamp': ts,
        'severity': det['severity'],
        'confidence': det['confidence']
    }
    
    # Upload
    requests.post(config.API_URL, json=payload)

# Cleanup
if gps:
    gps.close()
```

---

## Summary

| Feature | Setting |
|---------|---------|
| **Enable GPS** | `GPS_ENABLED = True` |
| **Connection** | `GPS_PORT = '/dev/ttyACM0'` |
| **Baud Rate** | `GPS_BAUD = 9600` |
| **Quality Threshold** | `GPS_MIN_QUALITY = 1` |
| **Satellite Minimum** | `GPS_MIN_SATS = 4` |
| **Fallback to IP** | `GPS_FALLBACK_TO_IP = True` |
| **Use Cache** | `GPS_USE_CACHED_IF_NO_FIX = True` |

---

**For more info:** See `GPS_SETUP_GUIDE.md` for hardware setup and troubleshooting.

Last Updated: 2026-01-31
