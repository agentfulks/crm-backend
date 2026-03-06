# Sending SOP & Audit Trail

_Last updated: 24 Feb 2026 — Owner: Lucas_

## Objective
Provide a single, repeatable process for sending approved investor packets, logging proof, and keeping CRM / Trello states synchronized. Every packet must show **Approved → Sent → Logged** with timestamps and evidence.

## Pre-Send Checklist
1. **Approval confirmed**
   - Card resides in **Approved / Send** list.
   - Approval comment includes timestamp + decision maker.
2. **Assets verified**
   - Deck link points to latest PDF (`deliverables/outreach_assets/pitch_deck/latest.pdf`).
   - KPI sheet + case study links accessible.
3. **Contact routing**
   - Primary email/DM handle validated (no `info@` unless no alternative). If enrichment pending, log blocker and hold send.
4. **Snippet finalized**
   - Outreach copy pasted from packet description, personalized per fund.
5. **CRM (or interim tracker) ready**
   - Ensure there is a row for the packet to log status updates (Google Sheet fallback until Postgres live).

## Execution Flow
1. **Send window**
   - Default target: **12:00 CST** for cold or warm email. Adjust if fund prefers other timezone.
2. **Channel-specific steps**
   - **Email:** Use approved sender (Lucas or ops alias). Subject + body derived from packet snippet. Attach deck/KPI or link in-line as agreed.
   - **Warm intro / DM:** Reference mutual contact + attach deck or summary. Log channel as `INTRO` / `SOCIAL`.
3. **Immediately after sending**
   - Add Trello checklist checks:
     - `[x] Approved`
     - `[x] Sent`
     - `[ ] Logged` (will complete once CRM updated).
   - Post Trello comment template (below) including channel, time, and link to sent copy (Gmail “View message” URL or screenshot stored in `/deliverables/outreach_assets/sent_proof/`).
4. **CRM / Tracker update**
   - Fields to capture:
     - `status = SENT`
     - `sent_at` (UTC)
     - `channel`
     - `contact_email`
     - `snippet_version`
     - `next_follow_up_at` (auto Day 3 date)
   - Until the backend is online, append the same data to `deliverables/outreach_assets/sent_log.csv` (create if missing) so we have an audit trail.
5. **Slack acknowledgement**
   - Drop a short note in `#all-fulk-em` once send is logged: `BITKRAFT packet sent at 18:05 UTC via email → waiting on reply.`

## Trello Comment Template (post-send)
```
Sent ✅
- Channel: Email (Lucas → pitch@bitkraft.vc)
- Timestamp: 24 Feb 2026 18:05 UTC
- Assets: deck v2026.02 + KPI snapshot (links inline)
- Proof: https://mail.google.com/... (view message link)
CRM updated → status=SENT, follow_up_due=27 Feb 2026.
```

## Audit Requirements
- Each packet card must maintain:
  - Approval comment + timestamp
  - Send comment + proof link
  - Follow-up comment(s) with outcomes
- The interim `sent_log.csv` (or CRM table) is the source for analytics / weekly reporting until backend API writes are live.

## Escalation / Failure Modes
- **Attachment issues:** Re-send within 15 minutes and log correction comment.
- **Contact bounce:** Update card with bounce details, shift card to **Follow-up** list, trigger enrichment workflow before retrying.
- **Missed send window:** Comment + Slack note explaining slip, reset due date, and prioritize next send.

## Next Automation Steps
1. When FastAPI + Postgres are online, replace CSV log with `packets` + `outreach_attempts` writes via `/api/packets/{id}/send` endpoint.
2. Use Trello Butler to auto-check the `Sent` checklist when a card moves to **Follow-up** after logging.
3. Mirror send events into Slack via webhook for real-time visibility.
