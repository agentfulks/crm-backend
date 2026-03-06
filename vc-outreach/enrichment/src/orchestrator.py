"""Enrichment orchestrator for contact discovery."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterator, List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.fund import Fund

from .models import (
    ContactRole,
    EnrichmentBatch,
    EnrichmentJob,
    EnrichmentResult,
    EnrichmentSource,
    RawContact
)
from .providers.apollo import ApolloEnricher
from .providers.hunter import HunterEnricher

logger = logging.getLogger(__name__)


class EnrichmentOrchestrator:
    """Orchestrates contact enrichment from multiple sources."""
    
    def __init__(self, session: Session, job: EnrichmentJob):
        self.session = session
        self.job = job
        self._providers = {}
        
        # Initialize providers
        if EnrichmentSource.APOLLO in job.sources and job.apollo_api_key:
            self._providers[EnrichmentSource.APOLLO] = ApolloEnricher(
                job.apollo_api_key,
                job.rate_limit_per_minute
            )
        
        if EnrichmentSource.HUNTER in job.sources and job.hunter_api_key:
            self._providers[EnrichmentSource.HUNTER] = HunterEnricher(
                job.hunter_api_key,
                job.rate_limit_per_minute
            )
    
    def run_enrichment(self) -> EnrichmentBatch:
        """Run full enrichment job."""
        batch = EnrichmentBatch(
            batch_id=str(uuid4()),
            job=self.job,
            total_funds=len(self.job.fund_ids),
            status="running",
            started_at=datetime.utcnow()
        )
        
        logger.info(f"Starting enrichment batch {batch.batch_id} for {batch.total_funds} funds")
        
        # Get funds to enrich
        if self.job.fund_ids:
            funds = self.session.execute(
                select(Fund).where(Fund.id.in_(self.job.fund_ids))
            ).scalars().all()
        else:
            # Enrich all funds without primary contacts
            funds = self.session.execute(
                select(Fund).outerjoin(Contact).where(
                    Contact.id.is_(None)
                )
            ).scalars().all()
        
        for fund in funds:
            try:
                result = self._enrich_fund(fund)
                batch.results.append(result)
                batch.funds_completed += 1
                
                if result.status == "completed":
                    batch.total_contacts_found += result.total_contacts
                    batch.total_emails_found += result.emails_found
                else:
                    batch.funds_failed += 1
                    
            except Exception as e:
                logger.error(f"Enrichment failed for {fund.name}: {e}")
                batch.funds_failed += 1
                batch.results.append(EnrichmentResult(
                    fund_id=fund.id,
                    fund_name=fund.name,
                    status="failed",
                    error_message=str(e)
                ))
        
        # Complete batch
        batch.status = "completed" if batch.funds_failed == 0 else "partial"
        batch.completed_at = datetime.utcnow()
        
        logger.info(
            f"Batch {batch.batch_id} complete: "
            f"{batch.funds_completed} completed, {batch.funds_failed} failed, "
            f"{batch.total_contacts_found} contacts found"
        )
        
        return batch
    
    def _enrich_fund(self, fund: Fund) -> EnrichmentResult:
        """Enrich contacts for a single fund."""
        result = EnrichmentResult(
            fund_id=fund.id,
            fund_name=fund.name,
            started_at=datetime.utcnow(),
            status="processing"
        )
        
        all_contacts: List[RawContact] = []
        
        # Get company domain
        domain = None
        if fund.website_url:
            domain = fund.website_url.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Enrich from Apollo
        if EnrichmentSource.APOLLO in self._providers:
            try:
                apollo = self._providers[EnrichmentSource.APOLLO]
                apollo_contacts = list(apollo.find_contacts_by_company(
                    company_name=fund.name,
                    company_website=fund.website_url,
                    max_results=self.job.max_contacts_per_fund
                ))
                all_contacts.extend(apollo_contacts)
                logger.debug(f"Apollo found {len(apollo_contacts)} contacts for {fund.name}")
            except Exception as e:
                logger.warning(f"Apollo enrichment failed for {fund.name}: {e}")
        
        # Enrich from Hunter (if we have domain)
        if EnrichmentSource.HUNTER in self._providers and domain:
            try:
                hunter = self._providers[EnrichmentSource.HUNTER]
                hunter_contacts = list(hunter.find_contacts_by_domain(
                    domain=domain,
                    company_name=fund.name,
                    max_results=self.job.max_contacts_per_fund,
                    seniority="executive"  # Focus on senior contacts
                ))
                all_contacts.extend(hunter_contacts)
                logger.debug(f"Hunter found {len(hunter_contacts)} contacts for {fund.name}")
            except Exception as e:
                logger.warning(f"Hunter enrichment failed for {fund.name}: {e}")
        
        # Filter and deduplicate contacts
        filtered_contacts = self._filter_contacts(all_contacts)
        
        # Update result
        result.contacts_found = filtered_contacts
        result.total_contacts = len(filtered_contacts)
        result.emails_found = sum(1 for c in filtered_contacts if c.email)
        result.emails_verified = sum(1 for c in filtered_contacts if c.email_verified)
        
        # Save to database (unless dry run)
        if not self.job.dry_run:
            self._save_contacts(fund.id, filtered_contacts)
        
        result.status = "completed"
        result.completed_at = datetime.utcnow()
        
        return result
    
    def _filter_contacts(self, contacts: List[RawContact]) -> List[RawContact]:
        """Filter and deduplicate contacts."""
        seen_emails = set()
        seen_names = set()
        filtered = []
        
        # Sort by confidence score descending
        contacts.sort(key=lambda c: c.confidence_score, reverse=True)
        
        for contact in contacts:
            # Skip low confidence
            if contact.confidence_score < self.job.min_confidence:
                continue
            
            # Skip if email already seen
            if contact.email and contact.email.lower() in seen_emails:
                continue
            
            # Skip if name already seen
            name_key = contact.full_name.lower().strip()
            if name_key in seen_names:
                continue
            
            # Apply role filter
            if self.job.required_roles and contact.role not in self.job.required_roles:
                continue
            
            # Skip generic emails
            if contact.email_type == 'generic':
                continue
            
            seen_emails.add(contact.email.lower() if contact.email else '')
            seen_names.add(name_key)
            filtered.append(contact)
        
        return filtered[:self.job.max_contacts_per_fund]
    
    def _save_contacts(self, fund_id: str, contacts: List[RawContact]) -> int:
        """Save contacts to database."""
        saved = 0
        
        for raw in contacts:
            # Check if contact already exists
            existing = self.session.execute(
                select(Contact).where(
                    Contact.fund_id == fund_id,
                    Contact.full_name == raw.full_name
                )
            ).scalar_one_or_none()
            
            if existing and not self.job.overwrite_existing:
                # Update missing fields
                if not existing.email and raw.email:
                    existing.email = raw.email
                if not existing.linkedin_url and raw.linkedin_url:
                    existing.linkedin_url = raw.linkedin_url
                if not existing.title and raw.title:
                    existing.title = raw.title
                continue
            
            if existing and self.job.overwrite_existing:
                # Update existing
                existing.email = raw.email
                existing.linkedin_url = raw.linkedin_url
                existing.title = raw.title
            else:
                # Create new
                contact = Contact(
                    id=str(uuid4()),
                    fund_id=fund_id,
                    full_name=raw.full_name,
                    title=raw.title,
                    email=raw.email,
                    linkedin_url=raw.linkedin_url,
                    is_primary=(raw.role in [ContactRole.PARTNER, ContactRole.MANAGING_PARTNER, ContactRole.GENERAL_PARTNER])
                )
                self.session.add(contact)
            
            saved += 1
        
        self.session.commit()
        return saved
