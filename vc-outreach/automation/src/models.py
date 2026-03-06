"""Pydantic models for source automation."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DataSource(str, Enum):
    """External data sources for VC ingestion."""
    CRUNCHBASE = "crunchbase"
    APOLLO = "apollo"
    MANUAL = "manual"


class FundStage(str, Enum):
    """Investment stages."""
    SEED = "seed"
    PRE_SEED = "pre_seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    LATE_STAGE = "late_stage"


class RawFund(BaseModel):
    """Raw fund data from external source before processing."""
    
    # Source tracking
    data_source: DataSource
    source_id: str = Field(description="Original ID from the source system")
    
    # Core fund info
    name: str
    firm_type: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    
    # Location
    hq_city: Optional[str] = None
    hq_region: Optional[str] = None
    hq_country: Optional[str] = None
    
    # Investment focus
    stage_focus: List[str] = Field(default_factory=list)
    sector_focus: List[str] = Field(default_factory=list)
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    check_size_currency: str = "USD"
    target_countries: List[str] = Field(default_factory=list)
    
    # Description
    overview: Optional[str] = None
    funding_requirements: Optional[str] = None
    
    # Metadata
    tags: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('stage_focus', 'sector_focus', 'target_countries', mode='before')
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [x.strip() for x in v.split(',') if x.strip()]
        return v


class ProcessedFund(RawFund):
    """Fund data after processing with deduplication info."""
    
    matched_fund_id: Optional[str] = None
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    match_reason: Optional[str] = None
    action: str = Field(default="create", pattern="^(create|update|skip)$")
    

class SyncRun(BaseModel):
    """Record of a sync operation."""
    
    id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    data_source: DataSource
    status: str = Field(default="running", pattern="^(running|completed|failed)$")
    
    # Stats
    records_fetched: int = 0
    records_new: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    

class SyncConfig(BaseModel):
    """Configuration for a sync job."""
    
    data_source: DataSource
    enabled: bool = True
    schedule: str = Field(default="0 6 * * *", description="Cron expression")
    
    # Filtering options
    target_sectors: List[str] = Field(default_factory=lambda: ["gaming", "ai", "artificial intelligence"])
    stage_focus: List[str] = Field(default_factory=lambda: ["seed", "series_a", "series_b"])
    min_check_size: Optional[float] = None
    max_check_size: Optional[float] = None
    
    # API configuration
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    rate_limit_per_minute: int = 60
    
    # Deduplication settings
    dedupe_threshold: float = Field(default=0.85, ge=0.0, le=1.0)


class DeduplicationResult(BaseModel):
    """Result of deduplication check."""
    
    is_duplicate: bool
    matched_fund_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    matching_fields: List[str] = Field(default_factory=list)
