#!/usr/bin/env python3
"""
BDR Message Drafter - Process Trello cards and draft personalized outreach messages
"""
import urllib.request
import os
import json

MATON_API_KEY = os.environ.get("MATON_API_KEY")
BASE_URL = "https://gateway.maton.ai/trello/1"
READY_FOR_REVIEW_LIST_ID = "699f376e916d1293ac8a24c2"

def api_call(path, method="GET", data=None):
    """Make API call to Maton Gateway"""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    req.add_header('Accept', 'application/json')
    
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error on {method} {path}: {e}")
        return None

def add_comment(card_id, text):
    """Add a comment to a Trello card"""
    return api_call(f"/cards/{card_id}/actions/comments", method="POST", data={"text": text})

def move_card(card_id, list_id):
    """Move a card to a different list"""
    return api_call(f"/cards/{card_id}", method="PUT", data={"idList": list_id})

# Message templates based on studio profile
def draft_message(studio_name, contact_name, focus, notable_games, size, recent_news, hq):
    """Draft a personalized outreach message"""
    
    # Extract first name
    first_name = contact_name.split()[0] if contact_name else "there"
    
    # Customize based on studio size and focus
    if "hyper-casual" in focus.lower() or "Hyper-casual" in focus:
        hook = f"With {notable_games} and your rapid release cycle, you're clearly masters of the hyper-casual format."
        value_prop = "Our platform helps hyper-casual teams scale content production without scaling headcount—automating live ops workflows so you can test more concepts faster."
    elif "match-3" in focus.lower() or "puzzle" in focus.lower():
        hook = f"{notable_games} shows you understand what keeps players coming back daily."
        value_prop = "We help puzzle studios automate live ops personalization at scale—delivering the right content to the right players without overwhelming your team."
    elif "idle" in focus.lower():
        hook = f"{notable_games} demonstrates your expertise in long-term retention mechanics."
        value_prop = "Our analytics infrastructure is built specifically for idle games—helping you optimize progression curves and monetization events in real-time."
    elif "casino" in focus.lower() or "social casino" in focus.lower():
        hook = f"Running {notable_games} at scale means your live ops team is constantly balancing retention and monetization."
        value_prop = "We provide enterprise-grade analytics and personalization tools that help social casino operators maximize LTV while maintaining compliance."
    elif "public" in size.lower() or "traded" in size.lower() or "NASDAQ" in size:
        hook = f"As a publicly-traded studio with hits like {notable_games}, you need analytics that satisfy both your product team and your investors."
        value_prop = "Our platform delivers real-time performance dashboards and automated reporting that give leadership instant visibility into portfolio health."
    else:
        hook = f"Your work on {notable_games} shows a team that knows how to build engaging mobile experiences."
        value_prop = "We help mobile game studios automate their live ops and analytics infrastructure—so your team can focus on creating great player experiences."
    
    message = f"""Subject: Quick question about {studio_name}'s live ops scaling

Hi {first_name},

{hook}

{value_prop}

Would you be open to a brief 15-minute call to see if this could be a fit for {studio_name}?

Best,
Lucas
"""
    return message

# Cards to process with their research data
cards_to_process = [
    {
        "id": "69a8913a58bb8b5430028f6f",
        "studio": "Kwalee",
        "contact": "David Darling CBE",
        "focus": "Hyper-casual, Hybrid-casual, Casual",
        "games": "Draw It, Shoot Out 3D, Teacher Simulator",
        "size": "Large (500M+ downloads)",
        "news": "Largest hypercasual publisher in UK",
        "hq": "Leamington Spa, UK"
    },
    {
        "id": "69a7fc7e065b150b2ebfef26",
        "studio": "Supercent",
        "contact": "Gong Jun-sik",
        "focus": "Hyper-casual publishing",
        "games": "Kingdom game series",
        "size": "Medium (Subsidiary of 111%)",
        "news": "2024 Korea Content Awards Ministerial Award",
        "hq": "Seoul, South Korea"
    },
    {
        "id": "69a8913bac68accb5d3998a0",
        "studio": "Moonee",
        "contact": "Erez Mishli",
        "focus": "Mobile game publishing, monetization",
        "games": "Published titles portfolio",
        "size": "Medium",
        "news": "Pocket Gamer Connects London 2024 participation",
        "hq": "Israel"
    },
    {
        "id": "69a8913bf097d06ca2980bab",
        "studio": "TapNation",
        "contact": "Hervé Montoute",
        "focus": "Hyper-casual publishing",
        "games": "Ice Cream Inc, 1B+ downloads milestone",
        "size": "Medium",
        "news": "1 billion downloads milestone, UAhero acquisition",
        "hq": "Paris, France"
    },
    {
        "id": "69a7fcc1bf5a87c56d8d9f88",
        "studio": "Devsisters",
        "contact": "Gil-Hyun Cho",
        "focus": "Midcore, Cookie Run IP",
        "games": "Cookie Run: Kingdom, Cookie Run: Braverse TCG",
        "size": "Large",
        "news": "Expanding CookieRun Card Game to Roblox in 2026",
        "hq": "Seoul, South Korea"
    },
    {
        "id": "69a891e65140c682359d95d8",
        "studio": "Playgendary",
        "contact": "Dmitriy Shelengovskiy",
        "focus": "Casual mobile games",
        "games": "Kick the Buddy, Polysphere, Tank Stars, Masters franchise",
        "size": "Large (300+ employees, 2B+ installs)",
        "news": "Remote team across multiple offices",
        "hq": "Limassol, Cyprus"
    },
    {
        "id": "69a956ec032c008646fd260a",
        "studio": "Azur Games",
        "contact": "Dmitry Yaminsky",
        "focus": "Hyper-casual",
        "games": "Hit games portfolio, 8B+ installs",
        "size": "Large (8B+ installs)",
        "news": "Topped 8B installs for hyper-casual games",
        "hq": "Dubai, UAE"
    },
    {
        "id": "69a956f19c4d5b94c3836c48",
        "studio": "Kwalee",
        "contact": "David Darling",
        "focus": "Hyper-casual, Hybrid-casual, Casual",
        "games": "Draw It, Shoot Out 3D, Teacher Simulator",
        "size": "Large (500M+ downloads)",
        "news": "Largest hypercasual publisher in UK",
        "hq": "Leamington Spa, UK"
    },
    {
        "id": "69a956f46890fd5af868396d",
        "studio": "Lion Studios",
        "contact": "Rafael Vivas",
        "focus": "Mobile game publishing",
        "games": "Love Rescue, Draw Story",
        "size": "Large (AppLovin subsidiary)",
        "news": "Leading AppLovin publishing division",
        "hq": "San Francisco, CA"
    },
    {
        "id": "69a8913a84d065cf67ed64e6",
        "studio": "BoomBit",
        "contact": "Marcin Olejarz",
        "focus": "Publicly-traded gaming, hyper-casual + mid-core",
        "games": "Ramp Car Jumping, Hunt Royale, Tow N Go",
        "size": "Publicly traded, 290+ employees, 1.7B+ downloads",
        "news": "One of Poland's largest gaming companies",
        "hq": "Poland"
    },
]

# Process each card
processed = 0
for card in cards_to_process:
    print(f"\n{'='*60}")
    print(f"Processing: {card['studio']} - {card['contact']}")
    print(f"{'='*60}")
    
    # Draft message
    message = draft_message(
        card['studio'],
        card['contact'],
        card['focus'],
        card['games'],
        card['size'],
        card['news'],
        card['hq']
    )
    
    print(f"\nDrafted Message:\n{message}")
    
    # Add comment with the message
    comment_result = add_comment(card['id'], f"**DRAFTED OUTREACH MESSAGE:**\n\n{message}")
    if comment_result:
        print(f"✓ Comment added successfully")
    else:
        print(f"✗ Failed to add comment")
        continue
    
    # Move card to Ready for Review
    move_result = move_card(card['id'], READY_FOR_REVIEW_LIST_ID)
    if move_result:
        print(f"✓ Card moved to Ready for Review")
    else:
        print(f"✗ Failed to move card")
        continue
    
    processed += 1
    print(f"✓ Card {processed} completed")

print(f"\n{'='*60}")
print(f"SUMMARY: Processed {processed} cards")
print(f"{'='*60}")
