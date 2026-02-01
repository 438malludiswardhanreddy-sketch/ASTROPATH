"""
ASTROPATH API Client Module (api_client.py)
Handle communication with cloud backend for detection data upload and status tracking
"""

import os
import sys
import requests
import json
import base64
from datetime import datetime
from typing import Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger

logger = setup_logger(__name__)


class APIClient:
    """Client for communicating with ASTROPATH cloud backend"""
    
    def __init__(self, base_url=config.API_URL, timeout=config.API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        logger.info(f"APIClient initialized: {base_url}")
    
    def _check_connectivity(self) -> bool:
        """Check if API is reachable"""
        try:
            response = self.session.head(self.base_url, timeout=5)
            logger.info(f"API connectivity check: {response.status_code}")
            return response.status_code < 500
        except Exception as e:
            logger.error(f"API connectivity check failed: {e}")
            return False
    
    def report_detection(self, detection_data: Dict) -> Tuple[bool, Dict]:
        """
        Report a pothole detection to the API
        
        Args:
            detection_data: Dictionary containing detection info
                {
                    'latitude': float,
                    'longitude': float,
                    'severity': str ('Low', 'Medium', 'High'),
                    'confidence': float,
                    'class': str,
                    'image_path': str or 'image_base64': str,
                    'timestamp': str
                }
        
        Returns:
            (success: bool, response_data: dict)
        """
        try:
            # Prepare payload
            payload = {
                'timestamp': detection_data.get('timestamp', datetime.now().isoformat()),
                'latitude': float(detection_data.get('latitude', 0)),
                'longitude': float(detection_data.get('longitude', 0)),
                'severity': detection_data.get('severity', 'Unknown'),
                'confidence': float(detection_data.get('confidence', 0)),
                'class': detection_data.get('class', 'pothole'),
            }
            
            # Handle image (either file path or base64)
            image_data = None
            if 'image_base64' in detection_data:
                image_data = detection_data['image_base64']
            elif 'image_path' in detection_data and os.path.exists(detection_data['image_path']):
                # Read and encode image as base64
                with open(detection_data['image_path'], 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            
            if image_data:
                payload['image_base64'] = image_data
            
            logger.debug(f"Sending detection: {payload}")
            
            # Send request
            response = self.session.post(
                f"{self.base_url}/report",
                json=payload,
                timeout=self.timeout
            )
            
            # Handle response
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Detection reported successfully: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {"status": "success"}
            else:
                logger.warning(f"API error: {response.status_code} - {response.text}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to report detection: {e}")
            return False, {"error": str(e)}
    
    def update_repair_status(self, detection_id: str, status: str, notes: str = "") -> Tuple[bool, Dict]:
        """
        Update repair status for a reported pothole
        
        Args:
            detection_id: Unique ID of the detection
            status: 'pending', 'in_progress', 'completed', 'rejected'
            notes: Optional notes about the repair
        
        Returns:
            (success: bool, response_data: dict)
        """
        try:
            payload = {
                'detection_id': detection_id,
                'status': status,
                'notes': notes,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Updating repair status: {detection_id} -> {status}")
            
            response = self.session.post(
                f"{self.base_url}/update-status",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Status updated: {status}")
                return True, response.json()
            else:
                logger.warning(f"Status update failed: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            return False, {"error": str(e)}
    
    def get_detection_by_id(self, detection_id: str) -> Tuple[bool, Dict]:
        """Retrieve detection details from API"""
        try:
            response = self.session.get(
                f"{self.base_url}/detection/{detection_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Retrieved detection: {detection_id}")
                return True, response.json()
            else:
                logger.warning(f"Failed to retrieve detection: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to get detection: {e}")
            return False, {"error": str(e)}
    
    def get_recent_detections(self, limit: int = 50, offset: int = 0) -> Tuple[bool, Dict]:
        """Get recent detections from API"""
        try:
            params = {'limit': limit, 'offset': offset}
            response = self.session.get(
                f"{self.base_url}/detections",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Retrieved {limit} detections")
                return True, response.json()
            else:
                logger.warning(f"Failed to retrieve detections: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to get detections: {e}")
            return False, {"error": str(e)}
    
    def get_heatmap_data(self, bounds: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        Get heatmap data for dashboard visualization
        
        Args:
            bounds: Optional map bounds {'north', 'south', 'east', 'west'}
        
        Returns:
            (success: bool, heatmap_data: dict)
        """
        try:
            params = bounds or {}
            response = self.session.get(
                f"{self.base_url}/heatmap",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info("Retrieved heatmap data")
                return True, response.json()
            else:
                logger.warning(f"Failed to retrieve heatmap: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to get heatmap: {e}")
            return False, {"error": str(e)}
    
    def request_drone_inspection(self, latitude: float, longitude: float, priority: str = "medium") -> Tuple[bool, Dict]:
        """
        Request drone inspection for a specific location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            priority: 'low', 'medium', 'high'
        
        Returns:
            (success: bool, inspection_data: dict)
        """
        try:
            payload = {
                'latitude': latitude,
                'longitude': longitude,
                'priority': priority,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Requesting drone inspection at ({latitude}, {longitude})")
            
            response = self.session.post(
                f"{self.base_url}/request-drone",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info("Drone inspection requested")
                return True, response.json()
            else:
                logger.warning(f"Drone request failed: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to request drone: {e}")
            return False, {"error": str(e)}
    
    def submit_citizen_report(self, latitude: float, longitude: float, 
                             description: str = "", image_path: str = "") -> Tuple[bool, Dict]:
        """
        Submit a citizen report via the API
        
        Args:
            latitude: Report location latitude
            longitude: Report location longitude
            description: Description of the issue
            image_path: Path to citizen-submitted image
        
        Returns:
            (success: bool, report_data: dict)
        """
        try:
            payload = {
                'latitude': latitude,
                'longitude': longitude,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'source': 'citizen_app'
            }
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    payload['image_base64'] = base64.b64encode(f.read()).decode('utf-8')
            
            logger.info(f"Submitting citizen report at ({latitude}, {longitude})")
            
            response = self.session.post(
                f"{self.base_url}/citizen-report",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info("Citizen report submitted")
                return True, response.json()
            else:
                logger.warning(f"Report submission failed: {response.status_code}")
                return False, {"error": response.text}
        
        except Exception as e:
            logger.error(f"Failed to submit citizen report: {e}")
            return False, {"error": str(e)}
    
    def get_api_status(self) -> Tuple[bool, Dict]:
        """Check API status"""
        try:
            response = self.session.get(
                f"{self.base_url}/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": "API unavailable"}
        
        except Exception as e:
            logger.error(f"API status check failed: {e}")
            return False, {"error": str(e)}


def test_api():
    """Test API connectivity and basic operations"""
    logger.info("="*60)
    logger.info("Testing ASTROPATH API Client")
    logger.info("="*60)
    
    client = APIClient()
    
    # Check connectivity
    if not client._check_connectivity():
        logger.error("API is not reachable. Please configure API_URL in config.py")
        return
    
    # Check API status
    success, data = client.get_api_status()
    if success:
        logger.info(f"API Status: {data}")
    else:
        logger.warning(f"Could not get API status: {data}")
    
    # Test detection report (mock data)
    test_detection = {
        'latitude': 17.3629,
        'longitude': 75.8930,
        'severity': 'High',
        'confidence': 0.87,
        'class': 'pothole',
        'image_path': '',
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Sending test detection: {test_detection}")
    success, response = client.report_detection(test_detection)
    logger.info(f"Response: {response}")


if __name__ == "__main__":
    test_api()
