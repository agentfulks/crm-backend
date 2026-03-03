"""Interaction endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import InteractionDirection, InteractionType
from app.schemas.interaction import (
    InteractionCreate,
    InteractionFilters,
    InteractionListResponse,
    InteractionRead,
    InteractionSortField,
    InteractionUpdate,
    SortDirection,
)
from app.services import interaction_service

router = APIRouter()


@router.get("/", response_model=InteractionListResponse)
def list_interactions(
    *,
    db: Session = Depends(get_db),
    fund_id: str | None = Query(None, description="Filter by fund ID"),
    contact_id: str | None = Query(None, description="Filter by contact ID"),
    interaction_type: InteractionType | None = Query(None, description="Filter by interaction type"),
    direction: InteractionDirection | None = Query(None, description="Filter by direction"),
    created_by: str | None = Query(None, description="Filter by creator"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: InteractionSortField = Query(InteractionSortField.created_at),
    sort_direction: SortDirection = Query(SortDirection.desc),
) -> InteractionListResponse:
    """Return paginated interactions matching filters."""

    filters = InteractionFilters(
        fund_id=fund_id,
        contact_id=contact_id,
        interaction_type=interaction_type,
        direction=direction,
        created_by=created_by,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = interaction_service.list_interactions(db, filters)
    payload = [InteractionRead.model_validate(item, from_attributes=True) for item in items]
    return InteractionListResponse(total=total, items=payload)


@router.post("/", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(
    *,
    db: Session = Depends(get_db),
    payload: InteractionCreate,
) -> InteractionRead:
    """Create an interaction record."""

    interaction = interaction_service.create_interaction(db, payload.model_dump())
    return InteractionRead.model_validate(interaction, from_attributes=True)


@router.get("/{interaction_id}", response_model=InteractionRead)
def get_interaction(
    *,
    db: Session = Depends(get_db),
    interaction_id: str,
) -> InteractionRead:
    """Retrieve an interaction by ID."""

    interaction = interaction_service.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )
    return InteractionRead.model_validate(interaction, from_attributes=True)


@router.patch("/{interaction_id}", response_model=InteractionRead)
def update_interaction(
    *,
    db: Session = Depends(get_db),
    interaction_id: str,
    payload: InteractionUpdate,
) -> InteractionRead:
    """Update fields on an interaction."""

    interaction = interaction_service.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    data = payload.model_dump(exclude_unset=True)
    interaction = interaction_service.update_interaction(db, interaction, data)
    return InteractionRead.model_validate(interaction, from_attributes=True)


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    *,
    db: Session = Depends(get_db),
    interaction_id: str,
) -> None:
    """Delete an interaction."""

    interaction = interaction_service.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    interaction_service.delete_interaction(db, interaction)


@router.get("/fund/{fund_id}", response_model=list[InteractionRead])
def get_interactions_by_fund(
    *,
    db: Session = Depends(get_db),
    fund_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[InteractionRead]:
    """Get all interactions for a specific fund."""

    interactions = interaction_service.get_interactions_by_fund(db, fund_id, limit)
    return [InteractionRead.model_validate(item, from_attributes=True) for item in interactions]


@router.get("/contact/{contact_id}", response_model=list[InteractionRead])
def get_interactions_by_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[InteractionRead]:
    """Get all interactions for a specific contact."""

    interactions = interaction_service.get_interactions_by_contact(db, contact_id, limit)
    return [InteractionRead.model_validate(item, from_attributes=True) for item in interactions]
