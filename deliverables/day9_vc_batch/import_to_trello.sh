#!/bin/bash
# Day 9 VC Batch - Trello Import Script
# Run this script to create cards in the Daily Queue
# Requires: TRELLO_API_KEY and TRELLO_TOKEN environment variables

BOARD_ID="tPkRdYjg"
LIST_NAME="Daily Queue"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Day 9 VC Batch - Trello Import ===${NC}"
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
    echo "  TRELLO_API_KEY=xxx TRELLO_TOKEN=yyy ./import_day9.sh"
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

# Card 1: BITKRAFT Ventures
echo "Creating Card 1/5: BITKRAFT Ventures - Carlos Pereira..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P1: BITKRAFT Ventures - Carlos Pereira" \
  -d "desc=**Fund:** BITKRAFT Ventures%0A**Partner:** Carlos Pereira (GP, Crypto & Gaming)%0A**Email:** carlos@bitkraft.vc%0A**Fit Score:** 94/100%0A%0A**Check Size:** \$500K - \$5M%0A**Stage:** Seed to Series B%0A**Recent Fund:** BITKRAFT Venture Fund 3 - \$275M (June 2025)%0A%0A**Key Investments:**%0A- Immutable X (Layer 2 gaming blockchain)%0A- Magic Eden (NFT marketplace, unicorn)%0A- Higgsfield (AI video, unicorn)%0A- Liminal Experiences (AI-powered gaming)%0A- GameRamp (AI-native publishing OS)%0A%0A**Outreach Angle:**%0ABITKRAFT's newly raised \$275M Fund 3 is actively deploying in AI-gaming intersections. Their 'Agents of Change' thesis explicitly targets autonomous agents and procedural world generation.%0A%0A**Email Draft:** deliverables/day9_vc_batch/emails/P1_BITKRAFT_CarlosPereira.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-06T17:00:00.000Z" > /dev/null

# Card 2: AI Grant
echo "Creating Card 2/5: AI Grant - Nat Friedman..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P2: AI Grant - Nat Friedman" \
  -d "desc=**Fund:** AI Grant%0A**Partner:** Nat Friedman (Co-Founder with Daniel Gross)%0A**Email:** nat@aigrant.com%0A**Fit Score:** 91/100%0A%0A**Check Size:** \$250K (grant) - \$1M+ (follow-on)%0A**Stage:** Pre-seed, Seed%0A**Recent Fund:** Andromeda Cluster expansion (2024)%0A%0A**Key Investments:**%0A- Cohere (AI foundation models - alumni)%0A- Cresta (AI - alumni)%0A- 60+ AI companies incubated since 2017%0A%0A**Outreach Angle:**%0AAI Grant's unique compute advantage via the Andromeda Cluster (4,000+ H100s) provides immediate infrastructure for training AI gaming models. Grant-first approach de-risks early-stage AI gaming experiments.%0A%0A**Email Draft:** deliverables/day9_vc_batch/emails/P2_AIGrant_NatFriedman.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-06T17:00:00.000Z" > /dev/null

# Card 3: Maven 11 Capital
echo "Creating Card 3/5: Maven 11 Capital - Balder Bomans..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P3: Maven 11 - Balder Bomans" \
  -d "desc=**Fund:** Maven 11 Capital%0A**Partner:** Balder Bomans (Managing Partner & CIO)%0A**Email:** balder@maven11.com%0A**Fit Score:** 88/100%0A%0A**Check Size:** \$500K - \$5M%0A**Stage:** Seed to Series A%0A**Recent Fund:** Fund III - \$107M (March 2025)%0A%0A**Key Investments:**%0A- Beam (gaming blockchain)%0A- Stardust (wallet infrastructure for games)%0A- Openfort (gaming account abstraction)%0A- Saga (chainlets for gaming)%0A%0A**Outreach Angle:**%0AMaven 11's freshly raised \$107M Fund III is explicitly focused on AI-crypto intersection and gaming infrastructure. 2024 predictions call out gaming-specific blockchain infrastructure emergence.%0A%0A**Email Draft:** deliverables/day9_vc_batch/emails/P5_Maven11_BalderBomans.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-06T17:00:00.000Z" > /dev/null

# Card 4: Lux Capital
echo "Creating Card 4/5: Lux Capital - Shahin Farshchi..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P4: Lux Capital - Shahin Farshchi" \
  -d "desc=**Fund:** Lux Capital%0A**Partner:** Shahin Farshchi (General Partner)%0A**Email:** shahin@luxcapital.com%0A**Fit Score:** 86/100%0A%0A**Check Size:** \$500K - \$50M+ (multi-stage)%0A**Stage:** Seed to Growth%0A**Recent Fund:** Fund IX - \$1.5B (January 2026)%0A%0A**Key Investments:**%0A- W4 Games (Godot Engine commercial)%0A- Runway AI (generative video)%0A- Applied Intuition (AI simulation)%0A- 26 unicorns including Unconventional AI (2025)%0A%0A**Outreach Angle:**%0ALux's 'Riskgaming' initiative and Q4 2024 report on Moravec's Paradox show deep engagement with AI gaming/simulation. Fresh \$1.5B Fund IX provides ample capital for seed-stage AI infrastructure bets.%0A%0A**Email Draft:** deliverables/day9_vc_batch/emails/P3_Lux_ShahinFarshchi.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-06T17:00:00.000Z" > /dev/null

# Card 5: Polychain Capital
echo "Creating Card 5/5: Polychain Capital - Olaf Carlson-Wee..."
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=$TRELLO_API_KEY" \
  -d "token=$TRELLO_TOKEN" \
  -d "idList=$LIST_ID" \
  -d "name=P5: Polychain - Olaf Carlson-Wee" \
  -d "desc=**Fund:** Polychain Capital%0A**Partner:** Olaf Carlson-Wee (Founder & CEO)%0A**Email:** olaf@polychain.capital%0A**Fit Score:** 84/100%0A%0A**Check Size:** \$500K - \$10M+%0A**Stage:** Seed to Growth%0A**AUM:** \$5B+%0A%0A**Key Investments:**%0A- Dapper Labs (NBA Top Shot, Flow blockchain)%0A- Immutable X (Layer 2 gaming)%0A- Axie Infinity (play-to-earn gaming)%0A- Gala Games (blockchain gaming)%0A%0A**Outreach Angle:**%0AOlaf founded Polychain after being Coinbase's first employee—understands crypto infrastructure and platform scaling. Investment in Dapper Labs and Immutable X shows commitment to gaming infrastructure.%0A%0A**Email Draft:** deliverables/day9_vc_batch/emails/P4_Polychain_OlafCarlsonWee.txt%0A%0A**Status:** Ready to send" \
  -d "due=2026-03-06T17:00:00.000Z" > /dev/null

echo ""
echo -e "${GREEN}✅ Day 9 batch import complete!${NC}"
echo ""
echo "5 cards created in Daily Queue:"
echo "  1. BITKRAFT Ventures - Carlos Pereira (Fit: 94)"
echo "  2. AI Grant - Nat Friedman (Fit: 91)"
echo "  3. Maven 11 - Balder Bomans (Fit: 88)"
echo "  4. Lux Capital - Shahin Farshchi (Fit: 86)"
echo "  5. Polychain - Olaf Carlson-Wee (Fit: 84)"
echo ""
echo -e "${YELLOW}Next: Move cards to 'Awaiting Approval' for review${NC}"
