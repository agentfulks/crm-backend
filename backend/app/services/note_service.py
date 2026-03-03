"""Note service layer."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteFilters


def create_note(session: Session, data: dict) -> Note:
    """Create a new note."""
    note = Note(**data)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def get_note(session: Session, note_id: str) -> Note | None:
    """Fetch a note by ID."""
    return session.query(Note).filter(Note.id == note_id).first()


def update_note(session: Session, note: Note, data: dict) -> Note:
    """Update note fields."""
    for key, value in data.items():
        setattr(note, key, value)
    session.commit()
    session.refresh(note)
    return note


def delete_note(session: Session, note: Note) -> None:
    """Delete a note."""
    session.delete(note)
    session.commit()


def list_notes(session: Session, filters: NoteFilters) -> tuple[list[Note], int]:
    """List notes with filtering and pagination."""
    query = session.query(Note)

    if filters.fund_id:
        query = query.filter(Note.fund_id == filters.fund_id)
    if filters.contact_id:
        query = query.filter(Note.contact_id == filters.contact_id)
    if filters.visibility:
        query = query.filter(Note.visibility == filters.visibility)
    if filters.pinned is not None:
        query = query.filter(Note.pinned == filters.pinned)

    total = query.count()

    # Default sort by pinned first, then created_at desc
    query = query.order_by(Note.pinned.desc(), Note.created_at.desc())
    query = query.offset(filters.offset).limit(filters.limit)

    return query.all(), total


def get_notes_by_fund(session: Session, fund_id: str, limit: int = 50) -> list[Note]:
    """Get all notes for a specific fund."""
    return (
        session.query(Note)
        .filter(Note.fund_id == fund_id)
        .order_by(Note.pinned.desc(), Note.created_at.desc())
        .limit(limit)
        .all()
    )


def get_notes_by_contact(session: Session, contact_id: str, limit: int = 50) -> list[Note]:
    """Get all notes for a specific contact."""
    return (
        session.query(Note)
        .filter(Note.contact_id == contact_id)
        .order_by(Note.created_at.desc())
        .limit(limit)
        .all()
    )


def pin_note(session: Session, note: Note) -> Note:
    """Pin a note."""
    note.pinned = True
    session.commit()
    session.refresh(note)
    return note


def unpin_note(session: Session, note: Note) -> Note:
    """Unpin a note."""
    note.pinned = False
    session.commit()
    session.refresh(note)
    return note
