"""Main entry point for Daily Intake Automation."""

import argparse
import json
import sys
from typing import Optional

import structlog

from src.config import get_settings
from src.services import DailyIntakeService


def setup_logging(log_level: str) -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if sys.stderr.isatty() else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Daily Intake Automation - Create Trello cards from CRM investor entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (5 entries, production mode)
  python -m src.main
  
  # Dry run - don't actually create cards
  python -m src.main --dry-run
  
  # Process only top 3 entries
  python -m src.main --limit 3
  
  # Output results as JSON
  python -m src.main --json
        """,
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode - don't actually create cards",
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of investor entries to process (default: 5)",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override logging level from environment",
    )
    
    return parser


def format_console_output(result) -> str:
    """Format results for console output."""
    lines = [
        "",
        "=" * 60,
        "DAILY INTAKE AUTOMATION - RESULTS",
        "=" * 60,
        f"Timestamp: {result.timestamp.isoformat()}",
        f"Mode: {'DRY RUN' if result.dry_run else 'PRODUCTION'}",
        "",
        "SUMMARY:",
        f"  Total entries found: {result.total_entries_found}",
        f"  Cards created: {result.cards_created}",
        f"  Cards skipped (duplicates): {result.cards_skipped}",
        f"  Cards failed: {result.cards_failed}",
        f"  Success rate: {result.success_rate:.1f}%",
        "",
    ]
    
    if result.details:
        lines.append("DETAILS:")
        for detail in result.details:
            status_icon = "✓" if detail.success else "✗"
            lines.append(f"  {status_icon} {detail.investor_entry.investor_name}")
            if detail.trello_card_url:
                lines.append(f"    → {detail.trello_card_url}")
            if detail.error_message:
                lines.append(f"    ERROR: {detail.error_message}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main(args: Optional[list] = None) -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Load settings
    settings = get_settings()
    
    # Setup logging
    log_level = parsed_args.log_level or settings.log_level
    setup_logging(log_level)
    logger = structlog.get_logger()
    
    logger.info(
        "Starting Daily Intake Automation",
        version="1.0.0",
        dry_run=parsed_args.dry_run,
        limit=parsed_args.limit,
    )
    
    try:
        # Create service and run
        service = DailyIntakeService(settings=settings)
        result = service.process_daily_intake(
            limit=parsed_args.limit,
            dry_run=parsed_args.dry_run or settings.dry_run,
        )
        
        # Output results
        if parsed_args.json:
            print(json.dumps(result.model_dump(mode="json"), indent=2))
        else:
            print(format_console_output(result))
        
        # Return non-zero if any failures
        if result.cards_failed > 0:
            logger.error("Processing completed with failures")
            return 1
        
        logger.info("Processing completed successfully")
        return 0
        
    except Exception as e:
        logger.exception("Fatal error during processing")
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
