# Daily Intake Automation

Automated system to create Trello cards from CRM's top-scored investor entries.

## Overview

This Python script runs daily at 8am to:
1. Query CRM for top 5 scored investor entries
2. Create Trello cards using proper template format
3. Assign correct labels (Type: Outreach, Priority: P1, Workstream: Investor)

## Features

- **Idempotent**: Won't create duplicate cards
- **Error Resilient**: Handles API failures and rate limits with exponential backoff
- **Structured Logging**: Comprehensive logging for debugging and monitoring
- **Configurable**: Environment-based configuration
- **Tested**: Unit and integration tests included

## Project Structure

```
daily_intake_automation/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic data models
│   ├── database.py        # CRM database connection
│   ├── trello_client.py   # Trello API client
│   ├── services.py        # Core business logic
│   └── main.py           # Entry point
├── tests/
│   ├── __init__.py
│   ├── test_services.py
│   ├── test_trello_client.py
│   └── test_integration.py
├── scripts/
│   └── daily_intake.py   # CLI script
├── .env.example          # Environment template
├── requirements.txt
├── card_template.json    # Trello card template spec
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Run tests:
```bash
pytest tests/ -v
```

4. Run dry run:
```bash
python scripts/daily_intake.py --dry-run
```

5. Run for real:
```bash
python scripts/daily_intake.py
```

## Scheduling

Add to crontab for 8am daily execution:
```bash
0 8 * * * cd /data/workspace/agents/backend-engineer/daily_intake_automation && /usr/bin/python3 scripts/daily_intake.py >> /var/log/daily_intake.log 2>&1
```

Or use the provided systemd timer (see `cron/` directory).

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `TRELLO_API_KEY` | Trello API key | Yes |
| `TRELLO_TOKEN` | Trello API token | Yes |
| `TRELLO_BOARD_ID` | Target Trello board ID | Yes |
| `TRELLO_LIST_ID` | Target list ID for new cards | Yes |
| `LABEL_TYPE_OUTREACH` | ID for "Type: Outreach" label | Yes |
| `LABEL_PRIORITY_P1` | ID for "Priority: P1" label | Yes |
| `LABEL_WORKSTREAM_INVESTOR` | ID for "Workstream: Investor" label | Yes |
| `LOG_LEVEL` | Logging level (default: INFO) | No |
| `DRY_RUN` | Set to "true" for dry run mode | No |

## Card Template Format

See `card_template.json` for the complete template specification.
