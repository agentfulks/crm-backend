#!/usr/bin/env python3
"""
Daily Intake Automation for VC Outreach Engine

Reads top 5 scored CRM entries daily and auto-creates "Investor packet" cards 
in the Daily Queue Trello list.

Usage:
    python daily_intake_automation.py [--dry-run] [--limit 5]

Environment Variables:
    MATON_API_KEY - Maton API key for Trello API access
    DATABASE_URL  - PostgreSQL connection string for CRM

Author: VANTAGE
Date: 2026-02-27
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

# Trello Configuration
TRELLO_BOARD_ID = "699d2728fd2ae8c35d1f7a24"
DAILY_QUEUE_LIST_ID = "699d309c1870f04a4b401759"
MATON_GATEWAY_URL = "https://gateway.maton.ai/trello"
MATON_CTRL_URL = "https://ctrl.maton.ai"

# CRM Configuration (Railway Postgres)
DEFAULT_DB_URL = "postgresql://postgres:HPwqUCIBvdUdwixoCSeowJTlBMqnpgOL@postgres.railway.internal:5432/railway"


def get_maton_api_key() -> str:
    """Retrieve Maton API key from environment."""
    key = os.environ.get("MATON_API_KEY")
    if not key:
        raise ValueError("MATON_API_KEY environment variable not set")
    return key


def trello_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Make a request to the Trello API via Maton gateway."""
    api_key = get_maton_api_key()
    
    # Build URL
    url = f"{MATON_GATEWAY_URL}{endpoint}"
    if query_params:
        url = f"{url}?{urlencode(query_params)}"
    
    # Prepare request
    req_data = None
    if data and method in ("POST", "PUT"):
        req_data = json.dumps(data).encode("utf-8")
    elif data and method == "PUT":
        # For PUT with form-like params
        req_data = urlencode(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"Trello API error: {e.code} - {error_body}")


def get_db_connection():
    """Create database connection using psycopg3."""
    import psycopg
    
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
    # Convert SQLAlchemy URL format to psycopg format if needed
    # postgresql:// -> postgresql://
    return psycopg.connect(db_url)


def get_top_scored_funds(limit: int = 5) -> List[Dict[str, Any]]:
    """Query the top N scored funds from the CRM database."""
    conn = get_db_connection()
    
    query = """
    SELECT 
        f.id,
        f.name,
        f.score,
        f.contact_email,
        f.hq_city,
        f.hq_country,
        f.check_size_min,
        f.check_size_max,
        f.check_size_currency,
        f.stage_focus,
        f.overview,
        c.full_name as contact_name,
        c.title as contact_title,
        c.email as contact_email_alt,
        c.linkedin_url as contact_linkedin
    FROM funds f
    LEFT JOIN contacts c ON c.fund_id = f.id AND c.is_primary = true
    WHERE f.score IS NOT NULL
    ORDER BY f.score DESC, f.updated_at DESC
    LIMIT %s
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
            
            funds = []
            for row in rows:
                fund = {
                    "id": row[0],
                    "name": row[1],
                    "score": row[2],
                    "contact_email": row[3],
                    "hq_city": row[4],
                    "hq_country": row[5],
                    "check_size_min": row[6],
                    "check_size_max": row[7],
                    "check_size_currency": row[8],
                    "stage_focus": row[9],
                    "overview": row[10],
                    "contact_name": row[11],
                    "contact_title": row[12],
                    "contact_email_alt": row[13],
                    "contact_linkedin": row[14],
                }
                # Normalize contact email
                fund["primary_email"] = fund.get("contact_email") or fund.get("contact_email_alt")
                funds.append(fund)
        
        return funds
    finally:
        conn.close()


def format_card_description(fund: Dict[str, Any], day_batch: int) -> str:
    """Format the Trello card description for an investor packet."""
    
    # Format check size
    check_size = "Unknown"
    if fund.get("check_size_min") and fund.get("check_size_max"):
        currency = fund.get("check_size_currency", "USD")
        min_val = float(fund["check_size_min"])
        max_val = float(fund["check_size_max"])
        
        # Format nicely (e.g., $200K-$5M)
        def fmt_amount(val: float) -> str:
            if val >= 1_000_000:
                return f"${val/1_000_000:.1f}M".replace(".0M", "M")
            elif val >= 1_000:
                return f"${val/1_000:.0f}K"
            return f"${val:.0f}"
        
        check_size = f"{fmt_amount(min_val)}-{fmt_amount(max_val)}"
    
    # Format stage focus
    stage_focus = fund.get("stage_focus", []) or []
    stage_str = ", ".join(stage_focus) if stage_focus else "Unknown"
    
    # Format location
    location_parts = [p for p in [fund.get("hq_city"), fund.get("hq_country")] if p]
    location = ", ".join(location_parts) if location_parts else "Unknown"
    
    # Format contact info
    contact_name = fund.get("contact_name") or "Unknown"
    contact_title = fund.get("contact_title") or ""
    contact_display = f"{contact_name}, {contact_title}" if contact_title else contact_name
    
    score = fund.get("score", 0) or 0
    
    desc = f"""## Snapshot
- **Fund:** {fund.get('name', 'Unknown')}
- **Contact:** {contact_display}
- **Email:** {fund.get('primary_email') or 'Not available'}
- **Check Size:** {check_size}
- **Stage:** {stage_str}
- **Location:** {location}
- **Fit Score:** {score:.1f}/100

## Overview
{fund.get('overview') or 'No overview available.'}

## Status
- **Batch:** Day {day_batch}
- **Created:** {datetime.now().strftime('%Y-%m-%d')}
- **CRM ID:** {fund.get('id')}
- **Ready for Review:** ✅

---
*Auto-generated by Daily Intake Automation*
"""
    return desc


def format_card_name(fund: Dict[str, Any], day_batch: int) -> str:
    """Format the Trello card name."""
    contact_name = fund.get("contact_name") or "Unknown Contact"
    fund_name = fund.get("name", "Unknown Fund")
    return f"[Day {day_batch}] {fund_name} - {contact_name}"


def card_exists_for_fund(fund_id: str, list_id: str) -> bool:
    """Check if a card already exists for this fund in the target list."""
    try:
        # Get cards in the list
        cards = trello_request(f"/1/lists/{list_id}/cards")
        for card in cards:
            desc = card.get("desc", "")
            if f"**CRM ID:** {fund_id}" in desc:
                return True
        return False
    except Exception as e:
        print(f"Warning: Could not check for existing card: {e}")
        return False


def create_investor_packet_card(
    fund: Dict[str, Any],
    list_id: str,
    day_batch: int,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """Create a Trello card for an investor packet."""
    
    # Check for duplicates
    if card_exists_for_fund(fund.get("id"), list_id):
        print(f"  ⏭️  Skipping {fund.get('name')} - card already exists")
        return None
    
    card_name = format_card_name(fund, day_batch)
    card_desc = format_card_description(fund, day_batch)
    
    if dry_run:
        print(f"  📝 DRY RUN: Would create card:")
        print(f"     Name: {card_name}")
        print(f"     Fund: {fund.get('name')}")
        print(f"     Score: {fund.get('score')}")
        return {"name": card_name, "dry_run": True}
    
    # Create the card
    card_data = {
        "name": card_name,
        "desc": card_desc,
        "idList": list_id,
    }
    
    result = trello_request("/1/cards", method="POST", data=card_data)
    print(f"  ✅ Created: {card_name}")
    return result


def run_daily_intake(
    limit: int = 5,
    dry_run: bool = False,
    day_batch: int = 1,
) -> List[Dict[str, Any]]:
    """Run the daily intake automation."""
    
    print(f"\n{'='*60}")
    print("DAILY INTAKE AUTOMATION")
    print(f"{'='*60}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Limit: {limit} funds")
    print(f"Target List: Daily Queue ({DAILY_QUEUE_LIST_ID})")
    print(f"{'='*60}\n")
    
    # Step 1: Query top scored funds
    print("📊 Querying CRM for top scored funds...")
    try:
        funds = get_top_scored_funds(limit)
        print(f"   Found {len(funds)} funds\n")
    except Exception as e:
        print(f"   ❌ Error querying CRM: {e}")
        return []
    
    if not funds:
        print("   ⚠️  No funds found with scores")
        return []
    
    # Step 2: Create Trello cards
    print("🎯 Creating Trello cards in Daily Queue...")
    created_cards = []
    for fund in funds:
        try:
            card = create_investor_packet_card(fund, DAILY_QUEUE_LIST_ID, day_batch, dry_run)
            if card:
                created_cards.append({
                    "fund_name": fund.get("name"),
                    "fund_id": fund.get("id"),
                    "score": fund.get("score"),
                    "card": card,
                })
        except Exception as e:
            print(f"   ❌ Error creating card for {fund.get('name')}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total funds processed: {len(funds)}")
    print(f"Cards created: {len(created_cards)}")
    print(f"{'='*60}\n")
    
    return created_cards


def main():
    parser = argparse.ArgumentParser(
        description="Daily Intake Automation for VC Outreach Engine"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without creating actual cards",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        dest="test_mode",
        help="Alias for --dry-run. Simulates card creation without API calls",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of top-scored funds to process (default: 5)",
    )
    parser.add_argument(
        "--day-batch",
        type=int,
        default=1,
        help="Day batch number for card naming (default: 1)",
    )
    
    args = parser.parse_args()
    
    # Test mode is alias for dry-run
    is_simulation = args.dry_run or args.test_mode
    
    # Validate environment (skip in test mode)
    if not is_simulation:
        try:
            get_maton_api_key()
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)
    
    # Run automation
    try:
        results = run_daily_intake(
            limit=args.limit,
            dry_run=is_simulation,
            day_batch=args.day_batch,
        )
        
        if results:
            print("✅ Automation completed successfully")
            sys.exit(0)
        else:
            print("⚠️  No cards created")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
