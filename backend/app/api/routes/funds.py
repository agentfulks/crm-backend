"""Funds endpoints."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import FundStatus, Priority
from app.models.fund import Fund
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


# ── Bulk import ────────────────────────────────────────────────────────────────

class BulkFundItem(BaseModel):
    name: str
    website_url: Optional[str] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    firm_type: Optional[str] = None
    stage_focus: Optional[str] = None   # comma-separated → list
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    overview: Optional[str] = None
    contact_email: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class BulkFundRequest(BaseModel):
    items: List[BulkFundItem]
    dry_run: bool = False


@router.post("/bulk")
def bulk_create_funds(
    *,
    db: Session = Depends(get_db),
    payload: BulkFundRequest,
):
    """Bulk-create VC funds. Skips duplicates matched by fund name."""
    created, skipped = 0, 0
    errors: List[dict] = []

    existing_names = {
        row[0].lower()
        for row in db.query(func.lower(Fund.name)).all()
    }

    for item in payload.items:
        if not item.name or not item.name.strip():
            errors.append({"name": "(empty)", "error": "name is required"})
            continue
        if item.name.lower() in existing_names:
            skipped += 1
            continue
        if payload.dry_run:
            created += 1
            existing_names.add(item.name.lower())
            continue
        try:
            data = item.model_dump(exclude_none=True)
            # Convert comma-separated stage_focus string → list
            if "stage_focus" in data and isinstance(data["stage_focus"], str):
                data["stage_focus"] = [s.strip() for s in data["stage_focus"].split(",") if s.strip()]
            fund = Fund(**data)
            db.add(fund)
            db.commit()
            db.refresh(fund)
            created += 1
            existing_names.add(item.name.lower())
        except Exception as e:
            db.rollback()
            errors.append({"name": item.name, "error": str(e)})

    return {"created": created, "skipped": skipped, "errors": errors, "dry_run": payload.dry_run}


# ── Bulk delete ────────────────────────────────────────────────────────────────

class BulkDeleteRequest(BaseModel):
    ids: List[str]

@router.post("/bulk-delete")
def bulk_delete_funds(*, db: Session = Depends(get_db), payload: BulkDeleteRequest):
    """Delete multiple funds by ID."""
    deleted = db.query(Fund).filter(Fund.id.in_(payload.ids)).delete(synchronize_session='fetch')
    db.commit()
    return {"deleted": deleted}
