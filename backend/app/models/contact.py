"""Contact ORM model."""
from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Contact(TimestampMixin, Base):
    """Represents a human contact within a fund."""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(320))
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    timezone: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    fund: Mapped["Fund"] = relationship(back_populates="contacts")
    outreach_attempts: Mapped[list["OutreachAttempt"]] = relationship(back_populates="contact")
    notes_rel: Mapped[list["Note"]] = relationship(back_populates="contact")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="contact")
