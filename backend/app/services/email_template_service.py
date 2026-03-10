"""Email template service."""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.email_template import EmailTemplate


def list_templates(
    db: Session,
    *,
    category: str | None = None,
    template_type: str | None = None,
    is_active: bool | None = True,
    limit: int = 50,
    offset: int = 0,
) -> list[EmailTemplate]:
    """List email templates with optional filters."""
    
    query = db.query(EmailTemplate)
    
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    if template_type:
        query = query.filter(EmailTemplate.template_type == template_type)
    
    if is_active is not None:
        query = query.filter(EmailTemplate.is_active == is_active)
    
    return (
        query.order_by(desc(EmailTemplate.is_default), desc(EmailTemplate.updated_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_template(db: Session, template_id: str) -> EmailTemplate | None:
    """Get an email template by ID."""
    return db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()


def get_default_template(db: Session, category: str | None = None) -> EmailTemplate | None:
    """Get the default email template, optionally by category."""
    query = db.query(EmailTemplate).filter(EmailTemplate.is_default == True)
    
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    return query.first()


def create_template(db: Session, data: dict) -> EmailTemplate:
    """Create a new email template."""
    
    template = EmailTemplate(**data)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(db: Session, template: EmailTemplate, data: dict) -> EmailTemplate:
    """Update an email template."""
    
    for key, value in data.items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template: EmailTemplate) -> None:
    """Soft delete an email template (mark as inactive)."""
    
    template.is_active = False
    db.commit()


def render_template(
    template: EmailTemplate,
    *,
    studio_name: str,
    contact_name: str,
    my_name: str = "Lucas Fulks",
) -> dict:
    """Render a template with variable substitution."""
    
    # Get first name from contact_name
    first_name = contact_name.split()[0] if contact_name else "there"
    
    # Default variables
    variables = {
        "studio_name": studio_name,
        "contact_name": contact_name,
        "first_name": first_name,
        "my_name": my_name,
    }
    
    subject = template.subject
    body = template.body
    
    # Replace variables
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, value)
        body = body.replace(placeholder, value)
    
    return {
        "subject": subject,
        "body": body,
    }


def increment_usage(db: Session, template: EmailTemplate) -> None:
    """Increment the usage count of a template."""
    
    template.usage_count += 1
    db.commit()
