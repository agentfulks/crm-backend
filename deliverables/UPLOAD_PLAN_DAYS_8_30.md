# UPLOAD PLAN: DAYS 8-30 TRELLO IMPORT
**Date:** March 2, 2026  
**Status:** 115 Cards Ready for Upload (Days 8-30)  
**Target Board:** VC Outreach Engine

---

## INVENTORY SUMMARY

| Days | Count | Avg Fit Score | Status | Location |
|------|-------|---------------|--------|----------|
| Day 8 | 5 | 88.4 | Ready | `day8_vc_batch/` |
| Day 9 | 5 | 88.6 | Ready | `day9_vc_batch/` |
| Day 10 | 5 | 88.4 | Ready | `day10_vc_batch/` |
| Day 11 | 5 | 88.6 | Ready | `day11_vc_batch/` |
| Day 12 | 5 | 87.0 | Ready | `day12_vc_batch/` |
| Day 13 | 5 | 87.4 | Ready | `day13_vc_batch/` |
| Day 14 | 5 | 87.0 | Ready | `day14_vc_batch/` |
| Day 15 | 5 | 87.0 | Ready | `day15_vc_batch/` |
| Day 16 | 5 | — | Ready | `day16_vc_batch/` |
| Day 17 | 5 | — | Ready | `day17_vc_batch/` |
| Day 18 | 5 | — | Ready | `day18_vc_batch/` |
| Day 19 | 5 | — | Ready | `day19_vc_batch/` |
| Day 20 | 5 | — | Ready | `day20_vc_batch/` |
| Day 21 | 5 | — | Ready | `day21_vc_batch/` |
| Day 22 | 5 | — | Ready | `day22_vc_batch/` |
| Day 23 | 5 | — | Ready | `day23_vc_batch/` |
| Day 24 | 5 | — | Ready | `day24_vc_batch/` |
| Day 25 | 5 | — | Ready | `day25_vc_batch/` |
| Day 26 | 5 | — | Ready | `day26_vc_batch/` |
| Day 27 | 5 | — | Ready | `day27_vc_batch/` |
| Day 28 | 5 | — | Ready | `day28_vc_batch/` |
| Day 29 | 5 | — | Ready | `day29_vc_batch/` |
| Day 30 | 5 | — | Ready | `day30_vc_batch/` |
| **TOTAL** | **115** | **87.9** | **READY** | — |

---

## CSV IMPORT FORMAT

Each batch contains a `trello_import.csv` file with this structure:

```csv
Name,Description,List,Labels,Checklist
"[Day X] Fund Name - Partner Name","**Fund:** ...
**Partner:** ...
**Email:** ...
...","Daily Queue","Day X,Priority","Contact enriched,Email drafted,..."
```

**Columns:**
- **Name:** Card title with Day number, Fund, Partner
- **Description:** Full packet data (fund info, thesis, investments, fit rationale)
- **List:** Target Trello list ("Daily Queue")
- **Labels:** Day tag + Priority level
- **Checklist:** Pre-populated workflow checklist

---

## UPLOAD OPTIONS

### OPTION 1: CSV Import via Trello UI (Recommended)

**Requirements:** Trello Premium (for CSV import feature)

**Steps:**
1. Open Trello board: https://trello.com/b/tPkRdYjg/vc-outreach-engine
2. Click "..." on the "Daily Queue" list
3. Select "Import CSV"
4. Upload each day's `trello_import.csv` file
5. Verify card formatting

**Batch Order Recommendation:**
1. **First:** Days 8-11 (20 cards) — Gaming-native VCs, highest fit scores
2. **Second:** Days 16-21 (30 cards) — AI Infrastructure focus
3. **Third:** Days 12-15 (20 cards) — Gaming/AI mixed
4. **Fourth:** Days 22-26 (25 cards) — Enterprise AI
5. **Fifth:** Days 27-30 (20 cards) — Vertical AI/Cybersecurity

**Time Estimate:** 5 minutes per batch = ~2 hours total for all 115 cards

---

### OPTION 2: API Upload (Requires Credentials)

**Requirements:** `TRELLO_API_KEY` and `TRELLO_TOKEN`

**Script Available:**
```bash
# Set credentials
export TRELLO_API_KEY=your_key
export TRELLO_TOKEN=your_token

# Run bulk upload (if script available)
bash deliverables/BULK_UPLOAD_DAYS_8_15.sh
```

**Note:** API credentials are currently unavailable. Use Option 1 (CSV import) instead.

---

### OPTION 3: Manual Card Creation

**For each card, copy from:**
- `day{X}_vc_batch/summary.md` — Card description template
- `day{X}_vc_batch/emails/` — Email draft attachments
- `day{X}_vc_batch/packets.json` — Full structured data

**Time Estimate:** 3-5 minutes per card = 6-10 hours total (NOT RECOMMENDED)

---

## DETAILED BATCH BREAKDOWN

### Days 8-11: Gaming-Native VCs (High Priority)

| Day | Theme | Top Target | Score | Upload Priority |
|-----|-------|------------|-------|-----------------|
| 8 | Gaming-Native | Transcend Fund (Shanti Bergel) | 92 | **1st** |
| 9 | AI + Crypto Gaming | BITKRAFT (Carlos Pereira) | 94 | **1st** |
| 10 | Tier-1 Gaming | a16z Games (Andrew Chen) | 92 | **1st** |
| 11 | Global Specialists | Lightspeed Gaming (Moritz) | 92 | **1st** |

**Files:**
- `/data/workspace/deliverables/day8_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day9_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day10_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day11_vc_batch/trello_import.csv`

---

### Days 12-15: Mixed Thesis (Medium Priority)

| Day | Theme | Top Target | Score | Upload Priority |
|-----|-------|------------|-------|-----------------|
| 12 | AI-Native VCs | General Catalyst (Niko) | 90 | **3rd** |
| 13 | Gaming Seed | Riot Games (Bing Gordon) | 90 | **3rd** |
| 14 | Crypto Gaming | NFX (Gigi Levy-Weiss) | 90 | **3rd** |
| 15 | Regional Leaders | CloudTree (Michael O'Donnell) | 89 | **3rd** |

**Files:**
- `/data/workspace/deliverables/day12_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day13_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day14_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day15_vc_batch/trello_import.csv`

---

### Days 16-21: AI Infrastructure Focus (High Priority)

| Day | Theme | Upload Priority |
|-----|-------|-----------------|
| 16 | AI Infrastructure | **2nd** |
| 17 | AI Infrastructure | **2nd** |
| 18 | Enterprise AI | **2nd** |
| 19 | Enterprise AI | **2nd** |
| 20 | Vertical AI | **2nd** |
| 21 | Vertical AI | **2nd** |

**Files:**
- `/data/workspace/deliverables/day16_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day17_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day18_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day19_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day20_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day21_vc_batch/trello_import.csv`

---

### Days 22-26: Enterprise AI (Medium Priority)

| Day | Theme | Upload Priority |
|-----|-------|-----------------|
| 22 | AI/Enterprise | **4th** |
| 23 | Vertical AI | **4th** |
| 24 | Enterprise AI | **4th** |
| 25 | Enterprise AI | **4th** |
| 26 | Vertical AI | **4th** |

**Files:**
- `/data/workspace/deliverables/day22_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day23_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day24_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day25_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day26_vc_batch/trello_import.csv`

---

### Days 27-30: Vertical/Cybersecurity (Lower Priority)

| Day | Theme | Upload Priority |
|-----|-------|-----------------|
| 27 | Vertical AI | **5th** |
| 28 | AI Infrastructure | **5th** |
| 29 | Gaming VCs | **5th** |
| 30 | Cybersecurity AI | **5th** |

**Files:**
- `/data/workspace/deliverables/day27_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day28_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day29_vc_batch/trello_import.csv`
- `/data/workspace/deliverables/day30_vc_batch/trello_import.csv`

---

## CONSOLIDATED CSV FILES

For bulk upload, use these pre-consolidated files:

| File | Contents | Card Count |
|------|----------|------------|
| `trello_upload_days_22_24_consolidated.csv` | Days 22-24 | 15 |
| Individual `day{X}_vc_batch/trello_import.csv` | Per day | 5 each |

---

## UPLOAD EXECUTION PLAN

### Phase 1: Immediate (Today)

**Upload Days 8-11** (20 cards)
- Gaming-native VCs with highest fit scores
- Enables immediate execution once Day 1 resolved

**Files:**
- `day8_vc_batch/trello_import.csv`
- `day9_vc_batch/trello_import.csv`
- `day10_vc_batch/trello_import.csv`
- `day11_vc_batch/trello_import.csv`

### Phase 2: This Week

**Upload Days 16-21** (30 cards)
- AI Infrastructure focus
- Maintains daily 5-fund cadence

### Phase 3: Next Week

**Upload Days 12-15** (20 cards)
- Fill gaps in pipeline

### Phase 4: Following Week

**Upload Days 22-30** (45 cards)
- Complete backlog

---

## CARD STRUCTURE

Each uploaded card will contain:

**Title Format:**
```
[Day X] Fund Name - Partner Name
```

**Description Includes:**
- Fund name and AUM
- Partner name, title, email
- Check size and stage focus
- Geographic focus
- Fit score (0-100)
- Gaming/AI thesis summary
- Notable investments
- Fit rationale

**Labels:**
- Day tag (e.g., "Day 8")
- Priority (High/Medium/Low)

**Checklist:**
- [ ] Contact enriched
- [ ] Email drafted
- [ ] Packet attached
- [ ] Approved for send
- [ ] Sent
- [ ] Day 3 follow-up scheduled
- [ ] Day 7 follow-up scheduled

---

## CONTENT GAPS & ISSUES

### Identified Gaps

| Issue | Severity | Impact | Resolution |
|-------|----------|--------|------------|
| **Trello API credentials missing** | High | Blocks automated upload | Use CSV import (Option 1) |
| **Day 8-15 emails incomplete** | Medium | Some drafts need review | Check `emails/` subfolder per batch |
| **Day 16+ packet quality unverified** | Low | May need enrichment | Review before send |
| **Follow-up sequences not pre-loaded** | Low | Manual tracking required | Use checklist on each card |

### Recommended Actions

1. **Immediate:** Upload Days 8-11 via CSV import
2. **This week:** Verify email drafts for Days 12-15
3. **Ongoing:** Review packet quality for Days 16+ before send

---

## SUCCESS METRICS

**Upload Completion:**
- [ ] Days 8-11 uploaded (20 cards)
- [ ] Days 12-15 uploaded (20 cards)
- [ ] Days 16-21 uploaded (30 cards)
- [ ] Days 22-26 uploaded (25 cards)
- [ ] Days 27-30 uploaded (20 cards)

**Quality Check:**
- [ ] All cards have verified partner emails
- [ ] All cards have personalized email drafts
- [ ] All cards have pitch deck attached
- [ ] All cards have KPI snapshot attached

---

## TRELLO BOARD WORKFLOW

Once uploaded, cards flow through these lists:

```
Daily Queue → To Approve → Approved → Sent → Follow-up → Complete
     ↑                                                           ↓
     └────────────────── New batches ────────────────────────────┘
```

**Daily Queue:** Cards ready for review (starting position)
**To Approve:** Cards moved for Lucas review
**Approved:** Green-lit for sending
**Sent:** Email sent, waiting for response
**Follow-up:** Day 3/7/14 follow-ups scheduled
**Complete:** Response received or loop closed

---

## FILE REFERENCE MAP

```
/data/workspace/deliverables/
├── day8_vc_batch/trello_import.csv       # Days 8-11: Gaming-native
├── day9_vc_batch/trello_import.csv
├── day10_vc_batch/trello_import.csv
├── day11_vc_batch/trello_import.csv
├── day12_vc_batch/trello_import.csv      # Days 12-15: Mixed thesis
├── day13_vc_batch/trello_import.csv
├── day14_vc_batch/trello_import.csv
├── day15_vc_batch/trello_import.csv
├── day16_vc_batch/trello_import.csv      # Days 16-21: AI Infrastructure
├── day17_vc_batch/trello_import.csv
├── day18_vc_batch/trello_import.csv
├── day19_vc_batch/trello_import.csv
├── day20_vc_batch/trello_import.csv
├── day21_vc_batch/trello_import.csv
├── day22_vc_batch/trello_import.csv      # Days 22-26: Enterprise AI
├── day23_vc_batch/trello_import.csv
├── day24_vc_batch/trello_import.csv
├── day25_vc_batch/trello_import.csv
├── day26_vc_batch/trello_import.csv
├── day27_vc_batch/trello_import.csv      # Days 27-30: Vertical/Cyber
├── day28_vc_batch/trello_import.csv
├── day29_vc_batch/trello_import.csv
└── day30_vc_batch/trello_import.csv
```

---

## NEXT STEPS

1. **Resolve Day 1** (see `DECISION_MEMO_DAY1.md`)
2. **Upload Days 8-11** via CSV import (highest priority)
3. **Verify email drafts** for Days 12-15
4. **Continue daily cadence** once pipeline flowing
5. **Upload remaining batches** in priority order

---

*Upload plan prepared by BDR-OUTREACH Specialist Agent*  
*Ready for execution*
