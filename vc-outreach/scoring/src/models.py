"""Scoring models and configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PriorityTier(str, Enum):
    """Priority tiers for VCs."""
    S = "S"  # Strategic/top tier
    A = "A"  # High priority
    B = "B"  # Medium priority
    C = "C"  # Low priority
    D = "D"  # Unlikely


class ScoreFactor(str, Enum):
    """Individual scoring factors."""
    # Fit factors
    THESIS_ALIGNMENT = "thesis_alignment"
    STAGE_MATCH = "stage_match"
    CHECK_SIZE_MATCH = "check_size_match"
    SECTOR_FOCUS = "sector_focus"
    
    # Quality factors
    FUND_REPUTATION = "fund_reputation"
    PORTFOLIO_QUALITY = "portfolio_quality"
    TRACK_RECORD = "track_record"
    
    # Engagement factors
    WARM_INTRO_AVAILABLE = "warm_intro_available"
    PREVIOUS_INTERACTION = "previous_interaction"
    RESPONSE_LIKELIHOOD = "response_likelihood"
    
    # Strategic factors
    CO_INVESTMENT_NETWORK = "co_investment_network"
    VALUE_ADD = "value_add"
    BRAND_PRESTIGE = "brand_prestige"
    SPEED = "speed"


@dataclass
class FactorWeight:
    """Configuration for a scoring factor."""
    factor: ScoreFactor
    weight: float  # 0.0 - 1.0
    description: str
    max_score: float = 1.0


class ScoringConfig(BaseModel):
    """Configuration for VC scoring algorithm."""
    
    # Factor weights (must sum to 1.0)
    weights: Dict[ScoreFactor, float] = Field(default_factory=lambda: {
        ScoreFactor.THESIS_ALIGNMENT: 0.20,
        ScoreFactor.STAGE_MATCH: 0.15,
        ScoreFactor.CHECK_SIZE_MATCH: 0.10,
        ScoreFactor.SECTOR_FOCUS: 0.15,
        ScoreFactor.FUND_REPUTATION: 0.10,
        ScoreFactor.WARM_INTRO_AVAILABLE: 0.15,
        ScoreFactor.VALUE_ADD: 0.10,
        ScoreFactor.SPEED: 0.05,
    })
    
    # Target criteria
    target_sectors: List[str] = Field(default_factory=lambda: ["gaming", "ai"])
    target_stage: str = "series_a"
    target_check_size_min: float = 1_000_000  # $1M
    target_check_size_max: float = 5_000_000  # $5M
    
    # Scoring thresholds
    tier_thresholds: Dict[PriorityTier, float] = Field(default_factory=lambda: {
        PriorityTier.S: 0.90,
        PriorityTier.A: 0.75,
        PriorityTier.B: 0.60,
        PriorityTier.C: 0.40,
        PriorityTier.D: 0.00,
    })
    
    # Minimum criteria
    min_sector_overlap: int = 1
    min_score_for_outreach: float = 0.50
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = sum(self.weights.values())
        return 0.99 <= total <= 1.01


class FactorScore(BaseModel):
    """Score for an individual factor."""
    
    factor: ScoreFactor
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)
    explanation: str = ""
    
    def calculate_weighted(self) -> float:
        """Calculate weighted score."""
        self.weighted_score = self.score * self.weight
        return self.weighted_score


class FundScore(BaseModel):
    """Complete scoring result for a fund."""
    
    fund_id: str
    fund_name: str
    
    # Component scores
    factor_scores: List[FactorScore] = Field(default_factory=list)
    
    # Aggregate scores
    raw_score: float = 0.0
    normalized_score: float = Field(default=0.0, ge=0.0, le=1.0)
    priority_tier: PriorityTier = PriorityTier.C
    
    # Breakdown
    fit_score: float = 0.0  # Thesis/stage/sector alignment
    quality_score: float = 0.0  # Fund quality/reputation
    engagement_score: float = 0.0  # Likelihood of response
    strategic_score: float = 0.0  # Strategic value
    
    # Recommendations
    should_outreach: bool = False
    outreach_priority: int = 0  # 1 = highest
    recommended_approach: str = "cold_email"
    
    # Metadata
    calculated_at: str = ""
    score_version: str = "1.0"


class ScoringBatchResult(BaseModel):
    """Result of batch scoring operation."""
    
    batch_id: str
    total_funds: int
    scored_funds: int
    failed_funds: int
    
    # Distribution
    tier_distribution: Dict[PriorityTier, int] = Field(default_factory=dict)
    
    # Funds by tier
    tier_s: List[FundScore] = Field(default_factory=list)
    tier_a: List[FundScore] = Field(default_factory=list)
    tier_b: List[FundScore] = Field(default_factory=list)
    tier_c: List[FundScore] = Field(default_factory=list)
    tier_d: List[FundScore] = Field(default_factory=list)
    
    # Stats
    avg_score: float = 0.0
    max_score: float = 0.0
    min_score: float = 0.0
