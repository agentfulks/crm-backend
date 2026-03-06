"""Integration tests for Daily Intake Automation."""

import pytest
from datetime import datetime

from src.models import InvestorEntry, TrelloCard


class TestInvestorEntry:
    """Tests for InvestorEntry model."""
    
    def test_card_title_generation(self):
        """Test that card title is properly formatted."""
        investor = InvestorEntry(
            id="inv_001",
            investor_name="John Doe",
            firm_name="Acme Ventures",
            email_address="john@example.com",
            outreach_score=85,
            created_at=datetime.now(),
        )
        
        assert investor.card_title == "Investor Packet: John Doe"
    
    def test_card_description_generation(self):
        """Test that card description is properly formatted."""
        investor = InvestorEntry(
            id="inv_001",
            investor_name="John Doe",
            firm_name="Acme Ventures",
            job_title="Partner",
            email_address="john@acme.vc",
            phone_number="+1-555-0123",
            linkedin_profile_url="https://linkedin.com/in/johndoe",
            investment_thesis_summary="Focuses on enterprise SaaS",
            outreach_score=95,
            created_at=datetime(2024, 3, 1, 10, 0, 0),
        )
        
        desc = investor.card_description
        
        assert "John Doe" in desc
        assert "Acme Ventures" in desc
        assert "Partner" in desc
        assert "95/100" in desc
        assert "john@acme.vc" in desc
        assert "+1-555-0123" in desc
        assert "https://linkedin.com/in/johndoe" in desc
        assert "enterprise SaaS" in desc
        assert "inv_001" in desc
    
    def test_card_description_without_optional_fields(self):
        """Test description generation when optional fields are missing."""
        investor = InvestorEntry(
            id="inv_002",
            investor_name="Jane Smith",
            firm_name="Beta Capital",
            email_address="jane@beta.capital",
            outreach_score=75,
            created_at=datetime.now(),
        )
        
        desc = investor.card_description
        
        assert "Jane Smith" in desc
        assert "Beta Capital" in desc
        assert "75/100" in desc
        # Optional fields should not appear or show placeholder
        assert "Phone:" not in desc or "LinkedIn:" not in desc
    
    def test_validation_empty_name(self):
        """Test that empty investor name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            InvestorEntry(
                id="inv_003",
                investor_name="",
                firm_name="Test Firm",
                email_address="test@example.com",
                outreach_score=80,
                created_at=datetime.now(),
            )
    
    def test_validation_score_range(self):
        """Test that score must be within 0-100 range."""
        with pytest.raises(ValueError):
            InvestorEntry(
                id="inv_004",
                investor_name="Test",
                firm_name="Firm",
                email_address="test@example.com",
                outreach_score=150,  # Invalid: > 100
                created_at=datetime.now(),
            )
        
        with pytest.raises(ValueError):
            InvestorEntry(
                id="inv_005",
                investor_name="Test",
                firm_name="Firm",
                email_address="test@example.com",
                outreach_score=-10,  # Invalid: < 0
                created_at=datetime.now(),
            )


class TestTrelloCard:
    """Tests for TrelloCard model."""
    
    def test_card_creation(self):
        """Test that TrelloCard can be created with required fields."""
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_123",
        )
        
        assert card.name == "Test Card"
        assert card.desc == "Test description"
        assert card.idList == "list_123"
        assert card.pos == "top"  # Default value
        assert card.idLabels == []  # Default value
    
    def test_card_with_labels(self):
        """Test card creation with labels."""
        card = TrelloCard(
            name="Test Card",
            desc="Test description",
            idList="list_123",
            idLabels=["label_1", "label_2", "label_3"],
        )
        
        assert len(card.idLabels) == 3
        assert "label_1" in card.idLabels


class TestCardTemplateCompliance:
    """Tests to verify compliance with card_template.json specification."""
    
    def test_card_name_format(self):
        """Verify card name follows template format: 'Investor Packet: {name}'."""
        investor = InvestorEntry(
            id="test_001",
            investor_name="Sarah Johnson",
            firm_name="Gamma Partners",
            email_address="sarah@gamma.vc",
            outreach_score=90,
            created_at=datetime.now(),
        )
        
        assert investor.card_title.startswith("Investor Packet: ")
        assert "Sarah Johnson" in investor.card_title
    
    def test_card_description_sections(self):
        """Verify description contains required sections."""
        investor = InvestorEntry(
            id="test_002",
            investor_name="Mike Brown",
            firm_name="Delta Fund",
            job_title="Principal",
            email_address="mike@delta.fund",
            investment_thesis_summary="B2B marketplace investments",
            outreach_score=85,
            created_at=datetime.now(),
        )
        
        desc = investor.card_description
        
        # Check required sections exist
        assert "## Investor Information" in desc
        assert "## Contact Details" in desc
        assert "## Investment Focus" in desc
        assert "## Source" in desc
        
        # Check required fields
        assert "Mike Brown" in desc
        assert "Delta Fund" in desc
        assert "Principal" in desc
        assert "85/100" in desc
        assert "mike@delta.fund" in desc
        assert "test_002" in desc
    
    def test_template_label_mapping(self):
        """Verify label IDs are properly mapped from settings."""
        # This test verifies that the expected label structure is documented
        # The actual label IDs come from environment variables
        expected_label_refs = [
            "LABEL_TYPE_OUTREACH",
            "LABEL_PRIORITY_P1",
            "LABEL_WORKSTREAM_INVESTOR",
        ]
        
        # Verify the config expects these labels
        from src.config import Settings
        
        # Check that Settings model has these fields
        assert hasattr(Settings, 'label_type_outreach')
        assert hasattr(Settings, 'label_priority_p1')
        assert hasattr(Settings, 'label_workstream_investor')
