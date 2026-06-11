# 🧠 ASTROPATH Main Controller (Master Node)

This script manages the "Brain" of the vehicle-mounted system. It is responsible for location tracking and coordinating with the **ESP32-CAM (Road Eye)**.

## 🚀 Key Functions
1.  **GPS Management**: Reads raw NMEA data from modules like NEO-6M.
2.  **Precision Parsing**: Uses `TinyGPS++` to calculate 6-decimal precision coordinates.
3.  **Synchronization**: Regularly sends current coordinates to the ESP32-CAM via Serial so all captured images are geotagged instantly.

## 📂 Folder Structure
- `astropath_master.ino`: Arduino sketch for the controller.

## 🛠️ Hardware Setup

### Recommended Boards
- **Arduino Mega 2560** (Best: Multiple Hardware Serials)
- **Arduino Uno** (Standard)
- **ESP32 / ESP8266** (Wireless Bridge)

### Wiring (Master to ESP32-CAM)
1.  **Master TX** -> **ESP32-CAM RX (GPIO 3)**
2.  **GND** -> **GND** (Common)

### Wiring (Master to GPS Module)
1.  **GPS TX** -> **Master pin 4** (SoftwareSerial RX)
2.  **GPS VCC** -> **3.3V/5V**
3.  **GPS GND** -> **GND**

## 📡 Protocol Details
The master sends the following packet every 1000ms:
`GPS:17.659921,75.906391\n`

This ensures that even if a pothole is detected at high speed, the ESP32-CAM has the most current location ready for the server upload.

---
*Part of the ASTROPATH Road Damage Detection System - 2026*
