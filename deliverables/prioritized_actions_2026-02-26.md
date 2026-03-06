# PRIORITIZED ACTIONS — Lucas Attention Required
**Date:** 2026-02-26 17:03 UTC  
**Source:** Trello Board Coordination Subagent  
**Files:** `board_state_2026-02-26.md` | `decision_memo_day1_2026-02-26.md`

---

## ATTENTION RANKING

| Priority | Item | Urgency | Time Required | Action |
|----------|------|---------|---------------|--------|
| **P0** | Day 1 Execution Decision | 48h overdue | 1 min (decide) | **Read decision memo, select Option A/B/C** |
| **P1** | Trello API Credentials | Blocking automation | 5 min | **Provide TRELLO_API_KEY + TOKEN** |
| **P2** | Send Day 1 Packets (if Option A) | Blocks follow-ups | 25 min | **Execute 5 sends from manual_execution_bridge/** |
| **P3** | Day 3 Trello Card Creation | Day 3 batch ready | 10 min | **Approve batch for card creation** |
| **P4** | Postgres DB Decision | Backend incomplete | 5 min | **Provision DB or deprioritize** |

---

## P0 — DECISION REQUIRED NOW

### Day 1 Execution: Choose Option A, B, or C

**Context:** 5 investor packets (BITKRAFT, Konvoy, Mechanism, Collab+Currency, Variant) ready to send. 48 hours overdue. Blocking follow-up sequence.

**Options:**
- **Option A:** Execute now (25 min), push follow-ups to Mar 2 — **RECOMMENDED**
- **Option B:** Skip Day 1, consolidate all 15 — Wastes prepared work
- **Option C:** Defer all follow-ups proportionally — Extended timeline

**Full analysis:** `/data/workspace/deliverables/decision_memo_day1_2026-02-26.md`

**What to do:**
1. Read the decision memo (2 minutes)
2. Reply with: "Option A", "Option B", or "Option C"
3. If Option A: indicate send timing (today vs tomorrow morning)

---

## P1 — UNBLOCK AUTOMATION

### Trello API Credentials

**Why it matters:** Cannot automate card moves, status updates, or workflow tracking without API access.

**What I need:**
```
TRELLO_API_KEY=your_key_here
TRELLO_TOKEN=your_token_here
TRELLO_BOARD_ID=your_board_id_here
```

**How to get:**
1. Visit: https://trello.com/app-key
2. Copy API Key
3. Click "Token" link, authorize, copy Token
4. Board ID: in Trello URL — `https://trello.com/b/[BOARD_ID]/board-name`

**Impact with credentials:**
- Auto-create cards for Day 3 batch
- Auto-move cards through lists (To Do → Active → Complete)
- Real-time board state updates
- No more manual CSV imports

---

## P2 — EXECUTION (IF OPTION A SELECTED)

### Send 5 Day 1 Packets

**Location:** `/data/workspace/deliverables/manual_execution_bridge/`

**Pre-flight checklist:**
- [ ] Fill `[Calendly link]` in all 5 email files
- [ ] Fill `[Your title]` placeholder
- [ ] Fill `[Company name]` placeholder
- [ ] Verify pitch deck exists: `outreach_assets/pitch_deck/latest.pdf`
- [ ] Verify KPI snapshot exists: `outreach_assets/kpi_snapshot/2026-02-24-kpis.csv`

**Send order (by priority score):**
1. **P1 BITKRAFT** (84.0) → martin@bitkraft.vc
2. **P2 Konvoy** (59.33) → taylor@konvoy.vc
3. **P3 Mechanism** (53.33) → steve@mechanism.capital
4. **P4 Collab+Currency** (51.33) → derek@collabcurrency.com
5. **P5 Variant** (48.33) → spencer@variant.fund

**Post-send:**
- Update `sent_log_planned.csv` with timestamps
- Set follow-up reminders: Mar 2 (Day 3), Mar 6 (Day 7)

**Guide:** `EXECUTION_CHECKLIST.md` (step-by-step)

---

## P3 — APPROVE DAY 3 BATCH

### Create Trello Cards for 5 New Funds

**Funds ready:**
| Fund | Contact | Score |
|------|---------|-------|
| Play Ventures | Henric Suuronen | 82.0 |
| GFR Fund | Yasushi Komori | 78.0 |
| Makers Fund | Michael Cheung | 80.0 |
| London Venture Partners | David Lau-Kee | 76.0 |
| Hiro Capital | Luke Alvarez | 74.0 |

**Location:** `/data/workspace/deliverables/day3_vc_batch/`

**Status:** Files ready, manifest prepared (`batch_manifest.json`)

**What I need:** Approval to create Trello cards (or API credentials to auto-create)

---

## P4 — INFRA DECISION

### Postgres CRM: Provision or Deprioritize

**Current state:**
- Schema defined in `backend/prisma/schema.prisma`
- Migrations ready but cannot run (no DB)
- Blocking: Full test suite, CRM logging automation

**Options:**
1. **Provision DB:** Neon, Supabase, or local Postgres → complete backend
2. **Deprioritize:** Continue with file-based tracking (current approach)
3. **Hybrid:** Use Airtable/Notion as interim CRM (requires Maton connection)

**Recommendation:** If fundraising is primary goal, deprioritize Postgres. File-based tracking works for 15-50 investor conversations. Upgrade when pipeline exceeds 100 contacts.

---

## WHAT YOU CAN DELEGATE

**I can handle immediately (no input needed):**
- Create Trello cards for Day 3 batch (once approved or credentials provided)
- Update follow-up templates with any traction metrics you provide
- Generate additional research packets (Day 4, Day 5 batches)
- Monitor board state and report changes

**I need your input for:**
- Day 1 execution decision (Option A/B/C)
- Placeholder values (Calendly link, title, company name)
- API credentials for automation
- DB provisioning (or confirmation to deprioritize)

---

## SUGGESTED RESPONSE FORMAT

Reply with:

```
DECISION: Option [A/B/C]
SEND TIMING: [Today/Tomorrow morning]
API CREDS: [Provided below/Will provide later/Not needed]
DAY 3 BATCH: [Approve for card creation/Wait for Day 1 decision]
POSTGRES: [Provision/Deprioritize]

[If Option A selected, include:]
CALENDLY LINK: https://...
TITLE: [Founder/CEO/Your title]
COMPANY NAME: [Your company]
```

---

## SUMMARY

**What needs your attention first:**

1. **P0 (1 min):** Read decision memo, pick Option A/B/C
2. **P1 (5 min):** Provide Trello API credentials (unblocks automation)
3. **P2 (25 min):** Execute 5 Day 1 sends (if Option A)

**Total time to unblock:** 31 minutes  
**Default action:** If no response by Feb 27 12:00 UTC, recommend proceeding with Option A

---

*Prioritized action list generated by VANTAGE subagent.*
