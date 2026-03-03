"""Packet schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import PacketStatus, Priority
from app.schemas.fund import FundRead


class PacketBase(BaseModel):
    """Base packet fields."""

    fund_id: str
    trello_card_id: Optional[str] = None
    trello_card_url: Optional[str] = None
    status: PacketStatus = PacketStatus.QUEUED
    priority: Priority = Priority.B
    score_snapshot: Optional[float] = None
    created_by: Optional[str] = None


class PacketCreate(PacketBase):
    """Schema for creating a packet."""

    pass


class PacketRead(PacketBase):
    """Schema for reading a packet."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    fund: Optional[FundRead] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    follow_up_due: Optional[datetime] = None
    crm_status: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class PacketUpdate(BaseModel):
    """Schema for updating a packet."""

    status: Optional[PacketStatus] = None
    priority: Optional[Priority] = None
    score_snapshot: Optional[float] = None
    trello_card_id: Optional[str] = None
    trello_card_url: Optional[str] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    follow_up_due: Optional[datetime] = None
    crm_status: Optional[dict] = None


class PacketListResponse(BaseModel):
    """Paginated packet list response."""

    total: int
    items: list[PacketRead]


class QueueStatus(BaseModel):
    """Daily queue status summary."""

    date: str
    total_queued: int
    awaiting_approval: int
    approved_today: int
    sent_today: int


class PacketActionResponse(BaseModel):
    """Response after approve/reject action."""

    success: bool
    packet: PacketRead
    message: str
