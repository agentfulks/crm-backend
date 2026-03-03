# CRM Backend Bootstrap

Backend scaffold providing the CRM data layer for gaming VC outreach.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker + docker compose

## Setup

1. Copy configuration:
   ```bash
   cp ../.env.example ../.env
   ```
2. **Provide a reachable Postgres instance.** Local Docker is unavailable inside OpenClaw, so point `DATABASE_URL` at a hosted database (Neon/Supabase/Railway). See `docs/infra/postgres-deployment.md` for provisioning steps.
3. Install dependencies via uv:
   ```bash
   cd backend
   uv sync
   ```
4. Run migrations:
   ```bash
   uv run alembic upgrade head
   ```
5. Seed funds from CSV:
   ```bash
   uv run python scripts/seed_funds.py
   ```
6. Sanity check connectivity any time credentials change:
   ```bash
   uv run python scripts/test_db_connection.py
   ```

Adminer instructions apply only when Docker is available locally.
