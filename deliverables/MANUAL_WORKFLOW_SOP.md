# MANUAL WORKFLOW SOP
## VC Outreach Engine — Manual Execution Guide
**Version:** 1.0  
**Date:** March 2, 2026  
**Status:** NO API AUTOMATION REQUIRED

---

## 1. EXECUTIVE SUMMARY

This SOP provides the exact manual steps to execute the VC outreach workflow without Trello API automation. Lucas can execute this independently using the Trello web interface.

**Current Board State (March 2):**
| List | Count | Action Required |
|------|-------|-----------------|
| Daily Queue | 7 | 5 Day 1 cards (stale) + 2 system cards |
| Awaiting Approval | 3 | Review + move or archive |
| Approved / Send | 1 | Ready to execute |
| Follow-up | 1 | Process Friday |

**Time Investment:** 45-60 minutes/day for full execution

---

## 2. WORKFLOW OVERVIEW

```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────┐    ┌─────────────┐
│  Daily Queue    │ →  │ Awaiting Approval│ →  │ Approved/Send │ →  │  Follow-up  │
│  (New/Backlog)  │    │  (Review)        │    │  (Execute)    │    │  (Nurture)  │
└─────────────────┘    └──────────────────┘    └───────────────┘    └─────────────┘
       ↑                                                    │
       └────────────────────── (Loop) ──────────────────────┘
```

---

## 3. STEP-BY-STEP MANUAL PROCESS

### PHASE 1: MORNING REVIEW (15 minutes)

**Step 1.1: Open Trello Board**
- URL: https://trello.com/b/tPkRdYjg/vc-outreach-engine
- Review each list from left to right

**Step 1.2: Assess Daily Queue**
- Count cards needing action
- Identify stale cards (due date passed)
- Prioritize by fit score (highest first)

**Step 1.3: Check Follow-up List**
- Identify cards due for follow-up today
- Note any replies received

---

### PHASE 2: CARD MOVEMENT — Daily Queue → Awaiting Approval (10 minutes)

**For each card in Daily Queue:**

1. **Open card** (click to expand)
2. **Review checklist items:**
   - [ ] Deck link verified
   - [ ] Partner email confirmed
   - [ ] Hook customized
   - [ ] Fit score validated
3. **If ready for review:**
   - Click "Move" (right sidebar)
   - Select "Awaiting Approval" list
   - Add comment: `Reviewed [DATE] — ready for approval`
4. **If NOT ready:**
   - Add comment with blocker
   - Update due date +2 days
   - Leave in Daily Queue

**Batch Size:** Move 3-5 cards per session max

---

### PHASE 3: APPROVAL DECISION — Awaiting Approval → Approved/Send (10 minutes)

**For each card in Awaiting Approval:**

1. **Open card**
2. **Review email draft:**
   - Check deliverables folder: `day{X}_vc_batch/emails/`
   - Verify personalization
   - Confirm subject line
3. **Decision:**
   - **APPROVE:** Click "Move" → "Approved / Send"
     - Add comment: `APPROVED [DATE] — Send today`
   - **REJECT:** Click "Move" → "Daily Queue"
     - Add comment: `REJECTED [DATE] — [reason]`
     - Update due date
   - **MODIFY:** Edit description, then approve

**Approval Speed Target:** 2-3 minutes per card

---

### PHASE 4: EXECUTION — Approved/Send → Follow-up (15 minutes)

**For each card in Approved / Send:**

1. **Open email draft** (path in card description)
2. **Copy subject line** from card
3. **Send email** via Gmail:
   - TO: Partner email (in card description)
   - SUBJECT: As specified in card
   - BODY: Copy from email draft file
   - ATTACH: Latest deck from `outreach_assets/pitch_deck/`
4. **Log the send:**
   - Add Trello comment template:
   ```
   SENT ✅
   - Channel: Email
   - Timestamp: [DATE TIME CST]
   - To: [partner@fund.vc]
   - Subject: [subject line]
   - Deck: v2026.03.02
   - Follow-up due: [DATE +3 days]
   ```
5. **Move card:** "Approved / Send" → "Follow-up"
6. **Set due date:** Today + 3 days
7. **Update checklist:**
   - [x] Approved
   - [x] Sent
   - [ ] Follow-up 1
   - [ ] Follow-up 2
   - [ ] Response logged

---

### PHASE 5: FOLLOW-UP MANAGEMENT (Friday Only — 20 minutes)

**For each card in Follow-up with due date = today:**

1. **Check for replies:**
   - Search Gmail for partner name
   - Check spam folder
2. **If reply received:**
   - Add comment: `REPLY RECEIVED [DATE] — [summary]`
   - Update due date based on reply (meeting booked = +7 days, no reply = +4 days)
3. **If NO reply:**
   - Open follow-up email draft (in `followups_march_2/`)
   - Send follow-up
   - Add comment:
   ```
   FOLLOW-UP 1 SENT ✅
   - Timestamp: [DATE]
   - Template: [template name]
   - Next follow-up: [DATE +4 days]
   ```
4. **Move card if needed:**
   - Reply received → Keep in Follow-up, update checklist
   - 3 follow-ups sent, no reply → Move to "Archive" (create list if needed)

---

## 4. DAILY EXECUTION CHECKLIST

### Morning Routine (Start of Day)

| # | Task | Time | Done |
|---|------|------|------|
| 1 | Open Trello board, review all lists | 3 min | [ ] |
| 2 | Process Daily Queue → Awaiting Approval (max 5 cards) | 10 min | [ ] |
| 3 | Approve cards → Approved/Send | 10 min | [ ] |
| 4 | **SEND WINDOW:** Execute Approved/Send cards (12:00 CST target) | 15 min | [ ] |
| 5 | Log sends in Trello comments | 5 min | [ ] |
| 6 | Update sent_log.csv (if maintaining) | 5 min | [ ] |

### End of Day

| # | Task | Time | Done |
|---|------|------|------|
| 7 | Verify all sent cards moved to Follow-up | 2 min | [ ] |
| 8 | Confirm due dates set (+3 days) | 2 min | [ ] |
| 9 | Note any blockers for tomorrow | 3 min | [ ] |

---

## 5. TIME ESTIMATES PER BATCH

### Batch Processing (5 cards)

| Phase | Time per Card | Batch of 5 |
|-------|---------------|------------|
| Review + Move to Approval | 2 min | 10 min |
| Approval Decision | 2 min | 10 min |
| Send Execution | 3 min | 15 min |
| Logging + Comments | 1 min | 5 min |
| **TOTAL per batch** | **8 min** | **40 min** |

### Daily Throughput Capacity

| Activity | Cards/Day | Time Required |
|----------|-----------|---------------|
| Conservative | 3-5 | 30-45 min |
| Moderate | 6-8 | 60-75 min |
| Aggressive | 10+ | 90+ min |

**Recommended:** 5 cards/day (40 min) for sustainable execution

---

## 6. CARD TEMPLATES

### New Card Creation (if needed)

**Card Name Format:**
```
[P{Priority}] {Fund Name} — {Partner Name}
```

**Description Template:**
```
Partner: {Full Name}
Email: {email@fund.vc}
Fit Score: {XX}/100
Priority: {P1/P2/P3}

Hook: {One-line personalized hook}

Subject: {Email subject line}

Email Draft: deliverables/day{X}_vc_batch/emails/{filename}.txt
Batch: Day {X}
Due: {YYYY-MM-DD}

---
Deck: outreach_assets/pitch_deck/latest.pdf
KPI Sheet: outreach_assets/kpi_sheet.pdf
Case Study: outreach_assets/case_studies/
```

---

## 7. TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Can't find email draft | Check `day{X}_vc_batch/emails/` folder; if missing, use generic template from `outreach_assets/templates/` |
| Partner email bounced | Add comment "BOUNCE — needs enrichment", move to Daily Queue, tag for research |
| Sent but forgot to log | Add comment retroactively with estimated timestamp |
| Card stuck in wrong list | Move manually; add comment explaining state change |
| Duplicate cards | Archive the lower-priority one; add comment "Duplicate — archived in favor of [card link]" |
| Too many cards in Daily Queue | Process only top 5 by fit score; rest stay in queue |

---

## 8. QUALITY CHECKPOINTS

**Before Moving to Approved/Send:**
- [ ] Fit score ≥ 80/100
- [ ] Partner email is direct (not info@)
- [ ] Hook references specific fund investment
- [ ] Subject line < 60 characters
- [ ] Email draft < 200 words

**Before Sending:**
- [ ] Deck is latest version
- [ ] No placeholder text in email
- [ ] Calendly link included
- [ ] Signature correct

**After Sending:**
- [ ] Comment logged with timestamp
- [ ] Card moved to Follow-up
- [ ] Due date set for +3 days
- [ ] Checklist updated

---

## 9. EMERGENCY PROCEDURES

### Day 1 Backlog (Current State — 7 Days Stale)

**Option A: Execute Now (RECOMMENDED)**
1. Move all 5 Day 1 cards to Approved/Send immediately
2. Send all 5 today (budget 75 minutes)
3. Skip Day 3 follow-ups (awkward timing)
4. Resume normal cadence with Day 22+ batches

**Option B: Archive and Restart**
1. Move Day 1 cards to Archive list
2. Start fresh with Day 22 batch
3. No awkward follow-up timing issues

**Option C: Hybrid**
1. Select top 3 from Day 1 by fit score
2. Send those, archive remaining 2
3. Continue with fresh batches

---

## 10. SUCCESS METRICS (Manual Tracking)

Track weekly in spreadsheet or notes:

| Week | Cards Sent | Follow-ups | Replies | Meetings |
|------|------------|------------|---------|----------|
| Mar 2-8 | ___ | ___ | ___ | ___ |
| Mar 9-15 | ___ | ___ | ___ | ___ |

**Target:** 25 sends/week, 5-10% reply rate

---

## APPENDIX: QUICK REFERENCE

**Board URL:** https://trello.com/b/tPkRdYjg/vc-outreach-engine  
**Send Window:** 12:00 CST  
**Follow-up Cadence:** Day 3, Day 7, Day 14  
**Deck Location:** `deliverables/outreach_assets/pitch_deck/latest.pdf`

**Label Codes:**
- `Day-{X}` — Batch identifier
- `Fit-Score-{XX}` — Priority indicator
- `Ready` — Approved for send
- `Sent` — Email sent
- `Replied` — Response received
- `Meeting` — Call/meeting booked

---

*Document Version: 1.0*  
*Last Updated: March 2, 2026*  
*Next Review: March 9, 2026*
