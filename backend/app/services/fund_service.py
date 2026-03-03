"""Business logic for fund operations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import FundStatus, Priority
from app.models.fund import Fund


class FundSortField(str, Enum):
    """Sortable fund fields."""

    updated_at = "updated_at"
    score = "score"
    name = "name"


class SortDirection(str, Enum):
    """Sort direction values."""

    asc = "asc"
    desc = "desc"


@dataclass
class FundFilters:
    """Filter parameters for listing funds."""

    search: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[FundStatus] = None
    limit: int = 50
    offset: int = 0
    sort_by: FundSortField = FundSortField.updated_at
    sort_direction: SortDirection = SortDirection.desc


def list_funds(session: Session, filters: FundFilters) -> Tuple[List[Fund], int]:
    """Return filtered funds and total count."""

    conditions = []
    if filters.search:
        pattern = f"%{filters.search.lower()}%"
        conditions.append(
            or_(
                func.lower(Fund.name).like(pattern),
                func.lower(func.coalesce(Fund.overview, "")).like(pattern),
            )
        )
    if filters.priority:
        conditions.append(Fund.priority == filters.priority)
    if filters.status:
        conditions.append(Fund.status == filters.status)

    base_stmt = select(Fund)
    count_stmt = select(func.count()).select_from(Fund)
    if conditions:
        base_stmt = base_stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    order_expression = _ordering_expression(filters.sort_by, filters.sort_direction)
    base_stmt = base_stmt.order_by(order_expression, Fund.id)
    base_stmt = base_stmt.offset(filters.offset).limit(filters.limit)

    total = session.execute(count_stmt).scalar_one()
    items = session.scalars(base_stmt).all()
    return items, total


def create_fund(session: Session, payload: dict) -> Fund:
    """Create and persist a fund."""

    fund = Fund(**payload)
    session.add(fund)
    session.commit()
    session.refresh(fund)
    return fund


def update_fund(session: Session, fund: Fund, payload: dict) -> Fund:
    """Update a fund with provided fields."""

    for field, value in payload.items():
        setattr(fund, field, value)
    session.add(fund)
    session.commit()
    session.refresh(fund)
    return fund


def get_fund(session: Session, fund_id: str) -> Optional[Fund]:
    """Fetch a fund by primary key."""

    return session.get(Fund, fund_id)


def get_top_funds(session: Session, limit: int) -> List[Fund]:
    """Return funds sorted by score descending."""

    stmt = (
        select(Fund)
        .order_by(
            desc(Fund.score),
            desc(Fund.updated_at),
        )
        .limit(limit)
    )
    return session.scalars(stmt).all()


def delete_fund(session: Session, fund: Fund) -> None:
    """Delete a fund."""

    session.delete(fund)
    session.commit()


def _ordering_expression(sort_by: FundSortField, direction: SortDirection):
    column_map = {
        FundSortField.updated_at: Fund.updated_at,
        FundSortField.score: Fund.score,
        FundSortField.name: Fund.name,
    }
    column = column_map.get(sort_by, Fund.updated_at)
    if direction == SortDirection.asc:
        return asc(column)
    return desc(column)
