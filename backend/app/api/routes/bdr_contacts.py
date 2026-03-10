"""BDR Contacts endpoints."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.bdr_company import BDRCompany
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
    is_flagged: Optional[bool] = None


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
        "is_flagged": bool(c.is_flagged),
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@router.get("/")
def list_bdr_contacts(
    *,
    db: Session = Depends(get_db),
    company_id: str | None = Query(None),
    is_decision_maker: bool | None = Query(None),
    is_flagged: bool | None = Query(None, description="If true, only flagged contacts; if false, only non-flagged"),
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
    if is_flagged is not None:
        query = query.filter(BDRContact.is_flagged == is_flagged)

    # last_contacted filters
    # last_contacted_at is TIMESTAMPTZ (tz-aware) in the DB, so we must compare
    # with tz-aware datetimes. We also use date.fromisoformat() to safely handle
    # date-only strings like "2026-03-09" (datetime.fromisoformat raises ValueError
    # for date-only strings on Python < 3.11).
    def _day_start(s: str) -> datetime:
        """Parse a date string → UTC midnight (tz-aware)."""
        return datetime.combine(date.fromisoformat(s), time.min, tzinfo=timezone.utc)

    def _day_end(s: str) -> datetime:
        """Parse a date string → UTC end-of-day (tz-aware)."""
        return datetime.combine(date.fromisoformat(s), time.max, tzinfo=timezone.utc)

    if never_contacted:
        query = query.filter(BDRContact.last_contacted_at.is_(None))
    else:
        if last_contacted_on:
            query = query.filter(
                BDRContact.last_contacted_at >= _day_start(last_contacted_on),
                BDRContact.last_contacted_at <= _day_end(last_contacted_on),
            )
        else:
            if last_contacted_after:
                query = query.filter(BDRContact.last_contacted_at >= _day_start(last_contacted_after))
            if last_contacted_before:
                query = query.filter(BDRContact.last_contacted_at <= _day_end(last_contacted_before))

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


class ContactCreate(BaseModel):
    company_id: str
    full_name: str
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    is_decision_maker: bool = False
    email_verified: bool = False


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_bdr_contact(
    *,
    db: Session = Depends(get_db),
    payload: ContactCreate,
):
    """Create a new BDR contact."""
    # Duplicate-email guard
    if payload.email:
        existing = (
            db.query(BDRContact)
            .filter(
                BDRContact.company_id == payload.company_id,
                BDRContact.email == payload.email,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A contact with email '{payload.email}' already exists for this company.",
            )

    contact = BDRContact(
        company_id=payload.company_id,
        full_name=payload.full_name,
        job_title=payload.job_title,
        email=payload.email,
        phone=payload.phone,
        linkedin_url=payload.linkedin_url,
        is_decision_maker=payload.is_decision_maker,
        email_verified=payload.email_verified,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return _contact_to_dict(contact)


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
    if body.is_flagged is not None:
        contact.is_flagged = body.is_flagged

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


# ── Bulk import ────────────────────────────────────────────────────────────────

class BulkContactItem(BaseModel):
    company_name: str          # resolved to company_id server-side
    full_name: str
    email: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_decision_maker: bool = False


class BulkContactRequest(BaseModel):
    items: List[BulkContactItem]
    dry_run: bool = False


@router.post("/bulk")
def bulk_create_contacts(
    *,
    db: Session = Depends(get_db),
    payload: BulkContactRequest,
):
    """Bulk-create BDR contacts. Looks up company by name. Skips email dupes."""
    created, skipped = 0, 0
    errors: List[dict] = []

    # Cache: company_name.lower() → company_id
    company_cache: Dict[str, str] = {}

    # Pre-fetch existing (company_id, email) pairs for dupe check
    existing_pairs = {
        (str(r[0]), (r[1] or "").lower())
        for r in db.query(BDRContact.company_id, BDRContact.email).all()
    }

    for item in payload.items:
        label = f"{item.full_name} <{item.email}>"
        if not item.full_name or not item.full_name.strip():
            errors.append({"name": label, "error": "full_name is required"})
            continue

        # Resolve company
        name_key = item.company_name.strip().lower()
        if name_key not in company_cache:
            company = db.query(BDRCompany).filter(
                func.lower(BDRCompany.company_name) == name_key
            ).first()
            if not company:
                errors.append({"name": label, "error": f"Company '{item.company_name}' not found"})
                continue
            company_cache[name_key] = str(company.id)
        company_id = company_cache[name_key]

        # Dupe check by email within company
        if item.email:
            pair = (company_id, item.email.lower())
            if pair in existing_pairs:
                skipped += 1
                continue

        if payload.dry_run:
            created += 1
            if item.email:
                existing_pairs.add((company_id, item.email.lower()))
            continue

        try:
            contact = BDRContact(
                company_id=company_id,
                full_name=item.full_name,
                email=item.email,
                job_title=item.job_title,
                phone=item.phone,
                linkedin_url=item.linkedin_url,
                is_decision_maker=item.is_decision_maker,
            )
            db.add(contact)
            db.commit()
            db.refresh(contact)
            created += 1
            if item.email:
                existing_pairs.add((company_id, item.email.lower()))
        except Exception as e:
            db.rollback()
            errors.append({"name": label, "error": str(e)})

    return {"created": created, "skipped": skipped, "errors": errors, "dry_run": payload.dry_run}
