# ASTROPATH RESTful API Specifications

The ASTROPATH server exposes RESTful API endpoints for drone telemetric uploads, citizen reporting portals, and real-time dashboard analytics synchronisation.

---

## Endpoint Specifications

| Method | Endpoint | Description | Sample Response Payload |
|:---|:---|:---|:---|
| **GET** | `/health` | Ingestion layer health check | `{"status": "healthy", "gpu_available": false}` |
| **GET** | `/api/detections` | Retrieve registered road defects | `[{"id": 12, "latitude": 17.65, "severity": "High"}]` |
| **GET** | `/api/stats` | Aggregated telemetry & count statistics | `{"total_potholes": 84, "high_severity": 19}` |
| **POST**| `/api/upload` | Upload citizen-submitted road defect | `{"status": "success", "detection_id": 232}` |

---

## Sample Citizen Reporting Request (Python)

The following script simulates a client upload of a detected road defect, attaching geolocated coordinates and a binary image file payload:

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
