"""
ASTROPATH Dashboard Module (dashboard.py)
Flask web server for real-time pothole detection visualization with GPS coordinates
Displays detection map, statistics, and repair tracking
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger
from src.database import DetectionDatabase

logger = setup_logger(__name__)


class DashboardServer:
    """Flask-based dashboard for pothole detection tracking"""
    
    def __init__(self, host: str = config.FLASK_HOST, 
                 port: int = config.FLASK_PORT,
                 db_path: str = "detections.db"):
        """
        Initialize dashboard server
        
        Args:
            host (str): Server host address
            port (int): Server port
            db_path (str): Path to detections database
        """
        self.host = host
        self.port = port
        self.db_path = db_path
        self.db = DetectionDatabase(db_path)
        
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['DEBUG'] = config.FLASK_DEBUG
        self.app.config['JSON_SORT_KEYS'] = False
        
        # Enable CORS
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Dashboard server initialized at {host}:{port}")
    
    def _setup_routes(self):
        """Register all routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/detections', methods=['GET'])
        def get_detections():
            """Get all detections or filtered by parameters"""
            try:
                limit = request.args.get('limit', 100, type=int)
                severity = request.args.get('severity', None)
                hours = request.args.get('hours', None, type=int)
                
                if severity:
                    detections = self.db.get_detections_by_severity(severity, limit)
                elif hours:
                    detections = self.db.get_recent_detections(hours, limit)
                else:
                    detections = self.db.get_all_detections(limit)
                
                return jsonify({
                    'status': 'success',
                    'count': len(detections),
                    'detections': detections
                })
            except Exception as e:
                logger.error(f"Error fetching detections: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/detections/<int:detection_id>', methods=['GET'])
        def get_detection(detection_id):
            """Get specific detection details"""
            try:
                detection = self.db.get_detection(detection_id)
                if detection:
                    return jsonify({
                        'status': 'success',
                        'detection': detection
                    })
                else:
                    return jsonify({'status': 'error', 'message': 'Detection not found'}), 404
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/detections/area', methods=['GET'])
        def get_detections_by_area():
            """Get detections within geographic area"""
            try:
                lat_min = request.args.get('lat_min', type=float)
                lat_max = request.args.get('lat_max', type=float)
                lon_min = request.args.get('lon_min', type=float)
                lon_max = request.args.get('lon_max', type=float)
                limit = request.args.get('limit', 100, type=int)
                
                if not all([lat_min, lat_max, lon_min, lon_max]):
                    return jsonify({'status': 'error', 'message': 'Missing area bounds'}), 400
                
                detections = self.db.get_detections_by_area(lat_min, lat_max, lon_min, lon_max, limit)
                
                return jsonify({
                    'status': 'success',
                    'count': len(detections),
                    'detections': detections
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/detections', methods=['POST'])
        def add_detection():
            """Add new detection"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required = ['timestamp', 'latitude', 'longitude', 'severity', 'confidence']
                if not all(field in data for field in required):
                    return jsonify({
                        'status': 'error',
                        'message': f'Missing required fields: {required}'
                    }), 400
                
                detection_id = self.db.add_detection(data)
                
                if detection_id > 0:
                    logger.info(f"New detection added via API: ID {detection_id}")
                    return jsonify({
                        'status': 'success',
                        'detection_id': detection_id,
                        'message': 'Detection recorded'
                    }), 201
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to add detection'}), 500
            
            except Exception as e:
                logger.error(f"Error adding detection: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/detections/<int:detection_id>/status', methods=['PUT'])
        def update_repair_status(detection_id):
            """Update repair status of detection"""
            try:
                data = request.get_json()
                status = data.get('status')
                notes = data.get('notes', '')
                
                if not status:
                    return jsonify({'status': 'error', 'message': 'Status required'}), 400
                
                success = self.db.update_repair_status(detection_id, status, notes)
                
                if success:
                    return jsonify({
                        'status': 'success',
                        'message': f'Detection {detection_id} status updated to {status}'
                    })
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to update status'}), 500
            
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Get dashboard statistics"""
            try:
                days = request.args.get('days', 30, type=int)
                stats = self.db.get_statistics(days)
                
                return jsonify({
                    'status': 'success',
                    'statistics': stats
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/heatmap', methods=['GET'])
        def get_heatmap():
            """Get heatmap data for map visualization"""
            try:
                limit = request.args.get('limit', 500, type=int)
                heatmap_data = self.db.get_heatmap_data(limit)
                
                return jsonify({
                    'status': 'success',
                    'count': len(heatmap_data),
                    'data': heatmap_data
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """API health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'ASTROPATH Dashboard',
                'version': '1.0'
            })
        
        logger.info("Dashboard routes registered successfully")
    
    def run(self, debug: bool = False):
        """Start the dashboard server"""
        logger.info(f"Starting dashboard server on {self.host}:{self.port}")
        logger.info(f"Access dashboard at: http://{self.host}:{self.port}")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug,
            use_reloader=False
        )
    
    def stop(self):
        """Stop the server and close database"""
        self.db.close()
        logger.info("Dashboard server stopped")


def create_app(db_path: str = "detections.db"):
    """Factory function to create Flask app"""
    dashboard = DashboardServer(db_path=db_path)
    return dashboard.app


# ==================== Standalone Execution ====================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("🌐 ASTROPATH Dashboard Server 🌐")
    print("="*60)
    
    dashboard = DashboardServer(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        db_path=os.path.join(config.BASE_DIR, "detections.db")
    )
    
    print(f"\n✓ Dashboard running at: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("✓ Press Ctrl+C to stop\n")
    
    try:
        dashboard.run(debug=config.FLASK_DEBUG)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        dashboard.stop()
