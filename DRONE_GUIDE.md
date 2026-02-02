# 🚁 ASTROPATH - Drone Integration Guide

## Complete Guide for Aerial Road Inspection with Drones

---

## 📋 Table of Contents
- [Overview](#overview)
- [Supported Drones](#supported-drones)
- [Quick Start](#quick-start)
- [Video Streaming Setup](#video-streaming-setup)
- [Running Drone Surveys](#running-drone-surveys)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

ASTROPATH now supports **drone-based automated road inspection** with:

✅ **Real-time video streaming** (RTSP/UDP/HTTP)  
✅ **Ground coordinate projection** (pixel to GPS)  
✅ **Telemetry integration** (MAVLink support)  
✅ **Automated survey missions**  
✅ **Live detection overlay**  
✅ **Database integration** with GPS coordinates  

---

## 🚁 Supported Drones

### Recommended Drones (2026)

| Drone | Best For | Flight Time | Notes |
|-------|----------|-------------|-------|
| **DJI Mavic 3** | Large area surveys | 45 min | Best camera, long range |
| **DJI Mini 3 Pro** | Urban inspection | 34 min | Compact, under 250g |
| **Autel EVO II** | Enterprise use | 40 min | Dual camera, thermal |
| **Skydio 2+** | Autonomous flight | 27 min | Best obstacle avoidance |
| **DIY Pixhawk** | Custom solutions | 20-30 min | Budget, fully customizable |

### Requirements
- Camera resolution: Minimum 1920x1080 (4K recommended)
- Video streaming capability (RTSP/UDP/HTTP)
- GPS module for telemetry
- Stable hover capability
- 20+ minute flight time

---

## 🚀 Quick Start

### Option 1: Using Drone Detector Script

```bash
# Navigate to project
cd ASTROPATH-1

# Run drone detector
python src/drone_detector.py
```

Follow the prompts:
1. Enter drone stream URL
2. Set survey duration
3. Choose save options
4. Start survey!

### Option 2: Web Interface

```bash
# Start web application
python app.py
```

Then:
1. Open http://localhost:5000
2. Select "Drone Stream" from camera dropdown
3. Click "Start Detection"

### Option 3: Configuration File

Edit `config.py`:
```python
# Enable drone mode
DRONE_ENABLED = True
DRONE_STREAM_URL = "rtsp://192.168.1.100:8554/video"

# Then use in app
CAMERA_SOURCE = DRONE_STREAM_URL
```

---

## 📡 Video Streaming Setup

### DJI Drones (Mavic, Mini, Air series)

#### Method 1: DJI SDK (Recommended)
```python
# Using DJI Mobile SDK
# 1. Install DJI Assistant 2
# 2. Enable API mode in drone settings
# 3. Stream via USB/WiFi to PC
```

#### Method 2: Third-Party Apps

**Using Dronelink:**
1. Install Dronelink app on mobile
2. Connect drone to phone
3. Enable video streaming
4. Stream to PC via WiFi network

**Using Litchi:**
1. Install Litchi app
2. Connect drone
3. Enable RTSP streaming
4. Use stream URL: `rtsp://PHONE_IP:8554/video`

#### Method 3: RTSP Restreamer
```bash
# Install on PC/Raspberry Pi
docker run -p 8554:8554 bluenviron/mediamtx

# Configure drone controller app to send to:
# rtsp://YOUR_PC_IP:8554/mystream
```

### Pixhawk-Based Drones

#### Setup with Mission Planner:
1. Connect drone via telemetry radio
2. Mission Planner → Data → Video → UDP Stream
3. Configure camera companion computer:
   ```bash
   # On companion computer (Raspberry Pi)
   gst-launch-1.0 -v v4l2src device=/dev/video0 ! \
   video/x-raw,width=1920,height=1080,framerate=30/1 ! \
   videoconvert ! x264enc ! rtph264pay ! \
   udpsink host=GROUND_STATION_IP port=5600
   ```

#### Using QGroundControl:
1. Connect drone
2. Application Settings → Video
3. Set video source to UDP/RTSP
4. Use URL in ASTROPATH config

### Manual IP Camera Setup

For any drone with IP camera:
```python
# RTSP
DRONE_STREAM_URL = "rtsp://192.168.1.100:8554/video"

# UDP
DRONE_STREAM_URL = "udp://192.168.1.100:5600"

# HTTP/MJPEG
DRONE_STREAM_URL = "http://192.168.1.100:8080/video"
```

---

## 🎮 Running Drone Surveys

### Interactive Mode

```bash
# Start drone detector
python src/drone_detector.py

# When prompted, enter:
# Stream URL: rtsp://192.168.1.100:8554/video
# Duration: 300 (5 minutes, or leave blank for continuous)
# Save video: y
# Auto-save detections: y
```

### Programmatic Mode

```python
from src.drone_controller import DroneController
from src.drone_detector import DroneDetector

# Initialize
drone = DroneController(stream_url="rtsp://192.168.1.100:8554/video")
drone.connect()

detector = DroneDetector(drone)

# Run survey
stats = detector.run_survey(
    duration=600,  # 10 minutes
    save_video=True,
    auto_save_detections=True
)

print(f"Survey complete: {stats['total_detections']} detections found")
drone.disconnect()
```

### Web Interface

1. Start app: `python app.py`
2. Open: http://localhost:5000/dashboard
3. Configure drone settings
4. Start detection
5. View live detections on map

---

## ⚙️ Configuration

### Basic Settings (config.py)

```python
# Enable drone mode
DRONE_ENABLED = True

# Stream URL
DRONE_STREAM_URL = "rtsp://192.168.1.100:8554/video"

# Camera parameters
DRONE_CAMERA_FOV_HORIZONTAL = 90  # Degrees
DRONE_CAMERA_FOV_VERTICAL = 60    # Degrees
DRONE_CAMERA_RESOLUTION = (1920, 1080)

# Flight parameters
DRONE_DEFAULT_ALTITUDE = 50  # meters
DRONE_DEFAULT_SPEED = 5      # m/s
```

### Advanced Settings

```python
# Gimbal angle (-90 = straight down, 0 = forward)
DRONE_GIMBAL_ANGLE = -90

# Telemetry source
DRONE_TELEMETRY_SOURCE = 'mavlink'  # or 'simulation'
DRONE_MAVLINK_CONNECTION = 'udp:127.0.0.1:14550'

# Detection thresholds
DRONE_DETECTION_MIN_AREA = 0.0005  # Smaller from altitude
DRONE_DETECTION_SAVE_INTERVAL = 5  # Save every 5 frames

# Survey settings
DRONE_SURVEY_ALTITUDE = 50  # meters
DRONE_SURVEY_SPEED = 5      # m/s
DRONE_SURVEY_OVERLAP = 30   # percentage
```

---

## 📊 Ground Coordinate Projection

The system automatically calculates ground GPS coordinates from drone camera pixels:

```
Drone Position (GPS) + Altitude + Camera FOV + Gimbal Angle
                    ↓
           Pixel to Ground Mapping
                    ↓
          Pothole GPS Coordinates
```

### How It Works:

1. **Drone telemetry** provides position and altitude
2. **Camera FOV** determines ground coverage
3. **Pixel position** in frame mapped to ground position
4. **Gimbal angle** adjusts for camera orientation
5. **GPS coordinates** calculated for each detection

### Accuracy:

| Altitude | Pixel Size | GPS Accuracy |
|----------|-----------|--------------|
| 30m | ~1.5 cm | ±0.5m |
| 50m | ~2.5 cm | ±1m |
| 100m | ~5 cm | ±2m |

---

## 🎯 Survey Mission Planning

### Grid Survey Pattern

```python
from src.drone_controller import DroneController

drone = DroneController(stream_url="...")

# Plan grid survey
waypoints = drone.plan_survey_mission(
    start_lat=17.6599,
    start_lon=75.9064,
    area_width=500,   # meters
    area_length=500,  # meters
    altitude=50,      # meters
    overlap=30        # percentage
)

print(f"Mission: {len(waypoints)} waypoints")
# Upload to drone autopilot or execute manually
```

### Linear Road Survey

```python
# For road inspection
waypoints = [
    (17.6599, 75.9064, 50),  # lat, lon, alt
    (17.6650, 75.9100, 50),
    (17.6700, 75.9150, 50),
]

drone.set_waypoints(waypoints)
```

---

## 🔧 Advanced Features

### MAVLink Integration

For real-time telemetry from Pixhawk/ArduPilot drones:

```python
# Install pymavlink
pip install pymavlink

# Configure
DRONE_TELEMETRY_SOURCE = 'mavlink'
DRONE_MAVLINK_CONNECTION = 'udp:127.0.0.1:14550'  # Or COM port
```

### Multi-Drone Support

```python
# Multiple drones
drones = [
    DroneController("rtsp://192.168.1.100:8554/video"),
    DroneController("rtsp://192.168.1.101:8554/video"),
]

for drone in drones:
    drone.connect()
    # Run parallel surveys
```

### Video Recording

```python
# All surveys automatically save video
detector.run_survey(
    duration=600,
    save_video=True,  # Saves to detections/drone_survey_TIMESTAMP.avi
    auto_save_detections=True
)
```

---

## 📱 Mobile Ground Control

Access drone operations from mobile device:

1. Start app: `python app.py`
2. Get PC IP: `ipconfig` (Windows) or `ifconfig` (Linux)
3. On phone, go to: `http://YOUR_PC_IP:5000`
4. Monitor live drone feed and detections

---

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to drone stream

```bash
# Test stream URL
ffplay rtsp://192.168.1.100:8554/video

# If fails, check:
# 1. Drone WiFi connected
# 2. IP address correct
# 3. Firewall settings
# 4. Stream format supported
```

**Problem:** Video laggy or dropping frames

```python
# Reduce detection load
FAST_MODE = True
DETECTION_FRAME_SKIP = 5  # Process every 5th frame
FAST_IMG_SIZE_YOLO = 320
```

### Telemetry Issues

**Problem:** GPS coordinates inaccurate

```python
# Check camera parameters
DRONE_CAMERA_FOV_HORIZONTAL = 90  # Verify actual FOV
DRONE_GIMBAL_ANGLE = -90  # Ensure correct angle

# Calibrate altitude
# Actual altitude may differ from barometric reading
```

**Problem:** MAVLink not connecting

```bash
# Test MAVLink connection
mavproxy.py --master=udp:127.0.0.1:14550

# Check port
netstat -an | findstr 14550  # Windows
netstat -an | grep 14550     # Linux
```

### Detection Issues

**Problem:** Missing detections from altitude

```python
# Adjust for smaller potholes from height
DRONE_DETECTION_MIN_AREA = 0.0001  # Smaller threshold
CONF_THRESHOLD = 0.3  # Lower confidence threshold
```

**Problem:** Too many false positives

```python
# Increase thresholds
CONF_THRESHOLD = 0.6
DRONE_DETECTION_MIN_AREA = 0.001
```

---

## 📊 Performance Optimization

### For Real-Time Processing

```python
# Fast mode for live surveys
FAST_MODE = True
FAST_IMG_SIZE_YOLO = 320
DETECTION_FRAME_SKIP = 3

# GPU acceleration
USE_CUDA = True  # Requires CUDA-enabled OpenCV
```

### For High-Accuracy Post-Processing

```python
# Process recorded video offline
FAST_MODE = False
IMG_SIZE_YOLO = 608
DETECTION_FRAME_SKIP = 1
```

---

## 📈 Survey Statistics

After each survey, you get:

```python
{
    'duration': 600.5,           # seconds
    'frames_processed': 12000,
    'total_detections': 47,
    'fps': 19.98,
    'survey_area': 'calculated'
}
```

All detections saved to database with:
- GPS coordinates (ground position)
- Altitude
- Timestamp
- Confidence score
- Severity level
- Image snapshot

---

## 🎓 Best Practices

### Pre-Flight Checklist
1. ✅ Test video stream before takeoff
2. ✅ Verify GPS signal (minimum 8 satellites)
3. ✅ Check battery level
4. ✅ Confirm network connectivity
5. ✅ Test detection system on ground

### During Flight
1. 📏 Maintain consistent altitude
2. 🐢 Fly at moderate speed (5 m/s recommended)
3. 📊 Monitor detection count
4. 🔋 Watch battery levels
5. 📡 Ensure stable video stream

### Post-Flight
1. 📁 Verify video saved
2. 🗺️ Check detections on map
3. 📊 Review statistics
4. 💾 Backup database
5. 🔋 Recharge batteries

---

## 🌐 Integration with Web Dashboard

View drone detections in real-time:

1. Start app: `python app.py`
2. Open dashboard: http://localhost:5000/dashboard
3. Detections appear on map as drone surveys
4. Filter by source: "drone"
5. View flight path and coverage

---

## 📚 Additional Resources

### Documentation
- `README.md` - General system overview
- `DEPLOY_GUIDE.md` - Deployment instructions
- `GPS_SETUP_GUIDE.md` - GPS configuration

### Example Scripts
- `src/drone_detector.py` - Main drone detection
- `src/drone_controller.py` - Drone control interface
- `test_drone_stream.py` - Test video streams

### Video Tutorials
- Setting up RTSP stream
- MAVLink integration
- Mission planning
- Post-processing workflow

---

## 🆘 Support

**Drone Issues:**
- Check manufacturer documentation
- Verify firmware version
- Test with manufacturer's app first

**ASTROPATH Issues:**
- Email: 438malludiswardhanreddy@gmail.com
- Check logs: `astropath.log`
- Run with debug: `DEBUG_MODE = True`

---

## 🚀 Quick Start Commands

```bash
# Test drone stream
python -c "import cv2; cap = cv2.VideoCapture('rtsp://192.168.1.100:8554/video'); print('Connected!' if cap.isOpened() else 'Failed')"

# Run detection
python src/drone_detector.py

# Web interface
python app.py
# Then open http://localhost:5000
```

---

## ✅ Checklist

Before first drone survey:
- [ ] Drone video stream working
- [ ] YOLO model downloaded
- [ ] GPS coordinates accurate
- [ ] Network connection stable
- [ ] Battery fully charged
- [ ] Flight permissions obtained
- [ ] Safety area clear

---

**Ready for Aerial Road Inspection! 🚁**

**ASTROPATH** - Smart Road Damage Detection from the Sky
© 2026 Solapur Municipal Corporation
