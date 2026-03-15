#!/usr/bin/env python3
"""Get final board states summary"""
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
        return None

# VC Board
vc_board_id = "699d2728fd2ae8c35d1f7a24"
vc_lists = api_request(f"/boards/{vc_board_id}/lists")

print("=" * 60)
print("VC OUTREACH ENGINE - FINAL STATE")
print("=" * 60)

vc_summary = {}
for lst in vc_lists:
    name = lst.get('name')
    cards = api_request(f"/lists/{lst.get('id')}/cards")
    count = len(cards) if cards else 0
    vc_summary[name] = count
    print(f"{name}: {count} cards")

# BDR Board
print("\n" + "=" * 60)
print("BDR - GAME STUDIOS OUTREACH - FINAL STATE")
print("=" * 60)

bdr_board_id = "699f37680e0b1bc16721ae44"
bdr_lists = api_request(f"/boards/{bdr_board_id}/lists")

bdr_summary = {}
for lst in bdr_lists:
    name = lst.get('name')
    cards = api_request(f"/lists/{lst.get('id')}/cards")
    count = len(cards) if cards else 0
    bdr_summary[name] = count
    print(f"{name}: {count} cards")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"\nVC Board Total: {sum(vc_summary.values())} cards")
print(f"BDR Board Total: {sum(bdr_summary.values())} cards")
print(f"Grand Total: {sum(vc_summary.values()) + sum(bdr_summary.values())} cards")
