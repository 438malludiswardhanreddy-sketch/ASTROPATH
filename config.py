"""
ASTROPATH Configuration Module
Centralized configuration for model paths, thresholds, and API endpoints
"""

import os

# ==================== Project Paths ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")
DETECTIONS_DIR = os.path.join(BASE_DIR, "detections")

# ==================== Model Paths ====================
YOLOV4_WEIGHTS = os.path.join(MODELS_DIR, "yolov4-tiny.weights")
YOLOV4_CFG = os.path.join(MODELS_DIR, "yolov4-tiny.cfg")
OBJ_NAMES = os.path.join(MODELS_DIR, "obj.names")
CLASSIFIER_MODEL = os.path.join(MODELS_DIR, "custom_classifier.h5")
CLASSIFIER_TFLITE = os.path.join(MODELS_DIR, "custom_classifier.tflite")

# ==================== Training Configuration ====================
IMG_SIZE_CLASSIFIER = 224
IMG_SIZE_YOLO = 416
BATCH_SIZE = 32
EPOCHS = 50
TRAIN_TEST_SPLIT = 0.2
LEARNING_RATE = 0.001
DATA_AUGMENTATION = True

# ✅ INTEGRATION: Your existing pothole images location
EXISTING_POTHOLE_IMAGES = os.path.join(os.path.dirname(BASE_DIR), "pothole-detection-main", "Image Annotation")

# Path to training dataset (folder structure: data/pothole/ and data/plain/)
TRAINING_DATA_PATH = os.path.join(DATA_DIR, "training_images")
POTHOLE_DATA_PATH = os.path.join(TRAINING_DATA_PATH, "pothole")
PLAIN_DATA_PATH = os.path.join(TRAINING_DATA_PATH, "plain")

# 💡 CHOOSE YOUR TRAINING DATA SOURCE:
# Option A: Use your existing images directly
# POTHOLE_DATA_PATH = EXISTING_POTHOLE_IMAGES
#
# Option B: Copy/organize images to data/training_images/{pothole,plain}/ (recommended)

# ==================== Detection Configuration ====================
CONF_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4
SEVERITY_THRESHOLDS = {
    "area_ratio_low": 0.01,      # < 1% of frame
    "area_ratio_medium": 0.05,   # < 5% of frame
}

# ==================== Severity Estimation ====================
# Severity levels based on area ratio and confidence
SEVERITY_LEVELS = {
    "Low": {"min_area": 0, "max_area": 0.01, "color": (0, 255, 0)},        # Green
    "Medium": {"min_area": 0.01, "max_area": 0.05, "color": (0, 165, 255)},  # Orange
    "High": {"min_area": 0.05, "max_area": 1.0, "color": (0, 0, 255)},      # Red
}

# ==================== Camera/Input Configuration ====================
CAMERA_SOURCE = 0  # 0 for webcam, or URL for IP camera / drone stream
# CAMERA_SOURCE = "udp://192.168.1.100:5000"  # Example for drone
VIDEO_OUTPUT_PATH = os.path.join(DETECTIONS_DIR, "output_video.avi")
SAVE_DETECTIONS = True
DETECTION_FRAME_SKIP = 2  # Process every Nth frame for faster inference (lower = faster but heavier)

# ==================== API/Cloud Configuration ====================
API_URL = "http://localhost:5000/api/report"  # Local test server; replace with production URL
API_TIMEOUT = 10  # seconds
ENABLE_CLOUD_UPLOAD = True  # Set to False to disable uploads

# Geolocation fallback (IP-based)
USE_GPS_MODULE = False  # Set to True if using real GPS on Raspberry Pi
FALLBACK_GEOLOCATION = True  # Use IP geolocation if GPS unavailable

# ==================== GPS Configuration (Real Module) ====================
# Enable/Disable real GPS module for location tracking
GPS_ENABLED = False  # Set to True when GPS hardware is connected

# Serial Port Configuration
# Linux/Pi: '/dev/ttyACM0' (USB), '/dev/ttyUSB0' (USB alt), '/dev/serial0' (GPIO UART)
# Windows: 'COM3', 'COM4', etc.
GPS_PORT = '/dev/serial0'
GPS_BAUD = 9600  # Common for NEO-6M, NEO-M8N. Some use 38400

# GPS Module Parameters
GPS_TIMEOUT = 1.0  # Serial read timeout (seconds)
GPS_MAX_RETRIES = 20  # Max attempts to read NMEA per call
GPS_MIN_SATS = 4  # Minimum satellites for valid fix (3-4 typical)

# Quality Threshold for Position Acceptance
GPS_MIN_QUALITY = 1  # 0=NoFix, 1=GPSFix, 2=DGPS, etc. (1+ is safe)

# Fallback Behavior
GPS_USE_CACHED_IF_NO_FIX = True  # Use last known position if no current fix
GPS_FALLBACK_TO_IP = True  # Use IP geolocation if GPS unavailable

# Recommended GPS Modules (2026):
# - u-blox NEO-6M / NEO-M8N: ~₹500-1500, 2-5m accuracy, very popular
# - Adafruit Ultimate GPS / PA1010D: Easy I2C/USB, high sensitivity
# - Beitian BN-220 / BZ-series: 10Hz update rate, drone-friendly
#
# For Raspberry Pi Setup:
# 1. Connect GPS via USB or GPIO (UART)
# 2. Verify port: ls /dev/tty{ACM,USB,serial}*
# 3. Enable serial if GPIO: sudo raspi-config → Interface Options → Serial
# 4. Install: pip install pynmea2 pyserial
# 5. Test: python test_gps.py --port <PORT>


# ==================== Raspberry Pi / Edge Deployment ====================
PI_OPTIMIZE = False  # Enable TensorFlow Lite and lightweight inference
USE_OPENVINO = False  # Use OpenVINO for YOLO acceleration on Pi
USE_NCNN = False  # Use NCNN for YOLO on embedded devices

# ==================== Fast Mode / Performance Tweaks ====================
# Enable FAST_MODE to prioritize speed: uses smaller YOLO input size and lower-cost processing.
FAST_MODE = True
# Input size for YOLO when FAST_MODE enabled. Smaller sizes increase speed at cost of accuracy.
FAST_IMG_SIZE_YOLO = 320
# When True and OpenCV DNN built with CUDA, prefer CUDA target for inference.
USE_CUDA = False

# ==================== Citizen App Configuration ====================
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# ==================== Logging Configuration ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join(BASE_DIR, "astropath.log")
LOG_TO_FILE = True
LOG_TO_CONSOLE = True

# ==================== Performance Metrics ====================
ENABLE_FPS_COUNTER = True
ENABLE_MEMORY_PROFILING = False

# ==================== Debug/Demo Mode ====================
DEBUG_MODE = True  # Show verbose output
SAVE_DEBUG_FRAMES = False  # Save each processed frame
DEMO_VIDEO_PATH = os.path.join(DATA_DIR, "test.mp4")  # For testing without real camera
