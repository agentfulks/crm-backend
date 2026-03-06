"""Apollo.io fetcher for VC data."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional

from ..models import DataSource, RawFund, SyncConfig
from .base import BaseFetcher

logger = logging.getLogger(__name__)


class ApolloFetcher(BaseFetcher):
    """Fetcher for Apollo.io API."""
    
    BASE_URL = "https://api.apollo.io/v1"
    
    def __init__(self, config: SyncConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("Apollo API key is required")
        self.api_key = config.api_key
    
    @property
    def data_source(self) -> DataSource:
        return DataSource.APOLLO
    
    def _build_search_query(self, **filters) -> Dict[str, Any]:
        """Build Apollo search query for VC funds."""
        query = {
            "api_key": self.api_key,
            "page": 1,
            "per_page": 100,
            "organization_ids": [],
            "organization_keyword_tags": []
        }
        
        # Add sector filters
        sectors = filters.get('sectors', self.config.target_sectors)
        if sectors:
            # Map to Apollo categories
            sector_keywords = []
            for sector in sectors:
                if sector.lower() in ['gaming', 'games', 'video games']:
                    sector_keywords.extend(['gaming', 'video games', 'game development'])
                elif sector.lower() in ['ai', 'artificial intelligence', 'machine learning']:
                    sector_keywords.extend(['artificial intelligence', 'machine learning', 'AI'])
            query["organization_keyword_tags"] = list(set(sector_keywords))
        
        # Add stage filters (Apollo uses funding stage filters)
        stages = filters.get('stages', self.config.stage_focus)
        if stages:
            query["organization_funding_stage"] = stages
        
        return query
    
    def fetch_funds(
        self, 
        limit: Optional[int] = None,
        **filters
    ) -> Iterator[RawFund]:
        """Fetch VC funds from Apollo.io."""
        query = self._build_search_query(**filters)
        
        total_fetched = 0
        page = 1
        
        while True:
            if limit and total_fetched >= limit:
                break
            
            query["page"] = page
            
            try:
                response = self._make_request(
                    "POST",
                    f"{self.BASE_URL}/mixed_companies/search",
                    json=query
                )
                data = response.json()
                
                organizations = data.get('organizations', [])
                if not organizations:
                    break
                
                for org in organizations:
                    if limit and total_fetched >= limit:
                        break
                    
                    fund = self._map_apollo_org(org)
                    if fund:
                        yield fund
                        total_fetched += 1
                
                # Check pagination
                if len(organizations) < query["per_page"]:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching from Apollo: {e}")
                break
    
    def _map_apollo_org(self, org: Dict[str, Any]) -> Optional[RawFund]:
        """Map Apollo organization to RawFund."""
        if not org.get('name'):
            return None
        
        # Extract investment info
        funding_data = org.get('funding_data', {})
        
        # Determine stage focus from funding data
        stage_focus = []
        if funding_data.get('last_funding_round_type'):
            stage = funding_data['last_funding_round_type'].lower()
            if 'seed' in stage:
                stage_focus.append('seed')
            elif 'series_a' in stage or 'series a' in stage:
                stage_focus.append('series_a')
            elif 'series_b' in stage or 'series b' in stage:
                stage_focus.append('series_b')
        
        # Get check size from funding data
        check_size_min = None
        check_size_max = None
        if funding_data.get('raised'):
            raised = funding_data['raised']
            if isinstance(raised, (int, float)):
                check_size_max = float(raised)
        
        return RawFund(
            data_source=self.data_source,
            source_id=str(org.get('id', '')),
            name=org.get('name', ''),
            firm_type=org.get('industry'),
            website_url=org.get('website_url'),
            linkedin_url=org.get('linkedin_url'),
            twitter_url=org.get('twitter_url'),
            hq_city=org.get('city'),
            hq_region=org.get('state'),
            hq_country=org.get('country'),
            stage_focus=stage_focus,
            sector_focus=org.get('keywords', []),
            check_size_min=check_size_min,
            check_size_max=check_size_max,
            check_size_currency='USD',
            target_countries=[org.get('country')] if org.get('country') else [],
            overview=org.get('description'),
            funding_requirements=None,
            tags={
                'apollo_id': org.get('id'),
                'employee_count': org.get('estimated_num_employees'),
                'funding_total': funding_data.get('raised'),
                'founded_year': org.get('founded_year'),
            },
            raw_data=org
        )


# Add fetcher to base.py imports for fetcher factory
# This is done at the module level to avoid circular imports
