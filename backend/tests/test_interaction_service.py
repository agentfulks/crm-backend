"""Tests for interaction service."""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.models.enums import InteractionDirection, InteractionType
from app.models.fund import Fund
from app.models.interaction import Interaction
from app.services import interaction_service as service


@pytest.fixture
def sample_fund(session: Session) -> Fund:
    """Create a sample fund for testing."""
    fund = Fund(
        name="Test Fund",
        stage_focus=["Seed"],
        target_countries=["USA"],
        priority="A",
        status="NEW",
    )
    session.add(fund)
    session.commit()
    session.refresh(fund)
    return fund


class TestInteractionService:
    """Tests for interaction service CRUD operations."""

    def test_create_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test creating a basic interaction."""
        interaction = service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.EMAIL,
                "direction": InteractionDirection.OUTBOUND,
                "subject": "Test Email",
                "content": "This is a test email",
                "created_by": "test@example.com",
            },
        )

        assert interaction.id is not None
        assert interaction.fund_id == sample_fund.id
        assert interaction.interaction_type == InteractionType.EMAIL
        assert interaction.direction == InteractionDirection.OUTBOUND
        assert interaction.subject == "Test Email"
        assert interaction.created_at is not None

    def test_get_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test fetching an interaction by ID."""
        created = service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.NOTE,
                "content": "Test note",
            },
        )

        fetched = service.get_interaction(session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.content == "Test note"

    def test_get_interaction_not_found(self, session: Session) -> None:
        """Test fetching a non-existent interaction."""
        result = service.get_interaction(session, "non-existent-id")
        assert result is None

    def test_update_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test updating an interaction."""
        created = service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.CALL,
                "subject": "Initial Call",
                "content": "Call notes",
            },
        )

        updated = service.update_interaction(
            session,
            created,
            {"subject": "Updated Call Subject", "content": "Updated call notes"},
        )

        assert updated.subject == "Updated Call Subject"
        assert updated.content == "Updated call notes"
        assert updated.interaction_type == InteractionType.CALL  # Unchanged

    def test_delete_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test deleting an interaction."""
        created = service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.SOCIAL,
                "content": "Social media interaction",
            },
        )

        service.delete_interaction(session, created)

        fetched = service.get_interaction(session, created.id)
        assert fetched is None

    def test_list_interactions_by_fund(self, session: Session, sample_fund: Fund) -> None:
        """Test listing interactions filtered by fund."""
        # Create interactions for the fund
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.EMAIL,
                "subject": "Email 1",
            },
        )
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.MEETING,
                "subject": "Meeting 1",
            },
        )

        filters = service.InteractionFilters(fund_id=sample_fund.id)
        items, total = service.list_interactions(session, filters)

        assert total == 2
        assert len(items) == 2

    def test_list_interactions_by_type(self, session: Session, sample_fund: Fund) -> None:
        """Test listing interactions filtered by type."""
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.EMAIL,
                "subject": "Email",
            },
        )
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.NOTE,
                "content": "Note",
            },
        )
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.EMAIL,
                "subject": "Another Email",
            },
        )

        filters = service.InteractionFilters(
            fund_id=sample_fund.id,
            interaction_type=InteractionType.EMAIL,
        )
        items, total = service.list_interactions(session, filters)

        assert total == 2
        assert all(i.interaction_type == InteractionType.EMAIL for i in items)

    def test_get_interactions_by_fund_helper(
        self, session: Session, sample_fund: Fund
    ) -> None:
        """Test the get_interactions_by_fund helper function."""
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.EMAIL,
                "subject": "Email 1",
            },
        )
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.NOTE,
                "content": "Note 1",
            },
        )

        items = service.get_interactions_by_fund(session, sample_fund.id)

        assert len(items) == 2
        # Should be sorted by created_at desc
        assert items[0].created_at >= items[1].created_at


class TestInteractionConvenienceMethods:
    """Tests for convenience methods like create_email_interaction."""

    def test_create_email_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test the create_email_interaction helper."""
        interaction = service.create_email_interaction(
            session=session,
            fund_id=sample_fund.id,
            subject="Pitch Deck",
            content="Please find our pitch deck attached.",
            direction=InteractionDirection.OUTBOUND,
            created_by="lucas@example.com",
        )

        assert interaction.interaction_type == InteractionType.EMAIL
        assert interaction.direction == InteractionDirection.OUTBOUND
        assert interaction.subject == "Pitch Deck"
        assert interaction.created_by == "lucas@example.com"
        assert interaction.occurred_at is not None

    def test_create_note_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test the create_note_interaction helper."""
        interaction = service.create_note_interaction(
            session=session,
            fund_id=sample_fund.id,
            content="Follow-up required next week",
            created_by="ops@example.com",
        )

        assert interaction.interaction_type == InteractionType.NOTE
        assert interaction.content == "Follow-up required next week"
        assert interaction.created_by == "ops@example.com"
        assert interaction.occurred_at is not None

    def test_create_meeting_interaction(self, session: Session, sample_fund: Fund) -> None:
        """Test the create_meeting_interaction helper."""
        interaction = service.create_meeting_interaction(
            session=session,
            fund_id=sample_fund.id,
            subject="Intro Call",
            content="Discussed AI gaming infrastructure. Partner interested in follow-up.",
            created_by="lucas@example.com",
        )

        assert interaction.interaction_type == InteractionType.MEETING
        assert interaction.subject == "Intro Call"
        assert "AI gaming infrastructure" in interaction.content


class TestInteractionPagination:
    """Tests for pagination and sorting."""

    def test_list_interactions_pagination(self, session: Session, sample_fund: Fund) -> None:
        """Test pagination in list_interactions."""
        # Create 10 interactions
        for i in range(10):
            service.create_interaction(
                session,
                {
                    "fund_id": sample_fund.id,
                    "interaction_type": InteractionType.NOTE,
                    "content": f"Note {i}",
                },
            )

        # Test limit
        filters = service.InteractionFilters(fund_id=sample_fund.id, limit=5)
        items, total = service.list_interactions(session, filters)

        assert total == 10
        assert len(items) == 5

        # Test offset
        filters = service.InteractionFilters(fund_id=sample_fund.id, limit=5, offset=5)
        items, total = service.list_interactions(session, filters)

        assert total == 10
        assert len(items) == 5

    def test_list_interactions_sorting(self, session: Session, sample_fund: Fund) -> None:
        """Test sorting in list_interactions."""
        # Create interactions
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.NOTE,
                "content": "First",
            },
        )
        service.create_interaction(
            session,
            {
                "fund_id": sample_fund.id,
                "interaction_type": InteractionType.NOTE,
                "content": "Second",
            },
        )

        # Test ascending sort
        filters = service.InteractionFilters(
            fund_id=sample_fund.id, sort_by="created_at", sort_direction="asc"
        )
        items, _ = service.list_interactions(session, filters)

        assert len(items) == 2
        assert items[0].created_at <= items[1].created_at
