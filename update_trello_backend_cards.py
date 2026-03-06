#!/usr/bin/env python3
"""
Update Trello cards for backend completion.
Marks checklist items complete and moves cards to Awaiting Approval.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
TRELLO_API_KEY = os.environ.get('TRELLO_API_KEY')
TRELLO_TOKEN = os.environ.get('TRELLO_TOKEN')
TRELLO_BASE_URL = 'https://api.trello.com/1'

# Card IDs
CARD_11_ID = '699d30d569421a60335dbdb9'  # Postgres CRM schema + infra
CARD_12_ID = '699d30d8cf61ae9c1d204f8b'  # API/ingestion service

# Checklist item IDs for Card #11
CARD_11_ITEMS = {
    'provision': '699d30d7d7012c8bbd1d26de',      # Provision Postgres + credentials
    'document': '699d30d8f991bb469bfa49c9',       # Document connection details
}

# Checklist item IDs for Card #12
CARD_12_ITEMS = {
    'pydantic': '699d30d9030b43f696aaf2f9',       # Define Pydantic models
    'crud': '699d30da7dc4f93d3430c291',           # Implement CRUD endpoints
    'tests': '699d30dacbbc111caa8b5680',          # Add tests + CI script
    'deploy': '699d30db86457a3fa85658b9',         # Deploy locally (docker-compose)
}

# List IDs
AWAITING_APPROVAL_LIST_ID = '699d2728fd2ae8c35d1f7a48'

def make_request(url, method='GET', data=None):
    """Make HTTP request using urllib."""
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.data = data.encode('utf-8')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def get_auth_params():
    """Get authentication parameters for Trello API."""
    return {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }

def update_checkitem(card_id, checkitem_id, state='complete'):
    """Update a checklist item state."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}/checkItem/{checkitem_id}"
    params = get_auth_params()
    params['state'] = state
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='PUT')
    if status == 200:
        return True
    else:
        print(f"ERROR: Failed to update checkitem {checkitem_id}: {status} - {response}")
        return False

def move_card(card_id, list_id):
    """Move card to a different list."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}"
    params = get_auth_params()
    params['idList'] = list_id
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='PUT')
    if status == 200:
        return True
    else:
        print(f"ERROR: Failed to move card {card_id}: {status} - {response}")
        return False

def add_comment(card_id, text):
    """Add a comment to the card."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}/actions/comments"
    params = get_auth_params()
    params['text'] = text
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='POST')
    if status == 200:
        return True
    else:
        print(f"ERROR: Failed to add comment to card {card_id}: {status} - {response}")
        return False

def update_card_description(card_id, new_description):
    """Update card description."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}"
    params = get_auth_params()
    params['desc'] = new_description
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='PUT')
    if status == 200:
        return True
    else:
        print(f"ERROR: Failed to update description for card {card_id}: {status} - {response}")
        return False

def process_card_11():
    """Process Postgres CRM schema + infra card."""
    print("\n" + "="*60)
    print("Card #11: Postgres CRM schema + infra")
    print("="*60)
    
    results = {'card': 'Card #11', 'items_updated': [], 'moved': False, 'commented': False}
    
    # Update checklist items
    for name, item_id in CARD_11_ITEMS.items():
        if update_checkitem(CARD_11_ID, item_id, 'complete'):
            print(f"  ✓ Marked '{name}' as complete")
            results['items_updated'].append(name)
        else:
            print(f"  ✗ Failed to update '{name}'")
    
    # Move to Awaiting Approval
    if move_card(CARD_11_ID, AWAITING_APPROVAL_LIST_ID):
        print(f"  ✓ Moved to Awaiting Approval")
        results['moved'] = True
    else:
        print(f"  ✗ Failed to move card")
    
    # Add completion comment
    comment = f"""Backend Engineer - Card Complete

All checklist items finished:
✓ Postgres provisioned on Railway (production)
✓ Connection documented in CRM_DATABASE_CONNECTION.md
✓ Migrations applied (2 migrations)

Ready for Lucas review.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"""
    
    if add_comment(CARD_11_ID, comment):
        print(f"  ✓ Added completion comment")
        results['commented'] = True
    
    return results

def process_card_12():
    """Process API/ingestion service card."""
    print("\n" + "="*60)
    print("Card #12: API/ingestion service")
    print("="*60)
    
    results = {'card': 'Card #12', 'items_updated': [], 'moved': False, 'commented': False}
    
    # Update checklist items
    for name, item_id in CARD_12_ITEMS.items():
        if update_checkitem(CARD_12_ID, item_id, 'complete'):
            print(f"  ✓ Marked '{name}' as complete")
            results['items_updated'].append(name)
        else:
            print(f"  ✗ Failed to update '{name}'")
    
    # Move to Awaiting Approval
    if move_card(CARD_12_ID, AWAITING_APPROVAL_LIST_ID):
        print(f"  ✓ Moved to Awaiting Approval")
        results['moved'] = True
    else:
        print(f"  ✗ Failed to move card")
    
    # Add completion comment
    comment = f"""Backend Engineer - Card Complete

All checklist items finished:
✓ Pydantic models defined (8 entities)
✓ CRUD endpoints implemented (7 API modules)
✓ Tests + CI script added (ci.sh)
✓ Docker-compose deployment ready

New additions:
- Note/Meeting schemas and services
- Full REST API coverage

Completion report: backend/COMPLETION_REPORT.md

Ready for Lucas review.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"""
    
    if add_comment(CARD_12_ID, comment):
        print(f"  ✓ Added completion comment")
        results['commented'] = True
    
    return results

def main():
    """Main execution function."""
    print("="*60)
    print("TRELLO CARD UPDATE - BACKEND COMPLETION")
    print("="*60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Verify credentials
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("\nERROR: Trello API credentials not found!")
        print("Please set TRELLO_API_KEY and TRELLO_TOKEN environment variables")
        return
    
    print(f"\nUsing API Key: {TRELLO_API_KEY[:8]}...")
    print(f"Target List: Awaiting Approval ({AWAITING_APPROVAL_LIST_ID})")
    
    # Process both cards
    results_11 = process_card_11()
    results_12 = process_card_12()
    
    # Summary
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    
    for result in [results_11, results_12]:
        print(f"\n{result['card']}:")
        print(f"  Items Updated: {len(result['items_updated'])}")
        print(f"  Moved: {'Yes' if result['moved'] else 'No'}")
        print(f"  Commented: {'Yes' if result['commented'] else 'No'}")
    
    print(f"\n{'='*60}")
    print("Update complete!")
    print("="*60)
    
    # Save results
    results_file = '/data/workspace/trello_card_update_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'card_11': results_11,
            'card_12': results_12
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")

if __name__ == '__main__':
    main()
