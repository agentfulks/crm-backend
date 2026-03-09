"""Kanban board CRUD routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.kanban_card import KanbanCard
from app.schemas.kanban_card import KanbanCardCreate, KanbanCardRead, KanbanCardUpdate

router = APIRouter()

VALID_COLUMNS = {"backlog", "todo", "doing", "review", "complete"}


@router.get("/", response_model=Dict[str, Any])
def list_kanban_cards(
    *,
    db: Session = Depends(get_db),
    column: Optional[str] = Query(None, description="Filter by column"),
    card_type: Optional[str] = Query(None, description="Filter by card_type"),
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    """Return all kanban cards, optionally filtered by column or type."""
    query = db.query(KanbanCard)
    if column:
        query = query.filter(KanbanCard.column == column)
    if card_type:
        query = query.filter(KanbanCard.card_type == card_type)

    query = query.order_by(KanbanCard.column, KanbanCard.position, KanbanCard.created_at)
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [_serialize(c) for c in items],
    }


@router.post("/", response_model=KanbanCardRead, status_code=status.HTTP_201_CREATED)
def create_kanban_card(
    *,
    db: Session = Depends(get_db),
    card_in: KanbanCardCreate,
):
    """Create a new kanban card."""
    if card_in.column not in VALID_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid column '{card_in.column}'. Must be one of: {sorted(VALID_COLUMNS)}",
        )

    # Auto-assign position at end of column
    if card_in.position == 0:
        count = db.query(KanbanCard).filter(KanbanCard.column == card_in.column).count()
        position = count
    else:
        position = card_in.position

    card = KanbanCard(
        title=card_in.title,
        description=card_in.description,
        column=card_in.column,
        position=position,
        card_type=card_in.card_type,
        source_id=card_in.source_id,
        source_data=card_in.source_data,
        priority=card_in.priority,
        due_date=card_in.due_date,
        tags=card_in.tags or [],
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.get("/{card_id}", response_model=KanbanCardRead)
def get_kanban_card(
    *,
    db: Session = Depends(get_db),
    card_id: UUID,
):
    """Get a single kanban card."""
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


@router.patch("/{card_id}", response_model=KanbanCardRead)
def update_kanban_card(
    *,
    db: Session = Depends(get_db),
    card_id: UUID,
    card_in: KanbanCardUpdate,
):
    """Update a kanban card (including moving between columns)."""
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    if card_in.column is not None and card_in.column not in VALID_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid column '{card_in.column}'.",
        )

    update_data = card_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)

    db.commit()
    db.refresh(card)
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kanban_card(
    *,
    db: Session = Depends(get_db),
    card_id: UUID,
):
    """Delete a kanban card."""
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    db.delete(card)
    db.commit()


def _serialize(c: KanbanCard) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "title": c.title,
        "description": c.description,
        "column": c.column,
        "position": c.position,
        "card_type": c.card_type,
        "source_id": c.source_id,
        "source_data": c.source_data,
        "priority": c.priority,
        "due_date": c.due_date.isoformat() if c.due_date else None,
        "tags": c.tags or [],
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }
