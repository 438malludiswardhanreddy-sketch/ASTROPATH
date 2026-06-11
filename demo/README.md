# ASTROPATH Demonstration and Video Stream Configuration Guide

This directory holds the assets, configuration files, and running instructions for executing the ASTROPATH live flight simulation and video analysis demonstration.

---

## 1. Overview of the Demonstration
The ASTROPATH demo showcases:
1.  **3D Kalman Filter Sensor Fusion:** Visualised through flight telemetry outputs.
2.  **Edge Perception:** Live video frames processed for road damage and classified by severity.
3.  **Autonomous Re-routing detours:** Active flight overrides to bypass dynamic hazards (birds, trees, power lines).
4.  **Weather and Battery Safety Overrides:** Triggering emergency landing procedures under extreme crosswinds, rainfall, or low battery status.

---

## 2. Running the Live Flight Simulation
To execute the live 3D sensor fusion flight simulation and see the safety priority overrides in action:
```bash
python src/navigation/autonomous_flight_system.py
```
This runs the modularized flight system end-to-end, printing real-time diagnostic telemetry, threat evaluations, and detour plan logs directly to the terminal.

---

## 3. Launching the Web Interface Dashboard
To start the real-time web dashboard and municipal portal, run:
```bash
python main.py
```
Choose **Option 3** from the interactive menu or run the Flask application directly:
```bash
python app.py
```
Open your web browser and navigate to `http://localhost:5000` to view:
*   Real-time pothole geolocalisation markers on the map.
*   System telemetry status logs.
*   Live video feed streams with overlaid bounding box and severity estimations.

---

## 4. Testing Video Streams (RTSP/UDP/HTTP)
If you have a live drone stream or RTSP camera configured, you can verify the stream bandwidth and latency using our utility:
```bash
python tests/test_drone_stream.py --port 8554
```
Replace the port with your RTSP server configurations. Supported formats include:
*   **RTSP:** `rtsp://<IP_ADDRESS>:8554/video`
*   **UDP:** `udp://<IP_ADDRESS>:5600`
*   **HTTP MJPEG:** `http://<IP_ADDRESS>:8080/stream`

---

## 5. Adding Project Assets
To upload your own project demonstration video or recordings to this repository:
1. Place your video file inside this directory and name it `astropath-demo.mp4`.
2. For large media files exceeding GitHub's file size limits ($100\text{ MB}$), upload the video to YouTube or Google Drive and link it directly in the main `README.md` file.
