# ASTROPATH Quick Deploy Script
# Automated deployment with model download and configuration

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ASTROPATH - Quick Deploy Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in project directory
if (!(Test-Path "app.py")) {
    Write-Host "✗ Error: app.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the ASTROPATH-1 directory" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Check/Download YOLO Model
Write-Host ""
Write-Host "[2/5] Checking YOLO model..." -ForegroundColor Yellow

if (Test-Path "models\yolov4-tiny.weights") {
    $fileSize = (Get-Item "models\yolov4-tiny.weights").length / 1MB
    Write-Host "✓ YOLO model found ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "⚠ YOLO model not found. Downloading..." -ForegroundColor Yellow
    Write-Host "  This is a 196 MB file, will take a few minutes..." -ForegroundColor Cyan
    
    New-Item -ItemType Directory -Force -Path "models" | Out-Null
    
    try {
        $url = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"
        $output = "models\yolov4-tiny.weights"
        
        # Show progress
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri $url -OutFile $output
        
        Write-Host "✓ YOLO model downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Download failed: $_" -ForegroundColor Red
        Write-Host "Please download manually from:" -ForegroundColor Yellow
        Write-Host "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights" -ForegroundColor Cyan
        Write-Host "Save to: models\yolov4-tiny.weights" -ForegroundColor Cyan
        exit 1
    }
}

# Step 3: Virtual Environment
Write-Host ""
Write-Host "[3/5] Setting up virtual environment..." -ForegroundColor Yellow

if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Step 4: Install Dependencies
Write-Host ""
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan

pip install -r requirements.txt --quiet --disable-pip-version-check

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some dependencies may have issues" -ForegroundColor Yellow
}

# Step 5: Get Local IP
Write-Host ""
Write-Host "[5/5] Getting network information..." -ForegroundColor Yellow

$localIP = (Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*VMware*"} | 
    Select-Object -First 1).IPAddress

if (!$localIP) {
    $localIP = "localhost"
}

# Display deployment options
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Choose Deployment Option" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Local Only" -ForegroundColor Green
Write-Host "   Access only from this computer"
Write-Host "   URL: http://localhost:5000"
Write-Host ""
Write-Host "2. Local Network" -ForegroundColor Green
Write-Host "   Access from any device on same WiFi"
Write-Host "   URL: http://${localIP}:5000"
Write-Host ""
Write-Host "3. Internet (via Ngrok)" -ForegroundColor Green
Write-Host "   Access from anywhere in the world"
Write-Host "   Requires: Ngrok installed"
Write-Host ""
Write-Host "4. Cloud Deployment Guide" -ForegroundColor Green
Write-Host "   Deploy to Render, Railway, AWS, etc."
Write-Host ""

$deployChoice = Read-Host "Enter choice (1-4)"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($deployChoice -eq "1") {
    # Local only
    Write-Host ""
    Write-Host "🚀 Starting ASTROPATH (Local Mode)..." -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Application will be available at:" -ForegroundColor Yellow
    Write-Host "  →  http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Update config for local
    $configContent = Get-Content config.py -Raw
    $configContent = $configContent -replace 'FLASK_HOST = "0.0.0.0"', 'FLASK_HOST = "127.0.0.1"'
    Set-Content config.py -Value $configContent
    
    python app.py
}
elseif ($deployChoice -eq "2") {
    # Local network
    Write-Host ""
    Write-Host "🚀 Starting ASTROPATH (Network Mode)..." -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Application will be available at:" -ForegroundColor Yellow
    Write-Host "  From this computer:  http://localhost:5000" -ForegroundColor Cyan
    Write-Host "  From other devices:  http://${localIP}:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📱 On your phone:" -ForegroundColor Yellow
    Write-Host "  1. Connect to same WiFi network" -ForegroundColor Gray
    Write-Host "  2. Open browser and go to:" -ForegroundColor Gray
    Write-Host "     http://${localIP}:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Update config for network
    $configContent = Get-Content config.py -Raw
    $configContent = $configContent -replace 'FLASK_HOST = "127.0.0.1"', 'FLASK_HOST = "0.0.0.0"'
    Set-Content config.py -Value $configContent
    
    python app.py
}
elseif ($deployChoice -eq "3") {
    # Ngrok setup
    Write-Host ""
    Write-Host "🌍 Internet Deployment via Ngrok" -ForegroundColor Green
    Write-Host ""
    
    try {
        ngrok version | Out-Null
        $ngrokInstalled = $true
    } catch {
        $ngrokInstalled = $false
    }
    
    if (!$ngrokInstalled) {
        Write-Host "⚠ Ngrok not found" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Setup Ngrok:" -ForegroundColor Cyan
        Write-Host "1. Download: https://ngrok.com/download" -ForegroundColor Gray
        Write-Host "2. Extract ngrok.exe to a folder" -ForegroundColor Gray
        Write-Host "3. Sign up: https://dashboard.ngrok.com/signup" -ForegroundColor Gray
        Write-Host "4. Get auth token and run config command" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "✓ Ngrok found" -ForegroundColor Green
        
        Write-Host "Starting Ngrok tunnel..." -ForegroundColor Cyan
        ngrok http 5000
    }
}
elseif ($deployChoice -eq "4") {
    Write-Host "Opening deployment guide..."
    Start-Process "REAL_WORLD_DEPLOYMENT.md"
}
else {
    Write-Host "Invalid choice. Please run again and select 1-4" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Thank you for using ASTROPATH!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
