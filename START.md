# 🚀 ASTROPATH - Quick Start

**Smart Road Damage Reporting & Rapid Response System**

## ⚡ 3-Minute Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model (196 MB)
# YOLOv4-tiny.weights → https://github.com/AlexeyAB/darknet/releases
# Place in: models/

# 3. Run the menu
python main.py
```

**Select Option 2** to start detection from webcam!

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **README.md** | 📖 Full project guide |
| **SETUP_GUIDE.md** | 🔧 Installation & setup |
| **QUICK_REFERENCE.md** | ⚡ Commands cheat sheet |
| **DATA_STRUCTURES.md** | 📊 API reference |
| **DEPLOYMENT_CHECKLIST.md** | ✅ Pre-launch checklist |

---

## 🎯 What You Can Do

```python
# 1. Train a classifier
python main.py  # Select: 1. Train Pothole Classifier

# 2. Run detection
python main.py  # Select: 2. Run Edge Detection

# 3. Start web form
python main.py  # Select: 3. Start Citizen Reporting Web App

# 4. Test API
python main.py  # Select: 4. Test API Client
```

---

## 📁 Project Structure

```
ASTROPATH/
├── config.py              # ⚙️ All settings (edit here!)
├── main.py                # 🎮 Menu interface
├── requirements.txt       # 📦 Dependencies
├── README.md              # 📖 Full guide
├── SETUP_GUIDE.md         # 🔧 Installation
├── QUICK_REFERENCE.md     # ⚡ Commands
├── DATA_STRUCTURES.md     # 📊 API specs
├── DEPLOYMENT_CHECKLIST.md # ✅ Checklist
│
├── src/
│   ├── train_classifier.py    # 🎓 Training
│   ├── detect_edge.py         # 📹 Detection
│   ├── api_client.py          # 🌐 Cloud API
│   ├── citizen_upload.py      # 👤 Web form
│   └── utils.py               # 🔧 Utilities
│
├── models/                # 🤖 Model files
├── data/                  # 📊 Training data
├── detections/            # 📁 Output
└── uploads/               # 📁 Uploads
```

---

## 🚀 Getting Started

**New here?** Start with README.md  
**Ready to install?** Use SETUP_GUIDE.md  
**Need commands?** Check QUICK_REFERENCE.md  
**Deploying?** See DEPLOYMENT_CHECKLIST.md  

---

## ✅ Project Status

✅ Production-ready code  
✅ Comprehensive documentation  
✅ Raspberry Pi compatible  
✅ Cloud-integrated  
✅ Ready to deploy  

---

**Next:** Download YOLOv4-tiny.weights, then run `python main.py` 🎉
