# Tiered Approval System Proposal
## Reducing Lucas's Approval Time by 70%

**Date:** March 4, 2026  
**Prepared by:** PLANNING_AGENT  
**Current State:** ~130 cards in backlog, 16 cards 7+ days stale

---

## Executive Summary

**Problem:** Daily production (10-15 cards) exceeds approval velocity (0-5 cards), creating a compounding backlog.

**Solution:** Implement a 3-tier approval system that auto-approves 60-70% of cards based on objective criteria, reducing Lucas's manual review to high-value/strategic decisions only.

**Projected Impact:** Reduces Lucas's approval time from ~6-8 hours/week to ~2 hours/week (70% reduction).

---

## Current Backlog Breakdown

| Source | Queue | Count | Avg Age | Primary Issue |
|--------|-------|-------|---------|---------------|
| VC Outreach Engine | Awaiting Approval | 29-37 | 4-12 days | 16 cards stale (7+ days) |
| VC Outreach Engine | Daily Queue | 25-33 | 1-2 days | Pending initial review |
| BDR Studios | Ready for Review | 93-103 | 2-7 days | Awaiting Lucas |
| BDR Studios | Research Queue | 29 | 1-3 days | Pre-processing |
| **Total** | | **~130** | | **Approval bottleneck** |

---

## Proposed 3-Tier Approval System

### TIER 1: AUTO-APPROVE (60-70% of cards)
**Goal:** Eliminate Lucas's involvement on routine, low-risk cards.

**Criteria (ALL must be met):**
- Card follows standardized template/format
- No custom fields blank or "TBD"
- Company fits target profile (pre-defined ICP match)
- Contact is not C-level or Board member (VP and below)
- Message score ≥ 7/10 (see scoring rubric below)
- No red flags (see below)
- Card aged < 5 days in queue

**Process:**
1. Cards meeting criteria auto-move to "Approved → Send"
2. Lucas receives daily digest of auto-approved cards (view-only)
3. Lucas can "pull back" any card within 24h if needed

**Estimated Volume:** 80-90 cards/week

---

### TIER 2: BATCH REVIEW (20-30% of cards)
**Goal:** Consolidate review time to 2 focused sessions/week.

**Criteria (ANY apply):**
- C-level or Board member contact
- Company is tier-1 target (top 50 VC list)
- Custom messaging required (non-standard angle)
- Message score 5-6/10 (needs polish)
- Card aged 5-10 days in queue

**Process:**
1. Cards accumulate in "Batch Review Queue"
2. Lucas reviews batch 2x/week (Monday/Thursday mornings, 1 hour each)
3. Approve/Reject/Edit in bulk
4. Approved cards move to "Approved → Send"

**Estimated Volume:** 25-35 cards/week  
**Time Required:** 2 hours/week

---

### TIER 3: STRATEGIC REVIEW (5-10% of cards)
**Goal:** Lucas focuses only on high-stakes, high-value opportunities.

**Criteria (ANY apply):**
- Warm intro or mutual connection mentioned
- Company in active fundraising (announced/public)
- Competitor or partner overlap
- Negative prior interaction flagged
- High-value relationship (existing portfolio, strategic)
- Message score < 5/10 (needs rewrite)
- Card aged > 10 days (stale)

**Process:**
1. Cards flagged with "NEEDS LUCAS" label
2. Individual notification sent (Slack/email)
3. Lucas reviews within 24-48 hours
4. Requires explicit approve/reject decision

**Estimated Volume:** 10-15 cards/week  
**Time Required:** 1-2 hours/week

---

## Message Scoring Rubric (7/10 = Auto-Approve)

| Criteria | Points | Description |
|----------|--------|-------------|
| Personalization | 0-2 | Specific reference to recipient's background, firm thesis, or recent activity |
| Value Prop Clarity | 0-2 | Clear "why now, why us" in 2 sentences or less |
| Call to Action | 0-2 | Specific, low-friction ask (15-min call, intro to X, feedback on deck) |
| Tone Fit | 0-2 | Matches recipient's style (formal vs. casual, based on LinkedIn/public persona) |
| No Red Flags | 0-1 | No typos, no generic "dear sir/madam," no attachment on first contact |
| Timing Relevance | 0-1 | References recent fund raise, investment, or market event (< 90 days) |

**Score 7+:** Auto-approve eligible (if other criteria met)  
**Score 5-6:** Batch review  
**Score < 5:** Return to author for rewrite

---

## Red Flags (Auto-Fail Tier 1)

**Hard No-Go:**
- Generic salutation ("Dear Investor," "To Whom It May Concern")
- No specific value proposition
- Attachment on cold outreach
- Typos or grammatical errors
- Wrong company/contact name
- Fund already invested in competitor (without addressing)
- Unsubstantiated claims ("the next unicorn")

**Soft Flags (Require Review):**
- Unusual request (partnership before intro)
- Request for NDA before conversation
- Aggressive follow-up tone

---

## Suggested Batch Approval Schedule

| Day | Time | Activity | Duration |
|-----|------|----------|----------|
| Monday | 9:00-10:00 AM | Batch Review (Tier 2) — approve routine cards | 1 hour |
| Monday | 10:00-10:30 AM | Quick scan of Tier 1 auto-approvals | 30 min |
| Thursday | 9:00-10:00 AM | Batch Review (Tier 2) — second batch | 1 hour |
| Thursday | 10:00-10:30 AM | Review any Tier 3 strategic cards | 30 min |
| Friday | 4:00-4:30 PM | Weekly summary review + adjustments | 30 min |

**Total Weekly Time:** ~3.5 hours (vs. current ~12 hours)  
**Time Savings:** 70% reduction

---

## Implementation Steps

### Week 1: Setup & Calibration
- [ ] Define ICP (Ideal Customer Profile) criteria for VC targets
- [ ] Create top 50 tier-1 VC list for Tier 2 flagging
- [ ] Build message scoring rubric into workflow (spreadsheet or tool)
- [ ] Create auto-approval digest template
- [ ] Set up "NEEDS LUCAS" notification channel (Slack DM or email)

### Week 2: Pilot
- [ ] Apply system to 20 cards (mix of Tier 1/2/3)
- [ ] Lucas reviews calibration — adjust criteria as needed
- [ ] Document edge cases
- [ ] Refine scoring thresholds

### Week 3: Full Rollout
- [ ] Apply to all new cards
- [ ] Process existing backlog through tier system
- [ ] Clear stale cards (> 10 days) first

### Week 4: Optimize
- [ ] Review auto-approval accuracy (false positives)
- [ ] Adjust thresholds based on outcomes
- [ ] Fine-tune batch schedule

---

## Success Metrics

| Metric | Current | Target (4 weeks) |
|--------|---------|------------------|
| Cards in backlog | ~130 | < 20 |
| Average card age | 4-7 days | < 3 days |
| Lucas approval time/week | ~12 hours | < 4 hours |
| Stale cards (> 7 days) | 16 | 0 |
| Auto-approval rate | 0% | 65% |
| Response rate (approved cards) | Baseline | Maintain or improve |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-auto-approval (bad messages sent) | Medium | High | 24-hour pull-back window; review samples weekly |
| Lucas misses important cards | Low | High | Tier 3 uses explicit notifications; stale cards auto-escalate |
| Team resistance to new criteria | Low | Medium | Pilot first; include team in calibration |
| Scoring too subjective | Medium | Medium | Use objective rubric; review edge cases together |
| Existing backlog delays rollout | High | Medium | Process backlog separately; apply to new cards immediately |

---

## Decision Required from Lucas

1. **Approve criteria for Tier 1 auto-approval?** (ICP definition, message score threshold)
2. **Confirm batch schedule?** (Monday/Thursday mornings suggested)
3. **Define tier-1 VC list?** (Top 50 firms for Tier 2 flagging)
4. **Choose notification method?** (Slack DM, email, or Trello mention)
5. **Assign implementation owner?** (Team member to own scoring/setup)

---

## Expected Outcome

Within 4 weeks:
- **Backlog cleared** from ~130 to < 20 cards
- **Lucas's approval time reduced** from ~12 hours to ~4 hours/week
- **Approval velocity matches** production velocity (no more compounding)
- **Stale cards eliminated** through auto-escalation
- **Lucas focuses** on strategic, high-value outreach

---

*Proposal prepared for Lucas review. Ready to implement upon approval.*
