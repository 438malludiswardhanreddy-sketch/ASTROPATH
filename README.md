# 🚀 ASTROPATH: Automated Smart Technology for Road Observation, Planning, Analysis, Tracking & Healing

ASTROPATH is an end-to-end autonomous AI and IoT ecosystem designed to automate the lifecycle of urban road damage detection, severity classification, and rapid maintenance reporting. By fusing **Autonomous Aerial Drones (PX4/ArduPilot)**, **Edge AI Devices (ESP32-CAM/Raspberry Pi)**, and **Mobile Citizen Portals**, ASTROPATH builds a real-time, high-accuracy digital twin of municipal road infrastructure.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]()
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green.svg)]()
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)](https://astropath-0yd4.onrender.com)

---

## 📌 Table of Contents
1. [🌟 Interface & System Showcase](#-interface--system-showcase)
2. [💡 The Project Vision](#-the-project-vision)
3. [🏗️ System Architecture](#%EF%B8%8F-system-architecture)
4. [🛰️ Functional Layer Breakdown](#%EF%B8%8F-functional-layer-breakdown)
5. [💻 Tech Stack](#-tech-stack)
6. [🚀 Quick Start (30 Seconds!)](#-quick-start-30-seconds)
7. [📂 Codebase Structure](#-codebase-structure)
8. [🔧 Edge & Hardware Configuration](#-edge--hardware-configuration)
9. [🚁 Drone & Mission Controller Integration](#-drone--mission-controller-integration)
10. [🤖 Autonomous Flight & Safety Simulation Engine](#-autonomous-flight--safety-simulation-engine)
11. [📊 RESTful API Specifications](#-restful-api-specifications)
12. [🤝 Contribution & Code Standards](#-contribution--code-standards)
13. [👥 Team & Contact](#-team--contact)
14. [📄 License](#-license)

---

## 🌟 Interface & System Showcase

### 📊 High-Tech Real-Time Dashboard
A centralized control room interface providing real-time AI computer vision feeds, Leaflet.js interactive maps for spatial analysis, automatic hotspot heatmaps, and repair order tracking.

![ASTROPATH Web Dashboard](assets/dashboard_mockup.png)

### 🚁 Autonomous Drone HUD & Edge Perception
A representation of the drone's aerial telemetry overlay and computer vision engine dynamically scanning for potholes, calculating real-world GPS coordinates, and reporting severity values.

![ASTROPATH Aerial HUD](assets/drone_vision_mockup.png)

### 🛠️ Working Hardware Prototype
The custom ESP32-CAM optical sensor payload, red NEO-6M GPS receiver module, and core telemetry bus integrated onto a simulated quadcopter platform.

![ASTROPATH Hardware Prototype](assets/hardware_prototype.png)

---

## 💡 The Project Vision

### ⚠️ The Problem
Traditional road maintenance relies on reactive citizen complaints or manual vehicle patrols. These methods suffer from:
*   **Fatal Safety Hazards:** Undetected potholes cause severe accidents, pedestrian injuries, and millions in vehicle damage daily.
*   **Escalating Infrastructure Costs:** Postponing repairs increases costs exponentially; a minor crack left unmanaged grows 10x in cost and repair complexity.
*   **Disruptive Traffic Congestion:** Repair schedules are rarely predictive, leading to unplanned road closures during peak commuting hours.

### 💡 The Solution: ASTROPATH
ASTROPATH automates the observation and management cycle by integrating multi-source inputs:
1.  **Autonomous Aerial Patrols:** Drones cover wide areas 20x faster than ground crews, streaming feeds and telemetric data.
2.  **Edge-AI Ground Ingestion:** Low-power edge processors (ESP32-CAM) mounted on municipal transit vehicles scan roads dynamically.
3.  **Crowdsourced Reports:** Citizen web applications allow residents to log geolocated pothole reports directly.

---

## 🏗️ System Architecture

### 1. Functional System Flow
The logical pipeline of ASTROPATH flows from destination planning and drone execution down to threat classification, safety oversight, and mission execution:

```
                    ┌─────────────────────┐
                    │   Mission Planner   │
                    │ (Destination Input) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Flight Controller  │
                    │ (PX4/ArduPilot)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼

┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│ GPS Module   │     │ IMU Sensors    │     │ Altimeter    │
│ Location     │     │ Orientation    │     │ Height Data  │
└──────┬───────┘     └──────┬─────────┘     └──────┬───────┘
       │                    │                      │
       └────────────┬───────┴──────────────┬───────┘
                    ▼                      ▼

            ┌──────────────────────────────┐
            │    Sensor Fusion Engine      │
            │  (Kalman Filter / AI Model)  │
            └──────────────┬───────────────┘
                           │
                           ▼

            ┌──────────────────────────────┐
            │ Environment Perception Layer │
            └──────────────┬───────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Bird Detect  │   │ Wire Detect  │   │ Tree Detect  │
│ AI Vision    │   │ AI Vision    │   │ AI Vision    │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  ▼                  ▼

         ┌───────────────────────────┐
         │ Obstacle Classification   │
         │ & Threat Assessment       │
         └─────────────┬─────────────┘
                       │
                       ▼

         ┌───────────────────────────┐
         │ Dynamic Path Planning AI  │
         │ (ASTROPATH Core Engine)   │
         └─────────────┬─────────────┘
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Route       │ │ Re-routing  │ │ Emergency   │
│ Optimization│ │ Engine      │ │ Landing AI  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼

         ┌───────────────────────────┐
         │ Battery & Weather Monitor │
         └─────────────┬─────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼

   Low Battery      Heavy Rain     High Wind
         │             │             │
         └─────────────┼─────────────┘
                       ▼

         ┌───────────────────────────┐
         │ Safety Decision Engine    │
         └─────────────┬─────────────┘
                       │
                       ▼

         ┌───────────────────────────┐
         │ Autonomous Flight Control │
         └─────────────┬─────────────┘
                       │
                       ▼

         ┌───────────────────────────┐
         │ Delivery / Mission Target │
         └───────────────────────────┘
```

### 2. Physical Deployment Architecture
This diagram outlines how data is ingested, processed, stored, and visualised:

![ASTROPATH Physical Architecture](assets/astropath_architecture.png)

### 3. Pipeline Flow Chart (Mermaid)
```mermaid
graph TD
    A[Data Sources] --> B{Detection Engine}
    A1[Drone Fleet - 4K Video] --> A
    A2[Citizen App - Mobile Camera] --> A
    A3[Ground Patrol - USB/Webcam] --> A
    A4[Edge Connect - ESP32-CAM] --> A
    
    B --> C[AI Processing Layer]
    C1[YOLOv4-tiny Detection] --> B
    C2[MobileNet Classification] --> B
    C3[GPS Projection - Drone Telemetry] --> B
    
    B --> D[(SQLite Ground DB)]
    D --> E[Real-Time Dashboard]
    E --> F[Heatmap Visualization]
    E --> G[Repair Status Management]
```

---

## 🛰️ Functional Layer Breakdown

### 1. Ingestion Layer
*   **Edge Connect (ESP32-CAM):** Operates on standard Wi-Fi micro-networks to stream frame payloads over HTTP/MJPEG protocols.
*   **Web Portal Uploads:** Citizens snap photos on their mobile devices; modern geolocation APIs query local device GPS and attach high-accuracy coordinates to the report.
*   **Aerial RTSP Streams:** Receives real-time video feeds from drone cameras via RTSP or UDP connections.

### 2. Computer Vision & Perception Layer
*   **YOLOv4-Tiny Model:** Analyzes 20-30 frames per second on typical hardware, outputting precise bounding boxes enclosing road defects.
*   **MobileNetV2 Classifier:** Validates detections, filters out false positives, and estimates pothole volume to determine repair priority (Low, Medium, High).
*   **Spatial Telemetry Projection:** Translates drone elevation, tilt, and gimbal angle into exact ground coordinates for potholes.

### 3. Safety Decision Engine
*   **Autonomous Safety Routing:** The flight manager continuously monitors atmospheric conditions (high winds, heavy rain) and battery status.
*   **Emergency Return-to-Home (RTH):** Automatically takes over flight operations to trigger safe emergency landings if thresholds are breached, preventing hardware losses.

---

## 💻 Tech Stack

*   **Backend Application:** Python 3.8+, Flask Framework, Waitress (WSGI server for production)
*   **Frontend UI:** HTML5, CSS3 (Modern Dark-Mode Grid/Flexbox Layout), Vanilla JavaScript
*   **Mapping & Spatial Analytics:** Leaflet.js, Leaflet.heat (Heatmap tracking)
*   **Computer Vision Frameworks:** OpenCV (cv2), Darknet YOLOv4-tiny, TensorFlow Lite / Keras (MobileNetV2 classification)
*   **Telemetry & Autonomous Flight:** Pymavlink, DroneKit API (for ArduPilot/PX4 simulated or physical communication)
*   **Storage & Database:** SQLite3 database engine
*   **Deployment Configuration:** Docker, Docker Compose, Render blueprints

---

## 🚀 Quick Start (30 Seconds!)

### Windows
```powershell
.\start.ps1
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

**Accessing the Dashboard:**
*   Local Web Portal: [http://localhost:5000](http://localhost:5000)
*   Municipal Dashboard: [http://localhost:5000/dashboard](http://localhost:5000/dashboard)

---

## 📂 Codebase Structure

```
ASTROPATH/
├── assets/                 # High-fidelity project screenshots and diagrams
├── src/                    # Source files implementing application modules
│   ├── detect_edge.py      # Core OpenCV/YOLO edge processing pipelines
│   ├── drone_detector.py   # Telemetry parsing & aerial video processing
│   ├── drone_controller.py # Drone MAVLink commands & flight control wrapper
│   ├── gps_handler.py      # Serial/USB GPS parsing (NMEA decoding)
│   ├── database.py         # SQLite connection, migration, & query layer
│   ├── citizen_upload.py   # Citizen report ingestion & image compression
│   └── esp32_camera.py     # Network stream fetcher for ESP32-CAM edge boards
├── templates/              # HTML layout components
│   ├── index.html          # Main live feed & reporting interface
│   └── dashboard.html      # Leaflet map visualization dashboard
├── static/                 # Static front-end assets
│   ├── css/style.css       # Premium, responsive dark-mode stylesheet
│   └── js/                 # Client-side map & websocket controller logic
├── models/                 # Neural network config & weights files
│   ├── yolov4-tiny.cfg     # YOLOv4-tiny layer definition
│   └── obj.names           # Class labels (e.g., pothole)
├── app.py                  # Main web application entry point
├── main.py                 # CLI interface menu for diagnostic scripts
├── config.py               # Centralized configuration parameters
├── requirements.txt        # Python dependency manifest
├── Dockerfile              # Docker container configuration
└── docker-compose.yml      # Multi-container service definitions
```

---

## 🔧 Edge & Hardware Configuration

### 1. ESP32-CAM Setup
The ESP32-CAM serves as a low-cost, edge-deployed camera unit.
1.  Navigate to `hardware/esp32_cam/` and upload the provided sketch to your ESP32 board using the Arduino IDE.
2.  Once connected to your local Wi-Fi network, the ESP32 serial console will output its local streaming IP (e.g., `http://192.168.1.55:81/stream`).
3.  Open `config.py` and modify the following value:
    ```python
    CAMERA_SOURCE = "http://192.168.1.55:81/stream"
    ```

### 2. GPS NEO-6M Integration
To mount a serial GPS receiver on a ground patrol vehicle:
1.  Connect the GPS module's TX/RX pins to your PC using a USB-to-TTL converter.
2.  Update `config.py` to enable the serial reader:
    ```python
    GPS_ENABLED = True
    GPS_PORT = "COM3"  # On Linux, use "/dev/ttyUSB0"
    ```
3.  Run diagnostics: `python test_gps.py` to confirm NMEA coordinates are parsing correctly.

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
   python test_drone_stream.py
   ```
3. Run the aerial surveyor:
   ```bash
   python src/drone_detector.py
   ```

*For step-by-step guidance on setting up flight simulators, read [DRONE_GUIDE.md](DRONE_GUIDE.md).*

---

## 🤖 Autonomous Flight & Safety Simulation Engine

To test the end-to-end logical flow of the ASTROPATH architecture, the repository contains a standalone physical and environmental flight simulation engine at [autonomous_flight_system.py](file:///C:/Users/mallu/OneDrive/Documents/Desktop/pothole/ASTROPATH-1/src/autonomous_flight_system.py).

This simulator models the flight cycle through 10 chronological steps, dynamically injecting real-world obstacles and sensor anomalies:
1. **Takeoff & Altitude Hold:** Simulates GPS, Altimeter, and IMU sensor data.
2. **Sensor Fusion:** Fuses noisy telemetry measurements using a **Kalman Filter** state estimator.
3. **AI Vision Perception:** Scans roads for potholes and detects tree branches, hanging electrical wires, and birds in front of the drone.
4. **Threat Assessment:** Evaluates spatial distance and collision danger scores.
5. **Re-routing Engine:** Generates detours (e.g., lateral bypass for trees, climb profile for wires, hover-in-place for birds).
6. **Battery & Weather Monitor:** Dynamically injects heavy wind gusts, severe downpours, and drains battery capacity.
7. **Safety Decision Engine:** Overrides standard flight paths to trigger RTH and safe emergency landing procedures if safety limits are breached.

### How to Run the Simulator
```bash
python src/autonomous_flight_system.py
```

### Complete Simulation Output Logs
```text
[22:36:56] [INFO] [ASTROPATH_Core] Mission Planner initialized. Start: (17.6599, 75.9064) | Target: (17.6682, 75.9125)
[22:36:56] [INFO] [ASTROPATH_Core] =========================================================
[22:36:56] [INFO] [ASTROPATH_Core] 🚀 ASTROPATH AUTONOMIC FLIGHT MISSION STARTING
[22:36:56] [INFO] [ASTROPATH_Core] =========================================================
[22:36:56] [INFO] [ASTROPATH_Core] Generated 10 mission waypoints successfully.

--- [MISSION FLIGHT STEP 1/10] Mode: TAKEOFF ---
Monitor Stats - Battery: 95.5% | Wind: 12.0 kts | Rain: 0.0 mm/h
Flight Controller: Takeoff complete. Holding altitude 15.0m.
Sensor Fusion State: Lat: 17.659967 | Lon: 75.906418 | Alt: 8.11m
AI Vision Layer: Scan clear. No environmental obstacles.

--- [MISSION FLIGHT STEP 2/10] Mode: CRUISE ---
Monitor Stats - Battery: 91.0% | Wind: 12.0 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.660322 | Lon: 75.906709 | Alt: 10.85m
AI Vision Layer: Scan clear. No environmental obstacles.

--- [MISSION FLIGHT STEP 3/10] Mode: CRUISE ---
Monitor Stats - Battery: 86.5% | Wind: 12.0 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.660724 | Lon: 75.907044 | Alt: 12.23m
AI Vision Layer: Detected 1 objects.
  └─ Label: Tree | Confidence: 94.0% | Spatial Offset: (x: 1.2m, y: 5.0m)
[WARNING] Threat Assessment: Collision Risk Alert! Danger Score: 0.70 [Tree]
🔄 Re-routing Engine activated due to: Tree obstacle.
Detour Action: Lateral bypass (+4m North-East deviation).
Autopilot Command: Adjusting heading/speed vectors to detours.

--- [MISSION FLIGHT STEP 4/10] Mode: CRUISE ---
Monitor Stats - Battery: 82.0% | Wind: 12.0 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.661174 | Lon: 75.907402 | Alt: 13.12m
AI Vision Layer: Detected 1 objects.
  └─ Label: Pothole | Confidence: 96.0% | Spatial Offset: (x: 0.068m, y: 3.984m)

--- [MISSION FLIGHT STEP 5/10] Mode: CRUISE ---
Monitor Stats - Battery: 77.5% | Wind: 12.0 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.661662 | Lon: 75.907758 | Alt: 13.72m
AI Vision Layer: Detected 1 objects.
  └─ Label: Wire | Confidence: 89.0% | Spatial Offset: (x: 0.1m, y: 3.5m)
[WARNING] Threat Assessment: Collision Risk Alert! Danger Score: 0.80 [Wire]
🔄 Re-routing Engine activated due to: Wire obstacle.
Detour Action: Vertical bypass (+6m climb profile).
Autopilot Command: Adjusting heading/speed vectors to detours.

--- [MISSION FLIGHT STEP 6/10] Mode: CRUISE ---
[WARNING] 💨 Wind speed sensor reporting high gust: 28.5 knots!
Monitor Stats - Battery: 73.0% | Wind: 28.5 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.662179 | Lon: 75.908141 | Alt: 15.88m
AI Vision Layer: Detected 1 objects.
  └─ Label: Pothole | Confidence: 96.0% | Spatial Offset: (x: 1.969m, y: 2.295m)
[CRITICAL] ⚠️ SAFETY INTERVENTION: High wind velocity limit exceeded!
Safety Decision Engine Override: Activating Auto-Stabilization. Reducing velocity to 1.5m/s.

--- [MISSION FLIGHT STEP 7/10] Mode: CRUISE ---
Monitor Stats - Battery: 68.5% | Wind: 28.5 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.662725 | Lon: 75.908525 | Alt: 17.35m
AI Vision Layer: Detected 1 objects.
  └─ Label: Bird | Confidence: 91.0% | Spatial Offset: (x: -2.5m, y: 6.0m)
[WARNING] Threat Assessment: Collision Risk Alert! Danger Score: 0.55 [Bird]
🔄 Re-routing Engine activated due to: Bird obstacle.
Detour Action: Hover-in-place state activated (wait for clearing).
Autopilot Command: Adjusting heading/speed vectors to detours.
[CRITICAL] ⚠️ SAFETY INTERVENTION: High wind velocity limit exceeded!
Safety Decision Engine Override: Activating Auto-Stabilization. Reducing velocity to 1.5m/s.

--- [MISSION FLIGHT STEP 8/10] Mode: CRUISE ---
[WARNING] 🌧️ Rain rate sensor reporting heavy downpour: 18.0 mm/h!
Monitor Stats - Battery: 64.0% | Wind: 12.0 kts | Rain: 18.0 mm/h
Sensor Fusion State: Lat: 17.663282 | Lon: 75.908951 | Alt: 16.74m
AI Vision Layer: Detected 1 objects.
  └─ Label: Pothole | Confidence: 96.0% | Spatial Offset: (x: -2.912m, y: 4.445m)
[CRITICAL] ⚠️ SAFETY INTERVENTION: Extreme precipitation detected!

--- [MISSION FLIGHT STEP 9/10] Mode: CRUISE ---
[WARNING] 🔋 Battery capacity dropped to critical levels: 12.0%!
Monitor Stats - Battery: 12.0% | Wind: 12.0 kts | Rain: 0.0 mm/h
Sensor Fusion State: Lat: 17.663888 | Lon: 75.909387 | Alt: 16.37m
AI Vision Layer: Detected 1 objects.
  └─ Label: Pothole | Confidence: 96.0% | Spatial Offset: (x: 1.137m, y: 3.317m)
[CRITICAL] ⚠️ SAFETY INTERVENTION: Critical Low Battery!
🚨 Emergency Landing AI locating nearest safe landing zone (LZ)...
Safe LZ calculated at: (17.663908, 75.909367). Beginning vertical descent.
[CRITICAL] Autopilot Override: Safety Decision Engine taking command. Navigating to Safe LZ.
🛑 Safety Override Landing Completed. System safe. Flight operations halted.

=========================================================
⚠️ MISSION ENDED VIA EMERGENCY SAFE LANDING OVERRIDE
=========================================================
```

---

## 📊 RESTful API Specifications

| Method | Endpoint | Description | Sample Response Payload |
|:---|:---|:---|:---|
| **GET** | `/health` | Ingestion layer health check | `{"status": "healthy", "gpu_available": false}` |
| **GET** | `/api/detections` | Retrieve registered road defects | `[{"id": 12, "latitude": 17.65, "severity": "High"}]` |
| **GET** | `/api/stats` | Aggregated telemetry & count statistics | `{"total_potholes": 84, "high_severity": 19}` |
| **POST**| `/api/upload` | Upload citizen-submitted road defect | `{"status": "success", "detection_id": 232}` |

### Sample Citizen Reporting Request
```python
import requests

url = "http://localhost:5000/api/upload"
payload = {
    "latitude": "17.6682",
    "longitude": "75.9015",
    "severity": "High"
}
files = {
    "image": ("defect.jpg", open("defect.jpg", "rb"), "image/jpeg")
}

response = requests.post(url, data=payload, files=files)
print(response.json())
```

---

## 🤝 Contribution & Code Standards

We welcome contributions from researchers, smart-city engineers, and students!
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Ensure your code conforms to PEP-8 guidelines.
4.  Commit your modifications (`git commit -m 'Add AmazingFeature'`).
5.  Push your branch (`git push origin feature/AmazingFeature`) and open a Pull Request.

---

## 👥 Team & Contact

*   **Lead Developer:** Mallu Diswardhan Reddy  
*   **Email:** [438malludiswardhanreddy@gmail.com](mailto:438malludiswardhanreddy@gmail.com)  
*   **Organization:** Solapur Municipal Corporation (Smart City Initiative)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Designed to make urban infrastructure safer, smarter, and more resilient. 🚗 📱 🚁**
