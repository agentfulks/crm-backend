"""Email template model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class EmailTemplate(Base):
    """Email template for outreach campaigns."""
    
    __tablename__ = "email_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "introduction", "follow_up", "art_product"
    template_type = Column(String(20), nullable=False, server_default='studio')  # 'studio' | 'vc'
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    
    # Variables that can be used in the template
    # e.g., {{studio_name}}, {{contact_name}}, {{my_name}}
    variables = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    usage_count = Column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<EmailTemplate {self.name}>"
