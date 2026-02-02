# 🚀 ASTROPATH - 3-Step Quick Start

## Step 1: Open PowerShell in Project Folder
1. Navigate to: `Desktop\pothole\ASTROPATH-1`
2. Right-click in folder → "Open in Terminal" or "PowerShell here"

## Step 2: Run Start Script
```powershell
.\start.ps1
```

## Step 3: Open Browser
Go to: **http://localhost:5000**

---

## ✅ That's It!

The app will:
- ✅ Check Python
- ✅ Install dependencies
- ✅ Offer to download YOLO model
- ✅ Start the web server

---

## 📱 Access from Phone

After starting, the script shows your IP (e.g., `192.168.1.100`)

On your phone:
1. Connect to same WiFi
2. Open browser
3. Go to: `http://YOUR_IP:5000`

---

## 🎥 What You'll See

### Main Page (/)
- Live camera feed with detection
- Statistics cards
- Recent detections list
- Citizen report button

### Dashboard (/dashboard)
- Interactive map with markers
- Heatmap view
- Detection statistics
- Filter by severity

---

## 🔧 Troubleshooting

### "Python not found"
Install Python from: https://www.python.org/downloads/

### "Port already in use"
Change port in `config.py`:
```python
FLASK_PORT = 8000
```

### "Camera not working"
Try different camera source in `config.py`:
```python
CAMERA_SOURCE = 0  # or 1, 2
```

---

## 📚 More Help

- **Complete Guide:** `DEPLOY_GUIDE.md`
- **Full Documentation:** `START_HERE.md`
- **API Reference:** `README.md`

---

**Need Help?** Contact: 438malludiswardhanreddy@gmail.com
