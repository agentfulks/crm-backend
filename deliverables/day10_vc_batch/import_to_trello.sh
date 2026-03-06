#!/bin/bash

# Day 10 VC Batch - Trello Import Script
# Creates Trello cards for 5 gaming VC funds
# Usage: ./import_to_trello.sh

set -e

# Configuration - Set these environment variables or modify directly
TRELLO_API_KEY="${TRELLO_API_KEY:-YOUR_API_KEY}"
TRELLO_TOKEN="${TRELLO_TOKEN:-YOUR_TOKEN}"
BOARD_ID="${TRELLO_BOARD_ID:-tPkRdYjg}"
LIST_NAME="${TRELLO_LIST_NAME:-Daily Queue}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================"
echo "Day 10 VC Batch - Trello Import"
echo "======================================"
echo ""

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: sudo apt-get install jq (Debian/Ubuntu) or brew install jq (macOS)"
    exit 1
fi

# Verify credentials
if [ "$TRELLO_API_KEY" = "YOUR_API_KEY" ] || [ "$TRELLO_TOKEN" = "YOUR_TOKEN" ]; then
    echo -e "${YELLOW}Warning: Trello credentials not set.${NC}"
    echo "Set environment variables:"
    echo "  export TRELLO_API_KEY=your_key"
    echo "  export TRELLO_TOKEN=your_token"
    echo ""
    echo "Or modify this script directly."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get list ID
echo "Fetching list ID for '$LIST_NAME'..."
LIST_ID=$(curl -s "https://api.trello.com/1/boards/$BOARD_ID/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | \
    jq -r ".[] | select(.name==\"$LIST_NAME\") | .id")

if [ -z "$LIST_ID" ]; then
    echo -e "${RED}Error: Could not find list '$LIST_NAME' on board.${NC}"
    echo "Available lists:"
    curl -s "https://api.trello.com/1/boards/$BOARD_ID/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | \
        jq -r '.[].name'
    exit 1
fi

echo -e "${GREEN}Found list ID: $LIST_ID${NC}"
echo ""

# Card 1: a16z Games - Andrew Chen
echo "Creating Card 1/5: [P1] a16z Games - Andrew Chen..."
curl -s -X POST "https://api.trello.com/1/cards" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "key=$TRELLO_API_KEY" \
    --data-urlencode "token=$TRELLO_TOKEN" \
    --data-urlencode "idList=$LIST_ID" \
    --data-urlencode "name=[P1] a16z Games - Andrew Chen" \
    --data-urlencode "desc=**Fund:** a16z Games
**Partner:** Andrew Chen (General Partner)
**Email:** andrew@a16z.com
**Fit Score:** 92/100
**Stage:** Pre-seed to Series A
**Check Size:** \$500K - \$5M+
**Recent Fund:** Games Fund Two - \$600M (June 2025)
**Tags:** gaming, AI, speedrun, infrastructure, social-platforms

**Fit Breakdown:**
- Gaming as Platform Thesis: 20/20
- AI Creative Tools Focus: 19/20
- Speedrun Accelerator Fit: 18/20
- a16z Network Effects: 18/20
- Check Size Flexibility: 17/20

**Key Investments:**
- Riot Games (League of Legends)
- Discord (gaming communication)
- Roblox (user-generated content platform)
- Sky Mavis/Axie Infinity (blockchain gaming)
- Singularity 6 (Paleo Pines)
- Series (AI game development platform)
- 40+ AI startups through Speedrun

**Outreach Angle:**
a16z Games' newly raised \$600M Fund Two (June 2025) is actively deploying in AI-gaming intersections. Andrew Chen's expertise in network effects and platform growth is legendary. The Speedrun accelerator provides a perfect entry point for NEXUS AI's stage.

---

**EMAIL DRAFT:**

To: andrew@a16z.com
Subject: Speedrun + the infrastructure layer for AI-powered social gaming

Hi Andrew,

a16z Games' \$600M Fund Two close in June and the continued momentum of Speedrun signal serious conviction that games are becoming the next-generation social platform. With 40+ AI startups already in the portfolio, you're seeing firsthand what happens when creative tools meet interactive entertainment.

NEXUS AI is building the infrastructure layer that makes those AI-powered social experiences actually scalable. While Speedrun companies push the boundaries of generative content and player-driven creation, we handle the runtime architecture—enabling persistent AI agents, dynamic world states, and procedural narrative systems that don't explode compute costs as communities grow.

Your essays on cold start problems and network effects are required reading for a reason. They explain why the next wave of gaming platforms will be defined by their ability to generate engaging content algorithmically. We're already piloting with studios that have cut AI runtime costs by 60% while shipping persistent multiplayer features they couldn't build before.

Worth a 15-minute conversation? I'd love to share how NEXUS enables the AI-powered social gaming experiences that Speedrun is betting on.

[CALENDLY_LINK]

Best,
Lucas Fulks
Founder, NEXUS AI

---

**Status:** Ready to send
**Due Date:** 2026-03-03" \
    --data-urlencode "due=2026-03-03T17:00:00.000Z" > /dev/null
echo -e "${GREEN}✓ Card 1 created${NC}"

# Card 2: Griffin Gaming Partners - Peter Levin
echo "Creating Card 2/5: [P2] Griffin Gaming Partners - Peter Levin..."
curl -s -X POST "https://api.trello.com/1/cards" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "key=$TRELLO_API_KEY" \
    --data-urlencode "token=$TRELLO_TOKEN" \
    --data-urlencode "idList=$LIST_ID" \
    --data-urlencode "name=[P2] Griffin Gaming Partners - Peter Levin" \
    --data-urlencode "desc=**Fund:** Griffin Gaming Partners
**Partner:** Peter Levin (Managing Director & Co-Founder)
**Email:** peter@griffingp.com
**Fit Score:** 90/100
**Stage:** Seed to Series A (Multi-stage)
**Check Size:** \$500K - \$5M+
**AUM:** \$1.5B
**Tags:** gaming, infrastructure, multi-stage, platforms

**Fit Breakdown:**
- Gaming Native Fund: 20/20
- AI Infrastructure Focus: 18/20
- Deep Operational Expertise: 18/20
- Strategic Portfolio Alignment: 17/20
- Check Size Flexibility: 17/20

**Key Investments:**
- Discord (gaming communication platform, \$15B+ valuation)
- Scopely (mobile gaming, acquired by Savvy Games for \$4.9B)
- AppLovin (mobile marketing, IPO)
- Overwolf (gaming platform/infrastructure)
- Second Dinner (Marvel Snap, \$100M+ funding)
- Spyke Games (mobile gaming, \$55M Series A)
- WinZO (social gaming platform, India)

**Outreach Angle:**
Griffin's portfolio of Discord, Overwolf, and Second Dinner demonstrates deep commitment to gaming infrastructure and social platforms. Peter Levin's background as President of Interactive Ventures at Lionsgate provides unique perspective on content-tech convergence.

---

**EMAIL DRAFT:**

To: peter@griffingp.com
Subject: Discord + Overwolf portfolio → the next gaming infrastructure play

Hi Peter,

Griffin's track record speaks for itself—Discord, Overwolf, Scopely, Second Dinner. You've consistently identified infrastructure and platform plays that reshape how gamers connect, create, and play. Your Lionsgate/Nerdist background gives you unique insight into where content and technology converge.

NEXUS AI is building the infrastructure layer for the next generation of gaming platforms. While Overwolf enables creators to build on top of existing games and Discord connects gaming communities, we're creating the runtime architecture for AI-powered persistent worlds—where NPCs have memory, environments evolve based on player behavior, and procedural content generation scales to millions of concurrent users.

The multi-stage flexibility Griffin offers is perfect for our roadmap: seed entry to prove the platform, Series A follow-on to scale with studios already piloting NEXUS. We're seeing 10x efficiency gains for developers building AI-powered multiplayer experiences.

Would you have 15 minutes next week to discuss how NEXUS fits Griffin's vision for gaming infrastructure?

[CALENDLY_LINK]

Best,
Lucas Fulks
Founder, NEXUS AI

---

**Status:** Ready to send
**Due Date:** 2026-03-03" \
    --data-urlencode "due=2026-03-03T17:00:00.000Z" > /dev/null
echo -e "${GREEN}✓ Card 2 created${NC}"

# Card 3: Galaxy Interactive - Sam Englebardt
echo "Creating Card 3/5: [P3] Galaxy Interactive - Sam Englebardt..."
curl -s -X POST "https://api.trello.com/1/cards" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "key=$TRELLO_API_KEY" \
    --data-urlencode "token=$TRELLO_TOKEN" \
    --data-urlencode "idList=$LIST_ID" \
    --data-urlencode "name=[P3] Galaxy Interactive - Sam Englebardt" \
    --data-urlencode "desc=**Fund:** Galaxy Interactive
**Partner:** Sam Englebardt (Co-Founder and General Partner)
**Email:** sam@galaxyinteractive.io
**Fit Score:** 88/100
**Stage:** Seed to Series A
**Check Size:** \$500K - \$3M
**Recent Fund:** Fund II - \$325M (October 2021)
**Tags:** gaming, AI, interactive, spatial-computing, blockchain

**Fit Breakdown:**
- Gaming Intersection Focus: 20/20
- AI Infrastructure Thesis: 18/20
- Strategic Platform Vision: 17/20
- Portfolio Synergies: 17/20
- Check Size Alignment: 16/20

**Key Investments:**
- Mythical Games (blockchain gaming, NFL Rivals)
- 1047 Games (Splitgate, \$100M+ raised)
- Immutable X (Layer 2 gaming blockchain)
- Genvid (interactive streaming technology)
- GreenPark Sports (virtual fan experiences)
- Republic (investment platform, gaming exposure)
- StockX (sneaker marketplace, gaming crossover)

**Outreach Angle:**
Galaxy Interactive's explicit thesis on gaming-born technology fueling AI and spatial computing directly aligns with NEXUS AI's infrastructure play. The 'Interactive is eating the world' framing perfectly captures the NEXUS AI opportunity.

---

**EMAIL DRAFT:**

To: sam@galaxyinteractive.io
Subject: \"Interactive is eating the world\" → the infrastructure thesis behind it

Hi Sam,

Galaxy Interactive's thesis that \"Interactive is eating the world\" perfectly captures what's happening as gaming-born technology—GPUs, real-time engines, user-driven systems—now powers AI, blockchain, and spatial computing. Your portfolio at Mythical Games and Immutable X demonstrates conviction that the next computing platforms will emerge from gaming infrastructure.

NEXUS AI is building that exact infrastructure layer. We enable game developers to create persistent, AI-powered worlds where autonomous agents generate content, modify environments in real-time, and create emergent gameplay that scales beyond manual design constraints. While your portfolio companies build the platforms and experiences players engage with, we provide the runtime architecture that makes AI-generated content viable in production multiplayer environments.

The convergence of immersive technology, AI, and interactive entertainment is creating new categories of experiences that weren't possible before. We're already working with studios that are cutting AI runtime costs by 60% while shipping features that were previously cost-prohibitive.

I'd love 15 minutes to show you the infrastructure layer making \"Interactive is eating the world\" a technical reality. When works for you?

[CALENDLY_LINK]

Best,
Lucas Fulks
Founder, NEXUS AI

---

**Status:** Ready to send
**Due Date:** 2026-03-04" \
    --data-urlencode "due=2026-03-04T17:00:00.000Z" > /dev/null
echo -e "${GREEN}✓ Card 3 created${NC}"

# Card 4: Makers Fund - Jay Chi
echo "Creating Card 4/5: [P4] Makers Fund - Jay Chi..."
curl -s -X POST "https://api.trello.com/1/cards" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "key=$TRELLO_API_KEY" \
    --data-urlencode "token=$TRELLO_TOKEN" \
    --data-urlencode "idList=$LIST_ID" \
    --data-urlencode "name=[P4] Makers Fund - Jay Chi" \
    --data-urlencode "desc=**Fund:** Makers Fund
**Partner:** Jay Chi (Founding Partner)
**Email:** jay@makersfund.com
**Fit Score:** 87/100
**Stage:** Seed to Series A
**Check Size:** \$1M - \$5M+
**Recent Fund:** Fund III - \$500M (March 2022)
**Tags:** gaming, interactive-entertainment, AI-infrastructure, hands-on

**Fit Breakdown:**
- Gaming Exclusive Focus: 20/20
- AI Infrastructure Interest: 18/20
- Hands-On Operational Support: 17/20
- Check Size Alignment: 16/20
- Global Gaming Network: 16/20

**Key Investments:**
- Scopely (mobile gaming, \$4.9B exit)
- Voodoo (hyper-casual mobile games)
- FundamentalVR (VR surgical training)
- Lila Games (mobile FPS)
- Kepler Interactive (publisher collective)
- Inworld AI (AI NPC platform)
- Portkey Games (WB Games, Hogwarts Legacy)

**Outreach Angle:**
Makers Fund's exclusive focus on interactive entertainment makes them ideal partners for NEXUS AI. Their investment in Inworld AI demonstrates active interest in AI-gaming intersections. The fund's hands-on approach offers operational value beyond capital.

---

**EMAIL DRAFT:**

To: jay@makersfund.com
Subject: Inworld AI + the runtime infrastructure powering AI-native gaming

Hi Jay,

Makers Fund's exclusive focus on interactive entertainment and your investment in Inworld AI show clear conviction that AI is fundamentally changing what's possible in gaming. But while Inworld enables smarter NPCs through natural language, studios still struggle to run AI at scale in production multiplayer environments—NEXUS AI solves that runtime infrastructure gap.

We're building the engine that enables persistent AI agents, dynamic world evolution, and real-time inference at unit economics that work for live games. Your portfolio companies like Scopely (congrats on the \$4.9B exit), Voodoo, and Lila Games understand the difference between demo AI and production AI. The studios we're piloting with have cut AI runtime costs by 60% while shipping persistent multiplayer features they couldn't build before.

Makers Fund's hands-on approach and global network across Tokyo, London, San Francisco, and Singapore aligns perfectly with our stage. We need strategic guidance navigating the complex gaming landscape as much as we need capital.

Worth a 15-minute conversation to explore how NEXUS AI fits Makers Fund's AI infrastructure thesis?

[CALENDLY_LINK]

Best,
Lucas Fulks
Founder, NEXUS AI

---

**Status:** Ready to send
**Due Date:** 2026-03-04" \
    --data-urlencode "due=2026-03-04T17:00:00.000Z" > /dev/null
echo -e "${GREEN}✓ Card 4 created${NC}"

# Card 5: GFR Fund - Yasushi Komori
echo "Creating Card 5/5: [P5] GFR Fund - Yasushi Komori..."
curl -s -X POST "https://api.trello.com/1/cards" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "key=$TRELLO_API_KEY" \
    --data-urlencode "token=$TRELLO_TOKEN" \
    --data-urlencode "idList=$LIST_ID" \
    --data-urlencode "name=[P5] GFR Fund - Yasushi Komori" \
    --data-urlencode "desc=**Fund:** GFR Fund
**Partner:** Yasushi Komori (General Partner)
**Email:** yasushi@gfrfund.com
**Fit Score:** 85/100
**Stage:** Seed to Series A
**Check Size:** \$100K - \$5M
**Tags:** gaming, generative-AI, creator-economy, consumer-tech

**Fit Breakdown:**
- Gaming AI Convergence Focus: 19/20
- Consumer Entertainment Expertise: 17/20
- Check Size Flexibility: 17/20
- Global Market Access: 16/20
- Founder Collaborative Approach: 16/20

**Key Investments:**
- GEEIQ (gaming/metaverse data platform)
- Omeda Studios (Predecessor game)
- Alinea Invest (community-first investing)
- Magma (gaming community platform)
- Multiple stealth AI gaming companies
- Creator economy platforms with gaming applications

**Outreach Angle:**
GFR Fund's explicit focus on gaming and generative AI convergence aligns perfectly with NEXUS AI's positioning. Yasushi Komori's Gamescom 2025 presence and thought leadership on AI-gaming trends demonstrate active engagement. Strong Asia network offers geographic expansion potential.

---

**EMAIL DRAFT:**

To: yasushi@gfrfund.com
Subject: GEEIQ + the convergence of gaming, AI, and creator infrastructure

Hi Yasushi,

GFR Fund's thesis on the convergence of gaming, generative AI, and digital communities is exactly where NEXUS AI is building. Your portfolio company GEEIQ provides data infrastructure for brands entering gaming—we're building the runtime infrastructure that enables those brands to create AI-powered, persistent experiences that evolve and engage players at scale.

Your thought leadership at Gamescom 2025 on AI-gaming trends and your collaborative approach with founders building at the intersection of Asian and Western markets resonates with our vision. We're creating the AI-native engine for procedural world generation, enabling autonomous agents to generate content, modify environments in real-time, and create emergent gameplay in persistent multiplayer worlds.

The studios we're piloting with have cut AI runtime costs by 60% while shipping features—dynamic NPCs with memory, evolving world states, procedural narrative systems—that were previously cost-prohibitive. Your check size flexibility (\$100K-\$5M) provides the runway we need to prove the platform before scaling with larger rounds.

I'd welcome 15 minutes to show you how NEXUS AI fits GFR's thesis on gaming-AI convergence and explore potential synergies with your portfolio. When works for you?

[CALENDLY_LINK]

Best,
Lucas Fulks
Founder, NEXUS AI

---

**Status:** Ready to send
**Due Date:** 2026-03-05" \
    --data-urlencode "due=2026-03-05T17:00:00.000Z" > /dev/null
echo -e "${GREEN}✓ Card 5 created${NC}"

echo ""
echo "======================================"
echo -e "${GREEN}Import complete!${NC}"
echo "======================================"
echo ""
echo "5 cards created in '$LIST_NAME':"
echo "  • [P1] a16z Games - Andrew Chen (Due: 2026-03-03)"
echo "  • [P2] Griffin Gaming Partners - Peter Levin (Due: 2026-03-03)"
echo "  • [P3] Galaxy Interactive - Sam Englebardt (Due: 2026-03-04)"
echo "  • [P4] Makers Fund - Jay Chi (Due: 2026-03-04)"
echo "  • [P5] GFR Fund - Yasushi Komori (Due: 2026-03-05)"
echo ""
echo "Next steps:"
echo "  1. Review cards in Trello"
echo "  2. Add labels (Day-10, Fit-Score-XX, Ready)"
echo "  3. Update [CALENDLY_LINK] placeholders"
echo "  4. Move to appropriate list when ready"
echo ""
