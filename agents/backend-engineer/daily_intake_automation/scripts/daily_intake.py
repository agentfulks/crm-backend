#!/usr/bin/env python3
"""
Daily Intake Automation Script

Creates Trello cards from CRM's top-scored investor entries.
Designed to run as a cron job at 8am daily.

Usage:
    python daily_intake.py [--dry-run] [--limit N] [--json]

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    TRELLO_API_KEY: Trello API key
    TRELLO_TOKEN: Trello API token
    TRELLO_BOARD_ID: Target board ID
    TRELLO_LIST_ID: Target list ID
    LABEL_TYPE_OUTREACH: Outreach label ID
    LABEL_PRIORITY_P1: P1 label ID
    LABEL_WORKSTREAM_INVESTOR: Investor label ID
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
