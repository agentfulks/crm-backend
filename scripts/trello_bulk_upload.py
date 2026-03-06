#!/usr/bin/env python3
"""
Trello Bulk Upload Script - BDR Outreach Agent
Uploads VC investor packets from CSV files to Trello board.

Environment Variables Required:
- TRELLO_API_KEY: Your Trello API key
- TRELLO_TOKEN: Your Trello API token
- TRELLO_BOARD_ID: (Optional) Target board ID (defaults to Lucas' VC Outreach board)

Usage:
    python trello_bulk_upload.py --day 7          # Upload specific day
    python trello_bulk_upload.py --all            # Upload all available days
    python trello_bulk_upload.py --dry-run        # Preview without uploading
    python trello_bulk_upload.py --list           # List all available batches
"""

import os
import sys
import json
import csv
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Configuration
TRELLO_API_KEY = os.environ.get('TRELLO_API_KEY')
TRELLO_TOKEN = os.environ.get('TRELLO_TOKEN')
TRELLO_BASE_URL = 'https://api.trello.com/1'

# Default board and list IDs (Lucas' VC Outreach board)
DEFAULT_BOARD_ID = '699d2728fd2ae8c35d1f7a44'  # VC Outreach Engine
DEFAULT_LIST_ID = '699d309c1870f04a4b401759'   # Daily Queue

# Deliverables path
DELIVERABLES_PATH = Path('/data/workspace/deliverables')


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


def get_board_lists(board_id):
    """Fetch all lists on a board."""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/lists"
    params = get_auth_params()
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url)
    if status == 200:
        return json.loads(response)
    else:
        print(f"ERROR: Failed to fetch lists: {status} - {response}")
        return []


def create_card(name, description, list_id, labels=None):
    """Create a new card on Trello."""
    url = f"{TRELLO_BASE_URL}/cards"
    params = get_auth_params()
    params['idList'] = list_id
    params['name'] = name
    params['desc'] = description
    
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='POST')
    if status == 200:
        return json.loads(response)
    else:
        print(f"ERROR: Failed to create card '{name}': {status} - {response}")
        return None


def add_label_to_card(card_id, label_id):
    """Add a label to a card."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}/idLabels"
    params = get_auth_params()
    params['value'] = label_id
    
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url, method='POST')
    return status == 200


def get_board_labels(board_id):
    """Fetch all labels on a board."""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/labels"
    params = get_auth_params()
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    status, response = make_request(full_url)
    if status == 200:
        return json.loads(response)
    else:
        return []


def find_csv_files():
    """Find all trello_import.csv files in deliverables."""
    csv_files = []
    
    # Check for day batch directories
    for item in DELIVERABLES_PATH.iterdir():
        if item.is_dir():
            csv_path = item / 'trello_import.csv'
            if csv_path.exists():
                # Extract day number from directory name
                day_num = None
                if 'day' in item.name:
                    try:
                        day_num = int(item.name.replace('day', '').split('_')[0])
                    except:
                        pass
                
                csv_files.append({
                    'path': csv_path,
                    'day': day_num,
                    'name': item.name
                })
    
    # Sort by day number
    csv_files.sort(key=lambda x: (x['day'] is None, x['day'] or 0))
    return csv_files


def parse_csv_file(csv_path):
    """Parse a trello_import.csv file and return card data."""
    cards = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cards.append({
                    'name': row.get('Name', ''),
                    'description': row.get('Description', ''),
                    'labels': row.get('Labels', ''),
                    'list': row.get('List', '')
                })
    except Exception as e:
        print(f"ERROR: Failed to parse {csv_path}: {e}")
    return cards


def upload_batch(csv_info, list_id, dry_run=False, delay=1):
    """Upload a batch of cards from CSV."""
    csv_path = csv_info['path']
    day = csv_info['day']
    name = csv_info['name']
    
    cards = parse_csv_file(csv_path)
    
    if not cards:
        print(f"  No cards found in {csv_path}")
        return {'uploaded': 0, 'failed': 0, 'skipped': 0}
    
    print(f"\n  Batch: {name}")
    print(f"  Day: {day or 'N/A'}")
    print(f"  Cards to upload: {len(cards)}")
    
    if dry_run:
        print(f"  [DRY RUN] Would upload {len(cards)} cards")
        for card in cards[:3]:  # Show first 3
            print(f"    - {card['name'][:60]}...")
        if len(cards) > 3:
            print(f"    ... and {len(cards) - 3} more")
        return {'uploaded': 0, 'failed': 0, 'skipped': len(cards)}
    
    results = {'uploaded': 0, 'failed': 0, 'skipped': 0}
    
    for i, card in enumerate(cards, 1):
        print(f"  [{i}/{len(cards)}] Creating: {card['name'][:50]}...", end=' ')
        
        result = create_card(
            name=card['name'],
            description=card['description'],
            list_id=list_id
        )
        
        if result:
            print("OK")
            results['uploaded'] += 1
        else:
            print("FAILED")
            results['failed'] += 1
        
        # Rate limiting delay
        if delay > 0 and i < len(cards):
            import time
            time.sleep(delay)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Bulk upload VC investor packets to Trello',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                          # List all available batches
  %(prog)s --day 7                         # Upload Day 7 batch
  %(prog)s --day 7,8,9                     # Upload Days 7-9
  %(prog)s --all                           # Upload all available batches
  %(prog)s --all --dry-run                 # Preview all uploads
  %(prog)s --day 19 --list-id <ID>         # Upload to specific list
        """
    )
    
    parser.add_argument('--list', action='store_true',
                        help='List all available CSV batches')
    parser.add_argument('--day', type=str,
                        help='Day number(s) to upload (comma-separated for multiple)')
    parser.add_argument('--all', action='store_true',
                        help='Upload all available batches')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without actually uploading')
    parser.add_argument('--list-id', type=str, default=DEFAULT_LIST_ID,
                        help=f'Trello list ID to upload to (default: {DEFAULT_LIST_ID})')
    parser.add_argument('--board-id', type=str, default=DEFAULT_BOARD_ID,
                        help=f'Trello board ID (default: {DEFAULT_BOARD_ID})')
    parser.add_argument('--delay', type=int, default=1,
                        help='Delay between API calls in seconds (default: 1)')
    
    args = parser.parse_args()
    
    # Header
    print("="*70)
    print("TRELLO BULK UPLOAD - BDR OUTREACH AGENT")
    print("="*70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Check credentials (unless just listing)
    if not args.list:
        if not TRELLO_API_KEY or not TRELLO_TOKEN:
            print("\nERROR: Trello API credentials not found!")
            print("Please set environment variables:")
            print("  export TRELLO_API_KEY='your_api_key'")
            print("  export TRELLO_TOKEN='your_token'")
            print("\nGet your credentials at: https://trello.com/app-key")
            sys.exit(1)
        
        print(f"API Key: {TRELLO_API_KEY[:8]}...")
        print(f"Target Board: {args.board_id}")
        print(f"Target List: {args.list_id}")
    
    # Find all available CSV files
    csv_files = find_csv_files()
    
    if args.list:
        print("\n" + "-"*70)
        print("AVAILABLE BATCHES")
        print("-"*70)
        print(f"{'Day':<6} {'Batch Name':<30} {'Cards':<8} {'Path'}")
        print("-"*70)
        
        total_cards = 0
        for csv_info in csv_files:
            cards = parse_csv_file(csv_info['path'])
            day_str = str(csv_info['day']) if csv_info['day'] else '-'
            print(f"{day_str:<6} {csv_info['name']:<30} {len(cards):<8} {csv_info['path']}")
            total_cards += len(cards)
        
        print("-"*70)
        print(f"Total: {len(csv_files)} batches, {total_cards} cards ready to upload")
        print("="*70)
        return
    
    # Filter batches to upload
    if args.all:
        batches_to_upload = csv_files
    elif args.day:
        days = [int(d.strip()) for d in args.day.split(',')]
        batches_to_upload = [c for c in csv_files if c['day'] in days]
    else:
        print("\nERROR: No action specified. Use --day, --all, or --list")
        parser.print_help()
        sys.exit(1)
    
    if not batches_to_upload:
        print("\nERROR: No matching batches found!")
        print("Run with --list to see available batches.")
        sys.exit(1)
    
    # Show preview
    print("\n" + "-"*70)
    print("UPLOAD PLAN")
    print("-"*70)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Batches to process: {len(batches_to_upload)}")
    
    total_cards = sum(len(parse_csv_file(c['path'])) for c in batches_to_upload)
    print(f"Total cards: {total_cards}")
    print("-"*70)
    
    for batch in batches_to_upload:
        card_count = len(parse_csv_file(batch['path']))
        day_str = f"Day {batch['day']}" if batch['day'] else batch['name']
        print(f"  - {day_str}: {card_count} cards")
    
    if args.dry_run:
        print("\n[DRY RUN - No cards will be created]")
    else:
        confirm = input("\nProceed with upload? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Upload cancelled.")
            sys.exit(0)
    
    # Execute uploads
    print("\n" + "="*70)
    print("EXECUTING UPLOADS")
    print("="*70)
    
    all_results = []
    for batch in batches_to_upload:
        result = upload_batch(batch, args.list_id, args.dry_run, args.delay)
        result['batch'] = batch['name']
        result['day'] = batch['day']
        all_results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    
    total_uploaded = sum(r['uploaded'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_skipped = sum(r['skipped'] for r in all_results)
    
    print(f"{'Batch':<25} {'Uploaded':<10} {'Failed':<10} {'Skipped'}")
    print("-"*70)
    for r in all_results:
        batch_name = f"Day {r['day']}" if r['day'] else r['batch'][:20]
        print(f"{batch_name:<25} {r['uploaded']:<10} {r['failed']:<10} {r['skipped']}")
    print("-"*70)
    print(f"{'TOTAL':<25} {total_uploaded:<10} {total_failed:<10} {total_skipped}")
    print("="*70)
    
    # Save results
    if not args.dry_run:
        results_file = f'/data/workspace/trello_upload_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'execution_time': datetime.now().isoformat(),
                'mode': 'live',
                'total_batches': len(all_results),
                'total_uploaded': total_uploaded,
                'total_failed': total_failed,
                'results': all_results
            }, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
    
    print(f"\nExecution complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    if total_failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
