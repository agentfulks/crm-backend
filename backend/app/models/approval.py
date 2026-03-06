"""Approval audit log model for tracking classification and approval actions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

# Cross-database compatible JSON type
JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")


class ApprovalAuditLog(Base, TimestampMixin):
    """Audit log for approval-related actions.
    
    Tracks:
    - Tier classifications
    - Auto-approvals
    - Manual approvals/rejections
    - Rule evaluations
    """
    
    __tablename__ = "approval_audit_log"
    
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    
    # Entity reference (polymorphic - can be packet_id or bdr_company_id)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'packet' or 'bdr_company'
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Action details
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Actions: 'classified', 'auto_approved', 'manually_approved', 'manually_rejected', 'tier_changed'
    
    # Tier classification
    tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Rule information
    rules_triggered: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON_VARIANT, nullable=True)
    classification_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Who performed the action
    performed_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    # 'system' for auto-actions, user_id for manual actions
    
    # Additional metadata
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON_VARIANT, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ApprovalAuditLog {self.action} {self.entity_type}:{self.entity_id}>"


class CardClassificationMixin:
    """Mixin to add tier classification fields to card models.
    
    Add this mixin to Packet and BDRCompany models to enable tiered approval.
    """
    
    # Tier classification
    tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Auto-approval tracking
    auto_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    auto_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Classification metadata
    tier_classification_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    classification_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # Version of the rules engine used for classification
    
    # Manual override tracking
    manually_reviewed: Mapped[bool] = mapped_column(default=False, nullable=False)
    manually_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    manually_reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Flags
    needs_review: Mapped[bool] = mapped_column(default=False, nullable=False)
    on_watch_list: Mapped[bool] = mapped_column(default=False, nullable=False)