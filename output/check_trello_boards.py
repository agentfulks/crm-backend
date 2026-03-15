#!/usr/bin/env python3
"""Check available Trello boards via Maton API"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')

url = "https://api.maton.ai/v1/trello/boards"
headers = {"Authorization": f"Bearer {MATON_API_KEY}"}

req = urllib.request.Request(url, method="GET")
for key, val in headers.items():
    req.add_header(key, val)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        print("Available Trello Boards:")
        print("=" * 60)
        for board in result.get('boards', []):
            print(f"  • {board.get('name')} (ID: {board.get('id')})")
except Exception as e:
    print(f"Error: {e}")
    print("Response:", result if 'result' in dir() else "N/A")
