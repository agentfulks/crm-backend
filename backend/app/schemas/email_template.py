"""Email template schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class EmailTemplateBase(BaseModel):
    """Base email template schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    variables: str | None = None
    is_active: bool = True
    is_default: bool = False


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating an email template."""
    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    subject: str | None = Field(None, min_length=1, max_length=500)
    body: str | None = Field(None, min_length=1)
    variables: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class EmailTemplateRead(EmailTemplateBase):
    """Schema for reading an email template."""
    id: str
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    usage_count: int
    
    class Config:
        from_attributes = True
        
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class EmailTemplateListResponse(BaseModel):
    """Schema for listing email templates."""
    total: int
    items: List[EmailTemplateRead]
