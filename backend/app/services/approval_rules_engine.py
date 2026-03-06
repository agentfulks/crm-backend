"""Tiered approval rules engine for automating card classification.

This module implements a rules-based engine for classifying cards (packets/bdr companies)
into three tiers based on confidence scoring:
- Tier 1 (Auto-approve): 95%+ confidence
- Tier 2 (Quick review): 85-94% confidence
- Tier 3 (Deep review): <85% confidence
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union

from app.models.enums import FundStatus, PacketStatus


class CardType(str, Enum):
    """Type of card being evaluated."""
    
    BDR = "bdr"
    VC = "vc"


class TierLevel(int, Enum):
    """Approval tier levels."""
    
    TIER_1 = 1  # Auto-approve
    TIER_2 = 2  # Quick review
    TIER_3 = 3  # Deep review


@dataclass
class RuleResult:
    """Result of evaluating a single rule."""
    
    rule_id: str
    rule_name: str
    passed: bool
    confidence: float  # 0.0 - 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class TierClassification:
    """Final classification result for a card."""
    
    tier: TierLevel
    confidence_score: float  # 0.0 - 100.0
    rules_triggered: List[str] = field(default_factory=list)
    rules_passed: List[str] = field(default_factory=list)
    rules_failed: List[str] = field(default_factory=list)
    reason: str = ""
    auto_approved: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


class CardData(Protocol):
    """Protocol for card data that can be evaluated."""
    
    id: str
    card_type: CardType
    icp_score: Optional[int]
    email: Optional[str]
    linkedin_url: Optional[str]
    status: str
    company_name: Optional[str]
    website_url: Optional[str]
    signals: List[Dict[str, Any]]
    tags: Optional[Union[List[str], str]]
    custom_metadata: Optional[Union[Dict[str, Any], str]]
    
    # For VC cards
    stage_focus: Optional[List[str]]
    sector: Optional[str]
    
    # For BDR cards
    partner_type: Optional[str]
    use_case_fit: Optional[str]


class Rule:
    """Base class for approval rules."""
    
    def __init__(self, rule_id: str, name: str, weight: float = 1.0):
        self.rule_id = rule_id
        self.name = name
        self.weight = weight
    
    def evaluate(self, card: CardData) -> RuleResult:
        """Evaluate the rule against card data."""
        raise NotImplementedError


class ICPScoreRule(Rule):
    """RULE-01: Check if ICP score meets threshold.
    
    BDR: ICP score >= 3
    VC: ICP score >= 4
    """
    
    def __init__(self):
        super().__init__("RULE-01", "ICP Score Check", weight=1.0)
    
    def evaluate(self, card: CardData) -> RuleResult:
        icp_score = card.icp_score
        
        if icp_score is None:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=False,
                confidence=0.0,
                message="ICP score not provided"
            )
        
        if card.card_type == CardType.BDR:
            threshold = 3
            max_score = 5
        else:  # VC
            threshold = 4
            max_score = 5
        
        passed = icp_score >= threshold
        
        # Calculate confidence based on how much above threshold
        if passed:
            confidence = 0.8 + (0.2 * (icp_score - threshold) / (max_score - threshold))
        else:
            confidence = max(0.0, 0.5 * (icp_score / threshold))
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=min(1.0, confidence),
            metadata={"icp_score": icp_score, "threshold": threshold},
            message=f"ICP score {icp_score} {'meets' if passed else 'below'} threshold {threshold}"
        )


class ContactVerificationRule(Rule):
    """RULE-02: Verify contact information format.
    
    Checks:
    - Email format is valid
    - LinkedIn URL format is valid
    - Email domain matches company (when possible)
    """
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    LINKEDIN_REGEX = re.compile(r'^https?://(www\.)?linkedin\.com/.*$', re.IGNORECASE)
    
    def __init__(self):
        super().__init__("RULE-02", "Contact Verification", weight=1.0)
    
    def evaluate(self, card: CardData) -> RuleResult:
        email = card.email or ""
        linkedin = card.linkedin_url or ""
        
        checks = []
        
        # Check email format
        if email:
            email_valid = bool(self.EMAIL_REGEX.match(email))
            checks.append(("email_format", email_valid))
            
            # Check if domain matches company website (heuristic)
            if email_valid and card.website_url:
                email_domain = email.split('@')[-1].lower()
                website_domain = self._extract_domain(card.website_url)
                domain_match = email_domain == website_domain or email_domain.endswith('.' + website_domain)
                checks.append(("domain_match", domain_match))
        else:
            checks.append(("email_format", False))
        
        # Check LinkedIn format
        if linkedin:
            linkedin_valid = bool(self.LINKEDIN_REGEX.match(linkedin))
            checks.append(("linkedin_format", linkedin_valid))
        else:
            checks.append(("linkedin_format", False))
        
        # Need at least one valid contact method
        has_email = any(c[0] == "email_format" and c[1] for c in checks)
        has_linkedin = any(c[0] == "linkedin_format" and c[1] for c in checks)
        
        passed = has_email or has_linkedin
        
        # Calculate confidence based on number of valid checks
        valid_count = sum(1 for _, valid in checks if valid)
        total_count = len(checks)
        confidence = valid_count / total_count if total_count > 0 else 0.0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=confidence,
            metadata={
                "has_valid_email": has_email,
                "has_valid_linkedin": has_linkedin,
                "checks": {name: valid for name, valid in checks}
            },
            message=f"Contact verification: {valid_count}/{total_count} checks passed"
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        url = url.lower().replace('https://', '').replace('http://', '').replace('www.', '')
        return url.split('/')[0].split(':')[0]


class SignalStrengthRule(Rule):
    """RULE-03: Check partner signal strength (BDR only).
    
    Requires at least 2 of the following signals:
    - Recent funding announcement (< 6 months)
    - Job posting in relevant category (< 30 days)
    - Leadership change announced (< 3 months)
    - Website technology change detected (< 60 days)
    """
    
    def __init__(self):
        super().__init__("RULE-03", "Signal Strength", weight=1.0)
    
    def evaluate(self, card: CardData) -> RuleResult:
        # This rule only applies to BDR cards
        if card.card_type != CardType.BDR:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=True,
                confidence=1.0,
                message="Signal strength rule not applicable to VC cards"
            )
        
        signals = card.signals or []
        
        if not signals:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=False,
                confidence=0.0,
                message="No signals provided"
            )
        
        now = datetime.utcnow()
        
        # Define signal recency windows
        signal_checks = {
            "funding": {"window": timedelta(days=180), "found": False},  # 6 months
            "job_posting": {"window": timedelta(days=30), "found": False},  # 30 days
            "leadership_change": {"window": timedelta(days=90), "found": False},  # 3 months
            "tech_change": {"window": timedelta(days=60), "found": False},  # 60 days
        }
        
        for signal in signals:
            signal_type = signal.get("type", "").lower()
            signal_date_str = signal.get("date") or signal.get("detected_at")
            
            if not signal_date_str:
                continue
            
            try:
                if isinstance(signal_date_str, str):
                    signal_date = datetime.fromisoformat(signal_date_str.replace('Z', '+00:00'))
                else:
                    signal_date = signal_date_str
                
                age = now - signal_date
                
                # Check each signal type
                if "fund" in signal_type or "investment" in signal_type or "series" in signal_type:
                    if age <= signal_checks["funding"]["window"]:
                        signal_checks["funding"]["found"] = True
                
                if "job" in signal_type or "hiring" in signal_type or "posting" in signal_type:
                    if age <= signal_checks["job_posting"]["window"]:
                        signal_checks["job_posting"]["found"] = True
                
                if "leadership" in signal_type or "executive" in signal_type or "ceo" in signal_type:
                    if age <= signal_checks["leadership_change"]["window"]:
                        signal_checks["leadership_change"]["found"] = True
                
                if "tech" in signal_type or "website" in signal_type or "stack" in signal_type:
                    if age <= signal_checks["tech_change"]["window"]:
                        signal_checks["tech_change"]["found"] = True
                        
            except (ValueError, TypeError):
                continue
        
        # Count valid signals
        valid_signals = sum(1 for check in signal_checks.values() if check["found"])
        required_signals = 2
        
        passed = valid_signals >= required_signals
        
        # Calculate confidence
        confidence = min(1.0, valid_signals / required_signals) if required_signals > 0 else 0.0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=confidence,
            metadata={
                "valid_signals": valid_signals,
                "required_signals": required_signals,
                "signals_found": {k: v["found"] for k, v in signal_checks.items()}
            },
            message=f"Found {valid_signals}/{required_signals} required signals"
        )


class NoOverrideFlagsRule(Rule):
    """RULE-04: Check for manual override flags.
    
    Card should NOT have:
    - "Needs Lucas Review" flag
    - Manual review requested
    - Company on watch/exclude list
    """
    
    def __init__(self):
        super().__init__("RULE-04", "No Override Flags", weight=1.0)
    
    def evaluate(self, card: CardData) -> RuleResult:
        flags_found = []
        
        # Check tags
        tags = card.tags or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        tag_lower = [t.lower() for t in tags]
        
        if "needs lucas review" in tag_lower or "manual review" in tag_lower:
            flags_found.append("manual_review_requested")
        
        if "watch list" in tag_lower or "exclude" in tag_lower:
            flags_found.append("on_watch_list")
        
        # Check custom metadata
        metadata = card.custom_metadata or {}
        if isinstance(metadata, str):
            try:
                import json
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        
        if metadata.get("manual_review_requested"):
            flags_found.append("manual_review_requested")
        
        if metadata.get("on_watch_list"):
            flags_found.append("on_watch_list")
        
        # Check status
        if card.status and card.status.upper() in ["NEEDS_REVIEW", "FLAGGED", "ON_HOLD"]:
            flags_found.append(f"status_{card.status.lower()}")
        
        passed = len(flags_found) == 0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=1.0 if passed else 0.0,
            metadata={"flags_found": list(set(flags_found))},
            message="No override flags found" if passed else f"Override flags: {flags_found}"
        )


class CardCompletenessRule(Rule):
    """RULE-05: Check card completeness.
    
    Required fields:
    - Company/partner name
    - Contact name + email/LinkedIn
    - Partner type (BDR) or Stage focus (VC)
    - ICP score
    """
    
    def __init__(self):
        super().__init__("RULE-05", "Card Completeness", weight=1.0)
    
    def evaluate(self, card: CardData) -> RuleResult:
        missing_fields = []
        
        # Check company name
        if not card.company_name or not card.company_name.strip():
            missing_fields.append("company_name")
        
        # Check contact info (email or linkedin)
        has_contact = bool(card.email and card.email.strip()) or bool(card.linkedin_url and card.linkedin_url.strip())
        if not has_contact:
            missing_fields.append("contact_info")
        
        # Check ICP score
        if card.icp_score is None:
            missing_fields.append("icp_score")
        
        # Check type-specific fields
        if card.card_type == CardType.BDR:
            if not card.partner_type or not card.partner_type.strip():
                missing_fields.append("partner_type")
        else:  # VC
            if not card.stage_focus or len(card.stage_focus) == 0:
                missing_fields.append("stage_focus")
        
        passed = len(missing_fields) == 0
        
        # Calculate confidence based on completeness
        required_fields = 4  # company_name, contact, icp_score, type_field
        filled_fields = required_fields - len(missing_fields)
        confidence = filled_fields / required_fields
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=confidence,
            metadata={"missing_fields": missing_fields, "filled_fields": filled_fields},
            message=f"Card completeness: {filled_fields}/{required_fields} fields populated"
        )


class StrategicAlignmentRule(Rule):
    """RULE-06: Check strategic alignment (VC only).
    
    For VC cards:
    - Investment stage matches target profile (Seed-Series B)
    - Sector/industry aligns with investment thesis
    """
    
    TARGET_STAGES = ["seed", "series a", "series b", "pre-seed", "angel"]
    TARGET_SECTORS = ["gaming", "games", "interactive entertainment", "esports", "game tech"]
    
    def __init__(self):
        super().__init__("RULE-06", "Strategic Alignment", weight=0.8)
    
    def evaluate(self, card: CardData) -> RuleResult:
        # This rule primarily applies to VC cards
        if card.card_type != CardType.VC:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=True,
                confidence=1.0,
                message="Strategic alignment rule not applicable to BDR cards"
            )
        
        checks = []
        
        # Check stage focus
        stage_focus = card.stage_focus or []
        if isinstance(stage_focus, str):
            stage_focus = [s.strip() for s in stage_focus.split(',') if s.strip()]
        
        stage_match = any(
            target in stage.lower() 
            for stage in stage_focus 
            for target in self.TARGET_STAGES
        )
        checks.append(("stage_match", stage_match))
        
        # Check sector alignment (using company info as proxy)
        sector = (card.sector or "").lower()
        industry = (getattr(card, 'industry', '') or "").lower()
        
        sector_match = any(
            target in sector or target in industry 
            for target in self.TARGET_SECTORS
        )
        checks.append(("sector_match", sector_match))
        
        # For VC, we want both stage and sector to match for high confidence
        passed = stage_match and sector_match
        
        valid_count = sum(1 for _, valid in checks if valid)
        total_count = len(checks)
        confidence = valid_count / total_count if total_count > 0 else 0.0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            confidence=confidence,
            metadata={
                "stage_focus": stage_focus,
                "sector": card.sector,
                "checks": {name: valid for name, valid in checks}
            },
            message=f"Strategic alignment: {valid_count}/{total_count} checks passed"
        )


class ApprovalRulesEngine:
    """Rules engine for classifying cards into approval tiers."""
    
    # Confidence thresholds for tier assignment
    TIER_1_THRESHOLD = 95.0  # Auto-approve
    TIER_2_THRESHOLD = 85.0  # Quick review
    
    def __init__(self):
        self.rules: List[Rule] = [
            ICPScoreRule(),
            ContactVerificationRule(),
            SignalStrengthRule(),
            NoOverrideFlagsRule(),
            CardCompletenessRule(),
            StrategicAlignmentRule(),
        ]
    
    def evaluate(self, card: CardData) -> TierClassification:
        """Evaluate all rules and return tier classification.
        
        Args:
            card: The card data to evaluate
            
        Returns:
            TierClassification with tier level, confidence score, and rule results
        """
        results: List[RuleResult] = []
        
        for rule in self.rules:
            try:
                result = rule.evaluate(card)
                results.append(result)
            except Exception as e:
                # Log error but continue with other rules
                results.append(RuleResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    passed=False,
                    confidence=0.0,
                    message=f"Rule evaluation error: {str(e)}"
                ))
        
        return self._calculate_classification(results)
    
    def _calculate_classification(self, results: List[RuleResult]) -> TierClassification:
        """Calculate final classification from rule results."""
        if not results:
            return TierClassification(
                tier=TierLevel.TIER_3,
                confidence_score=0.0,
                reason="No rules evaluated"
            )
        
        passed_rules = [r for r in results if r.passed]
        failed_rules = [r for r in results if not r.passed]
        
        # Calculate weighted confidence score
        total_weight = sum(r.weight for r in results)
        weighted_confidence = sum(r.confidence * r.weight for r in results) / total_weight if total_weight > 0 else 0.0
        
        # Convert to percentage
        confidence_percentage = round(weighted_confidence * 100, 2)
        
        # Determine tier based on confidence and rules passed
        all_rules_passed = len(failed_rules) == 0
        
        if confidence_percentage >= self.TIER_1_THRESHOLD and all_rules_passed:
            tier = TierLevel.TIER_1
            auto_approved = True
            reason = "All rules passed with high confidence"
        elif confidence_percentage >= self.TIER_2_THRESHOLD:
            tier = TierLevel.TIER_2
            auto_approved = False
            reason = f"Medium confidence ({confidence_percentage}%). {len(failed_rules)} rules failed."
        else:
            tier = TierLevel.TIER_3
            auto_approved = False
            reason = f"Low confidence ({confidence_percentage}%). {len(failed_rules)} rules failed."
        
        return TierClassification(
            tier=tier,
            confidence_score=confidence_percentage,
            rules_triggered=[r.rule_id for r in results],
            rules_passed=[r.rule_id for r in passed_rules],
            rules_failed=[r.rule_id for r in failed_rules],
            reason=reason,
            auto_approved=auto_approved,
            details={
                "rule_results": [
                    {
                        "rule_id": r.rule_id,
                        "rule_name": r.rule_name,
                        "passed": r.passed,
                        "confidence": round(r.confidence * 100, 2),
                        "message": r.message,
                        "metadata": r.metadata
                    }
                    for r in results
                ]
            }
        )
    
    def evaluate_bulk(self, cards: List[CardData]) -> List[TierClassification]:
        """Evaluate multiple cards in bulk."""
        return [self.evaluate(card) for card in cards]


# Convenience function for direct usage
def classify_card(card: CardData) -> TierClassification:
    """Classify a single card using the default rules engine."""
    engine = ApprovalRulesEngine()
    return engine.evaluate(card)