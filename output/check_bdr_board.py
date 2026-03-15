#!/usr/bin/env python3
"""Check BDR Game Studios Trello board"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')
BOARD_ID = "699f37680e0b1bc16721ae44"

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

print("=" * 60)
print("BDR - GAME STUDIOS OUTREACH - BOARD STATUS")
print("=" * 60)

# Get board info
board = api_request(f"/boards/{BOARD_ID}")
if not board:
    print("Failed to fetch board")
    exit(1)

print(f"\nBoard: {board.get('name')}")
print(f"URL: {board.get('url')}")

# Get all lists
lists = api_request(f"/boards/{BOARD_ID}/lists")
if not lists:
    print("Failed to fetch lists")
    exit(1)

print(f"\n{'='*60}")
print("LISTS AND CARDS")
print("=" * 60)

total_cards = 0
for lst in lists:
    list_name = lst.get('name')
    list_id = lst.get('id')
    
    cards = api_request(f"/lists/{list_id}/cards")
    card_count = len(cards) if cards else 0
    total_cards += card_count
    
    print(f"\n📋 {list_name} ({card_count} cards)")
    print("-" * 40)
    
    if cards:
        for card in cards[:10]:
            name = card.get('name', 'Untitled')
            print(f"  • {name[:70]}")
        
        if card_count > 10:
            print(f"  ... and {card_count - 10} more")

print(f"\n{'='*60}")
print(f"TOTAL CARDS: {total_cards}")
print("=" * 60)
