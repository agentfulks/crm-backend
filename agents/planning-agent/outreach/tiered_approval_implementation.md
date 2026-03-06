# Tiered Approval System — Implementation Spec

**Version:** 1.0  
**Created:** 2026-03-05  
**Owner:** Lucas  
**Target:** Reduce approval time from ~12hrs/week to ~4hrs/week  

---

## Executive Summary

This document provides an executable implementation plan for a 3-tier approval system to process Lucas's outreach backlog:
- **47 VC cards** + **103 BDR cards** = **150 total**
- **Tier 1 (60-70%):** Auto-approve — no Lucas time required
- **Tier 2 (25-30%):** Batch review 2x/week — ~30 min per session
- **Tier 3 (<10%):** Individual review — only high-stakes exceptions

---

## 1. Tier Classification Rules

### 1.1 VC Card Classification

#### Tier 1: Auto-Approve (Target: 65-70% of VCs)
**Must meet ALL of these criteria:**

| Criterion | Threshold/Condition |
|-----------|---------------------|
| Fund Size | <$300M AUM |
| Check Size | <$100K or >$2M (outside sweet spot) |
| Stage Focus | Seed/Series A only (we're pre-seed) |
| Geographic | Outside target markets (non-US, non-EU Tier 1) |
| Warm Path | No identifiable mutual connection |
| Response History | Previous outreach: 0 replies or auto-decline |
| Partner Accessibility | No partner email available (only info@/contact form) |

**Qualitative Flags (auto-Tier 1):**
- Description mentions "growth equity" or "late stage only"
- Portfolio is 100% SaaS enterprise (we're gaming)
- Recent fund announcements indicate mega-fund ($500M+) pivot

#### Tier 2: Batch Review (Target: 25-30% of VCs)
**Any of these criteria:**

| Criterion | Condition |
|-----------|-----------|
| Fund Size | $100M-$300M AUM |
| Check Size | $100K-$500K (in range but not ideal) |
| Stage Fit | Pre-seed + Seed (partial fit) |
| Geographic | Secondary US markets (Austin, Denver, etc.) |
| Warm Path | 2nd-degree connection exists (needs path assessment) |
| Partner Accessibility | Has partner email but partner is junior/associate |
| Strategic Value | Gaming-adjacent portfolio (media, entertainment tech) |
| Signal | Recent investment in similar space (12-18 months ago) |

#### Tier 3: Individual Review (Target: <10% of VCs)
**Any of these criteria (high-touch required):**

| Criterion | Condition |
|-----------|-----------|
| Fund Size | Gaming-focused micro-VC or <$100M sector fund |
| Check Size | $250K-$1M (ideal range) |
| Partner Relationship | Direct 1st-degree connection OR warm intro from portfolio founder |
| Strategic Value | Tier 1 gaming fund (a16z games, Lightspeed, etc.) |
| Competitive Intel | Recently funded direct competitor |
| Timing | Fund just announced (last 6 months) or partner just joined |
| Referral | Warm intro explicitly requested by partner |

---

### 1.2 BDR Card Classification

#### Tier 1: Auto-Approve (Target: 60% of BDRs)
**Must meet ALL of these criteria:**

| Criterion | Threshold/Condition |
|-----------|---------------------|
| Studio Size | 50+ employees (too large, slow decision-making) |
| Publisher Type | AAA publisher (out of scope for indie outreach) |
| Recent Releases | 3+ shipped titles in last 2 years (not hungry) |
| Reply History | 2+ previous BDR attempts with no reply |
| Strategic Fit | No portfolio overlap or co-dev interest |
| Contact Quality | Generic bizdev@ email only (no named contact) |
| Geographic | Non-English speaking market (unless localized) |

**Qualitative Flags (auto-Tier 1):**
- Studio description emphasizes "internal IP only" 
- Recent M&A activity suggests not partnering
- Leadership change in last 6 months (instability)

#### Tier 2: Batch Review (Target: 30-35% of BDRs)
**Any of these criteria:**

| Criterion | Condition |
|-----------|-----------|
| Studio Size | 10-50 employees |
| Game Portfolio | 1-2 released titles (proven but growing) |
| Reply History | 1 previous attempt with no reply |
| Strategic Fit | Portfolio has 1 similar game (tangential fit) |
| Timing | Just announced new project or hiring spree |
| Event Connection | Both attending same upcoming conference |
| Referral Source | Mutual LinkedIn connection exists |

#### Tier 3: Individual Review (Target: <10% of BDRs)
**Any of these criteria (high-touch required):**

| Criterion | Condition |
|-----------|-----------|
| Studio Size | <15 employees (ideal indie size) |
| Game Fit | Portfolio contains direct genre match |
| Warm Intro | Founder/CMO introduced by mutual contact |
| Engagement | Previously replied to outreach (even if declined) |
| Competitive | Currently working with competitor (time-sensitive) |
| Signal | Recently tweeted about seeking partners/projects |
| Portfolio Value | Could become a case study or reference customer |

---

## 2. Auto-Approval Criteria (Tier 1 Deep Dive)

### 2.1 VC Tier 1 Decision Matrix

**Hard Disqualifiers (any one = Tier 1 auto-approve):**
1. AUM > $500M AND no gaming investments
2. Check size minimum > $250K
3. Explicitly "Series A+ only" in description
4. Zero gaming/entertainment in portfolio
5. Info@ email + no partner names on website
6. Geographic = Asia-Pacific (unless specific gaming focus)
7. Response to previous outreach = "not investing in gaming"

**Safe Auto-Approvals (meet 4+ of these):**
1. Fund size < $150M
2. Check size outside $100K-$1M range
3. No warm intro path after LinkedIn check
4. Portfolio is 100% SaaS/fintech/healthcare
5. Last fund raised > 4 years ago (likely not actively deploying)
6. Partners have no Twitter/LinkedIn presence (hard to research)

### 2.2 BDR Tier 1 Decision Matrix

**Hard Disqualifiers (any one = Tier 1 auto-approve):**
1. Employee count > 200
2. Recent acquisition by major publisher
3. Bizdev contact = generic careers@ or info@
4. Previous 3+ BDR emails with zero reply
5. Public statements: "not seeking external projects"
6. All recent releases = licensed IP (won't take original)
7. Geographic timezone > 8 hours offset (no overlap)

**Safe Auto-Approvals (meet 4+ of these):**
1. Studio size 50-200 (too big for our target)
2. No portfolio overlap with our genre
3. Recent releases got mediocre reviews (not our quality tier)
4. Leadership = ex-AAA with no indie experience
5. No social media activity in last 6 months
6. Website hasn't been updated in 2+ years

---

## 3. Batch Review Process (Tier 2)

### 3.1 Cadence & Schedule

| Parameter | Setting |
|-----------|---------|
| Review Days | Tuesday + Thursday |
| Time Block | 10:00-10:30 AM (fixed 30-min window) |
| Max Cards per Session | 20 cards |
| Decision Time per Card | 90 seconds average |

**Why Tuesday/Thursday:**
- Monday = catch-up day, Friday = wind-down
- Mid-week = optimal energy for batch decisions
- Creates 2-3 day buffer between reviews (prevents decision fatigue pile-up)

### 3.2 Pre-Session Prep (5 minutes)

**Before the 30-min block:**
1. Cards are pre-sorted by Trello (auto-labeled Tier 2)
2. Sort order: Oldest first (FIFO to prevent stagnation)
3. Slack/email on Do Not Disturb
4. Open Trello board in dedicated browser tab

### 3.3 Decision Framework

For each Tier 2 card, decide in **90 seconds or less:**

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 2 DECISION TREE (90 seconds max)                      │
├─────────────────────────────────────────────────────────────┤
│  Q1: Can I find a warm intro in <30s LinkedIn search?       │
│      YES → Move to Tier 3 (high-potential, needs research)  │
│      NO  → Continue to Q2                                   │
│                                                             │
│  Q2: Does this fit our "stretch but possible" criteria?     │
│      YES → Approve (send to outreach queue)                 │
│      MAYBE → Modify (add note, change message, re-tier)     │
│      NO  → Reject (remove from queue)                       │
│                                                             │
│  Q3: Is there ANY scenario where this is worth individual   │
│      review time (i.e., could be Tier 3)?                   │
│      YES → Move to Tier 3                                   │
│      NO  → Batch decision stands                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Batch Review Actions

| Action | Trello Operation | Outcome |
|--------|------------------|---------|
| **Approve** | Move to "Approved - Send" | Card goes to outreach queue |
| **Reject** | Move to "Rejected - Archive" | Card archived with reason tag |
| **Modify** | Add comment + keep in Tier 2 | Re-reviewed next session |
| **Escalate** | Move to "Tier 3 - Manual Review" | Gets individual attention |

### 3.5 Escalation Triggers (Tier 2 → Tier 3)

Auto-escalate if:
- Fund/studio is in stealth mode (limited info = unknown risk)
- Personal connection discovered during 30s search
- Check size/message fit is ambiguous
- Competitive intelligence suggests urgency
- Response received to previous outreach (any reply = Tier 3)

---

## 4. Implementation Checklist

### 4.1 Phase 1: Setup (Day 1 - Today)

**Trello Board Configuration:**

| Step | Action | Trello How-To |
|------|--------|---------------|
| 1 | Create 3 new lists | Board → Add List: "Tier 1 - Auto-Approve", "Tier 2 - Batch Review", "Tier 3 - Manual Review" |
| 2 | Create Tier labels | Labels → Create: "Tier-1", "Tier-2", "Tier-3" (use colors: green, yellow, red) |
| 3 | Add decision labels | Labels → Create: "Approved", "Rejected", "Needs-Modification" |
| 4 | Enable Butler automation | Power-Ups → Butler → Enable |

**Label Color Coding:**
- Tier-1 = Green
- Tier-2 = Yellow
- Tier-3 = Red
- Approved = Dark Green
- Rejected = Gray
- Needs-Modification = Orange

### 4.2 Phase 2: Automation Rules (Day 1-2)

**Butler Automation Rules to Create:**

**Rule 1: Auto-Move Tier 1 to Send Queue**
```
When the "Tier-1" label is added to a card,
move the card to list "Tier 1 - Auto-Approve",
and add the "Approved" label
```

**Rule 2: Tier 2 Staging**
```
When the "Tier-2" label is added to a card,
move the card to list "Tier 2 - Batch Review",
and sort the list by date created (oldest first)
```

**Rule 3: Tier 3 Flagging**
```
When the "Tier-3" label is added to a card,
move the card to list "Tier 3 - Manual Review",
and add a red sticker to the card
```

**Rule 4: Archive Rejected**
```
When the "Rejected" label is added to a card,
archive the card
```

**Note:** If Butler is not available, these become **manual processes** (see 4.3).

### 4.3 Phase 3: Manual Fallback Process (If Automation Unavailable)

**If Trello Butler is unavailable or limited:**

| Process | Manual Workflow |
|---------|-----------------|
| Tier Classification | Use spreadsheet template (see Appendix A) → import to Trello as batch |
| Card Movement | Keyboard shortcut: `,` then type list name |
| Label Application | Keyboard: `l` then type label name |
| Sorting | List → ... → Sort by Date Created |
| Archiving | Card → Archive or `c` shortcut |

**Spreadsheet Classification Template:**
| Card ID | Card Name | Type (VC/BDR) | Fund Size/Studio Size | Warm Path? | Tier | Action |
|---------|-----------|---------------|----------------------|------------|------|--------|
| TBD | TBD | VC/BDR | Number | Y/N/Partial | 1/2/3 | Approve/Reject/Review |

### 4.4 Phase 4: Backlog Classification (Day 1-3)

**Current Backlog:** 150 cards (47 VC + 103 BDR)

| Step | Action | Time Estimate | Owner |
|------|--------|---------------|-------|
| 1 | Export current Trello board to CSV | 10 min | Lucas |
| 2 | Apply classification rules (spreadsheet) | 2-3 hours | Lucas |
| 3 | Import classified cards with labels | 30 min | Lucas |
| 4 | Spot-check 20 random cards for accuracy | 20 min | Lucas |
| 5 | Adjust criteria based on edge cases found | 20 min | Lucas |

**Classification Speed Target:**
- VC cards: ~3 min/card (needs more research) = 2.5 hours
- BDR cards: ~1 min/card (faster pattern-matching) = 1.5 hours
- **Total initial classification time: ~4 hours** (one focused session)

### 4.5 Phase 5: Metrics Tracking (Ongoing)

**Weekly Metrics Dashboard:**

| Metric | How to Track | Target |
|--------|--------------|--------|
| Approval Velocity | Cards moved from "Batch Review" → "Approved" per week | 15-20 cards |
| Reply Rate by Tier | Response rate for Tier 1 vs Tier 2 vs Tier 3 | Tier 3 > Tier 2 > Tier 1 |
| Time per Approval | Track time spent in batch reviews | <30 min per session |
| Tier Distribution | % of cards in each tier | 65/25/10 split |
| Escalation Rate | Tier 2 → Tier 3 moves | <15% of Tier 2 |

**Trello Metric Tracking:**
- Create a "Metrics" list
- Weekly card: "Week of [Date] - Metrics"
- Comment on card with:
  - Cards processed: X
  - Time spent: Y hours
  - Reply rate: Z%
  - Notes on adjustments needed

---

## 5. Immediate Action Items (Do Today)

### 5.1 Within Next Hour (Setup)

- [ ] Create the 3 Tier lists in Trello (Tier 1 - Auto-Approve, Tier 2 - Batch Review, Tier 3 - Manual Review)
- [ ] Create Tier labels (Tier-1, Tier-2, Tier-3 with green/yellow/red colors)
- [ ] Export current board to CSV for classification
- [ ] Set calendar block: Tuesdays + Thursdays 10:00-10:30 AM (Batch Review)

### 5.2 Today (Classification Sprint)

- [ ] **VC Classification (47 cards):** 
  - Sort by fund size (largest first)
  - Quick scan for obvious Tier 1s (>$500M, no gaming) = ~15 min
  - Identify obvious Tier 3s (gaming micro-VCs, warm connections) = ~15 min
  - Rest default to Tier 2 = ~30 min
  - **Total: 1 hour**

- [ ] **BDR Classification (103 cards):**
  - Sort by employee count
  - Batch-classify 50+ employee studios as Tier 1 = ~20 min
  - Identify <15 employee, portfolio-matched as Tier 3 = ~20 min
  - Rest default to Tier 2 = ~20 min
  - **Total: 1 hour**

- [ ] Apply labels to classified cards (use spreadsheet or manual in Trello) = ~30 min

### 5.3 This Week (Operationalize)

- [ ] First batch review session: Thursday 10:00 AM (process 15-20 Tier 2 cards)
- [ ] Set up Butler automation rules (or document manual process)
- [ ] Create metrics tracking card for Week 1
- [ ] After 1 week: review reply rates, adjust criteria if needed

### 5.4 Expected Immediate Impact

| Metric | Before | After (Week 1) |
|--------|--------|----------------|
| Cards needing review | 150 | ~40 (Tier 3) + ~35/session (Tier 2) |
| Weekly review time | ~12 hours | ~2 hours |
| Mental overhead | High (decision fatigue) | Low (clear rules) |
| Approval latency | Days/weeks | Hours (Tier 1), Days (Tier 2) |

**Week 1 Goal:**
- Clear 100+ cards from mental queue via Tier 1 auto-approval
- Process 30-40 Tier 2 cards through batch review
- Reduce active "needs attention" pile from 150 to <50

---

## Appendix A: Classification Spreadsheet Template

```
A: Card Name
B: Card URL (Trello link)
C: Type (VC/BDR)
D: Fund Size / Studio Size
E: Stage Fit / Game Fit (Y/N/Maybe)
F: Warm Path Exists (Y/N/Partial)
G: Partner/Contact Quality (High/Med/Low)
H: Geographic (US-Tier1/US-Tier2/EU/Asia/Other)
I: Previous Outreach (0/1/2+ replies)
J: Strategic Value (High/Med/Low)
K: TIER (1/2/3)
L: Rationale (brief)
M: Action (Approve/Reject/Escalate)
```

**Quick Sort Strategy:**
1. Sort by Column D (Fund/Studio Size) — largest = likely Tier 1
2. Sort by Column F (Warm Path) — Yes = likely Tier 3
3. Sort by Column E (Fit) — No = likely Tier 1
4. Everything else = Tier 2

---

## Appendix B: Decision Cheat Sheet (Print Me)

```
┌────────────────────────────────────────────────────────────┐
│ VC TIER CLASSIFICATION — 30 SECOND CHECK                   │
├────────────────────────────────────────────────────────────┤
│ □ Fund > $500M + No gaming? → TIER 1                       │
│ □ Warm intro path exists? → TIER 3                         │
│ □ Gaming micro-VC + ideal check size? → TIER 3             │
│ □ Info@ only + no partner names? → TIER 1                  │
│ □ Check size $100K-$500K + partial fit? → TIER 2           │
│ □ Otherwise? → TIER 2                                      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ BDR TIER CLASSIFICATION — 30 SECOND CHECK                  │
├────────────────────────────────────────────────────────────┤
│ □ 50+ employees? → TIER 1                                  │
│ □ Warm intro exists? → TIER 3                              │
│ □ <15 employees + genre match? → TIER 3                    │
│ □ 3+ previous attempts, no reply? → TIER 1                 │
│ □ 10-50 employees + tangential fit? → TIER 2               │
│ □ Otherwise? → TIER 2                                      │
└────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

This implementation is successful when:
1. ✅ 60-70% of incoming cards are auto-classified as Tier 1
2. ✅ Batch reviews take ≤30 minutes, 2x per week
3. ✅ <10% of cards require individual review
4. ✅ Lucas's weekly approval time drops from ~12hrs to ~4hrs
5. ✅ Reply rates remain stable or improve (quality over quantity)
6. ✅ No card sits in backlog >7 days without classification

---

**Questions? Edge cases?** Update this doc with lessons learned after Week 1.
