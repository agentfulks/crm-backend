#!/usr/bin/env python3
"""Extract BDR contacts with LinkedIn URLs from the markdown file."""

import re

# Read the all_contacts file
with open('/data/workspace/deliverables/bdr_game_studios/all_contacts_101_studios.md', 'r') as f:
    content = f.read()

# Parse contacts - looking for pattern like:
# 1. **Name** | Title | [linkedin.com/in/...](https://linkedin.com/in/...) | email@...
contacts = []

# Split by numbered entries
entries = re.split(r'\n\d+\. ', content)

for entry in entries[1:]:  # Skip first split which is header
    # Extract name (between ** **)
    name_match = re.search(r'\*\*(.*?)\*\*', entry)
    if not name_match:
        continue
    name = name_match.group(1).strip()
    
    # Extract LinkedIn URL
    linkedin_match = re.search(r'\[linkedin\.com/in/[^\]]+\]\((https?://[^\)]+)\)', entry)
    if not linkedin_match:
        # Try alternate format without brackets
        linkedin_match = re.search(r'(https?://linkedin\.com/in/[^\s|]+)', entry)
    
    linkedin_url = linkedin_match.group(1) if linkedin_match else "N/A"
    
    # Extract email
    email_match = re.search(r'[\w.-]+@[\w.-]+\.[\w]+', entry)
    email = email_match.group(0) if email_match else "N/A"
    
    # Extract company from context (usually mentioned before the contact)
    # Look for company name in the lines before this entry
    
    contacts.append({
        'name': name,
        'linkedin': linkedin_url,
        'email': email
    })

# Print first 50
print(f"Found {len(contacts)} contacts")
for i, c in enumerate(contacts[:50], 1):
    print(f"{i}. {c['name']} | {c['email']} | {c['linkedin']}")
