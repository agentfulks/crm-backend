#!/bin/bash
#
# Day 12 VC Batch - Trello Import Script
# This script creates Trello cards for the Day 12 VC outreach batch
#
# Prerequisites:
#   - Trello API Key: https://trello.com/app-key
#   - Trello Token: Generated from API key page
#   - Board ID and List ID for target list
#
# Usage:
#   export TRELLO_API_KEY="your_api_key"
#   export TRELLO_TOKEN="your_token"
#   export TRELLO_LIST_ID="your_list_id"
#   ./import_to_trello.sh
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPORT_JSON="${SCRIPT_DIR}/trello_import.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    if [ -z "$TRELLO_API_KEY" ]; then
        echo -e "${RED}Error: TRELLO_API_KEY environment variable not set${NC}"
        echo "Get your API key at: https://trello.com/app-key"
        exit 1
    fi

    if [ -z "$TRELLO_TOKEN" ]; then
        echo -e "${RED}Error: TRELLO_TOKEN environment variable not set${NC}"
        echo "Generate a token from your API key page"
        exit 1
    fi

    if [ -z "$TRELLO_LIST_ID" ]; then
        echo -e "${RED}Error: TRELLO_LIST_ID environment variable not set${NC}"
        echo "Get list ID from: https://api.trello.com/1/boards/{BOARD_ID}/lists?key={KEY}&token={TOKEN}"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is required but not installed${NC}"
        echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)"
        exit 1
    fi

    if [ ! -f "$IMPORT_JSON" ]; then
        echo -e "${RED}Error: Import JSON not found at ${IMPORT_JSON}${NC}"
        exit 1
    fi
}

# Create a single Trello card
create_card() {
    local name="$1"
    local description="$2"
    local due="$3"
    local labels="$4"

    # Build label parameters
    local label_params=""
    IFS=',' read -ra LABEL_ARRAY <<< "$labels"
    for label in "${LABEL_ARRAY[@]}"; do
        label_params="${label_params}&idLabels=${label}"
    done

    echo -e "${YELLOW}Creating card: ${name}${NC}"

    # Create card
    local response
    response=$(curl -s -X POST \
        "https://api.trello.com/1/cards?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}&idList=${TRELLO_LIST_ID}&name=$(jq -nr --arg n "$name" '$n|@uri')&desc=$(jq -nr --arg d "$description" '$d|@uri')&due=${due}${label_params}")

    if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
        local card_id
        card_id=$(echo "$response" | jq -r '.id')
        local card_url
        card_url=$(echo "$response" | jq -r '.shortUrl')
        echo -e "${GREEN}✓ Created card: ${card_url}${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create card: ${name}${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Main import function
import_cards() {
    echo "=== Day 12 VC Batch - Trello Import ==="
    echo "Import file: ${IMPORT_JSON}"
    echo "Target list ID: ${TRELLO_LIST_ID}"
    echo ""

    local total_cards
    total_cards=$(jq '.cards | length' "$IMPORT_JSON")
    echo "Found ${total_cards} cards to import"
    echo ""

    local success_count=0
    local fail_count=0

    for ((i=0; i<total_cards; i++)); do
        local name
        local description
        local due
        local labels

        name=$(jq -r ".cards[${i}].name" "$IMPORT_JSON")
        description=$(jq -r ".cards[${i}].description" "$IMPORT_JSON")
        due=$(jq -r ".cards[${i}].due" "$IMPORT_JSON")

        # Join labels array into comma-separated string
        labels=$(jq -r ".cards[${i}].labels | join(',')" "$IMPORT_JSON")

        if create_card "$name" "$description" "$due" "$labels"; then
            ((success_count++))
        else
            ((fail_count++))
        fi

        # Rate limiting - be nice to Trello API
        sleep 0.5
    done

    echo ""
    echo "=== Import Summary ==="
    echo -e "${GREEN}Success: ${success_count}${NC}"
    if [ $fail_count -gt 0 ]; then
        echo -e "${RED}Failed: ${fail_count}${NC}"
        exit 1
    else
        echo "Failed: 0"
    fi
}

# Alternative: Create cards with label names (labels must exist on board)
# This function maps label names to label IDs
import_cards_with_label_mapping() {
    echo "=== Day 12 VC Batch - Trello Import (with label mapping) ==="
    echo ""
    echo "Note: This version requires labels to already exist on the target board."
    echo "Make sure these labels exist: Day-12, Fit-Score-91, Fit-Score-88, Fit-Score-85, Fit-Score-87, Fit-Score-84, Ready"
    echo ""

    # Get board ID from list
    local board_id
    board_id=$(curl -s "https://api.trello.com/1/lists/${TRELLO_LIST_ID}?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" | jq -r '.idBoard')

    echo "Target board ID: ${board_id}"

    # Fetch all labels on the board
    local labels_json
    labels_json=$(curl -s "https://api.trello.com/1/boards/${board_id}/labels?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}")

    local total_cards
    total_cards=$(jq '.cards | length' "$IMPORT_JSON")
    echo "Found ${total_cards} cards to import"
    echo ""

    local success_count=0
    local fail_count=0

    for ((i=0; i<total_cards; i++)); do
        local name
        local description
        local due
        local label_names

        name=$(jq -r ".cards[${i}].name" "$IMPORT_JSON")
        description=$(jq -r ".cards[${i}].description" "$IMPORT_JSON")
        due=$(jq -r ".cards[${i}].due" "$IMPORT_JSON")
        label_names=$(jq -r ".cards[${i}].labels[]" "$IMPORT_JSON")

        # Map label names to IDs
        local label_ids=""
        while IFS= read -r label_name; do
            local label_id
            label_id=$(echo "$labels_json" | jq -r ".[] | select(.name == \"${label_name}\") | .id")
            if [ -n "$label_id" ] && [ "$label_id" != "null" ]; then
                label_ids="${label_ids}&idLabels=${label_id}"
            else
                echo -e "${YELLOW}Warning: Label '${label_name}' not found on board${NC}"
            fi
        done <<< "$label_names"

        echo -e "${YELLOW}Creating card: ${name}${NC}"

        # Create card
        local response
        response=$(curl -s -X POST \
            "https://api.trello.com/1/cards?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}&idList=${TRELLO_LIST_ID}&name=$(jq -nr --arg n "$name" '$n|@uri')&desc=$(jq -nr --arg d "$description" '$d|@uri')&due=${due}${label_ids}")

        if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
            local card_url
            card_url=$(echo "$response" | jq -r '.shortUrl')
            echo -e "${GREEN}✓ Created card: ${card_url}${NC}"
            ((success_count++))
        else
            echo -e "${RED}✗ Failed to create card: ${name}${NC}"
            echo "Response: $response"
            ((fail_count++))
        fi

        sleep 0.5
    done

    echo ""
    echo "=== Import Summary ==="
    echo -e "${GREEN}Success: ${success_count}${NC}"
    echo -e "${RED}Failed: ${fail_count}${NC}"
}

# Print usage
usage() {
    echo "Day 12 VC Batch - Trello Import Script"
    echo ""
    echo "Usage:"
    echo "  export TRELLO_API_KEY='your_api_key'"
    echo "  export TRELLO_TOKEN='your_token'"
    echo "  export TRELLO_LIST_ID='your_list_id'"
    echo "  $0 [basic|labels]"
    echo ""
    echo "Modes:"
    echo "  basic   - Create cards without labels (default)"
    echo "  labels  - Create cards with label mapping (requires labels to exist)"
    echo ""
    echo "Setup:"
    echo "  1. Get API Key: https://trello.com/app-key"
    echo "  2. Generate Token from API key page"
    echo "  3. Get List ID from: https://api.trello.com/1/boards/{BOARD_ID}/lists?key={KEY}&token={TOKEN}"
}

# Main
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    usage
    exit 0
fi

check_prerequisites

MODE="${1:-basic}"

case "$MODE" in
    basic)
        import_cards
        ;;
    labels)
        import_cards_with_label_mapping
        ;;
    *)
        echo -e "${RED}Unknown mode: ${MODE}${NC}"
        usage
        exit 1
        ;;
esac

echo ""
echo "Import complete!"
