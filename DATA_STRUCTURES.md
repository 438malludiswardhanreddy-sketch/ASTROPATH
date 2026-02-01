# ASTROPATH Data Structures & Sample Data

This file documents the expected data structures and provides examples.

## Training Data Structure

### Directory Layout

```
data/
└── training_images/
    ├── pothole/
    │   ├── pothole_001.jpg
    │   ├── pothole_002.png
    │   ├── pothole_003.jpg
    │   └── ... (50-200 images)
    │
    └── plain/
        ├── plain_001.jpg
        ├── plain_002.jpg
        ├── plain_003.png
        └── ... (50-200 images)
```

### Requirements

- **Format:** JPG, PNG
- **Size:** Any (auto-resized to 224×224)
- **Count:** 50+ per class (100+ recommended)
- **Content:** 
  - `pothole/`: Images showing potholes/road damage
  - `plain/`: Images of normal road surfaces

---

## Detection Output Structure

### Saved Detections

```
detections/
├── pothole_20260131-120000.jpg
├── pothole_20260131-120100.jpg
├── pothole_20260131-120200.jpg
└── output_video.avi
```

Each detection includes:
- **Timestamp:** When detected
- **Annotation:** Bounding boxes, severity levels
- **Colors:** Green (Low), Orange (Medium), Red (High)

---

## API Data Structures

### Detection Report

```json
{
  "timestamp": "2026-01-31T12:00:00",
  "latitude": 17.3629,
  "longitude": 75.8930,
  "severity": "High",
  "confidence": 0.87,
  "class": "pothole",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### Repair Status Update

```json
{
  "detection_id": "det_2026_0131_120000",
  "status": "in_progress",  // or "completed", "pending"
  "notes": "Patching started",
  "timestamp": "2026-01-31T12:30:00"
}
```

### Heatmap Data

```json
{
  "detections": [
    {
      "id": "det_001",
      "latitude": 17.3629,
      "longitude": 75.8930,
      "severity": "High",
      "count": 3,
      "last_updated": "2026-01-31T12:00:00"
    },
    {
      "id": "det_002",
      "latitude": 17.3630,
      "longitude": 75.8935,
      "severity": "Medium",
      "count": 1,
      "last_updated": "2026-01-31T11:00:00"
    }
  ],
  "total_detections": 2,
  "high_severity_count": 1,
  "medium_severity_count": 1,
  "low_severity_count": 0
}
```

---

## Configuration Data

### Model Configuration

```python
# From config.py
IMG_SIZE_CLASSIFIER = 224    # Input for MobileNetV2
IMG_SIZE_YOLO = 416         # Input for YOLOv4-tiny
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
```

### Severity Thresholds

```python
SEVERITY_LEVELS = {
    "Low": {
        "min_area": 0,
        "max_area": 0.01,      # < 1% of frame
        "color": (0, 255, 0)   # Green
    },
    "Medium": {
        "min_area": 0.01,
        "max_area": 0.05,      # 1-5% of frame
        "color": (0, 165, 255) # Orange
    },
    "High": {
        "min_area": 0.05,
        "max_area": 1.0,       # > 5% of frame
        "color": (0, 0, 255)   # Red
    }
}
```

---

## Video Input Formats

### Supported Sources

```python
# Webcam
CAMERA_SOURCE = 0

# Local video file
CAMERA_SOURCE = "data/test.mp4"
CAMERA_SOURCE = "/path/to/video.avi"

# IP camera stream
CAMERA_SOURCE = "http://192.168.1.100:8080/video"
CAMERA_SOURCE = "rtsp://camera-ip:554/stream"

# Drone UDP stream
CAMERA_SOURCE = "udp://192.168.1.100:5000"

# Drone stream (DJI SDK)
CAMERA_SOURCE = "drone:dji"
```

---

## Citizen Report Structure

### Web Form Submission

```json
{
  "latitude": 17.3629,
  "longitude": 75.8930,
  "description": "Large pothole on main road, risky for two-wheelers",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "timestamp": "2026-01-31T12:00:00",
  "source": "citizen_app"
}
```

### API Response

```json
{
  "success": true,
  "report_id": "rep_2026_0131_001",
  "message": "Report received and queued for inspection",
  "estimated_drone_arrival": "2 hours"
}
```

---

## Drone Request Structure

### Autonomous Inspection Request

```json
{
  "latitude": 17.3629,
  "longitude": 75.8930,
  "priority": "high",  // or "medium", "low"
  "inspection_type": "aerial",  // or "depth_scan"
  "timestamp": "2026-01-31T12:00:00",
  "detection_id": "det_2026_0131_120000"
}
```

### Drone Response

```json
{
  "success": true,
  "mission_id": "mission_001",
  "status": "queued",  // or "in_progress", "completed"
  "estimated_completion": "2026-01-31T13:00:00",
  "images_captured": 15,
  "video_url": "s3://bucket/missions/mission_001/video.mp4"
}
```

---

## Model Output Structure

### YOLOv4-tiny Detection

```python
{
    'class_id': 0,
    'class_name': 'pothole',
    'confidence': 0.87,  # 0-1
    'box': (x, y, w, h),  # Bounding box
    'x': 100,
    'y': 150,
    'w': 80,
    'h': 60,
    'severity': 'High',
    'severity_score': 0.92  # 0-1
}
```

### Classifier Output

```python
{
    'probability': 0.87,  # 0=plain, 1=pothole
    'class': 'pothole',
    'confidence': 0.87
}
```

---

## Logging Structure

### Log Entry Format

```
2026-01-31 12:00:00 - src.detect_edge - INFO - Detection: pothole (High, 0.87) at (17.3629, 75.8930)
2026-01-31 12:00:01 - src.api_client - INFO - Report submitted successfully: det_2026_0131_120000
2026-01-31 12:00:02 - src.utils - WARNING - GPS module failed. Using IP fallback.
```

### Log Levels

- **DEBUG:** Verbose output for debugging
- **INFO:** General information
- **WARNING:** Issues that might need attention
- **ERROR:** Something went wrong
- **CRITICAL:** System failure

---

## Database Schema (For Cloud Backend)

### Detections Table

```sql
CREATE TABLE detections (
    id VARCHAR(50) PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    severity ENUM('Low', 'Medium', 'High'),
    confidence FLOAT,
    class_name VARCHAR(50),
    image_url VARCHAR(255),
    detected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Repairs Table

```sql
CREATE TABLE repairs (
    id VARCHAR(50) PRIMARY KEY,
    detection_id VARCHAR(50) FOREIGN KEY,
    status ENUM('pending', 'in_progress', 'completed', 'rejected'),
    notes TEXT,
    assigned_crew_id VARCHAR(50),
    updated_at TIMESTAMP
);
```

### Citizen Reports Table

```sql
CREATE TABLE citizen_reports (
    id VARCHAR(50) PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    submitted_at TIMESTAMP,
    review_status ENUM('pending', 'approved', 'duplicate', 'invalid')
);
```

---

## Performance Metrics

### Expected Inference Times

| Hardware | Model | FPS |
|----------|-------|-----|
| Laptop (CPU) | YOLOv4-tiny | 20-30 |
| Laptop (GPU) | YOLOv4-tiny | 30-50 |
| Raspberry Pi | YOLOv4-tiny | 5-10 |
| Raspberry Pi | TFLite | 15-20 |

### Memory Usage

| Component | Memory |
|-----------|--------|
| YOLO model (weights) | 196 MB |
| Classifier (H5) | 30-50 MB |
| Classifier (TFLite) | 10-15 MB |
| Runtime (Pi) | 100-200 MB |

---

## File Size Examples

### Training Dataset

- 100 images × 500 KB = 50 MB

### Detections

- Single image: 50-200 KB
- 1 day detections (100/day): 5-20 MB
- Monthly (3000 detections): 150-600 MB

### Archived Videos

- 1 hour @ 30 FPS: 500 MB - 1 GB
- 24 hours: 12-24 GB

---

## Example: Complete Detection Flow

```python
# Input
frame = cv2.imread('pothole.jpg')  # 640×480 RGB image

# YOLO Detection
detections = detector.detect(frame)  # Returns list of bounding boxes

# Per Detection
detection = {
    'class_name': 'pothole',
    'confidence': 0.87,
    'box': (100, 150, 80, 60)
}

# Crop & Classify
crop = frame[150:210, 100:180]
classifier_output = classifier.predict(crop)  # 0.92

# Severity Estimation
area_ratio = (80 * 60) / (640 * 480) = 0.0156  # 1.56%
severity = "Medium"  # 1% < 1.56% < 5%

# API Report
payload = {
    'latitude': 17.3629,
    'longitude': 75.8930,
    'severity': 'Medium',
    'confidence': 0.87,
    'image_path': 'detections/pothole_20260131-120000.jpg'
}

# Cloud Response
{
    'success': true,
    'detection_id': 'det_2026_0131_120000',
    'recommendation': 'Schedule repair crew'
}
```

---

## Customization Examples

### For Multi-Class Detection

```python
# Add to models/obj.names:
"""
pothole
longitudinal_crack
transverse_crack
alligator_crack
"""

# Update severity calculation:
SEVERITY_MULTIPLIER = {
    'pothole': 1.0,
    'longitudinal_crack': 0.5,
    'transverse_crack': 0.6,
    'alligator_crack': 0.7
}
```

### For Depth Sensing

```python
# Include depth in detection:
detection = {
    'class_name': 'pothole',
    'confidence': 0.87,
    'depth_cm': 8.5,  # From ultrasonic
    'area_mm2': 15000
}

# Severity = f(area, depth):
SEVERITY = {
    'Low': {'depth': (0, 5), 'area': (0, 10000)},
    'Medium': {'depth': (5, 10), 'area': (10000, 30000)},
    'High': {'depth': (10, 100), 'area': (30000, 1000000)}
}
```

---

This document provides the foundation for understanding ASTROPATH's data flow.
For implementation details, see individual module documentation.
