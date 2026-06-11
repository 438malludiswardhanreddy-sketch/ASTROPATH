# ASTROPATH Edge Hardware & Drone Integration Guide

This document details the configuration and integration steps for the edge optical cameras, serial GPS modules, and autonomous flight controller telemetry radio busses.

---

## 🔧 Edge & Hardware Configuration

### 1. ESP32-CAM Setup
The ESP32-CAM serves as a low-cost, edge-deployed camera unit.
1. Navigate to `hardware/esp32_cam/` and upload the provided sketch to your ESP32 board using the Arduino IDE.
2. Once connected to your local Wi-Fi network, the ESP32 serial console will output its local streaming IP (e.g., `http://192.168.1.55:81/stream`).
3. Open `config.py` and modify the following value:
   ```python
   CAMERA_SOURCE = "http://192.168.1.55:81/stream"
   ```

### 2. GPS NEO-6M Integration
To mount a serial GPS receiver on a ground patrol vehicle or simulated vehicle bus:
1. Connect the GPS module's TX/RX pins to your PC using a USB-to-TTL converter.
2. Update `config.py` to enable the serial reader:
   ```python
   GPS_ENABLED = True
   GPS_PORT = "COM3"  # On Linux, use "/dev/ttyUSB0"
   ```
3. Run diagnostics: `python tests/test_gps.py` to confirm NMEA coordinates are parsing correctly.

---

## 🚁 Drone & Mission Controller Integration

ASTROPATH interfaces with flight controllers running PX4 or ArduPilot firmware to orchestrate autonomous flight profiles.

### Telemetry Connection
The system connects to physical or simulated flight systems using MAVLink over serial or UDP connections:

```python
# config.py
DRONE_ENABLED = True
DRONE_CONNECTION_STRING = "127.0.0.1:14550"  # Local SITL or telemetry radio
DRONE_STREAM_URL = "rtsp://192.168.1.100:8554/live"
```

To run a simulated mission alongside the telemetry pipeline:
1. Run your ArduPilot SITL simulator.
2. Test the telemetric stream parser:
   ```bash
   python tests/test_drone_stream.py
   ```
3. Run the aerial surveyor:
   ```bash
   python src/detection/drone_detector.py
   ```

*For step-by-step guidance on setting up flight simulators, read [DRONE_GUIDE.md](docs/DRONE_GUIDE.md).*
