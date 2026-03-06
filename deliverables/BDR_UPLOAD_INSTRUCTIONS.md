# BDR UPLOAD INSTRUCTIONS
## Game Studios Trello Import — Tier 1 Batch (30 Studios)
**Date:** March 3, 2026  
**Objective:** Upload 30 Tier-1 game studios to Trello board  
**Time Required:** 10-15 minutes  
**File:** `trello_import_batch_a.csv`

---

## PRE-UPLOAD CHECKLIST

- [ ] File verified: `/data/workspace/deliverables/bdr_game_studios/trello_import_batch_a.csv`
- [ ] File size: ~17KB (289 lines)
- [ ] Contains 30 studios with complete data
- [ ] Trello board access confirmed
- [ ] Target list identified: "Research Queue" or "To Do"

---

## UPLOAD METHODS

### METHOD A: Trello CSV Import (Recommended)

**Step 1: Prepare the Import**
1. Open Trello board
2. Navigate to target list (e.g., "Research Queue")
3. Click **... (More)** → **Import** → **CSV**

**Step 2: Upload File**
1. Click **Select CSV File**
2. Navigate to: `/data/workspace/deliverables/bdr_game_studios/`
3. Select: `trello_import_batch_a.csv`
4. Click **Open**

**Step 3: Map Fields**
| CSV Column | Trello Field | Status |
|------------|--------------|--------|
| Name | Card Name | ✓ Auto-mapped |
| Description | Description | ✓ Auto-mapped |
| Labels | Labels | ✓ Auto-mapped ("Tier-1") |
| Due Date | Due Date | ✓ Auto-mapped (2026-03-05 to 2026-03-10) |

**Step 4: Confirm Import**
1. Review preview (first 3 cards)
2. Click **Import**
3. Wait for completion (30-60 seconds)
4. Verify: 30 new cards created

---

### METHOD B: Manual Card Creation (Fallback)

If CSV import fails, use this template per card:

1. Click **Add a card** in target list
2. Paste format:
   ```
   [Studio Name]
   
   Location: [City, Country]
   Employees: [Count]
   Downloads: [Count]
   Focus: [Category]
   
   Primary Contact: [Name] | [Title] | [Email]
   
   Outreach Angle: [2-3 sentences]
   
   Key Contacts:
   - [Name] | [Title] | [Email]
   - [Name] | [Title] | [Email]
   ```
3. Add label: **Tier-1** (green)
4. Set due date: As specified in CSV
5. Repeat for all 30 studios

---

## POST-UPLOAD VERIFICATION

**Immediate Checks:**
- [ ] 30 new cards appear in target list
- [ ] All cards have "Tier-1" label (green)
- [ ] Due dates staggered: March 5-10, 2026
- [ ] Description field populated with full research

**Sample Verification (Check 3 random cards):**
1. Open card → Verify contact email present
2. Check description includes outreach angle
3. Confirm label = "Tier-1"

---

## STUDIO LIST (30 Tier-1 Studios)

| # | Studio | Location | Downloads | Due Date |
|---|--------|----------|-----------|----------|
| 1 | Voodoo | Paris, France | 7B+ | 2026-03-05 |
| 2 | Homa Games | Paris, France | 500M+ | 2026-03-05 |
| 3 | SayGames | Cyprus/Poland | 7B+ | 2026-03-05 |
| 4 | Supersonic Studios | Israel/SF | — | 2026-03-05 |
| 5 | Rollic (Zynga) | Istanbul | 250M+ MAU | 2026-03-05 |
| 6 | Kwalee | UK | 1B+ | 2026-03-05 |
| 7 | CrazyLabs | Tel Aviv | 7B+ | 2026-03-06 |
| 8 | Lion Studios | SF/Berlin/Shanghai | 2B+ | 2026-03-06 |
| 9 | Boombit | Poland | — | 2026-03-06 |
| 10 | Amanotes | Vietnam/Global | 2.5B+ | 2026-03-06 |
| 11 | Scopely | LA/Barcelona/Seoul | — | 2026-03-06 |
| 12 | Gismart | London | 1B+ | 2026-03-07 |
| 13 | TapNation | Paris | 1B+ | 2026-03-07 |
| 14 | Supercent | Seoul | 500M+ | 2026-03-07 |
| 15 | MAG Interactive | Stockholm | 300M+ | 2026-03-07 |
| 16 | Moonee | Tel Aviv | 500M+ | 2026-03-07 |
| 17 | Playrix | Dublin | — | 2026-03-08 |
| 18 | Ketchapp (Ubisoft) | Paris | — | 2026-03-08 |
| 19 | Gram Games | Istanbul/London | — | 2026-03-08 |
| 20 | Belka Games | Lithuania/Cyprus | 500M+ | 2026-03-08 |
| 21 | Alictus (SciPlay) | Turkey | — | 2026-03-09 |
| 22 | Ruby Games (Rovio) | Izmir | 500M+ | 2026-03-09 |
| 23 | N3TWORK Studios | SF (Remote) | — | 2026-03-09 |
| 24 | Tripledot Studios | London | — | 2026-03-09 |
| 25 | PeopleFun | Dallas | — | 2026-03-09 |
| 26 | iKame Games | Hanoi | 500M+ | 2026-03-10 |
| 27 | Bravestars Games | Hanoi | 1B+ | 2026-03-10 |
| 28 | Wildlife Studios | Brazil/CA | 3B+ | 2026-03-10 |
| 29 | Nexters (GDEV) | Cyprus | 500M+ | 2026-03-10 |
| 30 | Fingersoft | Finland | 1B+ | 2026-03-10 |

**Total Downloads Represented:** 50B+

---

## ALIGNMENT CHECK: Outreach Drafts

**Cross-Reference Verification:**

The outreach drafts in `outreach_drafts_batch_1.md` correspond 1:1 with this CSV:

| CSV Rank | Studio | Draft # | Contact Match |
|----------|--------|---------|---------------|
| 1 | Voodoo | 1 | Alexandre Yazdi ✓ |
| 2 | Homa Games | 2 | Daniel Nathan ✓ |
| 3 | SayGames | 3 | Yegor Vaikhanski ✓ |
| 4 | Supersonic | 4 | Nadav Ashkenazy ✓ |
| 5 | Rollic | 5 | Burak Vardal ✓ |
| 6 | Kwalee | 6 | David Darling ✓ |
| 7 | CrazyLabs | 7 | Sagi Schliesser ✓ |
| 8 | Lion Studios | 8 | Gilberto Marcal ✓ |
| ... | ... | ... | ... |
| 30 | Fingersoft | 30 | Teemu Närhi ✓ |

**All 30 studios have pre-drafted outreach messages ready for use.**

---

## NEXT BATCHES (Ready for Future Upload)

| Batch | File | Studios | Status |
|-------|------|---------|--------|
| Batch A | `trello_import_batch_a.csv` | 30 | **Ready now** |
| Batch B | `trello_import_batch_b.csv` | 30 | Ready |
| Batch C | `trello_import_batch_c.csv` | 41 | Ready |

**Total Pipeline:** 101 studios across 3 batches

---

## POST-UPLOAD WORKFLOW

After upload, cards flow through this pipeline:

```
Research Queue → Active → In Review → Awaiting Approval → Approved/Send → Complete
```

**Your Role:**
1. **Today:** Upload Batch A (this task)
2. **Ongoing:** Cards move through workflow per LUCAS_DAILY_CHECKLIST.md
3. **This Week:** Upload Batch B when Research Queue clears

---

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| CSV import fails | Check file encoding (UTF-8). Try Method B. |
| Duplicate cards | Check if batch already imported. Delete duplicates. |
| Labels not applied | Manually add "Tier-1" label to uploaded cards. |
| Due dates wrong | Bulk edit due dates in Trello after import. |
| Missing contact info | Reference `all_contacts_101_studios.md` for backup data. |

---

## SUCCESS CRITERIA

- [ ] 30 cards uploaded to Trello
- [ ] All cards have "Tier-1" label
- [ ] Due dates set (March 5-10)
- [ ] Descriptions complete with contact info
- [ ] Time elapsed: 10-15 minutes

---

## NEXT STEPS AFTER UPLOAD

1. **Immediate:** Verify upload success (5 min)
2. **Today:** Reference `outreach_drafts_batch_1.md` for messaging
3. **This Week:** Schedule upload of Batch B (30 studios)
4. **Ongoing:** Process cards per daily checklist

---

**Execute now. 30 Tier-1 studios will be in your pipeline within 15 minutes.**

*Document Version: 1.0*  
*Created: March 3, 2026*  
*Batch A: 30 studios, 50B+ downloads represented*
