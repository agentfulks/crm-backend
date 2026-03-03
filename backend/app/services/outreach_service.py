"""Business logic for outreach attempt operations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.enums import OutreachChannel, OutreachStatus
from app.models.outreach_attempt import OutreachAttempt


@dataclass
class OutreachFilters:
    """Filter parameters for listing outreach attempts."""

    packet_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: Optional[OutreachChannel] = None
    status: Optional[OutreachStatus] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "created_at"
    sort_direction: str = "desc"


def list_outreach_attempts(session: Session, filters: OutreachFilters) -> Tuple[List[OutreachAttempt], int]:
    """Return filtered outreach attempts and total count."""

    conditions = []
    if filters.packet_id:
        conditions.append(OutreachAttempt.packet_id == filters.packet_id)
    if filters.contact_id:
        conditions.append(OutreachAttempt.contact_id == filters.contact_id)
    if filters.channel:
        conditions.append(OutreachAttempt.channel == filters.channel)
    if filters.status:
        conditions.append(OutreachAttempt.status == filters.status)

    base_stmt = select(OutreachAttempt)
    count_stmt = select(func.count()).select_from(OutreachAttempt)
    if conditions:
        base_stmt = base_stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    order_expression = _ordering_expression(filters.sort_by, filters.sort_direction)
    base_stmt = base_stmt.order_by(order_expression, OutreachAttempt.id)
    base_stmt = base_stmt.offset(filters.offset).limit(filters.limit)

    total = session.execute(count_stmt).scalar_one()
    items = session.scalars(base_stmt).all()
    return items, total


def create_outreach_attempt(session: Session, payload: dict) -> OutreachAttempt:
    """Create and persist an outreach attempt."""

    outreach = OutreachAttempt(**payload)
    session.add(outreach)
    session.commit()
    session.refresh(outreach)
    return outreach


def update_outreach_attempt(
    session: Session, outreach: OutreachAttempt, payload: dict
) -> OutreachAttempt:
    """Update an outreach attempt with provided fields."""

    for field, value in payload.items():
        setattr(outreach, field, value)
    session.add(outreach)
    session.commit()
    session.refresh(outreach)
    return outreach


def get_outreach_attempt(session: Session, outreach_id: str) -> Optional[OutreachAttempt]:
    """Fetch an outreach attempt by primary key."""

    return session.get(OutreachAttempt, outreach_id)


def get_outreach_attempts_by_packet(
    session: Session, packet_id: str, limit: int = 50
) -> List[OutreachAttempt]:
    """Return outreach attempts for a specific packet."""

    stmt = (
        select(OutreachAttempt)
        .where(OutreachAttempt.packet_id == packet_id)
        .order_by(desc(OutreachAttempt.created_at))
        .limit(limit)
    )
    return session.scalars(stmt).all()


def get_outreach_attempts_by_contact(
    session: Session, contact_id: str, limit: int = 50
) -> List[OutreachAttempt]:
    """Return outreach attempts for a specific contact."""

    stmt = (
        select(OutreachAttempt)
        .where(OutreachAttempt.contact_id == contact_id)
        .order_by(desc(OutreachAttempt.created_at))
        .limit(limit)
    )
    return session.scalars(stmt).all()


def delete_outreach_attempt(session: Session, outreach: OutreachAttempt) -> None:
    """Delete an outreach attempt."""

    session.delete(outreach)
    session.commit()


def mark_as_sent(session: Session, outreach: OutreachAttempt) -> OutreachAttempt:
    """Mark an outreach attempt as sent."""

    outreach.status = OutreachStatus.SENT
    outreach.sent_at = datetime.now()
    session.add(outreach)
    session.commit()
    session.refresh(outreach)
    return outreach


def mark_as_responded(session: Session, outreach: OutreachAttempt) -> OutreachAttempt:
    """Mark an outreach attempt as responded."""

    outreach.status = OutreachStatus.RESPONDED
    outreach.responded_at = datetime.now()
    session.add(outreach)
    session.commit()
    session.refresh(outreach)
    return outreach


def _ordering_expression(sort_by: str, sort_direction: str):
    """Build ordering expression for queries."""

    column_map = {
        "created_at": OutreachAttempt.created_at,
        "sent_at": OutreachAttempt.sent_at,
        "responded_at": OutreachAttempt.responded_at,
    }
    column = column_map.get(sort_by, OutreachAttempt.created_at)
    if sort_direction == "asc":
        return asc(column)
    return desc(column)
