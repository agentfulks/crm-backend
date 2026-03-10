"""Business logic for contact operations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.contact import Contact


@dataclass
class ContactFilters:
    """Filter parameters for listing contacts."""

    fund_id: Optional[str] = None
    search: Optional[str] = None
    is_primary: Optional[bool] = None
    is_flagged: Optional[bool] = None
    limit: int = 100
    offset: int = 0
    sort_by: str = "created_at"
    sort_direction: str = "desc"


def list_contacts(session: Session, filters: ContactFilters) -> Tuple[List[Contact], int]:
    """Return filtered contacts and total count."""

    base_stmt = select(Contact).options(joinedload(Contact.fund))
    count_stmt = select(func.count()).select_from(Contact)

    conditions = []
    if filters.fund_id:
        conditions.append(Contact.fund_id == filters.fund_id)
    if filters.search:
        pattern = f"%{filters.search.lower()}%"
        conditions.append(
            or_(
                func.lower(Contact.full_name).like(pattern),
                func.lower(func.coalesce(Contact.email, "")).like(pattern),
                func.lower(func.coalesce(Contact.title, "")).like(pattern),
                func.lower(func.coalesce(Contact.phone, "")).like(pattern),
                func.lower(func.coalesce(Contact.department, "")).like(pattern),
            )
        )
    if filters.is_primary is not None:
        conditions.append(Contact.is_primary == filters.is_primary)
    if filters.is_flagged is not None:
        conditions.append(Contact.is_flagged == filters.is_flagged)

    if conditions:
        base_stmt = base_stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    order_expression = _ordering_expression(filters.sort_by, filters.sort_direction)
    base_stmt = base_stmt.order_by(order_expression, Contact.id)
    base_stmt = base_stmt.offset(filters.offset).limit(filters.limit)

    total = session.execute(count_stmt).scalar_one()
    items = session.scalars(base_stmt).unique().all()

    return items, total


def get_contact(session: Session, contact_id: str) -> Optional[Contact]:
    """Fetch a contact by ID with fund relationship."""

    stmt = select(Contact).options(joinedload(Contact.fund)).where(Contact.id == contact_id)
    return session.scalar(stmt)


def get_contacts_by_fund(session: Session, fund_id: str) -> List[Contact]:
    """Fetch all contacts for a specific fund."""

    stmt = (
        select(Contact)
        .where(Contact.fund_id == fund_id)
        .order_by(Contact.is_primary.desc(), Contact.full_name)
    )
    return session.scalars(stmt).all()


def create_contact(session: Session, payload: dict) -> Contact:
    """Create and persist a contact."""

    contact = Contact(**payload)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


def update_contact(session: Session, contact: Contact, payload: dict) -> Contact:
    """Update a contact with provided fields."""

    for field, value in payload.items():
        setattr(contact, field, value)

    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


def delete_contact(session: Session, contact: Contact) -> None:
    """Delete a contact."""

    session.delete(contact)
    session.commit()


def _ordering_expression(sort_by: str, sort_direction: str):
    """Build ordering expression for queries."""

    column_map = {
        "created_at": Contact.created_at,
        "updated_at": Contact.updated_at,
        "full_name": Contact.full_name,
        "is_primary": Contact.is_primary,
        "last_contacted_at": Contact.last_contacted_at,
    }

    column = column_map.get(sort_by, Contact.created_at)

    if sort_direction == "asc":
        return asc(column)
    return desc(column)
