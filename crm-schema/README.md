# VC Outreach CRM - PostgreSQL Schema

## Overview

PostgreSQL database schema for tracking VC firms, contacts, outreach attempts, and notes.

## Quick Start

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

This starts:
- PostgreSQL 16 on port 5432
- Adminer (DB UI) on port 8080

### 2. Connection Details

```
Host: localhost
Port: 5432
Database: vc_outreach
Username: crm
Password: crm_secret_password
```

Environment variables (create `.env` file to override):
- `POSTGRES_USER` (default: crm)
- `POSTGRES_PASSWORD` (default: crm_secret_password)
- `POSTGRES_DB` (default: vc_outreach)
- `POSTGRES_PORT` (default: 5432)
- `ADMINER_PORT` (default: 8080)

### 3. Running Migrations

**Option A: Auto-run on container start**
Place migration files in `./migrations/` folder - they execute automatically when the container starts.

```bash
mkdir -p migrations
cp V1__initial_schema.sql migrations/
docker-compose restart postgres
```

**Option B: Manual execution**

```bash
# Connect to database
docker exec -it vc-crm-postgres psql -U crm -d vc_outreach

# Or run SQL file directly
docker exec -i vc-crm-postgres psql -U crm -d vc_outreach < V1__initial_schema.sql
```

**Option C: Using psql from host (if installed)**

```bash
psql -h localhost -U crm -d vc_outreach -f V1__initial_schema.sql
```

### 4. Access Adminer (Database UI)

Open http://localhost:8080
- System: PostgreSQL
- Server: postgres
- Username: crm
- Password: crm_secret_password
- Database: vc_outreach

## Schema Overview

### Tables

| Table | Purpose |
|-------|---------|
| `firms` | VC firms and investment entities |
| `contacts` | People associated with firms |
| `outreach_attempts` | Outreach activities and outcomes |
| `notes` | Free-form notes about firms |

### Relationships

- `contacts.firm_id` → `firms.id` (many-to-one)
- `outreach_attempts.firm_id` → `firms.id` (many-to-one)
- `outreach_attempts.contact_id` → `contacts.id` (many-to-one, nullable)
- `notes.firm_id` → `firms.id` (many-to-one)

## Migration Files

| File | Description |
|------|-------------|
| `V1__initial_schema.sql` | Initial schema with all tables, indexes, and triggers |

## Stopping / Cleanup

```bash
# Stop containers
docker-compose down

# Stop and remove all data (WARNING: destroys database)
docker-compose down -v
```

## Production Considerations

1. **Security**: Change default passwords in production
2. **Backups**: Implement automated backup strategy
3. **SSL**: Enable SSL for production connections
4. **Migrations**: Use proper migration tool (Flyway, Liquibase) for production
