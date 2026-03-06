#!/bin/bash
# Trello Card Creation Script for BDR Research Queue
# Run this script with TRELLO_API_KEY and TRELLO_TOKEN environment variables set

BOARD_ID="699f37680e0b1bc16721ae44"
LIST_NAME="Research Queue"

# Get the List ID for "Research Queue"
LIST_ID=$(curl -s "https://api.trello.com/1/boards/${BOARD_ID}/lists?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" | grep -o '"id":"[^"]*","name":"Research Queue"' | cut -d'"' -f4)

if [ -z "$LIST_ID" ]; then
    echo "Error: Could not find 'Research Queue' list. Please check board ID and permissions."
    exit 1
fi

echo "Found Research Queue list ID: $LIST_ID"
echo "Creating 12 studio cards..."
echo ""

# Card 1: Amplitude Studios
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=Amplitude Studios — [Lead Contact TBD] — Independence + Endless Legend 2" \
  -d "desc=## Studio Summary%0A**Website:** https://www.amplitude-studios.com%0A**Location:** Paris, France%0A**Size:** ~100 employees%0A**Focus:** PC/Console Strategy (4X)%0A**Funding Status:** €12M Series A (May 2025), newly independent from Sega%0A%0A## Recent Games%0A- Endless Legend 2 (Early Access Sept 2025)%0A- Endless Space series%0A- Humankind%0A- Endless Dungeon%0A%0A## Key Contacts%0A- TBD (Research LinkedIn leadership)%0A%0A## Growth Signals%0A- €12M Series A led by Griffin Gaming Partners (May 2025)%0A- Independence from Sega (Nov 2024)%0A- Early Access launch for Endless Legend 2%0A%0A## Outreach Angle%0AFresh independence + major funding = budget for partnerships. PC strategy specialist with live ops content pipeline.%0A%0A## Source%0AHollywood Reporter, GamesIndustry.biz (May 2025)" \
  -d "due=2026-03-07" \
  -d "idLabels=green" > /dev/null && echo "✓ Card 1 created: Amplitude Studios"

# Card 2: Mainframe Industries
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=Mainframe Industries — [Lead Contact TBD] — Cloud-Native MMO" \
  -d "desc=## Studio Summary%0A**Website:** https://www.mainframeindustries.com%0A**Location:** Reykjavik, Iceland / Helsinki, Finland%0A**Size:** ~50-80 employees%0A**Focus:** PC/Console/Cloud MMO%0A**Funding Status:** €20M+ raised (a16z, Maki.vc, Play Ventures)%0A%0A## Recent Games%0A- Unnamed cloud-native open world social sandbox MMO (in development)%0A- Cross-platform: mobile, PC, TV%0A%0A## Key Contacts%0A- TBD (Research Nordic leadership team)%0A%0A## Growth Signals%0A- €20M+ from top-tier VCs including a16z%0A- Solsten partnership for player research%0A- Actively hiring across Nordic region%0A%0A## Outreach Angle%0ABuilding next-gen cloud MMO infrastructure. Strong VC backing indicates expansion budget. Nordic hub with international reach.%0A%0A## Source%0ANordic9, GamesIndustry.biz, Crunchbase" \
  -d "due=2026-03-07" > /dev/null && echo "✓ Card 2 created: Mainframe Industries"

# Card 3: Toys for Bob
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=Toys for Bob — Paul Yan/Avery Lodato — Independent + Xbox Partnership" \
  -d "desc=## Studio Summary%0A**Website:** https://www.toysforbob.com%0A**Location:** Novato, California, USA%0A**Size:** ~50-100 employees%0A**Focus:** PC/Console (AAA Indie)%0A**Funding Status:** Xbox development deal (2024), newly independent%0A%0A## Recent Games%0A- Crash Bandicoot 4: It's About Time%0A- Spyro Reignited Trilogy%0A- Skylanders series%0A%0A## Key Contacts%0A- Paul Yan (Co-Studio Head)%0A- Avery Lodato (Co-Studio Head)%0A%0A## Growth Signals%0A- Independent since May 2024 (spun from Activision/Microsoft)%0A- Signed development deal with Xbox for first indie title%0A- Veteran AAA console team%0A%0A## Outreach Angle%0ARecently independent with Xbox backing = flexibility + budget. Proven console experience. Looking to establish new partnerships as indie.%0A%0A## Source%0AGamesIndustry.biz, IGN, Variety (March-June 2024)" \
  -d "due=2026-03-07" > /dev/null && echo "✓ Card 3 created: Toys for Bob"

# Card 4: That's No Moon
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=That's No Moon — [CEO TBD] — \$110M+ AAA Single-Player" \
  -d "desc=## Studio Summary%0A**Website:** https://www.thatsnomoon.com%0A**Location:** Los Angeles, California, USA%0A**Size:** ~192 employees (PitchBook)%0A**Focus:** PC/Console AAA Single-Player%0A**Funding Status:** \$110M+ from Smilegate Entertainment%0A%0A## Recent Games%0A- Unannounced AAA single-player narrative game (in development)%0A- Veteran team from Uncharted, The Last of Us, Call of Duty%0A%0A## Key Contacts%0A- Nick Kononelos (CEO) - former EA/Activision%0A%0A## Growth Signals%0A- \$100M Smilegate investment (2021)%0A- Additional \$9.69M seed (2023)%0A- Rapid team growth to 192 employees%0A%0A## Outreach Angle%0AWell-funded AAA studio with clear vision. Building narrative/live ops infrastructure. Partnership with Korean giant Smilegate.%0A%0A## Source%0ALA Business Journal, Tracxn, PitchBook" \
  -d "due=2026-03-07" > /dev/null && echo "✓ Card 4 created: That's No Moon"

# Card 5: Something Wicked Games
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=Something Wicked Games — Jeff Gardiner — \$13.2M Open World RPG" \
  -d "desc=## Studio Summary%0A**Website:** https://www.somethingwickedgames.com%0A**Location:** USA%0A**Size:** ~40-60 employees%0A**Focus:** PC/Console Open World RPG%0A**Funding Status:** \$13.2M Seed (NetEase lead, March 2024)%0A%0A## Recent Games%0A- Untitled open world RPG (in development)%0A- Spiritual successor to Fallout/Skyrim-style games%0A%0A## Key Contacts%0A- Jeff Gardiner (Founder) - 15+ years at Bethesda%0A%0A## Growth Signals%0A- \$13M seed from NetEase%0A- Team formed by Bethesda/Obsidian veterans%0A- Building ambitious open world RPG%0A%0A## Outreach Angle%0AFresh funding with proven Bethesda talent. Open world RPG = long-term live ops potential. NetEase backing = international expansion.%0A%0A## Source%0AGamesBeat, CB Insights, Crunchbase (June 2024)" \
  -d "due=2026-03-08" > /dev/null && echo "✓ Card 5 created: Something Wicked Games"

echo ""
echo "Tier-1 cards (5) created successfully!"
echo ""
echo "To create Tier-2 and Tier-3 cards, run the extended script."
