# VC Outreach Execution Plan
## Manual Trello Workflow (API Unavailable)
**Date:** 2026-02-25
**Status:** 5 Packets Ready for Approval → Send

---

## CURRENT STATE

| Priority | Fund | Contact | Email | Status |
|----------|------|---------|-------|--------|
| P1 | BITKRAFT Ventures | Martin Garcia, CFO & General Partner | martin@bitkraft.vc | Ready |
| P2 | Konvoy Ventures | Taylor Hurst, Principal | taylor@konvoy.vc | Ready |
| P3 | Mechanism Capital | Steve Cho, Partner | steve@mechanism.capital | Ready |
| P4 | Variant | Spencer Noon, Co-Founder & General Partner | spencer@variant.fund | Ready |
| P5 | Collab+Currency | Derek Edwards, Managing Partner | derek@collabcurrency.com | Ready |

**Trello Board Structure:**
- Board: VC Outreach (or your default board)
- Columns: Daily Queue → Awaiting Approval → Approved → Sent

---

## LUCAS ACTION CHECKLIST

### Step 1: Trello Card Setup (2 minutes)

For each of the 5 packets below, manually create a card in Trello:

#### Card Names (copy/paste):

**P1:** `[P1] BITKRAFT Ventures - Martin Garcia, CFO & General Partner`

**P2:** `[P2] Konvoy Ventures - Taylor Hurst, Principal`

**P3:** `[P3] Mechanism Capital - Steve Cho, Partner`

**P4:** `[P4] Variant - Spencer Noon, Co-Founder & General Partner`

**P5:** `[P5] Collab+Currency - Derek Edwards, Managing Partner`

---

### Step 2: Card Description Template

Copy this into each card description (customize per packet):

```markdown
**Priority:** [P1/P2/P3/P4/P5]
**Fund:** [Fund Name]
**Contact:** [Full Name and Title]
**Email:** [email@fund.com]
**Fund Score:** [Score from manifest]
**Check Size:** [Range from manifest]
**Stage Focus:** [Stages from manifest]
**HQ:** [Location from manifest]

**Assets:**
- Pitch deck: `deliverables/outreach_assets/pitch_deck/latest.pdf`
- KPI snapshot: `deliverables/outreach_assets/kpi_snapshot/2026-02-24-kpis.csv`
- Blurb: `deliverables/outreach_assets/blurb.md`

**Email Template:** See `deliverables/outreach_assets/email_templates/packet-[P1-P5].md`

**Actions:**
- [ ] Move to Awaiting Approval
- [ ] Lucas reviews and approves
- [ ] Move to Approved
- [ ] Send email
- [ ] Move to Sent
- [ ] Log in sent_log.csv
```

---

### Step 3: Trello Workflow Actions

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Create 5 cards in "Daily Queue" column | Lucas | 2 min |
| 2 | Review each card, check email template | Lucas | 5 min |
| 3 | Move approved cards to "Awaiting Approval" | Lucas | 1 min |
| 4 | Quick approval review (or approve all) | Lucas | 3 min |
| 5 | Move approved cards to "Approved" column | Lucas | 1 min |
| 6 | Send emails (copy/paste templates) | Lucas | 10 min |
| 7 | Move sent cards to "Sent" column | Lucas | 1 min |
| 8 | Log sends in sent_log.csv | Lucas | 5 min |

**Total Time:** ~28 minutes for all 5 sends

---

## PACKET-SPECIFIC NOTES

### P1: BITKRAFT Ventures
- **Score:** 84.0 (highest priority)
- **Why them:** Synthetic reality thesis, gaming/esports focus, built by founders
- **Hook angle:** Daily scoring engine aligns with their "founders for founders" ethos
- **Best time to send:** Tuesday-Thursday, 9-11am EST

### P2: Konvoy Ventures
- **Score:** 59.33
- **Why them:** Pure gaming infrastructure thesis, Denver-based
- **Hook angle:** Infrastructure play (daily scoring engine as platform)
- **Note:** Check size max is $3M (lower overlap with target)

### P3: Mechanism Capital
- **Score:** 53.33
- **Why them:** Blockchain + gaming focus, crypto-native
- **Hook angle:** AI + gaming intersection, potential token model
- **Note:** No HQ listed, may be distributed team

### P4: Variant
- **Score:** 48.33
- **Why them:** User ownership thesis, crypto-native
- **Hook angle:** Alignment between AI engine and human partner workflow
- **Note:** Strong check size overlap (89%)

### P5: Collab+Currency
- **Score:** 51.33
- **Why them:** Crypto x culture intersection, thesis-fit for gaming
- **Hook angle:** Daily packet culture as product
- **Note:** Based in Eugene, OR (not SF/NYC)

---

## POST-SEND ACTIONS

### Immediate (within 1 hour of sending):
1. Log each send in `/data/workspace/deliverables/outreach_assets/sent_log.csv`
2. Schedule follow-ups (Day 3 and Day 7) in calendar
3. Update Trello cards to "Sent" column

### Follow-up Schedule:
| Fund | Send Date | Day 3 Follow-up | Day 7 Follow-up |
|------|-----------|-----------------|-----------------|
| P1 BITKRAFT | [DATE] | [DATE+3] | [DATE+7] |
| P2 Konvoy | [DATE] | [DATE+3] | [DATE+7] |
| P3 Mechanism | [DATE] | [DATE+3] | [DATE+7] |
| P4 Variant | [DATE] | [DATE+3] | [DATE+7] |
| P5 Collab+Currency | [DATE] | [DATE+3] | [DATE+7] |

---

## FILES REFERENCE

| File | Purpose | Path |
|------|---------|------|
| Email Templates | Ready-to-send emails | `/data/workspace/deliverables/outreach_assets/email_templates/packet-[P1-P5].md` |
| CRM Logging SOP | How to log sends/follow-ups | `/data/workspace/deliverables/outreach_assets/CRM_LOGGING_SOP.md` |
| Pitch Deck | Attachment for emails | `/data/workspace/deliverables/outreach_assets/pitch_deck/latest.pdf` |
| KPI Snapshot | Metrics attachment | `/data/workspace/deliverables/outreach_assets/kpi_snapshot/2026-02-24-kpis.csv` |
| Company Blurb | Reference copy | `/data/workspace/deliverables/outreach_assets/blurb.md` |
| Sent Log | Record of sends | `/data/workspace/deliverables/outreach_assets/sent_log.csv` |
| Follow-up Log | Track follow-ups | `/data/workspace/deliverables/outreach_assets/follow_up_log.csv` |

---

## TRELLO API SETUP (For Future Automation)

To enable automated card movement, set these environment variables:

```bash
export TRELLO_API_KEY="your_key_here"
export TRELLO_TOKEN="your_token_here"
export TRELLO_BOARD_ID="your_board_id_here"
```

Get your credentials at: https://trello.com/app-key

Once set, I can automate:
- Card creation from daily manifest
- Auto-move on approval
- Logging on send completion
- Follow-up scheduling

---

## NEXT ACTIONS

| Owner | Action | Due |
|-------|--------|-----|
| Lucas | Create 5 Trello cards in "Daily Queue" | Today |
| Lucas | Review email templates (in next section) | Today |
| Lucas | Move cards through workflow and send | Today |
| Lucas | Log sends in sent_log.csv | Today |
| Ops | Optional: Set Trello API credentials | This week |

---

## QUESTIONS?

If any packet needs revision or you want to customize angles:
- Edit templates at: `/data/workspace/deliverables/outreach_assets/email_templates/`
- Update card descriptions before moving to "Awaiting Approval"
- Ping me for real-time adjustments
