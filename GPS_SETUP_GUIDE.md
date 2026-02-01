# GPS Module Integration Guide for ASTROPATH
## Real-Time Location Tracking for Pothole Detection

---

## 📡 Overview

This guide provides step-by-step instructions to integrate a real GPS module with ASTROPATH for reliable, accurate location data when detecting potholes on Raspberry Pi or vehicle/drone platforms.

**Why Real GPS?**
- IP-based geolocation is inaccurate (±100-500m) and often fails in some regions
- Real GPS modules provide 2-5m accuracy ±
- Essential for drone/vehicle-based pothole tracking
- Enables precise pothole mapping for municipal response
- Integrates seamlessly with cloud API for location-based analysis

---

## 🛠️ Hardware Selection (2026 Recommendation)

### Best GPS Modules for ASTROPATH

| Module | Price | Accuracy | Connection | Update Rate | Use Case | Notes |
|--------|-------|----------|-----------|------------|----------|-------|
| **u-blox NEO-6M** | ₹500-800 | 2.5m | USB/UART | 1 Hz | ✓ Best Overall | Most popular, excellent tutorials |
| **u-blox NEO-M8N** | ₹1000-1500 | 2.5m | USB/UART | 1 Hz | ✓ High-Precision | Better than NEO-6M, more expensive |
| **u-blox SAM-M8Q** | ₹1200-1800 | 2.5m | USB/UART | 1 Hz | ✓ Compact | Tiny form factor for drones |
| **Adafruit Ultimate GPS** | ₹3000-4000 | 3-4m | USB/I2C | 1 Hz | ✓ Beginner | Easy setup, well-documented |
| **Beitian BN-220** | ₹800-1200 | 2.5m | USB/UART | 10 Hz | ✓ Drones | High update rate for moving vehicles |
| **PA1010D** | ₹2000-2500 | 2.5m | I2C/UART | 1 Hz | ✓ Compact | Integration with accelerometer |

**ASTROPATH Recommendation:** **u-blox NEO-M8N** (perfect balance of price, accuracy, and availability in India)

### Additional Hardware

- **Antenna**: Most modules have built-in ceramic antenna (adequate for outdoor use)
  - For better performance: External SMA antenna (~₹300-500, optional)
- **USB Cable**: For connection to Pi (if USB module)
- **Serial Adapter** (if using GPIO UART): CH340 or similar (~₹50-100)

---

## 🔌 Connection Types

### Option 1: USB Connection (EASIEST)

**Best for:** Rapid prototyping, testing, initial setup

**Hardware:**
- GPS module with USB output (NEO-M8N USB, Adafruit USB, etc.)
- USB cable
- Raspberry Pi or Windows machine

**Setup (Raspberry Pi):**
```bash
# 1. Plug USB GPS into Pi
# 2. Verify device appeared
ls /dev/ttyACM* 
# Output: /dev/ttyACM0 (or ttyUSB0)

# 3. Update config.py
GPS_PORT = '/dev/ttyACM0'
GPS_ENABLED = True
```

**Setup (Windows):**
```
1. Plug USB GPS into computer
2. Device Manager → Ports → Identify COM port (COM3, COM4, etc.)
3. Update config.py:
   GPS_PORT = 'COM3'  # or your port number
```

---

### Option 2: Serial UART (GPIO) Connection

**Best for:** Integrated deployment, battery-powered, Pi Zero

**Hardware:**
- GPS module with UART output (NEO-M8N, BN-220, most serial modules)
- Jumper wires
- Raspberry Pi (GPIO pins 8 & 10 for UART)

**Wiring (Raspberry Pi GPIO):**
```
GPS Module TX  →  Pi RX (GPIO 10 / Pin 19)
GPS Module RX  ←  Pi TX (GPIO 8 / Pin 21)
GPS Module GND →  Pi GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
GPS Module 5V  →  Pi 5V  (Pin 2, 4) [Some modules need 3.3V instead]
```

**Pinout Reference:**
```
Raspberry Pi GPIO Header (40-pin, newer Pi models):

3V3 (1)  (2) 5V
GPIO2    (3) (4) 5V
GPIO3    (5) (6) GND
GPIO4    (7) (8) GPIO 14 (TX - connect GPS RX here)
GND      (9) (10) GPIO 15 (RX - connect GPS TX here)
GPIO17   (11) (12) GPIO 18
GPIO27   (13) (14) GND
...

Pi Zero Pinout: Same 40-pin header
```

**Setup (Raspberry Pi GPIO):**
```bash
# 1. Enable UART in Raspberry Pi config
sudo raspi-config
# Navigate to: Interface Options → Serial → Login Shell: No, Hardware: Yes
# Exit and reboot

# 2. Verify UART enabled
ls /dev/serial0 /dev/ttyAMA0
# Output should show the device

# 3. Update config.py
GPS_PORT = '/dev/serial0'  # or '/dev/ttyAMA0' on older Pi
GPS_ENABLED = True

# 4. Test connection
python test_gps.py --port /dev/serial0
```

**Enable Persistence (Optional):**
```bash
# Edit /boot/cmdline.txt to disable serial console
# Remove: console=serial0,115200
sudo nano /boot/cmdline.txt
# Reboot after changes
```

---

### Option 3: I2C Connection

**Best for:** Projects with multiple I2C sensors, minimal GPIO usage

**Hardware:**
- GPS module with I2C support (Adafruit PA1010D, some NEO-M8 variants)
- I2C cables

**Wiring:**
```
GPS Module SDA → Pi GPIO 2 (SDA, Pin 3)
GPS Module SCL → Pi GPIO 3 (SCL, Pin 5)
GPS Module GND → Pi GND
GPS Module 3.3V → Pi 3.3V
```

**Setup (I2C):**
```bash
# Enable I2C
sudo raspi-config → Interface Options → I2C → Yes

# Test I2C device
i2cdetect -y 1
# Should show GPS module address (usually 0x10 or 0x42)

# Note: Requires different Python library
# Current gps_handler.py uses serial - would need modification
```

---

## 📦 Software Installation

### 1. Install Dependencies

```bash
# Update Pi (if on Raspberry Pi)
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-dev

# Install Python libraries for GPS
pip install pynmea2 pyserial

# Verify installation
python3 -c "import pynmea2; import serial; print('✓ GPS libraries installed')"
```

### 2. Configure ASTROPATH

**Update config.py:**
```python
# Enable GPS
GPS_ENABLED = True

# Set your serial port
GPS_PORT = '/dev/ttyACM0'  # USB: /dev/ttyACM0, /dev/ttyUSB0, /dev/serial0
                            # Windows: 'COM3', 'COM4', etc.

# Standard settings (usually don't need changing)
GPS_BAUD = 9600            # Some modules use 38400
GPS_MIN_QUALITY = 1        # Accept any GPS fix (1=good)
GPS_MIN_SATS = 4           # Need 4+ satellites (3 for basic fix)

# Fallback behavior
GPS_USE_CACHED_IF_NO_FIX = True   # Use last known position if no fix
GPS_FALLBACK_TO_IP = True         # Use IP geolocation if GPS fails
```

---

## 🧪 Testing GPS Module

### Quick Test (Before Production)

```bash
# 1. Go to ASTROPATH directory
cd /path/to/ASTROPATH

# 2. Run GPS test utility (60-second test)
python test_gps.py --port /dev/ttyACM0 --duration 60

# 3. Expected output:
# ✓ Connected to /dev/ttyACM0 @ 9600 baud
# [1] ✓ 28.613459, 77.209876 | Quality: GPS_FIX | 2026-01-31 14:30:45
# [2] ✓ 28.613467, 77.209881 | Quality: GPS_FIX | 2026-01-31 14:30:46
# ... (continues reading for 60s)
# Fix rate: 95.0%
# ✓ GPS module performing well - READY FOR PRODUCTION
```

### Detailed Test (Troubleshooting)

```bash
# Longer test with diagnostics
python test_gps.py --port /dev/ttyACM0 --duration 120

# Shows:
# - Connection status
# - NMEA parse success rate
# - Quality distribution
# - Position variance
# - Diagnostic info

# Look for:
# ✓ Fix rate > 80%
# ✓ Multiple GPS_FIX readings
# ✓ Position variance < 5m
```

### Test with Different Port/Baud

```bash
# If default doesn't work
python test_gps.py --port /dev/ttyUSB0 --baud 38400 --duration 60

# Common ports to try:
# Linux/Pi: /dev/ttyACM0, /dev/ttyUSB0, /dev/serial0, /dev/ttyAMA0
# Windows: COM3, COM4, COM5
```

---

## 🚀 Integration with ASTROPATH Detection

Once GPS is tested and working, update your detection script:

### In detect_edge.py (Already integrated via GPS handler):

```python
from src.gps_handler import GPSHandler
from config import GPS_ENABLED, GPS_PORT, GPS_BAUD, GPS_MIN_QUALITY

# Initialize GPS
gps = GPSHandler(port=GPS_PORT, baud=GPS_BAUD) if GPS_ENABLED else None

# In detection loop:
while True:
    ret, frame = cap.read()
    
    # ... YOLO detection ...
    
    # Get GPS coordinates when pothole detected
    if gps:
        lat, lon, timestamp, quality = gps.get_coordinates()
        
        if lat is not None and quality >= GPS_MIN_QUALITY:
            print(f"Pothole at: {lat:.6f}, {lon:.6f}")
            # Include in payload to cloud
        else:
            print("No GPS fix - using fallback")
    
    # Upload to cloud with location
    payload = {
        'latitude': lat or 0.0,
        'longitude': lon or 0.0,
        'gps_timestamp': timestamp,
        'severity': severity,
        'confidence': confidence,
        ...
    }
    requests.post(API_URL, json=payload)
```

---

## 🔧 Troubleshooting

### Issue: "GPS connection failed" or "Port not found"

**Cause:** GPS module not detected or wrong port

**Solution:**
```bash
# List all serial devices
ls /dev/tty*

# Look for:
# /dev/ttyACM0 (USB)
# /dev/ttyUSB0 (USB adapter)
# /dev/serial0 (GPIO UART)
# /dev/ttyAMA0 (old Pi UART)

# Plug/unplug module and watch for new device
ls /dev/tty* | tee before.txt
# ... plug GPS ...
ls /dev/tty* | diff before.txt -
```

**Quick Fix:**
```bash
# Try each port
python test_gps.py --port /dev/ttyACM0
python test_gps.py --port /dev/ttyUSB0
python test_gps.py --port /dev/serial0
```

---

### Issue: "Fix rate < 50%" or "No GPS fix"

**Cause:** Poor satellite visibility or antenna issue

**Solution:**
```
1. Move to open area (away from buildings, trees, tunnels)
2. Point antenna upward (if external antenna)
3. Let GPS warm-up (first fix takes 30-60 seconds)
4. Check antenna connection (wiggle SMA connector)
5. Try different antenna orientation
6. Update GPS firmware (check module documentation)
```

---

### Issue: High Position Variance or "Jittery" readings

**Cause:** Multipath, weak signal, or poor antenna

**Solution:**
```
1. Try external SMA antenna (better than built-in)
2. Reposition antenna away from metal/buildings
3. Filter readings in software (use average of last 3 readings)
4. Check GPS module is powered adequately (5V/3.3V as needed)
5. Use higher-quality baud rate (38400 for improved stability)
```

---

### Issue: Serial Port Permission Denied

**Cause:** Pi user doesn't have permissions

**Solution (Raspberry Pi):**
```bash
# Add user to dialout group
sudo usermod -a -G dialout pi

# Exit and login again
exit  # Logout
# Login again

# Test again
python test_gps.py --port /dev/ttyACM0
```

---

### Issue: "NMEA Parse Error" or Wrong Coordinates

**Cause:** Baud rate mismatch or corrupted data

**Solution:**
```
1. Check module baud rate (default usually 9600)
   - Some modules use 38400, 115200, etc.
   
2. Try different baud rates:
   python test_gps.py --port /dev/ttyACM0 --baud 38400
   python test_gps.py --port /dev/ttyACM0 --baud 115200
   
3. Verify with manufacturer documentation
   
4. Try factory reset of GPS module (consult manual)
```

---

## 📊 GPS Performance Metrics

### Expected Accuracy (by module)

| Module | Accuracy | Typical | Indoor | Multipath |
|--------|----------|---------|--------|-----------|
| NEO-6M | 2.5m | ±3-5m | ❌ Poor | ⚠️ Moderate |
| NEO-M8N | 2.5m | ±2-4m | ❌ Poor | ✓ Good filtering |
| PA1010D | 3-4m | ±3-5m | ❌ Poor | ⚠️ Moderate |
| BN-220 | 2.5m | ±2-4m | ❌ Poor | ✓ Good filtering |

**Note:** GPS is extremely poor indoors. For indoor detection, use IP geolocation fallback or integrate Bluetooth BLE beacons.

### Expected Fix Time

| Condition | Cold Start | Warm Start |
|-----------|-----------|-----------|
| Clear sky | 30-60s | 5-10s |
| Urban canyon | 60-120s | 10-30s |
| Partial obstruction | 120s+ | 30-60s |
| Indoors | ∞ (no fix) | ∞ (no fix) |

---

## 🌐 Cloud Integration

Once GPS is working, ensure payload includes location:

```python
# Payload structure with GPS
detection_payload = {
    'latitude': 28.613459,
    'longitude': 77.209876,
    'gps_timestamp': '2026-01-31 14:30:45',
    'altitude': None,  # Optional, if supported
    
    'pothole_severity': 'High',
    'confidence': 0.92,
    'area_pixels': 15000,
    'bounding_box': [x, y, w, h],
    
    'image_path': '/path/to/detection.jpg',
    'source': 'drone',  # or 'vehicle' or 'citizen'
    'timestamp': '2026-01-31 14:30:45',
    'device_id': 'astropath-pi-001'
}

# Upload to cloud
response = requests.post(
    'https://your-api.com/api/reports',
    json=detection_payload,
    timeout=10
)
```

---

## 🚁 For Drone Users

If flying ASTROPATH on a drone:

### Option A: Drone's Built-in GPS
```python
# Use drone SDK to get position
from drone_sdk import Drone

drone = Drone()
drone_lat, drone_lon = drone.gps.get_position()

# Use drone GPS directly
payload = {
    'latitude': drone_lat,
    'longitude': drone_lon,
    ...
}
```

### Option B: Separate GPS Module
```python
# Mount NEO-M8N or BN-220 on drone
# Connect via USB to Jetson Nano / companion computer
# Integrate as described above

# Considerations:
# - Higher vibration → use vibration dampener
# - Power budget → ensure 5V supply adequate
# - Antenna orientation → keep upward-facing
```

### Recommended Drone Setup
- **Flight Controller**: Pixhawk 4 (has built-in GPS)
- **Companion Computer**: Jetson Nano or Raspberry Pi 4
- **GPS Module**: u-blox NEO-M8N (RTK-ready if needed)
- **Connection**: USB to companion computer

---

## 📝 Configuration Reference

### config.py GPS Parameters

```python
# Master enable
GPS_ENABLED = False  # Set to True when hardware connected

# Hardware configuration
GPS_PORT = '/dev/ttyACM0'           # Serial port
GPS_BAUD = 9600                     # Baud rate

# Timing parameters
GPS_TIMEOUT = 1.0                   # Serial read timeout
GPS_MAX_RETRIES = 20                # NMEA read attempts per poll

# Validation parameters
GPS_MIN_SATS = 4                    # Minimum satellites for fix
GPS_MIN_QUALITY = 1                 # Minimum acceptable quality (1=GPS_FIX)

# Fallback behavior
GPS_USE_CACHED_IF_NO_FIX = True     # Use last position if no current fix
GPS_FALLBACK_TO_IP = True           # Fall back to IP geolocation
```

---

## 📚 Reference & Resources

### Libraries Used
- **pynmea2**: Parse NMEA GPS sentences (GGA, RMC, etc.)
- **pyserial**: Serial communication with GPS module

### Popular NMEA Sentences
| Sentence | Data | Used For |
|----------|------|----------|
| $GPGGA | Lat, Lon, Quality, Sats | Primary (this project) |
| $GPRMC | Lat, Lon, Speed, Course | Position + heading |
| $GPGSV | Satellite info | Diagnostic |
| $GPGSA | DOP, Satellites | Diagnostic |

### Useful Commands

```bash
# Monitor serial output in real-time
cat /dev/ttyACM0

# Monitor with hexdump
hexdump -C /dev/ttyACM0

# GPS minicom terminal (interactive)
minicom -D /dev/ttyACM0

# Check USB devices
lsusb | grep -i gps

# Check device info
udevadm info -a -n /dev/ttyACM0
```

### Module Documentation Links (2026)
- u-blox NEO-M8N: [datasheets.u-blox.com](https://www.u-blox.com)
- Adafruit GPS: [learn.adafruit.com/ultragps](https://learn.adafruit.com)
- Beitian GPS: Official documentation on Ali

---

## ✅ Deployment Checklist

- [ ] GPS module purchased and tested
- [ ] Connection type selected (USB/UART/I2C)
- [ ] Hardware connected to Pi/computer
- [ ] `test_gps.py` shows > 80% fix rate
- [ ] config.py GPS parameters updated
- [ ] GPS_ENABLED = True in config.py
- [ ] Detection script updated to use GPS handler
- [ ] Cloud API payload includes GPS data
- [ ] Tested in outdoor environment (clear sky)
- [ ] Fallback mechanisms verified (IP geolocation works)
- [ ] Production deployment ready ✓

---

## 🎯 Next Steps

1. **Procure Hardware**: Order GPS module + antenna (if needed)
2. **Connect & Test**: Follow connection guide, run test_gps.py
3. **Update Config**: Set GPS_ENABLED=True, correct port/baud
4. **Integrate**: Update detect_edge.py to use GPS coordinates
5. **Deploy**: Test on vehicle/drone with real detections
6. **Monitor**: Track accuracy, fix rates, and cloud uploads

---

**Questions?** Check TRAINING_DATA_STATUS.md and config.py for additional context.

Last Updated: 2026-01-31
