"""BDR Company model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class BDRCompany(Base):
    """BDR Company for game studio outreach."""
    
    __tablename__ = "bdr_companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    annual_revenue = Column(String(100), nullable=True)
    headquarters_city = Column(String(100), nullable=True)
    headquarters_state = Column(String(100), nullable=True)
    headquarters_country = Column(String(100), nullable=True)
    website_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    target_department = Column(String(100), nullable=True)
    ideal_buyer_persona = Column(String(255), nullable=True)
    pain_points = Column(Text, nullable=True)
    use_case_fit = Column(String(50), nullable=True)
    priority = Column(String(10), nullable=True)
    status = Column(String(50), nullable=True)
    lead_source = Column(String(100), nullable=True)
    icp_score = Column(Integer, nullable=True)
    engagement_score = Column(Integer, nullable=True)
    assigned_bdr = Column(String(255), nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    tags = Column(Text, nullable=True)
    custom_metadata = Column(Text, nullable=True)  # Renamed from 'metadata'
    
    def __repr__(self) -> str:
        return f"<BDRCompany {self.company_name}>"
