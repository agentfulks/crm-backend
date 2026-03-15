#!/usr/bin/env python3
"""Process Daily Queue cards in detail"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')
BOARD_ID = "699d2728fd2ae8c35d1f7a24"

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

# Get Daily Queue list
lists = api_request(f"/boards/{BOARD_ID}/lists")
daily_queue_list = None
for lst in lists:
    if lst.get('name') == 'Daily Queue':
        daily_queue_list = lst
        break

if not daily_queue_list:
    print("Daily Queue list not found")
    exit(1)

# Get cards in Daily Queue
cards = api_request(f"/lists/{daily_queue_list['id']}/cards")

print("=" * 70)
print("DAILY QUEUE - CARDS NEEDING PROCESSING")
print("=" * 70)

# Separate VC cards from ops cards
vc_cards = []
ops_cards = []

for card in cards:
    name = card.get('name', '')
    desc = card.get('desc', '')
    labels = card.get('labels', [])
    
    # Check if it's a VC card
    if '[VC]' in name or any(l.get('name') == 'Outreach' for l in labels) or 'Partner' in name or 'Managing' in name:
        vc_cards.append(card)
    else:
        ops_cards.append(card)

print(f"\n🔴 VC OUTREACH CARDS ({len(vc_cards)}):")
print("-" * 70)
for card in vc_cards:
    name = card.get('name', '')
    desc = card.get('desc', '')[:200] if card.get('desc') else ''
    labels = [l.get('name') for l in card.get('labels', []) if l.get('name')]
    
    print(f"\n• {name}")
    if labels:
        print(f"  Labels: {', '.join(labels)}")
    if desc:
        print(f"  Desc: {desc[:150]}...")

print(f"\n\n🔧 OPS/INFRA CARDS ({len(ops_cards)}):")
print("-" * 70)
for card in ops_cards:
    name = card.get('name', '')
    labels = [l.get('name') for l in card.get('labels', []) if l.get('name')]
    
    print(f"\n• {name}")
    if labels:
        print(f"  Labels: {', '.join(labels)}")
