"""Meeting endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import MeetingStatus
from app.schemas.meeting import (
    MeetingCreate,
    MeetingFilters,
    MeetingListResponse,
    MeetingRead,
    MeetingSortField,
    MeetingUpdate,
    SortDirection,
)
from app.services import meeting_service

router = APIRouter()


@router.get("/", response_model=MeetingListResponse)
def list_meetings(
    *,
    db: Session = Depends(get_db),
    fund_id: str | None = Query(None, description="Filter by fund ID"),
    contact_id: str | None = Query(None, description="Filter by contact ID"),
    packet_id: str | None = Query(None, description="Filter by packet ID"),
    status: MeetingStatus | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: MeetingSortField = Query(MeetingSortField.scheduled_at),
    sort_direction: SortDirection = Query(SortDirection.desc),
) -> MeetingListResponse:
    """Return paginated meetings matching filters."""

    filters = MeetingFilters(
        fund_id=fund_id,
        contact_id=contact_id,
        packet_id=packet_id,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = meeting_service.list_meetings(db, filters)
    payload = [MeetingRead.model_validate(item, from_attributes=True) for item in items]
    return MeetingListResponse(total=total, items=payload)


@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(*, db: Session = Depends(get_db), payload: MeetingCreate) -> MeetingRead:
    """Create a meeting record."""

    meeting = meeting_service.create_meeting(db, payload.model_dump())
    return MeetingRead.model_validate(meeting, from_attributes=True)


@router.get("/{meeting_id}", response_model=MeetingRead)
def get_meeting(*, db: Session = Depends(get_db), meeting_id: str) -> MeetingRead:
    """Retrieve a meeting by ID."""

    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return MeetingRead.model_validate(meeting, from_attributes=True)


@router.patch("/{meeting_id}", response_model=MeetingRead)
def update_meeting(
    *,
    db: Session = Depends(get_db),
    meeting_id: str,
    payload: MeetingUpdate,
) -> MeetingRead:
    """Update fields on a meeting."""

    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    data = payload.model_dump(exclude_unset=True)
    meeting = meeting_service.update_meeting(db, meeting, data)
    return MeetingRead.model_validate(meeting, from_attributes=True)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(*, db: Session = Depends(get_db), meeting_id: str) -> None:
    """Delete a meeting."""

    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    meeting_service.delete_meeting(db, meeting)


@router.get("/fund/{fund_id}", response_model=list[MeetingRead])
def get_meetings_by_fund(
    *,
    db: Session = Depends(get_db),
    fund_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[MeetingRead]:
    """Get all meetings for a specific fund."""

    meetings = meeting_service.get_meetings_by_fund(db, fund_id, limit)
    return [MeetingRead.model_validate(item, from_attributes=True) for item in meetings]


@router.get("/contact/{contact_id}", response_model=list[MeetingRead])
def get_meetings_by_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[MeetingRead]:
    """Get all meetings for a specific contact."""

    meetings = meeting_service.get_meetings_by_contact(db, contact_id, limit)
    return [MeetingRead.model_validate(item, from_attributes=True) for item in meetings]


@router.get("/upcoming/list", response_model=list[MeetingRead])
def get_upcoming_meetings(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
) -> list[MeetingRead]:
    """Get upcoming scheduled meetings."""

    meetings = meeting_service.get_upcoming_meetings(db, limit)
    return [MeetingRead.model_validate(item, from_attributes=True) for item in meetings]


@router.post("/{meeting_id}/complete", response_model=MeetingRead)
def complete_meeting(*, db: Session = Depends(get_db), meeting_id: str) -> MeetingRead:
    """Mark a meeting as completed."""

    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    meeting = meeting_service.complete_meeting(db, meeting)
    return MeetingRead.model_validate(meeting, from_attributes=True)


@router.post("/{meeting_id}/cancel", response_model=MeetingRead)
def cancel_meeting(*, db: Session = Depends(get_db), meeting_id: str) -> MeetingRead:
    """Cancel a meeting."""

    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    meeting = meeting_service.cancel_meeting(db, meeting)
    return MeetingRead.model_validate(meeting, from_attributes=True)
