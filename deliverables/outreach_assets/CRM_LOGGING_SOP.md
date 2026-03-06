# CRM Logging SOP
## How to Log Sends, Follow-ups, and Outcomes

---

## OVERVIEW

Until full CRM automation is live, we use CSV files for tracking:
- **sent_log.csv** — Record every email sent
- **follow_up_log.csv** — Track Day 3 and Day 7 follow-ups

**Files location:** `/data/workspace/deliverables/outreach_assets/`

---

## SENT LOG FORMAT

**File:** `sent_log.csv`

### Columns

| Column | Description | Example |
|--------|-------------|---------|
| fund_name | Full fund name | BITKRAFT Ventures |
| packet_id | Priority code | P1 |
| channel | Where sent from | email |
| sender | Who sent it | lucas@company.com |
| contact | Recipient name | Martin Garcia |
| target_send_at_utc | Planned send time | 2026-02-25T14:00:00Z |
| sent_at_utc | Actual send time | 2026-02-25T14:05:00Z |
| follow_up_due_utc | When to follow up | 2026-02-28T14:00:00Z |
| assets_link | Path to attachments | deliverables/outreach_assets/pitch_deck/latest.pdf |
| proof_link | Screenshot/link | [optional] |
| notes | Any context | First touch; intro via scoring engine |

### How to Log a Send

1. Open `sent_log.csv` in any spreadsheet editor (Excel, Google Sheets, or text editor)
2. Add a new row with the above fields
3. Save the file

### Example Entry

```csv
BITKRAFT Ventures,P1,email,lucas@company.com,Martin Garcia,2026-02-25T14:00:00Z,2026-02-25T14:05:00Z,2026-02-28T14:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch; intro via scoring engine
```

---

## FOLLOW-UP LOG FORMAT

**File:** `follow_up_log.csv`

### Columns

| Column | Description | Example |
|--------|-------------|---------|
| fund_name | Full fund name | BITKRAFT Ventures |
| packet_id | Priority code | P1 |
| follow_up_type | Day 3 or Day 7 | day_3 |
| scheduled_for_utc | When scheduled | 2026-02-28T14:00:00Z |
| completed_at_utc | When actually sent | 2026-02-28T14:10:00Z |
| channel | How sent | email |
| owner | Who sent it | lucas |
| outcome | Result | replied / no_reply / bounced / meeting_booked |
| notes | Context | Positive reply; call scheduled for March 5 |

### Follow-up Schedule

| Send Date | Day 3 Follow-up | Day 7 Follow-up |
|-----------|-----------------|-----------------|
| 2026-02-25 | 2026-02-28 | 2026-03-04 |
| 2026-02-26 | 2026-03-01 | 2026-03-05 |
| 2026-02-27 | 2026-03-02 | 2026-03-06 |

### Day 3 Follow-up Template

```
Hi [Name],

Quick follow-up on my note from [Day 0 date] about our AI sourcing engine for gaming/AI funds.

We're now booking 4-5 partner meetings per week through this system, and I'd love to get BITKRAFT's perspective on whether this fits your Seed/Series A thesis.

If timing's not right, totally understand—just let me know and I'll check back in a few months.

Best,
Lucas
```

### Day 7 Follow-up Template (Final Bump)

```
Hi [Name],

Last ping on this—I'll assume timing isn't right for now unless I hear otherwise.

If BITKRAFT's thesis evolves or you want to see our engine in action down the road, happy to reconnect.

Best,
Lucas
```

---

## OUTCOME TRACKING

Use these standardized outcome codes in follow_up_log.csv:

| Outcome Code | Meaning | Next Action |
|--------------|---------|-------------|
| no_reply | No response received | Archive; revisit in 90 days |
| replied | Got a response | Log reply content; respond same day |
| meeting_booked | Call scheduled | Log in calendar; prepare for call |
| passed | Explicit no | Archive; note reason if provided |
| bounced | Email bounced | Flag for contact refresh |
| ooo | Out of office | Reschedule follow-up |

---

## WORKFLOW CHECKLIST

### Immediately After Sending (Within 1 hour):

- [ ] Log send in `sent_log.csv`
- [ ] Calculate Day 3 follow-up date (send date + 3 days)
- [ ] Calculate Day 7 follow-up date (send date + 7 days)
- [ ] Add follow-up reminders to calendar
- [ ] Move Trello card to "Sent" column

### On Day 3 (Morning):

- [ ] Check if reply received
- [ ] If no reply: Send Day 3 follow-up
- [ ] Log follow-up in `follow_up_log.csv`
- [ ] Update Trello card with follow-up status

### On Day 7 (Morning):

- [ ] Check if reply received
- [ ] If no reply: Send Day 7 final bump
- [ ] Log follow-up in `follow_up_log.csv`
- [ ] Update Trello card with final outcome
- [ ] If still no reply: Move card to "No Response" or archive

### On Reply Received:

- [ ] Reply within 4 hours (same day max)
- [ ] Log outcome as "replied" in follow_up_log.csv
- [ ] If meeting booked: Log as "meeting_booked" with date
- [ ] Update Trello card description with reply summary
- [ ] Move card to appropriate column (Meeting Booked / Passed / etc.)

---

## SAMPLE COMPLETED LOGS

### sent_log.csv Example (After P1-P5 Sends):

```csv
fund_name,packet_id,channel,sender,contact,target_send_at_utc,sent_at_utc,follow_up_due_utc,assets_link,proof_link,notes
BITKRAFT Ventures,P1,email,lucas@company.com,Martin Garcia,2026-02-25T16:00:00Z,2026-02-25T16:05:00Z,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,Gaming/AI focus; synthetic reality thesis match
Konvoy Ventures,P2,email,lucas@company.com,Taylor Hurst,2026-02-25T16:00:00Z,2026-02-25T16:08:00Z,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,Infrastructure angle
Mechanism Capital,P3,email,lucas@company.com,Steve Cho,2026-02-25T16:00:00Z,2026-02-25T16:10:00Z,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,Crypto-gaming thesis
Variant,P4,email,lucas@company.com,Spencer Noon,2026-02-25T16:00:00Z,2026-02-25T16:12:00Z,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,User ownership angle
Collab+Currency,P5,email,lucas@company.com,Derek Edwards,2026-02-25T16:00:00Z,2026-02-25T16:15:00Z,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,Crypto x culture angle
```

### follow_up_log.csv Example (After Day 3 Follow-ups):

```csv
fund_name,packet_id,follow_up_type,scheduled_for_utc,completed_at_utc,channel,owner,outcome,notes
BITKRAFT Ventures,P1,day_3,2026-02-28T16:00:00Z,2026-02-28T16:05:00Z,email,lucas,meeting_booked,Call scheduled for March 5 2026
Konvoy Ventures,P2,day_3,2026-02-28T16:00:00Z,2026-02-28T16:08:00Z,email,lucas,no_reply,Will send Day 7 bump
Mechanism Capital,P3,day_3,2026-02-28T16:00:00Z,2026-02-28T16:10:00Z,email,lucas,replied,Asked for more info on metrics
```

---

## INTEGRATION WITH TRELLO

Mirror your CSV logging in Trello card comments:

1. **After send:** Comment "Sent 2026-02-25 16:05 UTC | Day 3: 2026-02-28 | Day 7: 2026-03-04"
2. **After follow-up:** Comment "Day 3 follow-up sent 2026-02-28 16:08 UTC"
3. **After reply:** Comment "Reply received 2026-03-01: [summary] | Outcome: meeting_booked"

This creates an audit trail in both CSV (data) and Trello (visual workflow).

---

## AUTOMATION ROADMAP

Future state (when Trello API credentials available):
- Auto-create cards from daily manifest
- Auto-move cards on approval
- Auto-log sends when marked "Sent"
- Auto-schedule follow-up reminders
- Two-way sync with CRM (HubSpot/Salesforce)

Until then: **Manual CSV logging = source of truth**

---

## FILES LOCATION SUMMARY

| File | Path | Purpose |
|------|------|---------|
| Sent Log | `/data/workspace/deliverables/outreach_assets/sent_log.csv` | Record all sends |
| Follow-up Log | `/data/workspace/deliverables/outreach_assets/follow_up_log.csv` | Track follow-ups |
| Execution Plan | `/data/workspace/deliverables/outreach_assets/MANUAL_EXECUTION_PLAN.md` | Full workflow |
| Email Templates | `/data/workspace/deliverables/outreach_assets/email_templates.md` | Ready-to-send copy |
| This SOP | `/data/workspace/deliverables/outreach_assets/CRM_LOGGING_SOP.md` | Logging instructions |
