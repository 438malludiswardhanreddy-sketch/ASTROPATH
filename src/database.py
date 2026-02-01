"""
ASTROPATH Database Module (database.py)
SQLite database for storing pothole detections with GPS coordinates, timestamps, and severity
Provides CRUD operations and query capabilities for dashboard integration
"""

import sqlite3
import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DetectionDatabase:
    """
    SQLite database manager for pothole detections
    Stores location data, timestamps, severity, and images
    """
    
    def __init__(self, db_path: str = "detections.db"):
        """
        Initialize database connection
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            cursor = self.conn.cursor()
            
            # Main detections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    class_name TEXT NOT NULL,
                    image_path TEXT,
                    image_base64 TEXT,
                    camera_source TEXT,
                    gps_quality INTEGER,
                    repair_status TEXT DEFAULT 'pending',
                    repair_date TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # GPS quality levels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gps_quality_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    quality INTEGER,
                    num_satellites INTEGER,
                    hdop REAL,
                    vdop REAL,
                    pdop REAL,
                    fix_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Repair tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS repairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_id INTEGER NOT NULL,
                    repair_date TEXT NOT NULL,
                    repair_crew TEXT,
                    cost REAL,
                    before_image TEXT,
                    after_image TEXT,
                    notes TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(detection_id) REFERENCES detections(id)
                )
            ''')
            
            # Analytics table for dashboard summary
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    total_detections INTEGER DEFAULT 0,
                    high_severity_count INTEGER DEFAULT 0,
                    medium_severity_count INTEGER DEFAULT 0,
                    low_severity_count INTEGER DEFAULT 0,
                    avg_confidence REAL,
                    repairs_completed INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON detections(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON detections(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_gps_location ON detections(latitude, longitude)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_repair_status ON detections(repair_status)')
            
            self.conn.commit()
            logger.info(f"Database initialized: {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_detection(self, detection_data: Dict) -> int:
        """
        Add a pothole detection to database
        
        Args:
            detection_data (dict): Detection information
                {
                    'timestamp': str,
                    'latitude': float,
                    'longitude': float,
                    'severity': str ('Low', 'Medium', 'High'),
                    'confidence': float (0-1),
                    'class_name': str (default 'pothole'),
                    'image_path': str (optional),
                    'image_base64': str (optional),
                    'camera_source': str (optional),
                    'gps_quality': int (optional, 0-8)
                }
        
        Returns:
            int: ID of inserted record
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO detections 
                (timestamp, latitude, longitude, severity, confidence, class_name, 
                 image_path, image_base64, camera_source, gps_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection_data.get('timestamp'),
                detection_data.get('latitude'),
                detection_data.get('longitude'),
                detection_data.get('severity', 'Unknown'),
                detection_data.get('confidence', 0.0),
                detection_data.get('class_name', 'pothole'),
                detection_data.get('image_path'),
                detection_data.get('image_base64'),
                detection_data.get('camera_source'),
                detection_data.get('gps_quality', 0)
            ))
            
            self.conn.commit()
            detection_id = cursor.lastrowid
            
            logger.info(f"Detection added (ID: {detection_id}): "
                       f"({detection_data.get('latitude'):.4f}, {detection_data.get('longitude'):.4f}) "
                       f"Severity: {detection_data.get('severity')}")
            
            return detection_id
        
        except Exception as e:
            logger.error(f"Error adding detection: {e}")
            return -1
    
    def add_gps_log(self, gps_data: Dict) -> int:
        """
        Log GPS reading for debugging and quality tracking
        
        Args:
            gps_data (dict): GPS information
                {
                    'timestamp': str,
                    'latitude': float,
                    'longitude': float,
                    'quality': int,
                    'num_satellites': int (optional),
                    'hdop': float (optional),
                    'vdop': float (optional),
                    'pdop': float (optional),
                    'fix_type': str (optional)
                }
        
        Returns:
            int: ID of inserted record
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO gps_quality_log 
                (timestamp, latitude, longitude, quality, num_satellites, hdop, vdop, pdop, fix_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gps_data.get('timestamp'),
                gps_data.get('latitude'),
                gps_data.get('longitude'),
                gps_data.get('quality', 0),
                gps_data.get('num_satellites'),
                gps_data.get('hdop'),
                gps_data.get('vdop'),
                gps_data.get('pdop'),
                gps_data.get('fix_type')
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        
        except Exception as e:
            logger.error(f"Error logging GPS data: {e}")
            return -1
    
    def get_detection(self, detection_id: int) -> Optional[Dict]:
        """Get single detection by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM detections WHERE id = ?', (detection_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching detection: {e}")
            return None
    
    def get_detections_by_area(self, lat_min: float, lat_max: float, 
                               lon_min: float, lon_max: float,
                               limit: int = 100) -> List[Dict]:
        """
        Get detections within geographic area
        
        Args:
            lat_min, lat_max: Latitude range
            lon_min, lon_max: Longitude range
            limit: Max results
        
        Returns:
            List of detection dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detections 
                WHERE latitude BETWEEN ? AND ? 
                  AND longitude BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (lat_min, lat_max, lon_min, lon_max, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error fetching detections by area: {e}")
            return []
    
    def get_detections_by_severity(self, severity: str, 
                                   limit: int = 100) -> List[Dict]:
        """Get detections filtered by severity level"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detections 
                WHERE severity = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (severity, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error fetching detections by severity: {e}")
            return []
    
    def get_recent_detections(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get detections from last N hours"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detections 
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (hours, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error fetching recent detections: {e}")
            return []
    
    def get_all_detections(self, limit: int = 1000) -> List[Dict]:
        """Get all detections with optional limit"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detections 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error fetching all detections: {e}")
            return []
    
    def update_repair_status(self, detection_id: int, status: str, notes: str = "") -> bool:
        """
        Update repair status of a detection
        
        Args:
            detection_id (int): Detection ID
            status (str): 'pending', 'in_progress', 'completed', 'rejected'
            notes (str): Additional notes
        
        Returns:
            bool: Success status
        """
        try:
            cursor = self.conn.cursor()
            
            repair_date = None if status == 'pending' else datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE detections 
                SET repair_status = ?, repair_date = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, repair_date, notes, detection_id))
            
            self.conn.commit()
            logger.info(f"Detection {detection_id} repair status updated to: {status}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating repair status: {e}")
            return False
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get dashboard statistics for specified period
        
        Args:
            days (int): Number of days to analyze
        
        Returns:
            Dict with statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Total detections
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high,
                       SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium,
                       SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) as low,
                       AVG(confidence) as avg_confidence
                FROM detections 
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            stats_row = cursor.fetchone()
            
            cursor.execute('''
                SELECT COUNT(*) as total FROM detections 
                WHERE repair_status = 'completed'
                  AND datetime(repair_date) > datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            repairs_row = cursor.fetchone()
            
            stats = {
                'total_detections': stats_row[0] or 0,
                'high_severity': stats_row[1] or 0,
                'medium_severity': stats_row[2] or 0,
                'low_severity': stats_row[3] or 0,
                'avg_confidence': stats_row[4] or 0,
                'repairs_completed': repairs_row[0] or 0,
                'pending_repairs': (stats_row[0] or 0) - (repairs_row[0] or 0)
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_heatmap_data(self, limit: int = 500) -> List[Dict]:
        """
        Get data formatted for heatmap visualization
        
        Returns:
            List of {latitude, longitude, severity_level}
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT latitude, longitude, severity 
                FROM detections 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            heatmap = []
            severity_weights = {'Low': 1, 'Medium': 5, 'High': 10}
            
            for row in cursor.fetchall():
                heatmap.append({
                    'latitude': row[0],
                    'longitude': row[1],
                    'severity': row[2],
                    'weight': severity_weights.get(row[2], 1)
                })
            
            return heatmap
        
        except Exception as e:
            logger.error(f"Error getting heatmap data: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ==================== Standalone Testing ====================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Database Module Test\n")
    
    # Initialize database
    db = DetectionDatabase("test_detections.db")
    
    # Add sample detections
    print("Adding sample detections...")
    
    detections = [
        {
            'timestamp': datetime.now().isoformat(),
            'latitude': 17.3590,
            'longitude': 73.8580,
            'severity': 'High',
            'confidence': 0.95,
            'class_name': 'pothole',
            'camera_source': 'main_camera',
            'gps_quality': 2
        },
        {
            'timestamp': datetime.now().isoformat(),
            'latitude': 17.3595,
            'longitude': 73.8585,
            'severity': 'Medium',
            'confidence': 0.87,
            'class_name': 'pothole',
            'camera_source': 'secondary_camera',
            'gps_quality': 1
        }
    ]
    
    for detection in detections:
        db.add_detection(detection)
    
    # Query detections
    print("\nFetching detections...")
    all_detections = db.get_all_detections()
    for det in all_detections:
        print(f"  [{det['id']}] {det['severity']} @ ({det['latitude']:.4f}, {det['longitude']:.4f})")
    
    # Get statistics
    print("\nDatabase Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get heatmap data
    print("\nHeatmap Data:")
    heatmap = db.get_heatmap_data()
    for point in heatmap:
        print(f"  ({point['latitude']:.4f}, {point['longitude']:.4f}) - {point['severity']}")
    
    db.close()
    print("\nTest completed")
