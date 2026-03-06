"""Tests for Daily Intake Service."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.models import InvestorEntry, TrelloCard, CardCreationResult, DailyIntakeResult
from src.services import DailyIntakeService, CHECKLIST_NAME, DEFAULT_CHECKLIST_ITEMS


class TestDailyIntakeService:
    """Test suite for DailyIntakeService."""
    
    @pytest.fixture
    def mock_settings(self):
        """Fixture for mock settings."""
        settings = MagicMock()
        settings.database_url = "postgresql://test"
        settings.trello_board_id = "board_123"
        settings.trello_list_id = "list_456"
        settings.label_ids = ["label_1", "label_2", "label_3"]
        return settings
    
    @pytest.fixture
    def mock_crm(self):
        """Fixture for mock CRM repository."""
        return MagicMock()
    
    @pytest.fixture
    def mock_trello(self):
        """Fixture for mock Trello client."""
        return MagicMock()
    
    @pytest.fixture
    def sample_investor(self):
        """Fixture for a sample investor entry."""
        return InvestorEntry(
            id="inv_001",
            investor_name="John Doe",
            firm_name="Acme Ventures",
            job_title="Partner",
            email_address="john@acme.vc",
            phone_number="+1-555-0123",
            linkedin_profile_url="https://linkedin.com/in/johndoe",
            investment_thesis_summary="Focuses on enterprise SaaS and AI",
            outreach_score=95,
            created_at=datetime(2024, 3, 1, 10, 0, 0),
        )
    
    def test_service_initialization(self, mock_settings, mock_crm, mock_trello):
        """Test that service initializes with dependencies."""
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        assert service.settings == mock_settings
        assert service.crm == mock_crm
        assert service.trello == mock_trello
    
    def test_process_single_investor_success(self, mock_settings, mock_crm, mock_trello, sample_investor):
        """Test successful processing of a single investor."""
        # Setup mocks
        mock_trello.check_card_exists_by_prefix.return_value = False
        mock_trello.create_card.return_value = {
            "id": "card_123",
            "shortUrl": "https://trello.com/c/card123",
        }
        mock_trello.add_checklist_to_card.return_value = {"id": "checklist_1"}
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        # Execute
        result = service._process_single_investor(sample_investor, dry_run=False)
        
        # Verify
        assert result.success is True
        assert result.investor_entry == sample_investor
        assert result.trello_card_id == "card_123"
        assert result.trello_card_url == "https://trello.com/c/card123"
        assert result.dry_run is False
        
        # Verify Trello API calls
        mock_trello.check_card_exists_by_prefix.assert_called_once()
        mock_trello.create_card.assert_called_once()
        mock_trello.add_checklist_to_card.assert_called_once()
    
    def test_process_single_investor_duplicate(self, mock_settings, mock_crm, mock_trello, sample_investor):
        """Test that duplicate investors are skipped."""
        mock_trello.check_card_exists_by_prefix.return_value = True
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        result = service._process_single_investor(sample_investor, dry_run=False)
        
        assert result.success is False
        assert "duplicate" in result.error_message.lower()
        mock_trello.create_card.assert_not_called()
    
    def test_process_single_investor_api_error(self, mock_settings, mock_crm, mock_trello, sample_investor):
        """Test handling of Trello API errors."""
        mock_trello.check_card_exists_by_prefix.return_value = False
        mock_trello.create_card.side_effect = Exception("API Error: Rate limited")
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        result = service._process_single_investor(sample_investor, dry_run=False)
        
        assert result.success is False
        assert "rate limited" in result.error_message.lower()
    
    def test_process_daily_intake_success(self, mock_settings, mock_crm, mock_trello, sample_investor):
        """Test full daily intake process."""
        # Setup mocks
        mock_crm.get_top_scored_investors.return_value = [
            sample_investor,
            InvestorEntry(
                id="inv_002",
                investor_name="Jane Smith",
                firm_name="Beta Capital",
                job_title="Managing Director",
                email_address="jane@beta.capital",
                outreach_score=88,
                created_at=datetime(2024, 3, 2, 10, 0, 0),
            ),
        ]
        mock_trello.check_card_exists_by_prefix.return_value = False
        mock_trello.create_card.return_value = {
            "id": "card_123",
            "shortUrl": "https://trello.com/c/card123",
        }
        mock_trello.add_checklist_to_card.return_value = {"id": "checklist_1"}
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        result = service.process_daily_intake(limit=5, dry_run=False)
        
        assert result.total_entries_found == 2
        assert result.cards_created == 2
        assert result.cards_skipped == 0
        assert result.cards_failed == 0
        assert result.success_rate == 100.0
        assert len(result.details) == 2
    
    def test_process_daily_intake_dry_run(self, mock_settings, mock_crm, mock_trello, sample_investor):
        """Test dry run mode doesn't create actual cards."""
        mock_crm.get_top_scored_investors.return_value = [sample_investor]
        mock_trello.check_card_exists_by_prefix.return_value = False
        mock_trello.create_card.return_value = {
            "id": "dry_run_card_id",
            "name": "Investor Packet: John Doe",
            "shortUrl": "https://trello.com/c/dryrun",
        }
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        result = service.process_daily_intake(limit=5, dry_run=True)
        
        assert result.dry_run is True
        assert result.cards_created == 0  # Dry run doesn't count as created
        mock_trello.create_card.assert_called_once()
        # Verify dry_run flag was passed
        call_args = mock_trello.create_card.call_args
        assert call_args[1]["dry_run"] is True
    
    def test_process_daily_intake_with_crm_failure(self, mock_settings, mock_crm, mock_trello):
        """Test handling of CRM database failure."""
        mock_crm.get_top_scored_investors.side_effect = Exception("Database connection failed")
        
        service = DailyIntakeService(
            settings=mock_settings,
            crm_repository=mock_crm,
            trello_client=mock_trello,
        )
        
        result = service.process_daily_intake(limit=5)
        
        assert result.total_entries_found == 0
        assert result.cards_created == 0
        assert len(result.details) == 0
