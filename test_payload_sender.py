"""
Test Payload Sender
Simulates pothole detections with GPS coordinates and sends to mock API
"""

import requests
import json
import time
from datetime import datetime
import random

# Configuration
API_URL = "http://localhost:5000/api/report"
TIMEOUT = 5  # seconds

def generate_test_payload(test_num=1, latitude=None, longitude=None, include_gps=True):
    """Generate a realistic detection payload with optional GPS data"""
    
    if latitude is None:
        # Random coordinates for demo (Bangalore, India region as example)
        latitude = 12.9716 + random.uniform(-0.1, 0.1)
    if longitude is None:
        longitude = 77.5946 + random.uniform(-0.1, 0.1)
    
    payload = {
        'timestamp': datetime.now().isoformat(),
        'class': 'pothole',
        'severity': random.choice(['Low', 'Medium', 'High']),
        'confidence': round(random.uniform(0.75, 0.99), 3),
        'image_path': f'/detections/pothole_{test_num}_{datetime.now().timestamp()}.jpg',
    }
    
    if include_gps:
        payload.update({
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'gps_timestamp': datetime.now().isoformat(),
            'gps_quality': random.choice([1, 2, 3, 4])  # 1=GPS, 2=DGPS, 3=PPS, 4=RTK
        })
    
    return payload

def send_payload(payload, verbose=True):
    """Send payload to API"""
    try:
        if verbose:
            print("\n" + "="*70)
            print(f"Sending Payload #{len(payload.get('timestamp', ''))}...")
            print("="*70)
            print(json.dumps(payload, indent=2))
            print("-"*70)
        
        response = requests.post(
            API_URL,
            json=payload,
            timeout=TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ SUCCESS - API Response: {result}")
            if result.get('gps_received'):
                print(f"✓ GPS Coordinates Accepted:")
                print(f"    Latitude:  {payload.get('latitude')}")
                print(f"    Longitude: {payload.get('longitude')}")
            return True
        else:
            print(f"✗ FAILED - Status {response.status_code}: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ CONNECTION ERROR - Is mock API server running on localhost:5000?")
        print("  Start it with: python mock_api_server.py")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def run_test_sequence(num_payloads=3, include_gps=True):
    """Run a sequence of test payloads"""
    print("\n" + "="*70)
    print("POTHOLE DETECTION PAYLOAD TEST")
    print("="*70)
    print(f"Sending {num_payloads} test payloads...")
    print(f"GPS Data Included: {'Yes' if include_gps else 'No'}")
    print("="*70)
    
    # Health check
    try:
        resp = requests.get("http://localhost:5000/health", timeout=TIMEOUT)
        if resp.status_code == 200:
            print("✓ Mock API Server is running")
        else:
            print("✗ Mock API Server not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Mock API Server on localhost:5000")
        print("  Start it with: python mock_api_server.py")
        return
    
    # Send test payloads
    success_count = 0
    for i in range(num_payloads):
        payload = generate_test_payload(
            test_num=i+1,
            include_gps=include_gps
        )
        
        if send_payload(payload):
            success_count += 1
        
        if i < num_payloads - 1:
            print("\nWaiting before next payload...")
            time.sleep(1)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Payloads Sent:    {num_payloads}")
    print(f"Successful:       {success_count}")
    print(f"Failed:           {num_payloads - success_count}")
    print("="*70)
    
    if success_count == num_payloads:
        print("✓ ALL TESTS PASSED - Payloads with GPS reaching API successfully")
    else:
        print("✗ SOME TESTS FAILED - Check API server logs")

if __name__ == "__main__":
    import sys
    
    # Parse command-line arguments
    num_payloads = 3
    include_gps = True
    
    if '--no-gps' in sys.argv:
        include_gps = False
    
    if '--count' in sys.argv:
        idx = sys.argv.index('--count')
        if idx + 1 < len(sys.argv):
            num_payloads = int(sys.argv[idx + 1])
    
    run_test_sequence(num_payloads=num_payloads, include_gps=include_gps)
