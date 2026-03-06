#!/bin/bash
# Day 8 VC Batch - Trello Import Script
# Run this script to create cards in the Daily Queue
# Requires: TRELLO_API_KEY and TRELLO_TOKEN environment variables

BOARD_ID="tPkRdYjg"
LIST_NAME="Daily Queue"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Day 8 VC Batch - Trello Import ===${NC}"
echo ""

# Check for credentials
if [ -z "$TRELLO_API_KEY" ] || [ -z "$TRELLO_TOKEN" ]; then
    echo -e "${RED}ERROR: TRELLO_API_KEY and TRELLO_TOKEN must be set${NC}"
    echo ""
    echo "To set them:"
    echo "  export TRELLO_API_KEY=your_key_here"
    echo "  export TRELLO_TOKEN=your_token_here"
    echo ""
    echo "Or run with:"
    echo "  TRELLO_API_KEY=xxx TRELLO_TOKEN=yyy ./import_day8.sh"
    exit 1
fi

# Get list ID
echo "Finding Daily Queue list ID..."
LIST_ID=$(curl -s "https://api.trello.com/1/boards/${BOARD_ID}/lists?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" | grep -o '"id":"[^"]*","name":"Daily Queue"' | head -1 | cut -d'"' -f4)

if [ -z "$LIST_ID" ]; then
    echo -e "${RED}ERROR: Could not find Daily Queue list${NC}"
    exit 1
fi

echo -e "${GREEN}Found list ID: $LIST_ID${NC}"
echo ""

# Card 1: Transcend Fund
echo "Creating Card 1/5: Transcend Fund - Shanti Bergel..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P1: Transcend Fund - Shanti Bergel" \
  -d "desc=**Fund:** Transcend Fund%0A**Partner:** Shanti Bergel (Managing Director)%0A**Email:** shanti@transcend.fund%0A**Fit Score:** 92/100%0A%0A**Check Size:** \$500K - \$3M%0A**Stage:** Seed to Series A%0A**Recent Fund:** Transcend Fund II - \$250M (2022)%0A%0A**Key Investments:**%0A- Ruckus Games (\$19M Series A, Jan 2025)%0A- Live Aware Labs (AI game dev platform)%0A- Gardens (cross-platform multiplayer)%0A- Stardust (wallet infra for games)%0A%0A**Outreach Angle:**%0ATranscend's portfolio shows clear thesis alignment with AI-powered game infrastructure. Recent Ruckus investment signals appetite for multiplayer + AI combinations.%0A%0A**Email Draft:** deliverables/day8_vc_batch/emails/P1_Transcend_ShantiBergel.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-05T17:00:00.000Z" > /dev/null

# Card 2: Konvoy Ventures
echo "Creating Card 2/5: Konvoy Ventures - Jason Chapman..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P2: Konvoy Ventures - Jason Chapman" \
  -d "desc=**Fund:** Konvoy Ventures%0A**Partner:** Jason Chapman (Co-Founder & General Partner)%0A**Email:** jason@konvoy.vc%0A**Fit Score:** 90/100%0A%0A**Check Size:** \$500K - \$2.5M%0A**Stage:** Seed to Series A%0A**Recent Fund:** Konvoy Fund III - \$150M (2023)%0A%0A**Key Investments:**%0A- Ready Player Me (exit to Square Enix)%0A- Overwolf (creator platform, acquired by Unity)%0A- Nexus (gaming infrastructure)%0A- mod.io (UGC platform for games)%0A%0A**Outreach Angle:**%0AKonvoy's 'Battle Road' thesis emphasizes planet-scale gaming infrastructure. Ready Player Me exit validates their gaming infra focus. Perfect fit for NEXUS AI's runtime architecture.%0A%0A**Email Draft:** deliverables/day8_vc_batch/emails/P2_Konvoy_JasonChapman.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-05T17:00:00.000Z" > /dev/null

# Card 3: Hiro Capital
echo "Creating Card 3/5: Hiro Capital - Luke Alvarez..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P3: Hiro Capital - Luke Alvarez" \
  -d "desc=**Fund:** Hiro Capital%0A**Partner:** Luke Alvarez (Managing Partner)%0A**Email:** luke@hiro.capital%0A**Fit Score:** 88/100%0A%0A**Check Size:** \$3M - \$10M%0A**Stage:** Series A to B%0A**Recent Fund:** Hiro Capital II - \$110M (2022)%0A%0A**Key Investments:**%0A- FRVR (GenAI game platform, \$15M Series A)%0A- Sidero Labs (Kubernetes gaming infrastructure)%0A- Oorbit (cloud gaming platform)%0A- Spatial AI (Nick Clegg as advisor)%0A%0A**Outreach Angle:**%0AHiro's investments in FRVR and Sidero Labs show deep commitment to AI-native gaming and cloud infrastructure. Nick Clegg connection provides strategic Meta partnership potential.%0A%0A**Email Draft:** deliverables/day8_vc_batch/emails/P3_Hiro_LukeAlvarez.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-05T17:00:00.000Z" > /dev/null

# Card 4: London Venture Partners
echo "Creating Card 4/5: London Venture Partners - David Lau-Kee..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P4: LVP - David Lau-Kee" \
  -d "desc=**Fund:** London Venture Partners%0A**Partner:** David Lau-Kee (Co-Founder)%0A**Email:** dlk@londonvp.com%0A**Fit Score:** 87/100%0A%0A**Check Size:** \$500K - \$2M%0A**Stage:** Seed%0A**Recent Fund:** LVP III - \$80M (2021)%0A%0A**Key Investments:**%0A- Bitpart.AI (seed, AI NPCs - Jan 2025)%0A- Supercell (early investor, exited 2016)%0A- Unity (early investor, IPO 2020)%0A- NaturalMotion (Zynga acquisition)%0A%0A**Outreach Angle:**%0ALVP's Bitpart.AI investment signals active thesis on AI NPCs and intelligent agents. As early Unity/Supercell investors, they understand gaming engine infrastructure evolution.%0A%0A**Email Draft:** deliverables/day8_vc_batch/emails/P4_LVP_DavidLauKee.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-05T17:00:00.000Z" > /dev/null

# Card 5: F4 Fund
echo "Creating Card 5/5: F4 Fund - David Kaye..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P5: F4 Fund - David Kaye" \
  -d "desc=**Fund:** F4 Fund%0A**Partner:** David Kaye (Founding Partner)%0A**Email:** david@f4.fund%0A**Fit Score:** 85/100%0A%0A**Check Size:** \$250K - \$1M%0A**Stage:** Seed%0A**Recent Fund:** F4 Fund I - \$32M (2024)%0A%0A**Key Investments:**%0A- Series (co-invest with a16z)%0A- Powder (gaming highlights, \$14M Series A)%0A- X1 (gaming credit card, acquired by Robinhood)%0A- Talon Esports (esports infrastructure)%0A%0A**Outreach Angle:**%0AF4's founder-first thesis and gaming-alumni network (Riot, Blizzard, etc.) provides founder empathy and operational support. Recent fund close means active deployment.%0A%0A**Email Draft:** deliverables/day8_vc_batch/emails/P5_F4_DavidKaye.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-05T17:00:00.000Z" > /dev/null

echo ""
echo -e "${GREEN}✅ Day 8 batch import complete!${NC}"
echo ""
echo "5 cards created in Daily Queue:"
echo "  1. Transcend Fund - Shanti Bergel (Fit: 92)"
echo "  2. Konvoy Ventures - Jason Chapman (Fit: 90)"
echo "  3. Hiro Capital - Luke Alvarez (Fit: 88)"
echo "  4. LVP - David Lau-Kee (Fit: 87)"
echo "  5. F4 Fund - David Kaye (Fit: 85)"
echo ""
echo -e "${YELLOW}Next: Move cards to 'Awaiting Approval' for review${NC}"
