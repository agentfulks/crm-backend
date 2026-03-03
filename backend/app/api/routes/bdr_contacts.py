"""BDR Contacts endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.bdr_contact import BDRContact

router = APIRouter()


@router.get("/")
def list_bdr_contacts(
    *,
    db: Session = Depends(get_db),
    company_id: str | None = Query(None, description="Filter by company ID"),
    is_decision_maker: bool | None = Query(None, description="Filter by decision maker"),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    """List all BDR contacts."""
    
    query = db.query(BDRContact)
    
    if company_id:
        query = query.filter(BDRContact.company_id == company_id)
    if is_decision_maker is not None:
        query = query.filter(BDRContact.is_decision_maker == is_decision_maker)
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
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
            for c in items
        ]
    }


@router.get("/{contact_id}")
def get_bdr_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
):
    """Get a single BDR contact."""
    
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {
        "id": str(contact.id),
        "company_id": str(contact.company_id),
        "full_name": contact.full_name,
        "job_title": contact.job_title,
        "department": contact.department,
        "seniority_level": contact.seniority_level,
        "email": contact.email,
        "phone": contact.phone,
        "linkedin_url": contact.linkedin_url,
        "is_decision_maker": contact.is_decision_maker,
        "is_champion": contact.is_champion,
        "email_verified": contact.email_verified,
        "timezone": contact.timezone,
        "last_contacted_at": contact.last_contacted_at.isoformat() if contact.last_contacted_at else None,
        "contact_preference": contact.contact_preference,
        "notes": contact.notes,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "updated_at": contact.updated_at.isoformat() if contact.updated_at else None,
    }


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
    full_name: str | None = None,
    job_title: str | None = None,
    email: str | None = None,
    linkedin_url: str | None = None,
    is_decision_maker: bool | None = None,
):
    """Update a BDR contact."""
    
    contact = db.query(BDRContact).filter(BDRContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if full_name:
        contact.full_name = full_name
    if job_title:
        contact.job_title = job_title
    if email:
        contact.email = email
    if linkedin_url:
        contact.linkedin_url = linkedin_url
    if is_decision_maker is not None:
        contact.is_decision_maker = is_decision_maker
    
    db.commit()
    db.refresh(contact)
    
    return {"id": str(contact.id), "message": "Contact updated successfully"}
