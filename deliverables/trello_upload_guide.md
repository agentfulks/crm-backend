# Trello Upload Guide - BDR Outreach

## Current Backlog Status

**Last Updated:** 2026-03-02 UTC

### Overview
- **Total Batches Ready:** 12
- **Total Cards Waiting:** ~608 investor packets
- **Batches Missing CSV:** 18 days (Days 3-6, 10-18, 23-26)
- **Existing Trello Cards Stuck:** 5 Day 1 packets (6 days overdue in Daily Queue)

---

## Ready-to-Upload Batches

| Day | Batch Name | Cards | Status |
|-----|------------|-------|--------|
| 7 | day7_vc_batch | 121 | Ready |
| 8 | day8_vc_batch | 99 | Ready |
| 9 | day9_vc_batch | 5 | Ready |
| 19 | day19_vc_batch | 136 | Ready |
| 20 | day20_vc_batch | 6 | Ready |
| 21 | day21_vc_batch | 5 | Ready |
| 22 | day22_vc_batch | 81 | Ready |
| 27 | day27_vc_batch | 86 | Ready |
| 28 | day28_vc_batch | 6 | Ready |
| 29 | day29_vc_batch | 6 | Ready |
| 30 | day30_vc_batch | 6 | Ready |
| 31 | day31_vc_batch | 51 | Ready |
| **TOTAL** | | **608** | |

### Missing CSV Batches (Need Generation)
- Days 3, 4, 5, 6
- Days 10, 11, 12, 13, 14, 15, 16, 17, 18
- Days 23, 24, 25, 26

---

## Method 1: Automated Upload (Recommended)

### Prerequisites
1. Trello API credentials
2. Python 3 installed
3. Environment variables configured

### Step 1: Get Trello API Credentials

1. Visit: https://trello.com/app-key
2. Copy your API Key
3. Click "Token" link to generate a token
4. Save both values securely

### Step 2: Set Environment Variables

```bash
export TRELLO_API_KEY='your_api_key_here'
export TRELLO_TOKEN='your_token_here'
```

### Step 3: Run Upload Script

Navigate to workspace and run:

```bash
cd /data/workspace

# List available batches
python3 scripts/trello_bulk_upload.py --list

# Preview upload (dry run)
python3 scripts/trello_bulk_upload.py --day 7 --dry-run

# Upload specific day
python3 scripts/trello_bulk_upload.py --day 7

# Upload multiple days
python3 scripts/trello_bulk_upload.py --day 7,8,9

# Upload all available batches
python3 scripts/trello_bulk_upload.py --all

# Upload to specific list (default: Daily Queue)
python3 scripts/trello_bulk_upload.py --day 7 --list-id YOUR_LIST_ID
```

### Upload Options

| Option | Description |
|--------|-------------|
| `--list` | Show all available batches |
| `--day N` | Upload specific day(s), comma-separated |
| `--all` | Upload all ready batches |
| `--dry-run` | Preview without uploading |
| `--delay N` | Seconds between API calls (default: 1) |
| `--list-id ID` | Target Trello list ID |
| `--board-id ID` | Target Trello board ID |

---

## Method 2: Manual CSV Import via Trello UI

### For Small Batches (1-50 cards)

1. Open Trello board: **VC Outreach Engine**
2. Navigate to list: **Daily Queue** (or create new list)
3. Click the list menu (three dots) → **Import CSV**
4. Select CSV file from `/data/workspace/deliverables/day*/trello_import.csv`
5. Map fields:
   - Name → Card Name
   - Description → Description
   - Labels → Labels (optional)
   - List → List (optional)
6. Click **Import**

### CSV File Locations

```
/data/workspace/deliverables/
├── day7_vc_batch/trello_import.csv   (121 cards)
├── day8_vc_batch/trello_import.csv   (99 cards)
├── day9_vc_batch/trello_import.csv   (5 cards)
├── day19_vc_batch/trello_import.csv  (136 cards)
├── day20_vc_batch/trello_import.csv  (6 cards)
├── day21_vc_batch/trello_import.csv  (5 cards)
├── day22_vc_batch/trello_import.csv  (81 cards)
├── day27_vc_batch/trello_import.csv  (86 cards)
├── day28_vc_batch/trello_import.csv  (6 cards)
├── day29_vc_batch/trello_import.csv  (6 cards)
├── day30_vc_batch/trello_import.csv  (6 cards)
└── day31_vc_batch/trello_import.csv  (51 cards)
```

---

## Method 3: Card-by-Card Manual Creation

### For Individual Investors

If you need to add individual investor packets manually:

1. Click **Add a card** in the Daily Queue list
2. **Card Name Format:** `Day X | Fund Name | Contact Name`
   - Example: `Day 7 | 359 Capital | Michael Spirito`
3. **Description Template:**

```markdown
**FUND OVERVIEW**
Fund: [FUND NAME]
AUM: $[AMOUNT]
Stage: [STAGES]
Check Size: $[MIN] - $[MAX]
Geographic Focus: [REGIONS]

**PARTNER DETAILS**
Name: [CONTACT NAME]
Title: [TITLE]
Email: [EMAIL]

**GAMING/AI THESIS**
[THESIS DESCRIPTION]

**FIT SCORE:** [SCORE]/100

**NOTABLE INVESTMENTS**
- [Investment 1]
- [Investment 2]
```

4. Add labels (optional):
   - `vc-fund` for venture capital firms
   - `angel` for angel investors
   - `strategic` for strategic investors
   - `priority` for high-fit targets

---

## Target Board Configuration

### Default Board
- **Board Name:** VC Outreach Engine
- **Board ID:** `699d2728fd2ae8c35d1f7a44`
- **Default List:** Daily Queue
- **List ID:** `699d309c1870f04a4b401759`

### List Structure
1. **Daily Queue** → New cards arrive here
2. **Awaiting Approval** → Cards ready for Lucas review
3. **Approved** → Approved for outreach
4. **In Progress** → Active outreach
5. **Contacted** → Initial contact made
6. **Responded** → Received response
7. **Meeting Scheduled** → Call/meeting booked
8. **Passed** → Not a fit
9. **Complete** → Process complete

---

## Recommended Upload Strategy

### Phase 1: Clear Backlog (Priority)
1. Upload Days 7-9 (225 cards)
2. Upload Days 19-22 (228 cards)
3. Process existing 5 Day 1 cards using `trello_workflow.py`

### Phase 2: Continue Pipeline
1. Upload Days 27-31 (155 cards)
2. Generate missing CSVs for Days 3-6, 10-18, 23-26

### Rate Limiting
- Trello API limit: 300 requests per 10 seconds
- Script default: 1 second delay between cards
- Recommended: Process max 100 cards per batch to avoid rate limits

---

## Troubleshooting

### "Authentication Failed" Error
- Verify `TRELLO_API_KEY` and `TRELLO_TOKEN` are set correctly
- Check token hasn't expired (tokens are valid until manually revoked)
- Ensure no extra whitespace in environment variables

### "List Not Found" Error
- Verify the list ID is correct
- Check you have access to the board
- Use `--list-id` to specify correct target

### Rate Limiting
- Increase delay: `--delay 2` or `--delay 3`
- Process smaller batches: `--day 7` instead of `--all`

### CSV Parse Errors
- Check CSV file encoding (should be UTF-8)
- Verify no special characters breaking format
- View sample: `head -5 /path/to/trello_import.csv`

---

## Existing Stuck Cards

**5 cards in Daily Queue (6 days overdue):**

| Card | Fund | Contact | Status |
|------|------|---------|--------|
| Packet: BITKRAFT Ventures | BITKRAFT | Martin Garcia | Needs enrichment |
| Packet: Variant | Variant | Spencer Noon | Needs enrichment |
| Packet: Collab+Currency | Collab+Currency | Derek Edwards | Needs enrichment |
| Packet: Konvoy Ventures | Konvoy | Taylor Hurst | Needs enrichment |
| Packet: Mechanism Capital | Mechanism | Steve Cho | Needs enrichment |

**To process these cards:**
```bash
export TRELLO_API_KEY='your_key'
export TRELLO_TOKEN='your_token'
python3 /data/workspace/trello_workflow.py
```

This will:
1. Add enriched contact data to descriptions
2. Move cards to Awaiting Approval list
3. Add status comments

---

## Quick Reference

### One-Liner Upload
```bash
cd /data/workspace && export TRELLO_API_KEY='xxx' && export TRELLO_TOKEN='yyy' && python3 scripts/trello_bulk_upload.py --day 7
```

### Check What's Ready
```bash
ls /data/workspace/deliverables/*/trello_import.csv | wc -l
```

### Count Cards Per Batch
```bash
for f in /data/workspace/deliverables/*/trello_import.csv; do echo "$f: $(wc -l < $f) cards"; done
```

---

## Next Actions

1. [ ] Obtain Trello API credentials
2. [ ] Run `--list` to verify batches
3. [ ] Process 5 stuck Day 1 cards
4. [ ] Upload Day 7-9 batches (225 cards)
5. [ ] Review and approve uploaded cards
6. [ ] Continue with Days 19-22
7. [ ] Generate missing CSVs for remaining days

---

*Generated by: BDR-OUTREACH AGENT*
*Script location: `/data/workspace/scripts/trello_bulk_upload.py`*
