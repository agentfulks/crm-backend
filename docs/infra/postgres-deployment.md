# Postgres Deployment Plan

Last updated: 2026-02-24 08:40 UTC

## Objective
Provide a hosted Postgres instance that the CRM backend can reach from Github Codespaces / OpenClaw (no local Docker). The database must stay online 24/7 for ingestion scripts, FastAPI services, and Trello automation hooks.

## Recommended Hosting Options

| Option | Why | Est. Setup Time | Notes |
| --- | --- | --- | --- |
| **Neon Serverless (Free tier)** | Native serverless Postgres, password auth, per-branch endpoints. Easy to rotate credentials and pause when idle. | 5–7 minutes | Create project → set password → grab pooled connection string → whitelist 0.0.0.0/0 (they allow by default). |
| **Supabase** | Managed Postgres + dashboard, row-level security if needed later. | 10 minutes | Requires project + password; need to disable RLS for CRM tables initially. |
| **Railway** | Simple CLI + per-service secrets. | 10 minutes | Need to keep project awake (paid tier after 500 hours). |

Any of these produce a standard Postgres URI we can drop into `.env`.

## Required Credentials
Capture the following and add them to `1Password → Infra → VC Outreach CRM` (or share securely):

- Hostname
- Port (usually 5432)
- Database name (e.g., `crm`)
- Username (e.g., `svc_crm`)
- Password
- Full SQLAlchemy URL (`postgresql+psycopg://user:pass@host:port/db`)

## Provisioning Steps (Neon Example)
1. Create a Neon project named `vc-outreach-crm`.
2. In the default branch/database, run:
   ```sql
   CREATE ROLE svc_crm LOGIN PASSWORD '<strong-random-password>';
   CREATE DATABASE crm OWNER svc_crm;
   GRANT ALL PRIVILEGES ON DATABASE crm TO svc_crm;
   ```
3. Under Settings → Connection Strings, copy the pooled connection string, replace the user/password with `svc_crm` credentials, and store in `1Password`.
4. In the repo root, duplicate `.env.example` → `.env` and replace `DATABASE_URL` with the provided Neon URL.
5. From `/data/workspace/backend`, run:
   ```bash
   uv sync
   uv run alembic upgrade head
   uv run python scripts/seed_funds.py
   ```
   (The commands succeed once the remote DB is reachable.)

## Operational Notes
- Local Docker is unavailable in this sandbox; everything must point to a remote DB.
- Alembic already has an initial migration (`20240224_000001_initial_schema.py`). Running `alembic upgrade head` will create schema + enums automatically.
- The seeding script idempotently upserts funds from `data/raw/gaming_vc_list.csv`. Running it multiple times is safe.
- Until credentials are supplied, cards dependent on live Postgres remain blocked.

## Next Actions
1. Lucas (or infra owner) provision Neon/Supabase instance and share connection string.
2. Update `.env` with the remote `DATABASE_URL` (keep file out of git).
3. Run migrations + seed script using `uv run ...` commands above.
4. Confirm connectivity via `uv run python scripts/test_db_connection.py` (script described below).
5. Once confirmed, move Trello checklist items "Provision Postgres + credentials" and "Document connection details" to complete.

## Validation Script (new)
Create `backend/scripts/test_db_connection.py` with:
```python
from sqlalchemy import text
from app.db.session import SessionLocal

session = SessionLocal()
try:
    session.execute(text("SELECT 1"))
    print("Database connection OK")
finally:
    session.close()
```
Run `uv run python scripts/test_db_connection.py` to verify credentials any time they change.
