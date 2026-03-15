#!/bin/bash
# Trello Card Creation Script for BDR Game Studios Outreach

BOARD_ID="699f37680e0b1bc16721ae44"
LIST_ID="699f376e916d1293ac8a24c2"  # Ready for Review
API_BASE="https://gateway.maton.ai/trello"

# Function to create a card
create_card() {
    local name="$1"
    local desc="$2"
    local labels="$3"
    
    curl -s -X POST "${API_BASE}/1/cards" \
        -H "Authorization: Bearer ${MATON_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{
            \"idList\": \"${LIST_ID}\",
            \"name\": \"${name}\",
            \"desc\": \"${desc}\",
            \"idLabels\": [${labels}]
        }"
}

# Note: Labels need to be created first or existing IDs used
# Green = Tier-1, Yellow = Tier-2, Blue = Tier-3, Red = Ready for Review

echo "Ready to create cards..."
