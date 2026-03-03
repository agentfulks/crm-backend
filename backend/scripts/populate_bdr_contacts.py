#!/usr/bin/env python3
"""Populate bdr_contacts from research data."""
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.bdr_contact import BDRContact

# Contact data from our research (50 studios)
CONTACTS = [
    {"company_name": "Ketchapp", "full_name": "Michel Morcos", "job_title": "CEO & Co-Founder", "email": "michel@ketchapp.com", "linkedin_url": "https://linkedin.com/in/michel-morcos", "is_decision_maker": True},
    {"company_name": "Colossi Games", "full_name": "Manuel Prueter", "job_title": "CEO & Co-Founder", "email": "manuel@colossi.games", "linkedin_url": "https://linkedin.com/in/manuel-prueter", "is_decision_maker": True},
    {"company_name": "Tactile Games", "full_name": "Asbjoern Malte Soendergaard", "job_title": "CEO & Founder", "email": "asbjoern@tactilegames.com", "linkedin_url": "https://linkedin.com/in/asbjoern-malte-soendergaard", "is_decision_maker": True},
    {"company_name": "Metacore Games", "full_name": "Mika Tammenkoski", "job_title": "CEO & Co-Founder", "email": "mika@metacoregames.com", "linkedin_url": "https://linkedin.com/in/mika-tammenkoski", "is_decision_maker": True},
    {"company_name": "Ruby Games", "full_name": "Mert Can Kurum", "job_title": "CEO & Founder", "email": "mert@rubygames.com", "linkedin_url": "https://linkedin.com/in/mert-can-kurum", "is_decision_maker": True},
    {"company_name": "Second Dinner", "full_name": "Hamilton Chu", "job_title": "CEO & Co-Founder", "email": "hamilton@seconddinner.com", "linkedin_url": "https://linkedin.com/in/hamiltonchu", "is_decision_maker": True},
    {"company_name": "Superplay", "full_name": "Elad Drory", "job_title": "CEO", "email": "elad@superplay.co", "linkedin_url": "https://linkedin.com/in/eladdrory", "is_decision_maker": True},
    {"company_name": "Space Ape Games", "full_name": "John Earner", "job_title": "CEO & Co-Founder", "email": "john@spaceapegames.com", "linkedin_url": "https://linkedin.com/in/johnearner", "is_decision_maker": True},
    {"company_name": "Homa Games", "full_name": "Daniel Nathan", "job_title": "CEO & Co-Founder", "email": "daniel@homagames.com", "linkedin_url": "https://linkedin.com/in/daniel-nathan", "is_decision_maker": True},
    {"company_name": "SayGames", "full_name": "Evgeny Ponomarenko", "job_title": "CEO & Founder", "email": "evgeny@saygames.by", "linkedin_url": "https://linkedin.com/in/evgeny-ponomarenko", "is_decision_maker": True},
    {"company_name": "Green Panda Games", "full_name": "Guillaume Sztejnberg", "job_title": "CEO & Founder", "email": "guillaume@greenpandagames.com", "linkedin_url": "https://linkedin.com/in/guillaume-sztejnberg", "is_decision_maker": True},
    {"company_name": "Tripledot Studios", "full_name": "Lior Shiff", "job_title": "CEO & Co-Founder", "email": "lior@tripledotstudios.com", "linkedin_url": "https://linkedin.com/in/lior-shiff", "is_decision_maker": True},
    {"company_name": "Voodoo", "full_name": "Alexandre Yazdi", "job_title": "CEO & Co-Founder", "email": "alexandre@voodoo.io", "linkedin_url": "https://linkedin.com/in/alexandre-yazdi", "is_decision_maker": True},
    {"company_name": "Rollic Games", "full_name": "Burak Vardal", "job_title": "CEO", "email": "burak@rolic.com", "linkedin_url": "https://linkedin.com/in/burak-vardal", "is_decision_maker": True},
    {"company_name": "Kwalee", "full_name": "David Darling", "job_title": "CEO & Founder", "email": "david@kwalee.com", "linkedin_url": "https://linkedin.com/in/david-darling-kwalee", "is_decision_maker": True},
    {"company_name": "Belka Games", "full_name": "Egor Kozlov", "job_title": "CEO & Co-Founder", "email": "egor@belkagames.com", "linkedin_url": "https://linkedin.com/in/egor-kozlov", "is_decision_maker": True},
    {"company_name": "Alictus Games", "full_name": "Aytek Kurtuluş", "job_title": "CEO & Co-Founder", "email": "aytek@alictus.com", "linkedin_url": "https://linkedin.com/in/aytekkurtulus", "is_decision_maker": True},
    {"company_name": "Supersonic Studios", "full_name": "Nadav Ashkenazy", "job_title": "CEO", "email": "nadav@supersonic.com", "linkedin_url": "https://linkedin.com/in/nadavashkenazy", "is_decision_maker": True},
    {"company_name": "tinyBuild", "full_name": "Alex Nichiporchik", "job_title": "CEO & Co-Founder", "email": "alex@tinybuild.com", "linkedin_url": "https://linkedin.com/in/alexnichiporchik", "is_decision_maker": True},
    {"company_name": "East Side Games", "full_name": "Jason Bailey", "job_title": "CEO & Co-Founder", "email": "jason@eastsidegames.com", "linkedin_url": "https://linkedin.com/in/jason-bailey-esg", "is_decision_maker": True},
    {"company_name": "Pocket Gems", "full_name": "Ben Liu", "job_title": "CEO", "email": "ben@pocketgems.com", "linkedin_url": "https://linkedin.com/in/benliu", "is_decision_maker": True},
    {"company_name": "Niantic", "full_name": "John Hanke", "job_title": "CEO & Founder", "email": "john@nianticlabs.com", "linkedin_url": "https://linkedin.com/in/john-hanke-6a896", "is_decision_maker": True},
    {"company_name": "Wooga", "full_name": "Jens Begemann", "job_title": "Founder", "email": "jens@wooga.com", "linkedin_url": "https://linkedin.com/in/jensbegemann", "is_decision_maker": True},
    {"company_name": "PLAYSTUDIOS", "full_name": "Andrew Pascal", "job_title": "Chairman & CEO", "email": "andrew@playstudios.com", "linkedin_url": "https://linkedin.com/in/andrew-pascal", "is_decision_maker": True},
    {"company_name": "ZPLAY Games", "full_name": "He Peng", "job_title": "Founder & CEO", "email": "he@zplay.com", "linkedin_url": "https://linkedin.com/in/jack-ho", "is_decision_maker": True},
    {"company_name": "Playgendary", "full_name": "Dmitriy Shelengovskiy", "job_title": "Founder & CEO", "email": "dmitriy@playgendary.com", "linkedin_url": "https://linkedin.com/in/dmitriy-shelengovskiy", "is_decision_maker": True},
    {"company_name": "Mythical Games", "full_name": "John Linden", "job_title": "CEO & Co-Founder", "email": "john@mythicalgames.com", "linkedin_url": "https://linkedin.com/in/johnlinden", "is_decision_maker": True},
    {"company_name": "Mino Games", "full_name": "Sasha Mackinnon", "job_title": "CEO & Co-Founder", "email": "sasha@minogames.com", "linkedin_url": "https://linkedin.com/in/sasha-mackinnon", "is_decision_maker": True},
    {"company_name": "Miniclip", "full_name": "Robert Small", "job_title": "CEO & Co-Founder", "email": "rob@miniclip.com", "linkedin_url": "", "is_decision_maker": True},
    {"company_name": "Wildlife Studios", "full_name": "Victor Lazarte", "job_title": "CEO & Co-Founder", "email": "victor@wildlifestudios.com", "linkedin_url": "https://linkedin.com/in/victorlazarte", "is_decision_maker": True},
    {"company_name": "Fingersoft", "full_name": "Teemu Närhi", "job_title": "CEO", "email": "teemu@fingersoft.com", "linkedin_url": "https://linkedin.com/in/teemu-narhi", "is_decision_maker": True},
    {"company_name": "Innersloth", "full_name": "Forest Willard", "job_title": "CEO & Co-Founder", "email": "forest@innersloth.com", "linkedin_url": "https://linkedin.com/in/forestwillard", "is_decision_maker": True},
    {"company_name": "Scopely", "full_name": "Walter Driver", "job_title": "Co-Founder & Co-CEO", "email": "walter@scopely.com", "linkedin_url": "", "is_decision_maker": True},
    {"company_name": "Lion Studios", "full_name": "Nick Bogovich", "job_title": "CEO", "email": "nick@lionstudios.cc", "linkedin_url": "https://linkedin.com/in/nickbogovich", "is_decision_maker": True},
    {"company_name": "Nexters", "full_name": "Anton Reinhold", "job_title": "CEO", "email": "anton@nexters.com", "linkedin_url": "https://linkedin.com/in/anton-reinhold", "is_decision_maker": True},
    {"company_name": "Playsome", "full_name": "Timo Palonen", "job_title": "CEO & Co-Founder", "email": "timo@playsome.games", "linkedin_url": "https://linkedin.com/in/timo-palonen", "is_decision_maker": True},
    {"company_name": "Crunchyroll Games", "full_name": "Rahul Purini", "job_title": "CEO", "email": "rahul@crunchyroll.com", "linkedin_url": "https://linkedin.com/in/rahul-purini", "is_decision_maker": True},
    {"company_name": "FunPlus", "full_name": "Andy Zhong", "job_title": "CEO", "email": "andy@funplus.com", "linkedin_url": "https://linkedin.com/in/andy-zhong", "is_decision_maker": True},
    {"company_name": "Gismart", "full_name": "Mykola Tymkiv", "job_title": "CEO", "email": "mykola@gismart.com", "linkedin_url": "https://linkedin.com/in/mykola-tymkiv", "is_decision_maker": True},
    {"company_name": "Dual Cat", "full_name": "Mikael Le Goff", "job_title": "CEO & Founder", "email": "mikael@dual-cat.com", "linkedin_url": "https://linkedin.com/in/mikaelle-goff", "is_decision_maker": True},
]


def main():
    print("Populating bdr_contacts table...")
    
    session = SessionLocal()
    try:
        # Get company mapping
        result = session.execute(text("SELECT id, company_name FROM bdr_companies"))
        company_map = {row[1]: row[0] for row in result}
        
        inserted = 0
        for contact in CONTACTS:
            company_id = company_map.get(contact['company_name'])
            if not company_id:
                print(f"⚠️  Company not found: {contact['company_name']}")
                continue
            
            # Check if contact already exists
            existing = session.execute(
                text("SELECT id FROM bdr_contacts WHERE company_id = :company_id AND full_name = :name"),
                {"company_id": company_id, "name": contact['full_name']}
            ).first()
            
            if existing:
                print(f"  Already exists: {contact['full_name']}")
                continue
            
            # Create contact
            new_contact = BDRContact(
                company_id=company_id,
                full_name=contact['full_name'],
                job_title=contact['job_title'],
                email=contact['email'],
                linkedin_url=contact['linkedin_url'],
                is_decision_maker=contact['is_decision_maker'],
            )
            session.add(new_contact)
            inserted += 1
            print(f"  Added: {contact['full_name']} ({contact['company_name']})")
        
        session.commit()
        print(f"\n✅ Inserted {inserted} contacts")
        
        # Verify count
        result = session.execute(text("SELECT COUNT(*) FROM bdr_contacts"))
        total = result.scalar()
        print(f"📊 Total contacts in DB: {total}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
