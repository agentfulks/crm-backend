"""Database operations for source automation."""
from __future__ import annotations

import logging
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import FundStatus, Priority
from app.models.fund import Fund

from .models import ProcessedFund, RawFund, SyncRun

logger = logging.getLogger(__name__)


def create_fund_from_raw(raw: RawFund) -> Fund:
    """Create Fund ORM model from RawFund."""
    return Fund(
        id=str(uuid4()),
        name=raw.name,
        firm_type=raw.firm_type,
        hq_city=raw.hq_city,
        hq_region=raw.hq_region,
        hq_country=raw.hq_country,
        stage_focus=raw.stage_focus,
        check_size_min=raw.check_size_min,
        check_size_max=raw.check_size_max,
        check_size_currency=raw.check_size_currency,
        target_countries=raw.target_countries,
        website_url=raw.website_url,
        linkedin_url=raw.linkedin_url,
        twitter_url=raw.twitter_url,
        funding_requirements=raw.funding_requirements,
        overview=raw.overview,
        priority=Priority.C,  # Default to lowest priority until scored
        status=FundStatus.NEW,
        data_source=raw.data_source.value,
        source_row_id=raw.source_id,
        tags={
            **raw.tags,
            'sector_focus': raw.sector_focus,
        }
    )


def update_fund_from_raw(existing: Fund, raw: RawFund) -> Fund:
    """Update existing Fund with data from RawFund."""
    # Only update fields that are not already set or have better data
    if not existing.website_url and raw.website_url:
        existing.website_url = raw.website_url
    if not existing.linkedin_url and raw.linkedin_url:
        existing.linkedin_url = raw.linkedin_url
    if not existing.twitter_url and raw.twitter_url:
        existing.twitter_url = raw.twitter_url
    if not existing.overview and raw.overview:
        existing.overview = raw.overview
    if not existing.funding_requirements and raw.funding_requirements:
        existing.funding_requirements = raw.funding_requirements
    if not existing.check_size_min and raw.check_size_min:
        existing.check_size_min = raw.check_size_min
    if not existing.check_size_max and raw.check_size_max:
        existing.check_size_max = raw.check_size_max
    
    # Merge tags
    existing.tags = {**(existing.tags or {}), **raw.tags}
    
    # Merge stage focus
    if raw.stage_focus:
        existing.stage_focus = list(set((existing.stage_focus or []) + raw.stage_focus))
    
    return existing


def insert_funds(
    session: Session,
    funds: List[ProcessedFund],
    sync_run_id: Optional[str] = None
) -> tuple:
    """
    Insert or update funds in database.
    
    Returns:
        Tuple of (created_count, updated_count, skipped_count)
    """
    created = 0
    updated = 0
    skipped = 0
    
    for fund in funds:
        try:
            if fund.action == "create":
                new_fund = create_fund_from_raw(fund)
                session.add(new_fund)
                created += 1
                logger.debug(f"Created fund: {fund.name}")
                
            elif fund.action == "update" and fund.matched_fund_id:
                existing = session.get(Fund, fund.matched_fund_id)
                if existing:
                    update_fund_from_raw(existing, fund)
                    updated += 1
                    logger.debug(f"Updated fund: {fund.name}")
                else:
                    # Fund was deleted or ID changed, create new
                    new_fund = create_fund_from_raw(fund)
                    session.add(new_fund)
                    created += 1
                    
            elif fund.action == "skip":
                skipped += 1
                logger.debug(f"Skipped fund (duplicate): {fund.name}")
                
        except Exception as e:
            logger.error(f"Error processing fund {fund.name}: {e}")
            skipped += 1
    
    session.commit()
    return created, updated, skipped


def get_fund_by_source_id(
    session: Session,
    data_source: str,
    source_id: str
) -> Optional[Fund]:
    """Get fund by its original source ID."""
    query = select(Fund).where(
        Fund.data_source == data_source,
        Fund.source_row_id == source_id
    )
    result = session.execute(query).scalar_one_or_none()
    return result


def get_sync_stats(
    session: Session,
    data_source: Optional[str] = None
) -> dict:
    """Get statistics about synced funds."""
    from sqlalchemy import func
    
    query = select(
        func.count(Fund.id).label('total'),
        func.count(Fund.id).filter(Fund.data_source == 'crunchbase').label('crunchbase'),
        func.count(Fund.id).filter(Fund.data_source == 'apollo').label('apollo'),
        func.count(Fund.id).filter(Fund.created_at >= func.now() - func.interval('1 day')).label('last_24h'),
    )
    
    if data_source:
        query = query.where(Fund.data_source == data_source)
    
    result = session.execute(query).one()
    
    return {
        'total_funds': result.total,
        'crunchbase_count': result.crunchbase,
        'apollo_count': result.apollo,
        'last_24h': result.last_24h,
    }
