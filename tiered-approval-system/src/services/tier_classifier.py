"""Tier classification service for approval cards."""
from typing import Dict, List
from src.models.approval_tiers import CardTier, ApprovalRule, CardSnapshot


class TierClassifier:
    """Classifies cards into priority tiers based on configurable rules."""
    
    DEFAULT_RULES: List[ApprovalRule] = [
        ApprovalRule(
            min_fit_score=95,
            max_fit_score=100,
            max_days_in_queue=3,
            tier=CardTier.P0
        ),
        ApprovalRule(
            min_fit_score=80,
            max_fit_score=94,
            tier=CardTier.P1
        ),
        ApprovalRule(
            min_fit_score=0,
            max_fit_score=79,
            tier=CardTier.P2
        ),
    ]
    
    def __init__(self, rules: List[ApprovalRule] = None):
        """Initialize classifier with optional custom rules.
        
        Args:
            rules: List of ApprovalRule objects. Uses DEFAULT_RULES if None.
        """
        self.rules = rules or self.DEFAULT_RULES.copy()
    
    def classify_card(self, card: CardSnapshot) -> CardTier:
        """Classify a single card into a tier.
        
        Classification priority:
        1. P0: High fit (95+) AND recent (<3 days)
        2. P1: Medium fit (80-94)
        3. P2: Low fit (<80) OR high fit but stale (3+ days)
        
        Args:
            card: CardSnapshot to classify
            
        Returns:
            CardTier: P0, P1, or P2
            
        Raises:
            ValueError: If card is None or has invalid data
        """
        if card is None:
            raise ValueError("Card cannot be None")
        
        fit_score = self._validate_fit_score(card.fit_score)
        days_in_queue = max(0, card.days_in_queue)
        
        # Check P0 criteria first (high fit + recent)
        if fit_score >= 95 and days_in_queue < 3:
            return CardTier.P0
        
        # Check P1 criteria (medium-high fit)
        if 80 <= fit_score <= 94:
            return CardTier.P1
        
        # High fit but stale goes to P1 for batch review
        if fit_score >= 95 and days_in_queue >= 3:
            return CardTier.P1
        
        # Everything else is P2
        return CardTier.P2
    
    def classify_cards(self, cards: List[CardSnapshot]) -> Dict[CardTier, List[CardSnapshot]]:
        """Classify multiple cards into tiers.
        
        Args:
            cards: List of CardSnapshot objects
            
        Returns:
            Dictionary mapping CardTier to list of cards
        """
        result: Dict[CardTier, List[CardSnapshot]] = {
            CardTier.P0: [],
            CardTier.P1: [],
            CardTier.P2: [],
        }
        
        for card in cards:
            tier = self.classify_card(card)
            result[tier].append(card)
        
        return result
    
    def _validate_fit_score(self, score: int) -> int:
        """Validate and clamp fit score to valid range.
        
        Args:
            score: Raw fit score value
            
        Returns:
            Clamped fit score (0-100)
        """
        try:
            score = int(score)
        except (TypeError, ValueError):
            score = 0
        return max(0, min(100, score))


def classify_card(card_data: Dict[str, any]) -> CardTier:
    """Convenience function to classify card from raw dictionary data.
    
    Args:
        card_data: Dictionary containing card fields
        
    Returns:
        CardTier classification
        
    Example:
        >>> card_data = {
        ...     "id": "card-123",
        ...     "name": "Startup XYZ",
        ...     "fit_score": 96,
        ...     "days_in_queue": 1,
        ...     "funding_stage": "Series A"
        ... }
        >>> classify_card(card_data)
        CardTier.P0
    """
    card = CardSnapshot(
        id=card_data.get("id", ""),
        name=card_data.get("name", ""),
        description=card_data.get("description", ""),
        fit_score=card_data.get("fit_score", 0),
        funding_stage=card_data.get("funding_stage", ""),
        portfolio_match=card_data.get("portfolio_match", False),
        days_in_queue=card_data.get("days_in_queue", 0),
        labels=card_data.get("labels", []),
        custom_fields=card_data.get("custom_fields", {})
    )
    
    classifier = TierClassifier()
    return classifier.classify_card(card)
