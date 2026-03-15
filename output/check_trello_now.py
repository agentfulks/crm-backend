#!/usr/bin/env python3
"""Quick Trello board state check via Maton API"""
import os
import json
import urllib.request
import urllib.error

MATON_API_KEY = os.environ.get('MATON_API_KEY', '2xeebNVm749KETi48PqXsENA7wAxo4UXcM-MHhcs2DAZ3ASnR-r8eLgB72QwFU0X_tMKOL71XLhIpFSWHiHAHbJ4-wUM3FGW-dICnjhbaA')

def maton_request(endpoint, method="GET", data=None):
    url = f"https://api.maton.ai/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {MATON_API_KEY}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, method=method)
    for key, val in headers.items():
        req.add_header(key, val)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}

# Get boards
result = maton_request("trello/boards")
print(json.dumps(result, indent=2))
