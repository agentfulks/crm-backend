#!/usr/bin/env python3
"""Verify LinkedIn URLs and emails for 40 BDR primary contacts."""

import re
import urllib.request
import urllib.error
import ssl

# Create SSL context that doesn't verify certificates (for testing)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 40 Primary contacts extracted from the data
contacts = [
    {"name": "Alexandre Yazdi", "company": "Voodoo", "email": "alexandre.yazdi@voodoo.io", "linkedin": "https://linkedin.com/in/alexandre-yazdi-21a9813a"},
    {"name": "Daniel Nathan", "company": "Homa Games", "email": "daniel.nathan@homagames.com", "linkedin": "https://linkedin.com/in/danielelinathan"},
    {"name": "Yegor Vaikhanski", "company": "SayGames", "email": "y.vaikhanski@saygames.by", "linkedin": "https://linkedin.com/in/yegor-vaikhanski-9922a526"},
    {"name": "Nadav Ashkenazy", "company": "Supersonic Studios", "email": "nadav.ashkenazy@supersonic.com", "linkedin": "https://linkedin.com/in/nadavashkenazy"},
    {"name": "Burak Vardal", "company": "Rollic (Zynga)", "email": "burak.vardal@rollicgames.com", "linkedin": "https://linkedin.com/in/burak-vardal"},
    {"name": "David Darling", "company": "Kwalee", "email": "d.darling@kwalee.com", "linkedin": "https://linkedin.com/in/ddarling"},
    {"name": "Sagi Schliesser", "company": "CrazyLabs", "email": "sagi@crazylabs.com", "linkedin": "https://linkedin.com/in/sagischliesser"},
    {"name": "Gilberto Marcal", "company": "Lion Studios", "email": "gilberto.marcal@lionstudios.cc", "linkedin": "https://linkedin.com/in/gilberto-santos-marcal-303087232"},
    {"name": "Marcin Olejarz", "company": "Boombit", "email": "marcin.olejarz@boombit.com", "linkedin": "https://linkedin.com/in/marcin-olejarz"},
    {"name": "Bill Vo", "company": "Amanotes", "email": "bill@amanotes.com", "linkedin": "https://linkedin.com/in/billvo"},
    {"name": "Bobby Loya", "company": "Scopely", "email": "bobby.loya@scopely.com", "linkedin": "https://linkedin.com/in/bobby-loya-117b209"},
    {"name": "Dmitri Lipnitsky", "company": "Gismart", "email": "dmitri.lipnitsky@gismart.com", "linkedin": "https://linkedin.com/in/lipnitsky"},
    {"name": "Hervé Montoute", "company": "TapNation", "email": "herve.montoute@tap-nation.io", "linkedin": "https://linkedin.com/in/hervemontoute"},
    {"name": "Junsik Kong", "company": "Supercent", "email": "junsik.kong@supercent.io", "linkedin": "N/A"},
    {"name": "Daniel Hasselberg", "company": "MAG Interactive", "email": "daniel.hasselberg@maginteractive.com", "linkedin": "N/A"},
    {"name": "Erez Mishli", "company": "Moonee", "email": "erez@moonee.io", "linkedin": "https://linkedin.com/in/erezmi"},
    {"name": "Dmitri Bukhman", "company": "Playrix", "email": "dmitri.bukhman@playrix.com", "linkedin": "https://linkedin.com/in/dmitribukhman"},
    {"name": "Michel Morcos", "company": "Ketchapp (Ubisoft)", "email": "michel.morcos@ketchapp.com", "linkedin": "https://linkedin.com/in/michel-morcos"},
    {"name": "Mehmet Ecevit", "company": "Gram Games", "email": "mehmet.ecevit@gramgames.com", "linkedin": "N/A"},
    {"name": "Ivan Gorchakov", "company": "Belka Games", "email": "ivan.gorchakov@belkagames.com", "linkedin": "https://linkedin.com/in/ivan-gorchakov-75bba6290"},
    {"name": "Emre Tas", "company": "Alictus (SciPlay)", "email": "emre@alictus.com", "linkedin": "https://linkedin.com/in/aemretas"},
    {"name": "Mert Can Kurum", "company": "Ruby Games (Rovio)", "email": "mert@rubygames.io", "linkedin": "https://linkedin.com/in/mert-can-kurum"},
    {"name": "Neil Young", "company": "N3TWORK Studios", "email": "neil@n3twork.com", "linkedin": "https://linkedin.com/in/neil-young-b84113"},
    {"name": "Lior Shiff", "company": "Tripledot Studios", "email": "lior.shiff@tripledotstudios.com", "linkedin": "https://linkedin.com/in/shiff"},
    {"name": "John Lee", "company": "PeopleFun", "email": "john.lee@peoplefun.com", "linkedin": "https://linkedin.com/in/chong-oak-john-lee"},
    {"name": "Quyet Nguyen", "company": "iKame Games", "email": "quyet.nguyen@ikame.vn", "linkedin": "N/A"},
    {"name": "Le Manh Duc", "company": "Bravestars Games", "email": "duc.lm@bravestars.com", "linkedin": "https://linkedin.com/in/duc-le-manh"},
    {"name": "Victor Lazarte", "company": "Wildlife Studios", "email": "victor.lazarte@wildlifestudios.com", "linkedin": "https://linkedin.com/in/victorlazarte"},
    {"name": "Anton Reinhold", "company": "Nexters (GDEV)", "email": "anton.reinhold@nexters.com", "linkedin": "https://linkedin.com/in/anton-reinhold-06157514"},
    {"name": "Teemu Närhi", "company": "Fingersoft", "email": "teemu.narhi@fingersoft.com", "linkedin": "https://linkedin.com/in/teemu-narhi"},
    {"name": "MJ Fahmi", "company": "Babil Games", "email": "mj.fahmi@babilgames.com", "linkedin": "https://linkedin.com/in/mj-fahmi"},
    {"name": "Ziad Feghali", "company": "Wixel Studios", "email": "ziad@wixelstudios.com", "linkedin": "N/A"},
    {"name": "Forest Willard", "company": "Innersloth", "email": "forest@innersloth.com", "linkedin": "https://linkedin.com/in/forestwillard"},
    {"name": "John Earner", "company": "Space Ape Games", "email": "john.earner@spaceapegames.com", "linkedin": "https://linkedin.com/in/johnearner"},
    {"name": "Guillaume Sztejnberg", "company": "Green Panda Games", "email": "guillaume@greenpandagames.com", "linkedin": "https://linkedin.com/in/guillaume-sztejnberg"},
    {"name": "Manuel Prueter", "company": "Colossi Games", "email": "manuel.prueter@colossi.games", "linkedin": "https://linkedin.com/in/manuel-prueter"},
    {"name": "Mikael Le Goff", "company": "Dual Cat", "email": "mikael@dual-cat.com", "linkedin": "https://linkedin.com/in/mikaelle-goff"},
    {"name": "Klaas Kersting", "company": "Flaregames", "email": "klaas.kersting@flaregames.com", "linkedin": "https://linkedin.com/in/klaaskersting"},
    {"name": "Asbjoern Malte Soendergaard", "company": "Tactile Games", "email": "asbjoern@tactilegames.com", "linkedin": "https://linkedin.com/in/asbjoern"},
]

def verify_email_format(email):
    """Verify email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def verify_linkedin(url):
    """Verify LinkedIn URL returns valid response."""
    if url == "N/A" or not url:
        return "MISSING", "No LinkedIn URL provided"
    
    try:
        # Try to fetch the URL
        req = urllib.request.Request(
            url, 
            method='HEAD',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response = urllib.request.urlopen(req, timeout=10, context=ssl_context)
        
        if response.status == 200:
            return "VALID", f"Status {response.status}"
        elif response.status in [301, 302]:
            return "REDIRECT", f"Status {response.status}"
        else:
            return "CHECK", f"Status {response.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "BROKEN", f"404 Not Found"
        elif e.code == 429:
            return "RATE_LIMITED", f"429 Rate Limited"
        elif e.code == 999:
            return "BLOCKED", f"999 LinkedIn Blocking"
        else:
            return "ERROR", f"HTTP {e.code}"
    except Exception as e:
        return "ERROR", str(e)[:50]

# Verify all contacts
print("Verifying 40 BDR contacts...\n")

verified = []
broken_linkedin = []
invalid_emails = []
missing_linkedin = []

for contact in contacts:
    # Verify email
    email_valid = verify_email_format(contact['email'])
    
    # Verify LinkedIn
    linkedin_status, linkedin_msg = verify_linkedin(contact['linkedin'])
    
    result = {
        **contact,
        'email_valid': email_valid,
        'linkedin_status': linkedin_status,
        'linkedin_msg': linkedin_msg
    }
    verified.append(result)
    
    if not email_valid:
        invalid_emails.append(result)
    
    if linkedin_status == "BROKEN":
        broken_linkedin.append(result)
    elif linkedin_status in ["MISSING", "N/A"]:
        missing_linkedin.append(result)
    
    print(f"✓ {contact['name']} ({contact['company']})")
    print(f"  Email: {contact['email']} - {'✓ Valid' if email_valid else '✗ Invalid'}")
    print(f"  LinkedIn: {linkedin_status} - {linkedin_msg}")
    print()

# Summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
print(f"Total contacts checked: {len(contacts)}")
print(f"Valid emails: {sum(1 for v in verified if v['email_valid'])}")
print(f"Invalid emails: {len(invalid_emails)}")
print(f"Valid LinkedIn: {sum(1 for v in verified if v['linkedin_status'] == 'VALID')}")
print(f"Broken LinkedIn (404): {len(broken_linkedin)}")
print(f"Missing LinkedIn: {len(missing_linkedin)}")
print(f"Other LinkedIn issues: {len(verified) - sum(1 for v in verified if v['linkedin_status'] in ['VALID', 'BROKEN', 'MISSING'])}")

print("\n\nBROKEN LINKEDIN URLs:")
for c in broken_linkedin:
    print(f"  - {c['name']} ({c['company']}): {c['linkedin']}")

print("\nMISSING LINKEDIN URLs:")
for c in missing_linkedin:
    print(f"  - {c['name']} ({c['company']})")

print("\nINVALID EMAILS:")
for c in invalid_emails:
    print(f"  - {c['name']} ({c['company']}): {c['email']}")
