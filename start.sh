#!/bin/bash
# ASTROPATH Quick Start Script for Linux/Mac

echo "======================================="
echo "🚨 ASTROPATH - Quick Start"
echo "Smart Road Damage Detection System"
echo "======================================="
echo ""

# Check Python installation
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Python found: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
echo "(This may take a few minutes on first run)"
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠ Some packages may have failed to install"
fi

# Check for YOLO model
echo ""
echo "🔍 Checking for YOLO model..."
if [ ! -f "models/yolov4-tiny.weights" ]; then
    echo "❌ YOLO model not found"
    echo ""
    echo "Downloading YOLO model (196 MB)..."
    
    mkdir -p models
    wget -q --show-progress \
        https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights \
        -O models/yolov4-tiny.weights
    
    if [ $? -eq 0 ]; then
        echo "✓ YOLO model downloaded successfully"
    else
        echo "❌ Download failed"
        echo "Please download manually from:"
        echo "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"
        echo "Save to: models/yolov4-tiny.weights"
    fi
else
    echo "✓ YOLO model found"
fi

# Create required directories
echo ""
echo "📁 Creating required directories..."
mkdir -p detections uploads models static/css static/js templates
echo "✓ Directories ready"

# Get local IP address
echo ""
echo "🌐 Network Information:"
IP_ADDRESS=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
echo "  Local IP: $IP_ADDRESS"

# Display access information
echo ""
echo "======================================="
echo "🚀 Starting ASTROPATH Application"
echo "======================================="
echo ""
echo "Access the application at:"
echo "  🖥️  This PC:"
echo "      http://localhost:5000"
echo ""
echo "  📱 From Phone/Tablet:"
echo "      http://${IP_ADDRESS}:5000"
echo ""
echo "Available Pages:"
echo "  • Main Interface:  http://localhost:5000"
echo "  • Dashboard:       http://localhost:5000/dashboard"
echo "  • API Health:      http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================="
echo ""

# Run the application
python3 app.py
