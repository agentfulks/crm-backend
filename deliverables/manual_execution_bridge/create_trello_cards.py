#!/usr/bin/env python3
"""
TRELLO CARD AUTO-CREATION SCRIPT (Python Version)
=================================================

This script creates all 5 outreach cards on your Trello board once you have
API credentials configured.

PREREQUISITES:
    1. Set environment variables (add to ~/.bashrc, ~/.zshrc, or .env file):
       export TRELLO_API_KEY="your_api_key"
       export TRELLO_TOKEN="your_token"
       export TRELLO_BOARD_ID="your_board_id"

    2. Get your credentials from: https://trello.com/app-key

    3. Get your board ID from the board URL or via API:
       curl "https://api.trello.com/1/members/me/boards?key=YOUR_KEY&token=YOUR_TOKEN"

    4. Install requests (if not already installed):
       pip install requests

USAGE:
    chmod +x create_trello_cards.py
    ./create_trello_cards.py

    Or with explicit credentials:
    TRELLO_API_KEY=xxx TRELLO_TOKEN=yyy TRELLO_BOARD_ID=zzz python3 create_trello_cards.py

OUTPUT:
    Creates 5 cards in the first list on your board with:
    - Full descriptions with contact details
    - Labels (Priority-A/B/C, Ready-to-Send)
    - Checklists with send workflow steps
"""

import os
import sys
import json
import urllib.parse
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found.")
    print("Install with: pip install requests")
    sys.exit(1)

# Card data - matching the CSV export
CARDS = [
    {
        "name": "[P1] BITKRAFT Ventures - Martin Garcia, CFO & General Partner",
        "description": """Priority: P1
Contact: Martin Garcia
Email: martin@bitkraft.vc
Check Size: $500K-$10M USD
Stage: Seed, Series A, Series B
Score: 84.0 (Rank #1)

Thesis Fit: Gaming, esports, immersive technology (Synthetic Reality focus)
Hook: Founder-built infrastructure alignment
Contact Source: ZoomInfo (medium confidence)
HQ: Los Angeles, California

Email: manual_execution_bridge/P1_BITKRAFT_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04""",
        "labels": ["Priority-A", "Ready-to-Send"],
        "priority": "A"
    },
    {
        "name": "[P2] Konvoy Ventures - Taylor Hurst, Principal",
        "description": """Priority: P2
Contact: Taylor Hurst
Email: taylor@konvoy.vc
Check Size: $500K-$3M USD
Stage: Pre-Seed, Seed, Series A
Score: 59.33 (Rank #2)

Thesis Fit: Gaming infrastructure and platform bets
Hook: Infrastructure play - daily VC scoring engine
Contact Source: LinkedIn (medium confidence)
HQ: Denver, Colorado

Email: manual_execution_bridge/P2_Konvoy_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04""",
        "labels": ["Priority-B", "Ready-to-Send"],
        "priority": "B"
    },
    {
        "name": "[P3] Mechanism Capital - Steve Cho, Partner",
        "description": """Priority: P3
Contact: Steve Cho (Head of Mech Play)
Email: steve@mechanism.capital
Check Size: $1M-$2M USD
Stage: Pre-seed, Seed, Series A
Score: 53.33 (Rank #3)

Thesis Fit: Blockchain, DeFi, crypto-gaming
Hook: Crypto-gaming meets AI
Contact Source: RocketReach (HIGH confidence)
Special: Former Apple App Store Games, leads web3 gaming deals

Email: manual_execution_bridge/P3_Mechanism_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04""",
        "labels": ["Priority-C", "Ready-to-Send"],
        "priority": "C"
    },
    {
        "name": "[P4] Collab+Currency - Derek Edwards, Managing Partner",
        "description": """Priority: P4
Contact: Derek Edwards
Email: derek@collabcurrency.com
Check Size: $100K-$3M USD
Stage: Pre-Seed, Seed
Score: 51.33 (Rank #4)

Thesis Fit: Intersection of crypto and culture
Hook: Crypto x culture - daily investor packets as product
Contact Source: Twitter (medium confidence)
HQ: Eugene, Oregon
Special: Former attorney and startup founder

Email: manual_execution_bridge/P4_CollabCurrency_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04""",
        "labels": ["Priority-C", "Ready-to-Send"],
        "priority": "C"
    },
    {
        "name": "[P5] Variant - Spencer Noon, Co-Founder & General Partner",
        "description": """Priority: P5
Contact: Spencer Noon
Email: spencer@variant.fund
Check Size: $1M-$5M USD
Stage: Pre-Seed, Seed, Series A
Score: 48.33 (Rank #5)

Thesis Fit: User ownership and alignment
Hook: User-owned VC sourcing - AI engine + partner approval
Contact Source: Twitter (medium confidence)
HQ: New York, NY / Distributed
Special: Runs OurNetwork newsletter, DeFi/Crypto focus

Email: manual_execution_bridge/P5_Variant_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04""",
        "labels": ["Priority-C", "Ready-to-Send"],
        "priority": "C"
    }
]

CHECKLIST_ITEMS = [
    "Move to Awaiting Approval",
    "Review email template",
    "Approve for send",
    "Send email",
    "Move to Sent",
    "Log in sent_log.csv",
    "Schedule Day 3 follow-up",
    "Schedule Day 7 follow-up"
]

LABEL_COLORS = {
    "Priority-A": "green",
    "Priority-B": "yellow",
    "Priority-C": "orange",
    "Ready-to-Send": "blue",
    "Sent": "purple"
}


class TrelloClient:
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.base_url = "https://api.trello.com/1"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated request to Trello API"""
        url = f"{self.base_url}{endpoint}"
        params = kwargs.pop('params', {})
        params['key'] = self.api_key
        params['token'] = self.token
        
        response = requests.request(method, url, params=params, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_board_lists(self, board_id: str) -> List[Dict]:
        """Get all lists on a board"""
        return self._request('GET', f'/boards/{board_id}/lists')
    
    def create_card(self, list_id: str, name: str, description: str) -> Dict:
        """Create a new card"""
        return self._request('POST', '/cards', data={
            'idList': list_id,
            'name': name,
            'desc': description
        })
    
    def add_label_to_card(self, card_id: str, label_name: str, color: str = None):
        """Add a label to a card"""
        data = {'name': label_name}
        if color:
            data['color'] = color
        return self._request('POST', f'/cards/{card_id}/labels', data=data)
    
    def create_checklist(self, card_id: str, name: str = "Send Workflow") -> Dict:
        """Create a checklist on a card"""
        return self._request('POST', '/checklists', data={
            'idCard': card_id,
            'name': name
        })
    
    def add_checklist_item(self, checklist_id: str, name: str):
        """Add an item to a checklist"""
        return self._request('POST', f'/checklists/{checklist_id}/checkItems', data={
            'name': name
        })


def check_environment() -> tuple:
    """Check that required environment variables are set"""
    api_key = os.environ.get('TRELLO_API_KEY')
    token = os.environ.get('TRELLO_TOKEN')
    board_id = os.environ.get('TRELLO_BOARD_ID')
    
    missing = []
    if not api_key:
        missing.append('TRELLO_API_KEY')
    if not token:
        missing.append('TRELLO_TOKEN')
    if not board_id:
        missing.append('TRELLO_BOARD_ID')
    
    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them with:")
        print('  export TRELLO_API_KEY="your_api_key"')
        print('  export TRELLO_TOKEN="your_token"')
        print('  export TRELLO_BOARD_ID="your_board_id"')
        print("\nGet your API key at: https://trello.com/app-key")
        sys.exit(1)
    
    return api_key, token, board_id


def get_target_list_id(client: TrelloClient, board_id: str) -> str:
    """Get the first list ID from the board"""
    try:
        lists = client.get_board_lists(board_id)
        if not lists:
            print("ERROR: No lists found on the board")
            sys.exit(1)
        
        # Try to find a list with "Daily" or "Queue" in the name
        for lst in lists:
            if 'daily' in lst['name'].lower() or 'queue' in lst['name'].lower():
                print(f"Found list: {lst['name']} (ID: {lst['id']})")
                return lst['id']
        
        # Fall back to first list
        print(f"Using first list: {lists[0]['name']} (ID: {lists[0]['id']})")
        return lists[0]['id']
    
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Failed to fetch lists: {e}")
        sys.exit(1)


def create_card_with_details(client: TrelloClient, list_id: str, card_data: dict) -> bool:
    """Create a card with labels and checklist"""
    try:
        print(f"\nCreating card: {card_data['name'][:50]}...")
        
        # Create the card
        card = client.create_card(list_id, card_data['name'], card_data['description'])
        card_id = card['id']
        print(f"  ✓ Created card ID: {card_id}")
        
        # Add labels
        for label in card_data.get('labels', []):
            color = LABEL_COLORS.get(label)
            try:
                client.add_label_to_card(card_id, label, color)
                print(f"  ✓ Added label: {label}")
            except requests.exceptions.HTTPError as e:
                print(f"  ⚠ Failed to add label {label}: {e}")
        
        # Create checklist
        try:
            checklist = client.create_checklist(card_id)
            checklist_id = checklist['id']
            print(f"  ✓ Created checklist")
            
            # Add checklist items
            for item in CHECKLIST_ITEMS:
                client.add_checklist_item(checklist_id, item)
            print(f"  ✓ Added {len(CHECKLIST_ITEMS)} checklist items")
        
        except requests.exceptions.HTTPError as e:
            print(f"  ⚠ Failed to create checklist: {e}")
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ Failed to create card: {e}")
        return False


def main():
    print("=" * 60)
    print("  TRELLO CARD AUTO-CREATION SCRIPT (Python)")
    print("=" * 60)
    print()
    
    # Check environment
    api_key, token, board_id = check_environment()
    
    # Initialize client
    client = TrelloClient(api_key, token)
    
    # Get target list
    list_id = get_target_list_id(client, board_id)
    print()
    
    # Create all cards
    success = 0
    failed = 0
    
    for card_data in CARDS:
        if create_card_with_details(client, list_id, card_data):
            success += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  SUMMARY: {success} cards created successfully")
    if failed > 0:
        print(f"           {failed} cards failed")
    print("=" * 60)
    
    return failed


if __name__ == "__main__":
    sys.exit(main())
