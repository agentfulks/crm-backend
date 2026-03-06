#!/bin/bash
# TRELLO BULK UPLOAD SCRIPT - Days 8-15 Batch
# Generated: 2026-02-28
# Total Cards: 40 funds across 8 days
# Board: https://trello.com/b/tPkRdYjg/vc-outreach-engine

# REQUIREMENTS:
# - TRELLO_API_KEY and TRELLO_TOKEN environment variables set
# - BOARD_ID: tPkRdYjg (VC Outreach Engine)
# - LIST_ID for Daily Queue (retrieve via API or use existing)

echo "=== TRELLO BULK UPLOAD: DAYS 8-15 ==="
echo "Total funds to upload: 40"
echo ""

# Function to create card via Trello API
create_card() {
    local name="$1"
    local desc="$2"
    local due="$3"
    local idList="$4"
    
    curl -s -X POST "https://api.trello.com/1/cards" \
        -d "key=$TRELLO_API_KEY" \
        -d "token=$TRELLO_TOKEN" \
        -d "idList=$idList" \
        -d "name=$name" \
        -d "desc=$desc" \
        -d "due=$due" \
        -d "pos=top"
}

# Check if credentials are set
if [ -z "$TRELLO_API_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo "ERROR: TRELLO_API_KEY and TRELLO_TOKEN must be set"
    echo "Export these variables or run:"
    echo "  export TRELLO_API_KEY=your_key"
    echo "  export TRELLO_TOKEN=your_token"
    exit 1
fi

# Get Daily Queue list ID
echo "Fetching Daily Queue list ID..."
BOARD_ID="tPkRdYjg"
LIST_RESPONSE=$(curl -s "https://api.trello.com/1/boards/$BOARD_ID/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN")
DAILY_QUEUE_ID=$(echo "$LIST_RESPONSE" | grep -o '"id":"[^"]*"[^}]*"name":"Daily Queue"' | head -1 | cut -d'"' -f4)

if [ -z "$DAILY_QUEUE_ID" ]; then
    echo "ERROR: Could not find Daily Queue list. Please check board structure."
    exit 1
fi

echo "Daily Queue List ID: $DAILY_QUEUE_ID"
echo ""

# Upload each day's batch
for DAY in 8 9 10 11 12 13 14 15; do
    IMPORT_FILE="deliverables/day${DAY}_vc_batch/day${DAY}_trello_import.json"
    
    if [ ! -f "$IMPORT_FILE" ]; then
        echo "WARNING: $IMPORT_FILE not found, skipping Day $DAY"
        continue
    fi
    
    echo "Uploading Day $DAY batch..."
    
    # Parse and upload each card
    jq -c '.[]' "$IMPORT_FILE" | while read card; do
        name=$(echo "$card" | jq -r '.name')
        desc=$(echo "$card" | jq -r '.desc')
        due=$(echo "$card" | jq -r '.due')
        
        echo "  Creating: $name"
        create_card "$name" "$desc" "$due" "$DAILY_QUEUE_ID" > /dev/null 2>&1
        sleep 0.5  # Rate limiting
    done
    
    echo "  Day $DAY complete"
done

echo ""
echo "=== UPLOAD COMPLETE ==="
echo "Check Trello board: https://trello.com/b/$BOARD_ID"
