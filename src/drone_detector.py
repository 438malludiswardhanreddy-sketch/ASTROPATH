"""
ASTROPATH - Drone Detection Module
Real-time pothole detection from drone video streams with GPS coordinate projection
"""

import cv2
import numpy as np
import logging
import time
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger
from src.database import DetectionDatabase

logger = setup_logger(__name__)


class DroneDetector:
    """Real-time detection from drone video with ground coordinate projection"""
    
    def __init__(self, drone_controller, yolo_net=None, classifier=None):
        """
        Initialize drone detector
        
        Args:
            drone_controller: DroneController instance
            yolo_net: Pre-loaded YOLO network (optional)
            classifier: Pre-loaded classifier (optional)
        """
        self.drone = drone_controller
        self.yolo_net = yolo_net
        self.classifier = classifier
        self.db = DetectionDatabase()
        
        # Load models if not provided
        if self.yolo_net is None:
            self.load_yolo()
        
        self.detection_count = 0
        self.frame_count = 0
        
        logger.info("✓ Drone detector initialized")
    
    def load_yolo(self):
        """Load YOLO model"""
        try:
            if os.path.exists(config.YOLOV4_WEIGHTS) and os.path.exists(config.YOLOV4_CFG):
                logger.info("Loading YOLO model for drone detection...")
                self.yolo_net = cv2.dnn.readNetFromDarknet(config.YOLOV4_CFG, config.YOLOV4_WEIGHTS)
                
                if config.USE_CUDA:
                    self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                    self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                else:
                    self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                    self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                
                logger.info("✓ YOLO model loaded")
            else:
                logger.warning("YOLO model files not found")
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
    
    def detect_in_frame(self, frame):
        """
        Detect potholes in a frame
        
        Args:
            frame: Input frame from drone
            
        Returns:
            List of detections with bounding boxes, confidence, and severity
        """
        detections = []
        
        if self.yolo_net is None:
            return detections
        
        try:
            height, width = frame.shape[:2]
            
            # Prepare blob for YOLO
            img_size = config.FAST_IMG_SIZE_YOLO if config.FAST_MODE else config.IMG_SIZE_YOLO
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (img_size, img_size), swapRB=True, crop=False)
            self.yolo_net.setInput(blob)
            
            # Get output layers
            layer_names = self.yolo_net.getLayerNames()
            output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
            
            # Forward pass
            outputs = self.yolo_net.forward(output_layers)
            
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
                        elif area_ratio < 0.05:
                            severity = "Medium"
                        else:
                            severity = "High"
                        
                        detections.append({
                            'bbox': [x, y, w, h],
                            'center': [center_x, center_y],
                            'confidence': confidence,
                            'severity': severity,
                            'area_ratio': area_ratio
                        })
        
        except Exception as e:
            logger.error(f"Detection error: {e}")
        
        return detections
    
    def annotate_frame(self, frame, detections, show_telemetry=True):
        """
        Annotate frame with detections and telemetry
        
        Args:
            frame: Input frame
            detections: List of detections
            show_telemetry: Show drone telemetry overlay
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        height, width = frame.shape[:2]
        
        # Draw detections
        for det in detections:
            x, y, w, h = det['bbox']
            confidence = det['confidence']
            severity = det['severity']
            
            # Color based on severity
            if severity == "Low":
                color = (0, 255, 0)  # Green
            elif severity == "Medium":
                color = (0, 165, 255)  # Orange
            else:
                color = (0, 0, 255)  # Red
            
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{severity}: {confidence:.2f}"
            cv2.putText(annotated, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Telemetry overlay
        if show_telemetry:
            telemetry = self.drone.get_telemetry()
            
            # Semi-transparent overlay box
            overlay = annotated.copy()
            cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)
            
            # Telemetry text
            y_offset = 30
            cv2.putText(annotated, f"Altitude: {telemetry['altitude']:.1f}m", 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            y_offset += 20
            cv2.putText(annotated, f"Position: {telemetry['latitude']:.6f}, {telemetry['longitude']:.6f}", 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            y_offset += 20
            cv2.putText(annotated, f"Heading: {telemetry['heading']:.1f}°", 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            y_offset += 20
            cv2.putText(annotated, f"Speed: {telemetry['speed']:.1f} m/s", 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Detection count
        cv2.putText(annotated, f"Detections: {len(detections)}", 
                   (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated, timestamp, 
                   (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def save_detection(self, frame, detection):
        """
        Save detection to database with ground coordinates
        
        Args:
            frame: Original frame
            detection: Detection dict
            
        Returns:
            Detection ID if saved successfully
        """
        try:
            # Get ground coordinates for detection center
            center_pixel = detection['center']
            ground_lat, ground_lon = self.drone.pixel_to_ground_coords(
                center_pixel[0], center_pixel[1],
                frame.shape[1], frame.shape[0]
            )
            
            # Save frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_filename = f"drone_detection_{timestamp}.jpg"
            image_path = os.path.join(config.DETECTIONS_DIR, image_filename)
            
            os.makedirs(config.DETECTIONS_DIR, exist_ok=True)
            cv2.imwrite(image_path, frame)
            
            # Prepare detection data
            detection_data = {
                'latitude': ground_lat,
                'longitude': ground_lon,
                'altitude': self.drone.get_telemetry()['altitude'],
                'severity': detection['severity'],
                'confidence': detection['confidence'],
                'image_path': image_path,
                'source': 'drone',
                'location_source': 'drone_gps',
                'heading': self.drone.get_telemetry()['heading'],
                'bbox': str(detection['bbox'])
            }
            
            # Add to database
            detection_id = self.db.add_detection(detection_data)
            
            self.detection_count += 1
            logger.info(f"Detection #{self.detection_count} saved at ({ground_lat:.6f}, {ground_lon:.6f})")
            
            return detection_id
            
        except Exception as e:
            logger.error(f"Failed to save detection: {e}")
            return None
    
    def run_survey(self, duration=None, save_video=True, auto_save_detections=True):
        """
        Run automated survey mission
        
        Args:
            duration: Survey duration in seconds (None for continuous)
            save_video: Save video to file
            auto_save_detections: Automatically save detections to database
            
        Returns:
            Survey statistics
        """
        logger.info("="*70)
        logger.info("🚁 ASTROPATH Drone Survey Mission")
        logger.info("="*70)
        
        # Video writer setup
        video_writer = None
        if save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = os.path.join(config.DETECTIONS_DIR, f"drone_survey_{timestamp}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
        start_time = time.time()
        total_detections = 0
        frames_processed = 0
        
        logger.info(f"Starting survey from: {self.drone.stream_url}")
        logger.info("Press 'q' to stop, 's' to save current frame")
        print()
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"Survey duration ({duration}s) completed")
                    break
                
                # Get frame
                ret, frame = self.drone.read_frame()
                
                if not ret or frame is None:
                    logger.warning("Failed to get frame")
                    time.sleep(0.1)
                    continue
                
                # Initialize video writer with actual frame size
                if save_video and video_writer is None:
                    height, width = frame.shape[:2]
                    video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (width, height))
                
                # Process every Nth frame
                if frames_processed % config.DETECTION_FRAME_SKIP == 0:
                    # Detect
                    detections = self.detect_in_frame(frame)
                    
                    # Save detections
                    if auto_save_detections and detections:
                        for detection in detections:
                            self.save_detection(frame, detection)
                            total_detections += 1
                    
                    # Annotate
                    annotated = self.annotate_frame(frame, detections, show_telemetry=True)
                else:
                    annotated = frame
                
                frames_processed += 1
                
                # Write video
                if save_video and video_writer:
                    video_writer.write(annotated)
                
                # Display
                cv2.imshow('ASTROPATH Drone Survey', annotated)
                
                # Keyboard controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Survey stopped by user")
                    break
                elif key == ord('s'):
                    # Manual save
                    save_path = os.path.join(config.DETECTIONS_DIR, f"manual_{int(time.time())}.jpg")
                    cv2.imwrite(save_path, frame)
                    logger.info(f"Frame saved: {save_path}")
        
        except KeyboardInterrupt:
            logger.info("Survey interrupted by user")
        
        except Exception as e:
            logger.error(f"Survey error: {e}")
        
        finally:
            # Cleanup
            if video_writer:
                video_writer.release()
                logger.info(f"Video saved: {video_path}")
            
            cv2.destroyAllWindows()
            
            # Statistics
            elapsed = time.time() - start_time
            fps = frames_processed / elapsed if elapsed > 0 else 0
            
            stats = {
                'duration': elapsed,
                'frames_processed': frames_processed,
                'total_detections': total_detections,
                'fps': fps,
                'survey_area': 'calculated'  # TODO: Calculate from flight path
            }
            
            logger.info("")
            logger.info("="*70)
            logger.info("📊 Survey Statistics")
            logger.info("="*70)
            logger.info(f"Duration: {elapsed:.1f}s")
            logger.info(f"Frames Processed: {frames_processed}")
            logger.info(f"Detections Found: {total_detections}")
            logger.info(f"Average FPS: {fps:.1f}")
            logger.info("="*70)
            
            return stats


def main():
    """Main function for drone detection"""
    from src.drone_controller import DroneController
    
    print()
    print("="*70)
    print("🚁 ASTROPATH - Drone Detection System")
    print("="*70)
    print()
    
    # Get stream URL
    stream_url = input("Enter drone stream URL (or press Enter for default): ").strip()
    if not stream_url:
        # Default examples
        print("\nExample stream URLs:")
        print("1. RTSP: rtsp://192.168.1.100:8554/video")
        print("2. UDP:  udp://192.168.1.100:5600")
        print("3. HTTP: http://192.168.1.100:8080/video")
        print()
        stream_url = input("Enter URL: ").strip()
    
    if not stream_url:
        print("❌ Stream URL required")
        return
    
    # Initialize drone controller
    print(f"\n📡 Connecting to: {stream_url}")
    drone = DroneController(stream_url=stream_url)
    
    if not drone.connect():
        print("❌ Failed to connect to drone")
        return
    
    print("✓ Connected to drone stream")
    
    # Initialize detector
    print("\n🔧 Initializing detector...")
    detector = DroneDetector(drone)
    
    # Survey options
    print("\n📋 Survey Options:")
    duration_input = input("Survey duration in seconds (or press Enter for continuous): ").strip()
    duration = int(duration_input) if duration_input else None
    
    save_video_input = input("Save video? (y/n, default=y): ").strip().lower()
    save_video = save_video_input != 'n'
    
    auto_save_input = input("Auto-save detections? (y/n, default=y): ").strip().lower()
    auto_save = auto_save_input != 'n'
    
    # Run survey
    print()
    stats = detector.run_survey(
        duration=duration,
        save_video=save_video,
        auto_save_detections=auto_save
    )
    
    # Cleanup
    drone.disconnect()
    print("\n✓ Survey complete!")


if __name__ == "__main__":
    main()
