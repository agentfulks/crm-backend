#!/usr/bin/env python3
"""CLI for contact enrichment."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

from app.db.session import get_session

# Import enrichment modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "enrichment" / "src"))
from models import EnrichmentJob, EnrichmentSource
from orchestrator import EnrichmentOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_enrich(args: argparse.Namespace) -> int:
    """Run enrichment for specified funds."""
    job = EnrichmentJob(
        job_id="enrich_cli",
        fund_ids=args.fund_ids or [],
        sources=[EnrichmentSource(s) for s in args.sources],
        apollo_api_key=os.getenv('APOLLO_API_KEY'),
        hunter_api_key=os.getenv('HUNTER_API_KEY'),
        max_contacts_per_fund=args.max_contacts,
        min_confidence=args.min_confidence,
        dry_run=args.dry_run,
        overwrite_existing=args.overwrite
    )
    
    with get_session() as session:
        orchestrator = EnrichmentOrchestrator(session, job)
        batch = orchestrator.run_enrichment()
        
        print(f"\nEnrichment Complete:")
        print(f"  Funds processed: {batch.funds_completed}")
        print(f"  Funds failed: {batch.funds_failed}")
        print(f"  Total contacts found: {batch.total_contacts_found}")
        print(f"  Total emails found: {batch.total_emails_found}")
        
        if args.verbose:
            for result in batch.results:
                print(f"\n  {result.fund_name}:")
                print(f"    Status: {result.status}")
                print(f"    Contacts: {result.total_contacts}")
                print(f"    Emails: {result.emails_found} (verified: {result.emails_verified})")
                
                for contact in result.contacts_found[:5]:
                    print(f"      - {contact.full_name} ({contact.title or 'N/A'})")
                    if contact.email:
                        print(f"        Email: {contact.email} {'✓' if contact.email_verified else ''}")
    
    return 0


def cmd_enrich_all(args: argparse.Namespace) -> int:
    """Enrich all funds without contacts."""
    job = EnrichmentJob(
        job_id="enrich_all_cli",
        sources=[EnrichmentSource(s) for s in args.sources],
        apollo_api_key=os.getenv('APOLLO_API_KEY'),
        hunter_api_key=os.getenv('HUNTER_API_KEY'),
        max_contacts_per_fund=args.max_contacts,
        min_confidence=args.min_confidence,
        dry_run=args.dry_run
    )
    
    with get_session() as session:
        orchestrator = EnrichmentOrchestrator(session, job)
        batch = orchestrator.run_enrichment()
        
        print(f"\nEnrichment Complete:")
        print(f"  Funds processed: {batch.funds_completed}")
        print(f"  Total contacts found: {batch.total_contacts_found}")
        print(f"  Total emails found: {batch.total_emails_found}")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Contact Enrichment CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Enrich specific funds
    enrich_parser = subparsers.add_parser('enrich', help='Enrich specific funds')
    enrich_parser.add_argument('fund_ids', nargs='*', help='Fund IDs to enrich')
    enrich_parser.add_argument('--sources', nargs='+', 
                               choices=['apollo', 'hunter'],
                               default=['apollo', 'hunter'],
                               help='Enrichment sources')
    enrich_parser.add_argument('--max-contacts', type=int, default=5,
                               help='Max contacts per fund')
    enrich_parser.add_argument('--min-confidence', type=float, default=0.7,
                               help='Minimum confidence score')
    enrich_parser.add_argument('--dry-run', action='store_true',
                               help='Dry run mode')
    enrich_parser.add_argument('--overwrite', action='store_true',
                               help='Overwrite existing contacts')
    enrich_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')
    
    # Enrich all
    all_parser = subparsers.add_parser('enrich-all', 
                                       help='Enrich all funds without contacts')
    all_parser.add_argument('--sources', nargs='+',
                            choices=['apollo', 'hunter'],
                            default=['apollo', 'hunter'])
    all_parser.add_argument('--max-contacts', type=int, default=5)
    all_parser.add_argument('--min-confidence', type=float, default=0.7)
    all_parser.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'enrich': cmd_enrich,
        'enrich-all': cmd_enrich_all,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
