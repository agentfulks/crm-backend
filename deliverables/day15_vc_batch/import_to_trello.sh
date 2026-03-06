#!/bin/bash

# Day 15 VC Batch Trello Import Script
# Theme: Emerging Gaming/AI Specialists - Regional Leaders
# Date: 2026-02-28

set -e

echo "=== Day 15 VC Batch Trello Import ==="
echo "Theme: Emerging Gaming/AI Specialists - Regional Leaders"
echo ""

# Configuration
TRELLO_BOARD_ID="your_board_id"
TRELLO_LIST_ID="your_list_id"
TRELLO_API_KEY="your_api_key"
TRELLO_TOKEN="your_token"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Install with: apt-get install jq"
    exit 1
fi

# Check if input file exists
if [ ! -f "day15_trello_import.json" ]; then
    echo "Error: day15_trello_import.json not found!"
    exit 1
fi

echo "Found $(jq length day15_trello_import.json) cards to import"
echo ""

# Counter for success/failure
SUCCESS=0
FAILED=0

# Process each card
jq -c '.[]' day15_trello_import.json | while read card; do
    NAME=$(echo $card | jq -r '.name')
    DESC=$(echo $card | jq -r '.desc')
    
    echo "Creating card: $NAME"
    
    # Create card via Trello API
    response=$(curl -s -w "\n%{http_code}" -X POST \
        "https://api.trello.com/1/cards" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "key=$TRELLO_API_KEY" \
        --data-urlencode "token=$TRELLO_TOKEN" \
        --data-urlencode "idList=$TRELLO_LIST_ID" \
        --data-urlencode "name=$NAME" \
        --data-urlencode "desc=$DESC" \
        --data-urlencode "pos=bottom")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "200" ]; then
        card_id=$(echo $body | jq -r '.id')
        card_url=$(echo $body | jq -r '.shortUrl')
        echo "  ✓ Created: $card_url"
        
        # Add labels if card was created successfully
        labels=$(echo $card | jq -r '.labels[]')
        for label in $labels; do
            # Note: Labels need to exist on the board first
            # This is a simplified version - you may need to map label names to IDs
            :
        done
        
        ((SUCCESS++))
    else
        echo "  ✗ Failed (HTTP $http_code)"
        echo "  Error: $body"
        ((FAILED++))
    fi
    
    # Rate limiting - Trello allows 300 requests per 10 seconds
    sleep 0.5
done

echo ""
echo "=== Import Complete ==="
echo "Successfully created: $SUCCESS cards"
echo "Failed: $FAILED cards"
echo ""

# Alternative: Manual import instructions
echo "=== Alternative: Manual Import ==="
echo "If API import fails, you can manually import the JSON:"
echo "1. Open Trello board"
echo "2. Go to Menu → More → Copy Board"
echo "3. Or use Trello's Bulk Import Power-Up"
echo ""
echo "Card Summary:"
jq -r '.[] | "• " + .name' day15_trello_import.json
