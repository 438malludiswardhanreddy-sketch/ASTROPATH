# 📡 ASTROPATH ESP32-CAM "Road Eye" Node

This module acts as the **Detection Node** in the ASTROPATH system. It is designed to be mounted on a vehicle and used to capture real-time road surface data.

## 🚀 Key Features
- **Smart Trigger**: Captures images ONLY when damage is suspected (via vibration/ultrasonic sensor).
- **Hybrid AI**: Streams video to the main server for high-accuracy YOLO processing.
- **GPS Tagging**: Syncs with the main controller via Serial to tag every frame with location.
- **Low Power**: Optimized for battery operation on moving vehicles.

## 📂 Folder Structure
- `astropath_cam.ino`: Main firmware for the ESP32-CAM.
- `camera_index.h` (Coming soon): Advanced web UI for calibration.

## 🛠️ Setup Instructions

### 1. Hardware Connections
| ESP32-CAM Pin | Device / Component | Description |
|---------------|-------------------|-------------|
| **VCC (5V)**  | Power Supply      | Use a stable 5V 2A source |
| **GND**       | Power/GPS Ground  | Common Ground |
| **GPIO 3 (RX)**| GPS TX / Master TX| Receives Geotags & Trigger |
| **GPIO 1 (TX)**| Master RX (Optional)| Sends status feedback |
| **GPIO 4**    | On-board Flash    | Optional: Illuminates road |

---

## 🛰️ GPS & ESP32-CAM Wiring Guide

To enable geotagging for your road damage images, you need to connect the ESP32-CAM to a GPS source (either a standalone GPS module or a Master Controller).

### Option A: Standalone GPS Module (e.g., NEO-6M)
Direct connection for simple setups:
1. **GPS VCC** -> **ESP32-CAM 3.3V/5V**
2. **GPS GND** -> **ESP32-CAM GND**
3. **GPS TX**  -> **ESP32-CAM RX (GPIO 3)**
4. **GPS RX**  -> **ESP32-CAM TX (GPIO 1)** (Optional, for config)

> **⚠️ WARNING**: You MUST disconnect the GPS TX pin while uploading code to the ESP32-CAM, as they share the same Serial port.

### Option B: Master-Slave Setup (Arduino/ESP32 Master)
Recommended for vehicle-mounted systems:
1. **Master TX** -> **ESP32-CAM RX (GPIO 3)**
2. **Master GND** -> **ESP32-CAM GND**

**Master Controller Logic**:
- Sends `GPS:lat,lon\n` every second to sync location.
- Sends `CAPTURE\n` to force an immediate image upload when its own sensors (like Vibration/Ultrasonic) detect a pothole.

---

### 2. Firmware Configuration
Open `astropath_cam.ino` in Arduino IDE and update:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:5000/api/upload";
```

### 3. Uploading Code
1. Install **ESP32** board support in Arduino IDE.
2. Select Board: **AI Thinker ESP32-CAM**.
3. Use a **USB-to-TTL Serial Adapter**.
4. Short **IO0 to GND** before powering up to enter Bootloader mode.
5. Click **Upload**.

## 🛰️ GPS Synchronization & Serial Protocol

If your vehicle has a main controller (like an Arduino Mega or another ESP32) with a GPS module, you can feed location data to the ESP32-CAM via Serial.

### Wiring
- **Main Controller TX** -> **ESP32-CAM RX (GPIO 3 / U0RXD)**
- **GND** -> **GND** (Common ground is mandatory)

### Protocol
The ESP32-CAM listens for strings in the following format:
`GPS:latitude,longitude\n`

**Example:**
`GPS:17.659921,75.906391`

When the ESP32-CAM receives this, it stores the location and automatically attaches it to any pothole detection it sends to the server.

---

## 📊 Project Role
According to the **ASTROPATH Architecture**:
1. **Sensing**: ESP32-CAM sees the road.
2. **Detection**: Sends suspicious frames to the Python Server.
3. **Evidence**: Provides visual proof stored in the `detections/` database.
4. **Wireless**: Transmits via WiFi to the central Hub.

---
*Part of the ASTROPATH Road Damage Detection System - 2026*
