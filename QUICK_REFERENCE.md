# 🚀 ASTROPATH Quick Reference

## One-Liner Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Show menu
python main.py

# Run detection from webcam
python -c "from src.detect_edge import main; main()"

# Start citizen app (http://localhost:5000)
python -c "from src.citizen_upload import main; main()"

# Train classifier
python -c "from src.train_classifier import main; main()"

# Test API
python -c "from src.api_client import test_api; test_api()"
```

---

## Configuration Snippets

### Webcam Detection
```python
# In config.py:
CAMERA_SOURCE = 0
```

### Video File Detection
```python
# In config.py:
CAMERA_SOURCE = "data/test.mp4"
```

### Raspberry Pi Optimization
```python
# In config.py:
PI_OPTIMIZE = True
IMG_SIZE_YOLO = 320
DETECTION_FRAME_SKIP = 2
```

### Enable Cloud Upload
```python
# In config.py:
API_URL = "http://your-api.com/api"
ENABLE_CLOUD_UPLOAD = True
```

### GPS Module (Pi)
```python
# In config.py:
USE_GPS_MODULE = True
```

---

## File Locations

| What | Where | Edit? |
|------|-------|-------|
| Settings | `config.py` | ✅ Yes |
| Training code | `src/train_classifier.py` | - |
| Detection code | `src/detect_edge.py` | - |
| Web app | `src/citizen_upload.py` | - |
| API client | `src/api_client.py` | - |
| Utilities | `src/utils.py` | - |
| YOLO weights | `models/yolov4-tiny.weights` | ⬇️ Download |
| Trained model | `models/custom_classifier.h5` | 🔨 Generated |
| Training images | `data/training_images/{pothole,plain}/` | ✅ Add |
| Test video | `data/test.mp4` | ✅ Add |
| Detections | `detections/` | 📁 Output |
| Citizen uploads | `uploads/` | 📁 Output |

---

## Key Classes & Functions

### Training
```python
from src.train_classifier import PotholeClassifierTrainer

trainer = PotholeClassifierTrainer()
(X_train, y_train), (X_val, y_val) = trainer.prepare_data(
    "data/training_images/pothole",
    "data/training_images/plain"
)
trainer.create_model()
trainer.train(X_train, y_train, X_val, y_val)
trainer.save_model()
```

### Detection
```python
from src.detect_edge import EdgeDetectionPipeline

pipeline = EdgeDetectionPipeline()
pipeline.run(source=0)  # 0=webcam, or video path
```

### API
```python
from src.api_client import APIClient

client = APIClient("http://api.example.com")
success, response = client.report_detection({
    'latitude': 17.3629,
    'longitude': 75.8930,
    'severity': 'High',
    'confidence': 0.87,
    'image_path': 'path/to/image.jpg'
})
```

### Utilities
```python
from src.utils import setup_logger, get_geolocation, save_image

logger = setup_logger(__name__)
lat, lon = get_geolocation()
img_path = save_image(frame, "detections/")
```

---

## Common Workflows

### 1️⃣ Train from Scratch
```bash
# Organize training data:
# data/training_images/pothole/ (50+ images)
# data/training_images/plain/   (50+ images)

python main.py
# Select: 1. Train Pothole Classifier
```

### 2️⃣ Detect from Webcam
```bash
python main.py
# Select: 2. Run Edge Detection
# Or: python -c "from src.detect_edge import main; main()"
# Press 'q' to quit
```

### 3️⃣ Deploy to Raspberry Pi
```bash
# 1. Enable Pi optimizations
# Edit config.py: PI_OPTIMIZE = True

# 2. Deploy files
scp -r ASTROPATH pi@192.168.x.x:/home/pi/

# 3. Run on Pi
ssh pi@192.168.x.x
cd ASTROPATH
python main.py
# Select: 2. Run Edge Detection
```

### 4️⃣ Start Citizen App
```bash
python main.py
# Select: 3. Start Citizen Reporting Web App
# Access: http://localhost:5000
```

### 5️⃣ Send to Cloud
```python
# 1. Configure API
# Edit config.py:
# API_URL = "http://your-api.com/api"
# ENABLE_CLOUD_UPLOAD = True

# 2. Run detection (auto-uploads)
python main.py
# Select: 2. Run Edge Detection
```

---

## Keyboard Shortcuts (During Detection)

| Key | Action |
|-----|--------|
| `q` | Quit detection |
| ESC | Quit (alternative) |

---

## Environment Variables (Optional)

```bash
# Create .env file:
echo "API_URL=http://your-api.com/api" > .env
echo "DEBUG_MODE=True" >> .env

# Load in code:
from dotenv import load_dotenv
load_dotenv()
```

---

## Logging

### View Logs
```bash
# Real-time
tail -f astropath.log

# Search
grep "Detection" astropath.log
grep "ERROR" astropath.log
```

### Enable Debug Mode
```python
# In config.py:
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_DEBUG_FRAMES = True
```

---

## Performance Tips

### Speed Up Detection
```python
# In config.py:
DETECTION_FRAME_SKIP = 2  # Process every 2nd frame
IMG_SIZE_YOLO = 320       # Smaller input
```

### Reduce Memory Usage
```python
# In config.py:
PI_OPTIMIZE = True
```

### Save Disk Space
```python
# In config.py:
SAVE_DETECTIONS = False
SAVE_DEBUG_FRAMES = False
```

---

## API Response Examples

### Successful Detection Report
```json
{
  "success": true,
  "detection_id": "det_2026_0131_120000",
  "latitude": 17.3629,
  "longitude": 75.8930,
  "severity": "High",
  "timestamp": "2026-01-31T12:00:00"
}
```

### Heatmap Response
```json
{
  "success": true,
  "data": [
    {"lat": 17.360, "lon": 75.890, "count": 5},
    {"lat": 17.365, "lon": 75.895, "count": 3}
  ]
}
```

---

## Troubleshooting Matrix

| Problem | Solution |
|---------|----------|
| YOLO weights missing | Download from GitHub (see SETUP_GUIDE.md) |
| No camera access | Try `CAMERA_SOURCE = 1` or use video file |
| Low FPS | Increase `DETECTION_FRAME_SKIP` or enable `PI_OPTIMIZE` |
| Out of memory (Pi) | Enable `PI_OPTIMIZE`, use TFLite |
| Training data not found | Create `data/training_images/{pothole,plain}/` |
| API connection failed | Check `API_URL`, verify network |
| Flask app won't start | Check port 5000 not in use, try port 8000 |

---

## File Size Reference

| Component | Size |
|-----------|------|
| YOLOv4-tiny weights | ~196 MB |
| Custom classifier (H5) | ~30-50 MB |
| Custom classifier (TFLite) | ~10-15 MB |
| Per detection image | ~50-200 KB |
| Project code (no models) | ~300 KB |

---

## GitHub Setup (After Completion)

```bash
git init
git add .
git commit -m "ASTROPATH v1.0.0-beta: Initial clean architecture"
git remote add origin https://github.com/user/ASTROPATH
git push -u origin main
```

---

## Useful Links

- YOLOv4: https://github.com/AlexeyAB/darknet
- TensorFlow: https://www.tensorflow.org/
- Raspberry Pi: https://www.raspberrypi.org/
- Flask: https://flask.palletsprojects.com/
- RDD2022 Dataset: https://data.mendeley.com/datasets/nz6yz6d68r

---

## Success Checklist ✅

- [ ] Project cloned/created
- [ ] `pip install -r requirements.txt`
- [ ] YOLO weights downloaded
- [ ] `python main.py` works
- [ ] Webcam detection tested
- [ ] Citizen app loads at localhost:5000
- [ ] Training data organized
- [ ] Classifier trained
- [ ] Detections saved to `detections/`
- [ ] Ready for cloud integration!

---

**Need Help?** See README.md or SETUP_GUIDE.md

**Ready to Deploy?** You're all set! 🚀
