#!/bin/bash
# Trello Card Movement Script - Day 1 Packet Cards
# Execute this script after setting TRELLO_API_KEY and TRELLO_TOKEN environment variables
#
# Required environment variables:
#   TRELLO_API_KEY - Your Trello API key
#   TRELLO_TOKEN   - Your Trello API token
#
# To obtain these:
#   1. API Key: https://trello.com/app-key
#   2. Token: Visit the link provided on that page after accepting terms
#
# Usage: export TRELLO_API_KEY=xxx && export TRELLO_TOKEN=yyy && ./trello_card_moves.sh

set -e

# Validate environment
if [ -z "$TRELLO_API_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo "ERROR: TRELLO_API_KEY and TRELLO_TOKEN must be set"
    echo "Example: export TRELLO_API_KEY=your_key && export TRELLO_TOKEN=your_token"
    exit 1
fi

# Card IDs to move
BITKRAFT_CARD_ID="699d62440c53022f56dc42b1"
VARIANT_CARD_ID="699d62471bee2f60a50aab9a"
COLLABCURRENCY_CARD_ID="699d6249d5248492eefc000e"
KONVOY_CARD_ID="699d624cdd614a5e0a62b5e3"
MECHANISM_CARD_ID="699d624efca4d3709cef25d5"

# Target list ID (Awaiting Approval)
# Note: You'll need to get this from the Trello board
# API call to get lists: curl -s "https://api.trello.com/1/boards/{board_id}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
TARGET_LIST_ID="${TARGET_LIST_ID:-AWAITING_APPROVAL_LIST_ID}"

echo "==============================================="
echo "Trello Card Movement - Day 1 Packets"
echo "==============================================="
echo ""

# Function to move a card
move_card() {
    local card_id=$1
    local card_name=$2
    
    echo "Moving: $card_name ($card_id)"
    echo "  -> Target List ID: $TARGET_LIST_ID"
    
    curl -s -X PUT \
        "https://api.trello.com/1/cards/$card_id" \
        -d "key=$TRELLO_API_KEY" \
        -d "token=$TRELLO_TOKEN" \
        -d "idList=$TARGET_LIST_ID" \
        -H "Content-Type: application/x-www-form-urlencoded" | jq -r '.name + " -> " + .idList'
    
    echo ""
}

# Check if TARGET_LIST_ID is set to actual value
if [ "$TARGET_LIST_ID" = "AWAITING_APPROVAL_LIST_ID" ]; then
    echo "WARNING: TARGET_LIST_ID not set!"
    echo ""
    echo "To find your 'Awaiting Approval' list ID, run:"
    echo "  curl -s \"https://api.trello.com/1/boards/{board_id}/lists?key=\$TRELLO_API_KEY&token=\$TRELLO_TOKEN\" | jq '.'"
    echo ""
    echo "Then set: export TARGET_LIST_ID=your_list_id"
    echo ""
    exit 1
fi

# Move each card
move_card "$BITKRAFT_CARD_ID" "Packet: BITKRAFT Ventures"
move_card "$VARIANT_CARD_ID" "Packet: Variant"
move_card "$COLLABCURRENCY_CARD_ID" "Packet: Collab+Currency"
move_card "$KONVOY_CARD_ID" "Packet: Konvoy Ventures"
move_card "$MECHANISM_CARD_ID" "Packet: Mechanism Capital"

echo "==============================================="
echo "All cards moved successfully!"
echo "==============================================="
