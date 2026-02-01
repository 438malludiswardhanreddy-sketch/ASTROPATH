# 🎥 ESP32-CAM Integration Guide

Complete setup instructions for integrating ESP32-CAM boards with ASTROPATH pothole detection system.

## 📋 Table of Contents
1. [Hardware Setup](#hardware-setup)
2. [Firmware Installation](#firmware-installation)
3. [Network Configuration](#network-configuration)
4. [Python Integration](#python-integration)
5. [Troubleshooting](#troubleshooting)
6. [Multi-Camera Setup](#multi-camera-setup)

---

## 🔧 Hardware Setup

### Components Required
- **ESP32-CAM Board** (OV2640 camera recommended)
  - Links: [Aliexpress](https://www.aliexpress.com) | [Amazon](https://www.amazon.com)
  - Alternative: ESP32-S3-CAM (higher performance)
  
- **USB-TTL Converter** (for programming)
  - CH340 or FT232RL recommended
  - ~₹150-300
  
- **Micro USB Cable** (for power)
  - Standard USB-A to Micro-B
  
- **Jumper Wires** (male-to-female)
  - For connection to USB-TTL converter

### Pinout Connections

#### ESP32-CAM to USB-TTL Converter
```
ESP32-CAM Pin          USB-TTL Pin
─────────────          ──────────
GND                    GND
3V3                    VCC (3.3V)
TX (GPIO1)             RXD
RX (GPIO3)             TXD
IO0                    GND (during programming)
```

### Physical Connection Steps
1. **Disconnect power** from all devices
2. **Connect pins** according to the table above
3. **Bridge IO0 to GND** using jumper wire (puts ESP32 in bootloader mode)
4. **Connect USB** to your computer
5. **Verify** COM port appears in Device Manager (Windows) or `lsusb` (Linux)

---

## 📦 Firmware Installation

### Option A: Arduino IDE (Recommended)

#### 1. Install Arduino IDE
- Download from: https://www.arduino.cc/en/software
- Version 1.8.19 or later recommended

#### 2. Add ESP32 Board Support
1. Go to **File → Preferences**
2. In "Additional Boards Manager URLs", add:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
3. Click **OK**
4. Go to **Tools → Board → Board Manager**
5. Search for "esp32" and install by Espressif Systems

#### 3. Select Board Configuration
1. **Tools → Board → ESP32 Arduino → AI Thinker ESP32-CAM**
2. **Tools → Port → COMx** (select your USB port)
3. **Tools → Upload Speed → 115200**
4. **Tools → Partition Scheme → Huge APP (3MB No OTA)**

#### 4. Upload Camera Webserver Sketch
1. Go to **File → Examples → ESP32 → Camera → CameraWebServer**
2. **Edit** the sketch to add your WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_SSID";
   const char* password = "YOUR_PASSWORD";
   ```
3. Click **Upload** (while IO0 is still bridged to GND)
4. Wait for upload to complete (~1-2 minutes)
5. **Remove** the IO0-GND jumper wire
6. Open Serial Monitor (**Tools → Serial Monitor**)
7. Press **RST** button on ESP32-CAM
8. You should see:
   ```
   Camera init OK
   Ready! Use 'http://192.168.x.x:81' to connect
   ```

### Option B: Using esptool.py (Advanced)

```bash
# Install esptool
pip install esptool

# Download pre-built firmware
# Then flash:
python -m esptool --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 camera_webserver.bin
```

---

## 🌐 Network Configuration

### Find ESP32-CAM IP Address
1. Open Serial Monitor (see step 6-8 above)
2. Note the IP address displayed (e.g., `192.168.1.100`)
3. Or check your WiFi router's connected devices list

### Test Camera Stream

#### In Web Browser
1. Open: `http://192.168.1.100:81` (replace with your IP)
2. You should see live camera feed and control panel
3. Test stream URL: `http://192.168.1.100:81/stream`

#### Using curl (Command Line)
```bash
# Get single JPEG frame
curl "http://192.168.1.100:81/capture" > frame.jpg

# Get MJPEG stream (save to file)
curl "http://192.168.1.100:81/stream" > stream.mjpeg
```

### Camera Control URLs
```
/stream          - MJPEG stream (for continuous video)
/capture         - Single JPEG frame
/control?var=framesize&val=10    - Change resolution
/control?var=quality&val=10      - Change JPEG quality
/control?var=brightness&val=0    - Adjust brightness
/control?var=contrast&val=0      - Adjust contrast
/control?var=saturation&val=0    - Adjust saturation
```

---

## 🐍 Python Integration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Single Camera Test

Create `test_esp32.py`:
```python
import sys
sys.path.insert(0, '.')
from src.esp32_camera import ESP32Camera
import time

# Connect to ESP32-CAM
camera = ESP32Camera(
    host="192.168.1.100",      # Update with your ESP32 IP
    port=80,
    mjpeg_path="/stream"
)

if camera.connect():
    print("Connected to ESP32-CAM!")
    
    # Capture 10 frames
    for i in range(10):
        frame = camera.get_frame()
        if frame is not None:
            print(f"Frame {i}: {frame.shape}")
            
            # Save every 5th frame
            if i % 5 == 0:
                camera.capture_frame(f"esp32_frame_{i}.jpg")
        
        time.sleep(0.5)
    
    camera.disconnect()
else:
    print("Failed to connect")
```

Run it:
```bash
python test_esp32.py
```

### 3. Multi-Camera Setup

Create `test_multi_camera.py`:
```python
import sys
sys.path.insert(0, '.')
from src.esp32_camera import MultiCameraController
import time

# Initialize controller
controller = MultiCameraController()

# Add multiple cameras
controller.add_camera("Front", "192.168.1.100", 80)
controller.add_camera("Back", "192.168.1.101", 80)
controller.add_camera("Side", "192.168.1.102", 80)

print(f"Connected to {len(controller)} cameras")

# Get frames from all cameras
for i in range(5):
    frames = controller.get_all_frames()
    print(f"Got frames from {len(frames)} cameras")
    time.sleep(1)

controller.disconnect_all()
```

### 4. Integration with Detection Pipeline

Update `src/detect_edge.py` to use ESP32-CAM:
```python
from src.esp32_camera import ESP32Camera

# Initialize ESP32-CAM
camera = ESP32Camera(host="192.168.1.100", port=80)
if not camera.connect():
    logger.error("Failed to connect to ESP32-CAM")
    exit(1)

# In detection loop
while True:
    frame = camera.get_frame()
    if frame is None:
        continue
    
    # Run detection on frame
    detections = detector.detect(frame)
    
    # ... rest of detection code ...
```

---

## 🐛 Troubleshooting

### Issue: "Failed to connect to ESP32-CAM"
**Solutions:**
1. Verify ESP32-CAM IP address is correct
2. Check both devices are on same WiFi network
3. Ping ESP32: `ping 192.168.1.100`
4. Check firewall isn't blocking port 80
5. Restart ESP32-CAM (press RST button)

### Issue: "USB Device Not Found"
**Solutions:**
1. Install CH340 driver if using that chip:
   - [Windows Driver](http://www.wch-ic.com/downloads/CH341SER_EXE.html)
   - Linux: Usually detected automatically
   - Mac: [Driver](http://www.wch-ic.com/downloads/CH34XSER_MAC_ZIP.html)
2. Try different USB port
3. Try different USB cable

### Issue: "Upload timed out"
**Solutions:**
1. Ensure IO0 is connected to GND
2. Try slower baud rate: 115200 or 460800
3. Press and hold RST button before upload, release when "Connecting..." appears
4. Check USB cable is data-capable (not charge-only)

### Issue: "Camera init failed"
**Solutions:**
1. Check camera module is properly seated
2. Check for bent pins
3. Try different power supply (should be 3.3V, 500mA+)
4. Ensure camera flex ribbon cable is fully inserted

### Issue: "MJPEG stream is choppy"
**Solutions:**
1. Reduce resolution: Change framesize to lower value
2. Reduce frame rate: Limit stream requests
3. Reduce JPEG quality: `&val=quality=10`
4. Use 5GHz WiFi if available
5. Move ESP32 closer to router

---

## 🎯 Multi-Camera Setup (Advanced)

### Architecture for Multiple ESP32-CAM Boards

```
                    WiFi Router
                        |
        ┌───────────────┼───────────────┐
        |               |               |
    ESP32-CAM      ESP32-CAM      ESP32-CAM
    (Front)        (Back)         (Side)
    192.168.1.100   192.168.1.101  192.168.1.102
        |               |               |
        └───────────────┼───────────────┘
                        |
                Raspberry Pi / PC
                (ASTROPATH Main)
```

### Configuration Example

```python
# config.py
ESP32_CAMERAS = {
    'front': {
        'host': '192.168.1.100',
        'port': 80,
        'mjpeg_path': '/stream',
        'location': 'North side street'
    },
    'back': {
        'host': '192.168.1.101',
        'port': 80,
        'mjpeg_path': '/stream',
        'location': 'South side street'
    },
    'side': {
        'host': '192.168.1.102',
        'port': 80,
        'mjpeg_path': '/stream',
        'location': 'Main intersection'
    }
}

# Usage
# In detect_edge.py:
from src.esp32_camera import MultiCameraController
import config

controller = MultiCameraController()
for name, cam_config in config.ESP32_CAMERAS.items():
    controller.add_camera(name, cam_config['host'], cam_config['port'])

# Then use:
frames = controller.get_all_frames()  # Get from all cameras
```

---

## 📊 Performance Metrics

### Typical Performance
- **Resolution**: 1024x768 pixels (configurable up to 2048x1536)
- **Frame Rate**: 15-30 FPS (depending on WiFi/stream)
- **Latency**: 100-500ms
- **Bandwidth**: 500KB-2MB per second (depends on quality)
- **Power Consumption**: 200-300mA @ 3.3V
- **Operating Temperature**: -10°C to +60°C

### Recommended Settings for Pothole Detection
```
Resolution: 1024x768 (good balance of quality/bandwidth)
Quality: 12 (good quality, reasonable bandwidth)
Brightness: Auto or 0
Contrast: 0
Saturation: 0 (or slightly lower for better detection)
```

---

## 🔗 Useful Resources

### ESP32-CAM Documentation
- [Official Espressif ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [Arduino-ESP32 GitHub](https://github.com/espressif/arduino-esp32)
- [CameraWebServer Example](https://github.com/espressif/arduino-esp32/blob/master/libraries/esp32/examples/Camera/CameraWebServer/CameraWebServer.ino)

### Related Projects
- [Smart IP Camera](https://github.com/easytarget/esp32-cam-webserver)
- [Motion Detection](https://github.com/jomjol/AI-on-the-edge-device)
- [Security Camera System](https://github.com/voiceye/esp32-camera-system)

### Community Support
- [ESP32 Forum](https://www.esp32.com/viewforum.php?f=19)
- [Arduino Forum](https://forum.arduino.cc/)
- [GitHub Issues](https://github.com/espressif/arduino-esp32/issues)

---

## ✅ Checklist

- [ ] ESP32-CAM board purchased and received
- [ ] USB-TTL converter obtained
- [ ] Arduino IDE installed
- [ ] Board support added in Arduino
- [ ] CameraWebServer firmware uploaded
- [ ] ESP32-CAM connected to WiFi
- [ ] Stream accessible in web browser
- [ ] Python environment set up
- [ ] esp32_camera.py module available
- [ ] Single camera test successful
- [ ] Integrated with detection pipeline
- [ ] Multi-camera setup (if needed)

---

**For questions or issues, refer to the main [README.md](README.md) or GitHub Issues.**
