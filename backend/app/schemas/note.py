"""Note API schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NoteVisibility


class NoteBase(BaseModel):
    """Base note fields."""

    fund_id: str = Field(..., description="ID of the associated fund")
    contact_id: Optional[str] = Field(default=None, description="ID of the associated contact (optional)")
    author: str = Field(..., min_length=1, max_length=255, description="Author of the note")
    body: str = Field(..., min_length=1, description="Note content")
    visibility: NoteVisibility = Field(default=NoteVisibility.INTERNAL, description="Visibility level")
    pinned: bool = Field(default=False, description="Whether the note is pinned")


class NoteCreate(NoteBase):
    """Payload for creating a note."""

    pass


class NoteUpdate(BaseModel):
    """Payload for updating a note."""

    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, min_length=1)
    visibility: Optional[NoteVisibility] = None
    pinned: Optional[bool] = None


class NoteRead(NoteBase):
    """Note response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """Paginated list of notes."""

    total: int
    items: list[NoteRead]


class NoteFilters(BaseModel):
    """Filter parameters for listing notes."""

    fund_id: Optional[str] = Field(default=None, description="Filter by fund ID")
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID")
    visibility: Optional[NoteVisibility] = Field(default=None, description="Filter by visibility")
    pinned: Optional[bool] = Field(default=None, description="Filter by pinned status")
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
