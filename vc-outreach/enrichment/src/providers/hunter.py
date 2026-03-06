"""Hunter.io enrichment provider for email discovery."""
from __future__ import annotations

import logging
from typing import Iterator, List, Optional

import requests

from ..models import ContactRole, EnrichmentSource, RawContact

logger = logging.getLogger(__name__)


class HunterEnricher:
    """Enrich contacts using Hunter.io."""
    
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: str, rate_limit_per_minute: int = 60):
        self.api_key = api_key
        self.rate_limit_per_minute = rate_limit_per_minute
        self.session = requests.Session()
    
    def find_contacts_by_domain(
        self,
        domain: str,
        company_name: Optional[str] = None,
        max_results: int = 10,
        seniority: Optional[str] = None,
        department: Optional[str] = None
    ) -> Iterator[RawContact]:
        """
        Find contacts by company domain.
        
        Args:
            domain: Company domain (e.g., "accel.com")
            company_name: Company name for context
            max_results: Maximum contacts to return
            seniority: Filter by seniority (junior, senior, executive)
            department: Filter by department
        """
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "limit": min(max_results, 100)
        }
        
        if seniority:
            params["seniority"] = seniority
        if department:
            params["department"] = department
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/domain-search",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            emails = data.get('data', {}).get('emails', [])
            
            for email_data in emails:
                contact = self._map_email_to_contact(email_data, company_name or domain)
                if contact:
                    yield contact
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter API error for {domain}: {e}")
            raise
    
    def verify_email(self, email: str) -> dict:
        """Verify an email address."""
        params = {
            "email": email,
            "api_key": self.api_key
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/email-verifier",
                params=params
            )
            response.raise_for_status()
            return response.json().get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter verification error for {email}: {e}")
            return {}
    
    def find_email(
        self,
        first_name: str,
        last_name: str,
        domain: str
    ) -> Optional[dict]:
        """Find email for a specific person."""
        params = {
            "first_name": first_name,
            "last_name": last_name,
            "domain": domain,
            "api_key": self.api_key
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/email-finder",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get('data')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter email finder error: {e}")
            return None
    
    def _map_email_to_contact(
        self,
        email_data: dict,
        fund_name: str
    ) -> Optional[RawContact]:
        """Map Hunter email data to RawContact."""
        first_name = email_data.get('first_name')
        last_name = email_data.get('last_name')
        
        if not first_name and not last_name:
            return None
        
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        
        title = email_data.get('position')
        role = self._infer_role(title)
        
        email = email_data.get('value')
        verification = email_data.get('verification', {})
        
        return RawContact(
            source=EnrichmentSource.HUNTER,
            source_id=email,  # Use email as ID
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            email_verified=verification.get('status') == 'valid',
            email_type='work',
            title=title,
            role=role,
            department=email_data.get('department'),
            seniority=email_data.get('seniority'),
            linkedin_url=email_data.get('linkedin'),
            twitter_url=None,
            fund_name=fund_name,
            confidence_score=self._calculate_confidence(email_data),
            tags={
                'sources': email_data.get('sources', []),
                'phone_number': email_data.get('phone_number'),
            },
            raw_data=email_data
        )
    
    def _infer_role(self, title: Optional[str]) -> ContactRole:
        """Infer contact role from title."""
        if not title:
            return ContactRole.UNKNOWN
        
        title_lower = title.lower()
        
        if 'managing partner' in title_lower:
            return ContactRole.MANAGING_PARTNER
        elif 'general partner' in title_lower or 'gp' in title_lower:
            return ContactRole.GENERAL_PARTNER
        elif 'partner' in title_lower:
            return ContactRole.PARTNER
        elif 'principal' in title_lower:
            return ContactRole.PRINCIPAL
        elif 'vice president' in title_lower or 'vp' in title_lower:
            return ContactRole.VP
        elif 'associate' in title_lower:
            return ContactRole.ASSOCIATE
        elif 'analyst' in title_lower:
            return ContactRole.ANALYST
        elif 'founder' in title_lower:
            return ContactRole.FOUNDER
        elif 'ceo' in title_lower:
            return ContactRole.CEO
        
        return ContactRole.UNKNOWN
    
    def _calculate_confidence(self, email_data: dict) -> float:
        """Calculate confidence score for contact data."""
        score = 0.5
        
        # Confidence based on sources
        sources = email_data.get('sources', [])
        if len(sources) > 5:
            score += 0.3
        elif len(sources) > 0:
            score += 0.2
        
        # Confidence based on verification
        verification = email_data.get('verification', {})
        if verification.get('status') == 'valid':
            score += 0.3
        
        # Confidence based on data completeness
        if email_data.get('first_name') and email_data.get('last_name'):
            score += 0.1
        if email_data.get('position'):
            score += 0.1
        
        return min(score, 1.0)
