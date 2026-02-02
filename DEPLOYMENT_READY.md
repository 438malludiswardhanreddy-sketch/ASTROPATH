# 🚨 ASTROPATH - Real-Time Deployment Ready! 🚀

## ✅ What's New - Real-Time Web Application

Your ASTROPATH system is now **fully deployable** with:

### 🎯 Key Features
- ✅ **Real-time camera detection** (Webcam, ESP32-CAM, Phone)
- ✅ **Live GPS tracking** (Hardware GPS or IP-based fallback)
- ✅ **Interactive dashboard** with real-time map visualization
- ✅ **Mobile-friendly** citizen reporting
- ✅ **RESTful API** for integrations
- ✅ **Docker support** for easy deployment
- ✅ **Production-ready** configuration

---

## 🚀 Quick Start (2 Minutes!)

### Windows
```powershell
# Just run this:
.\start.ps1
```

### Linux/Mac
```bash
# Make executable and run:
chmod +x start.sh
./start.sh
```

That's it! The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install dependencies
4. ✅ Download YOLO model (optional)
5. ✅ Start the application

**Access at:** http://localhost:5000

---

## 📱 Access from Your Phone

1. Run the app on your PC (using `start.ps1` or `start.sh`)
2. The script will show your IP address (e.g., `192.168.1.100`)
3. On your phone, open browser: `http://YOUR_IP:5000`
4. Use your phone's camera to report potholes!

---

## 🌐 Pages Available

| Page | URL | Description |
|------|-----|-------------|
| **Main Interface** | `/` | Live camera detection, citizen reporting |
| **Dashboard** | `/dashboard` | Real-time map with all detections |
| **API Health** | `/health` | System health status |
| **API Detections** | `/api/detections` | Get all detections (JSON) |
| **API Stats** | `/api/stats` | Get statistics (JSON) |
| **API Location** | `/api/location` | Get current GPS location (JSON) |

---

## 📸 Camera Options

The system supports multiple camera sources:

### Option 1: Webcam (Default)
```python
# config.py
CAMERA_SOURCE = 0  # Built-in webcam
CAMERA_SOURCE = 1  # External USB camera
```

### Option 2: ESP32-CAM
```python
# config.py
CAMERA_SOURCE = "http://192.168.1.100:81/stream"
```
See `ESP32_CAM_SETUP.md` for setup instructions.

### Option 3: Phone Camera
- Open the web interface on your phone
- Click "Report" button
- Use camera directly from browser
- GPS location automatically captured

---

## 🛰️ GPS Options

### Option 1: IP-based Geolocation (Default)
```python
# config.py
GPS_ENABLED = False
GPS_FALLBACK_TO_IP = True
```
Automatically detects location from IP address.

### Option 2: Real GPS Module
```python
# config.py
GPS_ENABLED = True
GPS_PORT = 'COM3'  # Windows: COM3, Linux: /dev/ttyUSB0
GPS_BAUD = 9600
```

Test GPS:
```bash
python test_gps.py
```

---

## 🐳 Docker Deployment

### Quick Deploy
```bash
docker-compose up -d
```

### Custom Build
```bash
# Build
docker build -t astropath:latest .

# Run
docker run -d -p 5000:5000 astropath:latest
```

---

## 🌍 Production Deployment

### Option 1: Local Network (Home/Office)
```powershell
# Windows
.\start.ps1

# Linux
./start.sh
```
Access from any device on your network.

### Option 2: Cloud Deployment

#### Heroku
```bash
heroku create astropath-app
git push heroku main
```

#### AWS EC2
```bash
# See DEPLOY_GUIDE.md for complete instructions
ssh ubuntu@your-ec2
git clone YOUR_REPO
./start.sh
```

#### DigitalOcean / Linode
```bash
# Same as AWS EC2
# Complete guide in DEPLOY_GUIDE.md
```

---

## 📊 How It Works

### 1. Detection Flow
```
Camera Feed → YOLO Detection → Classification → GPS Location → Database → Dashboard
```

### 2. System Architecture
```
┌─────────────────┐
│   Web Browser   │ ← User Interface (HTML/CSS/JS)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Flask App     │ ← app.py (Main Application)
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌────────┐
│  YOLO  │ │  GPS   │ ← Detection & Location
└────────┘ └────────┘
         │
         ↓
┌─────────────────┐
│   Database      │ ← SQLite (detections.db)
└─────────────────┘
```

### 3. Real-time Updates
- Video feed: Live MJPEG stream
- Dashboard: Auto-refresh every 30s
- API: RESTful JSON endpoints

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Camera
CAMERA_SOURCE = 0  # 0=webcam, 1=external, URL=IP camera

# Detection
CONF_THRESHOLD = 0.5  # Lower = more detections
FAST_MODE = True      # Better FPS on slow systems

# GPS
GPS_ENABLED = False   # Enable for real GPS
GPS_PORT = 'COM3'     # Serial port

# Server
FLASK_HOST = "0.0.0.0"  # Allow network access
FLASK_PORT = 5000        # Port number
```

---

## 📁 Project Structure

```
ASTROPATH-1/
├── app.py                    # 🆕 Main web application
├── start.ps1                 # 🆕 Windows quick start
├── start.sh                  # 🆕 Linux quick start
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── DEPLOY_GUIDE.md          # 🆕 Complete deployment guide
├── Dockerfile               # 🆕 Docker configuration
├── docker-compose.yml       # 🆕 Docker Compose
│
├── templates/               # 🆕 HTML templates
│   ├── index.html          # Main interface
│   └── dashboard.html      # Dashboard with map
│
├── static/                  # 🆕 Static files
│   ├── css/
│   │   └── style.css       # Modern dark theme
│   └── js/
│       ├── app.js          # Main app logic
│       └── dashboard.js    # Dashboard with maps
│
├── src/                     # Source code
│   ├── detect_edge.py      # Detection engine
│   ├── gps_handler.py      # GPS integration
│   ├── database.py         # Database operations
│   └── ...
│
├── models/                  # AI models
│   ├── yolov4-tiny.weights # Download required
│   ├── yolov4-tiny.cfg     # Included
│   └── obj.names           # Included
│
├── detections/             # Saved detections
├── uploads/                # Citizen uploads
└── detections.db          # SQLite database
```

---

## 🎨 User Interface

### Modern Features
✅ **Dark Theme** - Premium dark mode design
✅ **Responsive** - Works on desktop, tablet, and mobile
✅ **Real-time** - Live video feed and updates
✅ **Interactive Map** - Leaflet.js with heatmaps
✅ **Smooth Animations** - Modern transitions and effects
✅ **Mobile Camera** - Direct camera access from phone

---

## 📈 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/detections` | GET | Get all detections |
| `/api/heatmap` | GET | Get heatmap data |
| `/api/stats` | GET | Get statistics |
| `/api/location` | GET | Get current GPS location |
| `/api/upload` | POST | Upload citizen report |
| `/api/start_detection` | POST | Start detection |
| `/api/stop_detection` | POST | Stop detection |
| `/health` | GET | System health check |

### Example API Usage

```javascript
// Get all detections
fetch('/api/detections?limit=10')
  .then(res => res.json())
  .then(data => console.log(data));

// Upload a report
fetch('/api/upload', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    image: base64Image,
    severity: 'High',
    description: 'Large pothole'
  })
});
```

---

## 🔒 Security Notes

For production:
1. Change secret key in `app.py`
2. Set `FLASK_DEBUG = False` in `config.py`
3. Use HTTPS (SSL certificate)
4. Set up firewall rules
5. Use PostgreSQL instead of SQLite for high traffic

See `DEPLOY_GUIDE.md` for complete security checklist.

---

## 🐛 Troubleshooting

### Camera not working
```bash
# Test camera
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### Port already in use
```powershell
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### YOLO model missing
Download from: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights  
Save to: `models/yolov4-tiny.weights`

### GPS not connecting
```bash
python test_gps.py
```

### Low FPS
```python
# config.py
FAST_MODE = True
FAST_IMG_SIZE_YOLO = 320
DETECTION_FRAME_SKIP = 3
```

---

## 📚 Documentation

- `README.md` - This file (Quick start)
- `DEPLOY_GUIDE.md` - Complete deployment guide
- `ESP32_CAM_SETUP.md` - ESP32-CAM setup
- `GPS_SETUP_GUIDE.md` - GPS configuration
- `QUICK_START.md` - Quick reference

---

## 🎯 What You Can Do Now

### Immediate Use
1. ✅ Run locally: `.\start.ps1` (Windows) or `./start.sh` (Linux)
2. ✅ Access from phone on same WiFi
3. ✅ Start detecting potholes with webcam
4. ✅ Report potholes via mobile browser

### Next Steps
1. 🔧 Connect ESP32-CAM for outdoor detection
2. 🛰️ Add GPS module for accurate location
3. ☁️ Deploy to cloud (Heroku, AWS, etc.)
4. 📊 Add more training data
5. 🚁 Integrate with drone

---

## 💡 Use Cases

### 1. Municipal Corporation
- Deploy on patrol vehicles
- Citizen reporting via mobile
- Real-time dashboard for authorities
- Automated work order generation

### 2. Research Project
- Collect road condition data
- Train better models
- Analyze road deterioration patterns

### 3. Citizen Initiative
- Community reporting
- Local government awareness
- Data-driven road maintenance requests

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- [ ] User authentication
- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] ML model improvements
- [ ] Multi-language support

---

## 📄 License

ASTROPATH - Smart Road Damage Reporting System  
© 2026 Solapur Municipal Corporation

**Lead:** Mallu Diswardhan Reddy  
**Email:** 438malludiswardhanreddy@gmail.com

---

## 🌟 Credits

- **YOLOv4-tiny**: AlexeyAB/Darknet
- **Leaflet.js**: Interactive maps
- **OpenCV**: Computer vision
- **TensorFlow**: Machine learning
- **Flask**: Web framework

---

## 🚀 Ready to Deploy!

Your ASTROPATH system is now **production-ready**!

### Quick Deploy Commands

```powershell
# Windows - Local
.\start.ps1

# Linux - Local  
./start.sh

# Docker - Any Platform
docker-compose up -d

# Cloud - Heroku
git push heroku main
```

**Made with ❤️ for Smart Cities**
