import urllib.request
import json

url = 'http://127.0.0.1:8088/api/services'
payload = {
    "ownerName": "Test Lib Fixed",
    "bikeModel": "Kawasaki Ninja",
    "plateNumber": "K1-333",
    "issueDescription": "Revision 1000km",
    "status": "Pendiente"
}

try:
    print(f"INFO: POSTing to {url}...")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        body = response.read().decode('utf-8')
        print(f"INFO: Status: {status}")
        print(f"INFO: Response: {body}")
except Exception as e:
    print(f"ERROR: {e}")
