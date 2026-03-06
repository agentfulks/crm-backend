"""Crunchbase fetcher for VC data."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional

from ..models import DataSource, RawFund, SyncConfig
from .base import BaseFetcher

logger = logging.getLogger(__name__)


class CrunchbaseFetcher(BaseFetcher):
    """Fetcher for Crunchbase API."""
    
    BASE_URL = "https://api.crunchbase.com/v4"
    
    def __init__(self, config: SyncConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("Crunchbase API key is required")
        self.api_key = config.api_key
    
    @property
    def data_source(self) -> DataSource:
        return DataSource.CRUNCHBASE
    
    def _build_search_query(self, **filters) -> Dict[str, Any]:
        """Build Crunchbase search query for VC funds."""
        query = {
            "field_ids": [
                "identifier", "name", "website_url", "linkedin", "twitter",
                "location_identifiers", "short_description", "categories",
                "funding_total", "funding_round", "raised", "investor_type"
            ],
            "order": [
                {"field_id": "funding_total", "sort": "desc"}
            ],
            "limit": 100
        }
        
        # Build filter for investor type = venture capital
        query["query"] = [
            {
                "type": "predicate",
                "field_id": "investor_type",
                "operator_id": "includes",
                "values": ["venture_capital"]
            }
        ]
        
        # Add category filters for gaming/AI
        sectors = filters.get('sectors', self.config.target_sectors)
        if sectors:
            category_values = []
            for sector in sectors:
                sector_lower = sector.lower()
                if sector_lower in ['gaming', 'games']:
                    category_values.extend(['Gaming', 'Video Games', 'eSports'])
                elif sector_lower in ['ai', 'artificial intelligence']:
                    category_values.extend(['Artificial Intelligence', 'Machine Learning'])
            
            if category_values:
                query["query"].append({
                    "type": "predicate",
                    "field_id": "categories",
                    "operator_id": "includes",
                    "values": category_values
                })
        
        return query
    
    def fetch_funds(
        self, 
        limit: Optional[int] = None,
        **filters
    ) -> Iterator[RawFund]:
        """Fetch VC funds from Crunchbase."""
        query = self._build_search_query(**filters)
        
        total_fetched = 0
        after_id = None
        
        while True:
            if limit and total_fetched >= limit:
                break
            
            if after_id:
                query["after_id"] = after_id
            
            try:
                response = self._make_request(
                    "POST",
                    f"{self.BASE_URL}/searches/organizations",
                    headers={"X-cb-user-key": self.api_key},
                    json=query
                )
                data = response.json()
                
                entities = data.get('entities', [])
                if not entities:
                    break
                
                for entity in entities:
                    if limit and total_fetched >= limit:
                        break
                    
                    fund = self._map_crunchbase_entity(entity)
                    if fund:
                        yield fund
                        total_fetched += 1
                
                # Get next page cursor
                paging = data.get('paging', {})
                after_id = paging.get('after_id')
                
                if not after_id:
                    break
                
            except Exception as e:
                logger.error(f"Error fetching from Crunchbase: {e}")
                break
    
    def _map_crunchbase_entity(self, entity: Dict[str, Any]) -> Optional[RawFund]:
        """Map Crunchbase entity to RawFund."""
        properties = entity.get('properties', {})
        
        if not properties.get('name'):
            return None
        
        # Extract location
        locations = properties.get('location_identifiers', [])
        city = None
        region = None
        country = None
        
        for loc in locations:
            loc_type = loc.get('location_type', '').lower()
            if loc_type == 'city':
                city = loc.get('value')
            elif loc_type == 'region':
                region = loc.get('value')
            elif loc_type == 'country':
                country = loc.get('value')
        
        # Get categories
        categories = properties.get('categories', [])
        
        # Check if gaming/AI focused
        is_gaming = any('game' in c.lower() for c in categories)
        is_ai = any(c.lower() in ['artificial intelligence', 'machine learning', 'ai'] for c in categories)
        
        sector_focus = []
        if is_gaming:
            sector_focus.append('gaming')
        if is_ai:
            sector_focus.append('ai')
        
        # Get funding info
        funding_total = properties.get('funding_total', {})
        check_size_max = funding_total.get('value_usd') if funding_total else None
        
        # Extract social URLs
        linkedin = properties.get('linkedin', {}).get('value') if isinstance(properties.get('linkedin'), dict) else None
        twitter = properties.get('twitter', {}).get('value') if isinstance(properties.get('twitter'), dict) else None
        
        return RawFund(
            data_source=self.data_source,
            source_id=entity.get('uuid', ''),
            name=properties.get('name', ''),
            firm_type='Venture Capital',
            website_url=properties.get('website_url'),
            linkedin_url=linkedin,
            twitter_url=twitter,
            hq_city=city,
            hq_region=region,
            hq_country=country,
            stage_focus=[],  # Crunchbase doesn't directly provide stage focus for funds
            sector_focus=sector_focus,
            check_size_min=None,
            check_size_max=check_size_max,
            check_size_currency='USD',
            target_countries=[country] if country else [],
            overview=properties.get('short_description'),
            funding_requirements=None,
            tags={
                'crunchbase_uuid': entity.get('uuid'),
                'categories': categories,
                'investor_type': properties.get('investor_type', []),
            },
            raw_data=entity
        )
