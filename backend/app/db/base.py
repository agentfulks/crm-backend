"""Declarative base and shared mixins."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class."""

    pass


class TimestampMixin:
    """Adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class MetadataMixin(TimestampMixin):
    """Helper mixin for JSON payload fields."""

    @staticmethod
    def default_json() -> Dict[str, Any]:
        return {}


# Import models for Alembic metadata discovery.
# These imports are done in a function to avoid circular imports at module level.
def import_models():
    """Import all models for Alembic metadata discovery."""
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.contact import Contact  # noqa: F401
    from app.models.fund import Fund  # noqa: F401
    from app.models.interaction import Interaction  # noqa: F401
    from app.models.meeting import Meeting  # noqa: F401
    from app.models.note import Note  # noqa: F401
    from app.models.outreach_attempt import OutreachAttempt  # noqa: F401
    from app.models.packet import Packet  # noqa: F401
