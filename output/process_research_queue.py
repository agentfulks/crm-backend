#!/usr/bin/env python3
"""Process Research Queue cards for BDR"""
import os
import json
import urllib.request

MATON_API_KEY = os.environ.get('MATON_API_KEY')
BOARD_ID = "699f37680e0b1bc16721ae44"

def api_request(path, method="GET", data=None):
    url = f"https://gateway.maton.ai/trello/1{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {MATON_API_KEY}")
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

# Get lists
lists = api_request(f"/boards/{BOARD_ID}/lists")
research_queue_id = None
contact_research_id = None

for lst in lists:
    name = lst.get('name')
    if name == 'Research Queue':
        research_queue_id = lst.get('id')
    elif name == 'Contact Research':
        contact_research_id = lst.get('id')

if not research_queue_id or not contact_research_id:
    print("Required lists not found")
    exit(1)

# Get cards in Research Queue
cards = api_request(f"/lists/{research_queue_id}/cards")

print("=" * 70)
print("RESEARCH QUEUE CARDS")
print("=" * 70)

# Quick research data for known studios
research_data = {
    "Scopely": {"ceo": "Walter Driver", "focus": "Mobile games, monetization", "notable": "Monopoly GO, Stumble Guys"},
    "Playrix": {"ceo": "Dmitry Bukhman", "focus": "Match-3, casual", "notable": "Homescapes, Gardenscapes"},
    "Dream Games": {"ceo": "Soner Aydemir", "focus": "Puzzle games", "notable": "Royal Match ($1B+ revenue)"},
    "Miniclip": {"ceo": "Saad Choudri", "focus": "Mobile, web games", "notable": "8 Ball Pool, Agar.io"},
    "Zynga": {"ceo": "Frank Gibeau (EA)", "focus": "Social casino, hyper-casual", "notable": "Owned by Take-Two"},
    "Amanotes": {"ceo": "Bill Vo", "focus": "Music games", "notable": "Tiles Hop, Magic Tiles"},
    "FunPlus": {"ceo": "Andy Zhong", "focus": "Strategy, 4X", "notable": "State of Survival, King of Avalon"},
    "Mintegral": {"ceo": "Michael Wang", "focus": "Mobile marketing, in-app", "notable": "Mobvista subsidiary"},
    "Garena": {"ceo": "Forrest Li", "focus": "Gaming platform, esports", "notable": "Free Fire, Sea Limited"},
    "Ketchapp": {"ceo": "Ubisoft", "focus": "Hyper-casual", "notable": "2048, Stack, Knife Hit"},
}

for card in cards:
    name = card.get('name', '')
    card_id = card.get('id')
    
    # Clean up company name
    company = name.strip()
    
    print(f"\n• {company}")
    
    # Get research data
    data = research_data.get(company, {})
    
    if data:
        research_note = f"""**Research Notes:**

**Company:** {company}
**CEO/Lead:** {data.get('ceo', 'TBD')}
**Focus:** {data.get('focus', 'TBD')}
**Notable:** {data.get('notable', 'TBD')}

**Outreach Angle:**
AI-powered live ops automation for mobile gaming. Target: {data.get('focus', 'mobile gaming')} portfolio.

**Status:** Ready for contact research
"""
    else:
        research_note = f"""**Research Notes:**

**Company:** {company}
**Status:** Needs deeper research

**Action Items:**
- [ ] Identify CEO/Partnerships lead
- [ ] Find funding stage
- [ ] Research portfolio focus
- [ ] Look for live ops indicators
"""
    
    # Update card
    result = api_request(f"/cards/{card_id}", method="PUT", data={
        "desc": research_note
    })
    
    if result:
        # Move to Contact Research
        move_result = api_request(f"/cards/{card_id}", method="PUT", data={
            "idList": contact_research_id
        })
        if move_result:
            print(f"  ✅ Moved to Contact Research")
        else:
            print(f"  ⚠️ Updated but failed to move")
    else:
        print(f"  ❌ Failed to update")

print(f"\n{'='*70}")
print(f"Processed {len(cards)} cards")
