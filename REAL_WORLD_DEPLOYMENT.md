# 🚀 ASTROPATH - REAL WORLD DEPLOYMENT GUIDE

## Complete Guide to Deploy ASTROPATH to Production

---

## 🎯 Deployment Options

Choose the option that fits your needs:

| Option | Best For | Cost | Difficulty | Time |
|--------|----------|------|------------|------|
| **1. Local Network** | Testing, municipal office | Free | ⭐ Easy | 5 min |
| **2. Ngrok (Tunnel)** | Quick demo, testing | Free | ⭐ Easy | 2 min |
| **3. Render.com** | Production, free tier | Free | ⭐⭐ Medium | 15 min |
| **4. Railway** | Production, auto-deploy | Free tier | ⭐⭐ Medium | 10 min |
| **5. AWS EC2** | Enterprise, full control | Paid | ⭐⭐⭐ Hard | 30 min |
| **6. DigitalOcean** | Production, simple | $5/mo | ⭐⭐ Medium | 20 min |
| **7. Heroku** | Simple production | Free tier | ⭐⭐ Medium | 15 min |

---

## 🚀 OPTION 1: Local Network Deployment (Easiest!)

**Perfect for:** Municipal office, WiFi network access, testing

### Step 1: Download YOLO Model

```powershell
# Create models directory
New-Item -ItemType Directory -Force -Path "models"

# Download YOLO model (196 MB)
Write-Host "Downloading YOLO model..."
Invoke-WebRequest -Uri "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" -OutFile "models\yolov4-tiny.weights"
```

### Step 2: Configure for Network Access

Edit `config.py`:
```python
# Allow access from network
FLASK_HOST = "0.0.0.0"  # Listen on all network interfaces
FLASK_PORT = 5000

# Important: Set for production
FLASK_DEBUG = False
```

### Step 3: Start the Application

```powershell
.\start.ps1
```

### Step 4: Find Your IP Address

```powershell
# Get your local IP
ipconfig | findstr IPv4
```

### Step 5: Access from Any Device

On any device connected to the **same WiFi/network**:
- **From phone:** `http://YOUR_IP:5000`
- **From laptop:** `http://YOUR_IP:5000`
- **Example:** `http://192.168.1.100:5000`

✅ **That's it!** Your app is now accessible on your local network!

---

## 🌐 OPTION 2: Ngrok (Internet Access - Instant!)

**Perfect for:** Quick demo, sharing with anyone, testing

### Step 1: Install Ngrok

1. Download from: https://ngrok.com/download
2. Extract to folder
3. Sign up for free account
4. Get your auth token

### Step 2: Setup Ngrok

```powershell
# Navigate to ngrok folder
cd C:\path\to\ngrok

# Set auth token (from ngrok dashboard)
.\ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Start Your App

```powershell
# In ASTROPATH folder
.\start.ps1
```

### Step 4: Create Tunnel

```powershell
# In another PowerShell window
cd C:\path\to\ngrok
.\ngrok http 5000
```

### Step 5: Get Public URL

Ngrok will show:
```
Forwarding https://abc123.ngrok.io -> http://localhost:5000
```

✅ **Share this URL with anyone!** `https://abc123.ngrok.io`

⚠️ **Note:** Free tier URL changes each time. Upgrade for fixed URL.

---

## ☁️ OPTION 3: Render.com (Free Cloud Hosting)

**Perfect for:** Production deployment, 24/7 availability, free tier

### Step 1: Prepare Repository

```powershell
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/ASTROPATH.git
git branch -M main
git push -u origin main
```

### Step 2: Create render.yaml

Create file `render.yaml` in project root:

```yaml
services:
  - type: web
    name: astropath
    env: python
    buildCommand: |
      pip install -r requirements.txt
      mkdir -p models
      if [ ! -f models/yolov4-tiny.weights ]; then
        wget -q https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -O models/yolov4-tiny.weights
      fi
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: FLASK_ENV
        value: production
```

### Step 3: Deploy to Render

1. Go to https://render.com
2. Sign up (free)
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Render auto-detects settings
6. Click "Create Web Service"

✅ **Your app will be live at:** `https://astropath.onrender.com`

⚠️ **Note:** Free tier may sleep after inactivity (30 seconds wake-up time)

---

## 🚂 OPTION 4: Railway.app (Easy Auto-Deploy)

**Perfect for:** Developers, CI/CD, free tier

### Step 1: Prepare Project

Create `Procfile`:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

Create `runtime.txt`:
```
python-3.11
```

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select ASTROPATH repository
5. Railway auto-deploys!

✅ **Live at:** `https://astropath.railway.app`

---

## 🖥️ OPTION 5: AWS EC2 (Enterprise Production)

**Perfect for:** Large scale, full control, enterprise

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Choose: Ubuntu Server 22.04 LTS
4. Instance type: t2.medium (or t2.small for testing)
5. Create/select key pair
6. Security group: Allow port 22 (SSH) and 80 (HTTP)
7. Launch instance

### Step 2: Connect to Instance

```powershell
# Use SSH client or PuTTY
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

### Step 3: Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/ASTROPATH.git
cd ASTROPATH

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Download YOLO model
mkdir -p models
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -O models/yolov4-tiny.weights
```

### Step 4: Configure Gunicorn Service

Create `/etc/systemd/system/astropath.service`:

```ini
[Unit]
Description=ASTROPATH Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/ASTROPATH
Environment="PATH=/home/ubuntu/ASTROPATH/venv/bin"
ExecStart=/home/ubuntu/ASTROPATH/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start astropath
sudo systemctl enable astropath
```

### Step 5: Configure Nginx

Create `/etc/nginx/sites-available/astropath`:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/astropath /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

✅ **Access at:** `http://YOUR_EC2_IP`

---

## 🌊 OPTION 6: DigitalOcean Droplet

**Perfect for:** Simple VPS, good performance, $5/month

### Quick Deploy

1. Create droplet (Ubuntu 22.04)
2. Follow same steps as AWS EC2 above
3. Setup domain (optional): Point DNS to droplet IP
4. Add SSL: `sudo certbot --nginx -d yourdomain.com`

---

## 🟣 OPTION 7: Heroku (Simple Cloud Platform)

**Perfect for:** Quick deployment, managed platform

### Step 1: Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Prepare Application

Create `Procfile`:
```
web: gunicorn app:app
```

Create `requirements.txt` (ensure it has):
```
gunicorn==21.2.0
```

### Step 3: Deploy

```powershell
# Login to Heroku
heroku login

# Create app
heroku create astropath-detection

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

✅ **Live at:** `https://astropath-detection.herokuapp.com`

---

## 🔐 Security Considerations

### For Production Deployment:

1. **Disable Debug Mode**
```python
# config.py
FLASK_DEBUG = False
```

2. **Add Authentication** (Optional but recommended)
```python
# Simple password protection
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'your_secure_password'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('Login required', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# Apply to routes
@app.route('/')
@requires_auth
def index():
    ...
```

3. **Use HTTPS**
- For cloud platforms: Usually automatic
- For VPS: Use Let's Encrypt (free SSL)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

4. **Set Up Firewall**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

5. **Environment Variables**
Never commit sensitive data. Use environment variables:
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
```

---

## 📊 Recommended Setup by Use Case

### Municipal Office / Testing
**Option 1: Local Network**
- Cost: Free
- Time: 5 minutes
- Access: Office WiFi only

### Quick Demo / Presentation
**Option 2: Ngrok**
- Cost: Free
- Time: 2 minutes
- Access: Anyone with link

### Production - Small Scale
**Option 3: Render.com** or **Option 4: Railway**
- Cost: Free tier available
- Time: 15 minutes
- Access: Public URL, 24/7

### Production - Enterprise
**Option 5: AWS EC2** or **Option 6: DigitalOcean**
- Cost: $5-20/month
- Time: 30 minutes
- Access: Full control, scalable

---

## 🚀 Quick Deploy Script (Windows)

I'll create an automated deployment script for you:

Save as `deploy.ps1`:

```powershell
# ASTROPATH Quick Deploy Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   ASTROPATH Deployment Tool" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check YOLO model
if (!(Test-Path "models\yolov4-tiny.weights")) {
    Write-Host "⚠ YOLO model not found. Downloading..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path "models" | Out-Null
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" `
            -OutFile "models\yolov4-tiny.weights"
        Write-Host "✓ YOLO model downloaded" -ForegroundColor Green
    } catch {
        Write-Host "✗ Download failed. Please download manually." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Select deployment option:" -ForegroundColor Yellow
Write-Host "1. Local Network (WiFi access only)"
Write-Host "2. Ngrok Tunnel (Internet access)"
Write-Host "3. Cloud Setup Guide"
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting local network deployment..." -ForegroundColor Green
        
        # Get local IP
        $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
        
        Write-Host ""
        Write-Host "✓ Your app will be accessible at:" -ForegroundColor Green
        Write-Host "  Local:   http://localhost:5000" -ForegroundColor Cyan
        Write-Host "  Network: http://${ip}:5000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Starting application..." -ForegroundColor Yellow
        
        .\start.ps1
    }
    
    "2" {
        Write-Host ""
        Write-Host "Ngrok Setup:" -ForegroundColor Yellow
        Write-Host "1. Download ngrok from: https://ngrok.com/download"
        Write-Host "2. Sign up for free account"
        Write-Host "3. Run: ngrok http 5000"
        Write-Host ""
        Write-Host "Starting application..." -ForegroundColor Green
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\start.ps1"
        
        Write-Host ""
        Write-Host "App started! Now run ngrok in another window." -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "Cloud Deployment Options:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Free Options:" -ForegroundColor Cyan
        Write-Host "• Render.com   - https://render.com"
        Write-Host "• Railway.app  - https://railway.app"
        Write-Host "• Fly.io       - https://fly.io"
        Write-Host ""
        Write-Host "Paid Options:" -ForegroundColor Cyan
        Write-Host "• AWS EC2         - https://aws.amazon.com"
        Write-Host "• DigitalOcean    - https://digitalocean.com"
        Write-Host "• Google Cloud    - https://cloud.google.com"
        Write-Host ""
        Write-Host "See DEPLOY_GUIDE.md for detailed instructions"
    }
}
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] YOLO model downloaded (`models/yolov4-tiny.weights`)
- [ ] `FLASK_DEBUG = False` in config.py
- [ ] All dependencies in requirements.txt
- [ ] Database initialized
- [ ] Tested locally
- [ ] Choose deployment platform
- [ ] (Optional) Domain name ready
- [ ] (Optional) SSL certificate configured
- [ ] (Optional) Authentication added
- [ ] (Optional) Monitoring setup

---

## 📞 Getting Help

- **Documentation:** Check `DEPLOY_GUIDE.md`
- **Issues:** Common problems and solutions below
- **Contact:** 438malludiswardhanreddy@gmail.com

---

## 🐛 Common Issues

### Issue: "Address already in use"
```powershell
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "YOLO model not found"
```powershell
# Download manually
Invoke-WebRequest -Uri "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" -OutFile "models\yolov4-tiny.weights"
```

### Issue: "Module not found"
```powershell
pip install -r requirements.txt --upgrade
```

---

## 🎯 Recommendation

**For Getting Started:** Use **Option 1 (Local Network)** - 5 minutes, free, works immediately

**For Production:** Use **Option 3 (Render.com)** or **Option 4 (Railway)** - Free tier, auto-deploy, 24/7 uptime

**For Enterprise:** Use **Option 5 (AWS EC2)** - Full control, scalable

---

**Ready to deploy? Start with Option 1 above! 🚀**
