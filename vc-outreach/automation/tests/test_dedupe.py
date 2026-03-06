"""Tests for deduplication engine."""
from __future__ import annotations

import pytest

from src.dedupe import DeduplicationEngine


class TestDeduplicationEngine:
    """Test deduplication logic."""
    
    @pytest.fixture
    def engine(self):
        return DeduplicationEngine(threshold=0.85)
    
    def test_normalize_name_basic(self, engine):
        """Test basic name normalization."""
        assert engine.normalize_name("Accel Partners") == "accel"
        assert engine.normalize_name("Sequoia Capital LLC") == "sequoia"
        assert engine.normalize_name("  Greylock  Partners  ") == "greylock"
    
    def test_normalize_name_legal_suffixes(self, engine):
        """Test removal of legal suffixes."""
        assert engine.normalize_name("Firm LP") == "firm"
        assert engine.normalize_name("Firm LLC.") == "firm"
        assert engine.normalize_name("Firm Inc.") == "firm"
        assert engine.normalize_name("Firm Ltd") == "firm"
        assert engine.normalize_name("Firm Limited") == "firm"
    
    def test_normalize_name_special_chars(self, engine):
        """Test special character removal."""
        assert engine.normalize_name("A&B Capital") == "ab capital"
        assert engine.normalize_name("Firm (Corp)") == "firm corp"
    
    def test_name_similarity_exact_match(self, engine):
        """Test exact match detection."""
        assert engine.name_similarity("Accel", "Accel") == 1.0
    
    def test_name_similarity_subset(self, engine):
        """Test subset matching."""
        # One name contains the other
        assert engine.name_similarity("Accel Partners", "Accel") == 0.95
        assert engine.name_similarity("Accel", "Accel Partners") == 0.95
    
    def test_name_similarity_fuzzy(self, engine):
        """Test fuzzy matching."""
        # Similar names
        score = engine.name_similarity("Greylock", "Greylock Partners")
        assert score > 0.8
        
        # Different names
        score = engine.name_similarity("Accel", "Sequoia")
        assert score < 0.5
    
    def test_website_match_exact(self, engine):
        """Test exact website matching."""
        assert engine.website_match("https://accel.com", "https://accel.com") == 1.0
    
    def test_website_match_normalized(self, engine):
        """Test normalized website matching."""
        assert engine.website_match("https://www.accel.com/", "http://accel.com") == 1.0
    
    def test_website_match_domain(self, engine):
        """Test domain matching."""
        assert engine.website_match("https://accel.com/about", "https://accel.com/team") == 0.9
    
    def test_website_match_none(self, engine):
        """Test non-matching websites."""
        assert engine.website_match("https://accel.com", "https://sequoia.com") == 0.0
    
    def test_website_match_empty(self, engine):
        """Test empty website handling."""
        assert engine.website_match(None, "https://accel.com") == 0.0
        assert engine.website_match("", "") == 0.0
