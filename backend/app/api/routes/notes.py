"""Note endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import NoteVisibility
from app.schemas.note import (
    NoteCreate,
    NoteFilters,
    NoteListResponse,
    NoteRead,
    NoteUpdate,
)
from app.services import note_service

router = APIRouter()


@router.get("/", response_model=NoteListResponse)
def list_notes(
    *,
    db: Session = Depends(get_db),
    fund_id: str | None = Query(None, description="Filter by fund ID"),
    contact_id: str | None = Query(None, description="Filter by contact ID"),
    visibility: NoteVisibility | None = Query(None, description="Filter by visibility"),
    pinned: bool | None = Query(None, description="Filter by pinned status"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> NoteListResponse:
    """Return paginated notes matching filters."""

    filters = NoteFilters(
        fund_id=fund_id,
        contact_id=contact_id,
        visibility=visibility,
        pinned=pinned,
        limit=limit,
        offset=offset,
    )
    items, total = note_service.list_notes(db, filters)
    payload = [NoteRead.model_validate(item, from_attributes=True) for item in items]
    return NoteListResponse(total=total, items=payload)


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(*, db: Session = Depends(get_db), payload: NoteCreate) -> NoteRead:
    """Create a note record."""

    note = note_service.create_note(db, payload.model_dump())
    return NoteRead.model_validate(note, from_attributes=True)


@router.get("/fund/{fund_id}", response_model=list[NoteRead])
def get_notes_by_fund(
    *,
    db: Session = Depends(get_db),
    fund_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[NoteRead]:
    """Get all notes for a specific fund."""

    notes = note_service.get_notes_by_fund(db, fund_id, limit)
    return [NoteRead.model_validate(item, from_attributes=True) for item in notes]


@router.get("/contact/{contact_id}", response_model=list[NoteRead])
def get_notes_by_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[NoteRead]:
    """Get all notes for a specific contact."""

    notes = note_service.get_notes_by_contact(db, contact_id, limit)
    return [NoteRead.model_validate(item, from_attributes=True) for item in notes]


@router.get("/{note_id}", response_model=NoteRead)
def get_note(*, db: Session = Depends(get_db), note_id: str) -> NoteRead:
    """Retrieve a note by ID."""

    note = note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return NoteRead.model_validate(note, from_attributes=True)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    *,
    db: Session = Depends(get_db),
    note_id: str,
    payload: NoteUpdate,
) -> NoteRead:
    """Update fields on a note."""

    note = note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    data = payload.model_dump(exclude_unset=True)
    note = note_service.update_note(db, note, data)
    return NoteRead.model_validate(note, from_attributes=True)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(*, db: Session = Depends(get_db), note_id: str) -> None:
    """Delete a note."""

    note = note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note_service.delete_note(db, note)


@router.post("/{note_id}/pin", response_model=NoteRead)
def pin_note(*, db: Session = Depends(get_db), note_id: str) -> NoteRead:
    """Pin a note."""

    note = note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note = note_service.pin_note(db, note)
    return NoteRead.model_validate(note, from_attributes=True)


@router.post("/{note_id}/unpin", response_model=NoteRead)
def unpin_note(*, db: Session = Depends(get_db), note_id: str) -> NoteRead:
    """Unpin a note."""

    note = note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note = note_service.unpin_note(db, note)
    return NoteRead.model_validate(note, from_attributes=True)
