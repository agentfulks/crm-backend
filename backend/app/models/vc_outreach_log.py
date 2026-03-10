"""VC Outreach Log model - message history for contacts in the contacts table."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime, ForeignKey

from app.db.base import Base


class VCOutreachLog(Base):
    """Log of outreach attempts for VC fund contacts, storing the actual message sent."""

    __tablename__ = "vc_outreach_logs"

    # contacts.id is character varying, so we use String to match
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    contact_id = Column(
        String(36),
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
