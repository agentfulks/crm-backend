"""Outreach attempt API schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OutreachChannel, OutreachStatus


class OutreachSortField(str, Enum):
    """Sortable outreach attempt fields."""

    created_at = "created_at"
    sent_at = "sent_at"
    responded_at = "responded_at"


class SortDirection(str, Enum):
    """Sorting direction options."""

    asc = "asc"
    desc = "desc"


class OutreachAttemptBase(BaseModel):
    """Base outreach attempt schema."""

    packet_id: str = Field(..., description="ID of the associated packet")
    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact (optional)")
    channel: OutreachChannel = Field(..., description="Channel used for outreach")
    status: OutreachStatus = Field(default=OutreachStatus.DRAFT, description="Current status")
    subject: Optional[str] = Field(default=None, max_length=255, description="Subject/title")
    body_preview: Optional[str] = Field(default=None, description="Preview of the message body")
    sent_at: Optional[datetime] = Field(default=None, description="When the outreach was sent")
    responded_at: Optional[datetime] = Field(default=None, description="When a response was received")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class OutreachAttemptCreate(OutreachAttemptBase):
    """Payload for creating an outreach attempt."""

    pass


class OutreachAttemptUpdate(BaseModel):
    """Payload for updating an outreach attempt."""

    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact")
    channel: Optional[OutreachChannel] = Field(default=None, description="Channel used for outreach")
    status: Optional[OutreachStatus] = Field(default=None, description="Current status")
    subject: Optional[str] = Field(default=None, max_length=255, description="Subject/title")
    body_preview: Optional[str] = Field(default=None, description="Preview of the message body")
    sent_at: Optional[datetime] = Field(default=None, description="When the outreach was sent")
    responded_at: Optional[datetime] = Field(default=None, description="When a response was received")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class OutreachAttemptRead(OutreachAttemptBase):
    """Outreach attempt response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class OutreachAttemptListResponse(BaseModel):
    """Paginated list of outreach attempts."""

    total: int
    items: List[OutreachAttemptRead]


class OutreachAttemptFilters(BaseModel):
    """Filter parameters for listing outreach attempts."""

    packet_id: Optional[str] = Field(default=None, description="Filter by packet ID")
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID")
    channel: Optional[OutreachChannel] = Field(default=None, description="Filter by channel")
    status: Optional[OutreachStatus] = Field(default=None, description="Filter by status")
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: OutreachSortField = Field(default=OutreachSortField.created_at)
    sort_direction: SortDirection = Field(default=SortDirection.desc)


class OutreachStatusUpdate(BaseModel):
    """Payload for updating outreach status."""

    status: OutreachStatus
    notes: Optional[str] = Field(default=None, description="Additional notes about the status change")


class OutreachActionResponse(BaseModel):
    """Response after an outreach action (mark sent, mark responded, etc.)."""

    success: bool
    outreach_attempt: OutreachAttemptRead
    message: str
