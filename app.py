"""
ASTROPATH - Real-time Web Application
Complete web interface with live camera detection, GPS tracking, and dashboard
"""

import os
import sys
import json
import base64
from datetime import datetime
from io import BytesIO
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from src.utils import setup_logger
from src.database import DetectionDatabase
from src.gps_handler import GPSHandler

logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'astropath-2026-secret-key'
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# Initialize database
db = DetectionDatabase()

# Global variables for camera and detection
camera = None
yolo_net = None
classifier_model = None
gps_handler = None
detection_active = False


def load_models():
    """Load YOLO and classifier models"""
    global yolo_net, classifier_model
    
    try:
        # Load YOLO
        if os.path.exists(config.YOLOV4_WEIGHTS) and os.path.exists(config.YOLOV4_CFG):
            logger.info("Loading YOLO model...")
            yolo_net = cv2.dnn.readNetFromDarknet(config.YOLOV4_CFG, config.YOLOV4_WEIGHTS)
            
            if config.USE_CUDA:
                yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            else:
                yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            logger.info("✓ YOLO model loaded successfully")
        else:
            logger.warning("YOLO model files not found. Detection will be limited.")
        
        # Load classifier if available
        if os.path.exists(config.CLASSIFIER_MODEL):
            from tensorflow import keras
            logger.info("Loading classifier model...")
            classifier_model = keras.models.load_model(config.CLASSIFIER_MODEL)
            logger.info("✓ Classifier model loaded successfully")
        else:
            logger.warning("Classifier model not found. Using YOLO only.")
            
    except Exception as e:
        logger.error(f"Error loading models: {e}")


def initialize_gps():
    """Initialize GPS handler if enabled"""
    global gps_handler
    
    if config.GPS_ENABLED:
        try:
            logger.info("Initializing GPS handler...")
            gps_handler = GPSHandler(port=config.GPS_PORT, baud=config.GPS_BAUD)
            if gps_handler.is_connected():
                logger.info("✓ GPS handler initialized successfully")
            else:
                logger.warning("GPS handler initialized but not connected")
        except Exception as e:
            logger.error(f"GPS initialization failed: {e}")
            gps_handler = None


def get_location():
    """Get current location from GPS or fallback to IP geolocation"""
    lat, lon = None, None
    source = "unknown"
    
    # Try GPS first if available
    if gps_handler and gps_handler.is_connected():
        try:
            lat, lon, timestamp, quality = gps_handler.get_coordinates()
            if lat and lon:
                source = "gps"
                logger.info(f"Location from GPS: {lat}, {lon}")
                return lat, lon, source
        except Exception as e:
            logger.error(f"GPS read error: {e}")
    
    # Fallback to IP geolocation
    if config.GPS_FALLBACK_TO_IP or config.FALLBACK_GEOLOCATION:
        try:
            import geocoder
            g = geocoder.ip('me')
            if g.ok and g.latlng:
                lat, lon = g.latlng
                source = "ip"
                logger.info(f"Location from IP: {lat}, {lon}")
        except Exception as e:
            logger.error(f"IP geolocation error: {e}")
    
    # Default fallback (Solapur, India)
    if lat is None or lon is None:
        lat, lon = 17.6599, 75.9064
        source = "default"
        logger.warning(f"Using default location: {lat}, {lon}")
    
    return lat, lon, source


def detect_potholes(frame):
    """Detect potholes in a frame using YOLO"""
    detections = []
    
    if yolo_net is None:
        return detections, frame
    
    try:
        height, width = frame.shape[:2]
        
        # Prepare blob for YOLO
        img_size = config.FAST_IMG_SIZE_YOLO if config.FAST_MODE else config.IMG_SIZE_YOLO
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (img_size, img_size), swapRB=True, crop=False)
        yolo_net.setInput(blob)
        
        # Get output layers
        layer_names = yolo_net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]
        
        # Forward pass
        outputs = yolo_net.forward(output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                confidence = float(scores[0]) if len(scores) > 0 else 0
                
                if confidence > config.CONF_THRESHOLD:
                    # Get bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(confidence)
        
        # Non-maximum suppression
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, config.CONF_THRESHOLD, config.NMS_THRESHOLD)
            
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    confidence = confidences[i]
                    
                    # Calculate severity based on area
                    area_ratio = (w * h) / (width * height)
                    
                    if area_ratio < 0.01:
                        severity = "Low"
                        color = (0, 255, 0)
                    elif area_ratio < 0.05:
                        severity = "Medium"
                        color = (0, 165, 255)
                    else:
                        severity = "High"
                        color = (0, 0, 255)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    # Draw label
                    label = f"{severity}: {confidence:.2f}"
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    detections.append({
                        'bbox': [x, y, w, h],
                        'confidence': confidence,
                        'severity': severity,
                        'area_ratio': area_ratio
                    })
        
        # Add timestamp and detection count
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Detections: {len(detections)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, timestamp, (10, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
    
    return detections, frame


def generate_frames(camera_source=0):
    """Generate video frames with detection"""
    global camera, detection_active
    
    try:
        camera = cv2.VideoCapture(camera_source)
        
        if not camera.isOpened():
            logger.error(f"Cannot open camera source: {camera_source}")
            return
        
        detection_active = True
        frame_count = 0
        
        while detection_active:
            success, frame = camera.read()
            
            if not success:
                break
            
            # Process every Nth frame
            if frame_count % config.DETECTION_FRAME_SKIP == 0:
                detections, processed_frame = detect_potholes(frame)
                
                # Save detection to database if found
                if detections:
                    lat, lon, source = get_location()
                    
                    for detection in detections:
                        # Save frame as image
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"detection_{timestamp}_{frame_count}.jpg"
                        image_path = os.path.join(config.DETECTIONS_DIR, image_filename)
                        
                        os.makedirs(config.DETECTIONS_DIR, exist_ok=True)
                        cv2.imwrite(image_path, frame)
                        
                        # Add to database
                        detection_data = {
                            'latitude': lat,
                            'longitude': lon,
                            'severity': detection['severity'],
                            'confidence': detection['confidence'],
                            'image_path': image_path,
                            'source': 'camera',
                            'location_source': source
                        }
                        
                        db.add_detection(detection_data)
                        logger.info(f"Detection saved: {detection['severity']} at ({lat}, {lon})")
            else:
                processed_frame = frame
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
            
    except Exception as e:
        logger.error(f"Frame generation error: {e}")
    finally:
        if camera:
            camera.release()
        detection_active = False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    camera_source = request.args.get('source', config.CAMERA_SOURCE)
    return Response(generate_frames(camera_source),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/detections', methods=['GET'])
def get_detections():
    """Get all detections"""
    try:
        limit = int(request.args.get('limit', 100))
        detections = db.get_recent_detections(limit=limit)
        return jsonify({
            'success': True,
            'count': len(detections),
            'detections': detections
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/heatmap', methods=['GET'])
def get_heatmap():
    """Get heatmap data"""
    try:
        detections = db.get_heatmap_data()
        return jsonify({
            'success': True,
            'count': len(detections),
            'data': detections
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detection statistics"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/location', methods=['GET'])
def get_current_location():
    """Get current GPS location"""
    try:
        lat, lon, source = get_location()
        return jsonify({
            'success': True,
            'latitude': lat,
            'longitude': lon,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_detection():
    """Upload detection from mobile/citizen"""
    try:
        data = request.get_json()
        
        # Get location from request or current location
        lat = data.get('latitude')
        lon = data.get('longitude')
        
        if not lat or not lon:
            lat, lon, source = get_location()
        else:
            source = 'user'
        
        # Decode image if provided
        image_path = None
        if 'image' in data:
            image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
            image_bytes = base64.b64decode(image_data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"citizen_{timestamp}.jpg"
            image_path = os.path.join(config.DETECTIONS_DIR, image_filename)
            
            os.makedirs(config.DETECTIONS_DIR, exist_ok=True)
            
            # Save image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imwrite(image_path, img)
        
        # Add to database
        detection_data = {
            'latitude': lat,
            'longitude': lon,
            'severity': data.get('severity', 'Medium'),
            'confidence': data.get('confidence', 0.5),
            'image_path': image_path,
            'source': 'citizen',
            'location_source': source,
            'description': data.get('description', '')
        }
        
        detection_id = db.add_detection(detection_data)
        
        return jsonify({
            'success': True,
            'detection_id': detection_id,
            'message': 'Detection uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start detection service"""
    global detection_active
    detection_active = True
    return jsonify({'success': True, 'message': 'Detection started'})


@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    """Stop detection service"""
    global detection_active, camera
    detection_active = False
    if camera:
        camera.release()
    return jsonify({'success': True, 'message': 'Detection stopped'})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gps_enabled': config.GPS_ENABLED,
        'gps_connected': gps_handler.is_connected() if gps_handler else False,
        'models_loaded': yolo_net is not None
    })


if __name__ == '__main__':
    # Initialize
    logger.info("="*70)
    logger.info("🚨 ASTROPATH - Starting Real-time Web Application")
    logger.info("="*70)
    
    # Load models
    load_models()
    
    # Initialize GPS
    initialize_gps()
    
    # Create required directories
    os.makedirs(config.DETECTIONS_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    # Run Flask app
    logger.info(f"\n🌐 Starting server at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info("📱 Access the dashboard from any device on your network")
    logger.info("Press Ctrl+C to stop\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        threaded=True
    )
