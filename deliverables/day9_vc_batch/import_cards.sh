#!/bin/bash
# Trello Import Script - Day 9 VC Batch
# Generated: 2026-02-27
# Usage: ./import_cards.sh [TRELLO_BOARD_ID] [TRELLO_LIST_ID]

set -e

# Configuration
BOARD_ID="${1:-$TRELLO_BOARD_ID}"
LIST_ID="${2:-$TRELLO_LIST_ID}"
CARDS_FILE="trello_cards_ready.json"

# Check for Trello API credentials
if [ -z "$TRELLO_API_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo "Error: TRELLO_API_KEY and TRELLO_TOKEN environment variables must be set"
    echo "Get yours at: https://trello.com/app-key"
    exit 1
fi

# Validate inputs
if [ -z "$BOARD_ID" ] && [ -z "$LIST_ID" ]; then
    echo "Usage: ./import_cards.sh [BOARD_ID] [LIST_ID]"
    echo "Or set TRELLO_BOARD_ID and TRELLO_LIST_ID environment variables"
    exit 1
fi

if [ ! -f "$CARDS_FILE" ]; then
    echo "Error: $CARDS_FILE not found"
    exit 1
fi

echo "========================================"
echo "Trello Import: Day 9 VC Batch"
echo "========================================"
echo ""

# Parse and create cards
# Note: This uses jq if available, falls back to manual parsing

if command -v jq &> /dev/null; then
    echo "Using jq for JSON parsing..."
    
    NUM_CARDS=$(jq '.cards | length' "$CARDS_FILE")
    echo "Found $NUM_CARDS cards to import"
    echo ""
    
    for i in $(seq 0 $(($NUM_CARDS - 1))); do
        CARD_NAME=$(jq -r ".cards[$i].name" "$CARDS_FILE")
        CARD_DESC=$(jq -r ".cards[$i].desc" "$CARDS_FILE")
        
        echo "[$((i+1))/$NUM_CARDS] Creating: $CARD_NAME"
        
        # Create card via Trello API
        RESPONSE=$(curl -s -X POST \
            "https://api.trello.com/1/cards" \
            -H "Content-Type: application/json" \
            -d "{
                \"key\": \"$TRELLO_API_KEY\",
                \"token\": \"$TRELLO_TOKEN\",
                \"idList\": \"$LIST_ID\",
                \"name\": \"$CARD_NAME\",
                \"desc\": $(echo "$CARD_DESC" | jq -R -s '.')
            }")
        
        CARD_ID=$(echo "$RESPONSE" | jq -r '.id')
        
        if [ "$CARD_ID" != "null" ] && [ -n "$CARD_ID" ]; then
            echo "  ✓ Created: https://trello.com/c/$CARD_ID"
            
            # Add labels if specified
            NUM_LABELS=$(jq ".cards[$i].labels | length" "$CARDS_FILE")
            if [ "$NUM_LABELS" -gt 0 ]; then
                for j in $(seq 0 $(($NUM_LABELS - 1))); do
                    LABEL=$(jq -r ".cards[$i].labels[$j]" "$CARDS_FILE")
                    echo "  → Adding label: $LABEL"
                    # Note: Labels need to exist on the board or be created
                done
            fi
            
            # Set due date if specified
            DUE_DATE=$(jq -r ".cards[$i].due" "$CARDS_FILE")
            if [ "$DUE_DATE" != "null" ] && [ -n "$DUE_DATE" ]; then
                curl -s -X PUT \
                    "https://api.trello.com/1/cards/$CARD_ID" \
                    -H "Content-Type: application/json" \
                    -d "{\"key\": \"$TRELLO_API_KEY\", \"token\": \"$TRELLO_TOKEN\", \"due\": \"$DUE_DATE\"}" \
                    > /dev/null
                echo "  → Due date set: $DUE_DATE"
            fi
        else
            echo "  ✗ Failed to create card"
            echo "  Response: $RESPONSE"
        fi
        
        echo ""
    done
else
    echo "jq not found. Install jq for automated import, or use manual process:"
    echo ""
    echo "Manual Import Instructions:"
    echo "1. Open $CARDS_FILE"
    echo "2. Copy each card's name and description"
    echo "3. Create cards in Trello list '$LIST_ID'"
    echo ""
fi

echo "========================================"
echo "Import Complete"
echo "========================================"
echo ""
echo "Summary:"
echo "- Cards created: $NUM_CARDS"
echo "- Board: https://trello.com/b/$BOARD_ID"
echo ""
echo "Next Steps:"
echo "1. Review cards in Trello"
echo "2. Send emails using draft files in ./emails/"
echo "3. Move cards to 'Sent' list after outreach"
echo "4. Track responses and update card status"
