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
    phone: Optional[str] = Field(default=None, max_length=50)
    linkedin_url: Optional[str] = None
    department: Optional[str] = Field(default=None, max_length=100)
    seniority_level: Optional[str] = Field(default=None, max_length=50)
    is_primary: bool = False
    email_verified: bool = False
    is_flagged: bool = False
    timezone: Optional[str] = Field(default=None, max_length=100)
    last_contacted_at: Optional[datetime] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating a contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""

    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=320)
    phone: Optional[str] = Field(default=None, max_length=50)
    linkedin_url: Optional[str] = None
    department: Optional[str] = Field(default=None, max_length=100)
    seniority_level: Optional[str] = Field(default=None, max_length=50)
    is_primary: Optional[bool] = None
    email_verified: Optional[bool] = None
    is_flagged: Optional[bool] = None
    timezone: Optional[str] = Field(default=None, max_length=100)
    last_contacted_at: Optional[datetime] = None
    notes: Optional[str] = None


class ContactRead(ContactBase):
    """Contact response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    # Joined fund name for display (populated via joined load)
    fund_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        # Hydrate fund_name from the relationship if available
        if hasattr(obj, 'fund') and obj.fund is not None:
            instance.fund_name = obj.fund.name
        return instance


class ContactListResponse(BaseModel):
    """Paginated list of contacts."""

    total: int
    items: list[ContactRead]
