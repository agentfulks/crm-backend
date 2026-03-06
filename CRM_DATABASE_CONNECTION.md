# CRM Database Connection Details

## Status
✅ **Postgres provisioned and migrations applied**

## Connection String
```
DATABASE_URL=postgresql://postgres:HPwqUCIBvdUdwixoCSeowJTlBMqnpgOL@postgres.railway.internal:5432/railway
```

## Connection Parameters
| Parameter | Value |
|-----------|-------|
| Host | postgres.railway.internal |
| Port | 5432 |
| Database | railway |
| User | postgres |
| Provider | Railway |

## Tables
- `contacts` - Investor contacts
- `funds` - VC funds
- `interactions` - Communication history (NEW)
- `meetings` - Scheduled meetings
- `notes` - Contact notes
- `outreach_attempts` - Outreach campaign history
- `packets` - Document packets
- `audit_logs` - Audit trail

## Alembic Migrations
- ✅ 20240224_000001 - Initial CRM schema
- ✅ 702832c52976 - Add interactions table

## Notes
- Database hosted on Railway (managed Postgres)
- Migrations applied using Alembic from `/data/workspace/backend/`
- Connection string already configured in environment
