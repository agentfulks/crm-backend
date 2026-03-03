"""Audit log ORM model."""
from __future__ import annotations

from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text

from app.db.base import Base, TimestampMixin

# Cross-database compatible JSON type (JSONB for PostgreSQL, JSON for SQLite)
JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")


class AuditLog(TimestampMixin, Base):
    """Simple append-only audit records."""

    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON_VARIANT, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)
