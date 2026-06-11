# ASTROPATH Functional System Flow (ASCII Chart)

This document maps the complete functional flow of the ASTROPATH autopilot planning, sensor fusion, object perception, threat scoring, and safety override layers in plain-text ASCII representation.

---

## Logical System Pipeline

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
│ optimisation│ │ Engine      │ │ Landing AI  │
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
