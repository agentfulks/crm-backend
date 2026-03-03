"""Packet ORM model."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PacketStatus, Priority

# Cross-database compatible JSON type (JSONB for PostgreSQL, JSON for SQLite)
JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")


class Packet(TimestampMixin, Base):
    """Represents an approval packet tied to a fund."""

    __tablename__ = "packets"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id", ondelete="CASCADE"), nullable=False)
    trello_card_id: Mapped[str | None] = mapped_column(String(100))
    trello_card_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[PacketStatus] = mapped_column(
        Enum(PacketStatus, name="packet_status_enum"), nullable=False, default=PacketStatus.QUEUED
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority_enum"), nullable=False, default=Priority.B
    )
    score_snapshot: Mapped[float | None] = mapped_column(Numeric(5, 2))
    created_by: Mapped[str | None] = mapped_column(String(100))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    follow_up_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crm_status: Mapped[dict | None] = mapped_column(JSON_VARIANT, nullable=True)

    fund: Mapped["Fund"] = relationship(back_populates="packets")
    outreach_attempts: Mapped[list["OutreachAttempt"]] = relationship(back_populates="packet")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="packet")
