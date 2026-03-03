"""Fund API schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FundStatus, Priority


class FundSortField(str, Enum):
    """Sortable fund fields."""

    updated_at = "updated_at"
    score = "score"
    name = "name"


class SortDirection(str, Enum):
    """Sorting direction options."""

    asc = "asc"
    desc = "desc"


class FundBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    firm_type: Optional[str] = Field(default=None, max_length=100)
    hq_city: Optional[str] = Field(default=None, max_length=100)
    hq_region: Optional[str] = Field(default=None, max_length=100)
    hq_country: Optional[str] = Field(default=None, max_length=100)
    stage_focus: List[str] = Field(default_factory=list)
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    check_size_currency: Optional[str] = Field(default=None, max_length=10)
    target_countries: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    funding_requirements: Optional[str] = None
    overview: Optional[str] = None
    contact_email: Optional[str] = None
    score: Optional[float] = None
    priority: Priority = Priority.B
    status: FundStatus = FundStatus.NEW
    data_source: Optional[str] = None
    source_row_id: Optional[str] = None
    tags: dict = Field(default_factory=dict)


class FundCreate(FundBase):
    """Payload for creating a fund."""

    pass


class FundUpdate(BaseModel):
    """Payload for updating a fund."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    firm_type: Optional[str] = Field(default=None, max_length=100)
    hq_city: Optional[str] = Field(default=None, max_length=100)
    hq_region: Optional[str] = Field(default=None, max_length=100)
    hq_country: Optional[str] = Field(default=None, max_length=100)
    stage_focus: Optional[List[str]] = None
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    check_size_currency: Optional[str] = Field(default=None, max_length=10)
    target_countries: Optional[List[str]] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    funding_requirements: Optional[str] = None
    overview: Optional[str] = None
    contact_email: Optional[str] = None
    score: Optional[float] = None
    priority: Optional[Priority] = None
    status: Optional[FundStatus] = None
    data_source: Optional[str] = None
    source_row_id: Optional[str] = None
    tags: Optional[dict] = None


class FundRead(FundBase):
    """Fund response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class FundListResponse(BaseModel):
    """Paginated list of funds."""

    total: int
    items: List[FundRead]
