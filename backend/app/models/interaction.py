"""Interaction ORM model - unified touchpoint tracking."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import InteractionDirection, InteractionType

# Cross-database compatible JSON type (JSONB for PostgreSQL, JSON for SQLite)
JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")


class Interaction(TimestampMixin, Base):
    """Unified interaction log for all fund/contact touchpoints.
    
    Consolidates emails, meetings, notes, calls, and other touchpoints
    into a single queryable table.
    """

    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    fund_id: Mapped[str] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[str | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    interaction_type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType, name="interaction_type_enum"), nullable=False
    )
    direction: Mapped[InteractionDirection | None] = mapped_column(
        Enum(InteractionDirection, name="interaction_direction_enum"), nullable=True
    )
    subject: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str | None] = mapped_column(String(255))
    source_id: Mapped[str | None] = mapped_column(String(100))  # ID from source system (e.g., email ID)
    source_table: Mapped[str | None] = mapped_column(String(50))  # Origin table if migrated
    meta: Mapped[dict | None] = mapped_column(JSON_VARIANT, nullable=True)  # Additional metadata
    
    # Relationships
    fund: Mapped["Fund"] = relationship(back_populates="interactions")
    contact: Mapped["Contact | None"] = relationship(back_populates="interactions")
