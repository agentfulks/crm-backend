"""Core business logic for Daily Intake Automation."""

import structlog
from typing import List

from src.config import Settings, get_settings
from src.database import CRMRepository
from src.models import (
    CardCreationResult,
    DailyIntakeResult,
    InvestorEntry,
    TrelloCard,
)
from src.trello_client import TrelloClient

logger = structlog.get_logger()


# Default checklist items for investor packet cards
DEFAULT_CHECKLIST_ITEMS = [
    "Review investor profile and background",
    "Prepare pitch deck customization",
    "Draft personalized outreach message",
    "Schedule follow-up in calendar",
    "Mark complete when sent",
]

# Checklist name
CHECKLIST_NAME = "Packet Preparation"


class DailyIntakeService:
    """Service orchestrating the daily intake automation process."""
    
    def __init__(
        self,
        settings: Settings = None,
        crm_repository: CRMRepository = None,
        trello_client: TrelloClient = None,
    ):
        """
        Initialize the service with dependencies.
        
        Args:
            settings: Application settings
            crm_repository: Repository for CRM database access
            trello_client: Client for Trello API access
        """
        self.settings = settings or get_settings()
        self.crm = crm_repository or CRMRepository(self.settings.database_url)
        self.trello = trello_client or TrelloClient(self.settings)
        self.logger = logger.bind(service="DailyIntakeService")
    
    def process_daily_intake(
        self,
        limit: int = 5,
        dry_run: bool = False,
    ) -> DailyIntakeResult:
        """
        Main entry point for the daily intake process.
        
        Fetches top-scored investors from CRM and creates Trello cards for each.
        
        Args:
            limit: Maximum number of investor entries to process
            dry_run: If True, don't actually create cards
            
        Returns:
            DailyIntakeResult with complete processing details
        """
        self.logger.info(
            "Starting daily intake process",
            limit=limit,
            dry_run=dry_run,
        )
        
        # Fetch investor entries from CRM
        try:
            investors = self.crm.get_top_scored_investors(limit=limit)
            self.logger.info("Fetched investor entries", count=len(investors))
        except Exception as e:
            self.logger.error("Failed to fetch investor entries", error=str(e))
            return DailyIntakeResult(
                total_entries_found=0,
                cards_created=0,
                cards_skipped=0,
                cards_failed=0,
                dry_run=dry_run,
                details=[],
            )
        
        # Process each investor entry
        results: List[CardCreationResult] = []
        for investor in investors:
            result = self._process_single_investor(investor, dry_run)
            results.append(result)
        
        # Aggregate results
        created = sum(1 for r in results if r.success and not r.dry_run)
        skipped = sum(1 for r in results if not r.success and r.error_message and "duplicate" in r.error_message.lower())
        failed = sum(1 for r in results if not r.success and (not r.error_message or "duplicate" not in r.error_message.lower()))
        
        summary = DailyIntakeResult(
            total_entries_found=len(investors),
            cards_created=created,
            cards_skipped=skipped,
            cards_failed=failed,
            dry_run=dry_run,
            details=results,
        )
        
        self.logger.info(
            "Daily intake process completed",
            total=summary.total_entries_found,
            created=summary.cards_created,
            skipped=summary.cards_skipped,
            failed=summary.cards_failed,
            success_rate=f"{summary.success_rate:.1f}%",
        )
        
        return summary
    
    def _process_single_investor(
        self,
        investor: InvestorEntry,
        dry_run: bool = False,
    ) -> CardCreationResult:
        """
        Process a single investor entry.
        
        Args:
            investor: The investor entry to process
            dry_run: If True, don't actually create cards
            
        Returns:
            CardCreationResult with processing details
        """
        self.logger.debug(
            "Processing investor",
            investor_id=investor.id,
            name=investor.investor_name,
            score=investor.outreach_score,
        )
        
        # Check for duplicates
        card_title = investor.card_title
        try:
            exists = self.trello.check_card_exists_by_prefix(
                name_prefix=card_title,
                board_id=self.settings.trello_board_id,
            )
            if exists:
                self.logger.info(
                    "Skipping duplicate investor",
                    name=investor.investor_name,
                    reason="Card already exists",
                )
                return CardCreationResult(
                    success=False,
                    investor_entry=investor,
                    error_message=f"Duplicate: Card '{card_title}' already exists",
                    dry_run=dry_run,
                )
        except Exception as e:
            self.logger.warning(
                "Duplicate check failed, proceeding with caution",
                error=str(e),
            )
        
        # Build the Trello card
        card = TrelloCard(
            name=card_title,
            desc=investor.card_description,
            idList=self.settings.trello_list_id,
            idLabels=self.settings.label_ids,
            pos="top",
        )
        
        # Create the card
        try:
            card_data = self.trello.create_card(card, dry_run=dry_run)
            
            # Add checklist if card was created successfully
            if card_data.get("id") and not dry_run:
                try:
                    self.trello.add_checklist_to_card(
                        card_id=card_data["id"],
                        name=CHECKLIST_NAME,
                        items=DEFAULT_CHECKLIST_ITEMS,
                        dry_run=dry_run,
                    )
                except Exception as e:
                    self.logger.warning(
                        "Failed to add checklist, but card was created",
                        card_id=card_data.get("id"),
                        error=str(e),
                    )
            
            self.logger.info(
                "Successfully created card for investor",
                investor_name=investor.investor_name,
                card_id=card_data.get("id"),
                card_url=card_data.get("shortUrl"),
            )
            
            return CardCreationResult(
                success=True,
                investor_entry=investor,
                trello_card_id=card_data.get("id"),
                trello_card_url=card_data.get("shortUrl"),
                dry_run=dry_run,
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to create card for investor",
                investor_name=investor.investor_name,
                error=str(e),
            )
            return CardCreationResult(
                success=False,
                investor_entry=investor,
                error_message=str(e),
                dry_run=dry_run,
            )
