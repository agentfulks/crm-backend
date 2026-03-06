"""Base fetcher interface for VC data sources."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models import DataSource, RawFund, SyncConfig

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_call = time.time()


class BaseFetcher(ABC):
    """Abstract base class for VC data fetchers."""
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @property
    @abstractmethod
    def data_source(self) -> DataSource:
        """Return the data source type."""
        pass
    
    @abstractmethod
    def fetch_funds(
        self, 
        limit: Optional[int] = None,
        **filters
    ) -> Iterator[RawFund]:
        """
        Fetch funds from the data source.
        
        Args:
            limit: Maximum number of funds to fetch
            **filters: Source-specific filters
            
        Yields:
            RawFund objects
        """
        pass
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> requests.Response:
        """Make rate-limited HTTP request."""
        self.rate_limiter.wait()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def map_to_raw_fund(self, raw_data: Dict[str, Any]) -> RawFund:
        """Map raw API data to RawFund model."""
        return RawFund(
            data_source=self.data_source,
            source_id=str(raw_data.get('id', '')),
            name=raw_data.get('name', ''),
            firm_type=raw_data.get('firm_type'),
            website_url=raw_data.get('website_url'),
            linkedin_url=raw_data.get('linkedin_url'),
            twitter_url=raw_data.get('twitter_url'),
            hq_city=raw_data.get('hq_city'),
            hq_region=raw_data.get('hq_region'),
            hq_country=raw_data.get('hq_country'),
            stage_focus=raw_data.get('stage_focus', []),
            sector_focus=raw_data.get('sector_focus', []),
            check_size_min=raw_data.get('check_size_min'),
            check_size_max=raw_data.get('check_size_max'),
            check_size_currency=raw_data.get('check_size_currency', 'USD'),
            target_countries=raw_data.get('target_countries', []),
            overview=raw_data.get('overview'),
            funding_requirements=raw_data.get('funding_requirements'),
            tags=raw_data.get('tags', {}),
            raw_data=raw_data
        )
