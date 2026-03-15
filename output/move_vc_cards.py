#!/usr/bin/env python3
"""Move VC cards from Daily Queue to Awaiting Approval"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')
BOARD_ID = "699d2728fd2ae8c35d1f7a24"

def api_request(path, method="GET", data=None):
    url = f"https://gateway.maton.ai/trello/1{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {MATON_API_KEY}")
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

# Get lists
lists = api_request(f"/boards/{BOARD_ID}/lists")
daily_queue_id = None
awaiting_approval_id = None

for lst in lists:
    name = lst.get('name')
    if name == 'Daily Queue':
        daily_queue_id = lst.get('id')
    elif name == 'Awaiting Approval':
        awaiting_approval_id = lst.get('id')

if not daily_queue_id or not awaiting_approval_id:
    print("Required lists not found")
    exit(1)

# Get cards in Daily Queue
cards = api_request(f"/lists/{daily_queue_id}/cards")

# Filter for VC cards (have partner names, fit scores, etc.)
vc_cards_to_move = []
for card in cards:
    name = card.get('name', '')
    desc = card.get('desc', '')
    # Skip ops/infra cards
    if any(x in name for x in ['API/', 'automation', 'workflow', 'asset inventory', 'scoring', 'model']):
        continue
    # Include VC cards
    if '[VC]' in name or 'Partner' in name or 'Managing' in name or 'Fit Score:' in desc:
        vc_cards_to_move.append(card)

print(f"Found {len(vc_cards_to_move)} VC cards to move from Daily Queue to Awaiting Approval")
print("\nCards being moved:")
for card in vc_cards_to_move:
    print(f"  • {card.get('name')[:60]}")

# Move cards
moved_count = 0
for card in vc_cards_to_move:
    card_id = card.get('id')
    result = api_request(f"/cards/{card_id}", method="PUT", data={"idList": awaiting_approval_id})
    if result:
        moved_count += 1

print(f"\n✅ Successfully moved {moved_count}/{len(vc_cards_to_move)} cards")
