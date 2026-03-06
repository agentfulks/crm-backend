"""Apollo enrichment provider for contact discovery."""
from __future__ import annotations

import logging
from typing import Iterator, List, Optional

import requests

from ..models import ContactRole, EnrichmentSource, RawContact

logger = logging.getLogger(__name__)


class ApolloEnricher:
    """Enrich contacts using Apollo.io."""
    
    BASE_URL = "https://api.apollo.io/v1"
    
    def __init__(self, api_key: str, rate_limit_per_minute: int = 60):
        self.api_key = api_key
        self.rate_limit_per_minute = rate_limit_per_minute
        self.session = requests.Session()
    
    def find_contacts_by_company(
        self,
        company_name: str,
        company_website: Optional[str] = None,
        max_results: int = 10,
        titles: Optional[List[str]] = None
    ) -> Iterator[RawContact]:
        """
        Find contacts at a specific company.
        
        Args:
            company_name: Name of the company/firm
            company_website: Company website URL
            max_results: Maximum contacts to return
            titles: Filter by job titles
        """
        # First, search for the organization
        org_query = {
            "api_key": self.api_key,
            "q_organization_domains": company_website.replace('https://', '').replace('http://', '').split('/')[0] if company_website else None,
            "organization_name": company_name,
            "per_page": 1
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/mixed_companies/search",
                json=org_query
            )
            response.raise_for_status()
            data = response.json()
            
            organizations = data.get('organizations', [])
            if not organizations:
                logger.warning(f"No organization found for: {company_name}")
                return
            
            org_id = organizations[0].get('id')
            
            # Now search for people at this organization
            people_query = {
                "api_key": self.api_key,
                "organization_ids": [org_id],
                "per_page": min(max_results, 100),
                "person_titles": titles or [
                    "Partner", "Managing Partner", "General Partner",
                    "Principal", "VP", "Investor", "Founder"
                ]
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/mixed_people/search",
                json=people_query
            )
            response.raise_for_status()
            data = response.json()
            
            people = data.get('people', [])
            for person in people:
                contact = self._map_person_to_contact(person, company_name)
                if contact:
                    yield contact
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for {company_name}: {e}")
            raise
    
    def find_email(
        self,
        first_name: str,
        last_name: str,
        company_domain: str
    ) -> Optional[str]:
        """Find email for a specific person."""
        query = {
            "api_key": self.api_key,
            "first_name": first_name,
            "last_name": last_name,
            "domain": company_domain
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/people/match",
                json=query
            )
            response.raise_for_status()
            data = response.json()
            
            person = data.get('person', {})
            email = person.get('email')
            
            return email
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo email lookup error: {e}")
            return None
    
    def _map_person_to_contact(
        self,
        person: dict,
        fund_name: str
    ) -> Optional[RawContact]:
        """Map Apollo person to RawContact."""
        if not person.get('name'):
            return None
        
        name_parts = person.get('name', '').split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        title = person.get('title', '')
        role = self._infer_role(title)
        
        # Get email info
        email = person.get('email')
        email_verified = person.get('email_status') == 'verified'
        
        return RawContact(
            source=EnrichmentSource.APOLLO,
            source_id=str(person.get('id', '')),
            full_name=person.get('name', ''),
            first_name=first_name,
            last_name=last_name,
            email=email,
            email_verified=email_verified,
            email_type=self._get_email_type(email),
            title=title,
            role=role,
            department=person.get('department'),
            seniority=self._infer_seniority(title),
            linkedin_url=person.get('linkedin_url'),
            twitter_url=person.get('twitter_url'),
            fund_name=fund_name,
            confidence_score=self._calculate_confidence(person),
            tags={
                'apollo_id': person.get('id'),
                'headline': person.get('headline'),
                'country': person.get('country'),
                'state': person.get('state'),
            },
            raw_data=person
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
    
    def _infer_seniority(self, title: Optional[str]) -> Optional[str]:
        """Infer seniority level from title."""
        if not title:
            return None
        
        title_lower = title.lower()
        
        if any(r in title_lower for r in ['partner', 'founder', 'ceo', 'managing']):
            return 'executive'
        elif any(r in title_lower for r in ['principal', 'vp', 'director']):
            return 'senior'
        elif any(r in title_lower for r in ['associate', 'analyst']):
            return 'entry'
        
        return None
    
    def _get_email_type(self, email: Optional[str]) -> Optional[str]:
        """Determine email type."""
        if not email:
            return None
        
        if email.endswith(('@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com')):
            return 'personal'
        elif any(generic in email for generic in ['info@', 'contact@', 'hello@', 'support@']):
            return 'generic'
        else:
            return 'work'
    
    def _calculate_confidence(self, person: dict) -> float:
        """Calculate confidence score for contact data."""
        score = 0.5  # Base score
        
        if person.get('email'):
            score += 0.2
        if person.get('email_status') == 'verified':
            score += 0.2
        if person.get('title'):
            score += 0.1
        
        return min(score, 1.0)
