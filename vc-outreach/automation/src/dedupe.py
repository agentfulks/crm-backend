"""Deduplication engine for VC fund records."""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fund import Fund

from .models import DeduplicationResult, RawFund


class DeduplicationEngine:
    """Fuzzy matching engine for fund deduplication."""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
    
    def normalize_name(self, name: str) -> str:
        """Normalize fund name for comparison."""
        if not name:
            return ""
        # Lowercase, remove legal suffixes, normalize whitespace
        normalized = name.lower()
        # Remove common suffixes
        suffixes = [
            r'\s+lp\.?$', r'\s+llc\.?$', r'\s+inc\.?$', 
            r'\s+ltd\.?$', r'\s+limited$', r'\s+partners\.?$',
            r'\s+ventures\.?$', r'\s+capital\.?$', r'\s+fund\.?$',
            r'\s+investments\.?$', r'\s+group\.?$'
        ]
        for suffix in suffixes:
            normalized = re.sub(suffix, '', normalized)
        # Remove special characters, keep alphanumeric and spaces
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        return normalized.strip()
    
    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two fund names."""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match after normalization
        if norm1 == norm2:
            return 1.0
        
        # One contains the other
        if norm1 in norm2 or norm2 in norm1:
            return 0.95
        
        # Fuzzy match
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def website_match(self, url1: Optional[str], url2: Optional[str]) -> float:
        """Check if websites match."""
        if not url1 or not url2:
            return 0.0
        
        # Normalize URLs
        def normalize(url: str) -> str:
            url = url.lower().strip()
            url = re.sub(r'^https?://', '', url)
            url = re.sub(r'^www\.', '', url)
            url = url.rstrip('/')
            return url
        
        norm1 = normalize(url1)
        norm2 = normalize(url2)
        
        if norm1 == norm2:
            return 1.0
        
        # Check domain match
        domain1 = norm1.split('/')[0]
        domain2 = norm2.split('/')[0]
        if domain1 == domain2:
            return 0.9
        
        return 0.0
    
    def calculate_match_score(
        self, 
        new_fund: RawFund, 
        existing_fund: Fund
    ) -> Tuple[float, List[str]]:
        """Calculate overall match score and return matching fields."""
        scores = []
        matching_fields = []
        
        # Name similarity (highest weight)
        name_sim = self.name_similarity(new_fund.name, existing_fund.name)
        scores.append((name_sim, 0.5))  # 50% weight
        if name_sim > 0.8:
            matching_fields.append("name")
        
        # Website match (high weight)
        web_sim = self.website_match(new_fund.website_url, existing_fund.website_url)
        scores.append((web_sim, 0.3))  # 30% weight
        if web_sim > 0.8:
            matching_fields.append("website")
        
        # LinkedIn match
        linkedin_sim = self.website_match(new_fund.linkedin_url, existing_fund.linkedin_url)
        scores.append((linkedin_sim, 0.2))  # 20% weight
        if linkedin_sim > 0.8:
            matching_fields.append("linkedin")
        
        # Calculate weighted score
        total_weight = sum(w for _, w in scores)
        if total_weight == 0:
            return 0.0, []
        
        weighted_score = sum(s * w for s, w in scores) / total_weight
        return weighted_score, matching_fields
    
    def find_matches(
        self, 
        new_fund: RawFund, 
        session: Session,
        limit: int = 10
    ) -> List[Tuple[Fund, float, List[str]]]:
        """Find potential matching funds in database."""
        # First, try exact-ish name match
        normalized = self.normalize_name(new_fund.name)
        
        # Get candidates by partial name match or same website
        query = select(Fund).where(
            (Fund.name.ilike(f"%{new_fund.name[:10]}%")) |  # Similar start
            (Fund.website_url == new_fund.website_url) |  # Same website
            (Fund.linkedin_url == new_fund.linkedin_url)  # Same LinkedIn
        ).limit(limit * 3)  # Get more candidates for filtering
        
        candidates = session.execute(query).scalars().all()
        
        # Score each candidate
        matches = []
        for candidate in candidates:
            score, fields = self.calculate_match_score(new_fund, candidate)
            if score >= self.threshold:
                matches.append((candidate, score, fields))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def deduplicate(
        self, 
        new_fund: RawFund, 
        session: Session
    ) -> DeduplicationResult:
        """Check if fund is a duplicate and return deduplication result."""
        matches = self.find_matches(new_fund, session)
        
        if not matches:
            return DeduplicationResult(
                is_duplicate=False,
                confidence=0.0,
                reason="No matching fund found"
            )
        
        best_match, score, fields = matches[0]
        
        # High confidence match - likely duplicate
        if score >= 0.95:
            return DeduplicationResult(
                is_duplicate=True,
                matched_fund_id=best_match.id,
                confidence=score,
                reason=f"High confidence name/website match",
                matching_fields=fields
            )
        
        # Medium confidence - potential duplicate
        if score >= self.threshold:
            return DeduplicationResult(
                is_duplicate=True,
                matched_fund_id=best_match.id,
                confidence=score,
                reason=f"Medium confidence match on {', '.join(fields)}",
                matching_fields=fields
            )
        
        return DeduplicationResult(
            is_duplicate=False,
            confidence=score,
            reason="Match confidence below threshold"
        )


def deduplicate_funds(
    funds: List[RawFund], 
    session: Session,
    threshold: float = 0.85
) -> Tuple[List[RawFund], List[RawFund], List[RawFund]]:
    """
    Deduplicate a batch of funds.
    
    Returns:
        Tuple of (new_funds, update_funds, skip_funds)
    """
    engine = DeduplicationEngine(threshold)
    
    new_funds = []
    update_funds = []
    skip_funds = []
    
    for fund in funds:
        result = engine.deduplicate(fund, session)
        
        if result.is_duplicate and result.confidence >= 0.95:
            # High confidence - mark for update
            fund.matched_fund_id = result.matched_fund_id
            fund.match_confidence = result.confidence
            fund.match_reason = result.reason
            fund.action = "update"
            update_funds.append(fund)
        elif result.is_duplicate and result.confidence >= threshold:
            # Medium confidence - skip for manual review
            fund.matched_fund_id = result.matched_fund_id
            fund.match_confidence = result.confidence
            fund.match_reason = result.reason
            fund.action = "skip"
            skip_funds.append(fund)
        else:
            # No match - new fund
            fund.action = "create"
            new_funds.append(fund)
    
    return new_funds, update_funds, skip_funds
