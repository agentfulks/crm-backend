"""Contact endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.vc_outreach_log import VCOutreachLog
from app.schemas.contact import (
    ContactCreate,
    ContactListResponse,
    ContactRead,
    ContactUpdate,
)
from app.services.contact_service import (
    ContactFilters,
    create_contact,
    delete_contact,
    get_contact,
    get_contacts_by_fund,
    list_contacts,
    update_contact,
)

router = APIRouter()


# ── CRUD endpoints ─────────────────────────────────────────────────────────────


@router.get("/", response_model=ContactListResponse)
def list_contacts_endpoint(
    *,
    db: Session = Depends(get_db),
    fund_id: str | None = Query(None, description="Filter by fund ID"),
    search: str | None = Query(None, description="Search by name, email, title, phone, or department"),
    is_primary: bool | None = Query(None, description="Filter by primary status"),
    is_flagged: bool | None = Query(None, description="Filter by flagged status"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_direction: str = Query("desc", description="Sort direction: asc or desc"),
) -> ContactListResponse:
    """Return paginated contacts matching filters."""
    filters = ContactFilters(
        fund_id=fund_id,
        search=search,
        is_primary=is_primary,
        is_flagged=is_flagged,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = list_contacts(db, filters)
    payload = [ContactRead.model_validate(item, from_attributes=True) for item in items]
    return ContactListResponse(total=total, items=payload)


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact_endpoint(*, db: Session = Depends(get_db), payload: ContactCreate) -> ContactRead:
    """Create a contact record."""
    contact = create_contact(db, payload.model_dump())
    return ContactRead.model_validate(contact, from_attributes=True)


@router.get("/fund/{fund_id}", response_model=list[ContactRead])
def get_contacts_by_fund_endpoint(*, db: Session = Depends(get_db), fund_id: str) -> list[ContactRead]:
    """Get all contacts for a specific fund."""
    contacts = get_contacts_by_fund(db, fund_id)
    return [ContactRead.model_validate(item, from_attributes=True) for item in contacts]


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact_endpoint(*, db: Session = Depends(get_db), contact_id: str) -> ContactRead:
    """Retrieve a contact by ID."""
    contact = get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return ContactRead.model_validate(contact, from_attributes=True)


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact_endpoint(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    payload: ContactUpdate,
) -> ContactRead:
    """Update fields on a contact."""
    contact = get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    data = payload.model_dump(exclude_unset=True)
    contact = update_contact(db, contact, data)
    return ContactRead.model_validate(contact, from_attributes=True)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact_endpoint(*, db: Session = Depends(get_db), contact_id: str) -> None:
    """Delete a contact."""
    contact = get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    delete_contact(db, contact)


# ── Outreach log endpoints ──────────────────────────────────────────────────────


class OutreachIn(BaseModel):
    channel: str
    subject: Optional[str] = None
    body: Optional[str] = None


@router.get("/{contact_id}/outreach")
def list_outreach_logs(*, db: Session = Depends(get_db), contact_id: str):
    """Get outreach history for a VC contact, newest first."""
    contact = get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    logs = (
        db.query(VCOutreachLog)
        .filter(VCOutreachLog.contact_id == contact_id)
        .order_by(VCOutreachLog.sent_at.desc())
        .all()
    )
    items = [
        {
            "id": str(log.id),
            "contact_id": str(log.contact_id),
            "channel": log.channel,
            "subject": log.subject,
            "body": log.body,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
        }
        for log in logs
    ]
    return {"total": len(items), "items": items}


@router.post("/{contact_id}/outreach", status_code=status.HTTP_201_CREATED)
def create_outreach_log(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    payload: OutreachIn,
):
    """Record an outreach attempt and update last_contacted_at."""
    contact = get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    log = VCOutreachLog(
        contact_id=contact_id,
        channel=payload.channel,
        subject=payload.subject,
        body=payload.body,
        sent_at=datetime.utcnow(),
    )
    db.add(log)

    # Update last_contacted_at on the contact
    contact.last_contacted_at = datetime.utcnow()  # type: ignore[assignment]
    db.commit()
    db.refresh(log)

    return {
        "id": str(log.id),
        "contact_id": str(log.contact_id),
        "channel": log.channel,
        "subject": log.subject,
        "body": log.body,
        "sent_at": log.sent_at.isoformat() if log.sent_at else None,
    }


@router.delete("/{contact_id}/outreach/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outreach_log(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    log_id: str,
):
    """Delete a specific outreach log entry."""
    log = (
        db.query(VCOutreachLog)
        .filter(VCOutreachLog.contact_id == contact_id, VCOutreachLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log)
    db.commit()
