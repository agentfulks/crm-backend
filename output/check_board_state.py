#!/usr/bin/env python3
"""Check current state of VC Outreach Engine Trello board"""
import sys
sys.path.insert(0, '/data/workspace/vc-outreach/automation')

from trello_client import TrelloClient

# Initialize client
client = TrelloClient(
    gateway_url="https://gateway.maton.ai/trello",
    api_key="2xeebNVm749KETi48PqXsENA7wAxo4UXcM-MHhcs2DAZ3ASnR-r8eLgB72QwFU0X_tMKOL71XLhIpFSWHiHAHbJ4-wUM3FGW-dICnjhbaA"
)

BOARD_ID = "699d2728fd2ae8c35d1f7a24"

print("=" * 60)
print("VC OUTREACH ENGINE - TRELLO BOARD STATUS")
print("=" * 60)

# Get board info
board = client.get_board(BOARD_ID)
print(f"\nBoard: {board.get('name')}")
print(f"URL: {board.get('url')}")
print(f"ID: {board.get('id')}")

# Get all lists
lists = client.get_lists(BOARD_ID)
print(f"\n{'='*60}")
print("LISTS AND CARDS")
print("=" * 60)

total_cards = 0
for lst in lists:
    list_name = lst.get('name')
    list_id = lst.get('id')
    cards = client.get_cards_in_list(list_id)
    card_count = len(cards)
    total_cards += card_count
    
    print(f"\n📋 {list_name} ({card_count} cards)")
    print("-" * 40)
    
    for card in cards[:10]:  # Show first 10 cards
        labels = [l.get('name', l.get('color', 'unknown')) for l in card.labels]
        label_str = f" [{', '.join(labels)}]" if labels else ""
        print(f"  • {card.name[:60]}{label_str}")
        if len(card.name) > 60:
            print(f"    ...{card.name[60:80]}")
    
    if card_count > 10:
        print(f"  ... and {card_count - 10} more")

print(f"\n{'='*60}")
print(f"TOTAL CARDS: {total_cards}")
print("=" * 60)
