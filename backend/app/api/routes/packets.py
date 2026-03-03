"""Packet endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import PacketStatus, Priority
from app.schemas.packet import (
    PacketActionResponse,
    PacketCreate,
    PacketListResponse,
    PacketRead,
    PacketUpdate,
    QueueStatus,
)
from app.services import packet_service
from app.services.packet_service import PacketFilters

router = APIRouter()


@router.get("/", response_model=PacketListResponse)
def list_packets(
    *,
    db: Session = Depends(get_db),
    status: PacketStatus | None = Query(None, description="Filter by packet status"),
    priority: Priority | None = Query(None, description="Filter by priority"),
    fund_id: str | None = Query(None, description="Filter by fund ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_direction: str = Query("desc", description="Sort direction: asc or desc"),
) -> PacketListResponse:
    """Return paginated packets matching filters."""

    filters = PacketFilters(
        status=status,
        priority=priority,
        fund_id=fund_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    items, total = packet_service.list_packets(db, filters)
    payload = [PacketRead.model_validate(item, from_attributes=True) for item in items]
    return PacketListResponse(total=total, items=payload)


@router.post("/", response_model=PacketRead, status_code=status.HTTP_201_CREATED)
def create_packet(*, db: Session = Depends(get_db), payload: PacketCreate) -> PacketRead:
    """Create a new packet."""

    packet = packet_service.create_packet(db, payload.model_dump())
    return PacketRead.model_validate(packet, from_attributes=True)


@router.get("/queue/status", response_model=QueueStatus)
def get_queue_status(*, db: Session = Depends(get_db)) -> QueueStatus:
    """Get daily queue status summary."""

    status_data = packet_service.get_queue_status(db)
    return QueueStatus(**status_data)


@router.get("/pending", response_model=PacketListResponse)
def get_pending_packets(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
) -> PacketListResponse:
    """Get packets awaiting approval."""

    items = packet_service.get_pending_packets(db, limit)
    payload = [PacketRead.model_validate(item, from_attributes=True) for item in items]
    return PacketListResponse(total=len(payload), items=payload)


@router.get("/{packet_id}", response_model=PacketRead)
def get_packet(*, db: Session = Depends(get_db), packet_id: str) -> PacketRead:
    """Retrieve a packet by ID."""

    packet = packet_service.get_packet(db, packet_id)
    if not packet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packet not found")
    return PacketRead.model_validate(packet, from_attributes=True)


@router.patch("/{packet_id}", response_model=PacketRead)
def update_packet(
    *,
    db: Session = Depends(get_db),
    packet_id: str,
    payload: PacketUpdate,
) -> PacketRead:
    """Update a packet."""

    packet = packet_service.get_packet(db, packet_id)
    if not packet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packet not found")

    data = payload.model_dump(exclude_unset=True)
    packet = packet_service.update_packet(db, packet, data)
    return PacketRead.model_validate(packet, from_attributes=True)


@router.post("/{packet_id}/approve", response_model=PacketActionResponse)
def approve_packet(*, db: Session = Depends(get_db), packet_id: str) -> PacketActionResponse:
    """Approve a packet for sending."""

    packet = packet_service.get_packet(db, packet_id)
    if not packet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packet not found")

    packet = packet_service.approve_packet(db, packet)
    return PacketActionResponse(
        success=True,
        packet=PacketRead.model_validate(packet, from_attributes=True),
        message="Packet approved successfully",
    )


@router.post("/{packet_id}/reject", response_model=PacketActionResponse)
def reject_packet(*, db: Session = Depends(get_db), packet_id: str) -> PacketActionResponse:
    """Reject/close a packet."""

    packet = packet_service.get_packet(db, packet_id)
    if not packet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packet not found")

    packet = packet_service.reject_packet(db, packet)
    return PacketActionResponse(
        success=True,
        packet=PacketRead.model_validate(packet, from_attributes=True),
        message="Packet rejected",
    )


@router.delete("/{packet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_packet(
    *,
    db: Session = Depends(get_db),
    packet_id: str,
) -> None:
    """Delete a packet."""

    packet = packet_service.get_packet(db, packet_id)
    if not packet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Packet not found",
        )

    packet_service.delete_packet(db, packet)
