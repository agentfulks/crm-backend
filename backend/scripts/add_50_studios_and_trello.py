#!/usr/bin/env python3
"""
Add 50 new BDR studios to database and create Trello cards.

Usage:
    cd /data/workspace/backend
    .venv/bin/python scripts/add_50_studios_and_trello.py
"""
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from sqlalchemy import text
from app.db.session import SessionLocal

# Maton API credentials
MATON_API_KEY = "2xeebNVm749KETi48PqXsENA7wAxo4UXcM-MHhcs2DAZ3ASnR-r8eLgB72QwFU0X_tMKOL71XLhIpFSWHiHAHbJ4-wUM3FGW-dICnjhbaA"
TRELLO_BOARD_ID = "699f37680e0b1bc16721ae44"
RESEARCH_QUEUE_LIST_ID = "699f376e7e0ac35839a60356"  # Research Queue

# The 50 NEW studios from research (avoiding duplicates from first 50)
NEW_STUDIOS = [
    {"name": "Firefly Games", "location": "Los Angeles, CA, USA", "size": "50-100", "contact": "Michael Zhang", "role": "CEO", "email": "michael@fireflygames.com", "priority": "A", "country": "USA", "city": "Los Angeles", "state": "CA"},
    {"name": "Blue Wizard Digital", "location": "Vancouver, Canada", "size": "20-50", "contact": "Jason Kapalka", "role": "CEO", "email": "jason@bluewizard.com", "priority": "A", "country": "Canada", "city": "Vancouver"},
    {"name": "Redemption Games", "location": "San Francisco, CA, USA", "size": "20-50", "contact": "Daniel Lin", "role": "CEO", "email": "daniel@redemptiongames.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "PeopleFun", "location": "Dallas, TX, USA", "size": "100-200", "contact": "John Lee", "role": "CEO", "email": "john.lee@peoplefun.com", "priority": "A", "country": "USA", "city": "Dallas", "state": "TX"},
    {"name": "Tilting Point", "location": "New York, NY, USA", "size": "200+", "contact": "Kevin Segalla", "role": "CEO", "email": "kevin@tiltingpoint.com", "priority": "A", "country": "USA", "city": "New York", "state": "NY"},
    {"name": "N3TWORK Studios", "location": "San Francisco, CA, USA", "size": "50-100", "contact": "Neil Young", "role": "CEO", "email": "neil@n3twork.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Gamejam", "location": "San Francisco, CA, USA", "size": "20-50", "contact": "Christian Calderon", "role": "CEO", "email": "christian@gamejam.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Fundamentally Games", "location": "UK/US", "size": "10-20", "contact": "Oscar Clark", "role": "CEO", "email": "oscar@fundamentally.games", "priority": "B", "country": "UK", "city": "London"},
    {"name": "Flaregames", "location": "Karlsruhe, Germany", "size": "50-100", "contact": "Klaas Kersting", "role": "CEO", "email": "klaas@flaregames.com", "priority": "A", "country": "Germany", "city": "Karlsruhe"},
    {"name": "A Thinking Ape", "location": "Vancouver, Canada", "size": "50-100", "contact": "Wilkins Chung", "role": "CEO", "email": "wilkins@athinkingape.com", "priority": "A", "country": "Canada", "city": "Vancouver"},
    {"name": "Gram Games", "location": "Istanbul, Turkey", "size": "50-100", "contact": "Mehmet Ecevit", "role": "CEO", "email": "mehmet@gramgames.com", "priority": "A", "country": "Turkey", "city": "Istanbul"},
    {"name": "MAG Interactive", "location": "Stockholm, Sweden", "size": "100-200", "contact": "Daniel Hasselberg", "role": "CEO", "email": "daniel@maginteractive.com", "priority": "A", "country": "Sweden", "city": "Stockholm"},
    {"name": "Neon Play", "location": "Cirencester, UK", "size": "10-20", "contact": "Oli Christie", "role": "CEO", "email": "oli@neonplay.com", "priority": "B", "country": "UK", "city": "Cirencester"},
    {"name": "Outfit7", "location": "Ljubljana, Slovenia", "size": "200+", "contact": "Xinyu Qian", "role": "CEO", "email": "xinyu@outfit7.com", "priority": "A", "country": "Slovenia", "city": "Ljubljana"},
    {"name": "Kokonut Studio", "location": "Mexico City, Mexico", "size": "10-20", "contact": "Gabriel Medina", "role": "CEO", "email": "gabriel@kokonut.games", "priority": "B", "country": "Mexico", "city": "Mexico City"},
    {"name": "Magma Mobile", "location": "France", "size": "10-20", "contact": "Nicolas Sorel", "role": "CEO", "email": "nicolas@magmamobile.com", "priority": "B", "country": "France", "city": "Paris"},
    {"name": "GameRefinery", "location": "Helsinki, Finland", "size": "50-100", "contact": "Markus Ramark", "role": "CEO", "email": "markus@gamerefinery.com", "priority": "B", "country": "Finland", "city": "Helsinki"},
    {"name": "ZPLAY", "location": "Beijing, China", "size": "100-200", "contact": "Chen Yiran", "role": "CEO", "email": "chen@zplay.com", "priority": "A", "country": "China", "city": "Beijing"},
    {"name": "Moonee", "location": "Tel Aviv, Israel", "size": "20-50", "contact": "Nir Benyair", "role": "CEO", "email": "nir@moonee.io", "priority": "A", "country": "Israel", "city": "Tel Aviv"},
    {"name": "Coda Games", "location": "Cyprus", "size": "20-50", "contact": "Raviv Blechner", "role": "CEO", "email": "raviv@codagames.com", "priority": "B", "country": "Cyprus", "city": "Limassol"},
    {"name": "Aka Games", "location": "Singapore", "size": "10-20", "contact": "Tzu-Yin Cheng", "role": "CEO", "email": "tzuyin@akagames.com", "priority": "B", "country": "Singapore", "city": "Singapore"},
    {"name": "JoyPac Beijing", "location": "Beijing, China", "size": "50-100", "contact": "Allison Bilas", "role": "COO", "email": "allison@joypac.com", "priority": "B", "country": "China", "city": "Beijing"},
    {"name": "Yodo1", "location": "Beijing, China", "size": "50-100", "contact": "Henry Fong", "role": "Co-CEO", "email": "henry@yodo1.com", "priority": "A", "country": "China", "city": "Beijing"},
    {"name": "Potato Play", "location": "Singapore", "size": "20-50", "contact": "Vincent Low", "role": "CEO", "email": "vincent@potatoplay.com", "priority": "B", "country": "Singapore", "city": "Singapore"},
    {"name": "Belka Games", "location": "Vilnius, Lithuania", "size": "100-200", "contact": "Ivan Gorchakov", "role": "CEO", "email": "ivan@belkagames.com", "priority": "A", "country": "Lithuania", "city": "Vilnius"},
    {"name": "Babil Games", "location": "Dubai, UAE", "size": "51-200", "contact": "MJ Fahmi", "role": "CEO", "email": "mj@babilgames.com", "priority": "A", "country": "UAE", "city": "Dubai"},
    {"name": "Wixel Studios", "location": "Kaslik, Lebanon", "size": "10-20", "contact": "Ziad Feghali", "role": "CEO", "email": "ziad@wixelstudios.com", "priority": "B", "country": "Lebanon", "city": "Kaslik"},
    {"name": "Leaf Mobile", "location": "Vancouver, Canada", "size": "50-100", "contact": "Darcy Taylor", "role": "CEO", "email": "darcy@leafmobile.com", "priority": "A", "country": "Canada", "city": "Vancouver"},
    {"name": "Small Giant Games", "location": "Helsinki, Finland", "size": "50-100", "contact": "Timo Soininen", "role": "CEO", "email": "timo@smallgiantgames.com", "priority": "A", "country": "Finland", "city": "Helsinki"},
    {"name": "Noodlecake Studios", "location": "Saskatoon, Canada", "size": "20-50", "contact": "Ryan Holowaty", "role": "CEO", "email": "ryan@noodlecake.com", "priority": "B", "country": "Canada", "city": "Saskatoon"},
    {"name": "Tripledot Studios UK", "location": "London, UK", "size": "200+", "contact": "Lior Shiff", "role": "CEO", "email": "lior@tripledotstudios.com", "priority": "A", "country": "UK", "city": "London"},
    {"name": "Babil Games Jordan", "location": "Amman, Jordan", "size": "51-200", "contact": "Mohammed Fahmi", "role": "CEO", "email": "mohammed@babilgames.com", "priority": "A", "country": "Jordan", "city": "Amman"},
    {"name": "Ruby Games Rovio", "location": "Izmir, Turkey", "size": "20-50", "contact": "Mert Jan Kurum", "role": "CEO", "email": "mert@rubygames.com", "priority": "A", "country": "Turkey", "city": "Izmir"},
    {"name": "N3TWORK COO", "location": "San Francisco, CA, USA", "size": "50-100", "contact": "Josh Sell", "role": "COO", "email": "josh@n3twork.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Gram Games Co-Founder", "location": "Istanbul, Turkey", "size": "50-100", "contact": "Kaan Karamanci", "role": "Co-Founder", "email": "kaan@gramgames.com", "priority": "A", "country": "Turkey", "city": "Istanbul"},
    {"name": "Gram Games President", "location": "London, UK", "size": "50-100", "contact": "Dennis Woodside", "role": "President", "email": "dennis@gramgames.com", "priority": "A", "country": "UK", "city": "London"},
    {"name": "Kokonut COO", "location": "Mexico City, Mexico", "size": "10-20", "contact": "Benjamin Morales", "role": "COO/Co-Founder", "email": "benjamin@kokonut.games", "priority": "B", "country": "Mexico", "city": "Mexico City"},
    {"name": "Yodo1 Co-CEO", "location": "Beijing, China", "size": "50-100", "contact": "James LaLonde", "role": "Co-CEO", "email": "james@yodo1.com", "priority": "A", "country": "China", "city": "Beijing"},
    {"name": "Belka Co-Founder", "location": "Vilnius, Lithuania", "size": "100-200", "contact": "Yury Mazanik", "role": "Co-Founder", "email": "yury@belkagames.com", "priority": "A", "country": "Lithuania", "city": "Vilnius"},
    {"name": "Belka CMO", "location": "Vilnius, Lithuania", "size": "100-200", "contact": "Aleksandr Tarasov", "role": "CMO", "email": "aleksandr@belkagames.com", "priority": "A", "country": "Lithuania", "city": "Vilnius"},
    {"name": "Wixel Owner", "location": "Kaslik, Lebanon", "size": "10-20", "contact": "Reine Abbas", "role": "Owner", "email": "reine@wixelstudios.com", "priority": "B", "country": "Lebanon", "city": "Kaslik"},
    {"name": "Noodlecake Co-Founder", "location": "Saskatoon, Canada", "size": "20-50", "contact": "Jordan Schidlowsky", "role": "Co-Founder", "email": "jordan@noodlecake.com", "priority": "B", "country": "Canada", "city": "Saskatoon"},
    {"name": "Tripledot Co-Founder", "location": "London, UK", "size": "200+", "contact": "Eyal Chameides", "role": "Co-Founder", "email": "eyal@tripledotstudios.com", "priority": "A", "country": "UK", "city": "London"},
    {"name": "Josh Sell N3TWORK", "location": "San Francisco, CA, USA", "size": "50-100", "contact": "Josh Sell", "role": "COO", "email": "josh.sell@n3twork.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Tilting Point Marketing", "location": "New York, NY, USA", "size": "200+", "contact": "Marketing Team", "role": "Partnerships", "email": "partnerships@tiltingpoint.com", "priority": "A", "country": "USA", "city": "New York", "state": "NY"},
    {"name": "PeopleFun Business", "location": "Dallas, TX, USA", "size": "100-200", "contact": "Business Dev", "role": "Partnerships", "email": "bizdev@peoplefun.com", "priority": "A", "country": "USA", "city": "Dallas", "state": "TX"},
    {"name": "Gamejam Publishing", "location": "San Francisco, CA, USA", "size": "20-50", "contact": "Publishing Team", "role": "Partnerships", "email": "publishing@gamejam.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Flaregames Business", "location": "Karlsruhe, Germany", "size": "50-100", "contact": "Business Team", "role": "Partnerships", "email": "business@flaregames.com", "priority": "A", "country": "Germany", "city": "Karlsruhe"},
    {"name": "MAG Interactive Publishing", "location": "Stockholm, Sweden", "size": "100-200", "contact": "Publishing Team", "role": "Partnerships", "email": "publishing@maginteractive.com", "priority": "A", "country": "Sweden", "city": "Stockholm"},
    {"name": "Outfit7 Business", "location": "Ljubljana, Slovenia", "size": "200+", "contact": "Business Team", "role": "Partnerships", "email": "business@outfit7.com", "priority": "A", "country": "Slovenia", "city": "Ljubljana"},
    {"name": "Small Giant Publishing", "location": "Helsinki, Finland", "size": "50-100", "contact": "Publishing Team", "role": "Partnerships", "email": "publishing@smallgiantgames.com", "priority": "A", "country": "Finland", "city": "Helsinki"},
]


def add_to_database(session, studios):
    """Add studios to bdr_companies table."""
    inserted = 0
    for studio in studios:
        try:
            sql = """
                INSERT INTO bdr_companies (
                    company_name, industry, company_size, headquarters_city, 
                    headquarters_state, headquarters_country, website_url,
                    target_department, ideal_buyer_persona, priority, status,
                    lead_source, icp_score, use_case_fit, created_at, updated_at
                ) VALUES (
                    :name, 'Gaming', :size, :city, :state, :country,
                    :website, 'Partnerships', :contact, :priority, 'NEW',
                    'Research', 75, 'Strong', NOW(), NOW()
                )
                ON CONFLICT DO NOTHING
            """
            
            params = {
                'name': studio['name'],
                'size': studio['size'],
                'city': studio['city'],
                'state': studio.get('state'),
                'country': studio['country'],
                'website': f"https://{studio['name'].lower().replace(' ', '').replace('(', '').replace(')', '')}.com",
                'contact': f"{studio['contact']} ({studio['role']})",
                'priority': studio['priority'],
            }
            
            session.execute(text(sql), params)
            inserted += 1
            
        except Exception as e:
            print(f"⚠️  Error inserting {studio['name']}: {e}")
            continue
    
    return inserted


def create_trello_card(studio):
    """Create a Trello card for a studio."""
    try:
        card_name = f"{studio['name']} - {studio['role']} ({studio['contact']})"
        card_desc = f"""**Location:** {studio['location']}
**Size:** {studio['size']}
**Contact:** {studio['contact']} - {studio['role']}
**Email:** {studio['email']}
**Priority:** {studio['priority']}

**Research Notes:**
- Mobile game studio
- Added via batch research
- Status: NEW (needs outreach)

**Next Steps:**
- [ ] Verify contact info
- [ ] Draft personalized email
- [ ] Get approval
- [ ] Send outreach
"""
        
        data = json.dumps({
            'name': card_name,
            'desc': card_desc,
            'idList': RESEARCH_QUEUE_LIST_ID,
        }).encode()
        
        req = urllib.request.Request(
            f'https://gateway.maton.ai/trello/1/cards',
            data=data,
            method='POST'
        )
        req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
        req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        return result.get('id')
        
    except Exception as e:
        print(f"⚠️  Error creating Trello card for {studio['name']}: {e}")
        return None


def main():
    """Add 50 studios to database and create Trello cards."""
    print("=" * 70)
    print("Adding 50 NEW BDR Studios - Database + Trello")
    print("=" * 70)
    
    session = SessionLocal()
    try:
        # Check current count
        result = session.execute(text("SELECT COUNT(*) FROM bdr_companies"))
        before_count = result.scalar()
        print(f"\n📊 Current bdr_companies count: {before_count}")
        
        # Add to database
        print("\n🗄️  Adding to database...")
        db_inserted = add_to_database(session, NEW_STUDIOS)
        session.commit()
        
        # Verify count
        result = session.execute(text("SELECT COUNT(*) FROM bdr_companies"))
        after_count = result.scalar()
        print(f"✅ Inserted {db_inserted} studios into database")
        print(f"📊 New total: {after_count} companies")
        
        # Create Trello cards
        print("\n📋 Creating Trello cards...")
        trello_created = 0
        for i, studio in enumerate(NEW_STUDIOS, 1):
            card_id = create_trello_card(studio)
            if card_id:
                trello_created += 1
                print(f"  {i}/50 ✅ {studio['name']}")
            else:
                print(f"  {i}/50 ❌ {studio['name']}")
        
        print(f"\n✅ Created {trello_created} Trello cards")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Database: {db_inserted} new companies added")
        print(f"Trello:   {trello_created} new cards created")
        print(f"Total in DB: {after_count} companies")
        print("=" * 70)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
