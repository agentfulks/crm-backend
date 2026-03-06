"""Source automation tests."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.models import DataSource, RawFund, SyncConfig, ProcessedFund
from src.sync import SyncOrchestrator, run_daily_sync


class TestSyncOrchestrator:
    """Test sync orchestrator."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return Mock()
    
    @pytest.fixture
    def config(self):
        """Create test sync config."""
        return SyncConfig(
            data_source=DataSource.APOLLO,
            api_key='test_key',
            target_sectors=['gaming'],
            dedupe_threshold=0.85
        )
    
    def test_orchestrator_initialization(self, mock_session):
        """Test orchestrator initialization."""
        orchestrator = SyncOrchestrator(mock_session)
        assert orchestrator.session == mock_session
        assert orchestrator.sync_run is None
    
    @patch('src.sync.get_fetcher')
    @patch('src.sync.deduplicate_funds')
    @patch('src.sync.insert_funds')
    def test_run_sync_success(
        self, 
        mock_insert, 
        mock_dedupe, 
        mock_get_fetcher,
        mock_session,
        config
    ):
        """Test successful sync run."""
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_funds.return_value = iter([
            RawFund(
                data_source=DataSource.APOLLO,
                source_id='1',
                name='Test Fund'
            )
        ])
        mock_get_fetcher.return_value = mock_fetcher
        
        mock_dedupe.return_value = (
            [RawFund(data_source=DataSource.APOLLO, source_id='1', name='Test Fund')],
            [],
            []
        )
        
        mock_insert.return_value = (1, 0, 0)
        
        # Run sync
        orchestrator = SyncOrchestrator(mock_session)
        result = orchestrator.run_sync(config, limit=1)
        
        # Verify
        assert result.status == "completed"
        assert result.records_fetched == 1
        assert result.records_new == 1
        mock_insert.assert_called_once()
    
    @patch('src.sync.get_fetcher')
    def test_run_sync_fetch_failure(self, mock_get_fetcher, mock_session, config):
        """Test sync handles fetch failure."""
        mock_get_fetcher.side_effect = Exception("API error")
        
        orchestrator = SyncOrchestrator(mock_session)
        
        with pytest.raises(Exception):
            orchestrator.run_sync(config)
        
        assert orchestrator.sync_run.status == "failed"


class TestRunDailySync:
    """Test daily sync runner."""
    
    @pytest.fixture
    def mock_session(self):
        return Mock()
    
    def test_run_daily_sync_skips_disabled_configs(self, mock_session):
        """Test disabled configs are skipped."""
        configs = [
            SyncConfig(data_source=DataSource.APOLLO, enabled=False),
            SyncConfig(data_source=DataSource.CRUNCHBASE, enabled=False),
        ]
        
        results = run_daily_sync(mock_session, configs)
        assert len(results) == 0
    
    @patch('src.sync.SyncOrchestrator')
    def test_run_daily_sync_processes_enabled_configs(self, mock_orchestrator, mock_session):
        """Test enabled configs are processed."""
        configs = [
            SyncConfig(data_source=DataSource.APOLLO, enabled=True, api_key='test'),
        ]
        
        mock_instance = Mock()
        mock_instance.run_sync.return_value = Mock(
            status="completed",
            records_fetched=10
        )
        mock_orchestrator.return_value = mock_instance
        
        results = run_daily_sync(mock_session, configs)
        
        assert len(results) == 1
        mock_instance.run_sync.assert_called_once()


class TestModels:
    """Test data models."""
    
    def test_raw_fund_creation(self):
        """Test RawFund model."""
        fund = RawFund(
            data_source=DataSource.APOLLO,
            source_id='123',
            name='Test Fund',
            website_url='https://test.com'
        )
        
        assert fund.name == 'Test Fund'
        assert fund.data_source == DataSource.APOLLO
        assert fund.source_id == '123'
    
    def test_raw_fund_stage_focus_validator(self):
        """Test stage_focus validator handles strings."""
        fund = RawFund(
            data_source=DataSource.APOLLO,
            source_id='123',
            name='Test Fund',
            stage_focus='seed,series_a'  # String input
        )
        
        assert fund.stage_focus == ['seed', 'series_a']
    
    def test_sync_config_default_values(self):
        """Test SyncConfig defaults."""
        config = SyncConfig(data_source=DataSource.APOLLO)
        
        assert config.enabled is True
        assert config.schedule == "0 6 * * *"
        assert config.dedupe_threshold == 0.85
        assert config.check_size_currency == 'USD'
