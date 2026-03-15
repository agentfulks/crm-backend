#!/usr/bin/env python3
"""Find and check BDR Game Studios Trello board"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')

def api_request(path):
    url = f"https://gateway.maton.ai/trello/1{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {MATON_API_KEY}")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

# Get all boards for the user
boards = api_request("/members/me/boards")
if not boards:
    print("Failed to fetch boards")
    exit(1)

print("=" * 60)
print("AVAILABLE TRELLO BOARDS")
print("=" * 60)

for board in boards:
    print(f"\n• {board.get('name')}")
    print(f"  ID: {board.get('id')}")
    print(f"  URL: {board.get('url')}")
