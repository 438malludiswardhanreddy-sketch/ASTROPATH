"""
Mock API Server for Testing Pothole Detection Payloads
Receives detection payloads and logs GPS coordinates
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/report', methods=['POST'])
def receive_detection():
    """Receive and log detection payload with GPS coordinates"""
    try:
        payload = request.get_json()
        
        # Log the full payload
        logger.info("=" * 70)
        logger.info("POTHOLE DETECTION RECEIVED")
        logger.info("=" * 70)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Full Payload: {json.dumps(payload, indent=2)}")
        
        # Extract and highlight GPS data
        if 'latitude' in payload and 'longitude' in payload:
            lat = payload.get('latitude')
            lon = payload.get('longitude')
            gps_quality = payload.get('gps_quality', 'unknown')
            gps_ts = payload.get('gps_timestamp', 'unknown')
            
            logger.info("-" * 70)
            logger.info("GPS COORDINATES:")
            logger.info(f"  Latitude:      {lat}")
            logger.info(f"  Longitude:     {lon}")
            logger.info(f"  Quality:       {gps_quality}")
            logger.info(f"  GPS Timestamp: {gps_ts}")
            logger.info("-" * 70)
        else:
            logger.warning("NO GPS DATA IN PAYLOAD")
        
        # Log detection details
        logger.info("Detection Details:")
        logger.info(f"  Class:         {payload.get('class', 'unknown')}")
        logger.info(f"  Severity:      {payload.get('severity', 'unknown')}")
        logger.info(f"  Confidence:    {payload.get('confidence', 'unknown')}")
        logger.info(f"  Image Path:    {payload.get('image_path', 'unknown')}")
        logger.info("=" * 70)
        
        # Return success response
        return jsonify({
            'status': 'success',
            'message': f'Detection received at {datetime.now().isoformat()}',
            'gps_received': 'latitude' in payload and 'longitude' in payload
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing payload: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Mock API server running'}), 200

if __name__ == '__main__':
    logger.info("Starting Mock API Server on http://localhost:5000")
    logger.info("Endpoints:")
    logger.info("  POST /api/report - Receive detection payloads")
    logger.info("  GET  /health - Health check")
    app.run(host='127.0.0.1', port=5000, debug=False)
