# ASTROPATH: Real-Time Edge-Assisted Sensor Fusion and Autonomous Drone Navigation for Road Damage Diagnostics

**Author & Owner:** Mallu Diswardhan Reddy  
**Date:** June 2026  
**Document Reference:** docs/Project_Report.md  

---

## 1. Abstract
Urban road infrastructure maintenance remains a significant challenge for municipality corporations in developing economies. Conventional manual inspection techniques are slow, error-prone, and hazardous. This report presents **ASTROPATH**, an end-to-end, edge-assisted, autonomous aerial system designed to automate road damage diagnostics. Incorporating a custom 3D Kalman Filter for sensor fusion, a dual-stage neural network framework (YOLOv4-tiny and MobileNetV2) for edge-based classification, and a dynamic safety-priority route optimisation engine, ASTROPATH provides continuous pothole mapping and rapid response coordination. The system runs real-time perception pipelines on Raspberry Pi and ESP32-CAM hardware interfaces, syncing telemetry data with a centralised municipal dashboard to streamline public work repairs.

---

## 2. Objective
The primary objectives of the ASTROPATH system are:
1. **Autonomous Damage Detection:** Automating the identification and severity analysis of potholes and road cracks using high-speed edge devices.
2. **Reliable Geolocation Mapping:** Projecting pixel-level computer vision detections into precise real-world GPS coordinates using drone altitude, attitude (gimbal pitch/roll), and telemetry.
3. **Multi-Sensor State Estimation:** Filtering noisy GPS, IMU, and barometric altimeter data through a custom 3D Kalman Filter to ensure stable flight path tracing.
4. **Dynamic Path Planning and Safety Overrides:** Implementing collision avoidance algorithms (for birds, trees, and low-hanging wires) and autonomous safety triggers (Return-to-Home and Emergency Landing) during adverse wind, rain, or low battery conditions.
5. **Decentralised Citizen Reporting:** Integrating public citizen upload pipelines to verify and complement aerial survey maps.

---

## 3. Methodology

### 3.1. System Architecture
ASTROPATH is divided into three key architectural layers:
1. **Perception Layer (Edge Device):** Executes object detection and classification. It processes video frames from onboard camera streams (via RTSP or local WiFi interfaces like ESP32-CAM) and estimates the severity of detected hazards.
2. **Navigation and Fusion Layer (Flight Controller):** Acquires spatial coordinates from the GPS module and IMU. A 3D Kalman Filter fuses these streams to produce high-accuracy state estimations.
3. **Orchestration Layer (Cloud/Municipal Server):** Exposes RESTful API endpoints for telemetry logs and citizen uploads, maintaining a centralised SQLite database and dynamic Flask dashboard for visualising pothole maps.

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
        │                      │                      │
        ▼                      ▼                      ▼
  ┌───────────┐          ┌───────────┐          ┌───────────┐
  │  Sensors  │          │  Camera   │          │  Battery  │
  │ (GPS/IMU) │          │ (ESP32)   │          │  & Wind   │
  └─────┬─────┘          └─────┬─────┘          └─────┬─────┘
        │                      │                      │
        ▼                      ▼                      ▼
  ┌───────────┐          ┌───────────┐          ┌───────────┐
  │  Sensor   │          │  Object   │          │  Safety   │
  │  Fusion   │          │ Detection │          │ Decision  │
  │ (Kalman)  │          │  (YOLO)   │          │  Engine   │
  └─────┬─────┘          └─────┬─────┘          └─────┬─────┘
        │                      │                      │
        └──────────────┬───────┴──────────────────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   Path Planning     │
            │  (Dynamic Detour)   │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │  Drone Controller   │
            │ (Emergency Landing) │
            └─────────────────────┘
```

### 3.2. Sensor Fusion (3D Kalman Filter)
Drone navigation modules rely on sensor fusion to counteract high Gaussian noise in raw GPS signals (~5m variance) and altimeter sensors (~30cm variance). The state vector is defined as:
$$\mathbf{x} = \begin{bmatrix} lat \\ lon \\ alt \end{bmatrix}$$

The prediction and correction loops update the covariance matrix $P$ against process noise $Q$ and measurement noise covariance $R$:
1. **Predict State:**
   $$P_{k|k-1} = P_{k-1|k-1} + Q$$
2. **Correct State (GPS & Altimeter Ingestion):**
   $$K = P_{k|k-1} (P_{k|k-1} + R)^{-1}$$
   $$\mathbf{x}_k = \mathbf{x}_{k|k-1} + K (\mathbf{z}_k - \mathbf{x}_{k|k-1})$$
   $$P_{k|k} = (I - K) P_{k|k-1}$$

### 3.3. Computer Vision Perception Layer
- **YOLOv4-tiny Model:** Used to scan video frames at 30 FPS. It localises candidates for road anomalies (specifically bounding box coordinates).
- **MobileNetV2 Binary Classifier:** Acts as a secondary verification stage. It runs deep feature extraction on cropped bounding box images to confirm if they represent potholes or false positives (like shadows or dry leaves).
- **Severity Estimation:** Calculated based on the ratio of bounding box area to overall frame size. Low, Medium, and High classifications dictate the urgency level logged in the database.

### 3.4. Path Planning & Safety Control Logic
The flight orchestration system monitors battery discharge rates, wind velocity gusts, and precipitation levels:
- **Low Battery Override:** Triggered if charge drops below $15\%$. Forces an immediate emergency vertical descent.
- **Wind Override:** Triggered if wind speed exceeds $25\text{ knots}$. Reduces speed to $1.5\text{ m/s}$ and activates stabilisation controls.
- **Precipitation Override:** Triggered if rain exceeds $15\text{ mm/h}$. Restricts speed to prevent camera lens occlusion and electronic damage.
- **Collision Detours:** Initiates horizontal bypasses ($+4\text{m}$ offset) for static trees, vertical bypasses ($+6\text{m}$ altitude climb) for power lines/wires, and hover-in-place waits for transient bird flocks.

---

## 4. Run-Time Results (Simulation Verification)
The system was validated using a high-fidelity end-to-end mission simulator, tracing a path across Solapur, Maharashtra, India (coordinates starting at `17.6599, 75.9064`). Below is the step-by-step diagnostic log representing the automated state responses:

### 4.1. Phase 1: Takeoff & Initial State Estimation
At launch, the flight controller commands takeoff. The 3D Kalman Filter stabilises initial GPS signal variance:
*   **Sensor Fusion Output:** Lat: `17.659900` | Lon: `75.906418` | Alt: `8.02m`
*   **Safety Status:** Clear flight corridor, battery status at $95.5\%$.

### 4.2. Phase 2: Dynamic Obstacle Avoidance (Bypasses)
- **Step 3 (Tree Hazard):** AI vision detects a tree branch blocking the trajectory.
  - *Threat Assessment:* Collision Danger Score: `0.70`.
  - *Detour Executed:* Lateral bypass (+4m North-East deviation applied).
- **Step 5 (Wire Hazard):** AI vision detects a low-hanging electrical power line.
  - *Threat Assessment:* Collision Danger Score: `0.80`.
  - *Detour Executed:* Vertical bypass (+6m climb profile command).
- **Step 7 (Bird Hazard):** AI vision detects a flock of birds crossing the flight vector.
  - *Threat Assessment:* Collision Danger Score: `0.55`.
  - *Detour Executed:* Hover-in-place state activated (pause forward heading).

### 4.3. Phase 3: Environmental Safety Overrides
- **Step 6 (Wind Gust):** Wind speed rises to `28.5 knots`.
  - *Action:* Auto-stabilisation activated. Flight speed throttled to `1.5 m/s`.
- **Step 8 (Precipitation):** Heavy rain registered at `18.0 mm/h`.
  - *Action:* Warning flagged by Safety Decision Engine.
- **Step 9 (Critical Battery):** Onboard battery capacity drains to `12.0%` (below the $15.0\%$ limit).
  - *Action:* Critical Low Battery RTH override triggered.
  - *Landing Spot Calculation:* Safe Landing Zone established at `17.663944, 75.909374`.
  - *Final Status:* Vertically descended to $0.0\text{m}$. Flight operations halted safely.

---

## 5. Future Scope
1. **Real-time Edge TPU Integration:** Deploying compiled Google Coral Edge TPU models to accelerate MobileNetV2 inference latency to under $5\text{ ms}$.
2. **Autonomous Swarm Mapping:** Coordinating multiple edge-enabled micro-UAVs to divide large municipal sectors for rapid grid mapping.
3. **Advanced Depth/Thermal Vision:** Integrating stereo cameras to estimate pothole depth and volume directly from flight, allowing accurate material estimation for public repair teams.
4. **5G Telemetry Streams:** Incorporating high-bandwidth 5G transceivers to stream raw visual feeds back to control centres when GPU offloading is necessary.

---
*End of Report.*
