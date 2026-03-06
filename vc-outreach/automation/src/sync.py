"""Sync orchestrator for VC fund ingestion."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterator, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from .db_ops import insert_funds
from .dedupe import deduplicate_funds, DeduplicationEngine
from .fetchers import get_fetcher
from .models import ProcessedFund, RawFund, SyncConfig, SyncRun, DataSource

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """Orchestrates the end-to-end sync process."""
    
    def __init__(self, session: Session):
        self.session = session
        self._sync_run: Optional[SyncRun] = None
    
    def run_sync(
        self,
        config: SyncConfig,
        limit: Optional[int] = None,
        **filters
    ) -> SyncRun:
        """
        Run a complete sync operation.
        
        Args:
            config: Sync configuration
            limit: Maximum number of funds to fetch
            **filters: Additional source-specific filters
            
        Returns:
            SyncRun with results
        """
        # Initialize sync run
        self._sync_run = SyncRun(
            id=str(uuid4()),
            started_at=datetime.utcnow(),
            data_source=config.data_source,
            status="running"
        )
        
        logger.info(f"Starting sync for {config.data_source.value}")
        
        try:
            # Step 1: Fetch funds from source
            logger.info("Step 1: Fetching funds from source...")
            raw_funds = list(self._fetch(config, limit, **filters))
            self._sync_run.records_fetched = len(raw_funds)
            logger.info(f"Fetched {len(raw_funds)} funds")
            
            # Step 2: Deduplicate
            logger.info("Step 2: Deduplicating funds...")
            new_funds, update_funds, skip_funds = self._deduplicate(
                raw_funds, 
                config.dedupe_threshold
            )
            logger.info(
                f"Deduplication complete: {len(new_funds)} new, "
                f"{len(update_funds)} updates, {len(skip_funds)} skipped"
            )
            
            # Step 3: Process all funds
            all_funds: List[ProcessedFund] = []
            
            for fund in new_funds:
                processed = ProcessedFund(**fund.model_dump(), action="create")
                all_funds.append(processed)
            
            for fund in update_funds:
                processed = ProcessedFund(**fund.model_dump(), action="update")
                all_funds.append(processed)
            
            for fund in skip_funds:
                processed = ProcessedFund(**fund.model_dump(), action="skip")
                all_funds.append(processed)
            
            # Step 4: Insert/update in database
            logger.info("Step 3: Writing to database...")
            created, updated, skipped = insert_funds(
                self.session,
                all_funds,
                self._sync_run.id
            )
            
            self._sync_run.records_new = created
            self._sync_run.records_updated = updated
            self._sync_run.records_skipped = skipped
            
            # Mark as complete
            self._sync_run.status = "completed"
            self._sync_run.ended_at = datetime.utcnow()
            
            duration = (
                self._sync_run.ended_at - self._sync_run.started_at
            ).total_seconds()
            
            logger.info(
                f"Sync completed in {duration:.1f}s: "
                f"{created} created, {updated} updated, {skipped} skipped"
            )
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self._sync_run.status = "failed"
            self._sync_run.ended_at = datetime.utcnow()
            self._sync_run.errors.append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
        
        return self._sync_run
    
    def _fetch(
        self,
        config: SyncConfig,
        limit: Optional[int],
        **filters
    ) -> Iterator[RawFund]:
        """Fetch funds from configured source."""
        fetcher = get_fetcher(config.data_source.value, config)
        
        # Apply config filters
        fetch_filters = {
            'sectors': config.target_sectors,
            'stages': config.stage_focus,
            **filters
        }
        
        yield from fetcher.fetch_funds(limit=limit, **fetch_filters)
    
    def _deduplicate(
        self,
        funds: List[RawFund],
        threshold: float
    ) -> tuple:
        """Deduplicate funds against database."""
        return deduplicate_funds(funds, self.session, threshold)
    
    @property
    def sync_run(self) -> Optional[SyncRun]:
        """Get current sync run."""
        return self._sync_run


def run_daily_sync(
    session: Session,
    configs: List[SyncConfig],
    dry_run: bool = False
) -> List[SyncRun]:
    """
    Run daily sync for all enabled configs.
    
    Args:
        session: Database session
        configs: List of sync configurations
        dry_run: If True, don't write to database
        
    Returns:
        List of SyncRun results
    """
    results = []
    
    for config in configs:
        if not config.enabled:
            logger.info(f"Skipping disabled config: {config.data_source.value}")
            continue
        
        try:
            orchestrator = SyncOrchestrator(session)
            
            if dry_run:
                logger.info(f"DRY RUN: {config.data_source.value}")
                # Just fetch and dedupe, don't write
                fetcher = get_fetcher(config.data_source.value, config)
                raw_funds = list(fetcher.fetch_funds(limit=10))
                logger.info(f"Would fetch {len(raw_funds)} funds")
                # Create mock result
                run = SyncRun(
                    id=str(uuid4()),
                    started_at=datetime.utcnow(),
                    ended_at=datetime.utcnow(),
                    data_source=config.data_source,
                    status="completed",
                    records_fetched=len(raw_funds)
                )
            else:
                run = orchestrator.run_sync(config)
            
            results.append(run)
            
        except Exception as e:
            logger.error(f"Sync failed for {config.data_source.value}: {e}")
            results.append(SyncRun(
                id=str(uuid4()),
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow(),
                data_source=config.data_source,
                status="failed",
                errors=[{"error": str(e)}]
            ))
    
    return results
