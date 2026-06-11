# Mallu Diswardhan Reddy

### 🚁 AI • Computer Vision • Drones • Sensor Fusion • Embedded Systems

I am an ECE Systems Engineer & Robotics Developer exploring the boundary between embedded edge hardware and advanced autonomic intelligence. I design high-reliability algorithms for spatial localization, multi-sensor fusion state estimation, and vision-guided flight controllers.

---

## 🌟 Flagship Project: ASTROPATH

### Sky-View Autonomous Drone Navigation and Road Damage Detection System

**ASTROPATH** is an end-to-end autonomous aerial monitoring platform that integrates UAV flight guidance (MAVLink/PX4), 3D sensor fusion, and computer vision to automate urban road infrastructure diagnostics.

*   **GitHub Repository:** [github.com/438malludiswardhanreddy-sketch/ASTROPATH](https://github.com/438malludiswardhanreddy-sketch/ASTROPATH)
*   **Live Simulation Dashboard:** [astropath-0yd4.onrender.com](https://astropath-0yd4.onrender.com)
*   **Research Paper (PDF):** [docs/ASTROPATH_Research_Paper.pdf](https://github.com/438malludiswardhanreddy-sketch/ASTROPATH/blob/main/docs/ASTROPATH_Research_Paper.pdf)
*   **IPO Patent Specification Draft:** [research/patent_draft.md](https://github.com/438malludiswardhanreddy-sketch/ASTROPATH/blob/main/research/patent_draft.md)

### Key Technical Core
*   **3D Kalman Filter State Estimator:** Fuses noisy GPS measurements (~5m error) and barometric altimeter feeds (~30cm variance) to yield stabilized spatial coordinate trajectories.
*   **Edge AI Vision (YOLOv4-tiny + MobileNetV2):** Performs 30 FPS bounding-box localization of pavement damage, followed by binary classification to reject shadow/leaf false positives and score damage severity.
*   **Autonomic Path Routing AI:** Dynamically commands vertical bypasses (+6m climb) for power lines/wires, lateral bypasses (+4m East offset) for tree branch blockages, and hover waits for bird flight vectors.
*   **Fail-Safe Override Logic:** Automatically intercepts manual flight controls to command Return-To-Home (RTH) on critical batteries (<15%), wind gusts (>25 kts), or precipitation (>15 mm/h).

---

## 🛠️ Tech Stack & Skills
*   **Core Languages:** Python, C++, C, JavaScript, HTML/CSS
*   **Robotics & Systems:** PX4/ArduPilot SITL, MAVLink, pymavlink, ESP32-CAM, NEO-6M GPS serial interfaces, Sensor Fusion (Kalman Filtering)
*   **AI & Perception:** OpenCV, YOLO (Darknet), TensorFlow Lite, Keras, scikit-learn
*   **APIs & Server:** Flask, RESTful architecture, SQLite, Docker, Waitress (WSGI)

---
*Developed as part of my professional systems engineering research portfolio. Let's build safer, more resilient smart cities.*
