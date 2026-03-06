"""Fetchers package for VC data sources."""
from __future__ import annotations

from .apollo import ApolloFetcher
from .base import BaseFetcher, RateLimiter
from .crunchbase import CrunchbaseFetcher

__all__ = [
    'BaseFetcher',
    'ApolloFetcher', 
    'CrunchbaseFetcher',
    'RateLimiter',
]


# Fetcher factory
def get_fetcher(source: str, config) -> BaseFetcher:
    """Get appropriate fetcher for data source."""
    from ..models import DataSource
    
    source_map = {
        DataSource.APOLLO.value: ApolloFetcher,
        DataSource.CRUNCHBASE.value: CrunchbaseFetcher,
    }
    
    fetcher_class = source_map.get(source.lower())
    if not fetcher_class:
        raise ValueError(f"Unknown data source: {source}")
    
    return fetcher_class(config)
