# Follow-Up Cadence System

_Last updated: 24 Feb 2026 — Owner: Ops Lead_

## Objective
Guarantee every investor packet receives structured follow-ups until the conversation resolves. Standard cadence: **Day 0 send → Day 3 reminder → Day 7 bump → ongoing thread or close-out**. Goal metrics: ≥30% reply rate, 100% of replies logged within 12 hours.

## Cadence Overview
| Day | Trigger | Channel | Owner | Notes |
| --- | --- | --- | --- | --- |
| 0 | Packet approved + sent | Email / intro / DM | Sender (Lucas or Ops) | Log send proof + schedule follow-up in Trello/CRM. |
| 3 | No reply logged | Slack reminder + email bump #1 | Ops | Reference original thread, add new hook (metric, social proof). |
| 7 | Still no reply | Email bump #2 or alternate channel (DM/intro) | Ops / Lucas | Escalate tone slightly (“closing the loop”), optionally share new traction. |
| 10+ | Still dark | Move to nurture queue, note reason, schedule monthly check-in if fund remains high priority. |
| Any reply | Immediately | Same channel | Owner | Acknowledge within 2 business hours, move Trello card to **Follow-up** list, create meeting task if needed. |

## Operational Steps
1. **Scheduling follow-ups**
   - When logging a send, set `follow_up_due` to Day 3 at 15:00 recipient local time.
   - Use Trello due dates or CRM task table to surface due follow-ups each morning.
2. **Crafting bumps**
   - Keep to 3–4 sentences.
   - Reference new proof (customer logo, KPI delta, event speaking slot) so message stays fresh.
   - Always include Calendly link (once finalized) or two concrete time options.
3. **Logging replies**
   - When a reply arrives:
     - Move card from **Approved / Send** → **Follow-up**.
     - Add comment summarizing reply outcome (interested, request for deck, not a fit, etc.).
     - Update CRM `outreach_attempts` with `status=RESPONDED` and `responded_at` timestamp (use interim spreadsheet until backend is live).
4. **Meeting workflow**
   - For qualified replies, create a Meeting subtask immediately:
     - Capture date/time, participants, medium, and meeting link.
     - Once scheduled, add to Trello card checklist + log in CRM `meetings` table (or interim sheet).
5. **Closing the loop**
   - If after Day 7 bump there is no response, mark the packet as `CLOSED_NO_REPLY` and move to nurture board with lesson learned (missing contact, mismatch, etc.).
   - If fund explicitly passes, log reason verbatim, move card to archive list, and tag for future update if thesis shifts.

## Templates
**Day 3 Bump (email)**
```
Subject: Re: Packet for Konvoy Ventures

Hi <Name>, looping this back up — we’ve now booked four partner meetings from the daily AI x gaming packets and the Konvoy fit is even stronger given your Q1 report on live-service monetization. Happy to drop the metrics deck or hop on a 20-min call (Wed 10:30a CT / Thu 1:00p CT). Let me know if either works.
```

**Day 7 Bump**
```
Hi <Name>, quick close-the-loop on the AI gaming pipeline I sent last week. We’re locking next week’s investor packet queue tomorrow; if Konvoy wants to review the current top target (attention ops layer for live-service studios) I can prioritize the walkthrough. Otherwise I’ll circle back after our next release.
```

**Reply Logging Comment**
```
Reply 24 Feb 2026 22:14 UTC — <Name> (Konvoy) asked for KPI sheet + intro next week. Meeting placeholder 27 Feb pending confirmation.
```

## Automation Blueprint
- Butler rule: when card enters **Follow-up**, set due date to `follow_up_due` and add checklist `Day 3 bump`, `Day 7 bump`, `Outcome logged`.
- Scheduled script polls Trello each morning, posts outstanding follow-ups to Slack.
- Once backend API is live, `/api/outreach-attempts` endpoint will create Day 3/7 reminders automatically and write statuses back when checkboxes complete.

## Metrics to Monitor
- % of packets with Day 3 follow-up completed on time (target ≥95%).
- Reply rate by follow-up touch (expect ~60% of replies after Day 0, 30% Day 3, 10% Day 7).
- Average time from reply → meeting scheduled (<24h target).

## Dependencies / Blockers
- Need Calendly URL + meeting template.
- Need Slack webhook/Trello Butler access to auto-assign due dates and reminders.
- CRM connection required for permanent logging; using `deliverables/outreach_assets/sent_log.csv` and a matching `follow_up_log.csv` (to be added) until credentials arrive.
