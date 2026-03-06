"""Data models for the tiered approval system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class CardTier(Enum):
    """Priority tiers for card classification."""
    P0 = "P0"  # Urgent review required
    P1 = "P1"  # Batch approval eligible
    P2 = "P2"  # Auto-archive candidate


@dataclass
class ApprovalRule:
    """Defines criteria for tier classification.
    
    Attributes:
        min_fit_score: Minimum fit score threshold (0-100)
        max_fit_score: Maximum fit score threshold (0-100)
        max_days_in_queue: Maximum days card can sit before escalation
        funding_stages: List of eligible funding stages
        portfolio_match_required: Whether portfolio match is required
        tier: The CardTier this rule assigns
    """
    min_fit_score: int
    max_fit_score: int
    max_days_in_queue: Optional[int] = None
    funding_stages: List[str] = field(default_factory=list)
    portfolio_match_required: bool = False
    tier: CardTier = CardTier.P2


@dataclass
class CardSnapshot:
    """Snapshot of card metadata for approval processing.
    
    Attributes:
        id: Unique card identifier
        name: Card title/name
        description: Card description
        fit_score: Fit score (0-100)
        funding_stage: Company funding stage
        portfolio_match: Whether card matches portfolio criteria
        days_in_queue: Days since card entered queue
        created_at: Card creation timestamp
        last_activity: Last activity timestamp
        labels: List of card labels/tags
        custom_fields: Additional card metadata
    """
    id: str
    name: str
    description: str = ""
    fit_score: int = 0
    funding_stage: str = ""
    portfolio_match: bool = False
    days_in_queue: int = 0
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    labels: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def summary(self) -> str:
        """Returns a one-line summary of the card."""
        return f"[{self.id}] {self.name} (Fit: {self.fit_score}, Days: {self.days_in_queue})"


@dataclass
class BatchResult:
    """Result of a batch approval operation.
    
    Attributes:
        approved_ids: List of successfully approved card IDs
        failed_ids: List of card IDs that failed approval
        skipped_ids: List of card IDs that were skipped
        timestamp: When the batch operation completed
    """
    approved_ids: List[str] = field(default_factory=list)
    failed_ids: List[str] = field(default_factory=list)
    skipped_ids: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success_count(self) -> int:
        return len(self.approved_ids)
    
    @property
    def failure_count(self) -> int:
        return len(self.failed_ids)
    
    @property
    def skip_count(self) -> int:
        return len(self.skipped_ids)


@dataclass
class ArchiveResult:
    """Result of an archive operation.
    
    Attributes:
        archived_ids: List of archived card IDs
        failed_ids: List of card IDs that failed archiving
        reason: Why these cards were archived
        timestamp: When the archive operation completed
    """
    archived_ids: List[str] = field(default_factory=list)
    failed_ids: List[str] = field(default_factory=list)
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def archived_count(self) -> int:
        return len(self.archived_ids)
