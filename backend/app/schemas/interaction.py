"""Interaction API schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import InteractionDirection, InteractionType


class InteractionSortField(str, Enum):
    """Sortable interaction fields."""

    occurred_at = "occurred_at"
    created_at = "created_at"
    interaction_type = "interaction_type"


class SortDirection(str, Enum):
    """Sorting direction options."""

    asc = "asc"
    desc = "desc"


class InteractionBase(BaseModel):
    """Base interaction schema."""

    fund_id: str = Field(..., description="ID of the associated fund")
    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact (optional)")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    direction: Optional[InteractionDirection] = Field(default=None, description="Direction of interaction")
    subject: Optional[str] = Field(default=None, max_length=500, description="Subject/title of interaction")
    content: Optional[str] = Field(default=None, description="Content/body of interaction")
    occurred_at: Optional[datetime] = Field(default=None, description="When the interaction occurred")
    created_by: Optional[str] = Field(default=None, max_length=255, description="Who recorded the interaction")
    source_id: Optional[str] = Field(default=None, max_length=100, description="ID from source system (e.g., email ID)")
    source_table: Optional[str] = Field(default=None, max_length=50, description="Origin table if migrated")
    meta: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class InteractionCreate(InteractionBase):
    """Payload for creating an interaction."""

    pass


class InteractionUpdate(BaseModel):
    """Payload for updating an interaction."""

    fund_id: Optional[str] = Field(default=None, description="ID of the associated fund")
    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact")
    interaction_type: Optional[InteractionType] = Field(default=None, description="Type of interaction")
    direction: Optional[InteractionDirection] = Field(default=None, description="Direction of interaction")
    subject: Optional[str] = Field(default=None, max_length=500, description="Subject/title of interaction")
    content: Optional[str] = Field(default=None, description="Content/body of interaction")
    occurred_at: Optional[datetime] = Field(default=None, description="When the interaction occurred")
    created_by: Optional[str] = Field(default=None, max_length=255, description="Who recorded the interaction")
    source_id: Optional[str] = Field(default=None, max_length=100, description="ID from source system")
    source_table: Optional[str] = Field(default=None, max_length=50, description="Origin table if migrated")
    meta: Optional[dict] = Field(default=None, description="Additional metadata")


class InteractionRead(InteractionBase):
    """Interaction response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class InteractionListResponse(BaseModel):
    """Paginated list of interactions."""

    total: int
    items: List[InteractionRead]


class InteractionFilters(BaseModel):
    """Filter parameters for listing interactions."""

    fund_id: Optional[str] = Field(default=None, description="Filter by fund ID")
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID")
    interaction_type: Optional[InteractionType] = Field(default=None, description="Filter by type")
    direction: Optional[InteractionDirection] = Field(default=None, description="Filter by direction")
    created_by: Optional[str] = Field(default=None, description="Filter by creator")
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: InteractionSortField = Field(default=InteractionSortField.created_at)
    sort_direction: SortDirection = Field(default=SortDirection.desc)
