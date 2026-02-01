"""
ASTROPATH Edge Detection Module (detect_edge.py)
Core detection script for Raspberry Pi: YOLO + severity estimation + API upload
Upgraded version of camera_video (1).py with modular design
"""

import os
import sys
import cv2
import numpy as np
import time
from datetime import datetime
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger, get_geolocation, save_image, FPSCounter, ensure_dir_exists, create_detection_payload
from src.gps_handler import GPSHandler

logger = setup_logger(__name__)

try:
    from tensorflow.keras.models import load_model
except ImportError:
    logger.warning("TensorFlow not available. Using YOLO only.")
    load_model = None


class YOLODetector:
    """YOLO-based pothole detection"""
    
    def __init__(self, weights_path, cfg_path, names_path):
        logger.info("Initializing YOLO detector...")
        
        # Load network
        self.net = cv2.dnn.readNet(weights_path, cfg_path)

        # Prefer CUDA if configured and available
        try:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            if getattr(config, 'USE_CUDA', False):
                # Attempt to use CUDA target if available in OpenCV build
                try:
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                    logger.info('Using CUDA for DNN inference')
                except Exception:
                    logger.warning('CUDA target not available, falling back to CPU')
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            else:
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        except Exception as e:
            logger.debug(f'DNN backend/target setup error: {e}')

        self.model = cv2.dnn_DetectionModel(self.net)
        # Choose smaller input when FAST_MODE enabled
        input_size = config.FAST_IMG_SIZE_YOLO if getattr(config, 'FAST_MODE', False) else config.IMG_SIZE_YOLO
        self.model.setInputParams(
            size=(input_size, input_size),
            scale=1/255,
            swapRB=True
        )
        
        # Load class names
        with open(names_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        logger.info(f"YOLO loaded. Classes: {self.classes}")
    
    def detect(self, frame):
        """Detect objects in frame"""
        classes_ids, confidences, boxes = self.model.detect(
            frame,
            config.CONF_THRESHOLD,
            config.NMS_THRESHOLD
        )
        
        detections = []
        for (class_id, confidence, box) in zip(classes_ids, confidences, boxes):
            detections.append({
                'class_id': int(class_id),
                'class_name': self.classes[class_id] if class_id < len(self.classes) else 'Unknown',
                'confidence': float(confidence),
                'box': box,
                'x': int(box[0]),
                'y': int(box[1]),
                'w': int(box[2]),
                'h': int(box[3])
            })
        
        return detections


class SeverityEstimator:
    """Estimate pothole severity based on multiple factors"""
    
    def __init__(self, classifier_path=None):
        self.classifier = None
        if classifier_path and os.path.exists(classifier_path) and load_model:
            try:
                self.classifier = load_model(classifier_path)
                logger.info(f"Classifier loaded: {classifier_path}")
            except Exception as e:
                logger.warning(f"Failed to load classifier: {e}. Using heuristic-based severity only.")
    
    def estimate(self, frame, detection, frame_shape):
        """
        Estimate severity based on:
        1. Bounding box area ratio
        2. Classifier confidence (if available)
        3. Location in frame (center vs edge)
        """
        x, y, w, h = detection['x'], detection['y'], detection['w'], detection['h']
        
        # Extract crop
        crop = frame[y:y+h, x:x+w]
        if crop.size == 0:
            return "Unknown", 0.5
        
        # Area ratio (proportion of frame)
        area_ratio = (w * h) / (frame_shape[0] * frame_shape[1])
        
        # Classifier confidence (if available)
        classifier_conf = 0.5
        if self.classifier:
            try:
                crop_resized = cv2.resize(crop, (config.IMG_SIZE_CLASSIFIER, config.IMG_SIZE_CLASSIFIER))
                crop_normalized = crop_resized.astype(np.float32) / 255.0
                crop_input = np.expand_dims(crop_normalized, axis=0)
                classifier_conf = float(self.classifier.predict(crop_input, verbose=0)[0][0])
            except Exception as e:
                logger.debug(f"Classifier inference error: {e}")
        
        # Determine severity based on area and confidence
        if area_ratio < config.SEVERITY_THRESHOLDS["area_ratio_low"]:
            severity = "Low"
            severity_score = 0.3
        elif area_ratio < config.SEVERITY_THRESHOLDS["area_ratio_medium"]:
            severity = "Medium"
            severity_score = 0.6
        else:
            severity = "High"
            severity_score = 0.9
        
        # Adjust based on classifier confidence
        if self.classifier:
            severity_score = (severity_score + classifier_conf) / 2
        
        return severity, severity_score
    
    @staticmethod
    def get_severity_color(severity):
        """Get BGR color for severity level"""
        colors = {
            "Low": (0, 255, 0),      # Green
            "Medium": (0, 165, 255),  # Orange
            "High": (0, 0, 255),      # Red
        }
        return colors.get(severity, (255, 255, 255))


class EdgeDetectionPipeline:
    """Full detection pipeline for edge device"""
    
    def __init__(self):
        logger.info("Initializing EdgeDetectionPipeline...")
        
        # Check model files
        if not all(os.path.exists(p) for p in [config.YOLOV4_WEIGHTS, config.YOLOV4_CFG, config.OBJ_NAMES]):
            logger.error("YOLO model files not found. Please download from: https://github.com/AlexeyAB/darknet")
            raise FileNotFoundError("Missing YOLO model files")
        
        self.detector = YOLODetector(
            config.YOLOV4_WEIGHTS,
            config.YOLOV4_CFG,
            config.OBJ_NAMES
        )
        
        self.severity_estimator = SeverityEstimator(config.CLASSIFIER_MODEL)
        
        self.fps_counter = FPSCounter(window_size=30) if config.ENABLE_FPS_COUNTER else None
        self.frame_count = 0
        self.detection_count = 0

        # Initialize GPS if enabled
        self.gps = None
        if config.GPS_ENABLED:
            try:
                self.gps = GPSHandler(
                    port=config.GPS_PORT,
                    baud=config.GPS_BAUD,
                    timeout=config.GPS_TIMEOUT,
                    max_retries=config.GPS_MAX_RETRIES,
                    min_sats=config.GPS_MIN_SATS
                )
                if self.gps.is_connected():
                    logger.info(f"GPS connected on {config.GPS_PORT}")
                else:
                    logger.warning(f"GPS module not responding on {config.GPS_PORT}")
                    if config.GPS_FALLBACK_TO_IP:
                        logger.info("Will use IP geolocation fallback")
            except Exception as e:
                logger.error(f"GPS initialization failed: {e}")
                if config.GPS_FALLBACK_TO_IP:
                    logger.info("Will use IP geolocation fallback")
                self.gps = None
        
        ensure_dir_exists(config.DETECTIONS_DIR)
        logger.info("Pipeline ready")


class VideoStream:
    """Simple threaded video capture to reduce frame latency."""
    def __init__(self, src=0):
        self.src = src
        self.cap = cv2.VideoCapture(src)
        self.stopped = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.update, daemon=True)
            self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            try:
                ret, frame = self.cap.read()
            except Exception:
                ret = False
                frame = None

            if not ret or frame is None:
                time.sleep(0.01)
                continue

            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return None
            # Return a copy to avoid race conditions
            return self.frame.copy()

    def stop(self):
        self.stopped = True
        if self.thread:
            self.thread.join(timeout=0.5)
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
    
    def process_frame(self, frame):
        """Process single frame: detect -> estimate severity -> annotate"""
        self.frame_count += 1
        
        # Skip frames for performance
        if self.frame_count % config.DETECTION_FRAME_SKIP != 0 and config.DETECTION_FRAME_SKIP > 1:
            return frame, []
        
        # Detect objects
        detections = self.detector.detect(frame)
        
        # Filter and process detections
        processed_detections = []
        for det in detections:
            if det['confidence'] < 0.6:
                continue
            
            # Estimate severity (pass frame first, then detection)
            severity, severity_score = self.severity_estimator.estimate(frame, det, frame.shape)
            det['severity'] = severity
            det['severity_score'] = severity_score
            
            processed_detections.append(det)
            self.detection_count += 1
        
        # Annotate frame
        annotated_frame = self._annotate_frame(frame, processed_detections)
        
        # Add FPS counter
        if self.fps_counter:
            self.fps_counter.update()
            fps = self.fps_counter.get_fps()
            if fps > 0:
                cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add detection counter
        cv2.putText(annotated_frame, f"Detections: {self.detection_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return annotated_frame, processed_detections
    
    def _annotate_frame(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        annotated = frame.copy()
        
        for det in detections:
            x, y, w, h = det['x'], det['y'], det['w'], det['h']
            severity = det['severity']
            confidence = det['confidence']
            
            color = SeverityEstimator.get_severity_color(severity)
            
            # Draw bounding box


            
            cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
            
            # Draw label
            label = f"{det['class_name']} {severity} ({confidence:.2f})"
            cv2.putText(annotated, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return annotated
    
    def run(self, source=0, output_video=None):
        """Run detection pipeline on video source"""
        logger.info(f"Starting detection on source: {source}")
        
        # Open video source using threaded capture to reduce latency
        vs = VideoStream(source).start()
        if not vs.cap.isOpened():
            logger.error(f"Failed to open video source: {source}")
            return

        # Get video properties from underlying capture
        frame_width = int(vs.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(vs.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(vs.cap.get(cv2.CAP_PROP_FPS)) or 20
        
        logger.info(f"Video: {frame_width}x{frame_height} @ {fps} FPS")
        
        # Setup video writer if output requested
        writer = None
        if output_video and config.SAVE_DETECTIONS:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
        
        try:
            while True:
                frame = vs.read()
                if frame is None:
                    # No frame yet (stream warming) or end of stream
                    time.sleep(0.005)
                    continue
                
                # Process frame
                annotated_frame, detections = self.process_frame(frame)
                
                # Save detection images and prepare API payloads
                if detections and config.SAVE_DETECTIONS:
                    for det in detections:
                        img_path = save_image(annotated_frame, config.DETECTIONS_DIR, "pothole")

                        # Prefer GPS coordinates when available, else use cached or IP fallback
                        chosen_lat = None
                        chosen_lon = None
                        gps_meta = {}

                        if self.gps:
                            gps_lat, gps_lon, gps_ts, gps_quality = self.gps.get_coordinates()
                            if gps_lat is not None and gps_quality >= config.GPS_MIN_QUALITY:
                                chosen_lat, chosen_lon = gps_lat, gps_lon
                                gps_meta = {
                                    'gps_timestamp': gps_ts,
                                    'gps_quality': gps_quality
                                }
                                logger.info(f"GPS Fix: ({gps_lat:.6f}, {gps_lon:.6f}) Quality={gps_quality}")
                            elif config.GPS_USE_CACHED_IF_NO_FIX:
                                cached_lat, cached_lon, cached_ts = self.gps.get_cached_coordinates()
                                if cached_lat is not None:
                                    chosen_lat, chosen_lon = cached_lat, cached_lon
                                    gps_meta = {
                                        'gps_timestamp': cached_ts,
                                        'gps_quality': 0
                                    }
                                    logger.debug(f"Using cached GPS: ({cached_lat:.6f}, {cached_lon:.6f})")
                                else:
                                    logger.debug("No cached GPS available")
                            else:
                                logger.debug("GPS present but no valid fix")

                        # Fallback to IP geolocation if allowed and no GPS coords
                        if (chosen_lat is None or chosen_lon is None) and config.GPS_FALLBACK_TO_IP:
                            ip_lat, ip_lon = get_geolocation()
                            if ip_lat and ip_lon:
                                chosen_lat, chosen_lon = ip_lat, ip_lon
                                logger.info(f"Using IP geolocation: ({ip_lat}, {ip_lon})")

                        payload = create_detection_payload(
                            {
                                'class': det['class_name'],
                                'severity': det['severity'],
                                'confidence': det['confidence'],
                                'image_path': img_path,
                            },
                            chosen_lat, chosen_lon
                        )

                        # Inject any GPS metadata into payload before sending
                        if gps_meta:
                            payload.update(gps_meta)

                        logger.info(f"Detection: {payload}")

                        # Send to cloud (if enabled)
                        if config.ENABLE_CLOUD_UPLOAD:
                            self._send_to_api(payload)
                
                # Write to output video
                if writer:
                    writer.write(annotated_frame)
                
                # Display frame
                cv2.imshow("ASTROPATH Detection", annotated_frame)
                
                # Break on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            try:
                vs.stop()
            except Exception:
                pass
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            logger.info(f"Detection complete. Total frames: {self.frame_count}, Detections: {self.detection_count}")

            # Close GPS connection
            if self.gps:
                try:
                    diag = self.gps.get_diagnostics()
                    logger.info(f"GPS Statistics: {diag}")
                    self.gps.close()
                except Exception as e:
                    logger.error(f"Error closing GPS: {e}")
    
    def _send_to_api(self, payload):
        """Send detection payload to cloud API"""
        try:
            import requests
            response = requests.post(config.API_URL, json=payload, timeout=config.API_TIMEOUT)
            if response.status_code == 200:
                logger.info(f"API response: {response.status_code}")
            else:
                logger.warning(f"API error: {response.status_code}")
        except Exception as e:
            logger.error(f"API connection failed: {e}")


def main():
    """Main detection entry point"""
    logger.info("="*60)
    logger.info("ASTROPATH Edge Detection")
    logger.info("="*60)
    
    # Initialize pipeline
    pipeline = EdgeDetectionPipeline()
    
    # Determine source
    source = config.CAMERA_SOURCE
    if isinstance(source, int) and source == 0:
        # Webcam
        logger.info("Using webcam")
    elif isinstance(source, str):
        # Check if file or URL
        if source.startswith(('http', 'udp', 'rtsp')):
            logger.info(f"Using stream: {source}")
        else:
            # File
            if os.path.exists(source):
                logger.info(f"Using video file: {source}")
            else:
                logger.warning(f"File not found: {source}")
                return
    
    # Run detection
    pipeline.run(source, output_video=config.VIDEO_OUTPUT_PATH)


if __name__ == "__main__":
    main()
