"""Domain enumerations."""
from __future__ import annotations

from enum import Enum


class Priority(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class FundStatus(str, Enum):
    NEW = "NEW"
    RESEARCHING = "RESEARCHING"
    READY = "READY"
    APPROVED = "APPROVED"
    SENT = "SENT"
    FOLLOW_UP = "FOLLOW_UP"
    CLOSED = "CLOSED"


class PacketStatus(str, Enum):
    QUEUED = "QUEUED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    FOLLOW_UP = "FOLLOW_UP"
    CLOSED = "CLOSED"


class OutreachChannel(str, Enum):
    EMAIL = "EMAIL"
    INTRO = "INTRO"
    SOCIAL = "SOCIAL"
    MEETING = "MEETING"


class OutreachStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    RESPONDED = "RESPONDED"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


class MeetingStatus(str, Enum):
    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"


class NoteVisibility(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class InteractionType(str, Enum):
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    CALL = "CALL"
    INTRO = "INTRO"
    SOCIAL = "SOCIAL"


class InteractionDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
