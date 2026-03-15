"""
LinkedIn URL Verification Script for BDR Contacts
This script verifies and corrects LinkedIn URLs for all BDR contacts in the database.
"""
import psycopg2
import json
from datetime import datetime

# Connect to database
conn = psycopg2.connect('postgresql://postgres:HPwqUCIBvdUdwixoCSeowJTlBMqnpgOL@postgres.railway.internal:5432/railway')
cur = conn.cursor()

# Get all BDR contacts that need verification
cur.execute("""
    SELECT c.id, c.full_name, c.linkedin_url, c.job_title, bc.company_name
    FROM bdr_contacts c
    JOIN bdr_companies bc ON c.company_id = bc.id
    ORDER BY bc.company_name, c.full_name
""")

contacts = cur.fetchall()
print(f"Total contacts to verify: {len(contacts)}")

# Results tracking
results = {
    'verified': [],
    'corrected': [],
    'unverified': [],
    'errors': []
}

# Process each contact
for idx, (contact_id, name, current_url, title, company) in enumerate(contacts, 1):
    print(f"\n[{idx}/{len(contacts)}] {name} | {company}")
    print(f"  Current URL: {current_url}")
    
    # For now, mark as needing verification
    # The actual web search verification will be done in batches
    results['unverified'].append({
        'id': str(contact_id),
        'name': name,
        'company': company,
        'current_url': current_url,
        'status': 'pending_verification'
    })

# Save results to file for processing
with open('/data/workspace/deliverables/bdr_linkedin_pending_verification.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n=== SUMMARY ===")
print(f"Total contacts: {len(contacts)}")
print(f"Pending verification: {len(results['unverified'])}")
print(f"\nResults saved to: bdr_linkedin_pending_verification.json")

cur.close()
conn.close()
