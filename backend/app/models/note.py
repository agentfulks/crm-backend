"""Note ORM model."""
from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import NoteVisibility


class Note(TimestampMixin, Base):
    """Notes recorded against funds/contacts."""

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id", ondelete="CASCADE"), nullable=False)
    contact_id: Mapped[str | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    visibility: Mapped[NoteVisibility] = mapped_column(
        Enum(NoteVisibility, name="note_visibility_enum"), nullable=False
    )
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    fund: Mapped["Fund"] = relationship(back_populates="notes")
    contact: Mapped["Contact"] = relationship(back_populates="notes_rel")
