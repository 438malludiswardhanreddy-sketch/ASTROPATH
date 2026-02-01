"""
ASTROPATH Utilities Module
Common functions for logging, geolocation, and file handling
"""

import logging
import os
import sys
import numpy as np
import cv2
from datetime import datetime
import config

# ==================== Logging Setup ====================
def setup_logger(name=__name__):
    """Configure logging with both file and console handlers"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, config.LOG_LEVEL)
    logger.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if config.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if config.LOG_TO_FILE:
        os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logger(__name__)

# ==================== Geolocation ====================
def get_geolocation():
    """
    Get geolocation using GPS module or IP fallback
    Returns: (latitude, longitude) tuple
    """
    if config.USE_GPS_MODULE:
        try:
            # Try to use gpsd (real GPS on Raspberry Pi)
            import gps
            session = gps.gpsSession()
            session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
            
            for report in session:
                if hasattr(report, 'lat') and hasattr(report, 'lon'):
                    logger.info(f"GPS location: ({report.lat}, {report.lon})")
                    return (report.lat, report.lon)
        except Exception as e:
            logger.warning(f"GPS module failed: {e}. Using IP fallback.")
    
    if config.FALLBACK_GEOLOCATION:
        try:
            import geocoder
            g = geocoder.ip('me')
            if g.latlng:
                logger.info(f"IP geolocation: {g.latlng}")
                return tuple(g.latlng)
        except Exception as e:
            logger.warning(f"IP geolocation failed: {e}")
    
    logger.warning("No geolocation available. Using defaults.")
    return (0.0, 0.0)  # Default: no location


# ==================== Image Processing ====================
def resize_image(image, size):
    """Resize image to specified size maintaining aspect ratio"""
    h, w = image.shape[:2]
    aspect = w / h
    
    if aspect > 1:  # wider
        new_w = size
        new_h = int(size / aspect)
    else:
        new_h = size
        new_w = int(size * aspect)
    
    # Use INTER_AREA for downscaling (better quality, faster)
    orig_pixels = w * h
    new_pixels = new_w * new_h
    if new_pixels < orig_pixels:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_LINEAR

    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)


def fast_preprocess_for_yolo(frame, input_size):
    """Resize and pad frame to square input_size quickly for YOLO DNN

    Returns resized frame suitable for cv2.dnn model input.
    """
    # Convert to square by resizing shorter side then padding
    h, w = frame.shape[:2]
    scale = input_size / max(w, h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)

    # Pad to square
    pad_w = input_size - nw
    pad_h = input_size - nh
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114,114,114))
    return padded


def normalize_image(image):
    """Normalize image to 0-1 range"""
    return image.astype(np.float32) / 255.0


def denormalize_image(image):
    """Convert normalized image back to 0-255 range"""
    return (image * 255).astype(np.uint8)


# ==================== File Operations ====================
def ensure_dir_exists(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    return path


def get_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save_image(image, directory, prefix="detection"):
    """Save image with timestamp"""
    ensure_dir_exists(directory)
    ts = get_timestamp()
    filename = os.path.join(directory, f"{prefix}_{ts}.jpg")
    cv2.imwrite(filename, image)
    logger.info(f"Saved image: {filename}")
    return filename


# ==================== Performance Metrics ====================
class FPSCounter:
    """Calculate frames per second"""
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.frame_times = []
    
    def update(self):
        """Call once per frame"""
        current_time = datetime.now().timestamp()
        self.frame_times.append(current_time)
        
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Get current FPS"""
        if len(self.frame_times) < 2:
            return 0
        time_diff = self.frame_times[-1] - self.frame_times[0]
        if time_diff == 0:
            return 0
        return (len(self.frame_times) - 1) / time_diff


# ==================== Detection Output Formatting ====================
def create_detection_payload(detection_data, latitude, longitude):
    """Format detection data for API submission"""
    payload = {
        "timestamp": get_timestamp(),
        "latitude": latitude,
        "longitude": longitude,
        "severity": detection_data.get("severity", "Unknown"),
        "confidence": float(detection_data.get("confidence", 0)),
        "class": detection_data.get("class", "pothole"),
        "image_path": detection_data.get("image_path", ""),
        "image_base64": detection_data.get("image_base64", ""),  # Optional
    }
    return payload


# ==================== Validation ====================
def validate_model_files():
    """Check if required model files exist"""
    required_files = [
        config.YOLOV4_WEIGHTS,
        config.YOLOV4_CFG,
        config.OBJ_NAMES,
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"Missing model files: {missing_files}")
        logger.warning("Download YOLOv4-tiny files from: https://github.com/AlexeyAB/darknet")
        return False
    
    logger.info("All required model files found.")
    return True


def validate_training_data():
    """Check if training data structure exists"""
    if not os.path.exists(config.POTHOLE_DATA_PATH):
        logger.warning(f"Pothole data directory not found: {config.POTHOLE_DATA_PATH}")
        return False
    if not os.path.exists(config.PLAIN_DATA_PATH):
        logger.warning(f"Plain road data directory not found: {config.PLAIN_DATA_PATH}")
        return False
    
    pothole_count = len(os.listdir(config.POTHOLE_DATA_PATH))
    plain_count = len(os.listdir(config.PLAIN_DATA_PATH))
    
    logger.info(f"Training data found: {pothole_count} potholes, {plain_count} plain road images")
    return pothole_count > 0 and plain_count > 0
