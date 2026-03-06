# Contact Enrichment Workflow

_Last updated: 24 Feb 2026 23:40 UTC_

## Objective
Give every Priority A/B fund a validated human contact (partner/associate name + direct email), thesis snippet, and verification log so the CRM `contacts` table and Trello packets stay approval-ready.

Success criteria:
- ≥90% of Priority A/B funds have at least one named partner with a deliverability-tested email address.
- Each contact record stores: fund_id, contact_id, name, title, email, source URL, verification status, thesis/context snippet, last verified timestamp.
- Daily packet generation can pull a `primary_contact_id` without manual lookup.

## Tooling Decisions
| Need | Decision | Notes |
| --- | --- | --- |
| Official firm inbox | Scrape/parse fund websites + manifest metadata | Already captured for today’s top 5 (see `/deliverables/contact_enrichment/2026-02-24-top5.csv`). |
| Partner names + role context | Use website "Team" pages + Crunchbase/LinkedIn exports (manual for now) | Add `data/reference/partners_manual.csv` until automated sources available. |
| Direct partner emails | Request Maton API connections for **Apollo** and **People Data Labs** (preferred) or Hunter.io (backup). | Need Lucas to confirm which provider we can authorize; placeholder environment vars documented below. |
| Deliverability check | Standardize on **NeverBounce** (API) once key is shared; interim: `smtp-is-valid` Python lib for syntax/SMTP ping. | Wrap in `verify_email(address)` helper so provider swap is trivial. |
| Context snippets | Leverage existing `rank_funds` thesis fields + manual notes; store in `contacts.context` JSONB later. |

## Data Flow
1. **Input sources**
   - `deliverables/daily_queue/YYYY-MM-DD-manifest.json` (top scored funds)
   - `data/raw/gaming_vc_list.csv` (for additional metadata)
   - `deliverables/contact_enrichment/manual_overrides.csv` (hand-curated partner emails, LinkedIn URLs)
2. **Enrichment script** (to be added under `backend/scripts/enrich_contacts.py`):
   - Load manifest, hydrate baseline fields (official inbox, domain, HQ, thesis snippet).
   - Join manual overrides; if no direct email, flag `needs_enrichment=1`.
   - Optional: call Apollo/Hunter APIs (once keys available) to fetch partner emails by domain/title.
   - Append verification results (`deliverability_status`, `verified_at_utc`).
   - Write CSV/JSONL with schema below + drop into `deliverables/contact_enrichment/DATE-contacts.csv`.
3. **Outputs**
   - CSV with columns: `fund_name, priority, contact_name, title, email, source_url, verification_status, verification_method, notes`.
   - Markdown log summarizing coverage (% with partner email, % pending).
   - Future: direct insert into `contacts` table once Postgres is reachable.

## Verification Plan
1. Syntax + MX check (Python `validate-email-address==1.0.5`).
2. SMTP ping via NeverBounce (requires API key) or fallback CLI (`smtp-cli`).
3. Store result codes (`valid`, `accept-all`, `unknown`, `invalid`).
4. Re-check every 30 days (scheduled GitHub Action once DB live).

## Latest Run (24 Feb 2026)
- Script: `backend/scripts/enrich_contacts.py` (run via `python3 scripts/enrich_contacts.py`).
- Outputs: `/deliverables/contact_enrichment/2026-02-24-contacts.csv` + `/deliverables/contact_enrichment/2026-02-24-summary.md`.
- Coverage: 0/5 direct partner contacts (all five funds still need enrichment beyond general inboxes).
- Next step: populate `manual_overrides.csv` with validated partner names/emails so reruns graduate funds into `direct_partner` status.

## Immediate Next Actions
1. **Expand manual overrides** for today’s five funds (partners + emails from credibility sources) and rerun script to validate coverage uplift.
2. **Request API access** for Apollo (people enrichment) + NeverBounce (deliverability) via Maton connections.
3. **Integrate SMTP/verification step** once API keys arrive (hook into `enrich_contacts.py`).
4. **Backfill context notes**: capture thesis keywords + latest signal per contact so packets can auto-personalize.

## Blockers / Requests
- Need Lukas to provision or share credentials for a hosted Postgres instance before we can persist contacts server-side.
- Need approval to connect Maton API Gateway to the chosen enrichment + verification providers (Apollo/People Data Labs + NeverBounce/Hunter).
- Missing outreach assets (deck, KPI XLS) still keep packets from hitting “Awaiting Approval”; flagged separately on the Trello "Outreach asset inventory" card.

See `/deliverables/contact_enrichment/2026-02-24-contacts.csv` + summary for the current coverage snapshot.
