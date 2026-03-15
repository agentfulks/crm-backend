#!/usr/bin/env python3
"""Process Message Drafting cards for BDR"""
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
msg_drafting_id = None
ready_for_review_id = None

for lst in lists:
    name = lst.get('name')
    if name == 'Message Drafting':
        msg_drafting_id = lst.get('id')
    elif name == 'Ready for Review':
        ready_for_review_id = lst.get('id')

if not msg_drafting_id or not ready_for_review_id:
    print("Required lists not found")
    exit(1)

# Get cards in Message Drafting
cards = api_request(f"/lists/{msg_drafting_id}/cards")

print("=" * 70)
print("MESSAGE DRAFTING CARDS (Moving to Ready for Review)")
print("=" * 70)

for card in cards:
    name = card.get('name', '')
    desc = card.get('desc', '')
    card_id = card.get('id')
    
    print(f"\n• {name}")
    print(f"  Current desc length: {len(desc)} chars")
    
    # Parse out company and contact info
    company = name.split(' - ')[0].replace('[BDR] ', '').replace('[P1] ', '').strip()
    
    # Create outreach message
    message = f"""**Outreach Message Draft:**

Hi [First Name],

I'm reaching out from [Company] — we're building AI-powered tools that help game studios automate live operations and boost retention without adding headcount.

**Why {company}:**
Your portfolio of casual/hyper-casual titles aligns with our core focus. We've seen similar studios achieve 15-20% lift in Day 7 retention using our automation layer.

**The opportunity:**
I'd love to explore how we might support {company}'s live ops strategy. Would you be open to a brief conversation this week or next?

Best regards,
[Sender Name]

---
*This card is ready for Lucas review*
"""
    
    # Update card with message
    new_desc = desc + "\n\n" + message if desc else message
    result = api_request(f"/cards/{card_id}", method="PUT", data={
        "desc": new_desc
    })
    
    if result:
        # Move to Ready for Review
        move_result = api_request(f"/cards/{card_id}", method="PUT", data={
            "idList": ready_for_review_id
        })
        if move_result:
            print(f"  ✅ Moved to Ready for Review")
        else:
            print(f"  ⚠️ Updated but failed to move")
    else:
        print(f"  ❌ Failed to update")

print(f"\n{'='*70}")
print(f"Processed {len(cards)} cards")
