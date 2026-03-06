#!/bin/bash
# Day 13 Trello Import Script
# Run this to create cards in the Daily Queue

BOARD_ID="tPkRdYjg"
LIST_NAME="Daily Queue"
API_KEY="${TRELLO_API_KEY}"
API_TOKEN="${TRELLO_TOKEN}"

# Check for credentials
if [ -z "$API_KEY" ] || [ -z "$API_TOKEN" ]; then
    echo "Error: TRELLO_API_KEY and TRELLO_TOKEN must be set"
    echo "Get them at: https://trello.com/app-key"
    exit 1
fi

# Get list ID
LIST_ID=$(curl -s "https://api.trello.com/1/boards/${BOARD_ID}/lists?key=${API_KEY}&token=${API_TOKEN}" | jq -r ".[] | select(.name == \"${LIST_NAME}\") | .id")

if [ -z "$LIST_ID" ]; then
    echo "Error: Could not find list '${LIST_NAME}'"
    exit 1
fi

echo "Importing Day 13 cards to list: ${LIST_NAME}"
echo ""

# Card 1: Superscrypt
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${API_KEY}" \
  -d "token=${API_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=P1 | Superscrypt | Alina Kornienko | Fit: 90" \
  -d "desc=**Fund:** Superscrypt%0A**Partner:** Alina Kornienko (Partner)%0A**Email:** alina@superscrypt.xyz%0A**Stage:** Seed / Series A%0A**Check Size:** \$500K - \$3M%0A**AUM:** \$250M+ (Fund II deploying)%0A%0A**Fit Score:** 90/100%0A%0ASee full packet: deliverables/day13_vc_batch/" \
  -d "due=2026-02-28T09:00:00Z" > /dev/null
echo "✓ Created: Superscrypt (Alina Kornienko)"

# Card 2: Sisu
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${API_KEY}" \
  -d "token=${API_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=P2 | Sisu Game Ventures | Samuli Seppala | Fit: 89" \
  -d "desc=**Fund:** Sisu Game Ventures%0A**Partner:** Samuli Seppala (Managing Partner)%0A**Email:** samuli@sisu.vc%0A**Stage:** Pre-seed / Seed%0A**Check Size:** \$100K - \$1M%0A**AUM:** \$60M (Fund II raised Jan 2026)%0A%0A**Fit Score:** 89/100%0A%0ASee full packet: deliverables/day13_vc_batch/" \
  -d "due=2026-02-28T09:00:00Z" > /dev/null
echo "✓ Created: Sisu (Samuli Seppala)"

# Card 3: Initial Capital
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${API_KEY}" \
  -d "token=${API_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=P3 | Initial Capital | Mateusz Drozd | Fit: 87" \
  -d "desc=**Fund:** Initial Capital%0A**Partner:** Mateusz Drozd (General Partner)%0A**Email:** mateusz@initial.capital%0A**Stage:** Pre-seed / Seed%0A**Check Size:** \$250K - \$2M%0A**AUM:** \$75M%0A%0A**Fit Score:** 87/100%0A%0ASee full packet: deliverables/day13_vc_batch/" \
  -d "due=2026-02-28T09:00:00Z" > /dev/null
echo "✓ Created: Initial Capital (Mateusz Drozd)"

# Card 4: Theorycraft
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${API_KEY}" \
  -d "token=${API_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=P4 | Theorycraft Ventures | Joe Hsu | Fit: 86" \
  -d "desc=**Fund:** Theorycraft Ventures%0A**Partner:** Joe Hsu (Partner)%0A**Email:** joe@theorycraftgames.com%0A**Stage:** Seed%0A**Check Size:** \$500K - \$5M%0A**AUM:** \$150M%0A%0A**Fit Score:** 86/100%0A%0ASee full packet: deliverables/day13_vc_batch/" \
  -d "due=2026-02-28T09:00:00Z" > /dev/null
echo "✓ Created: Theorycraft (Joe Hsu)"

# Card 5: Pixeldust
curl -s -X POST "https://api.trello.com/1/cards" \
  -d "key=${API_KEY}" \
  -d "token=${API_TOKEN}" \
  -d "idList=${LIST_ID}" \
  -d "name=P5 | Pixeldust Ventures | Yanev Stoimenov | Fit: 85" \
  -d "desc=**Fund:** Pixeldust Ventures%0A**Partner:** Yanev Stoimenov (Managing Partner)%0A**Email:** yanev@pixeldust.vc%0A**Stage:** Pre-seed / Seed%0A**Check Size:** \$100K - \$1.5M%0A**AUM:** \$35M%0A%0A**Fit Score:** 85/100%0A%0ASee full packet: deliverables/day13_vc_batch/" \
  -d "due=2026-02-28T09:00:00Z" > /dev/null
echo "✓ Created: Pixeldust (Yanev Stoimenov)"

echo ""
echo "Day 13 import complete!"
echo "Created 5 cards in '${LIST_NAME}'"
