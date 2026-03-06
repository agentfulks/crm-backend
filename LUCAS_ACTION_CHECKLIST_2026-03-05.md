# LUCAS ACTION CHECKLIST — March 5, 2026
## Trello Outreach Loop | MATON_API_KEY Contingency

---

## RIGHT NOW (Choose One Path)

### Path A: Get MATON_API_KEY (5 minutes)
- [ ] Log into Maton dashboard
- [ ] Copy API key
- [ ] Paste into `.env` file: `MATON_API_KEY=your_key`
- [ ] Re-run import scripts

### Path B: Use Direct Trello API (5 minutes)
- [ ] Get TRELLO_API_KEY from https://trello.com/app-key
- [ ] Get TRELLO_TOKEN from same page
- [ ] Uncomment lines in `.env` file
- [ ] Run: `python scripts/import_bdr_batch_march4.py`

### Path C: Manual Mode (30 minutes)
- [ ] Open Trello boards in browser
- [ ] Copy-paste from files below into new cards

---

## TODAY (3-Hour Emergency Block)

### Hour 1: Clear Stale Approvals (45-60 min)
**Location:** VC Outreach Engine → Awaiting Approval  
**Target:** 16 cards (7+ days old)

For each card:
- [ ] Read card
- [ ] Approve → Move to "Approved/Send" OR
- [ ] Reject → Archive OR
- [ ] Needs work → Move to "Daily Queue" with notes

**Decision speed:** 2-3 minutes per card max

### Hour 2: Execute Approved Sends (30-45 min)
**Location:** VC Outreach Engine → Approved/Send  
**Target:** 41 cards ready to send

For each card:
- [ ] Copy message from card description
- [ ] Send via LinkedIn or email
- [ ] Move card to "Follow-up"
- [ ] Log send date

**Or:** Delegate this to assistant (all messages already written)

### Hour 3: BDR Batch Review (45-60 min)
**Location:** BDR Studios → Ready for Review  
**Target:** 25-30 cards (of 103 backlog)

Quick-review criteria (30 sec per card):
1. ICP score ≥ 3? → Yes = continue, No = archive
2. Contact valid? → Yes = continue, No = needs research
3. Signals relevant? → Yes = approve, No = skip

- [ ] Approve → Move to "Contact Research"
- [ ] Reject → Archive
- [ ] Needs work → Add comment, keep in queue

---

## IMPORT FILES READY TO USE

### VC Packets (5 cards)
**File:** `/data/workspace/output/trello-import-ready/VC_IMPORT_READY.md`

| Priority | Firm | Partner | Import To |
|----------|------|---------|-----------|
| P0 | a16z GAMES | Jonathan Lai | Daily Queue |
| P0 | Makers Fund | Michael Cheung | Daily Queue |
| P0 | Transcend Fund | Shanti Bergel | Daily Queue |
| P1 | Galaxy Interactive | Sam Englebardt | Daily Queue |
| P1 | Courtside Ventures | Deepen Parikh | Daily Queue |

**Action:** Copy-paste each into new Trello card

### BDR Studios (10 cards)
**File:** `/data/workspace/output/trello-import-ready/BDR_IMPORT_READY.md`
**File:** `/data/workspace/output/trello-import-ready/BDR_NEW_BATCH.md`

| Priority | Studio | CEO | Import To |
|----------|--------|-----|-----------|
| P0 | SayGames | Yegor Vaikhanski | Research Queue |
| P0 | Voodoo | Alexandre Yazdi | Research Queue |
| P0 | Azur Games | Dmitry Yaminsky | Research Queue |
| P0 | Dream Games | Soner Aydemir | Research Queue |
| P0 | Rollic | Burak Vardal | Research Queue |
| P1 | Homa Games | Daniel Nathan | Research Queue |
| P1 | CrazyLabs | Sagi Schliesser | Research Queue |
| P1 | Belka Games | Yury Mazanik | Research Queue |
| P1 | Boombit | Marcin Olejarz | Research Queue |
| P1 | Amanotes | Bill Vo | Research Queue |

**Action:** Copy-paste each into new Trello card

---

## THIS WEEK

### Implement Tiered Approval System
- [ ] Read: `deliverables/TIERED_APPROVAL_SYSTEM_DESIGN.md`
- [ ] Decide: Build internally or delegate?
- [ ] Schedule: 2 hours for implementation

**Impact:** Reduces daily approval time from 60 min → 10 min

### Establish Daily Habit
- [ ] Calendar block: 15 min every morning
- [ ] Target: Process 10-15 cards daily
- [ ] Rule: Never let queue exceed 20 cards

### Delegate Execution
- [ ] Identify: Who can send approved messages?
- [ ] Train: 30 min walkthrough of Approved/Send process
- [ ] Hand off: Lucas approves only, others execute sends

---

## BLOCKERS STATUS

| Blocker | Severity | Resolution |
|---------|----------|------------|
| MATON_API_KEY missing | MEDIUM | Get key OR use direct API OR manual mode |
| 132 cards awaiting approval | CRITICAL | 3-hour emergency block TODAY |
| 16 VC cards 7+ days stale | HIGH | Clear in Hour 1 of emergency block |
| 41 approved sends pending | HIGH | Execute in Hour 2 OR delegate |

---

## METRICS TO TRACK

| Metric | Current | Target | Check |
|--------|---------|--------|-------|
| Approval velocity | 0/day | 15/day | Daily |
| Backlog size | 132 | <20 | Daily |
| P1 cards stalled | 10 | 0 | Weekly |
| Daily approval time | 60+ min | 10 min | Weekly |

---

## QUESTIONS?

**Where are the import files?**
`/data/workspace/output/trello-import-ready/`

**How do I get Trello API credentials?**
https://trello.com/app-key

**What if I can't get MATON_API_KEY?**
Use Path B (Direct Trello API) or Path C (Manual). System works either way.

**How long will this take?**
- Emergency clear: 3 hours today
- Daily habit: 15 min/day ongoing
- Tiered system build: 2 hours this week

---

**Bottom line:** The API key is a minor inconvenience. The approval backlog is the real constraint. Spend your time on the cards, not the tooling.

---

*Generated: March 5, 2026 — 09:42 UTC*  
*Files ready: YES*  
*Action required: LUCAS*
