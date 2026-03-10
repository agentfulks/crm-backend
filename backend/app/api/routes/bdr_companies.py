"""BDR Companies endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.bdr_company import BDRCompany

router = APIRouter()


def _company_to_dict(c: BDRCompany) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "company_name": c.company_name,
        "industry": c.industry,
        "company_size": c.company_size,
        "headquarters_city": c.headquarters_city,
        "headquarters_state": c.headquarters_state,
        "headquarters_country": c.headquarters_country,
        "website_url": c.website_url,
        "linkedin_url": c.linkedin_url,
        "target_department": c.target_department,
        "ideal_buyer_persona": c.ideal_buyer_persona,
        "pain_points": c.pain_points,
        "use_case_fit": c.use_case_fit,
        "priority": c.priority,
        "status": c.status,
        "lead_source": c.lead_source,
        "icp_score": c.icp_score,
        "engagement_score": c.engagement_score,
        "assigned_bdr": c.assigned_bdr,
        "tags": c.tags,
        "is_flagged": bool(c.is_flagged),
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


class CompanyUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    use_case_fit: Optional[str] = None
    pain_points: Optional[str] = None
    icp_score: Optional[int] = None
    is_flagged: Optional[bool] = None


@router.get("/")
def list_bdr_companies(
    *,
    db: Session = Depends(get_db),
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    is_flagged: bool | None = Query(None, description="Filter by flagged status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List all BDR companies."""

    query = db.query(BDRCompany)

    if status:
        query = query.filter(BDRCompany.status == status)
    if priority:
        query = query.filter(BDRCompany.priority == priority)
    if is_flagged is not None:
        query = query.filter(BDRCompany.is_flagged == is_flagged)

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [_company_to_dict(c) for c in items],
    }


@router.get("/{company_id}")
def get_bdr_company(
    *,
    db: Session = Depends(get_db),
    company_id: str,
):
    """Get a single BDR company."""

    company = db.query(BDRCompany).filter(BDRCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return _company_to_dict(company)


@router.patch("/{company_id}")
def update_bdr_company(
    *,
    db: Session = Depends(get_db),
    company_id: str,
    body: CompanyUpdate,
):
    """Update a BDR company."""

    company = db.query(BDRCompany).filter(BDRCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return _company_to_dict(company)


# ── Bulk import ────────────────────────────────────────────────────────────────

class BulkCompanyItem(BaseModel):
    company_name: str
    website_url: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class BulkCompanyRequest(BaseModel):
    items: List[BulkCompanyItem]
    dry_run: bool = False


@router.post("/bulk")
def bulk_create_companies(
    *,
    db: Session = Depends(get_db),
    payload: BulkCompanyRequest,
):
    """Bulk-create BDR companies. Skips duplicates (matched by company_name).
    Pass dry_run=true to preview counts without writing."""
    created, skipped = 0, 0
    errors: List[dict] = []

    # Pre-fetch existing names for fast lookup
    existing_names = {
        row[0].lower()
        for row in db.query(func.lower(BDRCompany.company_name)).all()
    }

    for item in payload.items:
        if not item.company_name or not item.company_name.strip():
            errors.append({"name": "(empty)", "error": "company_name is required"})
            continue
        if item.company_name.lower() in existing_names:
            skipped += 1
            continue
        if payload.dry_run:
            created += 1
            existing_names.add(item.company_name.lower())
            continue
        try:
            data = item.model_dump(exclude_none=True)
            company = BDRCompany(**data)
            db.add(company)
            db.commit()
            db.refresh(company)
            created += 1
            existing_names.add(item.company_name.lower())
        except Exception as e:
            db.rollback()
            errors.append({"name": item.company_name, "error": str(e)})

    return {"created": created, "skipped": skipped, "errors": errors, "dry_run": payload.dry_run}


# ── Bulk delete ────────────────────────────────────────────────────────────────

class BulkDeleteRequest(BaseModel):
    ids: List[str]

@router.post("/bulk-delete")
def bulk_delete_bdr_companies(*, db: Session = Depends(get_db), payload: BulkDeleteRequest):
    """Delete multiple BDR companies by ID."""
    deleted = db.query(BDRCompany).filter(BDRCompany.id.in_(payload.ids)).delete(synchronize_session='fetch')
    db.commit()
    return {"deleted": deleted}
