"""Fund ORM model."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import FundStatus, Priority

JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")
MutableListJSON = MutableList.as_mutable(JSON_VARIANT)
# Use plain JSON for dict fields to avoid MutableDict issues with variants
MutableDictJSON = MutableDict.as_mutable(JSON())


class Fund(TimestampMixin, Base):
    """Represents an investment fund tracked by the CRM."""

    __tablename__ = "funds"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    firm_type: Mapped[Optional[str]] = mapped_column(String(100))
    hq_city: Mapped[Optional[str]] = mapped_column(String(100))
    hq_region: Mapped[Optional[str]] = mapped_column(String(100))
    hq_country: Mapped[Optional[str]] = mapped_column(String(100))
    stage_focus: Mapped[List[str] | None] = mapped_column(
        MutableListJSON,
        nullable=True,
        default=list,
    )
    check_size_min: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    check_size_max: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    check_size_currency: Mapped[Optional[str]] = mapped_column(String(10))
    target_countries: Mapped[List[str] | None] = mapped_column(
        MutableListJSON,
        nullable=True,
        default=list,
    )
    website_url: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    twitter_url: Mapped[Optional[str]] = mapped_column(Text)
    funding_requirements: Mapped[Optional[str]] = mapped_column(Text)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    contact_email: Mapped[Optional[str]] = mapped_column(String(320))
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    priority: Mapped[Priority] = mapped_column(Enum(Priority, name="priority_enum"), default=Priority.B)
    status: Mapped[FundStatus] = mapped_column(
        Enum(FundStatus, name="fund_status_enum"), nullable=False, default=FundStatus.NEW
    )
    data_source: Mapped[Optional[str]] = mapped_column(String(100))
    source_row_id: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[dict | None] = mapped_column(
        MutableDictJSON,
        nullable=True,
        default=dict,
    )
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_contacted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    packets: Mapped[list["Packet"]] = relationship(back_populates="fund", cascade="all, delete")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="fund", cascade="all, delete")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="fund", cascade="all, delete")
    notes: Mapped[list["Note"]] = relationship(back_populates="fund", cascade="all, delete")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="fund", cascade="all, delete")
