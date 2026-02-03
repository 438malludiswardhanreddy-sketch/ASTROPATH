"""
ASTROPATH System Diagnostics Tool
Performs a full end-to-end check of all subsystems and generates a detailed report.
"""

import os
import sys
import time
import json
import socket
import sqlite3
import requests
import datetime
import cv2

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger

logger = setup_logger("diagnostics")

class SystemDiagnostics:
    def __init__(self):
        self.results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": {
                "os": sys.platform,
                "python_version": sys.version,
                "cwd": os.getcwd()
            },
            "subsystems": {}
        }
        self.report_file = "system_diagnostics.json"

    def check_file_structure(self):
        logger.info("Checking file structure...")
        required_dirs = [config.MODELS_DIR, config.DATA_DIR, config.DETECTIONS_DIR, config.UPLOAD_FOLDER]
        status = {}
        for d in required_dirs:
            exists = os.path.exists(d)
            status[os.path.basename(d)] = "PASSED" if exists else "FAILED"
        
        # Check model files specifically
        models = ["yolov4-tiny.weights", "yolov4-tiny.cfg", "obj.names"]
        for m in models:
            path = os.path.join(config.MODELS_DIR, m)
            status[m] = "PASSED" if os.path.exists(path) else "FAILED"
            
        self.results["subsystems"]["file_structure"] = status

    def check_database(self):
        logger.info("Checking database integrity...")
        status = {"path": config.BASE_DIR + "/detections.db"}
        try:
            conn = sqlite3.connect("detections.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            status["tables_found"] = tables
            status["health"] = "PASSED" if "detections" in tables else "FAILED"
            
            cursor.execute("SELECT COUNT(*) FROM detections")
            status["total_detections"] = cursor.fetchone()[0]
            conn.close()
        except Exception as e:
            status["health"] = f"CRITICAL - {str(e)}"
            
        self.results["subsystems"]["database"] = status

    def check_network_api(self):
        logger.info("Checking network and API availability...")
        status = {"api_url": config.API_URL}
        
        # Check if local port is open (Server check)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', config.FLASK_PORT))
            status["local_server_port_open"] = "YES" if result == 0 else "NO (Server might be stopped)"
            sock.close()
        except:
            status["local_server_port_open"] = "UNKNOWN"

        # Try a real request to the health endpoint
        try:
            health_url = f"http://localhost:{config.FLASK_PORT}/health"
            resp = requests.get(health_url, timeout=3)
            status["health_endpoint"] = "UP" if resp.status_code == 200 else f"DOWN ({resp.status_code})"
        except:
            status["health_endpoint"] = "UNREACHABLE"

        self.results["subsystems"]["network_api"] = status

    def check_drone_mavlink(self):
        logger.info("Verifying MAVLink configuration...")
        status = {
            "mode": "DRONE_ENABLED" if config.DRONE_ENABLED else "DISABLED",
            "connection_string": config.DRONE_MAVLINK_CONNECTION,
            "telemetry_source": config.DRONE_TELEMETRY_SOURCE
        }
        
        if config.DRONE_ENABLED and config.DRONE_TELEMETRY_SOURCE == 'mavlink':
            try:
                from pymavlink import mavutil
                status["pymavlink_installed"] = "YES"
            except ImportError:
                status["pymavlink_installed"] = "NO (REQUIRED FOR DRONE)"
        
        self.results["subsystems"]["drone_integration"] = status

    def check_vision_dnn(self):
        logger.info("Verifying Vision/DNN subsystem...")
        status = {}
        try:
            # Check OpenCV version
            status["opencv_version"] = cv2.__version__
            
            # Try to load YOLO (Fast check)
            if os.path.exists(config.YOLOV4_CFG) and os.path.exists(config.YOLOV4_WEIGHTS):
                net = cv2.dnn.readNetFromDarknet(config.YOLOV4_CFG, config.YOLOV4_WEIGHTS)
                status["yolo_load"] = "PASSED"
                
                # Check CUDA support
                count = cv2.cuda.getCudaEnabledDeviceCount() if hasattr(cv2, 'cuda') else 0
                status["cuda_available"] = "YES" if count > 0 else "NO (CPU Only)"
            else:
                status["yolo_load"] = "FAILED (Missing model files)"
        except Exception as e:
            status["yolo_load"] = f"FAILED - {str(e)}"
            
        self.results["subsystems"]["vision_dnn"] = status

    def run_all(self):
        logger.info("=== STARTING FULL SYSTEM DIAGNOSTICS ===")
        self.check_file_structure()
        self.check_database()
        self.check_network_api()
        self.check_drone_mavlink()
        self.check_vision_dnn()
        
        # Save results
        with open(self.report_file, 'w') as f:
            json.dump(self.results, f, indent=4)
        
        logger.info(f"=== DIAGNOSTICS COMPLETE. Results saved to {self.report_file} ===")
        return self.results

if __name__ == "__main__":
    diag = SystemDiagnostics()
    diag.run_all()
