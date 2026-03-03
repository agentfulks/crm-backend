"""Meeting ORM model."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import MeetingStatus


class Meeting(TimestampMixin, Base):
    """Tracks meetings with funds/contacts."""

    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id", ondelete="CASCADE"), nullable=False)
    contact_id: Mapped[str | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    packet_id: Mapped[str | None] = mapped_column(
        ForeignKey("packets.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus, name="meeting_status_enum"), nullable=False
    )
    meeting_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    fund: Mapped["Fund"] = relationship(back_populates="meetings")
    contact: Mapped["Contact"] = relationship()
    packet: Mapped["Packet"] = relationship(back_populates="meetings")
