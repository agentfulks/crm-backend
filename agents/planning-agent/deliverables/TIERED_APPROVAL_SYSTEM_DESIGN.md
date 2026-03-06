# Tiered Approval System Design
## Reducing Lucas' Approval Load by 80%

**Date:** March 4, 2026  
**Current Backlog:** 132 cards (29 VC + 103 BDR)  
**Target:** Reduce daily approval time from 60+ min to 15 min  
**Success Metric:** 80% reduction in manual review time while preserving quality

---

## Executive Summary

This tiered approval system redistributes the approval workload across three tiers:

| Tier | Volume | Time per Card | Daily Time* | Cumulative |
|------|--------|---------------|-------------|------------|
| Tier 1 (Auto-approve) | 60% | 0 sec | 0 min | 0 min |
| Tier 2 (Quick review) | 25% | 30 sec | 3.75 min | 3.75 min |
| Tier 3 (Deep review) | 15% | 4 min | 6 min | 9.75 min |

*Based on 15 cards/day production rate

**Result:** Daily approval time drops from 60+ min to ~10 min (83% reduction).

---

## 1. AUTO-APPROVAL CRITERIA (Tier 1 - 60% of Cards)

### 1.1 Eligible Card Types

**Both VC and BDR cards qualify for auto-approval when they meet criteria.**

| Card Type | Qualification Rate | Estimated Cards/Day |
|-----------|-------------------|---------------------|
| BDR Cards | ~65% | 6-10 cards |
| VC Cards | ~45% | 2-3 cards |

**Why VC cards have lower auto-approval:** Higher strategic value and investment context sensitivity requires stricter criteria.

### 1.2 Auto-Approval Rules

A card auto-approves when it satisfies **ALL** required criteria for its type:

#### Rule 1: ICP Score Threshold
```
BDR: ICP score ≥ 3 (out of 5)
VC:  ICP score ≥ 4 (out of 5)
```
**Data Source:** Card's ICP scoring field (already collected)

#### Rule 2: Contact Verification
```
Partner contact email OR LinkedIn URL is verified as valid format
AND domain matches claimed company
```
**Data Source:** Contact enrichment API (Hunter.io, Clearbit)

#### Rule 3: Partner Signal Strength (BDR only)
```
At least 2 of the following signals present:
- Recent funding announcement (< 6 months)
- Job posting in relevant category (< 30 days)
- Leadership change announced (< 3 months)
- Website technology change detected (< 60 days)
```
**Data Source:** Signal tracking system (already implemented)

#### Rule 4: No Manual Override Flags
```
NONE of the following are true:
- Card marked "Needs Lucas Review"
- Manual review requested by card creator
- Company is on "Watch List" or "Exclude List"
```

#### Rule 5: Card Completeness (BDR)
```
All required fields populated:
- Partner company name
- Contact name + email/LinkedIn
- Partner type (Integrator/Referral/Strategic)
- ICP score
- Signal source(s)
```

#### Rule 6: Strategic Alignment (VC)
```
Investment stage matches target profile (Seed-Series B)
AND
Sector/industry aligns with current investment thesis
AND
Lead partner has track record (>2 investments in similar space)
```

### 1.3 Confidence Threshold Requirements

| Confidence Level | Requirements | Action |
|-----------------|--------------|--------|
| **HIGH (95%+)** | Meets ALL 6 rules | Auto-approve immediately |
| **MEDIUM (85-94%)** | Meets 5/6 rules OR has minor data gap | Queue for Tier 2 review |
| **LOW (<85%)** | Meets <5 rules OR major data uncertainty | Queue for Tier 2 review |

### 1.4 Auto-Approval Audit Trail

All auto-approved cards must log:
- Timestamp of approval
- Rules triggered (which criteria were met)
- Confidence score
- Data sources used
- Option to "Flag for Review" (visible on card)

---

## 2. QUICK REVIEW CRITERIA (Tier 2 - 25% of Cards)

Tier 2 cards require Lucas' review but are optimized for 30-second decision-making.

### 2.1 What Lands in Tier 2

| Scenario | Example |
|----------|---------|
| Medium confidence auto-approval | ICP score 3 but only 1 strong signal |
| High-value but low-complexity | BDR card for known partner, new contact |
| Data gaps in key fields | Missing LinkedIn but email verified |
| VC cards below auto-approve threshold | ICP score 3, funding 6 months old |
| Flagged auto-approvals | Team member questioned auto-approval |

### 2.2 The 30-Second Review Checklist

Lucas scans these elements in order:

```
[1] Card Type + ICP Score    (3 sec) → If ICP < 2, reject immediately
[2] Partner/Company Name     (5 sec) → Known good? Proceed. Unknown? Check.
[3] Contact Quality          (5 sec) → Email valid? LinkedIn populated?
[4] Signal Relevance         (8 sec) → Do signals match our needs?
[5] Strategic Fit            (5 sec) → Does this align with priorities?
[6] Gut Check                (4 sec) → Any red flags?
                                      ─────────────────────
                                      Total: 30 seconds
```

### 2.3 Red Flags That Escalate to Tier 3

| Red Flag | Why It Matters |
|----------|----------------|
| Contact email is generic (gmail/yahoo) | Quality indicator, possible spam |
| Company website returns 404 or looks abandoned | Dead opportunity |
| ICP score 1-2 with no strong signals | Low-value pursuit |
| Partner previously flagged as problematic | Relationship risk |
| Signals > 6 months old | Stale opportunity, likely missed window |
| Duplicate contact (already in CRM) | Wasted effort, possible conflict |
| VC firm outside target stage range | Misaligned investment profile |
| BDR partner has < 10 employees | Too small for meaningful partnership |

### 2.4 UI/UX Recommendations for Fast Review

**Current State Problem:** Full card view requires scrolling, multiple clicks to approve.

**Tier 2 Optimized View:**

```
┌─────────────────────────────────────────────────────────┐
│ [TIER 2 REVIEW]                    [Approve] [Reject]   │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Card Type: BDR Partner | ICP: 3/5 | Confidence: 87%     │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Company: Acme Technologies                              │
│ Contact: Sarah Chen (sarah@acmetech.io) ✓ verified      │
│ LinkedIn: linkedin.com/in/sarahchen ✓                   │
│                                                         │
│ SIGNALS:                                                │
│ • Recent funding: $5M Series A (2 months ago)           │
│ • Job posting: "Partnerships Manager" (14 days ago)     │
│                                                         │
│ WHY TIER 2: Only 1/2 required signals, ICP borderline   │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ [View Full Card]  [Add to Watch List]  [Send to Tier 3] │
└─────────────────────────────────────────────────────────┘
```

**Key UI Changes:**
1. **Condensed view** - All critical data above the fold
2. **Inline actions** - Approve/Reject without navigation
3. **Keyboard shortcuts** - A (approve), R (reject), E (escalate), J (next)
4. **Batch mode** - Checkbox selection for multiple approvals
5. **Confidence explanation** - Clear reason why card needs review

---

## 3. DEEP REVIEW CRITERIA (Tier 3 - 15% of Cards)

### 3.1 When Full Review Is Required

| Category | Criteria |
|----------|----------|
| **High-Value Opportunities** | Strategic partners (>$100K potential), Tier-1 VCs, unicorn-track startups |
| **Complex Scenarios** | Multi-partner deals, conflicting signals, ambiguous fit |
| **Escalations** | Flagged by team, red flags in Tier 2, requested by card creator |
| **VIP/Strategic Accounts** | Pre-defined list of priority companies/partners |
| **Unusual Patterns** | First-time partner type, new market entry, experimental approach |
| **Borderline Cases** | ICP 4-5 but negative signal, or ICP 2-3 with exceptional circumstance |

### 3.2 Strategic/High-Value Opportunity Indicators

**For BDR Cards:**
```
Score 5 on ANY of:
- Partner potential: >$100K ARR opportunity
- Strategic importance: Opens new market or vertical
- Timing: Perfect storm of signals (funding + hiring + exec change)
- Network effect: Partner brings 3+ other potential partners
- Brand value: Partner is recognizable, enhances our positioning
```

**For VC Cards:**
```
Score 5 on ANY of:
- Fund size: >$100M under management
- Track record: >3 successful exits in portfolio
- Strategic thesis: Directly aligns with our roadmap
- Timing: In active deployment phase
- Warm intro: Mutual connection or previous interaction
```

### 3.3 Deep Review Process (Current Process, Unchanged)

Time allocation: 4-5 minutes per card
- Full context review
- Research supplementary information
- Stakeholder consultation (if needed)
- Strategic fit assessment
- Decision with detailed notes

---

## 4. IMPLEMENTATION PLAN

### 4.1 Phase 1: Backend Rules Engine (Week 1)

#### 4.1.1 Rule Evaluation Service

**New Module:** `services/approvalRulesEngine.ts`

```typescript
interface RuleResult {
  ruleId: string;
  passed: boolean;
  confidence: number;
  metadata: Record<string, any>;
}

interface TierClassification {
  tier: 1 | 2 | 3;
  confidence: number;
  rulesTriggered: string[];
  reason: string;
}

class ApprovalRulesEngine {
  evaluate(card: Card): TierClassification {
    // Run all rules
    // Calculate confidence score
    // Return tier classification
  }
}
```

**Rules to Implement:**
| Rule ID | Name | Complexity | Priority |
|---------|------|------------|----------|
| RULE-01 | ICP Score Check | Low | P0 |
| RULE-02 | Contact Verification | Medium | P0 |
| RULE-03 | Signal Strength (BDR) | Medium | P0 |
| RULE-04 | No Override Flags | Low | P0 |
| RULE-05 | Card Completeness | Low | P1 |
| RULE-06 | Strategic Alignment (VC) | Medium | P1 |

#### 4.1.2 Automation Triggers

| Trigger | Action | Timing |
|---------|--------|--------|
| Card created | Run rules engine, assign tier | Immediate |
| Card updated | Re-run rules engine | On field change |
| Auto-approval executed | Log to audit trail, notify creator | Immediate |
| Manual flag added | Force Tier 3, bypass rules | Immediate |
| Batch job nightly | Re-evaluate unclassified cards | 2 AM UTC |

#### 4.1.3 Database Schema Changes

```sql
-- New fields on cards table
ALTER TABLE cards ADD COLUMN tier INT(1) DEFAULT NULL;
ALTER TABLE cards ADD COLUMN confidence_score DECIMAL(5,2) DEFAULT NULL;
ALTER TABLE cards ADD COLUMN auto_approved BOOLEAN DEFAULT FALSE;
ALTER TABLE cards ADD COLUMN auto_approved_at TIMESTAMP NULL;
ALTER TABLE cards ADD COLUMN tier_classification_reason TEXT;

-- New audit table
CREATE TABLE approval_audit_log (
  id SERIAL PRIMARY KEY,
  card_id VARCHAR(255) NOT NULL,
  action VARCHAR(50) NOT NULL, -- 'auto_approve', 'tier_assigned', etc.
  tier INT(1),
  confidence DECIMAL(5,2),
  rules_triggered JSON,
  performed_by VARCHAR(50), -- 'system' or user_id
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_cards_tier ON cards(tier);
CREATE INDEX idx_cards_auto_approved ON cards(auto_approved);
```

### 4.2 Phase 2: Frontend Changes (Week 2)

#### 4.2.1 Approval Dashboard Redesign

**New Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ APPROVAL DASHBOARD                              [Settings]  │
├─────────────────────────────────────────────────────────────┤
│ FILTERS: [All Tiers ▼] [BDR ▼] [Last 7 Days ▼]   [Refresh]  │
├─────────────┬─────────────┬─────────────────────────────────┤
│ TIER 1      │ TIER 2      │ TIER 3                          │
│ (Auto)      │ (Quick)     │ (Deep)                          │
│             │             │                                 │
│ ☑ 89 today  │ ○ 12 cards  │ ○ 4 cards                       │
│             │             │                                 │
│ [View Log]  │ [Start      │ [Start Review]                  │
│             │  Review]    │                                 │
├─────────────┴─────────────┴─────────────────────────────────┤
│ RECENT ACTIVITY                                             │
│ • Auto-approved: Acme Technologies (BDR) - 2 min ago        │
│ • Tier 2 approved: TechVentures (VC) - 15 min ago           │
│ • Escalated: StartupXYZ (BDR) - 1 hour ago                  │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Filtering & Views

**New Filter Options:**
- Tier (1/2/3)
- Card Type (BDR/VC)
- Auto-approval status
- Confidence range
- Date range
- Override flags

**Default Views:**
- **Lucas' View:** Tier 2 + Tier 3 cards only (hide auto-approved)
- **Team View:** All cards with tier labels
- **Audit View:** Auto-approved cards with confidence <95%

#### 4.2.3 Batch Actions

**Tier 2 Batch Mode:**
```
[Select All on Page]  [Select Tier 2 Only]

☑ Acme Technologies       [Approve] [Reject] [View]
☐ Beta Corp               [Approve] [Reject] [View]
☑ Gamma Partners          [Approve] [Reject] [View]

[Approve Selected (2)]  [Reject Selected]  [Export Selected]
```

**Bulk Operations:**
- Approve multiple Tier 2 cards at once
- Export audit log for date range
- Re-run rules engine on selected cards

#### 4.2.4 Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `A` | Approve card | Tier 2/3 review modal |
| `R` | Reject card | Tier 2/3 review modal |
| `E` | Escalate to Tier 3 | Tier 2 review |
| `J` / `↓` | Next card | List view |
| `K` / `↑` | Previous card | List view |
| `?` | Show shortcut help | Global |

### 4.3 Phase 3: Monitoring & Optimization (Week 3)

#### 4.3.1 Metrics Dashboard

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Auto-approval rate | 55-65% | <50% or >70% |
| Tier 2 approval time | <45 sec avg | >60 sec |
| Tier 2 → Tier 3 escalation rate | <10% | >15% |
| False positive rate (auto-approved, later rejected) | <2% | >5% |
| Daily approval time | <15 min | >20 min |

#### 4.3.2 Feedback Loop

**Weekly Review Process:**
1. Review 10 random auto-approved cards - any quality issues?
2. Check Tier 2 cards that were rejected - should criteria be tighter?
3. Analyze Tier 3 escalation patterns - any missing auto-approval rules?
4. Adjust confidence thresholds based on data

#### 4.3.3 Machine Learning Future State

**Phase 4 (Future):** Train model on historical approvals
- Features: ICP score, signal data, partner attributes
- Target: Lucas' historical approve/reject decisions
- Goal: Increase auto-approval accuracy to 98%+

---

## 5. SUCCESS METRICS & VALIDATION

### 5.1 Immediate Wins (Week 1-2)

| Metric | Before | Target | How to Measure |
|--------|--------|--------|----------------|
| Cards in backlog | 132 | Clear to <20 | Daily count |
| Lucas' daily approval time | 60+ min | 15 min | Time tracking |
| Auto-approval rate | 0% | 55-65% | Audit log |
| Time to approve (avg) | 4 min | 1 min | Timestamp analysis |

### 5.2 Quality Preservation

| Quality Metric | Target | Measurement |
|----------------|--------|-------------|
| False positive rate | <2% | Track auto-approved cards later rejected |
| Tier 2 approval rate | >80% | Of cards sent to Tier 2, % approved |
| Team satisfaction | >4/5 | Weekly survey |

### 5.3 System Health

| Metric | Target | Alert |
|--------|--------|-------|
| Rules engine latency | <100ms | >500ms |
| Classification accuracy | >90% | Manual spot-check |
| Audit log completeness | 100% | Any missing logs |

---

## 6. RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Auto-approve bad cards | Medium | High | Conservative thresholds initially; audit trail; easy revert |
| Lucas doesn't trust system | Medium | High | Full transparency on why each decision was made; manual override always available |
| Team confusion on tiers | Low | Medium | Clear documentation; in-app tooltips; training session |
| Edge cases break rules | Medium | Medium | Tier 3 catch-all; weekly rule refinement; override capability |
| Performance degradation | Low | Medium | Async rule processing; caching; monitoring alerts |
| Data quality issues | Medium | High | Input validation; fallback to Tier 2 for uncertain data |

---

## 7. ROLLOUT PLAN

### Week 1: Backend & Rules
- [ ] Implement rules engine
- [ ] Add database schema changes
- [ ] Deploy with shadow mode (classify but don't auto-approve)

### Week 2: Frontend & Soft Launch
- [ ] Build new dashboard views
- [ ] Enable for 25% of new cards
- [ ] Lucas reviews classifications, provides feedback

### Week 3: Full Launch
- [ ] Enable auto-approval for all qualifying cards
- [ ] Monitor metrics daily
- [ ] Adjust thresholds based on data

### Week 4: Optimization
- [ ] Refine rules based on false positives
- [ ] Optimize Tier 2 UI based on usage patterns
- [ ] Document final process

---

## 8. APPENDIX: DECISION TREES

### 8.1 Card Classification Flow

```
Card Created
     ↓
Run Rules Engine
     ↓
┌─────────────────┐
│ Confidence ≥95% │────Yes────┐
│ Meets all rules │           ↓
└─────────────────┘    [TIER 1] Auto-approve
      │ No
      ↓
┌─────────────────┐
│ Confidence ≥70% │────Yes────┐
│ Meets 4-5 rules │           ↓
└─────────────────┘    [TIER 2] Quick Review
      │ No
      ↓
                [TIER 3] Deep Review
```

### 8.2 Tier 2 Review Decision Flow

```
Open Tier 2 Card
      ↓
30-Second Scan
      ↓
┌────────────────┐
│ Red flag seen? │────Yes────┐
└────────────────┘           ↓
      │ No           [Escalate to Tier 3]
      ↓
┌────────────────┐
│ Strategic fit? │────No─────┐
└────────────────┘           ↓
      │ Yes          [Reject]
      ↓
   [Approve]
```

---

## 9. SUMMARY

This tiered approval system will:

1. **Eliminate 60% of manual reviews** through conservative, auditable auto-approval rules
2. **Reduce review time for 25% of cards** to 30 seconds via optimized UI
3. **Preserve quality** by routing only 15% of cards to deep review
4. **Achieve 80%+ time reduction** for Lucas (60 min → 12-15 min daily)
5. **Clear the backlog** within 2 weeks at current production rates

The system is designed for immediate implementation using existing infrastructure, with clear metrics to validate success and a feedback loop for continuous improvement.

**Next Action:** Begin Phase 1 implementation (backend rules engine).
