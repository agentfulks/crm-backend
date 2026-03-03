"""Outreach attempt endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import OutreachChannel, OutreachStatus
from app.schemas.outreach_attempt import (
    OutreachActionResponse,
    OutreachAttemptCreate,
    OutreachAttemptFilters,
    OutreachAttemptListResponse,
    OutreachAttemptRead,
    OutreachAttemptUpdate,
    OutreachSortField,
    SortDirection,
    OutreachStatusUpdate,
)
from app.services import outreach_service

router = APIRouter()


@router.get("/", response_model=OutreachAttemptListResponse)
def list_outreach_attempts(
    *,
    db: Session = Depends(get_db),
    packet_id: str | None = Query(None, description="Filter by packet ID"),
    contact_id: str | None = Query(None, description="Filter by contact ID"),
    channel: OutreachChannel | None = Query(None, description="Filter by channel"),
    status: OutreachStatus | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: OutreachSortField = Query(OutreachSortField.created_at),
    sort_direction: SortDirection = Query(SortDirection.desc),
) -> OutreachAttemptListResponse:
    """Return paginated outreach attempts matching filters."""

    filters = outreach_service.OutreachFilters(
        packet_id=packet_id,
        contact_id=contact_id,
        channel=channel,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = outreach_service.list_outreach_attempts(db, filters)
    payload = [OutreachAttemptRead.model_validate(item, from_attributes=True) for item in items]
    return OutreachAttemptListResponse(total=total, items=payload)


@router.post("/", response_model=OutreachAttemptRead, status_code=status.HTTP_201_CREATED)
def create_outreach_attempt(
    *,
    db: Session = Depends(get_db),
    payload: OutreachAttemptCreate,
) -> OutreachAttemptRead:
    """Create an outreach attempt record."""

    outreach = outreach_service.create_outreach_attempt(db, payload.model_dump())
    return OutreachAttemptRead.model_validate(outreach, from_attributes=True)


@router.get("/{outreach_id}", response_model=OutreachAttemptRead)
def get_outreach_attempt(
    *,
    db: Session = Depends(get_db),
    outreach_id: str,
) -> OutreachAttemptRead:
    """Retrieve an outreach attempt by ID."""

    outreach = outreach_service.get_outreach_attempt(db, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach attempt not found",
        )
    return OutreachAttemptRead.model_validate(outreach, from_attributes=True)


@router.patch("/{outreach_id}", response_model=OutreachAttemptRead)
def update_outreach_attempt(
    *,
    db: Session = Depends(get_db),
    outreach_id: str,
    payload: OutreachAttemptUpdate,
) -> OutreachAttemptRead:
    """Update fields on an outreach attempt."""

    outreach = outreach_service.get_outreach_attempt(db, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach attempt not found",
        )

    data = payload.model_dump(exclude_unset=True)
    outreach = outreach_service.update_outreach_attempt(db, outreach, data)
    return OutreachAttemptRead.model_validate(outreach, from_attributes=True)


@router.delete("/{outreach_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outreach_attempt(
    *,
    db: Session = Depends(get_db),
    outreach_id: str,
) -> None:
    """Delete an outreach attempt."""

    outreach = outreach_service.get_outreach_attempt(db, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach attempt not found",
        )

    outreach_service.delete_outreach_attempt(db, outreach)


@router.get("/packet/{packet_id}", response_model=list[OutreachAttemptRead])
def get_outreach_attempts_by_packet(
    *,
    db: Session = Depends(get_db),
    packet_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[OutreachAttemptRead]:
    """Get all outreach attempts for a specific packet."""

    attempts = outreach_service.get_outreach_attempts_by_packet(db, packet_id, limit)
    return [OutreachAttemptRead.model_validate(item, from_attributes=True) for item in attempts]


@router.get("/contact/{contact_id}", response_model=list[OutreachAttemptRead])
def get_outreach_attempts_by_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[OutreachAttemptRead]:
    """Get all outreach attempts for a specific contact."""

    attempts = outreach_service.get_outreach_attempts_by_contact(db, contact_id, limit)
    return [OutreachAttemptRead.model_validate(item, from_attributes=True) for item in attempts]


@router.post("/{outreach_id}/mark-sent", response_model=OutreachActionResponse)
def mark_as_sent(
    *,
    db: Session = Depends(get_db),
    outreach_id: str,
) -> OutreachActionResponse:
    """Mark an outreach attempt as sent."""

    outreach = outreach_service.get_outreach_attempt(db, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach attempt not found",
        )

    outreach = outreach_service.mark_as_sent(db, outreach)
    return OutreachActionResponse(
        success=True,
        outreach_attempt=OutreachAttemptRead.model_validate(outreach, from_attributes=True),
        message="Outreach marked as sent",
    )


@router.post("/{outreach_id}/mark-responded", response_model=OutreachActionResponse)
def mark_as_responded(
    *,
    db: Session = Depends(get_db),
    outreach_id: str,
) -> OutreachActionResponse:
    """Mark an outreach attempt as responded."""

    outreach = outreach_service.get_outreach_attempt(db, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach attempt not found",
        )

    outreach = outreach_service.mark_as_responded(db, outreach)
    return OutreachActionResponse(
        success=True,
        outreach_attempt=OutreachAttemptRead.model_validate(outreach, from_attributes=True),
        message="Outreach marked as responded",
    )
