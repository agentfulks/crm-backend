"""BDR Contact model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class BDRContact(Base):
    """BDR Contact for game studio outreach."""
    
    __tablename__ = "bdr_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("bdr_companies.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    seniority_level = Column(String(50), nullable=True)
    email = Column(String(320), nullable=True)
    phone = Column(String(50), nullable=True)
    linkedin_url = Column(Text, nullable=True)
    is_decision_maker = Column(Boolean, default=False, nullable=False)
    is_champion = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    timezone = Column(String(100), nullable=True)
    last_contacted_at = Column(DateTime, nullable=True)
    contact_preference = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_flagged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<BDRContact {self.full_name}>"
