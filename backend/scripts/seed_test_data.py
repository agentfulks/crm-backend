"""Comprehensive seed data for testing the CRM database.

This script creates sample data for all CRM tables:
- Funds (with various statuses and priorities)
- Contacts (linked to funds)
- Packets (outreach approval workflow)
- Outreach Attempts (email/intro tracking)
- Interactions (unified touchpoint log)
- Meetings (scheduled meetings)
- Notes (fund and contact notes)

Usage:
    cd /data/workspace/backend
    .venv/bin/python scripts/seed_test_data.py

Environment:
    DATABASE_URL - PostgreSQL connection string (required)
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Ensure backend package is importable when script executed directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.contact import Contact
from app.models.enums import (
    FundStatus,
    InteractionDirection,
    InteractionType,
    MeetingStatus,
    NoteVisibility,
    OutreachChannel,
    OutreachStatus,
    PacketStatus,
    Priority,
)
from app.models.fund import Fund
from app.models.interaction import Interaction
from app.models.meeting import Meeting
from app.models.note import Note
from app.models.outreach_attempt import OutreachAttempt
from app.models.packet import Packet


# Sample data templates
SAMPLE_FUNDS = [
    {
        "name": "Andreessen Horowitz",
        "firm_type": "Venture Capital",
        "hq_city": "Menlo Park",
        "hq_region": "California",
        "hq_country": "USA",
        "stage_focus": ["Seed", "Series A", "Series B"],
        "check_size_min": Decimal("100000.00"),
        "check_size_max": Decimal("10000000.00"),
        "check_size_currency": "USD",
        "target_countries": ["USA", "Canada", "UK"],
        "website_url": "https://a16z.com",
        "linkedin_url": "https://linkedin.com/company/andreessen-horowitz",
        "overview": "Andreessen Horowitz is a venture capital firm that backs bold entrepreneurs building the future through technology.",
        "priority": Priority.A,
        "status": FundStatus.RESEARCHING,
        "score": Decimal("95.50"),
    },
    {
        "name": "Sequoia Capital",
        "firm_type": "Venture Capital",
        "hq_city": "Menlo Park",
        "hq_region": "California",
        "hq_country": "USA",
        "stage_focus": ["Seed", "Series A", "Series B", "Series C"],
        "check_size_min": Decimal("500000.00"),
        "check_size_max": Decimal("50000000.00"),
        "check_size_currency": "USD",
        "target_countries": ["USA", "India", "China", "Israel"],
        "website_url": "https://sequoiacap.com",
        "linkedin_url": "https://linkedin.com/company/sequoia-capital",
        "overview": "Sequoia helps daring founders build legendary companies from idea to IPO and beyond.",
        "priority": Priority.A,
        "status": FundStatus.READY,
        "score": Decimal("98.00"),
    },
    {
        "name": "Benchmark Capital",
        "firm_type": "Venture Capital",
        "hq_city": "San Francisco",
        "hq_region": "California",
        "hq_country": "USA",
        "stage_focus": ["Series A", "Series B"],
        "check_size_min": Decimal("250000.00"),
        "check_size_max": Decimal("20000000.00"),
        "check_size_currency": "USD",
        "target_countries": ["USA"],
        "website_url": "https://benchmark.com",
        "overview": "Benchmark is a venture capital firm that focuses on early-stage venture investing.",
        "priority": Priority.B,
        "status": FundStatus.NEW,
        "score": Decimal("88.00"),
    },
    {
        "name": "Accel Partners",
        "firm_type": "Venture Capital",
        "hq_city": "Palo Alto",
        "hq_region": "California",
        "hq_country": "USA",
        "stage_focus": ["Seed", "Series A"],
        "check_size_min": Decimal("100000.00"),
        "check_size_max": Decimal("15000000.00"),
        "check_size_currency": "USD",
        "target_countries": ["USA", "Europe", "India"],
        "website_url": "https://accel.com",
        "overview": "Accel is a leading venture capital firm that invests in early-stage technology companies.",
        "priority": Priority.B,
        "status": FundStatus.APPROVED,
        "score": Decimal("92.00"),
    },
    {
        "name": "Index Ventures",
        "firm_type": "Venture Capital",
        "hq_city": "London",
        "hq_region": "England",
        "hq_country": "UK",
        "stage_focus": ["Seed", "Series A", "Series B"],
        "check_size_min": Decimal("50000.00"),
        "check_size_max": Decimal("25000000.00"),
        "check_size_currency": "USD",
        "target_countries": ["UK", "Europe", "USA"],
        "website_url": "https://indexventures.com",
        "overview": "Index Ventures is a European venture capital firm that invests in technology-enabled companies.",
        "priority": Priority.A,
        "status": FundStatus.SENT,
        "score": Decimal("90.00"),
    },
    {
        "name": "Local Angel Group",
        "firm_type": "Angel Group",
        "hq_city": "Austin",
        "hq_region": "Texas",
        "hq_country": "USA",
        "stage_focus": ["Pre-Seed", "Seed"],
        "check_size_min": Decimal("25000.00"),
        "check_size_max": Decimal("500000.00"),
        "check_size_currency": "USD",
        "target_countries": ["USA"],
        "website_url": "https://example-angels.com",
        "overview": "Local angel investor group focused on early-stage startups.",
        "priority": Priority.C,
        "status": FundStatus.NEW,
        "score": Decimal("65.00"),
    },
]

SAMPLE_CONTACTS = [
    # Andreessen Horowitz contacts
    {"full_name": "Marc Andreessen", "title": "Co-founder", "is_primary": True, "fund_idx": 0},
    {"full_name": "Ben Horowitz", "title": "Co-founder", "is_primary": False, "fund_idx": 0},
    {"full_name": "Katherine Boyle", "title": "Partner", "is_primary": False, "fund_idx": 0},
    # Sequoia contacts
    {"full_name": "Roelof Botha", "title": "Partner", "is_primary": True, "fund_idx": 1},
    {"full_name": "Doug Leone", "title": "Partner", "is_primary": False, "fund_idx": 1},
    # Benchmark contacts
    {"full_name": "Sarah Tavel", "title": "General Partner", "is_primary": True, "fund_idx": 2},
    # Accel contacts
    {"full_name": "Rich Wong", "title": "Partner", "is_primary": True, "fund_idx": 3},
    {"full_name": "Arun Mathew", "title": "Partner", "is_primary": False, "fund_idx": 3},
    # Index Ventures contacts
    {"full_name": "Danny Rimer", "title": "Partner", "is_primary": True, "fund_idx": 4},
    # Local Angel Group
    {"full_name": "John Smith", "title": "Lead Angel", "is_primary": True, "fund_idx": 5},
]

SAMPLE_PACKETS = [
    {"fund_idx": 3, "status": PacketStatus.APPROVED, "priority": Priority.A, "trello_card_id": "CARD-001"},
    {"fund_idx": 4, "status": PacketStatus.SENT, "priority": Priority.A, "trello_card_id": "CARD-002"},
    {"fund_idx": 0, "status": PacketStatus.AWAITING_APPROVAL, "priority": Priority.A, "trello_card_id": "CARD-003"},
    {"fund_idx": 2, "status": PacketStatus.QUEUED, "priority": Priority.B, "trello_card_id": None},
]

SAMPLE_OUTREACH = [
    {
        "packet_idx": 0,
        "contact_idx": 6,  # Rich Wong from Accel
        "channel": OutreachChannel.EMAIL,
        "status": OutreachStatus.RESPONDED,
        "subject": "Investment Opportunity - Gaming Studio",
    },
    {
        "packet_idx": 1,
        "contact_idx": 8,  # Danny Rimer from Index
        "channel": OutreachChannel.INTRO,
        "status": OutreachStatus.SENT,
        "subject": "Warm Intro - Gaming Investment",
    },
    {
        "packet_idx": 2,
        "contact_idx": 0,  # Marc Andreessen
        "channel": OutreachChannel.EMAIL,
        "status": OutreachStatus.DRAFT,
        "subject": "Series A Gaming Investment",
    },
]

SAMPLE_MEETINGS = [
    {
        "fund_idx": 3,
        "contact_idx": 6,
        "packet_idx": 0,
        "status": MeetingStatus.COMPLETED,
        "scheduled_at": datetime.now() - timedelta(days=7),
        "meeting_url": "https://zoom.us/j/123456789",
        "notes": "Great conversation about our gaming portfolio. They're interested in learning more.",
    },
    {
        "fund_idx": 4,
        "contact_idx": 8,
        "packet_idx": 1,
        "status": MeetingStatus.PLANNED,
        "scheduled_at": datetime.now() + timedelta(days=3),
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "notes": "Follow-up call scheduled",
    },
]

SAMPLE_NOTES = [
    {
        "fund_idx": 0,
        "contact_idx": None,
        "author": "Lucas Fulks",
        "body": "Top tier firm with strong gaming investments. High priority target.",
        "visibility": NoteVisibility.INTERNAL,
        "pinned": True,
    },
    {
        "fund_idx": 0,
        "contact_idx": 0,
        "author": "Lucas Fulks",
        "body": "Marc is very responsive. Prefers concise emails with clear metrics.",
        "visibility": NoteVisibility.INTERNAL,
        "pinned": False,
    },
    {
        "fund_idx": 3,
        "contact_idx": 6,
        "author": "Lucas Fulks",
        "body": "Meeting notes: Strong interest in our thesis. Asked for cap table and financial projections.",
        "visibility": NoteVisibility.INTERNAL,
        "pinned": True,
    },
]

SAMPLE_INTERACTIONS = [
    {
        "fund_idx": 3,
        "contact_idx": 6,
        "interaction_type": InteractionType.EMAIL,
        "direction": InteractionDirection.OUTBOUND,
        "subject": "Initial outreach",
        "content": "Sent cold email introducing our gaming studio",
    },
    {
        "fund_idx": 3,
        "contact_idx": 6,
        "interaction_type": InteractionType.EMAIL,
        "direction": InteractionDirection.INBOUND,
        "subject": "Re: Initial outreach",
        "content": "Rich replied expressing interest in a call",
    },
    {
        "fund_idx": 3,
        "contact_idx": 6,
        "interaction_type": InteractionType.MEETING,
        "direction": None,
        "subject": "Discovery call",
        "content": "30-min video call to discuss investment opportunity",
    },
    {
        "fund_idx": 4,
        "contact_idx": 8,
        "interaction_type": InteractionType.INTRO,
        "direction": InteractionDirection.INBOUND,
        "subject": "Warm intro from portfolio founder",
        "content": "Portfolio CEO made the warm connection",
    },
]


def seed_funds(session) -> list[Fund]:
    """Create sample funds and return them."""
    funds = []
    for data in SAMPLE_FUNDS:
        fund = Fund(**data)
        session.add(fund)
        funds.append(fund)
    session.flush()  # Get IDs assigned
    print(f"  Created {len(funds)} funds")
    return funds


def seed_contacts(session, funds: list[Fund]) -> list[Contact]:
    """Create sample contacts linked to funds."""
    contacts = []
    for data in SAMPLE_CONTACTS:
        fund = funds[data["fund_idx"]]
        contact = Contact(
            fund_id=fund.id,
            full_name=data["full_name"],
            title=data["title"],
            is_primary=data["is_primary"],
            email=f"{data['full_name'].lower().replace(' ', '.')}@example.com",
        )
        session.add(contact)
        contacts.append(contact)
    session.flush()
    print(f"  Created {len(contacts)} contacts")
    return contacts


def seed_packets(session, funds: list[Fund]) -> list[Packet]:
    """Create sample packets."""
    packets = []
    now = datetime.now()
    for data in SAMPLE_PACKETS:
        fund = funds[data["fund_idx"]]
        packet = Packet(
            fund_id=fund.id,
            trello_card_id=data.get("trello_card_id"),
            status=data["status"],
            priority=data["priority"],
            score_snapshot=fund.score,
            created_by="Lucas Fulks",
            approved_at=now - timedelta(days=2) if data["status"] == PacketStatus.APPROVED else None,
            sent_at=now - timedelta(days=1) if data["status"] == PacketStatus.SENT else None,
        )
        session.add(packet)
        packets.append(packet)
    session.flush()
    print(f"  Created {len(packets)} packets")
    return packets


def seed_outreach(session, packets: list[Packet], contacts: list[Contact]) -> list[OutreachAttempt]:
    """Create sample outreach attempts."""
    outreach_list = []
    now = datetime.now()
    for data in SAMPLE_OUTREACH:
        packet = packets[data["packet_idx"]]
        contact = contacts[data["contact_idx"]]
        outreach = OutreachAttempt(
            packet_id=packet.id,
            contact_id=contact.id,
            channel=data["channel"],
            status=data["status"],
            subject=data["subject"],
            body_preview="Sample email body preview...",
            sent_at=now - timedelta(days=3) if data["status"] in [OutreachStatus.SENT, OutreachStatus.RESPONDED] else None,
            responded_at=now - timedelta(days=1) if data["status"] == OutreachStatus.RESPONDED else None,
        )
        session.add(outreach)
        outreach_list.append(outreach)
    session.flush()
    print(f"  Created {len(outreach_list)} outreach attempts")
    return outreach_list


def seed_meetings(session, funds: list[Fund], contacts: list[Contact], packets: list[Packet]) -> list[Meeting]:
    """Create sample meetings."""
    meetings = []
    for data in SAMPLE_MEETINGS:
        meeting = Meeting(
            fund_id=funds[data["fund_idx"]].id,
            contact_id=contacts[data["contact_idx"]].id,
            packet_id=packets[data["packet_idx"]].id,
            status=data["status"],
            scheduled_at=data["scheduled_at"],
            meeting_url=data["meeting_url"],
            notes=data["notes"],
        )
        session.add(meeting)
        meetings.append(meeting)
    session.flush()
    print(f"  Created {len(meetings)} meetings")
    return meetings


def seed_notes(session, funds: list[Fund], contacts: list[Contact]) -> list[Note]:
    """Create sample notes."""
    notes = []
    for data in SAMPLE_NOTES:
        note = Note(
            fund_id=funds[data["fund_idx"]].id,
            contact_id=contacts[data["contact_idx"]].id if data["contact_idx"] is not None else None,
            author=data["author"],
            body=data["body"],
            visibility=data["visibility"],
            pinned=data["pinned"],
        )
        session.add(note)
        notes.append(note)
    session.flush()
    print(f"  Created {len(notes)} notes")
    return notes


def seed_interactions(session, funds: list[Fund], contacts: list[Contact]) -> list[Interaction]:
    """Create sample interactions."""
    interactions = []
    now = datetime.now()
    for idx, data in enumerate(SAMPLE_INTERACTIONS):
        interaction = Interaction(
            fund_id=funds[data["fund_idx"]].id,
            contact_id=contacts[data["contact_idx"]].id,
            interaction_type=data["interaction_type"],
            direction=data["direction"],
            subject=data["subject"],
            content=data["content"],
            occurred_at=now - timedelta(days=10 - idx),
            created_by="Lucas Fulks",
        )
        session.add(interaction)
        interactions.append(interaction)
    session.flush()
    print(f"  Created {len(interactions)} interactions")
    return interactions


def seed_audit_logs(session, funds: list[Fund]) -> list[AuditLog]:
    """Create sample audit logs."""
    logs = []
    now = datetime.now()
    audit_entries = [
        {"entity_type": "fund", "entity_id": funds[0].id, "action": "created", "notes": "Fund imported from CSV"},
        {"entity_type": "fund", "entity_id": funds[3].id, "action": "updated", "notes": "Status changed to APPROVED"},
        {"entity_type": "packet", "entity_id": str(uuid.uuid4()), "action": "created", "notes": "Packet created for Accel"},
    ]
    for data in audit_entries:
        log = AuditLog(
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            action=data["action"],
            payload={"timestamp": now.isoformat()},
            notes=data["notes"],
        )
        session.add(log)
        logs.append(log)
    session.flush()
    print(f"  Created {len(logs)} audit logs")
    return logs


def verify_seed_data(session) -> dict:
    """Verify all seed data was created correctly."""
    counts = {}
    tables = [
        ("funds", Fund),
        ("contacts", Contact),
        ("packets", Packet),
        ("outreach_attempts", OutreachAttempt),
        ("meetings", Meeting),
        ("notes", Note),
        ("interactions", Interaction),
        ("audit_log", AuditLog),
    ]
    for table_name, model in tables:
        count = session.query(model).count()
        counts[table_name] = count
    return counts


def main() -> None:
    """Main entry point for seeding test data."""
    print("=" * 60)
    print("CRM Database Test Data Seeder")
    print("=" * 60)
    
    session = SessionLocal()
    try:
        # Check if data already exists
        existing_funds = session.query(Fund).count()
        if existing_funds > 0:
            print(f"\n⚠️  Found {existing_funds} existing funds in database.")
            response = input("   Delete existing data and re-seed? (yes/no): ")
            if response.lower() == "yes":
                print("\n  Clearing existing data...")
                # Delete in order to respect FK constraints
                session.execute(text("DELETE FROM audit_log"))
                session.execute(text("DELETE FROM interactions"))
                session.execute(text("DELETE FROM notes"))
                session.execute(text("DELETE FROM meetings"))
                session.execute(text("DELETE FROM outreach_attempts"))
                session.execute(text("DELETE FROM packets"))
                session.execute(text("DELETE FROM contacts"))
                session.execute(text("DELETE FROM funds"))
                session.commit()
                print("  Existing data cleared.")
            else:
                print("  Aborting. Use --force to skip this check.")
                return
        
        print("\n📦 Creating seed data...")
        print()
        
        # Create data in dependency order
        funds = seed_funds(session)
        contacts = seed_contacts(session, funds)
        packets = seed_packets(session, funds)
        outreach = seed_outreach(session, packets, contacts)
        meetings = seed_meetings(session, funds, contacts, packets)
        notes = seed_notes(session, funds, contacts)
        interactions = seed_interactions(session, funds, contacts)
        audit_logs = seed_audit_logs(session, funds)
        
        session.commit()
        
        print("\n" + "=" * 60)
        print("✅ Seed data created successfully!")
        print("=" * 60)
        
        # Verify counts
        counts = verify_seed_data(session)
        print("\n📊 Table Counts:")
        for table, count in counts.items():
            print(f"  {table:25s}: {count:3d} rows")
        
        print("\n" + "=" * 60)
        print("Sample data summary:")
        print("  • 6 funds (A16z, Sequoia, Benchmark, Accel, Index, Angel Group)")
        print("  • 10 contacts across all funds")
        print("  • 4 packets in various workflow stages")
        print("  • 3 outreach attempts (email, intro)")
        print("  • 2 meetings (1 completed, 1 planned)")
        print("  • 3 notes (2 pinned)")
        print("  • 4 interactions (email, meetings, intro)")
        print("  • 3 audit log entries")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
