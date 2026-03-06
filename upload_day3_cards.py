#!/usr/bin/env python3
"""
Upload Day 3 VC Packets to Trello
Creates cards in the 'Awaiting Approval' list with full packet details
"""

import json
import os
import sys
from datetime import datetime

# Trello board configuration
BOARD_ID = "699d2728fd2ae8c35d1f7a24"
AWAITING_APPROVAL_LIST_ID = "699d2728fd2ae8c35d1f7a48"

# Label IDs from the board
LABELS = {
    "Type: Outreach": "699d61a9030ed21b87cd55f0",
    "Priority: P1": "699d61a983ac3df2ba519d9a",
    "Effort: M": "699d61ab9b245142d5d1f708",
    "Workstream: Investor": "699d61ad8b85a16de2cfab43"
}

# Day 3 funds data
DAY3_FUNDS = [
    {
        "packet_id": "D1",
        "fund": "Play Ventures",
        "contact": "Henric Suuronen",
        "title": "Founding Partner",
        "email": "henric@playventures.vc",
        "check_size": "$200K-$5M",
        "stage": "Pre-seed, Seed, Series A",
        "location": "Singapore",
        "score": 82.0,
        "hook": "Play Ventures' focus on early-stage gaming and games-inspired consumer products",
        "thesis_fit": "Strong - gaming, consumer products, infrastructure",
        "opening": "Hi Henric,\n\nPlay Ventures' focus on early-stage gaming and games-inspired consumer products aligns well with what we're building.",
        "followup_d3": "2026-03-01",
        "followup_d7": "2026-03-05"
    },
    {
        "packet_id": "D2",
        "fund": "GFR Fund",
        "contact": "Yasushi Komori",
        "title": "Partner",
        "email": "yasushi@gfrfund.com",
        "check_size": "$100K-$5M",
        "stage": "Seed, Series A",
        "location": "San Francisco, CA",
        "score": 78.0,
        "hook": "GFR Fund's focus on disrupting consumer entertainment and gaming",
        "thesis_fit": "Strong - gaming, virtual worlds, entertainment",
        "opening": "Hi Yasushi,\n\nGFR Fund's focus on disrupting consumer entertainment and gaming resonates with what we're building.",
        "followup_d3": "2026-03-01",
        "followup_d7": "2026-03-05"
    },
    {
        "packet_id": "D3",
        "fund": "Makers Fund",
        "contact": "Michael Cheung",
        "title": "Founding General Partner",
        "email": "mike@makersfund.com",
        "check_size": "$500K-$40M",
        "stage": "Seed, Series A, Series B",
        "location": "United Kingdom",
        "score": 80.0,
        "hook": "Makers Fund's thesis on funding the next generation of creators and innovators",
        "thesis_fit": "Strong - gaming, creator economy, infrastructure",
        "opening": "Hi Mike,\n\nMakers Fund's thesis on funding the next generation of creators and innovators aligns with what we're building.",
        "followup_d3": "2026-03-01",
        "followup_d7": "2026-03-05"
    },
    {
        "packet_id": "D4",
        "fund": "London Venture Partners (LVP)",
        "contact": "David Lau-Kee",
        "title": "General Partner",
        "email": "david@londonvp.com",
        "check_size": "$100K-$2M",
        "stage": "Seed, Series A",
        "location": "London, UK",
        "score": 76.0,
        "hook": "LVP's singular focus on gaming as operating experts — not just financial investors",
        "thesis_fit": "Strongest - pure-play gaming fund",
        "opening": "Hi David,\n\nLVP's singular focus on gaming as operating experts — not just financial investors — sets you apart. That operational depth is why I'm reaching out.",
        "followup_d3": "2026-03-01",
        "followup_d7": "2026-03-05",
        "notes": "Team includes former King, Sony, EA executives"
    },
    {
        "packet_id": "D5",
        "fund": "Hiro Capital",
        "contact": "Luke Alvarez",
        "title": "Founding Managing Partner",
        "email": "luke@hiro.capital",
        "check_size": "$1M-$10M",
        "stage": "Series A, Series B",
        "location": "London/Luxembourg",
        "score": 74.0,
        "hook": "Hiro Capital's focus on Games, Esports and Digital Sports at the Series A/B stage",
        "thesis_fit": "Strong - games, esports, digital sports",
        "opening": "Hi Luke,\n\nHiro Capital's focus on Games, Esports and Digital Sports at the Series A/B stage is unique in Europe. Your track record with the initial $110M fund speaks for itself.",
        "followup_d3": "2026-03-01",
        "followup_d7": "2026-03-05",
        "notes": "Co-founded by Sir Ian Livingstone (Games Workshop legend)"
    }
]

def generate_card_description(fund):
    """Generate the card description for a fund packet"""
    return f"""## Snapshot
- Fund: {fund['fund']}
- HQ: {fund['location']}
- Stage focus: {fund['stage']}
- Check size: {fund['check_size']}
- ICP Tier: Priority A (score {fund['score']}/100)
- Geo coverage: Global
- Contact(s): {fund['email']}
- CRM Record: Pending remote DB (need to attach once live)

## Personalization & Why Now
{fund['hook']}.
We run an AI-assisted sourcing engine that scores 200+ gaming, AI, and devtools funds daily, assembles five investor packets every morning, and logs approvals + meetings directly in Slack and Trello.

Thesis fit: {fund['thesis_fit']}

## Outreach Plan
- Opening: {fund['opening']}
- CTA: Offer to send investor packet now + line up 30-min partner call next week.
- Owner: Ops (packet build) / Lucas (approval)
- Send target: 28 Feb 2026 12:00 CST

## Attachments & Proof
- Deck: Upload latest deck link once finalized
- Metrics: Insert February KPI snapshot
- Case Study: Highlight strongest gaming/AI proof point

## Follow-up
- Day 3 reminder: {fund['followup_d3']} via Slack ping
- Day 7 reminder: {fund['followup_d7']} + bump email
{f'- Notes: {fund["notes"]}' if 'notes' in fund else '- Notes: Update with replies / meetings'}
"""

def generate_checklist_items():
    """Generate standard checklist items for packet cards"""
    packet_build = [
        "Confirm fund HQ, stage focus, check size, and ICP tier",
        "Draft 2-3 sentence Why Now blurb referencing recent signal",
        "Capture partner/contact info with direct email + social proof",
        "Attach deck + metrics doc + case study/press links",
        "Write approval-ready outbound snippet (email or DM)"
    ]
    
    approval_followup = [
        "Link CRM record + status in description",
        "Assign owner + due date for send once approved",
        "Schedule Day 3 and Day 7 reminders (Follow-up list)",
        "Log Lucas approval decision + timestamp",
        "Record reply / meeting outcome in comments"
    ]
    
    return packet_build, approval_followup

def create_card_payload(fund):
    """Create the Trello card creation payload"""
    desc = generate_card_description(fund)
    packet_build, approval_followup = generate_checklist_items()
    
    # Due date for send target (Feb 28, 2026 12:00 CST = 18:00 UTC)
    due_date = "2026-02-28T18:00:00.000Z"
    
    payload = {
        "name": f"Packet: {fund['fund']}",
        "desc": desc,
        "idList": AWAITING_APPROVAL_LIST_ID,
        "idLabels": list(LABELS.values()),
        "due": due_date,
        "checklists": [
            {
                "name": "Packet Build",
                "checkItems": [{"name": item, "state": "incomplete"} for item in packet_build]
            },
            {
                "name": "Approval & Follow-up",
                "checkItems": [{"name": item, "state": "incomplete"} for item in approval_followup]
            }
        ]
    }
    
    return payload

def print_card_creation_commands():
    """Print curl commands to create cards (requires Trello API key/token)"""
    print("=" * 80)
    print("TRELLO CARD CREATION COMMANDS")
    print("=" * 80)
    print("\nPrerequisites:")
    print("  export TRELLO_API_KEY=your_api_key")
    print("  export TRELLO_TOKEN=your_token")
    print("\nRun these commands to create the Day 3 cards:\n")
    
    for fund in DAY3_FUNDS:
        payload = create_card_payload(fund)
        
        print(f"\n# Create card for {fund['fund']}")
        print(f"curl -X POST 'https://api.trello.com/1/cards' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{json.dumps(payload, indent=2).replace(chr(39), chr(39)+chr(39))}' \\")
        print(f"  --url-query 'key=$TRELLO_API_KEY' \\")
        print(f"  --url-query 'token=$TRELLO_TOKEN'")

def print_card_summary():
    """Print summary of cards to be created"""
    print("=" * 80)
    print("DAY 3 CARD UPLOAD SUMMARY")
    print("=" * 80)
    print(f"\nTarget List: Awaiting Approval")
    print(f"Number of cards to create: {len(DAY3_FUNDS)}\n")
    
    for fund in DAY3_FUNDS:
        print(f"  {fund['packet_id']}. {fund['fund']}")
        print(f"     Contact: {fund['contact']} ({fund['title']})")
        print(f"     Score: {fund['score']} | Location: {fund['location']}")
        print(f"     Check Size: {fund['check_size']}")
        print()

def print_recommended_moves():
    """Print recommended card moves for stale Day 1 packets"""
    print("=" * 80)
    print("RECOMMENDED CARD MOVES (Stale Day 1 Packets)")
    print("=" * 80)
    print("\nThe following cards in Daily Queue are 72+ hours old (last activity: 2026-02-24):")
    print("Current date: 2026-02-27\n")
    
    stale_cards = [
        ("Packet: BITKRAFT Ventures", "699d62440c53022f56dc42b1"),
        ("Packet: Variant", "699d62471bee2f60a50aab9a"),
        ("Packet: Collab+Currency", "699d6249d5248492eefc000e"),
        ("Packet: Konvoy Ventures", "699d624cdd614a5e0a62b5e3"),
        ("Packet: Mechanism Capital", "699d624efca4d3709cef25d5"),
        ("Daily intake automation", "699d30ec21f4e2916322c73d")
    ]
    
    print("CARDS TO MOVE:\n")
    for name, card_id in stale_cards[:5]:
        print(f"  → MOVE '{name}'")
        print(f"    From: Daily Queue")
        print(f"    To:   Awaiting Approval (if ready for Lucas review)")
        print(f"    Or:   Archive (if no longer relevant)")
        print(f"    Card ID: {card_id}")
        print()
    
    print("  → KEEP 'Daily intake automation' in Daily Queue")
    print("    (This is the automation card, not a packet)")
    print()

def generate_card_move_commands():
    """Generate curl commands to move stale cards"""
    print("=" * 80)
    print("CARD MOVE COMMANDS (Using Trello API)")
    print("=" * 80)
    print("\nPrerequisites:")
    print("  export TRELLO_API_KEY=your_api_key")
    print("  export TRELLO_TOKEN=your_token")
    print("\nMove stale Day 1 packet cards to Awaiting Approval:\n")
    
    stale_packet_cards = [
        ("BITKRAFT Ventures", "699d62440c53022f56dc42b1"),
        ("Variant", "699d62471bee2f60a50aab9a"),
        ("Collab+Currency", "699d6249d5248492eefc000e"),
        ("Konvoy Ventures", "699d624cdd614a5e0a62b5e3"),
        ("Mechanism Capital", "699d624efca4d3709cef25d5")
    ]
    
    AWAITING_APPROVAL_LIST_ID = "699d2728fd2ae8c35d1f7a48"
    
    for name, card_id in stale_packet_cards:
        print(f"# Move {name} to Awaiting Approval")
        print(f"curl -X PUT 'https://api.trello.com/1/cards/{card_id}' \\")
        print(f"  -d '{{\"idList\": \"{AWAITING_APPROVAL_LIST_ID}\"}}' \\")
        print(f"  --url-query 'key=$TRELLO_API_KEY' \\")
        print(f"  --url-query 'token=$TRELLO_TOKEN'")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--commands":
        print_card_creation_commands()
        print()
        generate_card_move_commands()
    else:
        print_card_summary()
        print()
        print_recommended_moves()
        print()
        print("Run with --commands flag to see API commands:")
        print("  python3 upload_day3_cards.py --commands")
