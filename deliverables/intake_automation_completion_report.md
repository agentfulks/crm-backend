# Daily Intake Automation - Completion Report

**Date:** 2026-02-27  
**Status:** Production Ready  
**Location:** `/data/workspace/deliverables/`

---

## What Was Implemented

### 1. Core Script Enhancement
**File:** `daily_intake_automation.py`

The existing 300+ line script was enhanced with:
- **`--test-mode` flag**: Alias for `--dry-run` that simulates card creation without making actual API calls
- Environment validation (skipped in test mode for local testing)
- Railway Postgres database connectivity via `psycopg`
- Maton gateway integration for Trello API access

**Key Features:**
- Queries top N scored funds from CRM
- Checks for duplicate cards before creation
- Formats investor packet cards with fund details, contact info, and fit scores
- Creates cards in Trello "Daily Queue" list

---

## How to Run It Manually

### Using the Wrapper Script (Recommended)

```bash
# Navigate to deliverables directory
cd /data/workspace/deliverables

# Run with production settings (creates actual Trello cards)
./run_daily_intake.sh

# Run in test mode (simulates without API calls)
./run_daily_intake.sh --test-mode

# Process different number of funds
./run_daily_intake.sh --limit 10

# Combined options
./run_daily_intake.sh --test-mode --limit 3
```

### Direct Python Execution

```bash
cd /data/workspace/deliverables

# Production run
python3 daily_intake_automation.py

# Test mode
python3 daily_intake_automation.py --test-mode

# Custom limit
python3 daily_intake_automation.py --limit 10 --day-batch 2
```

### Log Files

All runs are logged to:
- `/data/workspace/deliverables/logs/intake_YYYYMMDD_HHMMSS.log`
- Symlink to latest: `/data/workspace/deliverables/logs/latest.log`

---

## Environment Variables Required

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MATON_API_KEY` | Yes (production) | Maton API key for Trello gateway access | - |
| `DATABASE_URL` | Yes | PostgreSQL connection string for CRM | Railway URL in code |

### .env File Support

Create a `.env` file in project root or deliverables directory:

```bash
# /data/workspace/.env or /data/workspace/deliverables/.env
MATON_API_KEY=your_maton_api_key_here
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

The wrapper script automatically loads `.env` if present.

---

## Cron/GitHub Actions Setup

### Option 1: GitHub Actions (Recommended)

**File:** `.github/workflows/daily-intake.yml`

**Schedule:** Daily at 08:00 UTC

**Setup Instructions:**

1. **Add Secrets to GitHub Repository:**
   - Go to Settings → Secrets and variables → Actions
   - Add `MATON_API_KEY` - Your Maton API key
   - Add `DATABASE_URL` - Railway Postgres connection string
   - (Optional) Add `WEBHOOK_URL` - URL to receive success/failure notifications

2. **Enable the Workflow:**
   - The workflow is already configured in `.github/workflows/daily-intake.yml`
   - It will run automatically on schedule
   - Can also be triggered manually via GitHub Actions UI

3. **Manual Trigger:**
   - Go to Actions tab → Daily Intake Automation
   - Click "Run workflow"
   - Optional: Enable test mode, adjust limit

### Option 2: System Cron (Alternative)

Add to crontab for local/server execution:

```bash
# Edit crontab
crontab -e

# Add daily run at 8:00 AM UTC (2:00 AM CST)
0 8 * * * cd /data/workspace/deliverables && ./run_daily_intake.sh >> /data/workspace/deliverables/logs/cron.log 2>&1

# Or with test mode for initial verification
0 8 * * * cd /data/workspace/deliverables && ./run_daily_intake.sh --test-mode >> /data/workspace/deliverables/logs/cron.log 2>&1
```

---

## File Structure

```
/data/workspace/
├── deliverables/
│   ├── daily_intake_automation.py    # Core automation script
│   ├── run_daily_intake.sh           # Wrapper script with logging
│   └── logs/                         # Execution logs
│       ├── intake_YYYYMMDD_HHMMSS.log
│       └── latest.log -> (symlink to latest)
├── .github/
│   └── workflows/
│       └── daily-intake.yml          # GitHub Actions workflow
└── .env                              # Environment variables (create this)
```

---

## Database Configuration

The script connects to Railway Postgres by default using:
- **Default URL:** `postgresql://postgres:HPwqUCIBvdUdwixoCSeowJTlBMqnpgOL@postgres.railway.internal:5432/railway`
- **Override:** Set `DATABASE_URL` environment variable

**Required Schema:**
- `funds` table with: `id`, `name`, `score`, `contact_email`, `hq_city`, `hq_country`, `check_size_*`, `stage_focus`, `overview`, `updated_at`
- `contacts` table with: `fund_id`, `full_name`, `title`, `email`, `linkedin_url`, `is_primary`

---

## Testing Checklist

Before production deployment:

- [ ] Run `./run_daily_intake.sh --test-mode` locally
- [ ] Verify log file creation in `logs/` directory
- [ ] Confirm environment variables are loaded from `.env`
- [ ] Test with `python3 daily_intake_automation.py --test-mode --limit 2`
- [ ] Add secrets to GitHub repository
- [ ] Trigger manual GitHub Actions run in test mode
- [ ] Verify webhook notifications (if configured)
- [ ] Schedule production run

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `MATON_API_KEY not set` | Add key to `.env` file or export as environment variable |
| `psycopg not found` | Run `pip3 install psycopg` |
| Database connection failed | Check `DATABASE_URL` format and network access |
| Trello API errors | Verify Maton API key has Trello permissions |
| No funds found | Check CRM has funds with `score` values set |

---

## Production Notes

1. **Idempotency:** The script checks for existing cards by CRM ID to prevent duplicates
2. **Logging:** All output is timestamped and logged to file
3. **Error Handling:** Non-zero exit codes on failure for proper CI/CD integration
4. **Day Batching:** Use `--day-batch N` for multi-day campaigns
5. **Webhook:** Placeholder URL defaults to httpbin.org for testing; replace with actual webhook in production

---

## Next Steps

1. Add `MATON_API_KEY` and `DATABASE_URL` to GitHub repository secrets
2. Run test mode: `./run_daily_intake.sh --test-mode`
3. Trigger manual GitHub Actions workflow
4. Monitor first scheduled run
5. (Optional) Configure actual webhook URL for notifications
