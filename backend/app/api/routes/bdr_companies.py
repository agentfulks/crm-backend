"""BDR Companies endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.bdr_company import BDRCompany

router = APIRouter()


@router.get("/")
def list_bdr_companies(
    *,
    db: Session = Depends(get_db),
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List all BDR companies."""
    
    query = db.query(BDRCompany)
    
    if status:
        query = query.filter(BDRCompany.status == status)
    if priority:
        query = query.filter(BDRCompany.priority == priority)
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": str(c.id),
                "company_name": c.company_name,
                "industry": c.industry,
                "company_size": c.company_size,
                "headquarters_city": c.headquarters_city,
                "headquarters_state": c.headquarters_state,
                "headquarters_country": c.headquarters_country,
                "website_url": c.website_url,
                "target_department": c.target_department,
                "ideal_buyer_persona": c.ideal_buyer_persona,
                "priority": c.priority,
                "status": c.status,
                "lead_source": c.lead_source,
                "icp_score": c.icp_score,
                "use_case_fit": c.use_case_fit,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in items
        ]
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
    
    return {
        "id": str(company.id),
        "company_name": company.company_name,
        "industry": company.industry,
        "company_size": company.company_size,
        "headquarters_city": company.headquarters_city,
        "headquarters_state": company.headquarters_state,
        "headquarters_country": company.headquarters_country,
        "website_url": company.website_url,
        "target_department": company.target_department,
        "ideal_buyer_persona": company.ideal_buyer_persona,
        "priority": company.priority,
        "status": company.status,
        "lead_source": company.lead_source,
        "icp_score": company.icp_score,
        "use_case_fit": company.use_case_fit,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


@router.patch("/{company_id}")
def update_bdr_company(
    *,
    db: Session = Depends(get_db),
    company_id: str,
    status: str | None = None,
    priority: str | None = None,
):
    """Update a BDR company."""
    
    company = db.query(BDRCompany).filter(BDRCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if status:
        company.status = status
    if priority:
        company.priority = priority
    
    db.commit()
    db.refresh(company)
    
    return {
        "id": str(company.id),
        "company_name": company.company_name,
        "status": company.status,
        "priority": company.priority,
    }
