#!/bin/bash

# Day 14 VC Outreach - Trello Card Import Script
# Usage: ./import_to_trello.sh <board_id>
# Requires: Trello API key and token set as environment variables

set -e

# Check for required environment variables
if [ -z "$TRELLO_API_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo "Error: TRELLO_API_KEY and TRELLO_TOKEN environment variables must be set"
    echo "Get your API key at: https://trello.com/app-key"
    echo "Get your token at: https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_API_KEY"
    exit 1
fi

# Check for board ID argument
if [ -z "$1" ]; then
    echo "Usage: $0 <board_id>"
    echo "Find your board ID in the Trello URL: https://trello.com/b/BOARD_ID/board-name"
    exit 1
fi

BOARD_ID="$1"
IMPORT_FILE="day14_trello_import.json"

# Check if import file exists
if [ ! -f "$IMPORT_FILE" ]; then
    echo "Error: $IMPORT_FILE not found in current directory"
    exit 1
fi

# Get the first list ID from the board (assumes "To Do" or first list is target)
echo "Fetching lists from board $BOARD_ID..."
LISTS_RESPONSE=$(curl -s "https://api.trello.com/1/boards/$BOARD_ID/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN")
LIST_ID=$(echo "$LISTS_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data[0]['id'] if data else '')")

if [ -z "$LIST_ID" ]; then
    echo "Error: Could not find any lists on the board. Please create a list first."
    exit 1
fi

echo "Using list ID: $LIST_ID"
echo ""

# Parse the JSON and create cards
echo "Importing cards..."

python3 << PYTHON
import json
import subprocess
import sys
import os

api_key = os.environ['TRELLO_API_KEY']
token = os.environ['TRELLO_TOKEN']
list_id = "$LIST_ID"

with open('$IMPORT_FILE', 'r') as f:
    data = json.load(f)

cards = data.get('cards', [])
total = len(cards)
success = 0
failed = 0

for i, card in enumerate(cards, 1):
    name = card.get('name', '')
    desc = card.get('desc', '')
    labels = card.get('labels', [])
    
    print(f"[{i}/{total}] Creating card: {name}")
    
    # Build curl command
    cmd = [
        'curl', '-s', '-X', 'POST',
        f'https://api.trello.com/1/cards?key={api_key}&token={token}',
        '--data-urlencode', f'idList={list_id}',
        '--data-urlencode', f'name={name}',
        '--data-urlencode', f'desc={desc}'
    ]
    
    # Add labels if present
    for label in labels:
        cmd.extend(['--data-urlencode', f'labels={label}'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        response = json.loads(result.stdout)
        
        if 'id' in response:
            print(f"  ✓ Created: https://trello.com/c/{response['shortUrl'].split('/')[-1]}")
            success += 1
        else:
            print(f"  ✗ Failed: {response.get('message', 'Unknown error')}")
            failed += 1
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        failed += 1

print("")
print(f"Import complete: {success} success, {failed} failed")
PYTHON

echo ""
echo "Import complete!"
echo ""
echo "Next steps:"
echo "1. Review imported cards in Trello"
echo "2. Assign team members to Tier 1 cards (NFX, Moonfire, Remagine)"
echo "3. Update card status as outreach progresses"
echo "4. Log all responses and meeting notes in card descriptions"
