"""Pydantic schemas for KanbanCard."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class KanbanCardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    column: str = "backlog"
    position: int = 0
    card_type: str = "custom"
    source_id: Optional[str] = None
    source_data: Optional[Dict[str, Any]] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class KanbanCardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    column: Optional[str] = None
    position: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    source_data: Optional[Dict[str, Any]] = None


class KanbanCardRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    column: str
    position: int
    card_type: str
    source_id: Optional[str] = None
    source_data: Optional[Dict[str, Any]] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
