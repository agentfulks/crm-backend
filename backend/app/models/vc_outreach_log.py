"""VC Outreach Log model - message history for contacts in the contacts table."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class VCOutreachLog(Base):
    """Log of outreach attempts for VC fund contacts, storing the actual message sent."""

    __tablename__ = "vc_outreach_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel = Column(String(50), nullable=False)  # 'email' or 'linkedin'
    subject = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<VCOutreachLog {self.contact_id} via {self.channel}>"
