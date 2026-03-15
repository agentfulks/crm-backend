#!/usr/bin/env python3
"""
Cycle 17 Trello Import Script
Imports VC and BDR cards to VC Outreach Engine board, Daily Queue list
"""

import csv
import os
import json
import urllib.request
import urllib.error
from datetime import datetime

# Configuration
MATON_API_KEY = os.environ.get('MATON_API_KEY')
BOARD_NAME = "VC Outreach Engine"
TARGET_LIST = "Daily Queue"

# File paths
VC_FILE = "/data/workspace/output/vc_packets_march04_import.csv"
BDR_FILE = "/data/workspace/output/bdr_studios_march04_import.csv"

def maton_api_request(endpoint, method="GET", data=None):
    """Make request to Maton API"""
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
        print(f"API Error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Request Error: {e}")
        return None

def get_board_and_list():
    """Find the board and list IDs"""
    print("🔍 Finding board and list...")
    
    # Get boards
    boards = maton_api_request("trello/boards")
    if not boards:
        print("❌ Failed to fetch boards")
        return None, None
    
    board_id = None
    for board in boards.get('boards', []):
        if board['name'] == BOARD_NAME:
            board_id = board['id']
            break
    
    if not board_id:
        print(f"❌ Board '{BOARD_NAME}' not found")
        return None, None
    
    print(f"✅ Found board: {BOARD_NAME} ({board_id})")
    
    # Get lists on board
    lists = maton_api_request(f"trello/boards/{board_id}/lists")
    if not lists:
        print("❌ Failed to fetch lists")
        return board_id, None
    
    list_id = None
    for lst in lists.get('lists', []):
        if lst['name'] == TARGET_LIST:
            list_id = lst['id']
            break
    
    if not list_id:
        print(f"❌ List '{TARGET_LIST}' not found on board")
        return board_id, None
    
    print(f"✅ Found list: {TARGET_LIST} ({list_id})")
    return board_id, list_id

def create_card(list_id, name, description):
    """Create a card in Trello"""
    data = {
        "name": name,
        "desc": description,
        "idList": list_id
    }
    
    result = maton_api_request("trello/cards", method="POST", data=data)
    return result

def parse_csv_file(filepath, limit=None):
    """Parse CSV file and return card data"""
    cards = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            cards.append({
                'name': row['Name'],
                'description': row['Description']
            })
    return cards

def main():
    print("=" * 60)
    print("CYCLE 17 TRELLO IMPORT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    if not MATON_API_KEY:
        print("❌ MATON_API_KEY not found in environment")
        return False
    
    # Get board and list
    board_id, list_id = get_board_and_list()
    if not list_id:
        print("\n⚠️  Falling back to CSV generation for manual import")
        return generate_manual_csv()
    
    print()
    
    # Parse and import VC cards
    print("📊 Parsing VC packets...")
    vc_cards = parse_csv_file(VC_FILE)
    print(f"   Found {len(vc_cards)} VC cards")
    
    # Parse and import BDR cards (top 5)
    print("📊 Parsing BDR studios...")
    bdr_cards = parse_csv_file(BDR_FILE, limit=5)
    print(f"   Found {len(bdr_cards)} BDR cards (top 5)")
    
    all_cards = vc_cards + bdr_cards
    print(f"\n🚀 Importing {len(all_cards)} cards to Trello...")
    print()
    
    imported = []
    failed = []
    
    for card in all_cards:
        print(f"   Creating: {card['name'][:60]}...", end=" ")
        result = create_card(list_id, card['name'], card['description'])
        if result and result.get('id'):
            print("✅")
            imported.append(card['name'])
        else:
            print("❌")
            failed.append(card['name'])
    
    print()
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total: {len(all_cards)}")
    print(f"Success: {len(imported)}")
    print(f"Failed: {len(failed)}")
    print()
    
    if imported:
        print("✅ IMPORTED CARDS:")
        for name in imported:
            print(f"   • {name}")
    
    if failed:
        print("\n❌ FAILED CARDS:")
        for name in failed:
            print(f"   • {name}")
    
    return len(failed) == 0

def generate_manual_csv():
    """Generate CSV for manual import if API fails"""
    print("\n📄 GENERATING MANUAL IMPORT CSV...")
    
    vc_cards = parse_csv_file(VC_FILE)
    bdr_cards = parse_csv_file(BDR_FILE, limit=5)
    all_cards = vc_cards + bdr_cards
    
    output_file = "/data/workspace/output/cycle17_trello_import_ready.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Description'])
        for card in all_cards:
            writer.writerow([card['name'], card['description']])
    
    print(f"✅ CSV saved to: {output_file}")
    print()
    print("📋 COPY-PASTE READY CARD NAMES:")
    print("-" * 60)
    for card in all_cards:
        print(f"• {card['name']}")
    print("-" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
