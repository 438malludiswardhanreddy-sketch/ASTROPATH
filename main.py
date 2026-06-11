"""
ASTROPATH Main Entry Point
Complete smart pothole detection system with dashboard, GPS, and ESP32-CAM support
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from src.utils import setup_logger

logger = setup_logger(__name__)


def main_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("🚨 ASTROPATH - Smart Road Damage Reporting & Rapid Response System 🚨")
    print("="*70)
    print("\n📊 Select operation:\n")
    print("1. 🎓 Train Pothole Classifier (ML Model Training)")
    print("2. 📹 Run Edge Detection (Camera/Video/ESP32-CAM)")
    print("3. 🌐 Start Dashboard (Real-time Detection Map)")
    print("4. 👥 Start Citizen Reporting Web App")
    print("5. 🔧 Configure Settings")
    print("6. 🧪 Test GPS Handler")
    print("7. 📷 Test ESP32-CAM Connection")
    print("8. 🔌 Test API Client")
    print("9. ℹ️  View Configuration")
    print("0. ❌ Exit\n")
    
    choice = input("Enter choice (0-9): ").strip()
    return choice


def train_classifier():
    """Launch training"""
    from src.detection.train_classifier import main
    main()


def detect_edge():
    """Launch edge detection"""
    from src.detection.detect_edge import main
    main()


def start_dashboard():
    """Launch dashboard server"""
    from src.dashboard import DashboardServer
    import os
    
    print("\n" + "="*70)
    print("🌐 ASTROPATH Dashboard Server")
    print("="*70)
    print(f"Starting dashboard at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("Press Ctrl+C to stop the server\n")
    
    db_path = os.path.join(config.BASE_DIR, "detections.db")
    dashboard = DashboardServer(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        db_path=db_path
    )
    
    try:
        dashboard.run(debug=config.FLASK_DEBUG)
    except KeyboardInterrupt:
        print("\n\nShutting down dashboard...")
        dashboard.stop()


def citizen_app():
    """Launch citizen reporting app"""
    from src.citizen_upload import main
    main()


def configure_settings():
    """Interactive configuration"""
    print("\n" + "="*70)
    print("⚙️  ASTROPATH Configuration")
    print("="*70)
    
    print("\n1. GPS Configuration")
    print(f"   - GPS Enabled: {config.GPS_ENABLED}")
    print(f"   - GPS Port: {config.GPS_PORT}")
    print(f"   - GPS Baud Rate: {config.GPS_BAUD}")
    
    print("\n2. ESP32-CAM Configuration")
    print("   - IP Address: (set in config.py)")
    print("   - Port: 80")
    
    print("\n3. Detection Settings")
    print(f"   - Confidence Threshold: {config.CONF_THRESHOLD}")
    print(f"   - NMS Threshold: {config.NMS_THRESHOLD}")
    
    print("\n4. Dashboard Settings")
    print(f"   - Dashboard URL: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"   - Debug Mode: {config.FLASK_DEBUG}")
    
    print("\nTo modify settings, edit config.py directly")
    print("="*70 + "\n")


def test_gps():
    """Test GPS handler"""
    from src.navigation.gps_handler import GPSHandler
    import time
    
    print("\n" + "="*70)
    print("🧪 GPS Handler Test")
    print("="*70)
    
    port = input(f"Enter GPS port (default: {config.GPS_PORT}): ").strip()
    if not port:
        port = config.GPS_PORT
    
    baud = input(f"Enter baud rate (default: {config.GPS_BAUD}): ").strip()
    if not baud:
        baud = config.GPS_BAUD
    else:
        baud = int(baud)
    
    print(f"\nConnecting to GPS on {port} @ {baud} baud...")
    
    try:
        gps = GPSHandler(port=port, baud=baud)
        
        if not gps.is_connected():
            print("❌ Failed to connect to GPS module")
            print("Make sure:")
            print("  1. GPS module is connected to the correct port")
            print("  2. Port name is correct (COM3, /dev/ttyACM0, etc.)")
            print("  3. Baud rate matches GPS module (usually 9600)")
            return
        
        print("✓ Connected to GPS module!\n")
        print("Reading GPS data (Press Ctrl+C to stop)...\n")
        
        for i in range(20):
            lat, lon, ts, quality = gps.get_coordinates()
            
            if lat is not None:
                print(f"[{i}] ✓ Position: ({lat:.6f}, {lon:.6f})")
                print(f"    Quality: {quality}, Time: {ts}")
            else:
                print(f"[{i}] ⏳ Waiting for GPS fix...")
            
            time.sleep(1)
        
        # Show diagnostics
        print("\n📊 GPS Diagnostics:")
        diag = gps.get_diagnostics()
        for key, value in diag.items():
            print(f"  {key}: {value}")
        
        gps.close()
        print("\n✓ GPS test completed")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"GPS test failed: {e}")


def test_esp32():
    """Test ESP32-CAM connection"""
    from src.detection.esp32_camera import ESP32Camera
    import time
    
    print("\n" + "="*70)
    print("📷 ESP32-CAM Connection Test")
    print("="*70)
    
    host = input("Enter ESP32-CAM IP address (e.g., 192.168.1.100): ").strip()
    if not host:
        print("❌ IP address required")
        return
    
    port = input("Enter port (default: 80): ").strip()
    port = int(port) if port else 80
    
    mjpeg_path = input("Enter stream path (default: /stream): ").strip()
    mjpeg_path = mjpeg_path if mjpeg_path else "/stream"
    
    print(f"\nConnecting to ESP32-CAM at {host}:{port}{mjpeg_path}...")
    
    try:
        camera = ESP32Camera(host=host, port=port, mjpeg_path=mjpeg_path)
        
        if not camera.connect():
            print("❌ Failed to connect to ESP32-CAM")
            print("Make sure:")
            print("  1. ESP32-CAM is powered on and connected to WiFi")
            print("  2. IP address is correct")
            print("  3. Both devices are on the same network")
            return
        
        print("✓ Connected to ESP32-CAM!\n")
        print("Capturing frames (Press Ctrl+C to stop)...\n")
        
        frame_count = 0
        while frame_count < 10:
            frame = camera.get_frame()
            
            if frame is not None:
                frame_count += 1
                h, w = frame.shape[:2]
                print(f"[{frame_count}] ✓ Frame captured: {w}x{h}")
                
                if frame_count % 5 == 0:
                    filename = f"esp32_test_{frame_count}.jpg"
                    camera.capture_frame(filename)
                    print(f"    Saved: {filename}")
            else:
                print("⏳ Waiting for frame...")
            
            time.sleep(0.5)
        
        # Show camera info
        print(f"\n📊 Camera Information:")
        w, h = camera.get_resolution()
        print(f"  Resolution: {w}x{h}")
        print(f"  Connected: {camera.is_connected()}")
        
        camera.disconnect()
        print("\n✓ ESP32-CAM test completed")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"ESP32-CAM test failed: {e}")


def test_api():
    """Test API client"""
    from src.api_client import test_api
    test_api()


def show_config():
    """Display configuration"""
    print("\n" + "="*70)
    print("ℹ️  ASTROPATH Configuration Summary")
    print("="*70)
    
    print("\n📁 Directories:")
    print(f"  Models: {config.MODELS_DIR}")
    print(f"  Data: {config.DATA_DIR}")
    print(f"  Detections: {config.DETECTIONS_DIR}")
    
    print("\n📷 Camera & Detection:")
    print(f"  Camera Source: {config.CAMERA_SOURCE}")
    print(f"  YOLO Input Size: {config.IMG_SIZE_YOLO}")
    print(f"  Classifier Input Size: {config.IMG_SIZE_CLASSIFIER}")
    print(f"  Confidence Threshold: {config.CONF_THRESHOLD}")
    print(f"  NMS Threshold: {config.NMS_THRESHOLD}")
    print(f"  Frame Skip: {config.DETECTION_FRAME_SKIP}")
    
    print("\n🛰️  GPS Configuration:")
    print(f"  GPS Enabled: {config.GPS_ENABLED}")
    print(f"  GPS Port: {config.GPS_PORT}")
    print(f"  GPS Baud Rate: {config.GPS_BAUD}")
    print(f"  GPS Min Satellites: {config.GPS_MIN_SATS}")
    
    print("\n🌐 API & Dashboard:")
    print(f"  API URL: {config.API_URL}")
    print(f"  API Timeout: {config.API_TIMEOUT}s")
    print(f"  Cloud Upload: {config.ENABLE_CLOUD_UPLOAD}")
    print(f"  Dashboard: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"  Flask Debug: {config.FLASK_DEBUG}")
    
    print("\n⚙️  System:")
    print(f"  Log Level: {config.LOG_LEVEL}")
    print(f"  Log File: {config.LOG_FILE}")
    print(f"  Debug Mode: {config.DEBUG_MODE}")
    print(f"  FPS Counter: {config.ENABLE_FPS_COUNTER}")
    
    print("\n" + "="*70)
    print("Edit config.py to change settings")
    print("="*70 + "\n")


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("ASTROPATH - Smart Road Damage Reporting System")
    logger.info("="*70)
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            print("\n🎓 Training Classifier...")
            try:
                train_classifier()
            except Exception as e:
                logger.error(f"Training failed: {e}")
        
        elif choice == '2':
            print("\n📹 Starting Edge Detection...")
            try:
                detect_edge()
            except Exception as e:
                logger.error(f"Detection failed: {e}")
        
        elif choice == '3':
            print("\n🌐 Starting Dashboard Server...")
            try:
                start_dashboard()
            except Exception as e:
                logger.error(f"Dashboard failed: {e}")
        
        elif choice == '4':
            print("\n👥 Starting Citizen Reporting App...")
            try:
                citizen_app()
            except Exception as e:
                logger.error(f"App failed: {e}")
        
        elif choice == '5':
            configure_settings()
        
        elif choice == '6':
            print("\n🧪 Testing GPS Handler...")
            try:
                test_gps()
            except Exception as e:
                logger.error(f"GPS test failed: {e}")
        
        elif choice == '7':
            print("\n📷 Testing ESP32-CAM...")
            try:
                test_esp32()
            except Exception as e:
                logger.error(f"ESP32-CAM test failed: {e}")
        
        elif choice == '8':
            print("\n🔌 Testing API Client...")
            try:
                test_api()
            except Exception as e:
                logger.error(f"API test failed: {e}")
        
        elif choice == '9':
            show_config()
        
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
