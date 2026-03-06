#!/usr/bin/env python3
"""CLI for analytics operations."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

from app.db.session import get_session

# Import analytics modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analytics" / "src"))
from etl import MetricsETL
from models import MetricPeriod, PIPELINE_METRICS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Generate and display dashboard data."""
    with get_session() as session:
        etl = MetricsETL(session)
        data = etl.generate_dashboard_data(MetricPeriod(args.period))
        
        print(f"\n{'='*60}")
        print(f"VC Outreach Dashboard - {data.generated_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        print(f"\n📊 FUND OVERVIEW")
        print(f"  Total Funds: {data.total_funds}")
        print(f"  Average Score: {data.avg_fund_score:.2f}")
        
        print(f"\n  By Tier:")
        for tier, count in sorted(data.funds_by_tier.items()):
            print(f"    {tier}: {count}")
        
        print(f"\n  By Source:")
        for source, count in sorted(data.funds_by_source.items(), key=lambda x: -x[1]):
            print(f"    {source}: {count}")
        
        print(f"\n📧 ENRICHMENT")
        print(f"  Enrichment Rate: {data.enrichment_rate:.1f}%")
        print(f"  Total Contacts: {data.total_contacts}")
        print(f"  Avg Contacts/Fund: {data.avg_contacts_per_fund:.1f}")
        print(f"  Email Coverage: {data.email_coverage:.1f}%")
        
        print(f"\n📤 OUTREACH")
        print(f"  Sent: {data.outreach_sent}")
        print(f"  Responded: {data.outreach_responded}")
        print(f"  Response Rate: {data.response_rate:.1f}%")
        
        print(f"\n📅 MEETINGS")
        print(f"  Scheduled: {data.meetings_scheduled}")
        print(f"  Completed: {data.meetings_completed}")
        
        print(f"\n📋 PIPELINE")
        print(f"  Funds by Status:")
        for status, count in sorted(data.funds_by_status.items()):
            print(f"    {status}: {count}")
        
        if args.json:
            output_path = args.json
            with open(output_path, 'w') as f:
                json.dump(data.model_dump(), f, indent=2, default=str)
            print(f"\n✓ Dashboard data saved to {output_path}")
    
    return 0


def cmd_etl(args: argparse.Namespace) -> int:
    """Run ETL pipeline."""
    with get_session() as session:
        etl = MetricsETL(session)
        run = etl.run_full_etl()
        
        print(f"\nETL Run: {run.run_id}")
        print(f"Status: {run.status}")
        print(f"Metrics Computed: {len(run.metrics_computed)}")
        print(f"Errors: {len(run.errors)}")
        
        if run.errors:
            print("\nErrors:")
            for error in run.errors:
                print(f"  - {error}")
        
        if run.ended_at and run.started_at:
            duration = (run.ended_at - run.started_at).total_seconds()
            print(f"Duration: {duration:.1f}s")
    
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    """List available metrics."""
    print(f"\n{'='*60}")
    print("Available Metrics")
    print(f"{'='*60}\n")
    
    for metric in PIPELINE_METRICS:
        print(f"{metric.id}")
        print(f"  Name: {metric.name}")
        print(f"  Type: {metric.type.value}")
        print(f"  Unit: {metric.unit}")
        print(f"  Refresh: {metric.refresh_frequency.value}")
        print(f"  Formula: {metric.formula}")
        print()
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analytics CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Show dashboard')
    dash_parser.add_argument('--period', choices=['daily', 'weekly', 'monthly'],
                            default='daily', help='Time period')
    dash_parser.add_argument('--json', help='Save to JSON file')
    
    # ETL command
    etl_parser = subparsers.add_parser('etl', help='Run ETL pipeline')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='List metrics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'dashboard': cmd_dashboard,
        'etl': cmd_etl,
        'metrics': cmd_metrics,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
