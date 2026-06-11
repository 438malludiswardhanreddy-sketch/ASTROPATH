# PATENT SPECIFICATION DRAFT: ASTROPATH FLIGHT SYSTEM

**Document Reference:** research/patent_draft.md  
**Format:** Indian Patent Office (IPO) Specification Draft  
**Language Style:** Indian English (UK/Commonwealth Conventions)  

---

## FORM 2
**THE PATENTS ACT, 1970**  
**(39 of 1970)**  
**&**  
**THE PATENT RULES, 2003**  

### COMPLETE SPECIFICATION
*(See section 10 and rule 13)*

---

### 1. TITLE OF THE INVENTION
**ASTROPATH: AN EDGE-INTEGRATED MULTI-SENSOR FUSION SKY-VIEW SYSTEM AND METHOD FOR REAL-TIME ROAD HAZARD GEOLOCALISATION AND AUTONOMOUS UAV FLIGHT SAFETY OVERRIDES**

---

### 2. APPLICANT(S)
*   **Name:** Mallu Diswardhan Reddy  
*   **Nationality:** Indian  
*   **Address:** Pune-Solapur Expressway Corridor, Maharashtra, India  

---

### 3. PREAMBLE TO THE DESCRIPTION
The following specification particularly describes the invention and the manner in which it is to be performed:

---

### 4. FIELD OF THE INVENTION
The present invention relates generally to unmanned aerial vehicle (UAV) navigation and automation. More specifically, the invention relates to an edge-computed multi-sensor state estimation architecture, pixel-to-coordinate geolocation projection, and dynamic safety decision overriding based on real-time environmental perception and power metrics.

---

### 5. BACKGROUND OF THE INVENTION AND PRIOR ART
Municipal infrastructure monitoring is highly dependent on manual inspections, which are resource-intensive and lack accuracy in mapping geographical damage patterns. Aerial mapping using standard commercial drones provides raw video data but presents key technical bottlenecks:
1.  **Coordinate Inaccuracy:** Raw GPS telemetry on small UAVs has high noise levels (5-10m), making pinpoint localization of small potholes impossible.
2.  **Lack of Real-Time Obstacle Avoidance:** Standard drones cannot differentiate between static obstacles (like tree branches), wire hazards (power lines), and dynamic objects (like birds), applying a generic collision response that often leads to flight stability losses.
3.  **No Onboard Safety Overrides:** Commercially available drones rely on simple battery RTH (Return-To-Home) thresholds, neglecting the coupled impacts of crosswinds and heavy monsoonal rain on power consumption during the return flight.

The present invention addresses these limitations by introducing a lightweight, edge-runnable 3D Kalman Filter, pixel-level projection equations, and a safety decision engine that dynamically adjusts flight parameters.

---

### 6. DETAILED DESCRIPTION OF THE TECHNICAL SYSTEM

#### 6.1. The Dual-Stage Edge Computer Vision Assembly
The onboard camera stream is analysed through a dual-stage neural network executed on an edge computing unit (e.g., Raspberry Pi 4 equipped with an Edge TPU accelerator). 
1.  A first YOLOv4-tiny network is configured to output bounding box coordinates of potential damage areas.
2.  A second MobileNetV2 classifier verifies the region of interest cropped from the bounding box to confirm a pothole match and estimate physical severity.

#### 6.2. Pixel-to-Ground Coordinate Geolocation Projection
Once a pothole is validated, its pixel centroid $(x_p, y_p)$ is projected to real-world ground GPS coordinates $(lat_g, lon_g)$ by resolving camera field-of-view (FOV) and gimbal angles:
$$ground\_width = 2 \times altitude \times \tan\left(\frac{FOV_h}{2}\right)$$
$$ground\_height = 2 \times altitude \times \tan\left(\frac{FOV_v}{2}\right)$$

Applying rotational transformation relative to drone heading $\psi$:
$$x_{rot} = x_{offset} \cos(\psi) - y_{offset} \sin(\psi)$$
$$y_{rot} = x_{offset} \sin(\psi) + y_{offset} \cos(\psi)$$

The ground latitudinal and longitudinal points are then calculated:
$$lat_g = lat_{drone} + \frac{y_{rot}}{111320.0}$$
$$lon_g = lon_{drone} + \frac{x_{rot}}{111320.0 \times \cos(lat_{drone})}$$

#### 6.3. Threat-Specific Detour and Routing Engine
Unlike generic navigation systems, this invention classifies threats into tree, wire, and bird hazard types and executes specialized spatial maneuvers:
```
                      [AI Perception Output]
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
           [if Tree]       [if Wire]       [if Bird]
               │               │               │
               ▼               ▼               ▼
         [Lateral detour]  [Vertical climb] [Hover-in-place]
         (+4m deviation)   (+6m altitude)   (Wait for flock)
```

#### 6.4. Combined Safety Decision Engine
A hardware monitor checks battery capacity, wind speed, and rain precipitation levels. The safety module overrides the autopilot state when threshold parameters are crossed:
- **Low Battery Override ($<15\%$):** Triggers a safe Emergency Landing (EL) at the nearest open space coordinate instead of returning to a distant home base.
- **Wind Speed Gusts ($>25\text{ knots}$):** Automatically reduces velocity to $1.5\text{ m/s}$ and adjusts yaw controls to stabilise crosswind impacts.
- **Precipitation ($>15\text{ mm/h}$):** Restricts drone speed and logs camera lens distortion adjustments.

---

### 7. CLAIMS
**We claim:**

1.  **An autonomous road damage diagnostics system comprising:**
    *   an onboard imaging sensor configured to stream road surface video;
    *   an edge processing unit executing a dual-stage neural network for object detection and classification;
    *   a telemetry suite comprising a GPS transceiver, a barometric altimeter, and an Inertial Measurement Unit (IMU);
    *   **characterised in that** a 3D Kalman Filter fuses telemetry data to generate a stabilized state estimation, and a projection engine converts image coordinate frames into absolute latitude and longitude coordinates.

2.  **The system as claimed in claim 1, wherein the edge processing unit classifies obstacles into static, thin wire, and dynamic bird categories:**
    *   wherein static tree obstacles trigger a lateral bypass deviation;
    *   wherein thin wire obstacles trigger a vertical climb profile detour;
    *   wherein dynamic bird obstacles trigger a hover-in-place pause.

3.  **The system as claimed in claim 1, further comprising a safety decision module configured to monitor battery and environmental sensors, wherein a battery drop below 15% triggers an immediate emergency landing sequence at a dynamically calculated safe landing zone.**

---
*End of Specification.*
