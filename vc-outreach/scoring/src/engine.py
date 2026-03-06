"""Scoring engine for VC fund prioritization."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.fund import Fund

from .models import (
    FactorScore,
    FundScore,
    PriorityTier,
    ScoreFactor,
    ScoringBatchResult,
    ScoringConfig
)

logger = logging.getLogger(__name__)


class FundScorer:
    """Calculates scores for VC funds."""
    
    # Reputation scoring - tier-based adjustments
    TIER_1_FUNDS = [
        'sequoia', 'andreessen horowitz', 'a16z', 'accel', 'benchmark',
        'bessemer', 'greylock', 'index ventures', 'insight partners',
        'khosla ventures', 'kleiner perkins', 'lightspeed',
        'new enterprise associates', 'nea', 'norwest', 'threshold'
    ]
    
    TIER_2_FUNDS = [
        '500 startups', 'battery ventures', 'craft ventures', 'dcvc',
        'first round', 'founders fund', 'foundry group', 'general catalyst',
        'gv', 'harrison metal', 'ivp', 'lerer hippeau', 'matrix partners',
        'menlo ventures', 'northzone', 'redpoint', 'spark capital',
        'union square ventures', 'usv'
    ]
    
    # Gaming-focused VCs (high strategic value)
    GAMING_VCS = [
        'bitkraft', 'griffin gaming partners', 'galaxy interactive',
        'konvoy', 'makers fund', 'hiro capital', 'transcend',
        'lumikai', 'gamedistrict'
    ]
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
        if not self.config.validate_weights():
            logger.warning("Scoring weights do not sum to 1.0")
    
    def score_fund(self, fund: Fund) -> FundScore:
        """Calculate comprehensive score for a fund."""
        result = FundScore(
            fund_id=fund.id,
            fund_name=fund.name,
            calculated_at=datetime.utcnow().isoformat()
        )
        
        factor_scores = []
        
        # Fit factors
        factor_scores.append(self._score_thesis_alignment(fund))
        factor_scores.append(self._score_stage_match(fund))
        factor_scores.append(self._score_check_size_match(fund))
        factor_scores.append(self._score_sector_focus(fund))
        
        # Quality factors
        factor_scores.append(self._score_fund_reputation(fund))
        
        # Engagement factors
        factor_scores.append(self._score_warm_intro(fund))
        
        # Strategic factors
        factor_scores.append(self._score_value_add(fund))
        factor_scores.append(self._score_speed(fund))
        
        result.factor_scores = factor_scores
        
        # Calculate aggregate scores
        result.raw_score = sum(fs.weighted_score for fs in factor_scores)
        result.normalized_score = min(result.raw_score, 1.0)
        
        # Calculate category breakdowns
        fit_factors = [ScoreFactor.THESIS_ALIGNMENT, ScoreFactor.STAGE_MATCH, 
                      ScoreFactor.CHECK_SIZE_MATCH, ScoreFactor.SECTOR_FOCUS]
        quality_factors = [ScoreFactor.FUND_REPUTATION]
        engagement_factors = [ScoreFactor.WARM_INTRO_AVAILABLE]
        strategic_factors = [ScoreFactor.VALUE_ADD, ScoreFactor.SPEED]
        
        result.fit_score = sum(fs.weighted_score for fs in factor_scores 
                               if fs.factor in fit_factors)
        result.quality_score = sum(fs.weighted_score for fs in factor_scores 
                                   if fs.factor in quality_factors)
        result.engagement_score = sum(fs.weighted_score for fs in factor_scores 
                                      if fs.factor in engagement_factors)
        result.strategic_score = sum(fs.weighted_score for fs in factor_scores 
                                     if fs.factor in strategic_factors)
        
        # Determine priority tier
        result.priority_tier = self._determine_tier(result.normalized_score)
        
        # Determine outreach recommendation
        result.should_outreach = result.normalized_score >= self.config.min_score_for_outreach
        result.outreach_priority = self._calculate_outreach_priority(result)
        result.recommended_approach = self._recommend_approach(fund, result)
        
        return result
    
    def _score_thesis_alignment(self, fund: Fund) -> FactorScore:
        """Score alignment with investment thesis."""
        score = 0.5  # Base score
        
        # Check for gaming/AI focus
        tags = fund.tags or {}
        sectors = tags.get('sector_focus', [])
        
        if isinstance(sectors, str):
            sectors = [s.strip() for s in sectors.split(',')]
        
        has_gaming = any('game' in s.lower() for s in sectors)
        has_ai = any(s.lower() in ['ai', 'artificial intelligence', 'machine learning'] for s in sectors)
        
        if has_gaming and has_ai:
            score = 1.0
            explanation = "Perfect thesis alignment: Gaming + AI focus"
        elif has_gaming:
            score = 0.85
            explanation = "Strong alignment: Gaming focus"
        elif has_ai:
            score = 0.75
            explanation = "Good alignment: AI focus"
        else:
            # Check stage alignment
            stage = fund.stage_focus or []
            if isinstance(stage, str):
                stage = [stage]
            
            target_stages = ['series_a', 'series_b', 'growth']
            stage_match = any(s in target_stages for s in stage)
            
            if stage_match:
                score = 0.60
                explanation = "Moderate alignment: Stage match"
            else:
                score = 0.30
                explanation = "Weak alignment: No sector/stage match"
        
        weight = self.config.weights.get(ScoreFactor.THESIS_ALIGNMENT, 0.20)
        
        return FactorScore(
            factor=ScoreFactor.THESIS_ALIGNMENT,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_stage_match(self, fund: Fund) -> FactorScore:
        """Score stage alignment."""
        stage_focus = fund.stage_focus or []
        if isinstance(stage_focus, str):
            stage_focus = [stage_focus]
        
        target = self.config.target_stage
        stage_lower = [s.lower().replace(' ', '_') for s in stage_focus]
        
        if target in stage_lower:
            score = 1.0
            explanation = f"Exact stage match: {target}"
        elif any(s in stage_lower for s in ['series_a', 'series_b']):
            score = 0.85
            explanation = "Good stage match: Series A/B"
        elif any(s in stage_lower for s in ['seed', 'pre_seed']):
            score = 0.60
            explanation = "Partial match: Earlier stage"
        elif any(s in stage_lower for s in ['growth', 'late_stage']):
            score = 0.60
            explanation = "Partial match: Later stage"
        else:
            score = 0.40
            explanation = "Unclear stage focus"
        
        weight = self.config.weights.get(ScoreFactor.STAGE_MATCH, 0.15)
        
        return FactorScore(
            factor=ScoreFactor.STAGE_MATCH,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_check_size_match(self, fund: Fund) -> FactorScore:
        """Score check size alignment."""
        min_size = fund.check_size_min or 0
        max_size = fund.check_size_max or float('inf')
        
        target_min = self.config.target_check_size_min
        target_max = self.config.target_check_size_max
        
        # Check if ranges overlap
        if min_size <= target_max and max_size >= target_min:
            # Calculate how well ranges align
            overlap_min = max(min_size, target_min)
            overlap_max = min(max_size, target_max)
            
            if overlap_max - overlap_min >= 1_000_000:
                score = 1.0
                explanation = "Perfect check size alignment"
            else:
                score = 0.75
                explanation = "Good check size alignment"
        elif min_size > target_max:
            score = 0.40
            explanation = "Fund check size too large"
        elif max_size < target_min:
            score = 0.30
            explanation = "Fund check size too small"
        else:
            score = 0.50
            explanation = "Unclear check size fit"
        
        weight = self.config.weights.get(ScoreFactor.CHECK_SIZE_MATCH, 0.10)
        
        return FactorScore(
            factor=ScoreFactor.CHECK_SIZE_MATCH,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_sector_focus(self, fund: Fund) -> FactorScore:
        """Score sector focus alignment."""
        tags = fund.tags or {}
        sectors = tags.get('sector_focus', [])
        
        if isinstance(sectors, str):
            sectors = [s.strip() for s in sectors.split(',')]
        
        target_sectors = [s.lower() for s in self.config.target_sectors]
        
        matches = sum(1 for s in sectors if any(t in s.lower() for t in target_sectors))
        
        if matches >= 2:
            score = 1.0
            explanation = f"Multi-sector match: {matches} target sectors"
        elif matches == 1:
            score = 0.75
            explanation = "Single sector match"
        else:
            score = 0.30
            explanation = "No target sector overlap"
        
        weight = self.config.weights.get(ScoreFactor.SECTOR_FOCUS, 0.15)
        
        return FactorScore(
            factor=ScoreFactor.SECTOR_FOCUS,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_fund_reputation(self, fund: Fund) -> FactorScore:
        """Score fund reputation/quality."""
        name_lower = fund.name.lower()
        
        # Check tier lists
        if any(tier_fund in name_lower for tier_fund in self.TIER_1_FUNDS):
            score = 1.0
            explanation = "Tier 1 fund"
        elif any(tier_fund in name_lower for tier_fund in self.TIER_2_FUNDS):
            score = 0.85
            explanation = "Tier 2 fund"
        elif fund.data_source == 'crunchbase' and fund.tags and fund.tags.get('funding_total'):
            score = 0.70
            explanation = "Established fund with track record"
        else:
            score = 0.50
            explanation = "Unknown/unverified fund quality"
        
        weight = self.config.weights.get(ScoreFactor.FUND_REPUTATION, 0.10)
        
        return FactorScore(
            factor=ScoreFactor.FUND_REPUTATION,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_warm_intro(self, fund: Fund) -> FactorScore:
        """Score likelihood of warm intro availability."""
        # Check for LinkedIn presence (proxy for network)
        score = 0.50  # Base assumption
        
        if fund.linkedin_url:
            score += 0.20
        
        # Check for contacts
        # This would require session query in practice
        # For now, assume average connectivity
        
        explanation = "Standard network connectivity"
        
        weight = self.config.weights.get(ScoreFactor.WARM_INTRO_AVAILABLE, 0.15)
        
        return FactorScore(
            factor=ScoreFactor.WARM_INTRO_AVAILABLE,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_value_add(self, fund: Fund) -> FactorScore:
        """Score strategic value-add potential."""
        name_lower = fund.name.lower()
        
        # Gaming VCs often provide strong value-add
        if any(gaming_vc in name_lower for gaming_vc in self.GAMING_VCS):
            score = 1.0
            explanation = "Gaming-specialist VC: high value-add"
        # Tier 1 funds provide value through network
        elif any(tier in name_lower for tier in self.TIER_1_FUNDS):
            score = 0.90
            explanation = "Tier 1 network value"
        else:
            score = 0.60
            explanation = "Standard value-add potential"
        
        weight = self.config.weights.get(ScoreFactor.VALUE_ADD, 0.10)
        
        return FactorScore(
            factor=ScoreFactor.VALUE_ADD,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _score_speed(self, fund: Fund) -> FactorScore:
        """Score decision speed likelihood."""
        # Smaller/newer funds often move faster
        score = 0.60  # Default assumption
        
        name_lower = fund.name.lower()
        
        # Tier 1 funds are slower due to competition
        if any(tier in name_lower for tier in self.TIER_1_FUNDS):
            score = 0.40
            explanation = "Tier 1: likely slower process"
        # Smaller/specialist funds faster
        elif any(gaming in name_lower for gaming in self.GAMING_VCS):
            score = 0.80
            explanation = "Specialist fund: likely faster"
        else:
            explanation = "Average expected speed"
        
        weight = self.config.weights.get(ScoreFactor.SPEED, 0.05)
        
        return FactorScore(
            factor=ScoreFactor.SPEED,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            explanation=explanation
        )
    
    def _determine_tier(self, score: float) -> PriorityTier:
        """Determine priority tier from score."""
        thresholds = self.config.tier_thresholds
        
        if score >= thresholds[PriorityTier.S]:
            return PriorityTier.S
        elif score >= thresholds[PriorityTier.A]:
            return PriorityTier.A
        elif score >= thresholds[PriorityTier.B]:
            return PriorityTier.B
        elif score >= thresholds[PriorityTier.C]:
            return PriorityTier.C
        else:
            return PriorityTier.D
    
    def _calculate_outreach_priority(self, result: FundScore) -> int:
        """Calculate outreach priority (1 = highest)."""
        tier_order = {
            PriorityTier.S: 1,
            PriorityTier.A: 2,
            PriorityTier.B: 3,
            PriorityTier.C: 4,
            PriorityTier.D: 5
        }
        return tier_order.get(result.priority_tier, 5)
    
    def _recommend_approach(self, fund: Fund, result: FundScore) -> str:
        """Recommend outreach approach."""
        if result.priority_tier in [PriorityTier.S, PriorityTier.A]:
            if fund.linkedin_url:
                return "warm_intro_preferred"
            return "personalized_email"
        elif result.priority_tier == PriorityTier.B:
            return "targeted_email"
        else:
            return "standard_outreach"
