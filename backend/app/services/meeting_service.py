"""Meeting service layer."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.schemas.meeting import MeetingFilters, MeetingSortField, SortDirection


def create_meeting(session: Session, data: dict) -> Meeting:
    """Create a new meeting."""
    meeting = Meeting(**data)
    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


def get_meeting(session: Session, meeting_id: str) -> Meeting | None:
    """Fetch a meeting by ID."""
    return session.query(Meeting).filter(Meeting.id == meeting_id).first()


def update_meeting(session: Session, meeting: Meeting, data: dict) -> Meeting:
    """Update meeting fields."""
    for key, value in data.items():
        setattr(meeting, key, value)
    session.commit()
    session.refresh(meeting)
    return meeting


def delete_meeting(session: Session, meeting: Meeting) -> None:
    """Delete a meeting."""
    session.delete(meeting)
    session.commit()


def list_meetings(session: Session, filters: MeetingFilters) -> tuple[list[Meeting], int]:
    """List meetings with filtering and pagination."""
    query = session.query(Meeting)

    if filters.fund_id:
        query = query.filter(Meeting.fund_id == filters.fund_id)
    if filters.contact_id:
        query = query.filter(Meeting.contact_id == filters.contact_id)
    if filters.packet_id:
        query = query.filter(Meeting.packet_id == filters.packet_id)
    if filters.status:
        query = query.filter(Meeting.status == filters.status)

    total = query.count()

    # Apply sorting
    sort_column = getattr(Meeting, filters.sort_by.value)
    if filters.sort_direction == SortDirection.desc:
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    query = query.offset(filters.offset).limit(filters.limit)
    return query.all(), total


def get_meetings_by_fund(session: Session, fund_id: str, limit: int = 50) -> list[Meeting]:
    """Get all meetings for a specific fund."""
    return (
        session.query(Meeting)
        .filter(Meeting.fund_id == fund_id)
        .order_by(Meeting.scheduled_at.desc())
        .limit(limit)
        .all()
    )


def get_meetings_by_contact(session: Session, contact_id: str, limit: int = 50) -> list[Meeting]:
    """Get all meetings for a specific contact."""
    return (
        session.query(Meeting)
        .filter(Meeting.contact_id == contact_id)
        .order_by(Meeting.scheduled_at.desc())
        .limit(limit)
        .all()
    )


def get_upcoming_meetings(session: Session, limit: int = 10) -> list[Meeting]:
    """Get upcoming scheduled meetings."""
    from datetime import datetime

    return (
        session.query(Meeting)
        .filter(Meeting.scheduled_at >= datetime.utcnow())
        .filter(Meeting.status == "PLANNED")
        .order_by(Meeting.scheduled_at.asc())
        .limit(limit)
        .all()
    )


def complete_meeting(session: Session, meeting: Meeting) -> Meeting:
    """Mark a meeting as completed."""
    from app.models.enums import MeetingStatus

    meeting.status = MeetingStatus.COMPLETED
    session.commit()
    session.refresh(meeting)
    return meeting


def cancel_meeting(session: Session, meeting: Meeting) -> Meeting:
    """Mark a meeting as cancelled."""
    from app.models.enums import MeetingStatus

    meeting.status = MeetingStatus.CANCELLED
    session.commit()
    session.refresh(meeting)
    return meeting
