#!/usr/bin/env python3
"""CLI for VC scoring."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

from app.db.session import get_session

# Import scoring modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scoring" / "src"))
from batch import BatchScorer
from engine import FundScorer
from models import ScoringConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_score(args: argparse.Namespace) -> int:
    """Score specific funds or all funds."""
    config = ScoringConfig(
        target_sectors=args.sectors or ["gaming", "ai"],
        target_stage=args.stage or "series_a"
    )
    
    with get_session() as session:
        scorer = BatchScorer(session, config)
        
        if args.fund_ids:
            result = scorer.score_all_funds(args.fund_ids)
        else:
            result = scorer.score_all_funds()
        
        print(f"\nScoring Complete:")
        print(f"  Total funds: {result.total_funds}")
        print(f"  Scored: {result.scored_funds}")
        print(f"  Failed: {result.failed_funds}")
        print(f"\n  Average score: {result.avg_score:.2f}")
        print(f"  Score range: {result.min_score:.2f} - {result.max_score:.2f}")
        
        print(f"\n  Tier Distribution:")
        for tier, count in sorted(result.tier_distribution.items(), 
                                   key=lambda x: x[1], reverse=True):
            print(f"    {tier.value}: {count}")
        
        if args.verbose:
            print("\n  Top S-Tier Funds:")
            for score in result.tier_s[:5]:
                print(f"    - {score.fund_name}: {score.normalized_score:.2f}")
                print(f"      Fit: {score.fit_score:.2f}, Quality: {score.quality_score:.2f}")
            
            print("\n  Top A-Tier Funds:")
            for score in result.tier_a[:5]:
                print(f"    - {score.fund_name}: {score.normalized_score:.2f}")
    
    return 0


def cmd_top(args: argparse.Namespace) -> int:
    """Show top-scored funds."""
    config = ScoringConfig()
    
    with get_session() as session:
        scorer = BatchScorer(session, config)
        top_funds = scorer.get_top_funds(tier=args.tier, limit=args.limit)
        
        print(f"\nTop {len(top_funds)} Funds:")
        print(f"{'Rank':<5} {'Name':<40} {'Score':<8} {'Tier':<6} {'Outreach'}")
        print("-" * 75)
        
        for i, fund in enumerate(top_funds, 1):
            outreach = "Yes" if fund.should_outreach else "No"
            print(f"{i:<5} {fund.fund_name[:38]:<40} {fund.normalized_score:.2f}    {fund.priority_tier.value:<6} {outreach}")
            
            if args.details:
                print(f"      Approach: {fund.recommended_approach}")
                print(f"      Fit: {fund.fit_score:.2f}, Quality: {fund.quality_score:.2f}")
                print()
    
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze a specific fund's score."""
    config = ScoringConfig()
    
    with get_session() as session:
        from app.models.fund import Fund
        
        fund = session.get(Fund, args.fund_id)
        if not fund:
            print(f"Fund not found: {args.fund_id}")
            return 1
        
        scorer = FundScorer(config)
        result = scorer.score_fund(fund)
        
        print(f"\nScore Analysis: {fund.name}")
        print(f"=" * 60)
        print(f"\nOverall Score: {result.normalized_score:.2f}/1.00")
        print(f"Priority Tier: {result.priority_tier.value}")
        print(f"Should Outreach: {'Yes' if result.should_outreach else 'No'}")
        print(f"Outreach Priority: #{result.outreach_priority}")
        print(f"Recommended Approach: {result.recommended_approach}")
        
        print(f"\nScore Breakdown:")
        print(f"  Fit Score:      {result.fit_score:.2f} (Thesis, Stage, Sector, Check Size)")
        print(f"  Quality Score:  {result.quality_score:.2f} (Reputation, Track Record)")
        print(f"  Engagement:     {result.engagement_score:.2f} (Response Likelihood)")
        print(f"  Strategic:      {result.strategic_score:.2f} (Value-Add, Speed)")
        
        print(f"\nFactor Scores:")
        for factor in sorted(result.factor_scores, key=lambda x: x.weighted_score, reverse=True):
            print(f"  {factor.factor.value:<25} {factor.score:.2f} × {factor.weight:.2f} = {factor.weighted_score:.2f}")
            print(f"    └─ {factor.explanation}")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="VC Scoring CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score funds')
    score_parser.add_argument('fund_ids', nargs='*', help='Specific fund IDs to score')
    score_parser.add_argument('--sectors', nargs='+', help='Target sectors')
    score_parser.add_argument('--stage', help='Target stage')
    score_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Top command
    top_parser = subparsers.add_parser('top', help='Show top-scored funds')
    top_parser.add_argument('--tier', choices=['S', 'A', 'B', 'C', 'D'], help='Filter by tier')
    top_parser.add_argument('--limit', type=int, default=20, help='Number of funds')
    top_parser.add_argument('--details', '-d', action='store_true', help='Show details')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specific fund')
    analyze_parser.add_argument('fund_id', help='Fund ID to analyze')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'score': cmd_score,
        'top': cmd_top,
        'analyze': cmd_analyze,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
