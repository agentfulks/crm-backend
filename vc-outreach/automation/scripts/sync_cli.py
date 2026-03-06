#!/usr/bin/env python3
"""CLI for VC source automation."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

from sqlalchemy.orm import Session

from app.db.session import get_session

# Import automation modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "automation" / "src"))
from fetchers import get_fetcher
from models import DataSource, SyncConfig
from scheduler import get_scheduler, run_scheduler_forever, setup_sync_schedule
from sync import run_daily_sync, SyncOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config_from_env() -> list[SyncConfig]:
    """Load sync configurations from environment variables."""
    configs = []
    
    # Apollo config
    apollo_key = os.getenv('APOLLO_API_KEY')
    if apollo_key:
        configs.append(SyncConfig(
            data_source=DataSource.APOLLO,
            api_key=apollo_key,
            target_sectors=['gaming', 'ai', 'artificial intelligence'],
            rate_limit_per_minute=60
        ))
    
    # Crunchbase config
    cb_key = os.getenv('CRUNCHBASE_API_KEY')
    if cb_key:
        configs.append(SyncConfig(
            data_source=DataSource.CRUNCHBASE,
            api_key=cb_key,
            target_sectors=['gaming', 'ai', 'artificial intelligence'],
            rate_limit_per_minute=30
        ))
    
    return configs


def cmd_sync(args: argparse.Namespace) -> int:
    """Run sync operation."""
    configs = load_config_from_env()
    
    if not configs:
        logger.error("No API keys configured. Set APOLLO_API_KEY or CRUNCHBASE_API_KEY.")
        return 1
    
    if args.source:
        configs = [c for c in configs if c.data_source.value == args.source]
    
    with get_session() as session:
        if args.dry_run:
            logger.info("DRY RUN - no data will be written")
        
        results = run_daily_sync(
            session,
            configs,
            dry_run=args.dry_run
        )
        
        # Print results
        for run in results:
            print(f"\n{run.data_source.value.upper()} Sync:")
            print(f"  Status: {run.status}")
            print(f"  Fetched: {run.records_fetched}")
            print(f"  New: {run.records_new}")
            print(f"  Updated: {run.records_updated}")
            print(f"  Skipped: {run.records_skipped}")
            
            if run.errors:
                print(f"  Errors: {len(run.errors)}")
    
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    """Fetch and display funds without saving."""
    config = SyncConfig(
        data_source=DataSource(args.source),
        api_key=os.getenv(f'{args.source.upper()}_API_KEY'),
        target_sectors=args.sectors or ['gaming', 'ai'],
        rate_limit_per_minute=60
    )
    
    if not config.api_key:
        logger.error(f"No API key found. Set {args.source.upper()}_API_KEY.")
        return 1
    
    fetcher = get_fetcher(args.source, config)
    
    print(f"Fetching up to {args.limit} funds from {args.source}...\n")
    
    count = 0
    for fund in fetcher.fetch_funds(limit=args.limit):
        count += 1
        print(f"{count}. {fund.name}")
        if fund.website_url:
            print(f"   Website: {fund.website_url}")
        if fund.hq_city:
            print(f"   Location: {fund.hq_city}, {fund.hq_country or 'Unknown'}")
        if fund.sector_focus:
            print(f"   Focus: {', '.join(fund.sector_focus)}")
        print()
    
    print(f"\nTotal fetched: {count}")
    return 0


def cmd_schedule(args: argparse.Namespace) -> int:
    """Run scheduler daemon."""
    configs = load_config_from_env()
    
    if not configs:
        logger.error("No API keys configured.")
        return 1
    
    def sync_callback():
        with get_session() as session:
            run_daily_sync(session, configs)
    
    setup_sync_schedule(sync_callback, args.cron)
    
    logger.info(f"Starting scheduler with cron: {args.cron}")
    run_scheduler_forever()
    return 0


def cmd_dedupe_test(args: argparse.Namespace) -> int:
    """Test deduplication logic."""
    from dedupe import DeduplicationEngine
    
    engine = DeduplicationEngine(threshold=args.threshold)
    
    test_cases = [
        ("Accel Partners", "Accel", 0.95),
        ("Andreessen Horowitz", "a16z", 0.0),
        ("Sequoia Capital", "Sequoia Capital India", 0.95),
        ("Lightspeed Venture Partners", "Lightspeed", 0.95),
        ("Greylock Partners", "Greylock", 0.95),
        ("Index Ventures", "Index Venture", 0.95),
    ]
    
    print("Deduplication Tests:\n")
    for name1, name2, expected in test_cases:
        score = engine.name_similarity(name1, name2)
        status = "✓" if abs(score - expected) < 0.1 else "✗"
        print(f"{status} '{name1}' vs '{name2}': {score:.2f} (expected: {expected:.2f})")
    
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show sync statistics."""
    from db_ops import get_sync_stats
    
    with get_session() as session:
        stats = get_sync_stats(session, args.source)
        
        print("\nFund Database Statistics:")
        print(f"  Total funds: {stats['total_funds']}")
        print(f"  From Crunchbase: {stats['crunchbase_count']}")
        print(f"  From Apollo: {stats['apollo_count']}")
        print(f"  Added in last 24h: {stats['last_24h']}")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VC Source Automation CLI"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Run sync operation')
    sync_parser.add_argument('--source', choices=['apollo', 'crunchbase'], help='Data source')
    sync_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch funds without saving')
    fetch_parser.add_argument('source', choices=['apollo', 'crunchbase'], help='Data source')
    fetch_parser.add_argument('--limit', type=int, default=10, help='Max funds to fetch')
    fetch_parser.add_argument('--sectors', nargs='+', help='Target sectors')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Run scheduler daemon')
    schedule_parser.add_argument('--cron', default='0 6 * * *', help='Cron expression')
    
    # Dedupe test command
    dedupe_parser = subparsers.add_parser('dedupe-test', help='Test deduplication')
    dedupe_parser.add_argument('--threshold', type=float, default=0.85, help='Match threshold')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--source', choices=['apollo', 'crunchbase'], help='Filter by source')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'sync': cmd_sync,
        'fetch': cmd_fetch,
        'schedule': cmd_schedule,
        'dedupe-test': cmd_dedupe_test,
        'stats': cmd_stats,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
