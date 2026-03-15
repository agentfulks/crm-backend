#!/usr/bin/env python3
"""
Trello Import Script — Cycles 21-22
Imports VC and BDR cards to Trello boards
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime

MATON_API_KEY = os.environ.get('MATON_API_KEY')

BOARDS = {
    "VC Outreach Engine": {
        "target_list": "Daily Queue",
        "cards": [
            # Cycle 21 VC (5 firms)
            {"name": "VC: Hiro Capital — Luke Alvarez (€300M gaming, AI thesis)", "desc": """**Hiro Capital**
Location: London, UK / Luxembourg
Fund: Hiro III (~$300M, launched Dec 2025)
Partner: Luke Alvarez (Managing Partner)
Check Size: $500K-$5M

**Thesis:** Gaming + Metaverse + AI
- Led $16M Series A for Believer Company
- Backed Solaris offworld (AI x gaming)
- Gaming-focused fund with deep European network

**Warm Angle:** Portfolio company intros through Believer or Solaris teams. Luke is vocal on LinkedIn about AI infrastructure.

**Priority:** P0 — Gaming thesis, active 2024-2025"""},
            {"name": "VC: The Games Fund — Anton Gorodetsky ($50M gaming)", "desc": """**The Games Fund**
Location: New York, USA / Cyprus
Fund: $50M Fund I (2022)
Partner: Anton Gorodetsky (Co-Founder)
Check Size: $100K-$1M

**Thesis:** Early-stage game studios + gaming infrastructure
- Focus on Eastern European and CIS talent
- Multiple gaming AI tool investments
- Strong network in game dev community

**Warm Angle:** Russian-speaking founder angle. Anton active on Telegram gaming channels.

**Priority:** P0 — Gaming-only fund, early-stage focus"""},
            {"name": "VC: Play Ventures — Kenrick Drijkoningen ($140M Fund III)", "desc": """**Play Ventures**
Location: Singapore / Helsinki
Fund: $140M Fund III (2024)
Partner: Kenrick Drijkoningen (Founding Partner)
Check Size: $250K-$2M

**Thesis:** Gaming + AI infrastructure
- Led Series A for AI-powered game testing startup
- Multiple gaming infrastructure bets
- Strong Asia/Europe presence

**Warm Angle:** Portfolio intros through existing gaming companies. Kenrick speaks at GDC.

**Priority:** P0 — Gaming infrastructure thesis"""},
            {"name": "VC: Dune Ventures — Brian Corrigan (~$100M)", "desc": """**Dune Ventures**
Location: New York City, USA
Fund: ~$100M
Partner: Brian Corrigan (Founder)
Check Size: $500K-$3M

**Thesis:** Gaming + Interactive media
- Seed investor in gaming infrastructure
- Focus on AI-native tools
- East Coast gaming network

**Warm Angle:** NYC gaming meetups. Portfolio company connections.

**Priority:** P1 — Gaming focus, smaller fund"""},
            {"name": "VC: Behold Ventures — Karl Magnus Troedsson ($52M Nordic)", "desc": """**Behold Ventures**
Location: Stockholm, Sweden
Fund: SEK 550M (~$52M) Fund I (July 2025)
Partner: Karl Magnus Troedsson (Founding Partner, ex-DICE/Paradox)
Check Size: $100K-$5M

**Thesis:** Gaming startups with AI-readiness
- Invested in Roro (AI-powered dollhouse)
- Pure gaming focus
- Nordic operational expertise

**Warm Angle:** Former DICE/EA connections. Nordic game dev community intros.

**Priority:** P0 — Pure gaming, operational expertise"""},
        ]
    },
    "BDR - Game Studios Outreach": {
        "target_list": "Research Complete",
        "cards": [
            # Cycle 21 BDR (10 studios)
            {"name": "BDR: Supercell — Ilkka Paananen (5B+ downloads)", "desc": """**Supercell**
Location: Helsinki, Finland
Downloads: 5B+
CEO: Ilkka Paananen
Games: Clash of Clans, Clash Royale, Brawl Stars, Hay Day

**AI NPC Angle:**
- Clash Royale could have AI-driven emote/dialogue interactions
- Brawl Stars characters have personalities that could be dynamic
- Small team culture = nimble for experiments

**Outreach:** "Your character IP in Brawl Stars shows the value of personality. AI NPCs could let players have unique conversations with their favorite brawlers."

**Tier:** Tier-1 — Top mobile studio"""},
            {"name": "BDR: Dream Games — Soner Aydemir (300M+)", "desc": """**Dream Games**
Location: Istanbul, Turkey / London
Downloads: 300M+ (Royal Match)
CEO: Soner Aydemir (ex-Peak Games)

**AI NPC Angle:**
- Royal Match has King Robert character
- Character-driven match-3 with narrative
- Perfect for AI-powered NPC companions

**Outreach:** "King Robert guides players through Royal Match — imagine if he could respond to each player's progress with personalized encouragement and tips."

**Tier:** Tier-1 — Fastest growing match-3"""},
            {"name": "BDR: Scopely — Javier Ferreira ($1B+ revenue)", "desc": """**Scopely**
Location: Culver City, CA
Revenue: $1B+ (MONOPOLY GO!)
CEO: Javier Ferreira

**AI NPC Angle:**
- MONOPOLY GO! has Mr. Monopoly character
- LiveOps-heavy with constant events
- AI NPCs could personalize event experiences

**Outreach:** "Mr. Monopoly drives MONOPOLY GO!'s success. AI NPCs could make his interactions unique to each player's journey and spending patterns."

**Tier:** Tier-1 — Massive revenue, LiveOps leader"""},
            {"name": "BDR: King — Tjodolf Sommestad (Candy Crush)", "desc": """**King**
Location: Stockholm, Sweden (Activision Blizzard)
Downloads: 10B+ (Candy Crush franchise)
President: Tjodolf Sommestad

**AI NPC Angle:**
- Candy Crush has Tiffi character
- Narrative-driven level progression
- AI could add character dialogue to puzzle experience

**Outreach:** "Tiffi has guided players through Candy Crush for years. AI NPCs could make her interactions fresh and personalized for each player."

**Tier:** Tier-1 — Massive scale, character IP"""},
            {"name": "BDR: Habby — Stefan Wang (Archero, 100M+)", "desc": """**Habby**
Location: Singapore / China
Downloads: 100M+ (Archero, PunBall)
CEO: Stefan Wang

**AI NPC Angle:**
- Archero has roguelike progression
- Character progression systems
- AI NPCs could add dialogue to dungeon runs

**Outreach:** "Archero's roguelike loops keep players engaged. AI NPCs could add narrative depth with companions that react to each dungeon run."

**Tier:** Tier-1 — Strong roguelike mechanics"""},
            {"name": "BDR: Homa Games — Daniel Nathan (1B+ downloads)", "desc": """**Homa Games**
Location: Paris, France
Downloads: 1B+
CEO: Daniel Nathan

**AI NPC Angle:**
- Hyper-casual publisher expanding to hybrid
- Looking for differentiation/retention tools
- AI NPCs for meta layers

**Outreach:** "With 1B+ downloads, you understand casual players. As you move hybrid, AI NPCs could drive retention in your meta layers."

**Tier:** Tier-2 — Transitioning to hybrid"""},
            {"name": "BDR: Game Science — Feng Ji (Black Myth)", "desc": """**Game Science**
Location: Hangzhou, China
Downloads: 10M+ (Black Myth: Wukong)
CEO: Feng Ji

**AI NPC Angle:**
- Black Myth has rich NPC world
- AAA production values
- AI NPCs for dynamic world interactions

**Outreach:** "Black Myth: Wukong's world is full of memorable characters. AI NPCs could make each player's journey through the mythology unique."

**Tier:** Tier-1 — AAA breakout hit"""},
            {"name": "BDR: miHoYo — Liu Wei (Genshin Impact)", "desc": """**miHoYo**
Location: Shanghai, China
Downloads: 100M+ (Genshin Impact)
CEO: Liu Wei (Forrest Liu)

**AI NPC Angle:**
- Genshin Impact has 50+ playable characters
- Strong narrative and character development
- AI could enhance NPC companion interactions

**Outreach:** "Genshin Impact's character system is industry-leading. AI NPCs could take companion interactions to the next level with dynamic dialogue."

**Tier:** Tier-1 — Character IP powerhouse"""},
            {"name": "BDR: Pocket Gems — Ben Liu (Episode)", "desc": """**Pocket Gems**
Location: San Francisco, CA
Downloads: 100M+ (Episode)
CEO: Ben Liu

**AI NPC Angle:**
- Episode is narrative choice game
- Character-driven storytelling
- AI NPCs for dynamic narrative branches

**Outreach:** "Episode puts players in control of their story. AI NPCs could make each narrative path truly unique with characters that adapt to choices."

**Tier:** Tier-1 — Narrative experts"""},
            {"name": "BDR: Zynga — Frank Gibeau (FarmVille)", "desc": """**Zynga**
Location: San Francisco, CA (Take-Two)
Downloads: 1B+
CEO: Frank Gibeau

**AI NPC Angle:**
- FarmVille, Words With Friends, CSR Racing
- LiveOps veteran
- AI NPCs for social game interactions

**Outreach:** "Zynga's social games connect millions. AI NPCs could add personalized characters that make each player's social experience unique."

**Tier:** Tier-2 — Large but slower moving"""},
            # Cycle 22 BDR (10 studios)
            {"name": "BDR: Magic Tavern — Miguel Vidaure (500M+)", "desc": """**Magic Tavern**
Location: San Francisco, CA
Downloads: 500M+ (Project Makeover, Matchington Mansion)
CEO: Miguel Vidaure

**AI NPC Angle:**
- Project Makeover: character transformation narratives
- Heavy character interaction with backstories
- Perfect for AI NPC dialogue

**Outreach:** "Your character-driven makeover journeys show deep empathy for NPC stories. Have you considered AI-powered NPCs that remember player choices?"

**Tier:** Tier-1 — Perfect ICP match"""},
            {"name": "BDR: Unico Studio — Erkay Uzun (1.6B+)", "desc": """**Unico Studio**
Location: Turkey
Downloads: 1.6B+ (Brain Test, Life Choices)
CEO: Erkay Uzun

**AI NPC Angle:**
- Life Choices: Life Simulator = perfect AI NPC fit
- Decision trees that could be AI-enhanced
- Character progression systems

**Outreach:** "Life Choices puts players in control of character destinies — imagine if those characters could respond intelligently with AI-driven dialogue."

**Tier:** Tier-1 — Life simulation focus"""},
            {"name": "BDR: Tactile Games — Asbjoern Soendergaard (300M+)", "desc": """**Tactile Games**
Location: Copenhagen, Denmark
Downloads: 300M+ ($500M rev from Lily's Garden)
CEO: Asbjoern Soendergaard

**AI NPC Angle:**
- Lily's Garden: rich narrative, character relationships
- Ongoing character storylines
- LiveOps with character themes

**Outreach:** "Lily's Garden's character-driven storytelling creates genuine player attachment. AI NPCs could make neighborhood cast feel even more alive."

**Tier:** Tier-1 — Narrative experts"""},
            {"name": "BDR: Playrix — Dmitri Bukhman (1B+)", "desc": """**Playrix**
Location: Dublin, Ireland
Downloads: 1B+ (Homescapes, Gardenscapes)
CEO: Dmitri Bukhman

**AI NPC Angle:**
- Austin the Butler = iconic NPC character
- Character-driven cutscenes
- Emotional storytelling focus

**Outreach:** "Austin is iconic — but imagine if he could respond uniquely to each player and remember their design preferences with AI."

**Tier:** Tier-1 — Clear character IP"""},
            {"name": "BDR: Century Games — Chen Qi ($3.5B rev)", "desc": """**Century Games**
Location: Beijing, China
Revenue: $3.5B+ (Whiteout Survival: $400M+)
CEO: Chen Qi

**AI NPC Angle:**
- Whiteout Survival: hero characters with backstories
- Family Farm: character-driven farming
- Livetopia: social simulation on Roblox

**Outreach:** "Whiteout Survival's heroes and Family Farm's character stories show narrative depth. AI NPCs could make strategy heroes truly memorable."

**Tier:** Tier-1 — Top 10 publisher"""},
            {"name": "BDR: CrazyLabs — Sagi Schliesser (7B+)", "desc": """**CrazyLabs**
Location: Tel Aviv, Israel
Downloads: 7B+
CEO: Sagi Schliesser

**AI NPC Angle:**
- Super Stylist: fashion game with character clients
- Character clients with preferences
- Perfect for AI NPC dialogue

**Outreach:** "Super Stylist's client characters could be more engaging with AI-driven dialogue that remembers style preferences and fashion journey."

**Tier:** Tier-1 — Massive scale"""},
            {"name": "BDR: Nordcurrent — Victoria Trofimova (500M+)", "desc": """**Nordcurrent**
Location: Vilnius, Lithuania
Downloads: 500M+ (Cooking Fever: 400M)
CEO: Victoria Trofimova

**AI NPC Angle:**
- Murder in the Alps / Murder by Choice: narrative mysteries
- NPC interrogations
- Branching narrative possibilities

**Outreach:** "Your Murder mystery games rely on NPC interrogations. AI NPCs could make each playthrough unique with characters that respond dynamically."

**Tier:** Tier-2 — Mystery narrative angle"""},
            {"name": "BDR: MYTONA — Alexey Ushnisky (200M+)", "desc": """**MYTONA**
Location: Singapore / New Zealand
Downloads: 200M+ (Seekers Notes)
CEO: Alexey Ushnisky

**AI NPC Angle:**
- Seekers Notes: hidden object with town NPCs
- Quest-giving NPCs with personalities
- Mystery narrative structure

**Outreach:** "Seekers Notes' Darkwood Town has memorable NPCs. AI NPCs could create truly living towns with daily routines and evolving relationships."

**Tier:** Tier-2 — Hidden object NPCs"""},
            {"name": "BDR: YSO Corp — Jean-Claude Yalap (1.47B+)", "desc": """**YSO Corp**
Location: Paris, France
Downloads: 1.47B+ (225+ games)
Co-Founder: Jean-Claude Yalap

**AI NPC Angle:**
- Hyper-casual shifting to hybrid-casual
- Looking for meta layers and retention
- AI NPCs for character progression

**Outreach:** "With 1.47B downloads, you know casual gaming. As you move hybrid, AI NPCs could be the retention driver with character stories."

**Tier:** Tier-2 — Transitioning from hyper"""},
            {"name": "BDR: Ninetap — Team (200M+)", "desc": """**Ninetap**
Location: South Korea
Downloads: 200M+ (Word Cookies, Roll the Ball)
Founder: Bitmango alumni

**AI NPC Angle:**
- Puzzle-focused currently
- Opportunity for AI tutorial/guide NPCs
- Story modes in puzzle games

**Outreach:** "With Bitmango heritage in casual hits, have you considered AI-powered character guides to make learning mechanics feel personal?"

**Tier:** Tier-2 — Tutorial NPC opportunity"""},
        ]
    }
}

def maton_request(endpoint, method="GET", data=None):
    """Make request to Maton API"""
    url = f"https://api.maton.ai/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {MATON_API_KEY}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, method=method)
    for key, val in headers.items():
        req.add_header(key, val)
    
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}

def get_board_id(board_name):
    """Find board ID by name"""
    result = maton_request("trello/boards")
    if "boards" in result:
        for board in result["boards"]:
            if board.get("name") == board_name:
                return board.get("id")
    return None

def get_list_id(board_id, list_name):
    """Find list ID by name"""
    result = maton_request(f"trello/boards/{board_id}/lists")
    if "lists" in result:
        for lst in result["lists"]:
            if lst.get("name") == list_name:
                return lst.get("id")
    return None

def create_card(list_id, name, description):
    """Create a card in Trello"""
    data = {
        "name": name[:500],  # Trello limit
        "desc": description[:5000],  # Trello limit
        "idList": list_id
    }
    return maton_request("trello/cards", method="POST", data=data)

def main():
    print("=" * 70)
    print("TRELLO IMPORT — CYCLES 21-22")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    if not MATON_API_KEY:
        print("❌ MATON_API_KEY not set")
        return False
    
    total_imported = 0
    total_failed = 0
    
    for board_name, config in BOARDS.items():
        print(f"\n📋 Board: {board_name}")
        print("-" * 70)
        
        # Get board and list IDs
        board_id = get_board_id(board_name)
        if not board_id:
            print(f"  ❌ Board not found: {board_name}")
            continue
        
        list_id = get_list_id(board_id, config["target_list"])
        if not list_id:
            print(f"  ❌ List not found: {config['target_list']}")
            continue
        
        print(f"  ✅ Board: {board_id}")
        print(f"  ✅ List: {list_id} ({config['target_list']})")
        print(f"  📝 Cards to import: {len(config['cards'])}")
        print()
        
        imported = 0
        failed = 0
        
        for card in config["cards"]:
            name = card["name"][:60] + "..." if len(card["name"]) > 60 else card["name"]
            print(f"    Creating: {name}...", end=" ")
            
            result = create_card(list_id, card["name"], card["desc"])
            
            if result and "id" in result:
                print("✅")
                imported += 1
            else:
                print(f"❌ ({result.get('error', 'unknown')})")
                failed += 1
        
        print(f"\n  📊 Summary: {imported} imported, {failed} failed")
        total_imported += imported
        total_failed += failed
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Imported: {total_imported}")
    print(f"Total Failed: {total_failed}")
    print(f"Success Rate: {(total_imported / (total_imported + total_failed) * 100):.1f}%")
    print()
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
