# VC Outreach Quick-Start Checklist
## 5 Packets Ready to Send | Today: 2026-02-25

---

## BEFORE YOU START (2 min)

- [ ] Open Trello board (VC Outreach)
- [ ] Locate or create columns: Daily Queue → Awaiting Approval → Approved → Sent
- [ ] Have email client ready
- [ ] Have pitch deck PDF ready to attach
- [ ] Have KPI snapshot ready to attach

---

## PHASE 1: TRELLO SETUP (5 min)

### Create 5 Cards in "Daily Queue"

Copy/paste these exact card names:

1. `[P1] BITKRAFT Ventures - Martin Garcia, CFO & General Partner`
2. `[P2] Konvoy Ventures - Taylor Hurst, Principal`
3. `[P3] Mechanism Capital - Steve Cho, Partner`
4. `[P4] Variant - Spencer Noon, Co-Founder & General Partner`
5. `[P5] Collab+Currency - Derek Edwards, Managing Partner`

### Add Description to Each Card

Use this template:
```
Priority: [P1/P2/P3/P4/P5]
Contact: [Name]
Email: [email@fund.com]
Check Size: [from manifest]
Stage: [from manifest]

Email template: email_templates.md
Attachments: pitch_deck/latest.pdf, kpi_snapshot/2026-02-24-kpis.csv

[ ] Move to Awaiting Approval
[ ] Approve
[ ] Move to Approved
[ ] Send email
[ ] Move to Sent
[ ] Log in sent_log.csv
```

---

## PHASE 2: REVIEW & APPROVE (5 min)

### Quick Review Checklist

For each card:
- [ ] Email address looks correct
- [ ] Fund thesis aligns with our product
- [ ] Check size overlap exists
- [ ] Hook angle makes sense

### Move Cards

- [ ] Move all 5 cards to "Awaiting Approval"
- [ ] Quick review (or skip if trusting the system)
- [ ] Move approved cards to "Approved"

---

## PHASE 3: SEND EMAILS (15 min)

### For Each Packet:

1. **Open** email_templates.md
2. **Copy** the template for your packet (P1-P5)
3. **Customize**:
   - Add your name/title/company
   - Update Calendly link (or remove if not ready)
4. **Attach**:
   - pitch_deck/latest.pdf
   - kpi_snapshot/2026-02-24-kpis.csv
5. **Send**
6. **Log** in sent_log.csv (see below)

### Email Reference Table

| Card | Send To | Subject Line (from template) |
|------|---------|------------------------------|
| P1 | martin@bitkraft.vc | AI sourcing engine for gaming/AI funds — 4 partner meetings/week |
| P2 | taylor@konvoy.vc | Infrastructure play: Daily VC scoring engine for gaming funds |
| P3 | steve@mechanism.capital | Crypto-gaming meets AI: Daily investor scoring engine |
| P4 | spencer@variant.fund | User-owned VC sourcing: AI engine + partner approval loop |
| P5 | derek@collabcurrency.com | Crypto x culture: Daily investor packets as product |

---

## PHASE 4: LOGGING (5 min)

### Update sent_log.csv

Open `/data/workspace/deliverables/outreach_assets/sent_log.csv`

Add 5 rows (one per send):

```csv
BITKRAFT Ventures,P1,email,YOUR_EMAIL,Martin Garcia,2026-02-25T16:00:00Z,2026-02-25TACTUAL_TIME,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch
Konvoy Ventures,P2,email,YOUR_EMAIL,Taylor Hurst,2026-02-25T16:00:00Z,2026-02-25TACTUAL_TIME,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch
Mechanism Capital,P3,email,YOUR_EMAIL,Steve Cho,2026-02-25T16:00:00Z,2026-02-25TACTUAL_TIME,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch
Variant,P4,email,YOUR_EMAIL,Spencer Noon,2026-02-25T16:00:00Z,2026-02-25TACTUAL_TIME,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch
Collab+Currency,P5,email,YOUR_EMAIL,Derek Edwards,2026-02-25T16:00:00Z,2026-02-25TACTUAL_TIME,2026-02-28T16:00:00Z,deliverables/outreach_assets/pitch_deck/latest.pdf,,First touch
```

### Update Trello

- [ ] Move all 5 cards to "Sent" column
- [ ] Add comment to each: "Sent [DATE] [TIME] | Follow-up Day 3: 2026-02-28"

### Set Calendar Reminders

- [ ] Day 3 Follow-ups: February 28, 2026
- [ ] Day 7 Follow-ups: March 4, 2026

---

## PHASE 5: FOLLOW-UPS (Scheduled)

### Day 3 - February 28

Check sent_log.csv for funds with no reply:
- [ ] Send Day 3 follow-up (template in CRM_LOGGING_SOP.md)
- [ ] Log in follow_up_log.csv
- [ ] Update Trello card

### Day 7 - March 4

Check for replies:
- [ ] Send Day 7 final bump (if no reply)
- [ ] Log in follow_up_log.csv
- [ ] Update Trello card with final outcome
- [ ] Archive non-responders

---

## FILE LOCATIONS

| Need | Go To |
|------|-------|
| Email templates | `/data/workspace/deliverables/outreach_assets/email_templates.md` |
| This checklist | `/data/workspace/deliverables/outreach_assets/QUICK_START_CHECKLIST.md` |
| Full execution plan | `/data/workspace/deliverables/outreach_assets/MANUAL_EXECUTION_PLAN.md` |
| CRM logging SOP | `/data/workspace/deliverables/outreach_assets/CRM_LOGGING_SOP.md` |
| Sent log (CSV) | `/data/workspace/deliverables/outreach_assets/sent_log.csv` |
| Follow-up log (CSV) | `/data/workspace/deliverables/outreach_assets/follow_up_log.csv` |
| Pitch deck | `/data/workspace/deliverables/outreach_assets/pitch_deck/latest.pdf` |
| KPI snapshot | `/data/workspace/deliverables/outreach_assets/kpi_snapshot/2026-02-24-kpis.csv` |
| Company blurb | `/data/workspace/deliverables/outreach_assets/blurb.md` |

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Calendly link missing | Remove from template; offer times manually |
| Pitch deck not ready | Send without; follow up with deck |
| Email bounces | Flag in notes; find alternative contact |
| Reply asks for different info | Log in follow_up_log.csv; respond same day |
| Want to customize template | Edit email_templates.md before sending |

---

## TIME ESTIMATE

| Phase | Time |
|-------|------|
| Trello Setup | 5 min |
| Review & Approve | 5 min |
| Send Emails | 15 min |
| Logging | 5 min |
| **Total** | **30 min** |

---

## NEXT STEPS AFTER TODAY

1. **Monitor replies** (check email 2x daily)
2. **Send Day 3 follow-ups** (Feb 28)
3. **Send Day 7 follow-ups** (Mar 4)
4. **Process replies** (same-day response target)
5. **Book meetings** (add to calendar, prep for calls)

---

## QUESTIONS?

- **Want to customize a template?** Edit `/data/workspace/deliverables/outreach_assets/email_templates.md`
- **Need to change a contact?** Update Trello card description
- **Lost track of what you sent?** Check `sent_log.csv`
- **Want to automate this?** Set Trello API credentials and I'll handle the workflow

**Ready to start?** Begin with Phase 1: Trello Setup.
