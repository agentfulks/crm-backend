"""BDR Contacts endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.bdr_contact import BDRContact
from app.models.bdr_outreach_log import BDROutreachLog

router = APIRouter()


# ─── Pydantic schemas ──────────────────────────────────────────────────────────

class ContactUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_decision_maker: Optional[bool] = None
    is_champion: Optional[bool] = None
    email_verified: Optional[bool] = None
    timezone: Optional[str] = None
    last_contacted_at: Optional[str] = None   # ISO string
    contact_preference: Optional[str] = None  # 'email' | 'linkedin'
    notes: Optional[str] = None
    reset_last_contacted: bool = False        # if True, clears last_contacted_at + contact_preference


class OutreachLogCreate(BaseModel):
    channel: str           # 'email' | 'linkedin'
    subject: Optional[str] = None
    body: Optional[str] = None


# ─── Contact endpoints ─────────────────────────────────────────────────────────

def _contact_to_dict(c: BDRContact) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "company_id": str(c.company_id),
        "full_name": c.full_name,
        "job_title": c.job_title,
        "department": c.department,
        "seniority_level": c.seniority_level,
        "email": c.email,
        "phone": c.phone,
        "linkedin_url": c.linkedin_url,
        "is_decision_maker": c.is_decision_maker,
        "is_champion": c.is_champion,
        "email_verified": c.email_verified,
        "timezone": c.timezone,
        "last_contacted_at": c.last_contacted_at.isoformat() if c.last_contacted_at else None,
        "contact_preference": c.contact_preference,
        "notes": c.notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@router.get("/")
def list_bdr_contacts(
    *,
    db: Session = Depends(get_db),
    company_id: str | None = Query(None),
    is_decision_maker: bool | None = Query(None),
    # last_contacted filters
    never_contacted: bool | None = Query(None, description="If true, only contacts never contacted"),
    last_contacted_after: str | None = Query(None, description="ISO date – contacts last contacted after this date (inclusive)"),
    last_contacted_before: str | None = Query(None, description="ISO date – contacts last contacted before this date (inclusive)"),
    last_contacted_on: str | None = Query(None, description="ISO date – contacts last contacted on this exact day"),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    """List all BDR contacts with optional filters."""
    query = db.query(BDRContact)

    if company_id:
        query = query.filter(BDRContact.company_id == company_id)
    if is_decision_maker is not None:
        query = query.filter(BDRContact.is_decision_maker == is_decision_maker)

    # last_contacted filters
    if never_contacted:
        query = query.filter(BDRContact.last_contacted_at.is_(None))
    else:
        if last_contacted_on:
            # Exact calendar day (midnight → midnight+1)
            day_start = datetime.fromisoformat(last_contacted_on).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(BDRContact.last_contacted_at >= day_start, BDRContact.last_contacted_at <= day_end)
        else:
            if last_contacted_after:
                after_dt = datetime.fromisoformat(last_contacted_after).replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(BDRContact.last_contacted_at >= after_dt)
            if last_contacted_before:
                before_dt = datetime.fromisoformat(last_contacted_before).replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.filter(BDRContact.last_contacted_at <= before_dt)

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return {"total": total, "items": [_contact_to_dict(c) for c in items]}


@router.get("/{contact_id}")
def get_bdr_contact(*, db: Session = Depends(get_db), contact_id: str):
    """Get a single BDR contact."""
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _contact_to_dict(contact)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_bdr_contact(
    *,
    db: Session = Depends(get_db),
    company_id: str,
    full_name: str,
    job_title: str | None = None,
    email: str | None = None,
    linkedin_url: str | None = None,
    is_decision_maker: bool = False,
):
    """Create a new BDR contact."""
    contact = BDRContact(
        company_id=company_id,
        full_name=full_name,
        job_title=job_title,
        email=email,
        linkedin_url=linkedin_url,
        is_decision_maker=is_decision_maker,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"id": str(contact.id), "message": "Contact created successfully"}


@router.patch("/{contact_id}")
def update_bdr_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    body: ContactUpdate,
):
    """Update a BDR contact (accepts JSON body)."""
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if body.full_name is not None:
        contact.full_name = body.full_name
    if body.job_title is not None:
        contact.job_title = body.job_title
    if body.department is not None:
        contact.department = body.department
    if body.email is not None:
        contact.email = body.email
    if body.phone is not None:
        contact.phone = body.phone
    if body.linkedin_url is not None:
        contact.linkedin_url = body.linkedin_url
    if body.is_decision_maker is not None:
        contact.is_decision_maker = body.is_decision_maker
    if body.is_champion is not None:
        contact.is_champion = body.is_champion
    if body.email_verified is not None:
        contact.email_verified = body.email_verified
    if body.timezone is not None:
        contact.timezone = body.timezone
    if body.reset_last_contacted:
        contact.last_contacted_at = None
        contact.contact_preference = None
    else:
        if body.last_contacted_at is not None:
            contact.last_contacted_at = datetime.fromisoformat(
                body.last_contacted_at.replace("Z", "+00:00")
            )
        if body.contact_preference is not None:
            contact.contact_preference = body.contact_preference
    if body.notes is not None:
        contact.notes = body.notes

    db.commit()
    db.refresh(contact)
    return _contact_to_dict(contact)


# ─── Outreach log endpoints ────────────────────────────────────────────────────

def _log_to_dict(log: BDROutreachLog) -> Dict[str, Any]:
    return {
        "id": str(log.id),
        "contact_id": str(log.contact_id),
        "channel": log.channel,
        "subject": log.subject,
        "body": log.body,
        "sent_at": log.sent_at.isoformat() if log.sent_at else None,
    }


@router.get("/{contact_id}/outreach")
def list_outreach_logs(*, db: Session = Depends(get_db), contact_id: str):
    """Get outreach history for a contact, newest first."""
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    logs = (
        db.query(BDROutreachLog)
        .filter(BDROutreachLog.contact_id == contact_id)
        .order_by(BDROutreachLog.sent_at.desc())
        .all()
    )
    return {"total": len(logs), "items": [_log_to_dict(l) for l in logs]}


@router.post("/{contact_id}/outreach", status_code=status.HTTP_201_CREATED)
def create_outreach_log(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    body: OutreachLogCreate,
):
    """Record an outreach attempt with the message content."""
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    log = BDROutreachLog(
        contact_id=contact_id,
        channel=body.channel,
        subject=body.subject,
        body=body.body,
        sent_at=datetime.utcnow(),
    )
    db.add(log)

    # Also update the contact's last_contacted_at and preference
    contact.last_contacted_at = log.sent_at
    contact.contact_preference = body.channel

    db.commit()
    db.refresh(log)
    return _log_to_dict(log)


@router.delete("/{contact_id}/outreach/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outreach_log(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    log_id: str,
):
    """Delete a specific outreach log entry."""
    log = (
        db.query(BDROutreachLog)
        .filter(BDROutreachLog.id == log_id, BDROutreachLog.contact_id == contact_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Outreach log not found")
    db.delete(log)
    db.commit()
    return
