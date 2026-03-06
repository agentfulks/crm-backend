#!/bin/bash
#===============================================================================
# TRELLO CARD AUTO-CREATION SCRIPT
#===============================================================================
# This script creates all 5 outreach cards on your Trello board once you have
# API credentials configured.
#
# PREREQUISITES:
#   1. Set environment variables (add to ~/.bashrc or ~/.zshrc):
#      export TRELLO_API_KEY="your_api_key"
#      export TRELLO_TOKEN="your_token"
#      export TRELLO_BOARD_ID="your_board_id"
#
#   2. Get your credentials from: https://trello.com/app-key
#
#   3. Get your board ID from the board URL or via API
#
# USAGE:
#   chmod +x create_trello_cards.sh
#   ./create_trello_cards.sh
#
# OUTPUT:
#   Creates 5 cards in the "Daily Queue" list (or first list on board)
#   Cards include: name, description, labels, and checklist items
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required environment variables
check_env() {
    local missing=0
    if [[ -z "$TRELLO_API_KEY" ]]; then
        echo -e "${RED}ERROR: TRELLO_API_KEY not set${NC}"
        missing=1
    fi
    if [[ -z "$TRELLO_TOKEN" ]]; then
        echo -e "${RED}ERROR: TRELLO_TOKEN not set${NC}"
        missing=1
    fi
    if [[ -z "$TRELLO_BOARD_ID" ]]; then
        echo -e "${RED}ERROR: TRELLO_BOARD_ID not set${NC}"
        missing=1
    fi
    
    if [[ $missing -eq 1 ]]; then
        echo ""
        echo "Please set the required environment variables:"
        echo "  export TRELLO_API_KEY='your_api_key'"
        echo "  export TRELLO_TOKEN='your_token'"
        echo "  export TRELLO_BOARD_ID='your_board_id'"
        echo ""
        echo "Get your API key at: https://trello.com/app-key"
        exit 1
    fi
}

# Get the first list ID from the board (assumes "Daily Queue" or similar)
get_list_id() {
    local board_id=$1
    local list_name
    
    echo -e "${YELLOW}Fetching lists from board...${NC}"
    
    # Try to find "Daily Queue" list first
    list_id=$(curl -s "https://api.trello.com/1/boards/${board_id}/lists?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); print([l['id'] for l in data if 'Daily' in l['name'] or 'Queue' in l['name']][0])" 2>/dev/null || echo "")
    
    if [[ -z "$list_id" ]]; then
        # Fall back to first list
        list_id=$(curl -s "https://api.trello.com/1/boards/${board_id}/lists?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" | \
            python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null || echo "")
    fi
    
    echo "$list_id"
}

# Create a single card
create_card() {
    local list_id=$1
    local name=$2
    local description=$3
    local labels=$4
    
    echo -e "${YELLOW}Creating card: ${name}${NC}"
    
    # URL encode the name and description
    local encoded_name=$(echo "$name" | python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip()))")
    local encoded_desc=$(echo "$description" | python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip()))")
    
    # Create the card
    local response=$(curl -s -X POST "https://api.trello.com/1/cards" \
        -d "key=${TRELLO_API_KEY}" \
        -d "token=${TRELLO_TOKEN}" \
        -d "idList=${list_id}" \
        -d "name=${encoded_name}" \
        -d "desc=${encoded_desc}")
    
    local card_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")
    
    if [[ -z "$card_id" ]]; then
        echo -e "${RED}Failed to create card: ${name}${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Created card ID: ${card_id}${NC}"
    
    # Add labels if specified
    if [[ -n "$labels" ]]; then
        add_labels "$card_id" "$labels"
    fi
    
    # Add checklist
    add_checklist "$card_id" "$name"
    
    return 0
}

# Add labels to a card
add_labels() {
    local card_id=$1
    local labels=$2
    
    # Trello label colors
    declare -A label_colors
    label_colors["Priority-A"]="green"
    label_colors["Priority-B"]="yellow"
    label_colors["Priority-C"]="orange"
    label_colors["Ready-to-Send"]="blue"
    label_colors["Sent"]="purple"
    
    IFS=',' read -ra LABEL_ARRAY <<< "$labels"
    for label in "${LABEL_ARRAY[@]}"; do
        label=$(echo "$label" | xargs) # trim whitespace
        local color=${label_colors[$label]:-"null"}
        
        # Try to find existing label or create new one
        echo -e "${YELLOW}  Adding label: ${label}${NC}"
        curl -s -X POST "https://api.trello.com/1/cards/${card_id}/idLabels" \
            -d "key=${TRELLO_API_KEY}" \
            -d "token=${TRELLO_TOKEN}" \
            -d "color=${color}" \
            -d "name=${label}" > /dev/null
    done
}

# Add checklist to a card
add_checklist() {
    local card_id=$1
    local card_name=$2
    
    echo -e "${YELLOW}  Adding checklist${NC}"
    
    # Create checklist
    local checklist_response=$(curl -s -X POST "https://api.trello.com/1/checklists" \
        -d "key=${TRELLO_API_KEY}" \
        -d "token=${TRELLO_TOKEN}" \
        -d "idCard=${card_id}" \
        -d "name=Send Workflow")
    
    local checklist_id=$(echo "$checklist_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")
    
    if [[ -z "$checklist_id" ]]; then
        echo -e "${RED}  Failed to create checklist${NC}"
        return 1
    fi
    
    # Add checklist items
    local items=(
        "Move to Awaiting Approval"
        "Review email template"
        "Approve for send"
        "Send email"
        "Move to Sent"
        "Log in sent_log.csv"
        "Schedule Day 3 follow-up"
        "Schedule Day 7 follow-up"
    )
    
    for item in "${items[@]}"; do
        curl -s -X POST "https://api.trello.com/1/checklists/${checklist_id}/checkItems" \
            -d "key=${TRELLO_API_KEY}" \
            -d "token=${TRELLO_TOKEN}" \
            -d "name=${item}" > /dev/null
    done
    
    return 0
}

# Main execution
main() {
    echo "=================================================================="
    echo "  TRELLO CARD AUTO-CREATION SCRIPT"
    echo "=================================================================="
    echo ""
    
    # Check environment
    check_env
    
    # Get list ID
    local list_id=$(get_list_id "$TRELLO_BOARD_ID")
    if [[ -z "$list_id" ]]; then
        echo -e "${RED}ERROR: Could not find a list on the board${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Using list ID: ${list_id}${NC}"
    echo ""
    
    # Card data
    declare -a names
    declare -a descriptions
    declare -a labels
    
    names[0]="[P1] BITKRAFT Ventures - Martin Garcia, CFO & General Partner"
    descriptions[0]="Priority: P1
Contact: Martin Garcia
Email: martin@bitkraft.vc
Check Size: \$500K-\$10M USD
Stage: Seed, Series A, Series B
Score: 84.0 (Rank #1)

Thesis Fit: Gaming, esports, immersive technology (Synthetic Reality focus)
Hook: Founder-built infrastructure alignment
Contact Source: ZoomInfo (medium confidence)
HQ: Los Angeles, California

Email: manual_execution_bridge/P1_BITKRAFT_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04"
    labels[0]="Priority-A,Ready-to-Send"
    
    names[1]="[P2] Konvoy Ventures - Taylor Hurst, Principal"
    descriptions[1]="Priority: P2
Contact: Taylor Hurst
Email: taylor@konvoy.vc
Check Size: \$500K-\$3M USD
Stage: Pre-Seed, Seed, Series A
Score: 59.33 (Rank #2)

Thesis Fit: Gaming infrastructure and platform bets
Hook: Infrastructure play - daily VC scoring engine
Contact Source: LinkedIn (medium confidence)
HQ: Denver, Colorado

Email: manual_execution_bridge/P2_Konvoy_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04"
    labels[1]="Priority-B,Ready-to-Send"
    
    names[2]="[P3] Mechanism Capital - Steve Cho, Partner"
    descriptions[2]="Priority: P3
Contact: Steve Cho (Head of Mech Play)
Email: steve@mechanism.capital
Check Size: \$1M-\$2M USD
Stage: Pre-seed, Seed, Series A
Score: 53.33 (Rank #3)

Thesis Fit: Blockchain, DeFi, crypto-gaming
Hook: Crypto-gaming meets AI
Contact Source: RocketReach (HIGH confidence)
Special: Former Apple App Store Games, leads web3 gaming deals

Email: manual_execution_bridge/P3_Mechanism_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04"
    labels[2]="Priority-C,Ready-to-Send"
    
    names[3]="[P4] Collab+Currency - Derek Edwards, Managing Partner"
    descriptions[3]="Priority: P4
Contact: Derek Edwards
Email: derek@collabcurrency.com
Check Size: \$100K-\$3M USD
Stage: Pre-Seed, Seed
Score: 51.33 (Rank #4)

Thesis Fit: Intersection of crypto and culture
Hook: Crypto x culture - daily investor packets as product
Contact Source: Twitter (medium confidence)
HQ: Eugene, Oregon
Special: Former attorney and startup founder

Email: manual_execution_bridge/P4_CollabCurrency_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04"
    labels[3]="Priority-C,Ready-to-Send"
    
    names[4]="[P5] Variant - Spencer Noon, Co-Founder & General Partner"
    descriptions[4]="Priority: P5
Contact: Spencer Noon
Email: spencer@variant.fund
Check Size: \$1M-\$5M USD
Stage: Pre-Seed, Seed, Series A
Score: 48.33 (Rank #5)

Thesis Fit: User ownership and alignment
Hook: User-owned VC sourcing - AI engine + partner approval
Contact Source: Twitter (medium confidence)
HQ: New York, NY / Distributed
Special: Runs OurNetwork newsletter, DeFi/Crypto focus

Email: manual_execution_bridge/P5_Variant_email.txt
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

Target Send: 2026-02-25 16:00 UTC
Follow-up Day 3: 2026-02-28
Follow-up Day 7: 2026-03-04"
    labels[4]="Priority-C,Ready-to-Send"
    
    # Create all cards
    local success=0
    local failed=0
    
    for i in {0..4}; do
        if create_card "$list_id" "${names[$i]}" "${descriptions[$i]}" "${labels[$i]}"; then
            ((success++))
        else
            ((failed++))
        fi
        echo ""
    done
    
    echo "=================================================================="
    echo -e "${GREEN}SUMMARY: ${success} cards created successfully${NC}"
    if [[ $failed -gt 0 ]]; then
        echo -e "${RED}         ${failed} cards failed${NC}"
    fi
    echo "=================================================================="
    
    exit $failed
}

# Run main function
main "$@"
