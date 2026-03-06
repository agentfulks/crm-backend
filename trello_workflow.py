#!/usr/bin/env python3
"""
Trello Board Workflow - Investor Packet Card Processing
Moves cards from Daily Queue to Awaiting Approval, updates descriptions with enriched contacts, adds status comments.
Uses only standard library modules.
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

# List IDs
DAILY_QUEUE_LIST_ID = '699d309c1870f04a4b401759'
AWAITING_APPROVAL_LIST_ID = '699d2728fd2ae8c35d1f7a48'

# Card IDs to process
CARDS_TO_PROCESS = [
    {'id': '699d62440c53022f56dc42b1', 'name': 'Packet: BITKRAFT Ventures'},
    {'id': '699d62471bee2f60a50aab9a', 'name': 'Packet: Variant'},
    {'id': '699d6249d5248492eefc000e', 'name': 'Packet: Collab+Currency'},
    {'id': '699d624cdd614a5e0a62b5e3', 'name': 'Packet: Konvoy Ventures'},
    {'id': '699d624efca4d3709cef25d5', 'name': 'Packet: Mechanism Capital'},
]

# Enriched contact data
CONTACT_ENRICHMENT = {
    'BITKRAFT Ventures': {
        'name': 'Martin Garcia',
        'title': 'CFO & General Partner',
        'email': 'martin@bitkraft.vc'
    },
    'Variant': {
        'name': 'Spencer Noon',
        'title': 'Co-Founder & General Partner',
        'email': 'spencer@variant.fund'
    },
    'Collab+Currency': {
        'name': 'Derek Edwards',
        'title': 'Managing Partner',
        'email': 'derek@collabcurrency.com'
    },
    'Konvoy Ventures': {
        'name': 'Taylor Hurst',
        'title': 'Principal',
        'email': 'taylor@konvoy.vc'
    },
    'Mechanism Capital': {
        'name': 'Steve Cho',
        'title': 'Partner - Head of Mech Play',
        'email': 'steve@mechanism.capital'
    }
}

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

def get_card(card_id):
    """Fetch card details from Trello."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}"
    params = get_auth_params()
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url)
    if status == 200:
        return json.loads(response)
    else:
        print(f"ERROR: Failed to fetch card {card_id}: {status} - {response}")
        return None

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

def extract_fund_name(card_name):
    """Extract fund name from card title."""
    if card_name.startswith('Packet: '):
        return card_name.replace('Packet: ', '')
    return card_name

def enrich_description(current_desc, fund_name):
    """Add enriched contact information to description."""
    contact = CONTACT_ENRICHMENT.get(fund_name)
    if not contact:
        return current_desc
    
    enrichment_section = f"""
---
**ENRICHED CONTACT DATA** (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')})
- Primary Contact: {contact['name']}
- Title: {contact['title']}
- Email: {contact['email']}
- Status: Contact enrichment complete - ready for approval
"""
    
    # Check if enrichment already exists and remove it
    if 'ENRICHED CONTACT DATA' in current_desc:
        parts = current_desc.split('---')
        # Filter out sections containing ENRICHED CONTACT DATA
        filtered_parts = [p for p in parts if 'ENRICHED CONTACT DATA' not in p]
        current_desc = '---'.join(filtered_parts)
    
    return current_desc + enrichment_section

def process_card(card_info):
    """Process a single card through the workflow."""
    card_id = card_info['id']
    card_name = card_info['name']
    fund_name = extract_fund_name(card_name)
    
    print(f"\n{'='*60}")
    print(f"Processing: {card_name}")
    print(f"Card ID: {card_id}")
    print(f"Fund: {fund_name}")
    print(f"{'='*60}")
    
    results = {
        'card_id': card_id,
        'card_name': card_name,
        'fund_name': fund_name,
        'moved': False,
        'description_updated': False,
        'comment_added': False,
        'errors': []
    }
    
    # Step 1: Fetch current card details
    card = get_card(card_id)
    if not card:
        results['errors'].append('Failed to fetch card details')
        return results
    
    print(f"Current list: {card.get('idList')}")
    print(f"Current description length: {len(card.get('desc', ''))} chars")
    
    # Step 2: Update description with enriched contact data
    current_desc = card.get('desc', '')
    new_desc = enrich_description(current_desc, fund_name)
    
    if update_card_description(card_id, new_desc):
        print("Description updated with enriched contact data")
        results['description_updated'] = True
    else:
        results['errors'].append('Failed to update description')
    
    # Step 3: Move card to Awaiting Approval
    if move_card(card_id, AWAITING_APPROVAL_LIST_ID):
        print(f"Card moved to Awaiting Approval (list: {AWAITING_APPROVAL_LIST_ID})")
        results['moved'] = True
    else:
        results['errors'].append('Failed to move card')
    
    # Step 4: Add status comment
    contact = CONTACT_ENRICHMENT.get(fund_name)
    if contact:
        comment_text = f"""Contact enrichment complete for {fund_name}.

Primary Contact: {contact['name']} ({contact['title']})
Email: {contact['email']}

Card moved from Daily Queue to Awaiting Approval.
Ready for Lucas review."""
    else:
        comment_text = f"""Contact enrichment attempted for {fund_name}.
No enriched contact data available.

Card moved from Daily Queue to Awaiting Approval.
Ready for Lucas review."""
    
    if add_comment(card_id, comment_text):
        print("Status comment added")
        results['comment_added'] = True
    else:
        results['errors'].append('Failed to add comment')
    
    return results

def main():
    """Main execution function."""
    print("="*60)
    print("TRELLO BOARD WORKFLOW EXECUTION")
    print("VC Outreach Engine - Investor Packet Processing")
    print("="*60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Source List: Daily Queue ({DAILY_QUEUE_LIST_ID})")
    print(f"Target List: Awaiting Approval ({AWAITING_APPROVAL_LIST_ID})")
    print(f"Cards to Process: {len(CARDS_TO_PROCESS)}")
    
    # Verify credentials
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("\nERROR: Trello API credentials not found in environment variables!")
        print("Please set TRELLO_API_KEY and TRELLO_TOKEN")
        return
    
    print(f"\nUsing API Key: {TRELLO_API_KEY[:8]}...")
    print(f"Using Token: {TRELLO_TOKEN[:8]}...")
    
    # Process all cards
    all_results = []
    for card_info in CARDS_TO_PROCESS:
        result = process_card(card_info)
        all_results.append(result)
    
    # Generate summary report
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    
    success_count = 0
    for result in all_results:
        status = "SUCCESS" if not result['errors'] else "PARTIAL"
        if result['moved'] and result['description_updated'] and result['comment_added']:
            success_count += 1
            status = "SUCCESS"
        
        print(f"\n{result['card_name']}:")
        print(f"  Status: {status}")
        print(f"  - Moved: {'Yes' if result['moved'] else 'No'}")
        print(f"  - Description Updated: {'Yes' if result['description_updated'] else 'No'}")
        print(f"  - Comment Added: {'Yes' if result['comment_added'] else 'No'}")
        if result['errors']:
            print(f"  - Errors: {', '.join(result['errors'])}")
    
    print(f"\n{'='*60}")
    print(f"Total Cards Processed: {len(all_results)}")
    print(f"Fully Successful: {success_count}")
    print(f"Execution Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)
    
    # Save detailed results to file
    results_file = '/data/workspace/trello_workflow_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'source_list': DAILY_QUEUE_LIST_ID,
            'target_list': AWAITING_APPROVAL_LIST_ID,
            'cards_processed': len(all_results),
            'successful': success_count,
            'results': all_results
        }, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == '__main__':
    main()
