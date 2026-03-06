# Approval Workflow SOP

_Last updated: 24 Feb 2026 — Owner: Ops Lead_

## Objective
Ensure every investor packet in the **Daily Queue** receives a fast, traceable approval decision from Lucas before being sent. Target SLA: **<4 hours** from the moment a card enters **Awaiting Approval**.

## Roles
- **Packet Preparer (Ops):** Finalizes packet content, owns Trello hygiene, triggers approval.
- **Approver (Lucas):** Reviews packet description + attachments, marks decision, and drops any edits inline.
- **Automation Layer:** Trello Butler + Slack webhook (or Maton bridge) that keeps Lucas notified until each card is cleared.

## Prerequisites
1. Trello card fully populated using the investor packet template (Snapshot → Follow-up sections completed).
2. Mandatory attachments added (deck PDF, KPI sheet, case study/press link, Calendly instructions once ready).
3. Checklist items for the packet marked complete (asset inventory, personalization, snippet, reminders).
4. Card assigned to Lucas with due date = target send time (default 12:00 CST same day).

## Step-by-Step
1. **Ready for review**
   - Title: `Packet: <Fund>`
   - Labels: `Type: Outreach`, `Priority: P1`, appropriate Workstream/ Effort.
   - Custom fields (if enabled): Priority tier, Score, Contact owner.
   - Move the card from **Daily Queue** → **Awaiting Approval** and add a comment summarizing the ask (see template below).
2. **Slack ping (minute 0)**
   - Immediately post in `#all-fulk-em` (or Lucas DM) with:
     - Fund name + priority tier
     - Key hook (1 sentence)
     - Attach Trello short link
     - Explicit ask: “Need approve-or-edit before 13:00 CST.”
3. **Reminder cadence**
   - If no Trello activity from Lucas within **30 minutes**, trigger a reminder (manual ping until automation is live).
   - Reminders repeat every 30 minutes (max 3 times) with most recent blocker/status.
   - After 90 minutes with no response, escalate via direct DM + note in daily summary.
4. **Approval logging**
   - Lucas reacts inside Trello by checking the `Approval` checklist or moving card to **Approved / Send**.
   - Packet preparer logs `approved_at` timestamp in a Trello custom field or comment until CRM sync is online.
5. **Edits requested**
   - If Lucas requests changes, keep card in **Awaiting Approval**, capture edits in checklist, and loop back to Step 2 once fixes complete.
6. **Audit trail**
   - Once card moves to **Approved / Send**, add a comment: `Approved by Lucas @ <UTC time>. Ready for send.`
   - Update CRM packet row with `status=APPROVED` (manual spreadsheet until DB live).

## Slack Message Templates
**Initial Ping**
```
Packet ready: BITKRAFT Ventures (Priority A | score 84). Hook: synthetic reality sourcing loop tied to their new Web3 partner bench. Need approval before 13:00 CST. https://trello.com/c/7nJkr10H
```

**Reminder (30 min)**
```
Reminder: BITKRAFT packet still in Awaiting Approval (32 mins). Blocking send target (12:00 CST). Need thumbs-up or edits.
```

## Automation Blueprint (post-credentials)
1. **Trello Butler rule**
   - Trigger: “When a card is moved to Awaiting Approval”
   - Actions: set due in 4h, add Lucas as member, post comment template, call webhook.
2. **Slack Incoming Webhook / Maton**
   - Payload: fund name, tier, due time, Trello URL.
   - Butler or serverless job schedules `card due` reminders every 30 min until card leaves list.
3. **Failsafe job**
   - Scheduled script (Cloudflare Worker or GitHub Action) polls Trello every 15 minutes and posts outstanding approvals + age to Slack if >2 hours.

## KPIs Tracked
- Approval SLA (target <4h)
- Count of cards awaiting approval per day
- Number of reminders sent per card (aim to reduce as automation + clarity improve)

## Dependencies / Next Actions
- Need Slack webhook URL (or Maton channel) to wire Butler automation.
- Trello custom fields for `Score`, `Priority Tier`, `Approval Timestamp`.
- CRM connection to auto-write `approved_at` once DB credentials exist.

---
**Trello Comment Template (paste when entering Awaiting Approval)**
```
@Lucas Packet ready for approval.
- Fund: BITKRAFT Ventures (Priority A, score 84)
- Hook: Synthetic Reality thesis + AI sourcing loop alignment
- Attachments: deck v2026.02, KPI snapshot, case study link
Need approve / edits before 13:00 CST to hit send target.
```
