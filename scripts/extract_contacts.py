#!/usr/bin/env python3
"""Extract and verify BDR contacts from CSV files."""

import csv
import re

# Read all three batch files
contacts = []

# Process Batch A (Tier-1)
with open('/data/workspace/deliverables/bdr_game_studios/trello_import_batch_a.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        desc = row['Description']
        
        # Extract company name
        company = row['Name']
        
        # Extract primary contact name and email
        primary_match = re.search(r'\*\*Primary Contact:\*\* (.*?) \|', desc)
        email_match = re.search(r'\| ([\w.-]+@[\w.-]+\.[\w]+)', desc)
        
        if primary_match and email_match:
            full_name = primary_match.group(1).strip()
            email = email_match.group(1).strip()
            
            # Extract LinkedIn URL - look for linkedin.com patterns
            linkedin_match = re.search(r'\| (https?://linkedin\.com/in/[^\s|]+)', desc)
            linkedin_url = linkedin_match.group(1) if linkedin_match else "N/A"
            
            contacts.append({
                'company': company,
                'name': full_name,
                'email': email,
                'linkedin': linkedin_url,
                'tier': 'Tier-1'
            })

# Process Batch B (Tier-2)
with open('/data/workspace/deliverables/bdr_game_studios/trello_import_batch_b.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        desc = row['Description']
        company = row['Name']
        
        primary_match = re.search(r'\*\*Primary Contact:\*\* (.*?) \|', desc)
        email_match = re.search(r'\| ([\w.-]+@[\w.-]+\.[\w]+)', desc)
        
        if primary_match and email_match:
            full_name = primary_match.group(1).strip()
            email = email_match.group(1).strip()
            
            linkedin_match = re.search(r'\| (https?://linkedin\.com/in/[^\s|]+)', desc)
            linkedin_url = linkedin_match.group(1) if linkedin_match else "N/A"
            
            contacts.append({
                'company': company,
                'name': full_name,
                'email': email,
                'linkedin': linkedin_url,
                'tier': 'Tier-2'
            })

# Process Batch C (Tier-3) - only need first 10 to reach 40 total
with open('/data/workspace/deliverables/bdr_game_studios/trello_import_batch_c.csv', 'r') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if count >= 10:
            break
        desc = row['Description']
        company = row['Name']
        
        primary_match = re.search(r'\*\*Primary Contact:\*\* (.*?) \|', desc)
        email_match = re.search(r'\| ([\w.-]+@[\w.-]+\.[\w]+)', desc)
        
        if primary_match and email_match:
            full_name = primary_match.group(1).strip()
            email = email_match.group(1).strip()
            
            linkedin_match = re.search(r'\| (https?://linkedin\.com/in/[^\s|]+)', desc)
            linkedin_url = linkedin_match.group(1) if linkedin_match else "N/A"
            
            contacts.append({
                'company': company,
                'name': full_name,
                'email': email,
                'linkedin': linkedin_url,
                'tier': 'Tier-3'
            })
            count += 1

# Output summary
print(f"Total contacts extracted: {len(contacts)}")
for i, c in enumerate(contacts, 1):
    print(f"{i}. {c['name']} ({c['company']}) | {c['email']} | {c['linkedin']}")

# Save to verification file
with open('/data/workspace/deliverables/bdr_contacts_extracted.csv', 'w') as f:
    f.write('Company,Name,Email,LinkedIn,Tier\n')
    for c in contacts:
        f.write(f"{c['company']},{c['name']},{c['email']},{c['linkedin']},{c['tier']}\n")

print(f"\nExtracted {len(contacts)} contacts to bdr_contacts_extracted.csv")
