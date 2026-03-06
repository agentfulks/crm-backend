#!/usr/bin/env python3
"""CLI dashboard for the tiered approval system.

Usage:
    python approval_dashboard.py
    python approval_dashboard.py approve-batch --tier P1 --limit 20
    python approval_dashboard.py archive-expired --days 14
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.approval_tiers import CardTier
from src.services.batch_approver import BatchApprover


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_card_summary(card, index: int = None) -> None:
    """Print a card summary line."""
    prefix = f"{index}. " if index else "   "
    tier_badge = ""
    
    print(f"{prefix}[{card.id}] {card.name}")
    print(f"      Fit Score: {card.fit_score} | Days in Queue: {card.days_in_queue}")
    if card.funding_stage:
        print(f"      Stage: {card.funding_stage}")
    if card.portfolio_match:
        print(f"      Portfolio Match: Yes")
    print()


def show_dashboard(approver: BatchApprover) -> None:
    """Display the main dashboard view."""
    print_header("TIERED APPROVAL DASHBOARD")
    
    # Show counts
    counts = approver.get_counts_by_tier()
    print("CARDS BY TIER:")
    print(f"  P0 (Urgent Review):     {counts[CardTier.P0]:3d} cards")
    print(f"  P1 (Batch Approval):    {counts[CardTier.P1]:3d} cards")
    print(f"  P2 (Auto-Archive):      {counts[CardTier.P2]:3d} cards")
    print(f"  {'─' * 25}")
    print(f"  TOTAL:                  {approver.total_cards:3d} cards")
    
    # Show top 10 P0 cards
    p0_cards = approver.get_top_p0_cards(limit=10)
    if p0_cards:
        print_header("TOP 10 P0 CARDS (URGENT REVIEW)")
        for i, card in enumerate(p0_cards, 1):
            print_card_summary(card, i)
    else:
        print("\n  No P0 cards requiring urgent review.\n")


def cmd_approve_batch(args) -> int:
    """Handle approve-batch command."""
    approver = BatchApprover(args.state_file)
    
    tier = CardTier(args.tier)
    
    print_header(f"BATCH APPROVAL: {tier.value}")
    
    # Preview what will be approved
    cards = approver.get_batch_for_review(tier, args.limit)
    if not cards:
        print(f"No {tier.value} cards found for approval.")
        return 0
    
    print(f"Found {len(cards)} {tier.value} cards to approve:\n")
    for i, card in enumerate(cards, 1):
        print_card_summary(card, i)
    
    # Confirm if not --yes flag
    if not args.yes:
        confirm = input(f"Approve these {len(cards)} cards? [y/N]: ")
        if confirm.lower() not in ('y', 'yes'):
            print("Approval cancelled.")
            return 0
    
    # Execute approval
    result = approver.approve_batch([c.id for c in cards])
    
    print(f"\n✓ Approved: {result.success_count} cards")
    if result.failure_count > 0:
        print(f"✗ Failed: {result.failure_count} cards")
    
    return 0


def cmd_archive_expired(args) -> int:
    """Handle archive-expired command."""
    approver = BatchApprover(args.state_file)
    
    print_header(f"ARCHIVE EXPIRED CARDS (> {args.days} days)")
    
    # Preview what will be archived
    p2_cards = approver.get_batch_for_review(CardTier.P2, limit=1000)
    expired_cards = [c for c in p2_cards if c.days_in_queue >= args.days]
    
    if not expired_cards:
        print(f"No P2 cards older than {args.days} days found.")
        return 0
    
    print(f"Found {len(expired_cards)} expired P2 cards:\n")
    for i, card in enumerate(expired_cards[:20], 1):  # Show first 20
        print_card_summary(card, i)
    
    if len(expired_cards) > 20:
        print(f"  ... and {len(expired_cards) - 20} more\n")
    
    # Confirm if not --yes flag
    if not args.yes:
        confirm = input(f"Archive these {len(expired_cards)} cards? [y/N]: ")
        if confirm.lower() not in ('y', 'yes'):
            print("Archive cancelled.")
            return 0
    
    # Execute archive
    result = approver.archive_low_tier_cards(min_days=args.days)
    
    print(f"\n✓ Archived: {result.archived_count} cards")
    if result.failed_ids:
        print(f"✗ Failed: {len(result.failed_ids)} cards")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Tiered Approval System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Show dashboard
  %(prog)s approve-batch --tier P1   # Batch approve P1 cards
  %(prog)s archive-expired --days 14 # Archive old P2 cards
        """
    )
    
    parser.add_argument(
        '--state-file',
        default='trello-state.json',
        help='Path to card state file (default: trello-state.json)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # approve-batch command
    approve_parser = subparsers.add_parser(
        'approve-batch',
        help='Approve a batch of cards by tier'
    )
    approve_parser.add_argument(
        '--tier',
        choices=['P0', 'P1', 'P2'],
        required=True,
        help='Tier to approve'
    )
    approve_parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of cards to approve (default: 20)'
    )
    approve_parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    # archive-expired command
    archive_parser = subparsers.add_parser(
        'archive-expired',
        help='Archive expired low-tier cards'
    )
    archive_parser.add_argument(
        '--days',
        type=int,
        default=14,
        help='Minimum days in queue to archive (default: 14)'
    )
    archive_parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    if args.command == 'approve-batch':
        return cmd_approve_batch(args)
    elif args.command == 'archive-expired':
        return cmd_archive_expired(args)
    else:
        # Default: show dashboard
        approver = BatchApprover(args.state_file)
        show_dashboard(approver)
        return 0


if __name__ == '__main__':
    sys.exit(main())
