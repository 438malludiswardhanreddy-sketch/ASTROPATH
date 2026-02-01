"""
ASTROPATH Citizen Upload Module (citizen_upload.py)
Flask-based web app for citizen reporting with image upload and geolocation
"""

import os
import sys
import json
from datetime import datetime
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger, ensure_dir_exists, get_timestamp
from src.api_client import APIClient

logger = setup_logger(__name__)

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from werkzeug.utils import secure_filename
    import logging as flask_logging
    
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not installed. Install with: pip install flask")


class CitizenReportingApp:
    """Flask web app for citizen pothole reporting"""
    
    def __init__(self, host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG):
        if not FLASK_AVAILABLE:
            raise RuntimeError("Flask not installed")
        
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
        self.app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
        
        ensure_dir_exists(config.UPLOAD_FOLDER)
        
        self.host = host
        self.port = port
        self.debug = debug
        self.api_client = APIClient()
        
        # Setup logging
        if not debug:
            flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)
        
        self._register_routes()
        logger.info(f"CitizenReportingApp initialized: {host}:{port}")
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Home page - serve HTML form"""
            return self._render_html()
        
        @self.app.route('/api/report', methods=['POST'])
        def submit_report():
            """API endpoint for citizen report submission"""
            try:
                # Get form data
                latitude = request.form.get('latitude', '0')
                longitude = request.form.get('longitude', '0')
                description = request.form.get('description', '')
                
                # Parse coordinates
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                except ValueError:
                    return jsonify({'error': 'Invalid coordinates'}), 400
                
                # Handle file upload
                image_path = None
                if 'image' in request.files:
                    file = request.files['image']
                    if file.filename:
                        filename = secure_filename(f"{get_timestamp()}_{file.filename}")
                        file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        image_path = file_path
                        logger.info(f"Image saved: {file_path}")
                
                # Submit to API
                success, response = self.api_client.submit_citizen_report(
                    latitude=latitude,
                    longitude=longitude,
                    description=description,
                    image_path=image_path or ''
                )
                
                if success:
                    logger.info(f"Citizen report submitted: ({latitude}, {longitude})")
                    return jsonify({
                        'success': True,
                        'message': 'Report submitted successfully',
                        'data': response
                    }), 200
                else:
                    logger.warning(f"Report submission failed: {response}")
                    return jsonify({
                        'success': False,
                        'message': 'Failed to submit report',
                        'error': response.get('error', 'Unknown error')
                    }), 500
            
            except Exception as e:
                logger.error(f"Error in report submission: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/reports', methods=['GET'])
        def get_reports():
            """Get recent reports"""
            try:
                limit = request.args.get('limit', 50, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                success, data = self.api_client.get_recent_detections(limit, offset)
                
                if success:
                    return jsonify({'success': True, 'data': data}), 200
                else:
                    return jsonify({'success': False, 'error': data.get('error')}), 500
            
            except Exception as e:
                logger.error(f"Error fetching reports: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/heatmap', methods=['GET'])
        def get_heatmap():
            """Get heatmap data for map visualization"""
            try:
                north = request.args.get('north', type=float)
                south = request.args.get('south', type=float)
                east = request.args.get('east', type=float)
                west = request.args.get('west', type=float)
                
                bounds = None
                if all([north, south, east, west]):
                    bounds = {'north': north, 'south': south, 'east': east, 'west': west}
                
                success, data = self.api_client.get_heatmap_data(bounds)
                
                if success:
                    return jsonify({'success': True, 'data': data}), 200
                else:
                    return jsonify({'success': False, 'error': data.get('error')}), 500
            
            except Exception as e:
                logger.error(f"Error fetching heatmap: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/uploads/<filename>', methods=['GET'])
        def download_file(filename):
            """Serve uploaded files"""
            try:
                return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)
            except:
                return jsonify({'error': 'File not found'}), 404
        
        @self.app.route('/api/status', methods=['GET'])
        def api_status():
            """Check API status"""
            success, data = self.api_client.get_api_status()
            return jsonify({'success': success, 'data': data}), 200 if success else 500
    
    def _render_html(self):
        """Render HTML form for citizen reporting"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTROPATH - Citizen Pothole Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 30px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        
        input[type="text"],
        input[type="number"],
        input[type="file"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        
        input[type="text"]:focus,
        input[type="number"]:focus,
        input[type="file"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .button-secondary {
            background: #f0f0f0;
            color: #333;
            margin-top: 10px;
        }
        
        .button-secondary:hover {
            background: #e0e0e0;
            box-shadow: none;
        }
        
        .alert {
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        
        .coordinates {
            display: flex;
            gap: 10px;
        }
        
        .coordinates input {
            flex: 1;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-size: 14px;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .info-text {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 ASTROPATH</h1>
            <p>Smart Road Damage Reporting System</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <form id="reportForm">
            <div class="coordinates">
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                    <label for="latitude">Latitude</label>
                    <input type="number" id="latitude" name="latitude" step="0.0001" placeholder="17.3629" required>
                </div>
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                    <label for="longitude">Longitude</label>
                    <input type="number" id="longitude" name="longitude" step="0.0001" placeholder="75.8930" required>
                </div>
            </div>
            <button type="button" id="getLocationBtn" class="button-secondary">📍 Get My Location</button>
            
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" placeholder="Describe the road damage (optional)"></textarea>
                <div class="info-text">Be specific about the damage type and severity</div>
            </div>
            
            <div class="form-group">
                <label for="image">Photo</label>
                <input type="file" id="image" name="image" accept="image/*">
                <div class="info-text">Upload a photo of the damage (max 5MB)</div>
            </div>
            
            <button type="submit">📤 Submit Report</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Submitting report...</p>
            </div>
        </form>
    </div>
    
    <script>
        const form = document.getElementById('reportForm');
        const alert = document.getElementById('alert');
        const loading = document.getElementById('loading');
        const getLocationBtn = document.getElementById('getLocationBtn');
        
        // Get user location
        getLocationBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                getLocationBtn.disabled = true;
                getLocationBtn.textContent = '📍 Getting location...';
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        document.getElementById('latitude').value = position.coords.latitude.toFixed(4);
                        document.getElementById('longitude').value = position.coords.longitude.toFixed(4);
                        getLocationBtn.disabled = false;
                        getLocationBtn.textContent = '📍 Get My Location';
                        showAlert('Location obtained successfully', 'success');
                    },
                    function(error) {
                        getLocationBtn.disabled = false;
                        getLocationBtn.textContent = '📍 Get My Location';
                        showAlert('Unable to get location: ' + error.message, 'error');
                    }
                );
            } else {
                showAlert('Geolocation not supported by this browser', 'error');
            }
        });
        
        // Form submission
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            loading.classList.add('show');
            
            try {
                const response = await fetch('/api/report', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                loading.classList.remove('show');
                
                if (result.success) {
                    showAlert('✓ Report submitted successfully! Thank you for reporting.', 'success');
                    form.reset();
                } else {
                    showAlert('✗ Error: ' + (result.error || result.message), 'error');
                }
            } catch (error) {
                loading.classList.remove('show');
                showAlert('✗ Network error: ' + error.message, 'error');
            }
        });
        
        function showAlert(message, type) {
            alert.textContent = message;
            alert.className = 'alert ' + type;
            setTimeout(() => {
                alert.className = 'alert';
            }, 5000);
        }
    </script>
</body>
</html>
        """
        return html
    
    def run(self):
        """Start the Flask app"""
        logger.info(f"Starting ASTROPATH Citizen Reporting App on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)


def main():
    """Main entry point"""
    if not FLASK_AVAILABLE:
        logger.error("Flask is required. Install with: pip install flask")
        return
    
    app = CitizenReportingApp()
    app.run()


if __name__ == "__main__":
    main()
