"""Pydantic models for contact enrichment."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class EnrichmentSource(str, Enum):
    """Sources for contact enrichment."""
    APOLLO = "apollo"
    HUNTER = "hunter"
    LINKEDIN = "linkedin"
    MANUAL = "manual"


class ContactRole(str, Enum):
    """Common VC roles."""
    PARTNER = "Partner"
    MANAGING_PARTNER = "Managing Partner"
    GENERAL_PARTNER = "General Partner"
    PRINCIPAL = "Principal"
    VP = "VP"
    ASSOCIATE = "Associate"
    ANALYST = "Analyst"
    FOUNDER = "Founder"
    CEO = "CEO"
    INVESTMENT_MANAGER = "Investment Manager"
    UNKNOWN = "Unknown"


class RawContact(BaseModel):
    """Raw contact data from enrichment source."""
    
    source: EnrichmentSource
    source_id: str
    
    # Identity
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Contact info
    email: Optional[str] = None
    email_verified: bool = False
    email_type: Optional[str] = None  # personal, work, generic
    
    # Professional
    title: Optional[str] = None
    role: ContactRole = ContactRole.UNKNOWN
    department: Optional[str] = None
    seniority: Optional[str] = None  # entry, senior, executive
    
    # Links
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    
    # Company context
    fund_name: Optional[str] = None
    fund_website: Optional[str] = None
    
    # Enrichment metadata
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    enrichment_date: Optional[datetime] = None
    
    # Raw data
    tags: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class EnrichmentResult(BaseModel):
    """Result of enrichment operation for a fund."""
    
    fund_id: str
    fund_name: str
    
    # Contacts found
    contacts_found: List[RawContact] = Field(default_factory=list)
    
    # Stats
    total_contacts: int = 0
    emails_found: int = 0
    emails_verified: int = 0
    
    # Status
    status: str = Field(default="pending", pattern="^(pending|processing|completed|failed)$")
    error_message: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EnrichmentJob(BaseModel):
    """Configuration for enrichment job."""
    
    job_id: str
    fund_ids: List[str] = Field(default_factory=list)
    
    # Enrichment sources to use
    sources: List[EnrichmentSource] = Field(
        default_factory=lambda: [EnrichmentSource.APOLLO, EnrichmentSource.HUNTER]
    )
    
    # Filtering
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    required_roles: List[ContactRole] = Field(default_factory=list)
    max_contacts_per_fund: int = Field(default=10, ge=1, le=50)
    
    # API config
    apollo_api_key: Optional[str] = None
    hunter_api_key: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Behavior
    dry_run: bool = False
    overwrite_existing: bool = False


class EnrichmentBatch(BaseModel):
    """Batch enrichment run."""
    
    batch_id: str
    job: EnrichmentJob
    
    # Results
    results: List[EnrichmentResult] = Field(default_factory=list)
    
    # Aggregate stats
    total_funds: int = 0
    funds_completed: int = 0
    funds_failed: int = 0
    total_contacts_found: int = 0
    total_emails_found: int = 0
    
    # Status
    status: str = "running"
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
