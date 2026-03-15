# LinkedIn URL Verification Report - March 6, 2026

## BDR Contacts Summary

**Total BDR Contacts: 147**

| Status | Count | Percentage |
|--------|-------|------------|
| Verified URLs | 134 | 91.2% |
| Unverified URLs | 12 | 8.2% |
| No URL (Invalid/404) | 1 | 0.7% |

### Recently Corrected URLs (7 contacts)

| Name | Company | Previous URL | Corrected URL |
|------|---------|--------------|---------------|
| John Hanke | Niantic | linkedin.com/in/john-hanke-6a896 | www.linkedin.com/in/john-hanke-6a896/ |
| Andy Zhong | FunPlus | cn.linkedin.com/in/andy-zhong | cn.linkedin.com/in/andyzhonginvestor |
| Ben Brode | Second Dinner | linkedin.com/in/ben-brode | linkedin.com/in/benbrode/ |
| Julia Humphreys | Second Dinner | linkedin.com/in/julia-humphreys | linkedin.com/in/julia-humphreys-7013321/ |
| Simon Hade | Space Ape Games | linkedin.com/in/simon-hade | uk.linkedin.com/in/simonhade |
| Thomas Dubreuil | Homa Games | linkedin.com/in/thomas-dubreuil | linkedin.com/in/thomasdubreuil/ |
| Teppo Soininen | Metacore Games | linkedin.com/in/teppo-soininen | fi.linkedin.com/in/tepposoininen |

### Unverified Contacts (12 contacts - need verification)

These contacts have URLs that could not be verified through web search:

| Name | Company | Current URL | Issue |
|------|---------|-------------|-------|
| Dmitriy Shelengovskiy | Playgendary | linkedin.com/in/dmitriy-shelengovskiy | Not found in search |
| Mikael Le Goff | Dual Cat | linkedin.com/in/legoffmikael | Wrong person (Dalkia energy company) |
| Marc Sutter | Ketchapp | linkedin.com/in/marc-sutter | Not found at Ketchapp |
| Anton Karpov | Colossi Games | linkedin.com/in/antonkarpov | Not found |
| Denis Puhalski | Colossi Games | linkedin.com/in/denis-puhalski | Not found |
| Vladimir Chirin | Colossi Games | linkedin.com/in/vladimir-chirin | Not found |
| Søren Krogh | Tactile Games | linkedin.com/in/soren-krogh | Not found |
| Markus Halonen | Metacore Games | linkedin.com/in/markus-halonen | Not found |
| Can Karter | Ruby Games | linkedin.com/in/can-karter | Not found |
| Mert Karter | Ruby Games | linkedin.com/in/mert-karter | Not found |
| Onur Karter | Ruby Games | linkedin.com/in/onur-karter | Not found |
| Joe Rulli | Space Ape Games | linkedin.com/in/joe-rulli | Not found |

### Invalid/404 Contacts (1 contact)

| Name | Company | Status |
|------|---------|--------|
| Egor Kozlov | Belka Games | NOT A FOUNDER - Profile returns 404. Real founders are Yury Mazanik and Dzmitry Khusainau (both verified in DB). |

## VC Contacts Summary

**Total VC Contacts: 55**

| Status | Count | Percentage |
|--------|-------|------------|
| Has URL | 8 | 14.5% |
| No URL | 47 | 85.5% |

### Verified VC Contacts (8 contacts)

| Name | Fund | LinkedIn URL |
|------|------|--------------|
| Jens Hilgers | BITKRAFT Ventures | de.linkedin.com/in/jenshilgers |
| Josh Chapman | Konvoy Ventures | linkedin.com/in/joshchapmanb/ |
| Steve Cho | Mechanism Capital | linkedin.com/in/stevencho/ |
| Jesse Walden | Variant | linkedin.com/in/jessewalden/ |
| Li Jin | Variant | linkedin.com/in/ljin1/ |
| Chris Dixon | a16z crypto | linkedin.com/in/chris-dixon-9599b127b/ |
| Stephen McKeon | Collab+Currency | linkedin.com/in/smckeon |
| Nick Tuosto | Griffin Gaming Partners | linkedin.com/in/ntuosto/ |

### Missing VC LinkedIn URLs (47 contacts need URLs)

All major VC funds have contacts without LinkedIn URLs:
- a16z crypto: 6 contacts
- BITKRAFT Ventures: 6 contacts
- Collab+Currency: 5 contacts
- Griffin Gaming Partners: 4 contacts
- Konvoy Ventures: 7 contacts
- Maven 11 Capital: 5 contacts
- Mechanism Capital: 5 contacts
- Not Boring Capital: 4 contacts
- Paradigm: 5 contacts
- Variant: 4 contacts

## Recommendations

### Immediate Actions
1. **Unverified BDR contacts**: Manually verify the 12 unverified contacts by checking company websites or reaching out directly
2. **Invalid contact**: Egor Kozlov has been marked as invalid - the real Belka Games founders (Yury Mazanik, Dzmitry Khusainau) are already in the database with verified URLs

### VC Contacts
1. All 47 VC contacts without LinkedIn URLs need to be researched
2. Use the same verification process: Search "[Name] [Fund] LinkedIn" and verify the profile matches

### Ongoing Process
1. Add LinkedIn verification as a mandatory step for all new contacts
2. Flag URLs that return 404 as invalid
3. Update URLs when contacts change companies

## SQL Updates Applied

```sql
-- Sample of corrections applied
UPDATE bdr_contacts SET linkedin_url = 'https://www.linkedin.com/in/john-hanke-6a896/' WHERE full_name = 'John Hanke';
UPDATE bdr_contacts SET linkedin_url = 'https://cn.linkedin.com/in/andyzhonginvestor' WHERE full_name = 'Andy Zhong';
-- ... (7 total corrections)

-- Mark unverified contacts
UPDATE bdr_contacts SET notes = 'UNVERIFIED: LinkedIn URL could not be verified via search' WHERE full_name IN (...);
```
