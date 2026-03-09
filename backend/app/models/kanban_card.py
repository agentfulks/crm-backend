"""Kanban card model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class KanbanCard(Base):
    """Kanban card for the Tasks board."""

    __tablename__ = "kanban_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Column position: backlog | todo | doing | review | complete
    column = Column(String(50), nullable=False, default="backlog")
    # Sort order within the column (lower = higher on the board)
    position = Column(Integer, nullable=False, default=0)

    # Where the card came from: custom | vc | studio | contact
    card_type = Column(String(50), nullable=False, default="custom")
    # ID of the source entity (packet id, studio id, contact id, etc.)
    source_id = Column(String(255), nullable=True)
    # Snapshot of source entity data so the card is useful without extra fetches
    source_data = Column(JSON, nullable=True)

    priority = Column(String(10), nullable=True)   # A | B | C
    due_date = Column(DateTime, nullable=True)
    tags = Column(JSON, nullable=True, default=list)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<KanbanCard {self.title!r} [{self.column}]>"
