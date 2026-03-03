"""Business logic for interaction operations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.enums import InteractionDirection, InteractionType
from app.models.interaction import Interaction


@dataclass
class InteractionFilters:
    """Filter parameters for listing interactions."""

    fund_id: Optional[str] = None
    contact_id: Optional[str] = None
    interaction_type: Optional[InteractionType] = None
    direction: Optional[InteractionDirection] = None
    created_by: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "created_at"
    sort_direction: str = "desc"


def list_interactions(session: Session, filters: InteractionFilters) -> Tuple[List[Interaction], int]:
    """Return filtered interactions and total count."""

    conditions = []
    if filters.fund_id:
        conditions.append(Interaction.fund_id == filters.fund_id)
    if filters.contact_id:
        conditions.append(Interaction.contact_id == filters.contact_id)
    if filters.interaction_type:
        conditions.append(Interaction.interaction_type == filters.interaction_type)
    if filters.direction:
        conditions.append(Interaction.direction == filters.direction)
    if filters.created_by:
        conditions.append(Interaction.created_by == filters.created_by)

    base_stmt = select(Interaction)
    count_stmt = select(func.count()).select_from(Interaction)
    if conditions:
        base_stmt = base_stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    order_expression = _ordering_expression(filters.sort_by, filters.sort_direction)
    base_stmt = base_stmt.order_by(order_expression, Interaction.id)
    base_stmt = base_stmt.offset(filters.offset).limit(filters.limit)

    total = session.execute(count_stmt).scalar_one()
    items = session.scalars(base_stmt).all()
    return items, total


def create_interaction(session: Session, payload: dict) -> Interaction:
    """Create and persist an interaction."""

    interaction = Interaction(**payload)
    session.add(interaction)
    session.commit()
    session.refresh(interaction)
    return interaction


def update_interaction(session: Session, interaction: Interaction, payload: dict) -> Interaction:
    """Update an interaction with provided fields."""

    for field, value in payload.items():
        setattr(interaction, field, value)
    session.add(interaction)
    session.commit()
    session.refresh(interaction)
    return interaction


def get_interaction(session: Session, interaction_id: str) -> Optional[Interaction]:
    """Fetch an interaction by primary key."""

    return session.get(Interaction, interaction_id)


def get_interactions_by_fund(
    session: Session, fund_id: str, limit: int = 50
) -> List[Interaction]:
    """Return interactions for a specific fund."""

    stmt = (
        select(Interaction)
        .where(Interaction.fund_id == fund_id)
        .order_by(desc(Interaction.created_at))
        .limit(limit)
    )
    return session.scalars(stmt).all()


def get_interactions_by_contact(
    session: Session, contact_id: str, limit: int = 50
) -> List[Interaction]:
    """Return interactions for a specific contact."""

    stmt = (
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(desc(Interaction.created_at))
        .limit(limit)
    )
    return session.scalars(stmt).all()


def delete_interaction(session: Session, interaction: Interaction) -> None:
    """Delete an interaction."""

    session.delete(interaction)
    session.commit()


def create_email_interaction(
    session: Session,
    fund_id: str,
    subject: str,
    content: str,
    direction: InteractionDirection,
    contact_id: Optional[str] = None,
    created_by: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
) -> Interaction:
    """Convenience method to create an email interaction."""

    return create_interaction(
        session,
        {
            "fund_id": fund_id,
            "contact_id": contact_id,
            "interaction_type": InteractionType.EMAIL,
            "direction": direction,
            "subject": subject,
            "content": content,
            "created_by": created_by,
            "occurred_at": occurred_at or datetime.now(),
        },
    )


def create_note_interaction(
    session: Session,
    fund_id: str,
    content: str,
    contact_id: Optional[str] = None,
    created_by: Optional[str] = None,
) -> Interaction:
    """Convenience method to create a note interaction."""

    return create_interaction(
        session,
        {
            "fund_id": fund_id,
            "contact_id": contact_id,
            "interaction_type": InteractionType.NOTE,
            "content": content,
            "created_by": created_by,
            "occurred_at": datetime.now(),
        },
    )


def create_meeting_interaction(
    session: Session,
    fund_id: str,
    subject: str,
    content: str,
    contact_id: Optional[str] = None,
    created_by: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
) -> Interaction:
    """Convenience method to create a meeting interaction."""

    return create_interaction(
        session,
        {
            "fund_id": fund_id,
            "contact_id": contact_id,
            "interaction_type": InteractionType.MEETING,
            "subject": subject,
            "content": content,
            "created_by": created_by,
            "occurred_at": occurred_at or datetime.now(),
        },
    )


def _ordering_expression(sort_by: str, sort_direction: str):
    """Build ordering expression for queries."""

    column_map = {
        "created_at": Interaction.created_at,
        "occurred_at": Interaction.occurred_at,
        "interaction_type": Interaction.interaction_type,
    }
    column = column_map.get(sort_by, Interaction.created_at)
    if sort_direction == "asc":
        return asc(column)
    return desc(column)
