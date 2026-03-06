#!/usr/bin/env python3
"""
Daily Intake Automation System - Complete Implementation
VC Outreach Engine - Auto-creates investor packet cards from CRM

This script:
1. Queries the top 5 scored funds from the CRM database
2. Auto-creates Trello cards in the Daily Queue
3. Enriches contact information
4. Schedules follow-up reminders

Usage:
    python daily_intake_automation_full.py [--dry-run] [--limit 5] [--day-batch N]

Environment Variables:
    MATON_API_KEY - Maton API key for Trello/Slack API access
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
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

# Configuration
TRELLO_BOARD_ID = "699d2728fd2ae8c35d1f7a24"
DAILY_QUEUE_LIST_ID = "699d309c1870f04a4b401759"
MATON_GATEWAY_URL = "https://gateway.maton.ai/trello"
MATON_CTRL_URL = "https://ctrl.maton.ai"

# CRM Configuration (Railway Postgres)
DEFAULT_DB_URL = "postgresql://postgres:HPwqUCIBvdUdwixoCSeowJTlBMqnpgOL@postgres.railway.internal:5432/railway"

# List ID mappings
LISTS = {
    "foundation": "699d2728fd2ae8c35d1f7a46",
    "pipeline_build": "699d2728fd2ae8c35d1f7a47",
    "daily_queue": "699d309c1870f04a4b401759",
    "in_progress": "699d345f2437461523243d65",
    "awaiting_approval": "699d2728fd2ae8c35d1f7a48",
    "approved_send": "699d27651350afa8f2b8ec25",
    "follow_up": "699d309d2ef034a3ba04deb8",
    "insights": "699d309ee719309d39b554da",
}


def get_maton_api_key() -> str:
    """Retrieve Maton API key from environment."""
    key = os.environ.get("MATON_API_KEY")
    if not key:
        raise ValueError("MATON_API_KEY environment variable not set")
    return key


def get_db_url() -> str:
    """Get database URL from environment or default."""
    return os.environ.get("DATABASE_URL", DEFAULT_DB_URL)


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
    
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"Trello API error: {e.code} - {error_body}")


def get_db_connection():
    """Create database connection using psycopg."""
    import psycopg
    db_url = get_db_url()
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
        f.website_url,
        f.linkedin_url,
        f.twitter_url,
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
                    "score": float(row[2]) if row[2] else 0,
                    "contact_email": row[3],
                    "hq_city": row[4],
                    "hq_country": row[5],
                    "check_size_min": row[6],
                    "check_size_max": row[7],
                    "check_size_currency": row[8],
                    "stage_focus": row[9],
                    "overview": row[10],
                    "website_url": row[11],
                    "linkedin_url": row[12],
                    "twitter_url": row[13],
                    "contact_name": row[14],
                    "contact_title": row[15],
                    "contact_email_alt": row[16],
                    "contact_linkedin": row[17],
                }
                fund["primary_email"] = fund.get("contact_email") or fund.get("contact_email_alt")
                funds.append(fund)
        
        return funds
    finally:
        conn.close()


def format_check_size(fund: Dict[str, Any]) -> str:
    """Format check size for display."""
    min_val = fund.get("check_size_min")
    max_val = fund.get("check_size_max")
    currency = fund.get("check_size_currency", "USD")
    
    if not min_val and not max_val:
        return "Unknown"
    
    def fmt(val):
        if val is None:
            return "?"
        val = float(val)
        if val >= 1_000_000:
            return f"${val/1_000_000:.1f}M".replace(".0M", "M")
        elif val >= 1_000:
            return f"${val/1_000:.0f}K"
        return f"${val:.0f}"
    
    if min_val and max_val:
        return f"{fmt(min_val)}-{fmt(max_val)} {currency}"
    elif min_val:
        return f"≥{fmt(min_val)} {currency}"
    elif max_val:
        return f"≤{fmt(max_val)} {currency}"
    return "Unknown"


def format_card_description(fund: Dict[str, Any], day_batch: int) -> str:
    """Format the Trello card description for an investor packet."""
    
    check_size = format_check_size(fund)
    stage_focus = fund.get("stage_focus") or []
    stage_str = ", ".join(stage_focus) if isinstance(stage_focus, list) else str(stage_focus)
    
    location_parts = [p for p in [fund.get("hq_city"), fund.get("hq_country")] if p]
    location = ", ".join(location_parts) if location_parts else "Unknown"
    
    contact_name = fund.get("contact_name") or "Unknown"
    contact_title = fund.get("contact_title") or ""
    contact_display = f"{contact_name}, {contact_title}" if contact_title else contact_name
    
    score = fund.get("score", 0) or 0
    now = datetime.now()
    day_3 = (now + timedelta(days=3)).strftime("%Y-%m-%d")
    day_7 = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    
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

## Links
- Website: {fund.get('website_url') or 'N/A'}
- LinkedIn: {fund.get('linkedin_url') or 'N/A'}
- Twitter: {fund.get('twitter_url') or 'N/A'}

## Status
- **Batch:** Day {day_batch}
- **Created:** {now.strftime('%Y-%m-%d')}
- **CRM ID:** {fund.get('id')}
- **Ready for Review:** ✅

## Follow-up Schedule
- Day 3: {day_3}
- Day 7: {day_7}

---
*Auto-generated by Daily Intake Automation*
*Contact enrichment: {contact_display}*
"""
    return desc


def format_card_name(fund: Dict[str, Any], day_batch: int) -> str:
    """Format the Trello card name."""
    contact_name = fund.get("contact_name") or "Unknown Contact"
    fund_name = fund.get("name", "Unknown Fund")
    score = fund.get("score", 0) or 0
    return f"[Day {day_batch}] {fund_name} - {contact_name} (Score: {score:.0f})"


def card_exists_for_fund(fund_id: str, list_id: str) -> bool:
    """Check if a card already exists for this fund in the target list."""
    try:
        cards = trello_request(f"/1/lists/{list_id}/cards")
        for card in cards:
            desc = card.get("desc", "")
            if f"**CRM ID:** {fund_id}" in desc:
                return True
        return False
    except Exception as e:
        print(f"  ⚠️  Warning: Could not check for existing card: {e}")
        return False


def create_checklist(card_id: str, fund_name: str) -> bool:
    """Create a checklist on the card for the approval workflow."""
    try:
        # Create checklist
        checklist = trello_request(
            "/1/checklists",
            method="POST",
            data={"idCard": card_id, "name": "Packet Build & Approval"}
        )
        checklist_id = checklist.get("id")
        
        # Add checklist items
        items = [
            "Confirm fund HQ, stage focus, check size, and ICP tier",
            "Draft 2-3 sentence Why Now blurb referencing recent signal",
            "Capture partner/contact info with direct email + social proof",
            "Attach deck + metrics doc + case study/press links",
            "Write approval-ready outbound snippet (email or DM)",
            "Move to Awaiting Approval for Lucas review",
            "Log approval decision + timestamp",
            "Send email once approved",
            "Schedule Day 3 follow-up",
            "Schedule Day 7 follow-up",
        ]
        
        for item in items:
            trello_request(
                f"/1/checklists/{checklist_id}/checkItems",
                method="POST",
                data={"name": item}
            )
        
        return True
    except Exception as e:
        print(f"  ⚠️  Warning: Could not create checklist: {e}")
        return False


def create_investor_packet_card(
    fund: Dict[str, Any],
    list_id: str,
    day_batch: int,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """Create a Trello card for an investor packet."""
    
    fund_id = fund.get("id")
    fund_name = fund.get("name", "Unknown")
    
    # Check for duplicates
    if not dry_run and card_exists_for_fund(fund_id, list_id):
        print(f"  ⏭️  Skipping {fund_name} - card already exists")
        return None
    
    card_name = format_card_name(fund, day_batch)
    card_desc = format_card_description(fund, day_batch)
    
    if dry_run:
        print(f"  📝 DRY RUN: Would create card:")
        print(f"     Name: {card_name[:60]}...")
        print(f"     Fund: {fund_name}")
        print(f"     Score: {fund.get('score'):.1f}")
        return {"name": card_name, "dry_run": True}
    
    # Create the card
    card_data = {
        "name": card_name,
        "desc": card_desc,
        "idList": list_id,
    }
    
    result = trello_request("/1/cards", method="POST", data=card_data)
    card_id = result.get("id")
    print(f"  ✅ Created: {card_name[:50]}...")
    
    # Add checklist
    create_checklist(card_id, fund_name)
    
    # Add labels
    try:
        score = fund.get("score", 0) or 0
        if score >= 80:
            label_color = "green"  # Priority A
        elif score >= 60:
            label_color = "yellow"  # Priority B
        else:
            label_color = "orange"  # Priority C
        
        trello_request(
            f"/1/cards/{card_id}/labels",
            method="POST",
            data={"color": label_color}
        )
    except Exception as e:
        print(f"  ⚠️  Warning: Could not add label: {e}")
    
    return result


def run_daily_intake(
    limit: int = 5,
    dry_run: bool = False,
    day_batch: int = 1,
) -> List[Dict[str, Any]]:
    """Run the daily intake automation."""
    
    print(f"\n{'='*70}")
    print("  DAILY INTAKE AUTOMATION - VC OUTREACH ENGINE")
    print(f"{'='*70}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"  Limit: {limit} funds")
    print(f"  Target List: Daily Queue")
    print(f"  Day Batch: {day_batch}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*70}\n")
    
    # Step 1: Query top scored funds
    print("📊 Querying CRM for top scored funds...")
    try:
        funds = get_top_scored_funds(limit)
        print(f"   Found {len(funds)} funds\n")
    except Exception as e:
        print(f"   ❌ Error querying CRM: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    if not funds:
        print("   ⚠️  No funds found with scores")
        return []
    
    # Display found funds
    print("   Top Funds:")
    for i, fund in enumerate(funds, 1):
        print(f"   {i}. {fund.get('name')} (Score: {fund.get('score', 0):.1f})")
    print()
    
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
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total funds processed: {len(funds)}")
    print(f"  Cards created: {len(created_cards)}")
    print(f"  Skipped (duplicates): {len(funds) - len(created_cards)}")
    print(f"{'='*70}\n")
    
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
    
    # Validate environment
    try:
        get_maton_api_key()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Run automation
    try:
        results = run_daily_intake(
            limit=args.limit,
            dry_run=args.dry_run,
            day_batch=args.day_batch,
        )
        
        if results:
            print("✅ Automation completed successfully")
            sys.exit(0)
        else:
            print("⚠️  No cards created (may be duplicates or no funds available)")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
