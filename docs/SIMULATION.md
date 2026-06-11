# ASTROPATH Autonomous Flight & Safety Simulation Engine

To test the end-to-end logical flow of the ASTROPATH architecture, the repository contains a standalone physical and environmental flight simulation engine at [autonomous_flight_system.py](file:///C:/Users/mallu/OneDrive/Documents/Desktop/pothole/ASTROPATH-1/src/navigation/autonomous_flight_system.py).

This simulator models the flight cycle through 10 chronological steps, dynamically injecting real-world obstacles and sensor anomalies:
1. **Takeoff & Altitude Hold:** Simulates GPS, Altimeter, and IMU sensor data.
2. **Sensor Fusion:** Fuses noisy telemetry measurements using a **Kalman Filter** state estimator.
3. **AI Vision Perception:** Scans roads for potholes and detects tree branches, hanging electrical wires, and birds in front of the drone.
4. **Threat Assessment:** Evaluates spatial distance and collision danger scores.
5. **Re-routing Engine:** Generates detours (e.g., lateral bypass for trees, climb profile for wires, hover-in-place for birds).
6. **Battery & Weather Monitor:** Dynamically injects heavy wind gusts, severe downpours, and drains battery capacity.
7. **Safety Decision Engine:** Overrides standard flight paths to trigger RTH and safe emergency landing procedures if safety limits are breached.

---

## How to Run the Simulator
Ensure you have the virtual environment activated and dependencies installed, then execute:
```bash
python src/navigation/autonomous_flight_system.py
```

---

## Complete Simulation Output Logs
```text
[22:36:56] [INFO] [ASTROPATH_Core] Mission Planner initialised. Start: (17.6599, 75.9064) | Target: (17.6682, 75.9125)
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
Safety Decision Engine Override: Activating Auto-Stabilisation. Reducing velocity to 1.5m/s.

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
Safety Decision Engine Override: Activating Auto-Stabilisation. Reducing velocity to 1.5m/s.

--- [MISSION FLIGHT STEP 8/10] Mode: CRUISE ---
[WARNING] 🌧️ Rain rate sensor reporting heavy downpour: 18.0 mm/h!
Monitor Stats - Battery: 64.0% | Wind: 12.0 kts | Rain: 18.0 mm/h
Sensor Fusion State: Lat: 17.663282 | Lon: 75.908951 | Alt: 16.74m
AI Vision Layer: Detected 1 objects.
  └─ Label: Pothole | Confidence: 96.0% | Spatial Offset: (x: -2.912m, y: 4.445m)
[CRITICAL] ⚠️ SAFETY INTERVENTION: Extreme precipitation detected!
Safety Decision Engine Override: Activating Auto-Stabilisation. Reducing velocity to 1.5m/s.

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
