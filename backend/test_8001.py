import requests
import json

url = "http://127.0.0.1:8001/api/video/process"
payload = {"url": "https://www.youtube.com/watch?v=kqtD5dpn9C8"}
headers = {"Content-Type": "application/json"}

print(f"Testing POST to {url}...")
try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

url_slash = "http://127.0.0.1:8001/api/video/process/"
print(f"\nTesting POST to {url_slash}...")
try:
    response = requests.post(url_slash, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
