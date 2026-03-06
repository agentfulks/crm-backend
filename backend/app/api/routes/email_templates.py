"""Email template endpoints."""
from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateRead,
    EmailTemplateUpdate,
    EmailTemplateListResponse,
)
from app.services import email_template_service

router = APIRouter()


@router.get("/")
def list_email_templates(
    *,
    db: Session = Depends(get_db),
    category: str | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(True, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Return all email templates."""
    
    templates = email_template_service.list_templates(
        db, category=category, is_active=is_active, limit=limit, offset=offset
    )
    return {
        'total': len(templates),
        'items': [{
            'id': str(t.id),
            'name': t.name,
            'description': t.description,
            'category': t.category,
            'subject': t.subject,
            'body': t.body,
            'variables': t.variables,
            'is_active': t.is_active,
            'is_default': t.is_default,
            'created_by': t.created_by,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'updated_at': t.updated_at.isoformat() if t.updated_at else None,
            'usage_count': t.usage_count,
        } for t in templates]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_email_template(
    *,
    db: Session = Depends(get_db),
    payload: EmailTemplateCreate,
):
    """Create a new email template."""
    
    data = payload.model_dump()
    template = email_template_service.create_template(db, data)
    # Return as dict to avoid Pydantic validation issues with UUID
    return {
        'id': str(template.id),
        'name': template.name,
        'description': template.description,
        'category': template.category,
        'subject': template.subject,
        'body': template.body,
        'variables': template.variables,
        'is_active': template.is_active,
        'is_default': template.is_default,
        'created_by': template.created_by,
        'created_at': template.created_at.isoformat() if template.created_at else None,
        'updated_at': template.updated_at.isoformat() if template.updated_at else None,
        'usage_count': template.usage_count,
    }


@router.get("/{template_id}", response_model=EmailTemplateRead)
def get_email_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
) -> EmailTemplateRead:
    """Retrieve an email template by ID."""
    
    template = email_template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found",
        )
    return EmailTemplateRead.model_validate(template, from_attributes=True)


@router.patch("/{template_id}", response_model=EmailTemplateRead)
def update_email_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    payload: EmailTemplateUpdate,
) -> EmailTemplateRead:
    """Update an email template."""
    
    template = email_template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found",
        )
    
    data = payload.model_dump(exclude_unset=True)
    template = email_template_service.update_template(db, template, data)
    return EmailTemplateRead.model_validate(template, from_attributes=True)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
) -> None:
    """Delete (soft delete) an email template."""
    
    template = email_template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found",
        )
    
    email_template_service.delete_template(db, template)


@router.post("/{template_id}/apply", response_model=dict)
def apply_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    studio_name: str = Query(..., description="Studio name for personalization"),
    contact_name: str = Query(..., description="Contact name for personalization"),
) -> dict:
    """Apply a template and return the rendered email content."""
    
    template = email_template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found",
        )
    
    rendered = email_template_service.render_template(
        template, studio_name=studio_name, contact_name=contact_name
    )
    return rendered
