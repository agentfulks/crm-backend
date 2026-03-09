"""Funds endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import FundStatus, Priority
from app.schemas.fund import (
    FundCreate,
    FundListResponse,
    FundRead,
    FundUpdate,
)
from app.services import fund_service
from app.services.fund_service import FundFilters, FundSortField, SortDirection

router = APIRouter()


@router.get("/", response_model=FundListResponse)
def list_funds(
    *,
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search by fund name or overview"),
    priority: Priority | None = Query(None, description="Filter by priority"),
    status_filter: FundStatus | None = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_by: FundSortField = Query(FundSortField.updated_at),
    sort_direction: SortDirection = Query(SortDirection.desc),
) -> FundListResponse:
    """Return paginated funds matching filters."""

    filters = FundFilters(
        search=search,
        priority=priority,
        status=status_filter,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = fund_service.list_funds(db, filters)
    payload = [FundRead.model_validate(item, from_attributes=True) for item in items]
    return FundListResponse(total=total, items=payload)


@router.post("/", response_model=FundRead, status_code=status.HTTP_201_CREATED)
def create_fund(*, db: Session = Depends(get_db), payload: FundCreate) -> FundRead:
    """Create a fund record."""

    fund = fund_service.create_fund(db, payload.model_dump())
    return FundRead.model_validate(fund, from_attributes=True)


@router.get("/top", response_model=list[FundRead])
def get_top_funds(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=1, le=25, description="Maximum number of funds to return"),
) -> list[FundRead]:
    """Return the highest-scoring funds."""

    funds = fund_service.get_top_funds(db, limit)
    return [FundRead.model_validate(item, from_attributes=True) for item in funds]


@router.get("/{fund_id}", response_model=FundRead)
def get_fund(*, db: Session = Depends(get_db), fund_id: str) -> FundRead:
    """Retrieve a fund by id."""

    fund = fund_service.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund not found")
    return FundRead.model_validate(fund, from_attributes=True)


@router.patch("/{fund_id}", response_model=FundRead)
def update_fund(*, db: Session = Depends(get_db), fund_id: str, payload: FundUpdate) -> FundRead:
    """Update fields on a fund."""

    fund = fund_service.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund not found")
    data = payload.model_dump(exclude_unset=True)
    fund = fund_service.update_fund(db, fund, data)
    return FundRead.model_validate(fund, from_attributes=True)


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fund(
    *,
    db: Session = Depends(get_db),
    fund_id: str,
) -> None:
    """Delete a fund."""

    fund = fund_service.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund not found",
        )

    fund_service.delete_fund(db, fund)
