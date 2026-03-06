# Approval Workflow Optimization
## Outreach System Velocity Enhancement

**Current State:** 31 cards stuck in "Awaiting Approval" (30-45 min to clear), 41 cards in "Approved/Send" queue. Research velocity exceeds approval velocity, creating a compounding backlog.

**Objective:** Reduce approval bottleneck by 70% while maintaining quality standards through pre-qualification scoring and tiered workflows.

---

## 1. Pre-Qualification Scoring System (0-100)

Cards are scored automatically before entering "Awaiting Approval" using six weighted criteria:

| Criteria | Weight | 0 Points | 25 Points | 50 Points | 75 Points | 100 Points |
|----------|--------|----------|-----------|-----------|-----------|------------|
| **ICP Fit** | 25% | No match | Peripheral role/industry | Role fits, industry off | Both fit, weak signal | Strong ICP match + intent signal |
| **Data Quality** | 20% | Missing 3+ fields | Missing 2 fields | Complete basic data | Complete + enriched | Complete + enriched + personalized hook |
| **Source Quality** | 15% | Scraped/unverified | Purchased list | Referral/organic | Warm intro | Direct inbound request |
| **Timing Signal** | 15% | No signal | Funding 12mo+ ago | Recent funding/hiring | Active job posts | Explicit pain statement shared |
| **Personalization** | 15% | Template only | Basic merge tags | Company-specific | Role-specific angle | Trigger-based custom hook |
| **Account Tier** | 10% | Below target | Tier 3 | Tier 2 | Tier 1 strategic | Tier 1 + competitive intel |

**Scoring Formula:** Weighted average across all criteria, rounded to nearest integer.

**Auto-Actions Based on Score:**
- **90-100:** Auto-approve, send immediately
- **75-89:** Auto-approve, batch-send (top of hour)
- **60-74:** Flag for batch review (Lucas reviews 10 at once)
- **Below 60:** Return to researcher for improvement or reject

---

## 2. Decision Tree for Batch Approvals

```
START: Card reaches "Awaiting Approval"
│
├─→ Score ≥ 75?
│   ├─→ YES → Auto-approve → Move to "Approved/Send"
│   └─→ NO → Continue to manual review
│
├─→ Score 60-74?
│   ├─→ ICP Fit ≥ 50 AND Data Quality ≥ 50?
│   │   ├─→ YES → Batch review queue (review 10 together)
│   │   └─→ NO → Return for improvement with specific notes
│   └─→
│
├─→ Score < 60?
│   ├─→ ICP Fit ≥ 25?
│   │   ├─→ YES → Return with improvement request
│   │   └─→ NO → Reject (does not meet minimum threshold)
│   └─→
│
└─→ Manual Review Required?
    ├─→ Tier 1-2 accounts (strategic priority)
    ├─→ Unusual signals requiring judgment
    └─→ First-time ICP segments (calibration mode)
```

**Batch Review Protocol (60-74 score cards):**
1. Group by score range (60-64, 65-69, 70-74)
2. Sort by ICP Fit within each group
3. Review in blocks of 10
4. Binary decision: Approve All / Flag Exceptions / Reject All
5. Target: 2 minutes per batch of 10

---

## 3. Tiered Approval Workflow

### Tier 1: Strategic Accounts (Score 90-100)
- **Criteria:** Enterprise logos, board members at tier-1 VCs, direct competitors of current customers
- **Process:** Auto-approve with delay buffer (30-min window to cancel)
- **Volume Target:** <10% of total flow
- **Escalation:** Immediately notify Lucas of sends via daily digest

### Tier 2: High-Value Prospects (Score 75-89)
- **Criteria:** Clear ICP fit, strong timing signal, complete data
- **Process:** Auto-approve, batch-send hourly
- **Volume Target:** 30-40% of total flow
- **Review:** Weekly sampling audit (5% random sample)

### Tier 3: Standard Prospects (Score 60-74)
- **Criteria:** Meets minimum thresholds, needs batch review
- **Process:** Accumulate in "Batch Review" column, review 2x daily
- **Volume Target:** 40-50% of total flow
- **SLA:** Review within 4 hours of reaching threshold (10+ cards)

### Tier 4: Below Threshold (<60)
- **Criteria:** Insufficient data or poor fit
- **Process:** Return to researcher with automated feedback
- **Volume Target:** Reduce to <10% through researcher coaching

---

## 4. Implementation Roadmap

### Phase 1: Scoring System (Week 1)
- [ ] Add "Pre-Qual Score" custom field to cards
- [ ] Create scoring rubric checklist for researchers
- [ ] Train researchers to self-score before submitting
- [ ] Implement auto-calculation formula

### Phase 2: Auto-Approval Rules (Week 2)
- [ ] Configure automation: Score ≥75 → Move to "Approved/Send"
- [ ] Set up delayed send buffer for Tier 1 (30-min cancellation window)
- [ ] Create "Batch Review" column for 60-74 scores
- [ ] Build rejection workflow with feedback templates

### Phase 3: Batch Review UI (Week 3)
- [ ] Create filtered view: Score 60-74, grouped by tier
- [ ] Design side-by-side comparison layout (10 cards visible)
- [ ] Add bulk action buttons: Approve All / Flag / Reject All
- [ ] Set up daily digest of auto-approved sends

### Phase 4: Calibration (Week 4)
- [ ] Run parallel scoring (researcher + system) for calibration
- [ ] Adjust weights based on reply-rate correlation
- [ ] Tune thresholds based on false-positive rate
- [ ] Document edge cases and judgment calls

---

## 5. Expected Outcomes

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Cards in "Awaiting Approval" | 31 | <10 | -68% |
| Time to clear approval queue | 30-45 min | <10 min | -75% |
| Auto-approved volume | 0% | 40-50% | +50pp |
| Lucas review time per card | 60-90 sec | 12 sec (batched) | -85% |
| Research→Send cycle time | 2-4 hours | <1 hour | -70% |

**Risk Mitigation:**
- 30-minute cancellation window for Tier 1 auto-approvals
- Weekly audit of 5% random sample from auto-approved pool
- Reply rate tracking by approval method (manual vs auto)
- Escalation trigger: If auto-approved reply rate drops 20%+ below manual, pause and recalibrate

---

## 6. Tooling & Automation

**Required:**
- Trello custom fields for scoring
- Butler automation rules for auto-approval
- Filtered views for batch review

**Optional Enhancements:**
- Zapier/Make integration for send delays
- Simple dashboard tracking approval velocity
- Slack notification for Tier 1 sends

**No additional tools required** — works within existing Trello setup.

---

## Summary

This system converts approval from a serial bottleneck into a tiered flow:
- **High-quality cards** bypass approval entirely
- **Medium-quality cards** batch efficiently
- **Low-quality cards** return for improvement before consuming review time

Lucas's cognitive load shifts from reviewing every card to spot-checking samples and handling edge cases. Research velocity can increase without creating approval debt.

**Next Step:** Implement Phase 1 scoring system and run calibration for 1 week before activating auto-approvals.
