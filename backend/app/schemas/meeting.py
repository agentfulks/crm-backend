"""Meeting API schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MeetingStatus


class MeetingSortField(str, Enum):
    """Sortable meeting fields."""

    scheduled_at = "scheduled_at"
    created_at = "created_at"
    status = "status"


class SortDirection(str, Enum):
    """Sorting direction options."""

    asc = "asc"
    desc = "desc"


class MeetingBase(BaseModel):
    """Base meeting fields."""

    fund_id: str = Field(..., description="ID of the associated fund")
    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact (optional)")
    packet_id: Optional[str] = Field(default=None, description="ID of the associated packet (optional)")
    scheduled_at: Optional[datetime] = Field(default=None, description="When the meeting is scheduled")
    status: MeetingStatus = Field(default=MeetingStatus.PLANNED, description="Meeting status")
    meeting_url: Optional[str] = Field(default=None, description="URL for virtual meeting")
    notes: Optional[str] = Field(default=None, description="Meeting notes")


class MeetingCreate(MeetingBase):
    """Payload for creating a meeting."""

    pass


class MeetingUpdate(BaseModel):
    """Payload for updating a meeting."""

    scheduled_at: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    meeting_url: Optional[str] = None
    notes: Optional[str] = None


class MeetingRead(MeetingBase):
    """Meeting response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class MeetingListResponse(BaseModel):
    """Paginated list of meetings."""

    total: int
    items: list[MeetingRead]


class MeetingFilters(BaseModel):
    """Filter parameters for listing meetings."""

    fund_id: Optional[str] = Field(default=None, description="Filter by fund ID")
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID")
    packet_id: Optional[str] = Field(default=None, description="Filter by packet ID")
    status: Optional[MeetingStatus] = Field(default=None, description="Filter by status")
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: MeetingSortField = Field(default=MeetingSortField.scheduled_at)
    sort_direction: SortDirection = Field(default=SortDirection.desc)
