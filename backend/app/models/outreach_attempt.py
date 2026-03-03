"""Outreach attempt model."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import OutreachChannel, OutreachStatus


class OutreachAttempt(TimestampMixin, Base):
    """Individual outreach attempt linked to a packet and optionally a contact."""

    __tablename__ = "outreach_attempts"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    packet_id: Mapped[str] = mapped_column(
        ForeignKey("packets.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[str | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    channel: Mapped[OutreachChannel] = mapped_column(
        Enum(OutreachChannel, name="outreach_channel_enum"), nullable=False
    )
    status: Mapped[OutreachStatus] = mapped_column(
        Enum(OutreachStatus, name="outreach_status_enum"), nullable=False
    )
    subject: Mapped[str | None] = mapped_column(String(255))
    body_preview: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    packet: Mapped["Packet"] = relationship(back_populates="outreach_attempts")
    contact: Mapped["Contact"] = relationship(back_populates="outreach_attempts")
