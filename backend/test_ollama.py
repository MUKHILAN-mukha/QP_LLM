import requests
import json

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": "hi", "stream": False},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json().get('response')}")
except Exception as e:
    print(f"Error: {e}")
