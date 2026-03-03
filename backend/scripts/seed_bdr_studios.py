#!/usr/bin/env python3
"""
Insert 50 BDR game studios into the database.

Usage:
    cd /data/workspace/backend
    .venv/bin/python scripts/seed_bdr_studios.py
"""
import sys
from pathlib import Path

# Add backend to path
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from sqlalchemy import text
from app.db.session import SessionLocal

# The 50 studios from research
BDR_STUDIOS = [
    {"name": "Ketchapp", "location": "Paris, France", "size": "51-200", "contact": "Michel Morcos", "role": "CEO & Co-Founder", "email": "michel@ketchapp.com", "priority": "A"},
    {"name": "Colossi Games", "location": "Limassol, Cyprus", "size": "11-50", "contact": "Manuel Prueter", "role": "CEO & Co-Founder", "email": "manuel@colossi.games", "priority": "A"},
    {"name": "Tactile Games", "location": "Copenhagen, Denmark", "size": "51-200", "contact": "Asbjoern Malte Soendergaard", "role": "CEO & Founder", "email": "asbjoern@tactilegames.com", "priority": "A"},
    {"name": "Metacore Games", "location": "Helsinki, Finland", "size": "51-200", "contact": "Mika Tammenkoski", "role": "CEO & Co-Founder", "email": "mika@metacoregames.com", "priority": "A"},
    {"name": "Ruby Games", "location": "Izmir, Turkey", "size": "11-50", "contact": "Mert Can Kurum", "role": "CEO & Founder", "email": "mert@rubygames.com", "priority": "A"},
    {"name": "Second Dinner", "location": "Irvine, CA, USA", "size": "51-200", "contact": "Hamilton Chu", "role": "CEO & Co-Founder", "email": "hamilton@seconddinner.com", "priority": "A"},
    {"name": "Superplay", "location": "Tel Aviv, Israel", "size": "51-200", "contact": "Elad Drory", "role": "CEO", "email": "elad@superplay.co", "priority": "A"},
    {"name": "Space Ape Games", "location": "London, UK", "size": "51-200", "contact": "John Earner", "role": "CEO & Co-Founder", "email": "john@spaceapegames.com", "priority": "A"},
    {"name": "Homa Games", "location": "Paris, France", "size": "51-200", "contact": "Daniel Nathan", "role": "CEO & Co-Founder", "email": "daniel@homagames.com", "priority": "A"},
    {"name": "SayGames", "location": "Minsk, Belarus", "size": "51-200", "contact": "Evgeny Ponomarenko", "role": "CEO & Founder", "email": "evgeny@saygames.by", "priority": "A"},
    {"name": "Green Panda Games", "location": "Paris, France", "size": "51-200", "contact": "Guillaume Sztejnberg", "role": "CEO & Founder", "email": "guillaume@greenpandagames.com", "priority": "B"},
    {"name": "Tripledot Studios", "location": "London, UK", "size": "51-200", "contact": "Lior Shiff", "role": "CEO & Co-Founder", "email": "lior@tripledotstudios.com", "priority": "B"},
    {"name": "First Fun", "location": "London, UK", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@firstfungames.com", "priority": "B"},
    {"name": "Century Games", "location": "Beijing, China", "size": "201-500", "contact": "Song Qian", "role": "CEO", "email": "song@centurygames.com", "priority": "B"},
    {"name": "Joy Nice Games", "location": "China", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@joynices.com", "priority": "B"},
    {"name": "Microfun", "location": "China", "size": "51-200", "contact": "CEO", "role": "CEO", "email": "contact@microfun.com", "priority": "B"},
    {"name": "Voodoo", "location": "Paris, France", "size": "201-500", "contact": "Alexandre Yazdi", "role": "CEO & Co-Founder", "email": "alexandre@voodoo.io", "priority": "A"},
    {"name": "Rollic Games", "location": "Istanbul, Turkey", "size": "51-200", "contact": "Burak Vardal", "role": "CEO", "email": "burak@rolic.com", "priority": "A"},
    {"name": "Kwalee", "location": "Leamington Spa, UK", "size": "51-200", "contact": "David Darling", "role": "CEO & Founder", "email": "david@kwalee.com", "priority": "A"},
    {"name": "Belka Games", "location": "Vilnius, Lithuania", "size": "51-200", "contact": "Egor Kozlov", "role": "CEO & Co-Founder", "email": "egor@belkagames.com", "priority": "B"},
    {"name": "Alictus Games", "location": "Ankara, Turkey", "size": "51-200", "contact": "Aytek Kurtuluş", "role": "CEO & Co-Founder", "email": "aytek@alictus.com", "priority": "B"},
    {"name": "Supersonic Studios", "location": "Tel Aviv, Israel", "size": "51-200", "contact": "Nadav Ashkenazy", "role": "CEO", "email": "nadav@supersonic.com", "priority": "A"},
    {"name": "tinyBuild", "location": "Amsterdam, Netherlands", "size": "51-200", "contact": "Alex Nichiporchik", "role": "CEO & Co-Founder", "email": "alex@tinybuild.com", "priority": "B"},
    {"name": "East Side Games", "location": "Vancouver, Canada", "size": "51-200", "contact": "Jason Bailey", "role": "CEO & Co-Founder", "email": "jason@eastsidegames.com", "priority": "B"},
    {"name": "Pocket Gems", "location": "San Francisco, CA, USA", "size": "201-500", "contact": "Ben Liu", "role": "CEO", "email": "ben@pocketgems.com", "priority": "B"},
    {"name": "Ketchapp (Antoine)", "location": "Paris, France", "size": "51-200", "contact": "Antoine Morcos", "role": "Co-Founder", "email": "antoine@ketchapp.com", "priority": "B"},
    {"name": "Niantic", "location": "San Francisco, CA, USA", "size": "501+", "contact": "John Hanke", "role": "CEO & Founder", "email": "john@nianticlabs.com", "priority": "A"},
    {"name": "Wooga", "location": "Berlin, Germany", "size": "201-500", "contact": "Jens Begemann", "role": "Founder", "email": "jens@wooga.com", "priority": "B"},
    {"name": "PLAYSTUDIOS", "location": "Las Vegas, NV, USA", "size": "201-500", "contact": "Andrew Pascal", "role": "Chairman & CEO", "email": "andrew@playstudios.com", "priority": "B"},
    {"name": "ZPLAY Games", "location": "Beijing, China", "size": "51-200", "contact": "He Peng", "role": "Founder & CEO", "email": "he@zplay.com", "priority": "B"},
    {"name": "Playgendary", "location": "Limassol, Cyprus", "size": "51-200", "contact": "Dmitriy Shelengovskiy", "role": "Founder & CEO", "email": "dmitriy@playgendary.com", "priority": "B"},
    {"name": "JoyPac", "location": "Berlin, Germany", "size": "11-50", "contact": "Mark Zhou", "role": "CEO", "email": "mark@joypac.com", "priority": "B"},
    {"name": "Mythical Games", "location": "Los Angeles, CA, USA", "size": "51-200", "contact": "John Linden", "role": "CEO & Co-Founder", "email": "john@mythicalgames.com", "priority": "A"},
    {"name": "Mino Games", "location": "Montreal, Canada", "size": "51-200", "contact": "Sasha Mackinnon", "role": "CEO & Co-Founder", "email": "sasha@minogames.com", "priority": "B"},
    {"name": "Miniclip", "location": "Neuchâtel, Switzerland", "size": "201-500", "contact": "Robert Small", "role": "CEO & Co-Founder", "email": "rob@miniclip.com", "priority": "A"},
    {"name": "Wildlife Studios", "location": "São Paulo, Brazil", "size": "201-500", "contact": "Victor Lazarte", "role": "CEO & Co-Founder", "email": "victor@wildlifestudios.com", "priority": "A"},
    {"name": "Fingersoft", "location": "Oulu, Finland", "size": "51-200", "contact": "Teemu Närhi", "role": "CEO", "email": "teemu@fingersoft.com", "priority": "A"},
    {"name": "Innersloth", "location": "Redmond, WA, USA", "size": "11-50", "contact": "Forest Willard", "role": "CEO & Co-Founder", "email": "forest@innersloth.com", "priority": "A"},
    {"name": "Scopely", "location": "Los Angeles, CA, USA", "size": "501+", "contact": "Walter Driver", "role": "Co-Founder & Co-CEO", "email": "walter@scopely.com", "priority": "A"},
    {"name": "Lion Studios", "location": "San Francisco, CA, USA", "size": "51-200", "contact": "Nick Bogovich", "role": "CEO", "email": "nick@lionstudios.cc", "priority": "A"},
    {"name": "Nexters", "location": "Limassol, Cyprus", "size": "501+", "contact": "Anton Reinhold", "role": "CEO", "email": "anton@nexters.com", "priority": "B"},
    {"name": "Playsome", "location": "Helsinki, Finland", "size": "11-50", "contact": "Timo Palonen", "role": "CEO & Co-Founder", "email": "timo@playsome.games", "priority": "B"},
    {"name": "Crunchyroll Games", "location": "San Francisco, CA, USA", "size": "501+", "contact": "Rahul Purini", "role": "CEO", "email": "rahul@crunchyroll.com", "priority": "B"},
    {"name": "FunPlus", "location": "Beijing, China", "size": "501+", "contact": "Andy Zhong", "role": "CEO", "email": "andy@funplus.com", "priority": "A"},
    {"name": "Gismart", "location": "London, UK", "size": "201-500", "contact": "Mykola Tymkiv", "role": "CEO", "email": "mykola@gismart.com", "priority": "B"},
    {"name": "Dual Cat", "location": "Paris, France", "size": "11-50", "contact": "Mikael Le Goff", "role": "CEO & Founder", "email": "mikael@dual-cat.com", "priority": "B"},
    {"name": "Magmatic Games", "location": "Berlin, Germany", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@magmaticgames.com", "priority": "B"},
    {"name": "PlayCore", "location": "Chattanooga, TN, USA", "size": "51-200", "contact": "Roger Posacki", "role": "President & CEO", "email": "roger@playcore.com", "priority": "C"},
    {"name": "Neuroflag", "location": "Tokyo, Japan", "size": "11-50", "contact": "CEO", "role": "CEO", "email": "contact@neuroflag.com", "priority": "C"},
    {"name": "Gubbe", "location": "Helsinki, Finland", "size": "11-50", "contact": "Sandra Lounamaa", "role": "CEO & Co-Founder", "email": "sandra@gubbe.io", "priority": "C"},
]


def get_table_columns(session, table_name):
    """Get column names for a table."""
    result = session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = :table
        ORDER BY ordinal_position
    """), {"table": table_name})
    return [row[0] for row in result]


def main():
    """Insert BDR studios into database."""
    print("=" * 60)
    print("BDR Studios Database Seeder")
    print("=" * 60)
    
    session = SessionLocal()
    try:
        # Check available tables
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"\nAvailable tables: {tables}")
        
        # Look for BDR-related tables
        bdr_tables = [t for t in tables if 'bdr' in t.lower() or 'studio' in t.lower() or 'company' in t.lower()]
        
        if not bdr_tables:
            print("\n❌ No BDR or studio tables found!")
            print("Available tables:", tables)
            return
        
        print(f"\nFound tables: {bdr_tables}")
        
        # Use the first matching table
        target_table = bdr_tables[0]
        print(f"\nUsing table: {target_table}")
        
        # Get columns
        columns = get_table_columns(session, target_table)
        print(f"Columns: {columns}")
        
        # Check existing count
        count_result = session.execute(text(f"SELECT COUNT(*) FROM {target_table}"))
        existing_count = count_result.scalar()
        print(f"\nExisting records: {existing_count}")
        
        # Insert data
        inserted = 0
        for studio in BDR_STUDIOS:
            try:
                # Build INSERT based on available columns
                values = {}
                if 'name' in columns:
                    values['name'] = studio['name']
                if 'company_name' in columns:
                    values['company_name'] = studio['name']
                if 'location' in columns:
                    values['location'] = studio['location']
                if 'size' in columns:
                    values['size'] = studio['size']
                if 'contact_name' in columns:
                    values['contact_name'] = studio['contact']
                if 'contact_email' in columns:
                    values['contact_email'] = studio['email']
                if 'priority' in columns:
                    values['priority'] = studio['priority']
                if 'status' in columns:
                    values['status'] = 'NEW'
                
                if not values:
                    print(f"⚠️  No matching columns for {studio['name']}")
                    continue
                
                cols = ', '.join(values.keys())
                placeholders = ', '.join([f':{k}' for k in values.keys()])
                
                sql = f"INSERT INTO {target_table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                session.execute(text(sql), values)
                inserted += 1
                
            except Exception as e:
                print(f"⚠️  Error inserting {studio['name']}: {e}")
                continue
        
        session.commit()
        
        # Verify count
        count_result = session.execute(text(f"SELECT COUNT(*) FROM {target_table}"))
        new_count = count_result.scalar()
        
        print(f"\n✅ Inserted {inserted} studios")
        print(f"📊 Total records in {target_table}: {new_count}")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
