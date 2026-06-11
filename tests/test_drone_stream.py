"""
ASTROPATH - Test Drone Video Stream
Quick utility to test drone video streaming before running full detection
"""

import cv2
import sys
import time
from datetime import datetime

def test_stream(url):
    """Test drone video stream"""
    print("="*70)
    print("🚁 ASTROPATH - Drone Stream Tester")
    print("="*70)
    print(f"\n📡 Testing stream: {url}")
    print("Press 'q' to quit, 's' to save snapshot\n")
    
    # Try to connect
    print("Connecting...")
    cap = cv2.VideoCapture(url)
    
    if not cap.isOpened():
        print("❌ Failed to connect to stream")
        print("\nTroubleshooting:")
        print("1. Check drone is powered on and connected")
        print("2. Verify IP address and port")
        print("3. Ensure both devices on same network")
        print("4. Try different stream URL formats:")
        print("   - RTSP: rtsp://IP:8554/video")
        print("   - UDP:  udp://IP:5600")
        print("   - HTTP: http://IP:8080/video")
        return False
    
    print("✓ Connected to stream!\n")
    
    # Get stream info
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    
    print(f"Stream Info:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print()
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("\n⚠ Stream interrupted or ended")
                break
            
            frame_count += 1
            
            # Calculate actual FPS
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                
                # Overlay info
                info_text = f"FPS: {actual_fps:.1f} | Frame: {frame_count} | {width}x{height}"
                cv2.putText(frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, timestamp, (10, height - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display
            cv2.imshow('Drone Stream Test - Press Q to quit, S to snapshot', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✓ Stream test stopped by user")
                break
            elif key == ord('s'):
                filename = f"snapshot_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📷 Snapshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n✓ Stream test interrupted")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # Final stats
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\nTest Statistics:")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Frames received: {frame_count}")
        print(f"  Average FPS: {avg_fps:.1f}")
        print()
    
    return True


def main():
    """Main function"""
    print()
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Enter drone stream URL:")
        print("\nCommon formats:")
        print("  RTSP: rtsp://192.168.1.100:8554/video")
        print("  UDP:  udp://192.168.1.100:5600")
        print("  HTTP: http://192.168.1.100:8080/video")
        print("  File: /path/to/video.mp4")
        print()
        url = input("URL: ").strip()
    
    if not url:
        print("❌ URL required")
        print(f"Usage: python {sys.argv[0]} <stream_url>")
        return
    
    success = test_stream(url)
    
    if success:
        print("✓ Stream test successful!")
        print("\nNext steps:")
        print("1. Run: python src/drone_detector.py")
        print("2. Or update config.py with this URL")
        print("3. Or use in web interface at http://localhost:5000")
    else:
        print("❌ Stream test failed")
        print("\nGet help:")
        print("- Check DRONE_GUIDE.md for setup instructions")
        print("- Verify drone manufacturer's streaming guide")
        print("- Test with VLC or ffplay first")


if __name__ == "__main__":
    main()
