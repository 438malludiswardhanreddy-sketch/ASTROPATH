# 🚀 ASTROPATH - Complete Deployment Guide

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start (Windows)

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd ASTROPATH-1

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Download YOLO Model (Required)

```powershell
# Download YOLOv4-tiny weights (196 MB)
# Option A: Using PowerShell
Invoke-WebRequest -Uri "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" -OutFile "models\yolov4-tiny.weights"

# Option B: Download manually from browser
# https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
# Save to: models\yolov4-tiny.weights
```

### 3. Run the Application

```powershell
# Start the real-time web application
python app.py
```

**Access the application:**
- **Main Interface:** http://localhost:5000
- **Dashboard:** http://localhost:5000/dashboard
- **From Phone/Tablet:** http://YOUR_PC_IP:5000

---

## 💻 Local Development

### Configuration

Edit `config.py` to customize settings:

```python
# Camera Source
CAMERA_SOURCE = 0  # 0 = Default webcam
# CAMERA_SOURCE = 1  # External camera
# CAMERA_SOURCE = "http://192.168.1.100:81/stream"  # ESP32-CAM

# GPS Settings
GPS_ENABLED = False  # Set True if GPS hardware connected
GPS_PORT = 'COM3'  # Windows: COM3, COM4, etc.
GPS_BAUD = 9600

# Detection Thresholds
CONF_THRESHOLD = 0.5  # Lower = more detections (less strict)
NMS_THRESHOLD = 0.4

# Fast Mode (Better FPS on slower systems)
FAST_MODE = True
```

### Testing GPS

If you have GPS hardware:

```python
python test_gps.py
```

### Testing with ESP32-CAM

1. Set up your ESP32-CAM (see `ESP32_CAM_SETUP.md`)
2. Update `config.py`:
   ```python
   CAMERA_SOURCE = "http://192.168.1.100:81/stream"
   ```
3. Run the application

---

## 🌐 Production Deployment

### Option 1: Using Waitress (Recommended for Windows)

```powershell
# Install waitress
pip install waitress

# Run with waitress
waitress-serve --host=0.0.0.0 --port=5000 --call app:app
```

### Option 2: Using Gunicorn (Linux)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Option 3: Systemd Service (Linux)

Create `/etc/systemd/system/astropath.service`:

```ini
[Unit]
Description=ASTROPATH Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ASTROPATH-1
Environment="PATH=/home/pi/ASTROPATH-1/venv/bin"
ExecStart=/home/pi/ASTROPATH-1/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable astropath
sudo systemctl start astropath
```

---

## 🐳 Docker Deployment

### Build and Run

```powershell
# Build Docker image
docker build -t astropath:latest .

# Run container
docker run -d `
  --name astropath `
  -p 5000:5000 `
  -v ${PWD}/detections:/app/detections `
  -v ${PWD}/models:/app/models `
  --restart unless-stopped `
  astropath:latest

# View logs
docker logs -f astropath
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  astropath:
    build: .
    container_name: astropath
    ports:
      - "5000:5000"
    volumes:
      - ./detections:/app/detections
      - ./models:/app/models
      - ./uploads:/app/uploads
    environment:
      - FLASK_ENV=production
      - GPS_ENABLED=false
    restart: unless-stopped
    device_cgroup_rules:
      - 'c 81:* rmw'  # For camera access
```

Run:
```powershell
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create astropath-app

# Add buildpack for OpenCV
heroku buildpacks:clear
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add --index 2 heroku/python

# Deploy
git push heroku main
```

### AWS EC2

```bash
# Connect to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Clone repository
git clone YOUR_REPO_URL
cd ASTROPATH-1

# Set up
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download YOLO model
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
mv yolov4-tiny.weights models/

# Run with systemd (see above)
```

### Nginx Configuration

Create `/etc/nginx/sites-available/astropath`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket support for video streaming
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /static {
        alias /path/to/ASTROPATH-1/static;
        expires 30d;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/astropath /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📱 Mobile Access

### Connect Phone to PC Network

1. Connect phone to same WiFi as PC
2. Find PC IP address:
   ```powershell
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```
3. Open browser on phone: `http://192.168.1.100:5000`

### Use Phone Camera

The web interface supports:
- Direct camera access via browser
- File upload from camera roll
- GPS location from phone

---

## 🔧 Advanced Configuration

### For Raspberry Pi

```python
# config.py
PI_OPTIMIZE = True
FAST_MODE = True
FAST_IMG_SIZE_YOLO = 320
DETECTION_FRAME_SKIP = 3  # Process every 3rd frame

# Enable GPS
GPS_ENABLED = True
GPS_PORT = '/dev/serial0'
```

### For ESP32-CAM

```python
# config.py
CAMERA_SOURCE = "http://192.168.1.100:81/stream"
```

Upload this to ESP32-CAM:
```cpp
// See ESP32_CAM_SETUP.md for complete code
#include <WiFi.h>
#include <esp_camera.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
```

---

## 🐛 Troubleshooting

### Camera Not Working

```python
# Test camera sources
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
python -c "import cv2; print(cv2.VideoCapture(1).isOpened())"
```

### YOLO Model Not Found

```
Error: YOLO model files not found
Solution: 
1. Download yolov4-tiny.weights
2. Place in models/ folder
3. Check file path in config.py
```

### Port Already in Use

```powershell
# Windows - Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Change port in config.py
FLASK_PORT = 8000
```

### Low FPS / Performance Issues

```python
# config.py adjustments
FAST_MODE = True
FAST_IMG_SIZE_YOLO = 320  # Smaller = faster
DETECTION_FRAME_SKIP = 3  # Higher = faster but less frequent detection
```

### GPS Not Connecting

```python
# Test GPS
python test_gps.py

# Common fixes:
# 1. Check port name (COM3, /dev/ttyUSB0, etc.)
# 2. Check baud rate (9600 is most common)
# 3. Ensure GPS has clear sky view for satellite fix
# 4. Install drivers if needed
```

---

## 📊 Monitoring

### Check System Status

```bash
# Health check
curl http://localhost:5000/health

# View logs
tail -f astropath.log

# Docker logs
docker logs -f astropath
```

### Database Check

```python
# Open Python shell
python

>>> from src.database import DetectionDatabase
>>> db = DetectionDatabase()
>>> stats = db.get_statistics()
>>> print(stats)
```

---

## 🔐 Security Recommendations

For production deployment:

1. **Disable Debug Mode**
   ```python
   FLASK_DEBUG = False
   ```

2. **Change Secret Key**
   ```python
   app.config['SECRET_KEY'] = 'your-secret-key-here'
   ```

3. **Use HTTPS** (with Let's Encrypt)
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **Set Up Firewall**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

---

## 📈 Performance Optimization

### For High-Traffic Deployments

1. **Use load balancer** (nginx upstream)
2. **Enable caching** (Redis)
3. **Use PostgreSQL** instead of SQLite
4. **CDN for static files**
5. **Multiple worker processes**

---

## 📄 License & Support

**ASTROPATH** - Smart Road Damage Reporting System
© 2026 Solapur Municipal Corporation

For support: 438malludiswardhanreddy@gmail.com

---

**Ready to deploy! 🚀**
