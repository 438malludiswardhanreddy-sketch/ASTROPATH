# 🚀 ASTROPATH Quick Reference Guide

Fast access to common commands and configurations for ASTROPATH pothole detection system.

---

## ⚡ Quick Commands

### Start Dashboard (Map with GPS detections)
```bash
python main.py
# Select: 3. Start Dashboard
# Open: http://localhost:5000
```

### Run Edge Detection (with GPS tracking)
```bash
python main.py
# Select: 2. Run Edge Detection
```

### Test GPS Module
```bash
python main.py
# Select: 6. Test GPS Handler
```

### Test ESP32-CAM
```bash
python main.py
# Select: 7. Test ESP32-CAM Connection
```

### Train Classifier
```bash
python main.py
# Select: 1. Train Pothole Classifier
```

### Citizen Reporting App
```bash
python main.py
# Select: 4. Start Citizen Reporting App
# Open: http://localhost:5000
```

---

## 🔧 Configuration Essentials

### GPS Setup (config.py)
```python
GPS_ENABLED = True
GPS_PORT = '/dev/serial0'      # Linux/Pi
# GPS_PORT = '/dev/ttyACM0'    # USB connection
# GPS_PORT = 'COM3'            # Windows
GPS_BAUD = 9600
GPS_MIN_SATS = 4
GPS_MIN_QUALITY = 1
```

### ESP32-CAM Setup (config.py)
```python
# Add to config or update detect_edge.py
ESP32_HOST = "192.168.1.100"
ESP32_PORT = 80
ESP32_STREAM_PATH = "/stream"
```

### Dashboard Setup (config.py)
```python
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
```

### Detection Settings (config.py)
```python
CONF_THRESHOLD = 0.5           # Confidence threshold
NMS_THRESHOLD = 0.4            # Non-max suppression
DETECTION_FRAME_SKIP = 5       # Process every Nth frame
```

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/detections` | GET | Fetch detections with GPS coords |
| `/api/detections` | POST | Add new detection |
| `/api/detections/<id>` | GET | Fetch single detection details |
| `/api/detections/area` | GET | Query GPS area bounds |
| `/api/heatmap` | GET | Get heatmap data (severity weighted) |
| `/api/statistics` | GET | Get dashboard statistics |
| `/api/detections/<id>/status` | PUT | Update repair status |

### Example: Fetch GPS Detections
```bash
curl "http://localhost:5000/api/detections?limit=50"
```

### Example: Add Detection with GPS
```bash
curl -X POST http://localhost:5000/api/detections \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-02-01T10:30:00",
    "latitude": 17.3629,
    "longitude": 75.8930,
    "severity": "High",
    "confidence": 0.95,
    "gps_quality": 2
  }'
```

---

## 🎯 GPS Module Selection

| Module | Price | Accuracy | Notes |
|--------|-------|----------|-------|
| u-blox NEO-6M | ₹500-800 | 2-5m | Most popular, reliable |
| Adafruit GPS | ₹800-1200 | 2-10m | Easy setup, I2C/USB |
| Beitian BN-220 | ₹600-900 | 2-5m | High update rate (10Hz) |
| Generic NMEA | ₹300-500 | 5-20m | Variable quality |

---

## 📷 ESP32-CAM Quick Setup

### 1. Flash Firmware
```bash
# Using Arduino IDE:
# - Tools → Board → AI Thinker ESP32-CAM
# - Upload CameraWebServer example
# - Add WiFi credentials in sketch
```

### 2. Connect to WiFi
```cpp
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
```

### 3. Find IP Address
- Check Serial Monitor after upload
- Check router's connected devices

### 4. Access Stream
```
http://192.168.1.100:81/stream     # MJPEG stream
http://192.168.1.100:81/capture    # Single JPEG
http://192.168.1.100:81            # Control panel
```

---

## 🗂️ Project Structure Cheat Sheet

```
ASTROPATH/
├── main.py                 ← Start here (menu system)
├── config.py              ← Edit configurations
├── requirements.txt       ← Install with: pip install -r
│
├── src/
│   ├── database.py        ← Detections storage (SQLite)
│   ├── dashboard.py       ← Web server (Flask)
│   ├── gps_handler.py     ← GPS communication
│   ├── esp32_camera.py    ← ESP32-CAM streaming
│   ├── detect_edge.py     ← Main detection pipeline
│   ├── api_client.py      ← Cloud API communication
│   └── utils.py           ← Helper functions
│
├── templates/
│   └── dashboard.html     ← Web UI
│
├── static/
│   ├── css/dashboard.css
│   └── js/dashboard.js
│
├── models/                ← Download YOLO weights here
│   ├── yolov4-tiny.weights
│   ├── yolov4-tiny.cfg
│   └── obj.names
│
└── data/                  ← Training & test data
    └── training_images/
        ├── pothole/
        └── plain/
```

---

## 🐛 Quick Troubleshooting

### GPS Not Connecting
```bash
# List available ports
ls /dev/tty*              # Linux
Get-SerialPort            # PowerShell (Windows)

# Verify baud rate matches module (usually 9600)
# Check config.py GPS_PORT setting
```

### ESP32-CAM Not Found
```bash
# Test connectivity
ping 192.168.1.100

# Check camera at web address
# http://192.168.1.100:81

# Verify WiFi network & password correct
```

### Dashboard Not Loading
```bash
# Check API is working
curl http://localhost:5000/api/detections

# Verify database exists
ls -la detections.db

# Check logs
tail -f astropath.log
```

### Low Detections/FPS
```python
# In config.py:
IMG_SIZE_YOLO = 320         # Reduce from 416
DETECTION_FRAME_SKIP = 5    # Skip more frames
PI_OPTIMIZE = True          # Enable Pi optimizations
```

---

## 📱 GPS Data in Dashboard

Each detection on the map shows:
- **📍 Coordinates:** Latitude, Longitude (6 decimals)
- **🛰️ GPS Quality:** Fix type (0=None, 1=GPS, 2=DGPS)
- **⏰ Timestamp:** UTC time from GPS
- **🎯 Severity:** High/Medium/Low with color coding
- **✓ Confidence:** AI model score (0-100%)

---

## 🔌 Database Queries

### View Recent Detections
```python
from src.database import DetectionDatabase

db = DetectionDatabase()

# Get high-severity detections
high_detections = db.get_detections_by_severity("High", limit=10)
for det in high_detections:
    print(f"{det['latitude']:.6f}, {det['longitude']:.6f}")

# Get detections in GPS area
area_detections = db.get_detections_by_area(17.36, 17.37, 75.88, 75.89)

# Get statistics
stats = db.get_statistics(days=7)
print(f"Total: {stats['total_detections']}")
print(f"High severity: {stats['high_severity']}")

db.close()
```

---

## 📦 Installation Checklist

- [ ] Clone/download ASTROPATH
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate: `source venv/bin/activate`
- [ ] Install: `pip install -r requirements.txt`
- [ ] Download YOLO weights to `models/`
- [ ] Edit `config.py` with your settings
- [ ] Test dashboard: `python main.py` → option 3
- [ ] Test GPS: `python main.py` → option 6
- [ ] Test ESP32: `python main.py` → option 7
- [ ] Ready for production deployment!

---

## 🎯 Key Filenames to Remember

| File | Purpose |
|------|---------|
| `main.py` | Main menu entry point |
| `config.py` | All settings (edit here!) |
| `detections.db` | Detection database (auto-created) |
| `astropath.log` | System logs |
| `dashboard.html` | Web UI template |
| `dashboard.js` | Interactive map code |

---

## 🌐 URLs to Access

| Service | URL |
|---------|-----|
| Dashboard | `http://localhost:5000` |
| API Base | `http://localhost:5000/api` |
| ESP32-CAM Stream | `http://192.168.1.100:81/stream` |
| ESP32-CAM Control | `http://192.168.1.100:81` |

---

## 💡 Pro Tips

1. **Use GPS mode 1 or 2** - Mode 1 (GPS Fix) is sufficient for pothole mapping
2. **Adjust DETECTION_FRAME_SKIP** - Higher values = faster but fewer detections
3. **Place GPS near camera** - Reduces error in detection coordinates
4. **Multi-camera setup** - Add multiple ESP32-CAM boards via config
5. **Dashboard auto-refresh** - Pauses when browser tab not active
6. **Enable debug mode** - Set `DEBUG_MODE = True` in config.py for verbose logs

---

**Need help?** Check [README_COMPLETE.md](README_COMPLETE.md) or [ESP32_CAM_SETUP.md](ESP32_CAM_SETUP.md)

**Ready to start?** Run `python main.py` now! 🚀
