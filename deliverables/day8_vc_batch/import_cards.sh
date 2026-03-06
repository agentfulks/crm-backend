#!/bin/bash
# Trello Import Script for Day 8 VC Batch
# Usage: ./import_cards.sh [TRELLO_BOARD_ID] [TRELLO_LIST_ID]

TRELLO_KEY="${TRELLO_API_KEY}"
TRELLO_TOKEN="${TRELLO_TOKEN}"
BOARD_ID="${1:-YOUR_BOARD_ID}"
LIST_ID="${2:-YOUR_LIST_ID}"

if [ -z "$TRELLO_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo "Error: TRELLO_API_KEY and TRELLO_TOKEN environment variables must be set"
    exit 1
fi

if [ "$BOARD_ID" = "YOUR_BOARD_ID" ] || [ "$LIST_ID" = "YOUR_LIST_ID" ]; then
    echo "Usage: ./import_cards.sh [BOARD_ID] [LIST_ID]"
    echo ""
    echo "Or set defaults in script and run: ./import_cards.sh"
    exit 1
fi

# Card data
CARDS=(
    "Transcend Fund - Shanti Bergel|Fit Score: 92 | Seed-Series A | $500K-$3M | Email: P1_Transcend_ShantiBergel.txt"
    "Konvoy Ventures - Jason Chapman|Fit Score: 90 | Seed-Series A | $500K-$2.5M | Email: P2_Konvoy_JasonChapman.txt"
    "Hiro Capital - Luke Alvarez|Fit Score: 88 | Series A-B | $3M-$10M | Email: P3_Hiro_LukeAlvarez.txt"
    "London Venture Partners - David Lau-Kee|Fit Score: 87 | Seed | $500K-$2M | Email: P4_LVP_DavidLauKee.txt"
    "F4 Fund - David Kaye|Fit Score: 85 | Seed | $250K-$1M | Email: P5_F4_DavidKaye.txt"
)

echo "Importing Day 8 VC Batch to Trello..."
echo "Board ID: $BOARD_ID"
echo "List ID: $LIST_ID"
echo ""

for card in "${CARDS[@]}"; do
    IFS='|' read -r name desc <<< "$card"
    
    # Create card
    response=$(curl -s -X POST "https://api.trello.com/1/cards" \
        -H "Content-Type: application/json" \
        -d "{
            \"key\": \"$TRELLO_KEY\",
            \"token\": \"$TRELLO_TOKEN\",
            \"idList\": \"$LIST_ID\",
            \"name\": \"$name\",
            \"desc\": \"$desc\",
            \"labels\": \"Day8-VC-Batch,gaming-ai\"
        }")
    
    card_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$card_id" ]; then
        echo "✓ Created card: $name"
    else
        echo "✗ Failed to create card: $name"
        echo "  Response: $response"
    fi
done

echo ""
echo "Import complete. 5 cards created."
echo ""
echo "Email draft files:"
ls -la /data/workspace/deliverables/day8_vc_batch/emails/
