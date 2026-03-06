# Tiered Approval System: Resolving the Lucas Approval Bottleneck

## Executive Summary

**The Problem:** Lucas is the sole approval bottleneck with 132 cards queued and 0/day approval velocity against 10-15/day production rate. At current velocity, the backlog grows infinitely. This is a classic single-point-of-failure that will collapse the outbound system within days.

**The Solution:** A 3-tier approval system that automates 60% of approvals, delegates 25% to quick review, and reserves Lucas's attention for 15% of high-stakes decisions. Combined with the "Morning 20" ritual, this reduces Lucas's daily approval burden from 10-15 cards to 3-5 cards.

---

## 1. Backlog Analysis: Time-to-Clear Projections

### Current State
| Metric | Value |
|--------|-------|
| Total backlog | 132 cards |
| Daily production | 10-15 cards |
| Current approval velocity | 0/day |
| Net daily growth | +10-15 cards |
| 7+ day stale cards | 29 cards |

### Time-to-Clear at Different Approval Velocities

| Daily Approvals | Days to Clear Backlog | Net Daily Change | Sustainability |
|-----------------|----------------------|------------------|----------------|
| 5 cards/day | 26 days | +5 to +10 growth | **Failing** |
| 10 cards/day | 13 days | 0 to +5 growth | **Stagnant** |
| 15 cards/day | 9 days | -5 to 0 change | Stable |
| 20 cards/day (Morning 20) | 7 days | -5 to -10 reduction | **Improving** |
| 25 cards/day | 5 days | -10 to -15 reduction | Fast recovery |
| 40 cards/day (catch-up mode) | 4 days | -25 to -30 reduction | Emergency only |

**Key Insight:** Lucas needs to approve at least 15 cards/day just to stop the backlog from growing. To actually clear it, we need 20+ cards/day or must reduce the approval burden through automation.

### Without Intervention: Projected Backlog Growth
| Day | Backlog Size | 7+ Day Stale Cards |
|-----|--------------|-------------------|
| Today | 132 | 29 |
| +7 days | 207-237 | 58-88 |
| +14 days | 282-342 | 87-147 |
| +30 days | 432-582 | 146-296 |

**Critical:** The system becomes unrecoverable at ~200 cards. Intervention is required immediately.

---

## 2. Tiered Approval System Design

### Tier Distribution Logic

| Tier | % of Cards | Volume (of 15/day) | Action Required | Time per Card |
|------|-----------|-------------------|-----------------|---------------|
| Tier 1: Auto-Approve | 60% | 9 cards | Zero | 0 seconds |
| Tier 2: Quick Review | 25% | 4 cards | Scan checklist | 30 seconds |
| Tier 3: Deep Review | 15% | 2 cards | Full attention | 5 minutes |
| **Total** | **100%** | **15 cards** | — | **~12 minutes** |

**Result:** Lucas's daily time commitment drops from "infinite" to ~12 minutes.

---

## 3. Auto-Approval Criteria (Tier 1 Rules)

Cards automatically approved if they meet ALL criteria in any rule set:

### Rule Set A: Standard VC Outreach
```
IF:
  - Source = "VC Outreach Engine"
  - Fund stage matches target list (Pre-seed, Seed, Series A)
  - Location = US, UK, Canada, or EU
  - Last funding round within 18 months
  - Portfolio company count >= 5
  - Checkmate score >= 7/10
  - No red flags in company description
THEN: Auto-approve
```

### Rule Set B: Game Studio BDR
```
IF:
  - Source = "BDR Game Studios"
  - Studio size = 10-200 employees
  - Recent funding OR revenue-positive
  - Genre alignment with portfolio
  - No active litigation or major controversy
  - Pitch angle uses approved template variant
THEN: Auto-approve
```

### Rule Set C: Repeat Outreach
```
IF:
  - Same target contacted before (previous campaign)
  - Previous response was neutral or positive
  - New pitch uses improved angle
  - Time since last contact > 90 days
  - No opt-out or negative response on record
THEN: Auto-approve
```

### Rule Set D: Warm Introduction Path
```
IF:
  - Mutual connection identified
  - Connection strength = strong or very strong
  - Introduction request message pre-approved
  - Target fits ideal customer profile
THEN: Auto-approve
```

### Rule Set E: Data-Rich Cold Outreach
```
IF:
  - Decision maker email verified (not guessed)
  - Personalization tokens > 3
  - Company research summary attached
  - Recent trigger event identified (funding, hiring, expansion)
  - Pitch references specific company milestone
THEN: Auto-approve
```

### Rule Set F: Template-Based with Perfect Match
```
IF:
  - 100% match with pre-approved template criteria
  - All required fields populated
  - No custom modifications outside template bounds
  - Target on "green list" (pre-vetted companies)
THEN: Auto-approve
```

---

## 4. The "Morning 20" Ritual

### Protocol

**Time:** 20 minutes, first thing each morning (before Slack, before email)

**Goal:** Process 20 cards minimum (10+ backlog, 10+ daily new)

**Structure:**

| Minutes | Action | Target |
|---------|--------|--------|
| 0-2 | Review Tier 3 stack | Identify 2-3 cards needing deep review |
| 2-10 | Deep reviews (Tier 3) | Approve/reject/delegate 2 cards |
| 10-15 | Quick scans (Tier 2) | Batch-process 8 cards (1 min each) |
| 15-18 | Clear oldest cards | Process 5 cards from 7+ day queue |
| 18-20 | Buffer/overflow | Handle any urgent exceptions |

### Execution Checklist
- [ ] Open Trello filter: "Awaiting Approval" sorted by age (oldest first)
- [ ] Apply tier tags based on criteria (if not auto-tagged)
- [ ] Process Tier 3 first (decision quality highest when fresh)
- [ ] Batch Tier 2 (approve all, mark exceptions)
- [ ] Escalate any card >7 days to priority queue
- [ ] Log count: Approved / Rejected / Delegated / Escalated

### Success Metrics
- 20 cards processed in 20 minutes = 1 card/minute velocity
- Zero cards >7 days in queue
- Tier 3 cards never sit >3 days
- Approval velocity matches or exceeds production rate

---

## 5. Escalation Protocol for Stale Cards

### Severity Levels

#### Level 1: Warning (7 days old)
- **Trigger:** Card in "Awaiting Approval" for 7 days
- **Action:** 
  - Auto-tag with red "STALE" label
  - Move to top of Lucas's queue
  - Send Slack DM: "7 cards need your attention (oldest: [Company Name])"
- **Owner:** System auto-escalation

#### Level 2: Urgent (10 days old)
- **Trigger:** Card still in queue at 10 days
- **Action:**
  - Add "URGENT" label
  - Remove from general queue, add to "Lucas Priority" list
  - Slack DM + email: "10+ day backlog: [X] cards blocked on approval"
  - Notify on next standup agenda
- **Owner:** System + ops team

#### Level 3: Critical (14 days old)
- **Trigger:** Card at 14 days
- **Action:**
  - Move to "Needs Delegation" list
  - Card auto-approved with "deferred review" tag
  - Lucas has 48 hours to override, otherwise sends
  - Weekly report: "Cards auto-approved due to timeout"
- **Owner:** System auto-delegation

#### Level 4: Emergency (21 days old)
- **Trigger:** Card at 21 days
- **Action:**
  - Archive card with reason: "Approval timeout"
  - Add target to "revisit in 90 days" list
  - Process audit: Why did this sit 3 weeks?
- **Owner:** System archival

### Escalation Dashboard

Track these metrics daily:

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Cards >7 days | 0 | 1-10 | 11+ |
| Cards >14 days | 0 | 1-5 | 6+ |
| Avg approval time | <3 days | 3-7 days | >7 days |
| Daily approval velocity | 15+ | 10-14 | <10 |

---

## 6. Implementation Plan

### Immediate Actions (Today)

1. **Audit current backlog**
   - Tag all 132 cards by tier (estimate: 30 minutes)
   - Apply "STALE" label to 29 cards >7 days
   - Move oldest 20 to "Lucas Priority" list

2. **Configure auto-approval rules**
   - Document criteria in team wiki
   - Train BDR/VC teams on Tier 1 requirements
   - Set up automated tagging (if Trello automation available)

3. **Schedule Morning 20**
   - Block 20 minutes on Lucas's calendar (recurring daily)
   - Set Slack status: "Morning 20 in progress"
   - Create Trello filter bookmark

### Week 1 Targets
- [ ] Clear all cards >14 days (emergency triage)
- [ ] Process 20 cards/day via Morning 20
- [ ] Achieve 0 cards entering Level 3 escalation
- [ ] Measure actual tier distribution (validate 60/25/15 assumption)

### Week 2-4 Targets
- [ ] Backlog cleared to <50 cards
- [ ] Approval velocity sustained at 15+/day
- [ ] Auto-approval rate at 60% or higher
- [ ] Lucas time commitment <15 min/day

### Success Criteria (30 Days)
- [ ] Average approval time <48 hours
- [ ] Zero cards >7 days in queue
- [ ] Lucas approval load reduced 70%+
- [ ] Outbound volume maintained or increased
- [ ] Response rates unchanged (quality maintained)

---

## 7. Risk Analysis & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Lucas skips Morning 20 | Medium | High | Calendar block + Slack bot reminder + escalation to team lead |
| Auto-approval criteria too loose | Low | High | Weekly spot-check sample of auto-approved cards; tighten rules if quality drops |
| Auto-approval criteria too tight | Medium | Medium | Monitor Tier 3 volume; if >25%, relax 1-2 criteria |
| Backlog grows despite intervention | Low | Critical | Emergency "approval sprint" — team lead processes cards for 1 hour |
| Quality degrades with speed | Medium | Medium | Track response rates; correlate with approval tier; adjust if needed |
| Team resists new process | Low | Medium | Show time savings; make it easier than old process; no extra work for BDRs |

---

## 8. Quick Reference: Tier Decision Tree

```
CARD ENTERS QUEUE
        |
        v
[Check auto-criteria]
        |
    +---+---+
    |       |
   YES      NO
    |       |
    v       v
AUTO-APPROVE  [Tier 2 or 3?]
    |             |
    |         +---+---+
    |         |       |
    |      QUICK    DEEP
    |      SCAN     REVIEW
    |         |       |
    |         v       v
    |    APPROVE    APPROVE
    |    (30 sec)   (5 min)
    |    or FLAG    or REJECT
    |    for Lucas  or DELEGATE
    |
    v
SEND IMMEDIATELY
```

---

## 9. Appendix: Calculations

### Backlog Clear Math
```
Backlog = 132 cards
Production = 12.5 cards/day (midpoint of 10-15)

To clear in 7 days:
  (132 + 7*12.5) / 7 = 31.4 approvals/day required

To clear in 14 days:
  (132 + 14*12.5) / 14 = 21.9 approvals/day required

To clear in 30 days:
  (132 + 30*12.5) / 30 = 16.9 approvals/day required
```

### Morning 20 Efficiency
```
20 minutes = 1200 seconds

Tier 1 (60%): 12 cards * 0s = 0s
Tier 2 (25%): 5 cards * 30s = 150s
Tier 3 (15%): 3 cards * 300s = 900s
Total time: 1050s = 17.5 minutes
Buffer: 2.5 minutes for context switching
```

### Lucas Time Savings
```
Current state: Infinite (backlog grows)
With Morning 20: 20 min/day
Time saved: ~2-4 hours/day (assuming manual review at 10 min/card)
Efficiency gain: 600-1200%
```

---

## Conclusion

The Lucas approval bottleneck is a process failure, not a people failure. The current single-point-of-approval architecture cannot scale. 

**The tiered system delivers:**
- **Speed:** 20 cards processed in 20 minutes
- **Quality:** High-stakes cards still get full attention
- **Scale:** System handles 2x volume without bottleneck
- **Relief:** Lucas's approval burden reduced by 70%+

**Immediate next step:** Schedule 30 minutes today to tag the existing 132-card backlog by tier and clear all cards >14 days via emergency triage.

---

*Document version: 1.0*
*Created: 2026-03-04*
*Next review: After 30 days of implementation*
