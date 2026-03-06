# Board Cleanup Strategy: Clearing the Awaiting Approval Backlog
**Date:** February 27, 2026  
**Current State:** 46 cards in Awaiting Approval (OVERLOADED), 8 cards in Approved/Send  
**Objective:** Clear backlog in 48 hours while implementing systems to prevent recurrence

---

## 1. TIERED REVIEW FRAMEWORK

### Priority Classification System

| Tier | Fit Score | Action | Processing Time | % of Backlog (Est.) |
|------|-----------|--------|-----------------|---------------------|
| **P0** | 90+ | Auto-approve | Immediate | ~5-10% (2-5 cards) |
| **P1** | 85-89 | Fast-track review | 15 min/card | ~15-20% (7-9 cards) |
| **P2** | 80-84 | Standard review | 30 min/card | ~40-50% (18-23 cards) |
| **P3** | <80 | Deep review / Defer | 45+ min/card | ~25-30% (12-14 cards) |

### P0: Auto-Approve Criteria (Score 90+)
**Characteristics:**
- Perfect or near-perfect firmographic match
- Strong strategic fit signals
- No red flags in qualification data
- High-confidence scoring algorithm output

**Auto-approval rules:**
1. Score ≥90 AND investor type matches target profile
2. No disqualifying attributes (stage mismatch, geography blockers)
3. Warm intro path exists OR high-response-probability cold channel
4. Recent activity signal (funding announcement, portfolio news)

**Action:** Move directly to Approved/Send queue. Batch-process daily at 09:00 and 14:00.

---

### P1: Fast-Track Review (Score 85-89)
**Characteristics:**
- Strong fit with minor uncertainties
- One or two qualification gaps that need quick verification
- Strategic value but requires human judgment

**Fast-track protocol:**
1. Review qualification data for gaps (5 min)
2. Quick web search for recent signals (5 min)
3. Verify contact/channel approach (3 min)
4. Decision: Approve, improve, or downgrade to P2 (2 min)

**Target:** 15 minutes per card maximum. Any card requiring longer investigation gets bumped to P2.

---

### P2: Standard Review (Score 80-84)
**Characteristics:**
- Moderate fit - potential value but requires work
- Multiple qualification gaps or unclear strategic angle
- Worth pursuing but needs customized positioning

**Standard review protocol:**
1. Full qualification verification (10 min)
2. Research for positioning angle (10 min)
3. Draft/customize outreach approach (8 min)
4. Decision: Approve with notes, defer, or reject (2 min)

**Decision options:**
- **Approve:** Move to Approved/Send with custom messaging
- **Defer:** Move to "On Hold" with reason tag
- **Reject:** Archive with disqualification reason

---

### P3: Deep Review / Defer (Score <80)
**Characteristics:**
- Below-threshold fit score
- Significant qualification concerns
- May be viable but requires substantial research or qualification work

**P3 protocol:**
1. Quick triage: Is there a strategic reason to pursue despite low score? (5 min)
2. If yes → Deep research session scheduled separately
3. If no → Move to "Low Priority" queue for batch processing during low-velocity periods

**Rule:** Do not let P3 cards block P0-P2 processing. They can wait.

---

## 2. 48-HOUR CLEARANCE PLAN

### Current Inventory Assessment
- **Total backlog:** 46 cards
- **Estimated distribution:** P0 (3) | P1 (8) | P2 (20) | P3 (15)
- **Day 8 priority cards:** Highest fit scores (85-92) - these bypass normal queue

### Day 1 (Friday) - Clear P0 + P1 + Day 8 Priority

**Phase 1: Auto-Process (09:00-09:30)**
| Time | Action | Output |
|------|--------|--------|
| 09:00-09:15 | Run score analysis, identify P0 cards (~3 cards) | 3 cards auto-approved |
| 09:15-09:30 | Batch-move P0 to Approved/Send | P0 queue cleared |

**Phase 2: Day 8 Priority Sprint (09:30-11:30)**
| Time | Action | Output |
|------|--------|--------|
| 09:30-10:30 | Identify and review all Day 8 cards with scores 85-92 | Day 8 cards categorized |
| 10:30-11:30 | Fast-track approve Day 8 cards with scores 85-89; auto-approve 90+ | Day 8 priority cleared |

**Phase 3: P1 Fast-Track Blitz (11:30-13:30)**
| Time | Action | Output |
|------|--------|--------|
| 11:30-13:30 | Process P1 cards (8 cards × 15 min = 120 min) | P1 queue cleared |

**Phase 4: P2 Initial Processing (14:00-17:00)**
| Time | Action | Output |
|------|--------|--------|
| 14:00-15:30 | Process first 6 P2 cards | 6 P2 cards cleared |
| 15:30-17:00 | Process next 6 P2 cards | 12 P2 cards cleared total |

**End of Day 1 Target:**
- P0: Cleared ✓
- P1: Cleared ✓
- Day 8: Cleared ✓
- P2: 12 of 20 cleared (8 remaining)
- P3: 0 of 15 (intentionally deferred)
- **Remaining backlog:** 23 cards

---

### Day 2 (Saturday/Sunday - as applicable) - Clear Remaining P2 + Triage P3

**Phase 1: Complete P2 Processing (09:00-11:00)**
| Time | Action | Output |
|------|--------|--------|
| 09:00-11:00 | Process remaining 8 P2 cards (8 × 30 min = 240 min) | P2 queue cleared ✓ |

**Phase 2: P3 Triage (11:00-12:00)**
| Time | Action | Output |
|------|--------|--------|
| 11:00-11:30 | Quick triage: Strategic keep vs. defer vs. reject | 15 P3 cards categorized |
| 11:30-12:00 | Move "strategic keep" to dedicated research queue (est. 3-5 cards) | Research queue populated |

**Phase 3: Buffer + Catch-up (14:00-16:00)**
| Time | Action | Output |
|------|--------|--------|
| 14:00-16:00 | Address any cards that needed follow-up from Day 1 | Catch-up complete |

**End of Day 2 Target:**
- P0: Cleared ✓
- P1: Cleared ✓
- P2: Cleared ✓
- Day 8: Cleared ✓
- P3: Triaged (3-5 to research queue, 10-12 to Low Priority queue)
- **Awaiting Approval:** 0 cards (all processed or categorized)

---

## 3. WORKFLOW OPTIMIZATION

### Daily Approval Caps

**Per-Session Limits:**
| Tier | Daily Cap | Rationale |
|------|-----------|-----------|
| P0 | Unlimited | Auto-processed, zero time cost |
| P1 | 10 cards/day | 2.5 hours max (10 × 15 min) |
| P2 | 8 cards/day | 4 hours max (8 × 30 min) |
| P3 | 3 cards/day | 2.25 hours max (3 × 45 min) |

**Daily Total Review Budget:** ~8.75 hours maximum  
**Recommended Sustainable Pace:** 5 hours/day (5 P1 + 6 P2 + 2 P3)

**Overflow Protocol:**
- Cards exceeding daily cap move to next day's queue
- P3 cards that accumulate >30 days without review → auto-archive with "stale" tag
- Weekly "P3 cleanup hour" to process or purge accumulated low-priority cards

---

### Auto-Approve Criteria (Expanded)

**Hard Criteria (ALL must be met):**
1. Fit score ≥90
2. Firmographic match: Stage, check size, geography aligned
3. No disqualifying signals in data enrichment
4. Contact information verified and deliverable

**Soft Criteria (2 of 3 must be met):**
1. Recent activity signal (funding, portfolio news, social activity within 30 days)
2. Warm intro path available OR high-probability cold channel identified
3. Strategic narrative alignment (thesis match clearly documented)

**Auto-approve execution:**
- Batch process at 09:00 and 14:00 daily
- Flag any auto-approved card with "auto" tag for spot-check auditing
- Weekly audit: Review 10% of auto-approved cards for quality
- If error rate >5%, tighten criteria; if <2%, consider expanding criteria

---

### Quality Gates

**Gate 1: Data Enrichment (Pre-Review)**
- All cards must have complete firmographic data before entering Awaiting Approval
- Missing data → auto-return to enrichment queue
- Quality check: Verify investor type, stage focus, check size range

**Gate 2: Scoring Validation (At Review)**
- Reviewer must confirm score rationale before approving
- If reviewer disagrees with score by >10 points → flag for algorithm review
- Monthly: Analyze score-to-outcome correlation to tune algorithm

**Gate 3: Messaging Review (Pre-Send)**
- All approved cards must have custom positioning statement
- Generic/template messaging → return to Approved/Send with notes
- Quality bar: Would this get a response? Test: Read aloud → if it sounds like spam, rewrite.

**Gate 4: Post-Send Monitoring (Feedback Loop)**
- Track response rates by tier (P0/P1/P2/P3)
- If P0 cards show <15% response rate → investigate auto-approve criteria
- If P3 cards show >25% response rate → may need score recalibration

---

## 4. PREVENTING FUTURE BACKLOGS

### Early Warning System

| Trigger Level | Condition | Action |
|---------------|-----------|--------|
| **Green** | <15 cards in Awaiting Approval | Normal operations |
| **Yellow** | 15-25 cards in Awaiting Approval | Increase daily review capacity by 50% |
| **Red** | 25-40 cards in Awaiting Approval | Emergency sprint mode; pause new intake |
| **Critical** | >40 cards in Awaiting Approval | All-hands backlog clearance; freeze enrichment pipeline |

**Current Status:** RED → Moving to Green in 48 hours

### Pipeline Flow Controls

1. **Enrichment Throttle:** If Awaiting Approval >25 cards, pause new enrichment until backlog clears
2. **Review Sprint Mode:** Daily standup when backlog >20 cards; clear P0/P1 first
3. **P3 Overflow Protocol:** P3 cards >30 days old → monthly purge review (approve/reject/archive)

### Automation Opportunities

| Current Manual Task | Automation Potential | Priority |
|--------------------|----------------------|----------|
| P0 identification | High - rules-based auto-approval | Implement immediately |
| P1 pre-screening | Medium - AI-assisted qualification check | Implement within 2 weeks |
| P2 research prep | Medium - auto-populate research links | Implement within 1 month |
| P3 triage | High - auto-move to Low Priority queue | Implement immediately |
| Response tracking | High - auto-tag based on email responses | Implement within 2 weeks |

---

## 5. SUCCESS METRICS

### 48-Hour Clearance KPIs
- [ ] P0 cleared: 100% (all auto-approved)
- [ ] P1 cleared: 100% (all reviewed and dispositioned)
- [ ] Day 8 priority: 100% (all high-fit cards processed)
- [ ] P2 cleared: 100% (all reviewed and dispositioned)
- [ ] P3 triaged: 100% (categorized and queued appropriately)
- [ ] Awaiting Approval backlog: 0 cards

### Ongoing Health Metrics
- **Target backlog size:** <15 cards (Green status)
- **Average time in Awaiting Approval:** <48 hours
- **Auto-approve rate:** 10-20% of inbound cards
- **P3 staleness:** 0 cards >30 days old
- **Reviewer throughput:** 6-10 cards/hour (blended average)

---

## 6. IMMEDIATE ACTION ITEMS

### Today (Day 1 - Friday)
1. [ ] Run score analysis on all 46 cards, apply tier tags
2. [ ] Identify and flag Day 8 priority cards (85-92 fit scores)
3. [ ] Auto-approve all P0 cards (3 cards est.)
4. [ ] Fast-track Day 8 cards through approval
5. [ ] Clear P1 queue (8 cards, 2 hours)
6. [ ] Process first 12 P2 cards (6 hours)

### Tomorrow (Day 2 - Saturday/Sunday)
1. [ ] Complete remaining 8 P2 cards (4 hours)
2. [ ] Triage all 15 P3 cards (1 hour)
3. [ ] Move strategic P3s to research queue
4. [ ] Archive or defer non-strategic P3s
5. [ ] Verify Awaiting Approval = 0

### This Week (Post-Clearance)
1. [ ] Implement auto-approve automation for P0
2. [ ] Set up daily approval cap alerts
3. [ ] Create P3 overflow auto-archive rule
4. [ ] Schedule weekly backlog health check
5. [ ] Document lessons learned and update playbook

---

## APPENDIX: SCORE-TO-TIER MAPPING

| Fit Score | Tier | Processing Path |
|-----------|------|-----------------|
| 90-100 | P0 | Auto-approve |
| 85-89 | P1 | Fast-track review (15 min) |
| 80-84 | P2 | Standard review (30 min) |
| 70-79 | P3 | Deep review / Defer (45+ min) |
| <70 | P3/Low | Triage for archival or extreme edge case |

**Note:** Day 8 cards with scores 85-92 receive expedited processing regardless of their position in the queue.

---

*Strategy v1.0 | Generated February 27, 2026 | Next review: Post-clearance audit*
