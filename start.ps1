# ASTROPATH Quick Start Script for Windows
# This script sets up and runs the application

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "🚨 ASTROPATH - Quick Start" -ForegroundColor Cyan
Write-Host "Smart Road Damage Detection System" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8 or higher" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes on first run)" -ForegroundColor Gray
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some packages may have failed to install" -ForegroundColor Yellow
}

# Check for YOLO model
Write-Host ""
Write-Host "🔍 Checking for YOLO model..." -ForegroundColor Yellow
if (-not (Test-Path "models\yolov4-tiny.weights")) {
    Write-Host "❌ YOLO model not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "You have two options:" -ForegroundColor Yellow
    Write-Host "1. Download automatically (196 MB)" -ForegroundColor White
    Write-Host "2. Download manually later" -ForegroundColor White
    Write-Host ""
    $download = Read-Host "Download now? (y/n)"
    
    if ($download -eq "y" -or $download -eq "Y") {
        Write-Host ""
        Write-Host "⬇️  Downloading YOLO model (196 MB)..." -ForegroundColor Yellow
        Write-Host "This will take a few minutes depending on your internet speed" -ForegroundColor Gray
        
        $url = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"
        $output = "models\yolov4-tiny.weights"
        
        try {
            # Create models directory if it doesn't exist
            if (-not (Test-Path "models")) {
                New-Item -ItemType Directory -Path "models" | Out-Null
            }
            
            Invoke-WebRequest -Uri $url -OutFile $output
            Write-Host "✓ YOLO model downloaded successfully" -ForegroundColor Green
        } catch {
            Write-Host "❌ Download failed" -ForegroundColor Red
            Write-Host "Please download manually from:" -ForegroundColor Yellow
            Write-Host $url -ForegroundColor White
            Write-Host "Save to: $output" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "⚠ Note: Detection will be limited without YOLO model" -ForegroundColor Yellow
        Write-Host "Download from: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" -ForegroundColor White
        Write-Host "Save to: models\yolov4-tiny.weights" -ForegroundColor White
    }
} else {
    Write-Host "✓ YOLO model found" -ForegroundColor Green
}

# Create required directories
Write-Host ""
Write-Host "📁 Creating required directories..." -ForegroundColor Yellow
$dirs = @("detections", "uploads", "models", "static\css", "static\js", "templates")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories ready" -ForegroundColor Green

# Get local IP address
Write-Host ""
Write-Host "🌐 Network Information:" -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "  Local IP: $ipAddress" -ForegroundColor White
} else {
    $ipAddress = "localhost"
    Write-Host "  Using: localhost" -ForegroundColor White
}

# Display access information
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "🚀 Starting ASTROPATH Application" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  🖥️  This PC:" -ForegroundColor White
Write-Host "      http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "  📱 From Phone/Tablet:" -ForegroundColor White
Write-Host "      http://${ipAddress}:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Available Pages:" -ForegroundColor Yellow
Write-Host "  • Main Interface:  http://localhost:5000" -ForegroundColor White
Write-Host "  • Dashboard:       http://localhost:5000/dashboard" -ForegroundColor White
Write-Host "  • API Health:      http://localhost:5000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Run the application
python app.py
