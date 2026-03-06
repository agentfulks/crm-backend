"""Tests for Trello Client."""

import pytest
from unittest.mock import MagicMock, patch
import requests

from src.trello_client import TrelloClient, TrelloAPIError
from src.models import TrelloCard


class TestTrelloClient:
    """Test suite for TrelloClient."""
    
    @pytest.fixture
    def mock_settings(self):
        """Fixture for mock settings."""
        settings = MagicMock()
        settings.trello_api_key = "test_key"
        settings.trello_token = "test_token"
        settings.trello_api_base = "https://api.trello.com/1"
        settings.trello_board_id = "board_123"
        settings.trello_list_id = "list_456"
        settings.label_ids = ["label_1", "label_2"]
        settings.request_timeout = 30
        settings.max_retries = 3
        settings.retry_delay = 1.0
        return settings
    
    @pytest.fixture
    def client(self, mock_settings):
        """Fixture for TrelloClient instance."""
        return TrelloClient(settings=mock_settings)
    
    def test_client_initialization(self, mock_settings):
        """Test client initialization."""
        client = TrelloClient(settings=mock_settings)
        
        assert client.settings == mock_settings
        assert client.base_url == "https://api.trello.com/1"
    
    @patch("src.trello_client.requests.Session.request")
    def test_create_card_success(self, mock_request, client):
        """Test successful card creation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "card_123",
            "name": "Test Card",
            "shortUrl": "https://trello.com/c/card123",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
            idLabels=["label_1"],
        )
        
        result = client.create_card(card, dry_run=False)
        
        assert result["id"] == "card_123"
        assert result["name"] == "Test Card"
        mock_request.assert_called_once()
    
    @patch("src.trello_client.requests.Session.request")
    def test_create_card_dry_run(self, mock_request, client):
        """Test dry run mode doesn't make API call."""
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
        )
        
        result = client.create_card(card, dry_run=True)
        
        assert result["id"] == "dry_run_card_id"
        mock_request.assert_not_called()
    
    @patch("src.trello_client.requests.Session.request")
    def test_rate_limit_retry(self, mock_request, client):
        """Test retry logic on rate limit (429)."""
        # First two calls return 429, third succeeds
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"id": "card_123"}
        mock_response_success.raise_for_status.return_value = None
        
        mock_request.side_effect = [
            mock_response_429,
            mock_response_429,
            mock_response_success,
        ]
        
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
        )
        
        result = client.create_card(card, dry_run=False)
        
        assert result["id"] == "card_123"
        assert mock_request.call_count == 3
    
    @patch("src.trello_client.requests.Session.request")
    def test_max_retries_exceeded(self, mock_request, client):
        """Test that exception is raised after max retries."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
        )
        
        with pytest.raises(TrelloAPIError) as exc_info:
            client.create_card(card, dry_run=False)
        
        assert "Rate limit exceeded" in str(exc_info.value)
        assert mock_request.call_count == 4  # Initial + 3 retries
    
    @patch("src.trello_client.requests.Session.request")
    def test_server_error_retry(self, mock_request, client):
        """Test retry logic on server error (5xx)."""
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"id": "card_123"}
        mock_response_success.raise_for_status.return_value = None
        
        mock_request.side_effect = [
            mock_response_500,
            mock_response_success,
        ]
        
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
        )
        
        result = client.create_card(card, dry_run=False)
        
        assert result["id"] == "card_123"
        assert mock_request.call_count == 2
    
    @patch("src.trello_client.requests.Session.request")
    def test_check_card_exists_by_prefix(self, mock_request, client):
        """Test duplicate card detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cards": [
                {"id": "card_1", "name": "Investor Packet: John Doe"},
                {"id": "card_2", "name": "Other Card"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        exists = client.check_card_exists_by_prefix(
            name_prefix="Investor Packet: John Doe",
            board_id="board_123",
        )
        
        assert exists is True
    
    @patch("src.trello_client.requests.Session.request")
    def test_check_card_not_exists(self, mock_request, client):
        """Test when no duplicate card exists."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cards": [
                {"id": "card_1", "name": "Other Card"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        exists = client.check_card_exists_by_prefix(
            name_prefix="Investor Packet: John Doe",
            board_id="board_123",
        )
        
        assert exists is False
    
    @patch("src.trello_client.requests.Session.request")
    def test_timeout_retry(self, mock_request, client):
        """Test retry on request timeout."""
        from requests.exceptions import Timeout
        
        mock_request.side_effect = [
            Timeout("Connection timed out"),
            Timeout("Connection timed out"),
            MagicMock(
                status_code=200,
                json=lambda: {"id": "card_123"},
                raise_for_status=lambda: None,
            ),
        ]
        
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_456",
        )
        
        result = client.create_card(card, dry_run=False)
        
        assert result["id"] == "card_123"
        assert mock_request.call_count == 3
    
    @patch("src.trello_client.requests.Session.request")
    def test_add_checklist_to_card(self, mock_request, client):
        """Test adding checklist to a card."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "checklist_1", "name": "Test Checklist"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = client.add_checklist_to_card(
            card_id="card_123",
            name="Test Checklist",
            items=["Item 1", "Item 2"],
        )
        
        assert result["id"] == "checklist_1"
        # Should be called for checklist + 2 items
        assert mock_request.call_count == 3
