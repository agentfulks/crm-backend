# LinkedIn URL Verification Results - March 6, 2026

## Summary
This file contains verified LinkedIn URLs for BDR and VC contacts found through web search.

## BDR CONTACTS - Verified URLs

| Name | Studio | Correct LinkedIn URL | Status |
|------|--------|---------------------|--------|
| Alexandre Yazdi | Voodoo | https://www.linkedin.com/in/alexandre-yazdi-21a9813a/ | ✓ Verified |
| Andrew Pascal | playstudios | https://www.linkedin.com/in/andrew-pascal-926aaa27/ | ✓ Verified |
| Anton Reinhold | Nexters | https://www.linkedin.com/in/anton-reinhold-06157514/ | ✓ Verified |
| Ben Liu | Pocket Gems | https://www.linkedin.com/in/benliuprofile/ | ✓ Verified |
| Daniel Nathan | Homa Games | https://www.linkedin.com/in/danielelinathan/ | ✓ Verified |
| David Darling | Kwalee | https://www.linkedin.com/in/ddarling/ | ✓ Verified |
| Egor Kozlov | Belka Games | https://www.linkedin.com/in/yegor-kozlov-99a46587/ | ✓ Verified (spelled Yegor) |
| Forest Willard | Innersloth | https://www.linkedin.com/in/forest-w-202b579a/ | ✓ Verified |
| Guillaume Sztejnberg | Green Panda Games | https://fr.linkedin.com/in/gsztejnberg | ✓ Verified |
| Hamilton Chu | Second Dinner | https://www.linkedin.com/in/hamilton-chu-b92909/ | ✓ Verified |
| Jason Bailey | East Side Games | https://www.linkedin.com/in/JasonBailey/ | ✓ Verified |
| John Earner | Space Ape Games | https://uk.linkedin.com/in/john-earner-076101 | ✓ Verified |
| Lior Shiff | Tripledot Studios | https://uk.linkedin.com/in/shiff | ✓ Verified |
| Mert Can Kurum | Ruby Games | https://tr.linkedin.com/in/mert-can-kurum-a4123961 | ✓ Verified |

## VC CONTACTS - Verified URLs

| Name | Fund | Correct LinkedIn URL | Status |
|------|------|---------------------|--------|
| Jens Hilgers | BITKRAFT Ventures | https://de.linkedin.com/in/jenshilgers | ✓ Verified |
| Josh Chapman | Konvoy Ventures | https://www.linkedin.com/in/joshchapmanb/ | ✓ Verified |
| Steve Cho | Mechanism Capital | https://www.linkedin.com/in/stevencho/ | ✓ Verified |
| Jesse Walden | Variant | https://www.linkedin.com/in/jessewalden/ | ✓ Verified |
| Li Jin | Variant | https://www.linkedin.com/in/ljin1/ | ✓ Verified |
| Chris Dixon | a16z crypto | https://www.linkedin.com/in/chris-dixon-9599b127b/ | ✓ Verified |
| Stephen McKeon | Collab+Currency | https://www.linkedin.com/in/smckeon | ✓ Verified |
| Nick Tuosto | Griffin Gaming Partners | https://www.linkedin.com/in/ntuosto/ | ✓ Verified |

## SQL UPDATE Statements

### BDR Contacts Updates
```sql
-- BDR Contacts Corrections
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/alexandre-yazdi-21a9813a/' WHERE name = 'Alexandre Yazdi';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/andrew-pascal-926aaa27/' WHERE name = 'Andrew Pascal';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/anton-reinhold-06157514/' WHERE name = 'Anton Reinhold';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/benliuprofile/' WHERE name = 'Ben Liu';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/danielelinathan/' WHERE name = 'Daniel Nathan';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/ddarling/' WHERE name = 'David Darling';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/yegor-kozlov-99a46587/' WHERE name = 'Egor Kozlov';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/forest-w-202b579a/' WHERE name = 'Forest Willard';
UPDATE bdr_contacts SET linkedin_url = 'https://fr.linkedin.com/in/gsztejnberg' WHERE name = 'Guillaume Sztejnberg';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/hamilton-chu-b92909/' WHERE name = 'Hamilton Chu';
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/JasonBailey/' WHERE name = 'Jason Bailey';
UPDATE bdr_contacts SET linkedin_url = 'https://uk.linkedin.com/in/john-earner-076101' WHERE name = 'John Earner';
UPDATE bdr_contacts SET linkedin_url = 'https://uk.linkedin.com/in/shiff' WHERE name = 'Lior Shiff';
UPDATE bdr_contacts SET linkedin_url = 'https://tr.linkedin.com/in/mert-can-kurum-a4123961' WHERE name = 'Mert Can Kurum';
```

### VC Contacts Updates
```sql
-- VC Contacts Corrections
UPDATE contacts SET linkedin_url = 'https://de.linkedin.com/in/jenshilgers' WHERE name = 'Jens Hilgers';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/joshchapmanb/' WHERE name = 'Josh Chapman';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/stevencho/' WHERE name = 'Steve Cho';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/jessewalden/' WHERE name = 'Jesse Walden';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/ljin1/' WHERE name = 'Li Jin';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/chris-dixon-9599b127b/' WHERE name = 'Chris Dixon';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/smckeon' WHERE name = 'Stephen McKeon';
UPDATE contacts SET linkedin_url = 'https://www.linkedin.com/in/ntuosto/' WHERE name = 'Nick Tuosto';
```

## Next Steps
1. Apply these SQL updates to the database
2. Continue verification for remaining contacts
3. Rebuild frontend to reflect updated URLs
