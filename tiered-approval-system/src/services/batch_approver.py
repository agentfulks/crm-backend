"""Batch approval service for processing card approvals."""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.models.approval_tiers import (
    CardSnapshot, CardTier, BatchResult, ArchiveResult
)
from src.services.tier_classifier import TierClassifier


class BatchApprover:
    """Service for batch approval operations on card queues."""
    
    def __init__(self, state_file: str = "trello-state.json"):
        """Initialize batch approver with state file.
        
        Args:
            state_file: Path to JSON file containing card data
        """
        self.state_file = Path(state_file)
        self.classifier = TierClassifier()
        self._cards: List[CardSnapshot] = []
        self._load_cards()
    
    def _load_cards(self) -> None:
        """Load cards from state file."""
        if not self.state_file.exists():
            self._cards = []
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            # Handle both list and dict formats
            if isinstance(data, dict) and "cards" in data:
                card_list = data["cards"]
            elif isinstance(data, list):
                card_list = data
            else:
                card_list = []
            
            self._cards = [self._dict_to_card(c) for c in card_list]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state file: {e}")
            self._cards = []
    
    def _dict_to_card(self, data: Dict[str, Any]) -> CardSnapshot:
        """Convert dictionary to CardSnapshot."""
        created_at = None
        last_activity = None
        
        if "created_at" in data and data["created_at"]:
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        if "last_activity" in data and data["last_activity"]:
            try:
                last_activity = datetime.fromisoformat(data["last_activity"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return CardSnapshot(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            fit_score=data.get("fit_score", 0),
            funding_stage=data.get("funding_stage", ""),
            portfolio_match=data.get("portfolio_match", False),
            days_in_queue=data.get("days_in_queue", 0),
            created_at=created_at,
            last_activity=last_activity,
            labels=data.get("labels", []),
            custom_fields=data.get("custom_fields", {})
        )
    
    def get_counts_by_tier(self) -> Dict[CardTier, int]:
        """Get card counts grouped by tier.
        
        Returns:
            Dictionary mapping CardTier to count
        """
        classified = self.classifier.classify_cards(self._cards)
        return {tier: len(cards) for tier, cards in classified.items()}
    
    def get_batch_for_review(
        self, 
        tier: CardTier, 
        limit: int = 10
    ) -> List[CardSnapshot]:
        """Get a batch of cards for review by tier.
        
        Args:
            tier: Target tier to filter by
            limit: Maximum number of cards to return
            
        Returns:
            List of CardSnapshot objects matching the tier
        """
        classified = self.classifier.classify_cards(self._cards)
        cards = classified.get(tier, [])
        
        # Sort by days in queue (oldest first) then by fit score (highest first)
        sorted_cards = sorted(
            cards, 
            key=lambda c: (-c.days_in_queue, -c.fit_score)
        )
        
        return sorted_cards[:limit]
    
    def get_top_p0_cards(self, limit: int = 10) -> List[CardSnapshot]:
        """Get top P0 cards requiring urgent review.
        
        Args:
            limit: Maximum number of cards to return
            
        Returns:
            List of P0 CardSnapshot objects
        """
        return self.get_batch_for_review(CardTier.P0, limit)
    
    def approve_batch(self, card_ids: List[str]) -> BatchResult:
        """Approve a batch of cards by ID.
        
        Args:
            card_ids: List of card IDs to approve
            
        Returns:
            BatchResult with approval outcomes
        """
        result = BatchResult()
        card_id_set = set(card_ids)
        
        for card in self._cards:
            if card.id in card_id_set:
                # In a real implementation, this would call Trello API
                # For now, we simulate approval by removing from queue
                result.approved_ids.append(card.id)
        
        # Remove approved cards from internal list
        self._cards = [c for c in self._cards if c.id not in result.approved_ids]
        
        return result
    
    def approve_batch_by_tier(self, tier: CardTier, limit: int = 20) -> BatchResult:
        """Approve cards matching a specific tier.
        
        Args:
            tier: Tier to approve
            limit: Maximum number of cards to approve
            
        Returns:
            BatchResult with approval outcomes
        """
        cards = self.get_batch_for_review(tier, limit)
        card_ids = [c.id for c in cards]
        return self.approve_batch(card_ids)
    
    def archive_low_tier_cards(self, min_days: int = 14) -> ArchiveResult:
        """Archive P2 cards that have been in queue too long.
        
        Args:
            min_days: Minimum days in queue to qualify for archiving
            
        Returns:
            ArchiveResult with archive outcomes
        """
        result = ArchiveResult(reason=f"P2 cards older than {min_days} days")
        
        p2_cards = self.get_batch_for_review(CardTier.P2, limit=1000)
        
        for card in p2_cards:
            if card.days_in_queue >= min_days:
                # In a real implementation, this would call Trello API
                result.archived_ids.append(card.id)
        
        # Remove archived cards from internal list
        self._cards = [c for c in self._cards if c.id not in result.archived_ids]
        
        return result
    
    def reload(self) -> None:
        """Reload cards from state file."""
        self._load_cards()
    
    @property
    def total_cards(self) -> int:
        """Total number of cards in queue."""
        return len(self._cards)
