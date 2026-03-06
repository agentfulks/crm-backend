# Source Automation v1 — Planning Brief (24 Feb 2026)

## A) Objective
- **Goal:** Automate ingestion of high-fit gaming/AI/devtools investor records so the CRM receives ≥20 fresh, fully qualified entries every day.
- **Success Criteria:**
  - Daily job ingests/de-dupes ≥20 funds that meet Priority A/B score thresholds.
  - Each record includes partner name, direct email, stage/check ranges, geo, and thesis keywords.
  - Pipeline writes into Postgres `funds` + `contacts` tables (or interim CSV) with QA sample logged.

## B) Assumptions & Constraints
- **Assumptions:**
  - `data/raw/gaming_vc_list.csv` remains the master seed list until web/API integrations go live.
  - Remote Postgres credentials will be available once Neon/Supabase instance is provisioned.
  - Outreach team can tolerate <24h latency between ingestion and Trello packet generation.
- **Constraints:**
  - No local Docker; scripts must run in OpenClaw or GitHub Actions.
  - Some sources (Crunchbase, PitchBook) require API keys—fallback to public datasets + manual enrichment until keys provided.
  - Need idempotent runs—no duplicate Trello cards or CRM rows.

## C) Approach Options
1. **CSV-first ETL (Recommended)**
   - Use existing `rank_funds.py` parsing utilities to normalize CSV daily, push deltas into CRM.
   - Pros: Uses current data, minimal external dependencies, fast to ship.
   - Cons: Limited freshness; depends on manual CSV refresh.
2. **Scraper Layer + CSV Merge**
   - Augment CSV with lightweight scrapers (LinkedIn, firm sites) for contact enrichment before insert.
   - Pros: Improves completeness; semi-automated enrichment.
   - Cons: Requires HTML parsing + anti-bot handling; higher maintenance.
3. **API Aggregator Integration**
   - Connect to Crunchbase/F6S APIs, stream new funds nightly.
   - Pros: Real-time data, less manual curation.
   - Cons: Needs API access + auth, slower to stand up.

**Recommendation:** Ship CSV-first ETL immediately, stub hooks for enrichment so we can layer scrapers/API sources later without rework.

## D) Execution Plan
- **Phase 1 — Data Pipeline Skeleton (Day 0)
  - Task 1: Extend `rank_funds.py` utilities into `scripts/ingest_funds.py` with CLI for `--limit` + `--output`.
  - Task 2: Add normalization helpers (stage mapping, geo ISO codes, check size parsing).
  - Task 3: Write ingestion manifest (JSONL) for QA + incremental diffing.
- **Phase 2 — CRM Write Path (blocked on DB)
  - Task 4: Implement repository layer (`app/services/ingestion_service.py`) to upsert funds + contacts via SQLAlchemy session.
  - Task 5: Create Alembic migration for `contacts` if pending; ensure indexes on `funds.name`, `contacts.email`.
  - Task 6: Build CLI entry point `uv run python scripts/ingest_funds.py --commit` that reads manifest and writes to DB.
- **Phase 3 — Scheduling & QA
  - Task 7: Add GitHub Action (or cron) that runs daily at 09:00 CST, stores artifacts in `deliverables/daily_queue/YYYY-MM-DD.json`.
  - Task 8: Implement QA sample—random 20 entries logged to `/deliverables/source_automation/qa/YYYY-MM-DD.md` with verification checklist.
  - Task 9: Post summary to Slack (#all-fulk-em) after each run (count of new/updated funds, errors).

**Dependencies:** Remote Postgres credentials (Phase 2), Slack webhook (Phase 3).
**Parallel Work:** Phase 1 can run immediately while infra team provisions database.

## E) Trello Board Blueprint
**Board Name:** VC Outreach Engine (existing)

**List: Pipeline Build**
- **Card:** Source automation v1 *(existing card)*
  - **Description:** Build CSV → CRM ingestion job delivering ≥20 qualified funds/day, with QA + Slack summary.
  - **Checklist:**
    - [ ] Script parses & normalizes CSV
    - [ ] Upsert writes to CRM tables
    - [ ] Daily schedule + Slack summary
    - [ ] QA sample logged
  - **Labels:** Outreach · P1 · Effort L · Workstream BDR
  - **Owner:** Research Ops / Backend pairing
  - **Definition of Done:** Automated run populates CRM + QA log with zero critical errors for 3 consecutive days.
  - **Dependencies:** Postgres credentials, Slack webhook, contact enrichment workflow.

If granularity is needed, split into two cards: **“Ingestion CLI + manifest”** and **“Daily scheduler + QA”** with the same DoD.

## F) Risks & Mitigations
- **Risk:** Remote DB not provisioned → ingestion blocked.
  - **Mitigation:** Implement interim CSV → JSONL drop + manual Trello upload; document blocker for infra.
- **Risk:** Source CSV stale / missing contacts.
  - **Mitigation:** Add freshness column + fall back to enrichment workflow for missing contact emails.
- **Risk:** Duplicate or malformed entries clog Trello.
  - **Mitigation:** Use deterministic hash (fund name + hq_country) to skip duplicates; include validation step before writing.

## G) Next 3 Actions
1. Scaffold `scripts/ingest_funds.py` using existing parsing helpers; output normalized JSONL + summary table.
2. Define SQLAlchemy repositories + DTOs for `funds` + `contacts` upserts (safe even before DB credentials).
3. Draft GitHub Action YAML (disabled) so it’s ready to point at real credentials once infra is live.
