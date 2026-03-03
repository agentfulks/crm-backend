#!/usr/bin/env python3
"""
Insert 50 BDR game studios into bdr_companies table.

Usage:
    cd /data/workspace/backend
    .venv/bin/python scripts/seed_bdr_companies.py
"""
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from sqlalchemy import text
from app.db.session import SessionLocal

# The 50 studios from research
BDR_COMPANIES = [
    {"name": "Ketchapp", "location": "Paris, France", "size": "51-200", "contact": "Michel Morcos", "role": "CEO & Co-Founder", "email": "michel@ketchapp.com", "priority": "A", "country": "France", "city": "Paris"},
    {"name": "Colossi Games", "location": "Limassol, Cyprus", "size": "11-50", "contact": "Manuel Prueter", "role": "CEO & Co-Founder", "email": "manuel@colossi.games", "priority": "A", "country": "Cyprus", "city": "Limassol"},
    {"name": "Tactile Games", "location": "Copenhagen, Denmark", "size": "51-200", "contact": "Asbjoern Malte Soendergaard", "role": "CEO & Founder", "email": "asbjoern@tactilegames.com", "priority": "A", "country": "Denmark", "city": "Copenhagen"},
    {"name": "Metacore Games", "location": "Helsinki, Finland", "size": "51-200", "contact": "Mika Tammenkoski", "role": "CEO & Co-Founder", "email": "mika@metacoregames.com", "priority": "A", "country": "Finland", "city": "Helsinki"},
    {"name": "Ruby Games", "location": "Izmir, Turkey", "size": "11-50", "contact": "Mert Can Kurum", "role": "CEO & Founder", "email": "mert@rubygames.com", "priority": "A", "country": "Turkey", "city": "Izmir"},
    {"name": "Second Dinner", "location": "Irvine, CA, USA", "size": "51-200", "contact": "Hamilton Chu", "role": "CEO & Co-Founder", "email": "hamilton@seconddinner.com", "priority": "A", "country": "USA", "city": "Irvine", "state": "CA"},
    {"name": "Superplay", "location": "Tel Aviv, Israel", "size": "51-200", "contact": "Elad Drory", "role": "CEO", "email": "elad@superplay.co", "priority": "A", "country": "Israel", "city": "Tel Aviv"},
    {"name": "Space Ape Games", "location": "London, UK", "size": "51-200", "contact": "John Earner", "role": "CEO & Co-Founder", "email": "john@spaceapegames.com", "priority": "A", "country": "UK", "city": "London"},
    {"name": "Homa Games", "location": "Paris, France", "size": "51-200", "contact": "Daniel Nathan", "role": "CEO & Co-Founder", "email": "daniel@homagames.com", "priority": "A", "country": "France", "city": "Paris"},
    {"name": "SayGames", "location": "Minsk, Belarus", "size": "51-200", "contact": "Evgeny Ponomarenko", "role": "CEO & Founder", "email": "evgeny@saygames.by", "priority": "A", "country": "Belarus", "city": "Minsk"},
    {"name": "Green Panda Games", "location": "Paris, France", "size": "51-200", "contact": "Guillaume Sztejnberg", "role": "CEO & Founder", "email": "guillaume@greenpandagames.com", "priority": "B", "country": "France", "city": "Paris"},
    {"name": "Tripledot Studios", "location": "London, UK", "size": "51-200", "contact": "Lior Shiff", "role": "CEO & Co-Founder", "email": "lior@tripledotstudios.com", "priority": "B", "country": "UK", "city": "London"},
    {"name": "First Fun", "location": "London, UK", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@firstfungames.com", "priority": "B", "country": "UK", "city": "London"},
    {"name": "Century Games", "location": "Beijing, China", "size": "201-500", "contact": "Song Qian", "role": "CEO", "email": "song@centurygames.com", "priority": "B", "country": "China", "city": "Beijing"},
    {"name": "Joy Nice Games", "location": "China", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@joynices.com", "priority": "B", "country": "China", "city": "Unknown"},
    {"name": "Microfun", "location": "China", "size": "51-200", "contact": "CEO", "role": "CEO", "email": "contact@microfun.com", "priority": "B", "country": "China", "city": "Unknown"},
    {"name": "Voodoo", "location": "Paris, France", "size": "201-500", "contact": "Alexandre Yazdi", "role": "CEO & Co-Founder", "email": "alexandre@voodoo.io", "priority": "A", "country": "France", "city": "Paris"},
    {"name": "Rollic Games", "location": "Istanbul, Turkey", "size": "51-200", "contact": "Burak Vardal", "role": "CEO", "email": "burak@rolic.com", "priority": "A", "country": "Turkey", "city": "Istanbul"},
    {"name": "Kwalee", "location": "Leamington Spa, UK", "size": "51-200", "contact": "David Darling", "role": "CEO & Founder", "email": "david@kwalee.com", "priority": "A", "country": "UK", "city": "Leamington Spa"},
    {"name": "Belka Games", "location": "Vilnius, Lithuania", "size": "51-200", "contact": "Egor Kozlov", "role": "CEO & Co-Founder", "email": "egor@belkagames.com", "priority": "B", "country": "Lithuania", "city": "Vilnius"},
    {"name": "Alictus Games", "location": "Ankara, Turkey", "size": "51-200", "contact": "Aytek Kurtuluş", "role": "CEO & Co-Founder", "email": "aytek@alictus.com", "priority": "B", "country": "Turkey", "city": "Ankara"},
    {"name": "Supersonic Studios", "location": "Tel Aviv, Israel", "size": "51-200", "contact": "Nadav Ashkenazy", "role": "CEO", "email": "nadav@supersonic.com", "priority": "A", "country": "Israel", "city": "Tel Aviv"},
    {"name": "tinyBuild", "location": "Amsterdam, Netherlands", "size": "51-200", "contact": "Alex Nichiporchik", "role": "CEO & Co-Founder", "email": "alex@tinybuild.com", "priority": "B", "country": "Netherlands", "city": "Amsterdam"},
    {"name": "East Side Games", "location": "Vancouver, Canada", "size": "51-200", "contact": "Jason Bailey", "role": "CEO & Co-Founder", "email": "jason@eastsidegames.com", "priority": "B", "country": "Canada", "city": "Vancouver"},
    {"name": "Pocket Gems", "location": "San Francisco, CA, USA", "size": "201-500", "contact": "Ben Liu", "role": "CEO", "email": "ben@pocketgems.com", "priority": "B", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Ketchapp (Antoine)", "location": "Paris, France", "size": "51-200", "contact": "Antoine Morcos", "role": "Co-Founder", "email": "antoine@ketchapp.com", "priority": "B", "country": "France", "city": "Paris"},
    {"name": "Niantic", "location": "San Francisco, CA, USA", "size": "501+", "contact": "John Hanke", "role": "CEO & Founder", "email": "john@nianticlabs.com", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Wooga", "location": "Berlin, Germany", "size": "201-500", "contact": "Jens Begemann", "role": "Founder", "email": "jens@wooga.com", "priority": "B", "country": "Germany", "city": "Berlin"},
    {"name": "PLAYSTUDIOS", "location": "Las Vegas, NV, USA", "size": "201-500", "contact": "Andrew Pascal", "role": "Chairman & CEO", "email": "andrew@playstudios.com", "priority": "B", "country": "USA", "city": "Las Vegas", "state": "NV"},
    {"name": "ZPLAY Games", "location": "Beijing, China", "size": "51-200", "contact": "He Peng", "role": "Founder & CEO", "email": "he@zplay.com", "priority": "B", "country": "China", "city": "Beijing"},
    {"name": "Playgendary", "location": "Limassol, Cyprus", "size": "51-200", "contact": "Dmitriy Shelengovskiy", "role": "Founder & CEO", "email": "dmitriy@playgendary.com", "priority": "B", "country": "Cyprus", "city": "Limassol"},
    {"name": "JoyPac", "location": "Berlin, Germany", "size": "11-50", "contact": "Mark Zhou", "role": "CEO", "email": "mark@joypac.com", "priority": "B", "country": "Germany", "city": "Berlin"},
    {"name": "Mythical Games", "location": "Los Angeles, CA, USA", "size": "51-200", "contact": "John Linden", "role": "CEO & Co-Founder", "email": "john@mythicalgames.com", "priority": "A", "country": "USA", "city": "Los Angeles", "state": "CA"},
    {"name": "Mino Games", "location": "Montreal, Canada", "size": "51-200", "contact": "Sasha Mackinnon", "role": "CEO & Co-Founder", "email": "sasha@minogames.com", "priority": "B", "country": "Canada", "city": "Montreal"},
    {"name": "Miniclip", "location": "Neuchâtel, Switzerland", "size": "201-500", "contact": "Robert Small", "role": "CEO & Co-Founder", "email": "rob@miniclip.com", "priority": "A", "country": "Switzerland", "city": "Neuchâtel"},
    {"name": "Wildlife Studios", "location": "São Paulo, Brazil", "size": "201-500", "contact": "Victor Lazarte", "role": "CEO & Co-Founder", "email": "victor@wildlifestudios.com", "priority": "A", "country": "Brazil", "city": "São Paulo"},
    {"name": "Fingersoft", "location": "Oulu, Finland", "size": "51-200", "contact": "Teemu Närhi", "role": "CEO", "email": "teemu@fingersoft.com", "priority": "A", "country": "Finland", "city": "Oulu"},
    {"name": "Innersloth", "location": "Redmond, WA, USA", "size": "11-50", "contact": "Forest Willard", "role": "CEO & Co-Founder", "email": "forest@innersloth.com", "priority": "A", "country": "USA", "city": "Redmond", "state": "WA"},
    {"name": "Scopely", "location": "Los Angeles, CA, USA", "size": "501+", "contact": "Walter Driver", "role": "Co-Founder & Co-CEO", "email": "walter@scopely.com", "priority": "A", "country": "USA", "city": "Los Angeles", "state": "CA"},
    {"name": "Lion Studios", "location": "San Francisco, CA, USA", "size": "51-200", "contact": "Nick Bogovich", "role": "CEO", "email": "nick@lionstudios.cc", "priority": "A", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "Nexters", "location": "Limassol, Cyprus", "size": "501+", "contact": "Anton Reinhold", "role": "CEO", "email": "anton@nexters.com", "priority": "B", "country": "Cyprus", "city": "Limassol"},
    {"name": "Playsome", "location": "Helsinki, Finland", "size": "11-50", "contact": "Timo Palonen", "role": "CEO & Co-Founder", "email": "timo@playsome.games", "priority": "B", "country": "Finland", "city": "Helsinki"},
    {"name": "Crunchyroll Games", "location": "San Francisco, CA, USA", "size": "501+", "contact": "Rahul Purini", "role": "CEO", "email": "rahul@crunchyroll.com", "priority": "B", "country": "USA", "city": "San Francisco", "state": "CA"},
    {"name": "FunPlus", "location": "Beijing, China", "size": "501+", "contact": "Andy Zhong", "role": "CEO", "email": "andy@funplus.com", "priority": "A", "country": "China", "city": "Beijing"},
    {"name": "Gismart", "location": "London, UK", "size": "201-500", "contact": "Mykola Tymkiv", "role": "CEO", "email": "mykola@gismart.com", "priority": "B", "country": "UK", "city": "London"},
    {"name": "Dual Cat", "location": "Paris, France", "size": "11-50", "contact": "Mikael Le Goff", "role": "CEO & Founder", "email": "mikael@dual-cat.com", "priority": "B", "country": "France", "city": "Paris"},
    {"name": "Magmatic Games", "location": "Berlin, Germany", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@magmaticgames.com", "priority": "B", "country": "Germany", "city": "Berlin"},
    {"name": "PlayCore", "location": "Chattanooga, TN, USA", "size": "51-200", "contact": "Roger Posacki", "role": "President & CEO", "email": "roger@playcore.com", "priority": "C", "country": "USA", "city": "Chattanooga", "state": "TN"},
    {"name": "Neuroflag", "location": "Tokyo, Japan", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@neuroflag.com", "priority": "C", "country": "Japan", "city": "Tokyo"},
    {"name": "Gubbe", "location": "Helsinki, Finland", "size": "11-50", "contact": "Sandra Lounamaa", "role": "CEO & Co-Founder", "email": "sandra@gubbe.io", "priority": "C", "country": "Finland", "city": "Helsinki"},
]


def main():
    """Insert BDR companies into database."""
    print("=" * 60)
    print("BDR Companies Database Seeder")
    print("=" * 60)
    
    session = SessionLocal()
    try:
        # Check existing count
        result = session.execute(text("SELECT COUNT(*) FROM bdr_companies"))
        existing_count = result.scalar()
        print(f"\nExisting records in bdr_companies: {existing_count}")
        
        # Clear existing if less than 50
        if existing_count > 0 and existing_count < 50:
            print("Clearing existing records...")
            session.execute(text("DELETE FROM bdr_companies"))
            session.commit()
            print("Cleared.")
        
        # Insert all 50 companies
        inserted = 0
        for company in BDR_COMPANIES:
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
                    'name': company['name'],
                    'size': company['size'],
                    'city': company['city'],
                    'state': company.get('state'),
                    'country': company['country'],
                    'website': f"https://{company['name'].lower().replace(' ', '').replace('(', '').replace(')', '')}.com",
                    'contact': f"{company['contact']} ({company['role']})",
                    'priority': company['priority'],
                }
                
                session.execute(text(sql), params)
                inserted += 1
                
            except Exception as e:
                print(f"⚠️  Error inserting {company['name']}: {e}")
                continue
        
        session.commit()
        
        # Verify count
        result = session.execute(text("SELECT COUNT(*) FROM bdr_companies"))
        new_count = result.scalar()
        
        print(f"\n✅ Inserted {inserted} companies")
        print(f"📊 Total records in bdr_companies: {new_count}")
        
        # Show breakdown
        result = session.execute(text("SELECT priority, COUNT(*) FROM bdr_companies GROUP BY priority ORDER BY priority"))
        print("\n📈 By Priority:")
        for row in result:
            print(f"   Priority {row[0]}: {row[1]} companies")
        
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
