"""Pydantic schemas for tiered approval system."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class CardType(str, Enum):
    """Type of card being evaluated."""
    BDR = "bdr"
    VC = "vc"


class TierLevel(int, Enum):
    """Approval tier levels."""
    TIER_1 = 1  # Auto-approve
    TIER_2 = 2  # Quick review
    TIER_3 = 3  # Deep review


class RuleResultDetail(BaseModel):
    """Detail of a single rule evaluation result."""
    
    rule_id: str
    rule_name: str
    passed: bool
    confidence: float
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClassificationResult(BaseModel):
    """Result of card classification."""
    
    tier: TierLevel
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    rules_triggered: List[str] = Field(default_factory=list)
    rules_passed: List[str] = Field(default_factory=list)
    rules_failed: List[str] = Field(default_factory=list)
    reason: str
    auto_approved: bool
    rule_details: List[RuleResultDetail] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class ClassificationRequest(BaseModel):
    """Request to classify a card."""
    
    card_id: str
    card_type: CardType
    force_reclassification: bool = False


class ClassificationResponse(BaseModel):
    """Response from card classification."""
    
    card_id: str
    card_type: CardType
    classification: ClassificationResult
    processed_at: datetime


class ApprovalActionRequest(BaseModel):
    """Request to perform an approval action."""
    
    action: str = Field(..., pattern="^(approve|reject|escalate)$")
    reason: Optional[str] = None
    performed_by: str = "user"


class ApprovalActionResponse(BaseModel):
    """Response from approval action."""
    
    card_id: str
    card_type: CardType
    action: str
    previous_tier: Optional[int]
    new_tier: Optional[int]
    performed_by: str
    performed_at: datetime
    success: bool
    message: str


class BatchApproveRequest(BaseModel):
    """Request to batch approve cards."""
    
    card_ids: List[str]
    card_type: CardType
    performed_by: str = "user"


class BatchApproveResponse(BaseModel):
    """Response from batch approval."""
    
    processed: int
    approved: int
    failed: int
    errors: List[Dict[str, str]] = Field(default_factory=list)


class ApprovalDashboardFilter(BaseModel):
    """Filter parameters for approval dashboard."""
    
    tier: Optional[TierLevel] = None
    card_type: Optional[CardType] = None
    status: Optional[str] = None
    auto_approved: Optional[bool] = None
    needs_review: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


class DashboardCardSummary(BaseModel):
    """Summary of a card in the dashboard."""
    
    id: str
    card_type: CardType
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    tier: Optional[int]
    confidence_score: Optional[float]
    icp_score: Optional[int]
    auto_approved: bool
    status: Optional[str]
    created_at: Optional[datetime]
    classification_reason: Optional[str] = None
    tags: Optional[List[str]] = None


class ApprovalDashboardResponse(BaseModel):
    """Response from approval dashboard query."""
    
    total: int
    tier_1_count: int
    tier_2_count: int
    tier_3_count: int
    unclassified_count: int
    items: List[DashboardCardSummary]
    filters: Dict[str, Any]


class DailyMetrics(BaseModel):
    """Daily approval metrics."""
    
    date: str
    total_classified: int
    tier_1_count: int
    tier_2_count: int
    tier_3_count: int
    auto_approval_rate: float
    avg_confidence_score: float
    manual_approvals: int
    manual_rejections: int
    avg_review_time_seconds: Optional[float]


class ApprovalMetricsResponse(BaseModel):
    """Response from approval metrics query."""
    
    period: str
    start_date: str
    end_date: str
    daily_metrics: List[DailyMetrics]
    summary: Dict[str, Any]


class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    
    id: str
    entity_type: str
    entity_id: str
    action: str
    tier: Optional[int]
    confidence: Optional[float]
    classification_reason: Optional[str]
    performed_by: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]]


class AuditLogResponse(BaseModel):
    """Response from audit log query."""
    
    total: int
    items: List[AuditLogEntry]
    limit: int
    offset: int