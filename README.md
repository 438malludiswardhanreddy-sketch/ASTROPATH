# 🚨 ASTROPATH - Smart Road Damage Reporting & Rapid Response System

**A complete smart city solution for automated pothole and road damage detection, reporting, and management** combining citizen reporting, drone-based scanning, AI analysis, and cloud-based tracking.

## 📋 Project Overview

ASTROPATH is an integrated platform designed for **Solapur Municipal Corporation** (and scalable to any city) that:

- **Detects** potholes and road cracks using YOLOv4-tiny + CNN classifier
- **Estimates severity** using multi-factor analysis (area, confidence, depth)
- **Processes on edge** (Raspberry Pi, ESP32-CAM) for low-latency response
- **Enables citizen reporting** via web form with geolocation
- **Integrates drone surveillance** for high-coverage inspection
- **Tracks repairs** with before/after verification
- **Provides dashboard** for city officials with real-time heatmaps

### Key Features

✅ **Dual Detection Modes:**
- Autonomous edge detection (Pi-based surveillance)
- Citizen crowdsourcing via mobile browser

✅ **Advanced Analysis:**
- Transfer learning classifier (MobileNetV2)
- Multi-class severity estimation (Low/Medium/High)
- Simulated depth sensing (ultrasonic-ready)

✅ **Scalable Architecture:**
- Modular Python codebase
- Cloud API ready (Firebase/Google Cloud compatible)
- TFLite for embedded deployment

✅ **Smart Routing:**
- Geolocation via GPS or IP fallback
- Automatic drone deployment prioritization
- Repair crew optimization

---

## 🏗️ Project Structure

```
ASTROPATH/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                          # Centralized configuration
├── models/
│   ├── yolov4-tiny.weights           # Pre-trained YOLO weights
│   ├── yolov4-tiny.cfg               # YOLO architecture config
│   ├── obj.names                     # Class names (e.g., "pothole")
│   └── custom_classifier.h5          # Trained MobileNetV2 model
├── src/
│   ├── __init__.py
│   ├── utils.py                      # Logging, geolocation, image processing
│   ├── train_classifier.py           # Training script (improved from main.py)
│   ├── detect_edge.py                # Edge detection pipeline (Pi-ready)
│   ├── api_client.py                 # Cloud API communication
│   └── citizen_upload.py             # Flask web app for citizen reports
├── data/
│   ├── training_images/
│   │   ├── pothole/                  # Pothole images
│   │   └── plain/                    # Plain road images
│   └── test.mp4                      # Test video file
├── detections/                        # Output detections & frames
└── uploads/                           # Citizen-submitted images
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows/Linux/Raspberry Pi OS**
- **pip** (Python package manager)

### 1. Installation

```bash
# Clone or navigate to the repository
cd ASTROPATH

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Model Files

The repo requires pre-trained YOLOv4-tiny weights:

```bash
# Download YOLOv4-tiny weights (196 MB)
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
mv yolov4-tiny.weights models/

# YOLOv4-tiny config is already in repo
# YOLOv4-tiny class names (one per line)
echo "pothole" > models/obj.names
```

Or download via browser and place in `models/` folder.

### 3. Configuration

Edit `config.py` to customize:

```python
# Camera/Input
CAMERA_SOURCE = 0  # 0 = webcam, or "path/to/video.mp4"

# API Endpoint (set when cloud backend is ready)
API_URL = "http://your-server.com/api"
ENABLE_CLOUD_UPLOAD = False  # Set to True when ready

# Raspberry Pi
PI_OPTIMIZE = False  # Enable TFLite for edge devices

# Geolocation
USE_GPS_MODULE = False  # True if using real GPS on Pi
```

---

## 📖 Usage Guide

### A. Train Pothole Classifier

Prepare your dataset:
```
data/training_images/
├── pothole/  (100+ images)
└── plain/    (100+ images)
```

**Train the model:**

```bash
python src/train_classifier.py
```

**Output:**
- `models/custom_classifier.h5` - Trained model
- `models/custom_classifier.tflite` - Optimized for Raspberry Pi

### B. Run Edge Detection

**On Laptop/Desktop (with webcam):**

```bash
python src/detect_edge.py
```

**On Raspberry Pi:**

```bash
# Configure for Pi
# Edit config.py: PI_OPTIMIZE = True, CAMERA_SOURCE = 0

python src/detect_edge.py

# Press 'q' to quit
```

**On Drone (via video stream):**

```python
# In config.py, update:
# CAMERA_SOURCE = "udp://192.168.1.100:5000"  # Drone IP & port

python src/detect_edge.py
```

### C. Citizen Reporting (Web App)

Start the Flask web app:

```bash
python src/citizen_upload.py
```

**Access at:** `http://localhost:5000`

Features:
- 📍 Auto-detect user location (browser geolocation)
- 📸 Upload photo
- 📝 Add description
- 🚀 Submit report to cloud

### D. API Client (Cloud Integration)

```python
from src.api_client import APIClient

client = APIClient("http://your-cloud-server.com/api")

# Submit detection
success, response = client.report_detection({
    'latitude': 17.3629,
    'longitude': 75.8930,
    'severity': 'High',
    'confidence': 0.87,
    'image_path': 'path/to/image.jpg'
})

# Check repair status
success, data = client.get_detection_by_id('detection_123')

# Get heatmap
success, heatmap = client.get_heatmap_data()
```

---

## 🔧 Advanced Configuration

### Raspberry Pi Deployment

**1. Install TensorFlow Lite:**

```bash
pip install tensorflow-lite
```

**2. Enable Pi optimizations in `config.py`:**

```python
PI_OPTIMIZE = True
IMG_SIZE_YOLO = 320  # Smaller for faster inference
DETECTION_FRAME_SKIP = 2  # Process every 2nd frame
```

**3. Convert classifier to TFLite:**

```python
from src.train_classifier import PotholeClassifierTrainer

trainer = PotholeClassifierTrainer()
trainer.model = load_model('models/custom_classifier.h5')
trainer.convert_to_tflite()
```

### Multi-Class Detection (Cracks, Potholes)

**1. Train YOLO on RDD2022 dataset:**

```bash
# Modify config.py obj.names:
# pothole
# longitudinal_crack
# transverse_crack
# alligator_crack

# Use Darknet/YOLO training pipeline (external)
```

**2. Update `detect_edge.py` to handle multiple classes**

### GPS Integration on Pi

**1. Install gpsd:**

```bash
sudo apt-get install gpsd gpsd-clients
```

**2. Enable in `config.py`:**

```python
USE_GPS_MODULE = True
```

### Cloud Dashboard (Leaflet + Folium)

Example visualization template (place in `src/dashboard.py`):

```python
import folium
from folium.plugins import HeatMap

def create_map(detections):
    m = folium.Map(location=[17.3629, 75.8930], zoom_start=13)
    
    heat_data = [[d['lat'], d['lon'], d['severity_score']] 
                 for d in detections]
    HeatMap(heat_data).add_to(m)
    
    m.save('dashboard.html')
```

---

## 📊 Model Details

### Classifier (Pothole Detection)

- **Base Model:** MobileNetV2 (ImageNet pre-trained)
- **Task:** Binary classification (Pothole vs. Plain Road)
- **Input:** 224×224 RGB
- **Augmentation:** Rotation, shift, zoom, flip
- **Output:** Sigmoid (0-1 probability)

### Detector (Localization)

- **Model:** YOLOv4-tiny
- **Input:** 416×416 (configurable)
- **FPS:** ~10-15 on Pi, ~30+ on laptop
- **Classes:** Expandable (default: "pothole")

### Severity Estimation

Currently uses heuristic:

```
Severity = f(BBox_Area_Ratio, Classifier_Confidence)

Low:    Area < 1% of frame
Medium: 1% ≤ Area < 5%
High:   Area ≥ 5%
```

**Future:** Integrate ultrasonic depth sensor or stereo depth estimation.

---

## 🔄 API Endpoints (Expected Cloud Implementation)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/report` | POST | Submit detection |
| `/api/update-status` | POST | Update repair status |
| `/api/detection/<id>` | GET | Fetch detection details |
| `/api/detections` | GET | List recent detections |
| `/api/heatmap` | GET | Get geospatial heatmap |
| `/api/request-drone` | POST | Request drone inspection |
| `/api/citizen-report` | POST | Submit citizen report |
| `/api/status` | GET | Check API health |

---

## 🧪 Testing & Debugging

### Test with Demo Video

```python
# In config.py:
DEMO_VIDEO_PATH = "data/test.mp4"
CAMERA_SOURCE = DEMO_VIDEO_PATH

python src/detect_edge.py
```

### Verbose Logging

```python
# In config.py:
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_DEBUG_FRAMES = True  # Save each processed frame
```

### API Testing

```bash
python src/api_client.py  # Runs test_api() function
```

---

## 📦 Deployment Checklist

- [ ] Models downloaded and placed in `models/`
- [ ] Training data organized in `data/training_images/`
- [ ] Classifier trained: `python src/train_classifier.py`
- [ ] Config.py updated with your API endpoint
- [ ] Edge device (Pi) configured and tested
- [ ] Citizen app accessible via web
- [ ] Cloud backend ready to receive API calls
- [ ] Geolocation (GPS or IP) configured

---

## 🐛 Troubleshooting

### Model Files Not Found

```
Error: YOLO model files not found
Solution: Download yolov4-tiny.weights to models/
```

### TensorFlow Import Error

```
Error: No module named 'tensorflow'
Solution: pip install tensorflow
```

### Raspberry Pi: Out of Memory

```
Solution: Enable SWAP, use TFLite, reduce YOLO input size
```

### API Connection Failed

```
Solution: Check API_URL in config.py, verify network connectivity
```

### Low FPS on Raspberry Pi

```
Optimize:
- Reduce IMG_SIZE_YOLO to 320
- Increase DETECTION_FRAME_SKIP
- Use TFLite instead of full TensorFlow
```

---

## 📚 References & Resources

- **YOLOv4-tiny:** https://github.com/AlexeyAB/darknet
- **RDD2022 Dataset:** https://data.mendeley.com/datasets/nz6yz6d68r
- **TensorFlow Lite:** https://www.tensorflow.org/lite
- **Raspberry Pi ML:** https://www.raspberrypi.org/
- **Flask:** https://flask.palletsprojects.com/
- **Leaflet Maps:** https://leafletjs.com/

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Multi-class detection (cracks, potholes, potholes_large)
- 3D depth estimation from stereo cameras
- Drone flight planning optimization
- Cloud dashboard UI
- Mobile app (citizen side)
- Real-time repair tracking

---

## 📄 License

This project is open-source. Please provide attribution to ASTROPATH & Solapur Municipal Corporation.

---

## 👥 Team & Contact

**ASTROPATH Hackathon Project (2026)**

- **Lead:** [Your Name]
- **Organization:** Solapur Municipality / Academic Institution
- **Email:** contact@astropath.local

---

## 🗺️ Roadmap

**Phase 1 (Current):** Edge detection + citizen app
**Phase 2:** Cloud integration + dashboard
**Phase 3:** Drone automation + repair tracking
**Phase 4:** ML model improvement (RDD2022 training)
**Phase 5:** Mobile app (iOS/Android)

---

## 🎯 PPT Vision Alignment

This codebase directly implements the SAMVED Hackathon 2026 PPT architecture:

✅ Citizen + Drone Dual Input  
✅ AI Analysis (YOLO + CNN)  
✅ Severity Estimation  
✅ Geolocation & Dashboard  
✅ Re-verification Loop  
✅ Raspberry Pi Edge Processing  
✅ Modular & Scalable Design  

**Ready to deploy to Solapur or any smart city!**

---

**Last Updated:** January 2026  
**Version:** 1.0.0-beta
