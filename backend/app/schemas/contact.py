"""Contact API schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContactBase(BaseModel):
    """Base contact fields."""

    fund_id: str
    full_name: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=320)
    linkedin_url: Optional[str] = None
    is_primary: bool = False
    timezone: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating a contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""

    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=320)
    linkedin_url: Optional[str] = None
    is_primary: Optional[bool] = None
    timezone: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class ContactRead(ContactBase):
    """Contact response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    """Paginated list of contacts."""

    total: int
    items: list[ContactRead]
