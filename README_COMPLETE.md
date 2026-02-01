# 🚨 ASTROPATH - Smart Road Damage Reporting & Rapid Response System

**A complete smart city solution for automated pothole and road damage detection, reporting, and management** with GPS tracking, real-time dashboard, and ESP32-CAM integration.

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Quick Start](#quick-start)
5. [Complete Setup Guide](#complete-setup-guide)
6. [Module Documentation](#module-documentation)
7. [GPS Integration](#gps-integration)
8. [ESP32-CAM Integration](#esp32-cam-integration)
9. [Dashboard](#dashboard)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [Deployment](#deployment)

---

## 🎯 Overview

ASTROPATH is an integrated platform designed for **Solapur Municipal Corporation** (and scalable to any city) that:

- **🎥 Detects** potholes using YOLOv4-tiny + CNN classifier
- **🛰️ Tracks locations** via GPS (u-blox, Adafruit GPS modules)
- **📍 Maps detections** on real-time dashboard with coordinates
- **👥 Enables citizen reporting** via web form with geolocation
- **📊 Provides analytics** with severity heatmaps
- **🔧 Tracks repairs** with status updates
- **📹 Supports ESP32-CAM** for wireless video streaming
- **🚀 Processes on edge** (Raspberry Pi) for low-latency response

---

## ✨ Key Features

### 🎯 Dual Detection Modes
- **Autonomous Edge Detection** (Pi-based with ESP32-CAM)
- **Citizen Crowdsourcing** via mobile browser with GPS

### 🗺️ GPS Integration
- Real GPS module support (u-blox NEO-6M, Adafruit GPS)
- NMEA sentence parsing (GGA, RMC)
- Quality indicators (number of satellites, fix type)
- Fallback to cached positions
- IP geolocation fallback

### 📱 ESP32-CAM Support
- WiFi-based video streaming
- MJPEG stream parsing
- Multi-camera controller
- Real-time frame capture
- Resolution management

### 📊 Real-Time Dashboard
- **Interactive Leaflet map** with marker clustering
- **GPS coordinate visualization** for each detection
- **Severity heatmaps** (High/Medium/Low)
- **Statistics panel** with repair tracking
- **Auto-refresh** with 30-second intervals
- **Filterable list** by severity and time range

### 🔍 Advanced Analysis
- Transfer learning classifier (MobileNetV2)
- Multi-class severity estimation
- Area-based severity calculation
- Confidence scoring
- Timestamp tracking with GPS quality

### 💾 Database System
- SQLite database for all detections
- GPS quality logging
- Repair tracking
- Analytics aggregation
- Indexed queries for fast retrieval

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ASTROPATH System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Input Sources                                │  │
│  │  ┌─────────────┐  ┌──────────┐  ┌─────────────┐    │  │
│  │  │ ESP32-CAM   │  │ Webcam   │  │ GPS Module  │    │  │
│  │  │ (WiFi)      │  │ (Local)  │  │ (UART)      │    │  │
│  │  └─────────────┘  └──────────┘  └─────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │    Edge Detection Pipeline (detect_edge.py)         │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │ YOLO Detector│  │ GPS Handler  │                │  │
│  │  │ (localize)   │  │ (coordinates)│                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  │           ▼                 ▼                        │  │
│  │  ┌─────────────────────────────────┐                │  │
│  │  │ Severity Estimator (Area-based) │                │  │
│  │  └─────────────────────────────────┘                │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │    Detection Output (with GPS coords)                │  │
│  │  - Location (lat, lon, quality)                     │  │
│  │  - Severity (High/Medium/Low)                       │  │
│  │  - Confidence Score                                 │  │
│  │  - Timestamp                                        │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│          ┌───────────────┼───────────────┐                │
│          │               │               │                │
│          ▼               ▼               ▼                │
│    ┌─────────┐    ┌──────────┐   ┌────────────┐         │
│    │ Database │    │ Dashboard│   │ API Client │         │
│    │(SQLite)  │    │(Flask UI)│   │(Cloud)     │         │
│    └─────────┘    └──────────┘   └────────────┘         │
│          │               │               │                │
│          └───────────────┼───────────────┘                │
│                          │                                │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │      Output Visualization & Tracking                │  │
│  │  - Real-time map with GPS markers                  │  │
│  │  - Repair status management                        │  │
│  │  - Statistics & heatmaps                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows/Linux/Raspberry Pi OS
- pip (Python package manager)

### Step 1: Installation

```bash
# Navigate to project directory
cd ASTROPATH

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download Model Files

```bash
# Create models directory (if needed)
mkdir -p models

# Download YOLOv4-tiny weights (~196 MB)
# Option A: Using wget
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -O models/yolov4-tiny.weights

# Option B: Manual download from browser
# https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
```

### Step 3: Launch Dashboard

```bash
# Start the dashboard server
python main.py
# Select option 3 from menu
```

**Dashboard URL:** `http://localhost:5000`

### Step 4: Start Detection

```bash
# In another terminal:
python main.py
# Select option 2 to run edge detection
```

---

## 📚 Complete Setup Guide

### Project Structure

```
ASTROPATH/
│
├── main.py                          # Entry point with menu system
├── config.py                        # Centralized configuration
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── ESP32_CAM_SETUP.md              # ESP32-CAM detailed guide
│
├── src/                            # Source modules
│   ├── __init__.py
│   ├── utils.py                    # Utilities (logging, geolocation, etc.)
│   ├── database.py                 # SQLite database for detections
│   ├── dashboard.py                # Flask dashboard server
│   ├── detect_edge.py              # Edge detection pipeline
│   ├── gps_handler.py              # GPS module communication
│   ├── esp32_camera.py             # ESP32-CAM integration
│   ├── api_client.py               # Cloud API communication
│   ├── train_classifier.py         # ML model training
│   ├── citizen_upload.py           # Citizen web app
│   └── __pycache__/
│
├── models/                          # ML models
│   ├── yolov4-tiny.weights         # YOLO detector weights
│   ├── yolov4-tiny.cfg             # YOLO configuration
│   ├── obj.names                   # Class names
│   └── custom_classifier.h5        # Pothole classifier
│
├── data/                            # Data storage
│   ├── training_images/
│   │   ├── pothole/                # Pothole images
│   │   └── plain/                  # Plain road images
│   └── test.mp4                    # Test video
│
├── templates/                       # Flask HTML templates
│   └── dashboard.html              # Dashboard webpage
│
├── static/                          # Frontend assets
│   ├── css/
│   │   └── dashboard.css           # Dashboard styling
│   └── js/
│       └── dashboard.js            # Dashboard interactivity
│
├── detections/                      # Output detection results
└── uploads/                         # Citizen-submitted images
```

---

## 📖 Module Documentation

### 1. GPS Handler (`src/gps_handler.py`)

Real-time GPS coordinate acquisition from serial modules.

**Supported GPS Modules:**
- u-blox NEO-6M / NEO-M8N (~₹500-1500)
- Adafruit Ultimate GPS
- Beitian BN-220 series
- Any NMEA-compatible module

**Usage:**
```python
from src.gps_handler import GPSHandler

gps = GPSHandler(port='/dev/ttyACM0', baud=9600)
latitude, longitude, timestamp, quality = gps.get_coordinates()

if quality >= 1:  # GPS_FIX or better
    print(f"Position: {latitude:.6f}, {longitude:.6f}")
    print(f"Time: {timestamp}, Quality: {quality}")
```

**Key Features:**
- Thread-safe NMEA parsing
- Quality indicators (0-8 levels)
- Satellite count tracking
- Fallback to cached positions
- Automatic reconnection

### 2. ESP32-CAM Integration (`src/esp32_camera.py`)

WiFi-based video streaming from ESP32-CAM boards.

**Supported Boards:**
- ESP32-CAM (OV2640)
- ESP32-S3-CAM (better performance)

**Usage:**
```python
from src.esp32_camera import ESP32Camera

camera = ESP32Camera(host="192.168.1.100", port=80)
if camera.connect():
    frame = camera.get_frame()
    camera.capture_frame("snapshot.jpg")
```

**Multi-Camera Support:**
```python
from src.esp32_camera import MultiCameraController

controller = MultiCameraController()
controller.add_camera("front", "192.168.1.100")
controller.add_camera("back", "192.168.1.101")

frames = controller.get_all_frames()  # Get from all cameras
```

### 3. Database (`src/database.py`)

SQLite database for storing detection records with GPS data.

**Tables:**
- `detections` - Main detection records
- `gps_quality_log` - GPS quality tracking
- `repairs` - Repair history
- `analytics` - Aggregated statistics

**Usage:**
```python
from src.database import DetectionDatabase

db = DetectionDatabase("detections.db")

# Add detection
db.add_detection({
    'timestamp': '2026-02-01T10:30:00',
    'latitude': 17.3629,
    'longitude': 75.8930,
    'severity': 'High',
    'confidence': 0.95,
    'gps_quality': 2
})

# Query detections
detections = db.get_detections_by_area(17.36, 17.37, 75.88, 75.89)
stats = db.get_statistics(days=30)
heatmap = db.get_heatmap_data()

db.close()
```

### 4. Dashboard (`src/dashboard.py`)

Flask web server for real-time visualization.

**API Endpoints:**
- `GET /api/detections` - Fetch detections
- `POST /api/detections` - Add detection
- `GET /api/heatmap` - Get heatmap data
- `GET /api/statistics` - Get statistics
- `PUT /api/detections/<id>/status` - Update repair status

**Running:**
```bash
python main.py
# Choose option 3: Start Dashboard
# Then open: http://localhost:5000
```

### 5. Edge Detection (`src/detect_edge.py`)

Main detection pipeline integrating YOLO, GPS, and ESP32-CAM.

**Features:**
- Real-time YOLO detection
- GPS coordinate logging
- Severity estimation
- Database storage
- API upload (when ready)

**Running with different inputs:**
```bash
# Webcam
python src/detect_edge.py

# ESP32-CAM (update config first)
# In config.py: CAMERA_SOURCE = "http://192.168.1.100:81/stream"
python src/detect_edge.py

# Video file
# In config.py: CAMERA_SOURCE = "test_video.mp4"
python src/detect_edge.py
```

---

## 🛰️ GPS Integration

### Hardware Setup

1. **Purchase GPS Module:**
   - u-blox NEO-6M: ₹500-800
   - Adafruit Ultimate GPS: ₹800-1200
   
2. **Connect to Raspberry Pi:**
   ```
   GPS Module          Raspberry Pi
   VCC (3.3V)  ──→  Pin 1 (3.3V)
   GND         ──→  Pin 6 (GND)
   TX          ──→  Pin 10 (RX/GPIO15)
   RX          ──→  Pin 8 (TX/GPIO14)
   ```

3. **Enable UART:**
   ```bash
   sudo raspi-config
   # Interface Options → Serial → Enable
   ```

4. **Test Connection:**
   ```bash
   python main.py
   # Select option 6: Test GPS Handler
   ```

### Configuration

Edit `config.py`:
```python
GPS_ENABLED = True
GPS_PORT = '/dev/serial0'  # or '/dev/ttyACM0' for USB
GPS_BAUD = 9600
GPS_MIN_SATS = 4
GPS_MIN_QUALITY = 1
```

### Test Script

```python
from src.gps_handler import GPSHandler

gps = GPSHandler()
for i in range(10):
    lat, lon, ts, quality = gps.get_coordinates()
    print(f"{i}: ({lat:.6f}, {lon:.6f}) Quality={quality}")
    
gps.close()
```

---

## 📷 ESP32-CAM Integration

### Complete Setup

1. **Flash firmware** (see [ESP32_CAM_SETUP.md](ESP32_CAM_SETUP.md))
2. **Connect to WiFi**
3. **Find IP address** from router or serial monitor
4. **Test in browser:** `http://192.168.1.100:81`

### Configuration

Edit `config.py`:
```python
ESP32_HOST = "192.168.1.100"
ESP32_PORT = 80
ESP32_STREAM_PATH = "/stream"
```

### Testing

```bash
python main.py
# Select option 7: Test ESP32-CAM Connection
```

### Integration with Detection

Automatic in `detect_edge.py`:
```python
from src.esp32_camera import ESP32Camera

camera = ESP32Camera(host="192.168.1.100")
camera.connect()

# Frames are automatically used in detection pipeline
```

---

## 📊 Dashboard

### Accessing the Dashboard

```bash
python main.py
# Select: 3. Start Dashboard

# Open browser: http://localhost:5000
```

### Features

**🗺️ Interactive Map**
- Marker clustering
- Severity color coding
- Pop-up with detection details
- Click to view full details

**📈 Statistics Panel**
- Total detections
- Severity breakdown
- Repair tracking
- Time-based filtering

**🔍 Filters**
- By severity (High/Medium/Low)
- By time range (1hr, 24hr, week, month)
- By GPS area bounds

**🔄 Auto-refresh**
- Refreshes every 30 seconds
- Pauses when tab inactive
- Manual refresh button

### GPS Data Display

Each detection shows:
- **Coordinates:** Latitude & Longitude (6 decimal precision)
- **GPS Quality:** 0-8 scale (0=No Fix, 1=GPS Fix, 2=DGPS, etc.)
- **Timestamp:** Precise UTC time from GPS
- **Confidence:** AI model confidence (0-100%)
- **Severity:** Low/Medium/High based on area

---

## 🔌 API Reference

### Report Detection

```http
POST /api/detections
Content-Type: application/json

{
  "timestamp": "2026-02-01T10:30:00",
  "latitude": 17.3629,
  "longitude": 75.8930,
  "severity": "High",
  "confidence": 0.95,
  "class_name": "pothole",
  "camera_source": "esp32_cam_front",
  "gps_quality": 2
}
```

### Get Detections

```http
GET /api/detections?limit=100&severity=High&hours=24
```

### Get Heatmap Data

```http
GET /api/heatmap?limit=500
```

### Update Repair Status

```http
PUT /api/detections/123/status
Content-Type: application/json

{
  "status": "completed",
  "notes": "Filled with asphalt"
}
```

### Get Statistics

```http
GET /api/statistics?days=30
```

---

## 🧪 Testing & Troubleshooting

### Test GPS

```bash
python main.py
# Select: 6. Test GPS Handler
```

### Test ESP32-CAM

```bash
python main.py
# Select: 7. Test ESP32-CAM Connection
```

### View Logs

```bash
# Real-time logging
tail -f astropath.log

# View specific errors
grep ERROR astropath.log
```

### Common Issues

**Dashboard not loading?**
- Check: `http://localhost:5000/api/detections`
- Verify database exists: `ls -la detections.db`

**GPS not connecting?**
- Check port: `ls /dev/tty*` (Linux) or Device Manager (Windows)
- Verify baud rate matches GPS module
- Try different cable

**ESP32-CAM connection failed?**
- Verify IP address is correct
- Check both devices on same WiFi
- Try: `ping 192.168.1.100`
- Restart ESP32-CAM

**No detections appearing?**
- Verify camera is working
- Check YOLO model files exist
- Enable debug mode in config.py

---

## 🚀 Deployment

### Raspberry Pi Deployment

1. **Install on Pi:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   git clone <repo-url>
   cd ASTROPATH
   pip install -r requirements.txt
   ```

2. **Configure for Pi:**
   ```python
   # config.py
   PI_OPTIMIZE = True
   IMG_SIZE_YOLO = 320
   DETECTION_FRAME_SKIP = 2
   GPS_ENABLED = True
   GPS_PORT = '/dev/serial0'
   ```

3. **Run as service:**
   ```bash
   sudo nano /etc/systemd/system/astropath.service
   ```
   
   ```ini
   [Unit]
   Description=ASTROPATH Detection Service
   After=network.target
   
   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/ASTROPATH
   ExecStart=/usr/bin/python3 /home/pi/ASTROPATH/main.py
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   sudo systemctl enable astropath
   sudo systemctl start astropath
   ```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 📋 Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] YOLO model files downloaded
- [ ] config.py configured
- [ ] Database created: `src/database.py` auto-creates
- [ ] Dashboard tested: http://localhost:5000
- [ ] GPS module (if using): tested and connected
- [ ] ESP32-CAM (if using): configured and accessible
- [ ] Detection pipeline tested
- [ ] Logs reviewed: `astropath.log`

---

## 📞 Support & Resources

### Documentation
- [ESP32-CAM Setup Guide](ESP32_CAM_SETUP.md)
- [Main README](README.md)
- Configuration examples in `config.py`

### External Resources
- [YOLOv4 Documentation](https://github.com/AlexeyAB/darknet)
- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Leaflet.js Maps](https://leafletjs.com/)

### Community
- GitHub Issues: Report bugs and feature requests
- Stack Overflow: General Python/TensorFlow questions
- Raspberry Pi Forums: Hardware-specific help

---

## 📄 License & Attribution

**ASTROPATH** - Smart Road Damage Reporting System  
**Version:** 1.0  
**Last Updated:** February 2026  

This project is open-source and scalable to any smart city. Attribution to ASTROPATH and contributing institutions is appreciated.

---

**Ready to deploy? Start with `python main.py` today!** 🚀
