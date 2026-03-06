"""Batch scoring operations."""
from __future__ import annotations

import logging
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fund import Fund

from .engine import FundScorer
from .models import FundScore, PriorityTier, ScoringBatchResult, ScoringConfig

logger = logging.getLogger(__name__)


class BatchScorer:
    """Batch scoring for multiple funds."""
    
    def __init__(self, session: Session, config: Optional[ScoringConfig] = None):
        self.session = session
        self.config = config or ScoringConfig()
        self.scorer = FundScorer(self.config)
    
    def score_all_funds(self, fund_ids: Optional[List[str]] = None) -> ScoringBatchResult:
        """Score all funds or specific fund IDs."""
        result = ScoringBatchResult(batch_id=str(uuid4()))
        
        # Query funds
        if fund_ids:
            query = select(Fund).where(Fund.id.in_(fund_ids))
        else:
            query = select(Fund).where(Fund.score.is_(None))  # Unscored funds
        
        funds = self.session.execute(query).scalars().all()
        result.total_funds = len(funds)
        
        logger.info(f"Scoring {len(funds)} funds...")
        
        scores = []
        
        for fund in funds:
            try:
                score = self.scorer.score_fund(fund)
                scores.append(score)
                result.scored_funds += 1
                
                # Update database
                fund.score = score.normalized_score
                fund.priority = score.priority_tier.value
                
                # Categorize by tier
                self._categorize_by_tier(result, score)
                
            except Exception as e:
                logger.error(f"Failed to score fund {fund.name}: {e}")
                result.failed_funds += 1
        
        self.session.commit()
        
        # Calculate stats
        if scores:
            scores_sorted = sorted([s.normalized_score for s in scores])
            result.avg_score = sum(scores_sorted) / len(scores_sorted)
            result.max_score = max(scores_sorted)
            result.min_score = min(scores_sorted)
        
        # Calculate tier distribution
        for tier in PriorityTier:
            result.tier_distribution[tier] = len(
                [s for s in scores if s.priority_tier == tier]
            )
        
        logger.info(
            f"Batch complete: {result.scored_funds} scored, "
            f"{result.failed_funds} failed, avg score: {result.avg_score:.2f}"
        )
        
        return result
    
    def _categorize_by_tier(self, result: ScoringBatchResult, score: FundScore) -> None:
        """Add fund to appropriate tier list."""
        if score.priority_tier == PriorityTier.S:
            result.tier_s.append(score)
        elif score.priority_tier == PriorityTier.A:
            result.tier_a.append(score)
        elif score.priority_tier == PriorityTier.B:
            result.tier_b.append(score)
        elif score.priority_tier == PriorityTier.C:
            result.tier_c.append(score)
        else:
            result.tier_d.append(score)
    
    def get_top_funds(self, tier: Optional[PriorityTier] = None, limit: int = 20) -> List[FundScore]:
        """Get top-scored funds."""
        query = select(Fund).where(Fund.score.isnot(None))
        
        if tier:
            query = query.where(Fund.priority == tier.value)
        
        query = query.order_by(Fund.score.desc()).limit(limit)
        
        funds = self.session.execute(query).scalars().all()
        
        return [self.scorer.score_fund(fund) for fund in funds]
    
    def recalculate_scores(self) -> ScoringBatchResult:
        """Recalculate scores for all funds with existing scores."""
        funds = self.session.execute(
            select(Fund).where(Fund.score.isnot(None))
        ).scalars().all()
        
        fund_ids = [f.id for f in funds]
        return self.score_all_funds(fund_ids)
