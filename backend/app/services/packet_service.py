"""Business logic for packet operations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import PacketStatus
from app.models.packet import Packet


@dataclass
class PacketFilters:
    """Filter parameters for listing packets."""

    status: Optional[PacketStatus] = None
    priority: Optional[str] = None
    fund_id: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "created_at"
    sort_direction: str = "desc"


def list_packets(session: Session, filters: PacketFilters) -> Tuple[List[Packet], int]:
    """Return filtered packets with total count."""

    # Build base query with fund relationship
    base_stmt = select(Packet).options(joinedload(Packet.fund))
    count_stmt = select(func.count()).select_from(Packet)

    # Apply filters
    conditions = []
    if filters.status:
        conditions.append(Packet.status == filters.status)
    if filters.priority:
        conditions.append(Packet.priority == filters.priority)
    if filters.fund_id:
        conditions.append(Packet.fund_id == filters.fund_id)

    if conditions:
        base_stmt = base_stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    # Apply sorting
    order_expression = _ordering_expression(filters.sort_by, filters.sort_direction)
    base_stmt = base_stmt.order_by(order_expression, Packet.id)

    # Apply pagination
    base_stmt = base_stmt.offset(filters.offset).limit(filters.limit)

    # Execute queries
    total = session.execute(count_stmt).scalar_one()
    items = session.scalars(base_stmt).unique().all()

    return items, total


def get_packet(session: Session, packet_id: str) -> Optional[Packet]:
    """Fetch a packet by ID with fund relationship."""

    stmt = select(Packet).options(joinedload(Packet.fund)).where(Packet.id == packet_id)
    return session.scalar(stmt)


def create_packet(session: Session, payload: dict) -> Packet:
    """Create and persist a new packet."""

    packet = Packet(**payload)
    session.add(packet)
    session.commit()
    session.refresh(packet)
    return packet


def update_packet(session: Session, packet: Packet, payload: dict) -> Packet:
    """Update a packet with provided fields."""

    for field, value in payload.items():
        if value is not None:
            setattr(packet, field, value)

    packet.updated_at = datetime.now()
    session.add(packet)
    session.commit()
    session.refresh(packet)
    return packet


def approve_packet(session: Session, packet: Packet) -> Packet:
    """Approve a packet for sending."""

    packet.status = PacketStatus.APPROVED
    packet.approved_at = datetime.now()
    packet.updated_at = datetime.now()
    session.add(packet)
    session.commit()
    session.refresh(packet)
    return packet


def reject_packet(session: Session, packet: Packet) -> Packet:
    """Reject/close a packet."""

    packet.status = PacketStatus.CLOSED
    packet.updated_at = datetime.now()
    session.add(packet)
    session.commit()
    session.refresh(packet)
    return packet


def get_pending_packets(session: Session, limit: int = 50) -> List[Packet]:
    """Get packets awaiting approval."""

    stmt = (
        select(Packet)
        .options(joinedload(Packet.fund))
        .where(Packet.status == PacketStatus.AWAITING_APPROVAL)
        .order_by(desc(Packet.score_snapshot), desc(Packet.created_at))
        .limit(limit)
    )
    return session.scalars(stmt).unique().all()


def get_queue_status(session: Session) -> dict:
    """Get daily queue status summary."""

    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # Count by status
    total_queued = session.scalar(
        select(func.count()).where(Packet.status == PacketStatus.QUEUED)
    ) or 0

    awaiting_approval = session.scalar(
        select(func.count()).where(Packet.status == PacketStatus.AWAITING_APPROVAL)
    ) or 0

    approved_today = session.scalar(
        select(func.count()).where(
            Packet.status == PacketStatus.APPROVED,
            Packet.approved_at >= today_start,
            Packet.approved_at <= today_end,
        )
    ) or 0

    sent_today = session.scalar(
        select(func.count()).where(
            Packet.status == PacketStatus.SENT,
            Packet.sent_at >= today_start,
            Packet.sent_at <= today_end,
        )
    ) or 0

    return {
        "date": today.isoformat(),
        "total_queued": total_queued,
        "awaiting_approval": awaiting_approval,
        "approved_today": approved_today,
        "sent_today": sent_today,
    }


def delete_packet(session: Session, packet: Packet) -> None:
    """Delete a packet."""

    session.delete(packet)
    session.commit()


def _ordering_expression(sort_by: str, sort_direction: str):
    """Build ordering expression for queries."""

    column_map = {
        "created_at": Packet.created_at,
        "updated_at": Packet.updated_at,
        "approved_at": Packet.approved_at,
        "sent_at": Packet.sent_at,
        "score_snapshot": Packet.score_snapshot,
        "priority": Packet.priority,
    }

    column = column_map.get(sort_by, Packet.created_at)

    if sort_direction == "asc":
        return asc(column)
    return desc(column)
