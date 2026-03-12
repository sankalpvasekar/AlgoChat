import requests
import json

url = "http://localhost:8000/api/video/process/"
payload = {"url": "https://www.youtube.com/watch?v=kqtD5dpn9C8"}
headers = {"Content-Type": "application/json"}

print(f"Testing POST to {url}...")
try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS! Received Video ID: {data.get('video_id')}")
        print(f"Number of steps: {len(data.get('steps', []))}")
    else:
        print(f"Response Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
