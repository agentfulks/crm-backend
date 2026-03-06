"""Tests for fetchers."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from src.fetchers.apollo import ApolloFetcher
from src.fetchers.base import RateLimiter
from src.fetchers.crunchbase import CrunchbaseFetcher
from src.models import DataSource, RawFund, SyncConfig


class TestRateLimiter:
    """Test rate limiting."""
    
    def test_rate_limiter_calculates_interval(self):
        """Test rate limiter calculates correct interval."""
        limiter = RateLimiter(calls_per_minute=60)
        assert limiter.min_interval == 1.0
        
        limiter = RateLimiter(calls_per_minute=120)
        assert limiter.min_interval == 0.5
    
    @patch('time.time')
    @patch('time.sleep')
    def test_rate_limiter_waits(self, mock_sleep, mock_time):
        """Test rate limiter waits between calls."""
        limiter = RateLimiter(calls_per_minute=60)
        
        # First call
        mock_time.return_value = 100.0
        limiter.wait()
        assert not mock_sleep.called
        
        # Second call immediately after
        mock_time.return_value = 100.0
        limiter.wait()
        mock_sleep.assert_called_once()


class TestApolloFetcher:
    """Test Apollo fetcher."""
    
    @pytest.fixture
    def config(self):
        return SyncConfig(
            data_source=DataSource.APOLLO,
            api_key='test_key',
            target_sectors=['gaming', 'ai']
        )
    
    def test_apollo_fetcher_creation(self, config):
        """Test Apollo fetcher initialization."""
        fetcher = ApolloFetcher(config)
        assert fetcher.data_source == DataSource.APOLLO
        assert fetcher.api_key == 'test_key'
    
    def test_apollo_fetcher_requires_api_key(self):
        """Test Apollo fetcher requires API key."""
        config = SyncConfig(
            data_source=DataSource.APOLLO,
            api_key=None
        )
        with pytest.raises(ValueError, match="API key is required"):
            ApolloFetcher(config)
    
    @patch('src.fetchers.apollo.ApolloFetcher._make_request')
    def test_apollo_fetch_funds(self, mock_request, config):
        """Test Apollo fund fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'organizations': [
                {
                    'id': '123',
                    'name': 'Test Fund',
                    'website_url': 'https://test.com',
                    'city': 'San Francisco',
                    'country': 'USA',
                    'keywords': ['gaming', 'ai']
                }
            ]
        }
        mock_request.return_value = mock_response
        
        fetcher = ApolloFetcher(config)
        funds = list(fetcher.fetch_funds(limit=1))
        
        assert len(funds) == 1
        assert funds[0].name == 'Test Fund'
        assert funds[0].data_source == DataSource.APOLLO


class TestCrunchbaseFetcher:
    """Test Crunchbase fetcher."""
    
    @pytest.fixture
    def config(self):
        return SyncConfig(
            data_source=DataSource.CRUNCHBASE,
            api_key='test_key',
            target_sectors=['gaming', 'ai']
        )
    
    def test_crunchbase_fetcher_creation(self, config):
        """Test Crunchbase fetcher initialization."""
        fetcher = CrunchbaseFetcher(config)
        assert fetcher.data_source == DataSource.CRUNCHBASE
        assert fetcher.api_key == 'test_key'
    
    def test_crunchbase_fetcher_requires_api_key(self):
        """Test Crunchbase fetcher requires API key."""
        config = SyncConfig(
            data_source=DataSource.CRUNCHBASE,
            api_key=None
        )
        with pytest.raises(ValueError, match="API key is required"):
            CrunchbaseFetcher(config)
    
    @patch('src.fetchers.crunchbase.CrunchbaseFetcher._make_request')
    def test_crunchbase_fetch_funds(self, mock_request, config):
        """Test Crunchbase fund fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'entities': [
                {
                    'uuid': '456',
                    'properties': {
                        'name': 'VC Fund',
                        'website_url': 'https://vcfund.com',
                        'short_description': 'Gaming and AI investor',
                        'categories': ['Gaming', 'Artificial Intelligence'],
                        'location_identifiers': [
                            {'value': 'San Francisco', 'location_type': 'city'},
                            {'value': 'CA', 'location_type': 'region'},
                            {'value': 'USA', 'location_type': 'country'}
                        ]
                    }
                }
            ]
        }
        mock_request.return_value = mock_response
        
        fetcher = CrunchbaseFetcher(config)
        funds = list(fetcher.fetch_funds(limit=1))
        
        assert len(funds) == 1
        assert funds[0].name == 'VC Fund'
        assert 'gaming' in funds[0].sector_focus


class TestFetcherFactory:
    """Test fetcher factory."""
    
    def test_get_apollo_fetcher(self):
        """Test getting Apollo fetcher."""
        from src.fetchers import get_fetcher
        
        config = SyncConfig(
            data_source=DataSource.APOLLO,
            api_key='test'
        )
        fetcher = get_fetcher('apollo', config)
        assert isinstance(fetcher, ApolloFetcher)
    
    def test_get_crunchbase_fetcher(self):
        """Test getting Crunchbase fetcher."""
        from src.fetchers import get_fetcher
        
        config = SyncConfig(
            data_source=DataSource.CRUNCHBASE,
            api_key='test'
        )
        fetcher = get_fetcher('crunchbase', config)
        assert isinstance(fetcher, CrunchbaseFetcher)
    
    def test_get_fetcher_unknown_source(self):
        """Test error on unknown source."""
        from src.fetchers import get_fetcher
        
        config = SyncConfig(data_source=DataSource.APOLLO)
        with pytest.raises(ValueError, match="Unknown data source"):
            get_fetcher('unknown', config)
