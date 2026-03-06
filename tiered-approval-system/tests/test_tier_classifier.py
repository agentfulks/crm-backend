"""Tests for the tier classifier."""
import pytest
from datetime import datetime

from src.models.approval_tiers import CardSnapshot, CardTier, ApprovalRule
from src.services.tier_classifier import TierClassifier, classify_card


class TestTierClassifier:
    """Test cases for tier classification logic."""
    
    @pytest.fixture
    def classifier(self):
        """Create a fresh classifier instance."""
        return TierClassifier()
    
    def test_p0_high_fit_recent(self, classifier):
        """Cards with 95+ fit and <3 days should be P0."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=96,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P0
    
    def test_p0_boundary_fit(self, classifier):
        """Cards with exactly 95 fit and <3 days should be P0."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=95,
            days_in_queue=2
        )
        assert classifier.classify_card(card) == CardTier.P0
    
    def test_p0_boundary_days(self, classifier):
        """Cards with 95+ fit and exactly 2 days should be P0."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=98,
            days_in_queue=2
        )
        assert classifier.classify_card(card) == CardTier.P0
    
    def test_p0_high_fit_stale_becomes_p1(self, classifier):
        """High fit cards that are stale (3+ days) become P1."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=98,
            days_in_queue=5
        )
        assert classifier.classify_card(card) == CardTier.P1
    
    def test_p1_medium_fit(self, classifier):
        """Cards with 80-94 fit should be P1."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=85,
            days_in_queue=10
        )
        assert classifier.classify_card(card) == CardTier.P1
    
    def test_p1_boundary_low(self, classifier):
        """Cards with exactly 80 fit should be P1."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=80,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P1
    
    def test_p1_boundary_high(self, classifier):
        """Cards with exactly 94 fit should be P1."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=94,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P1
    
    def test_p2_low_fit(self, classifier):
        """Cards with <80 fit should be P2."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=50,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P2
    
    def test_p2_boundary(self, classifier):
        """Cards with exactly 79 fit should be P2."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=79,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P2
    
    def test_p2_zero_fit(self, classifier):
        """Cards with 0 fit should be P2."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=0,
            days_in_queue=0
        )
        assert classifier.classify_card(card) == CardTier.P2
    
    def test_invalid_fit_score_negative(self, classifier):
        """Negative fit scores should be clamped to 0 (P2)."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=-10,
            days_in_queue=1
        )
        assert classifier.classify_card(card) == CardTier.P2
    
    def test_invalid_fit_score_over_100(self, classifier):
        """Fit scores over 100 should be clamped to 100."""
        card = CardSnapshot(
            id="test-1",
            name="Test Card",
            fit_score=150,
            days_in_queue=1
        )
        # 150 clamped to 100, which is 95+ fit but <3 days = P0
        assert classifier.classify_card(card) == CardTier.P0
    
    def test_none_card_raises_error(self, classifier):
        """Classifying None should raise ValueError."""
        with pytest.raises(ValueError, match="Card cannot be None"):
            classifier.classify_card(None)
    
    def test_classify_cards_batch(self, classifier):
        """Batch classification should return correct grouping."""
        cards = [
            CardSnapshot(id="p0-1", name="P0 Card", fit_score=97, days_in_queue=1),
            CardSnapshot(id="p1-1", name="P1 Card", fit_score=85, days_in_queue=1),
            CardSnapshot(id="p1-2", name="P1 Stale", fit_score=98, days_in_queue=5),
            CardSnapshot(id="p2-1", name="P2 Card", fit_score=60, days_in_queue=1),
        ]
        
        result = classifier.classify_cards(cards)
        
        assert len(result[CardTier.P0]) == 1
        assert len(result[CardTier.P1]) == 2
        assert len(result[CardTier.P2]) == 1
        
        assert result[CardTier.P0][0].id == "p0-1"
        assert result[CardTier.P2][0].id == "p2-1"


class TestClassifyCardFunction:
    """Test cases for the convenience classify_card function."""
    
    def test_classify_from_dict_p0(self):
        """Should correctly classify P0 from dictionary."""
        card_data = {
            "id": "card-123",
            "name": "Startup XYZ",
            "fit_score": 96,
            "days_in_queue": 1,
            "funding_stage": "Series A"
        }
        assert classify_card(card_data) == CardTier.P0
    
    def test_classify_from_dict_p1(self):
        """Should correctly classify P1 from dictionary."""
        card_data = {
            "id": "card-123",
            "name": "Startup XYZ",
            "fit_score": 85,
            "days_in_queue": 5,
            "funding_stage": "Seed"
        }
        assert classify_card(card_data) == CardTier.P1
    
    def test_classify_from_dict_p2(self):
        """Should correctly classify P2 from dictionary."""
        card_data = {
            "id": "card-123",
            "name": "Startup XYZ",
            "fit_score": 70,
            "days_in_queue": 10,
            "funding_stage": "Pre-seed"
        }
        assert classify_card(card_data) == CardTier.P2
    
    def test_classify_missing_fields_defaults(self):
        """Should handle missing fields with defaults."""
        card_data = {"id": "card-123", "name": "Minimal Card"}
        assert classify_card(card_data) == CardTier.P2


class TestCardSnapshot:
    """Test cases for CardSnapshot model."""
    
    def test_summary_property(self):
        """Summary should format correctly."""
        card = CardSnapshot(
            id="card-123",
            name="Test Startup",
            fit_score=85,
            days_in_queue=5
        )
        expected = "[card-123] Test Startup (Fit: 85, Days: 5)"
        assert card.summary == expected
