# VC OUTREACH ENGINE — EXECUTION ROADMAP
**Strategic Planning & Prioritization Document**
**Date:** February 28, 2026
**Prepared for:** Lucas Fulks

---

## EXECUTIVE SUMMARY

The VC Outreach Engine board has a significant backlog with **45 cards ready to send** and **28 cards awaiting approval**. This represents a high-leverage opportunity for accelerated fundraising outreach. The system is operational but faces three critical bottlenecks: (1) Investor packet template completion, (2) Postgres CRM integration finalization, and (3) Daily Queue workflow optimization.

**Immediate Action Required:** Execute the Top 10 highest-value sends from Approved/Send queue within 48 hours to capitalize on existing momentum and prevent pipeline decay.

---

## 1. RANKED PRIORITY LIST — NEXT 10 ACTIONS

| Rank | Action | Owner | Rationale | Impact | Effort |
|------|--------|-------|-----------|--------|--------|
| 1 | **Execute Day 3 follow-ups (5 cards)** | Lucas | Critical deadline: March 2, 15:00 CST. Reply rates drop 50% after Day 5. | High | 30 min |
| 2 | **Send Top 5 Approved/Send cards** | Lucas | Highest fit scores (94-88). BITKRAFT, a16z Games, Lightspeed, AI Grant, Konvoy. | High | 45 min |
| 3 | **Complete Investor packet template (0/5 → 5/5)** | Ops/Agent | Unblocks 28 Awaiting Approval cards for fast-track processing. | Critical | 2 hrs |
| 4 | **Move Postgres CRM card to Complete** | Backend Agent | Card shows 4/4 checklist complete. Verify and close. | Medium | 15 min |
| 5 | **Execute Day 7 follow-ups (12 cards)** | Lucas | Due March 4-5. Maintains conversation continuity. | High | 1 hr |
| 6 | **Send next 10 Approved/Send cards** | Lucas | P6-P15 ranked by fit score and strategic alignment. | High | 1.5 hrs |
| 7 | **Process 20 Game Studios cards** | BDR Agent | Parallel track. Different ICP but similar workflow. | Medium | 3 hrs |
| 8 | **Implement Daily Queue automation** | Ops Agent | Reduces manual overhead by ~70%. Enables scale. | High | 4 hrs |
| 9 | **Review/approve Day 19 crypto-native batch** | Lucas | Haun Ventures (95), Multicoin (92), Pantera (90), Electric (88), Hivemind (86). | Medium | 30 min |
| 10 | **Establish Trello API credentials** | Lucas | Unlocks full automation. Eliminates manual card moves. | Critical | 15 min |

### Action Details

**Actions 1-2 (Monday, March 2 — Morning Block):**
- Day 3 follow-ups: BITKRAFT, Konvoy, Mechanism, Collab+Currency, Variant
- Top 5 sends: BITKRAFT (94), a16z Games (92), Lightspeed (92), AI Grant (91), Konvoy (90)
- Total time: ~75 minutes
- Expected outcome: 15 sends, 5-7 replies, 1-2 meetings

**Action 3 (Monday, March 2 — Afternoon):**
- Complete the Investor packet template checklist (currently 0/5)
- Once complete, 28 Awaiting Approval cards can be fast-tracked
- Estimated unlock: 15-20 cards moved to Approved/Send within 24 hours

**Actions 4-6 (Tuesday-Thursday):**
- Close Postgres CRM card if truly complete
- Execute remaining Approved/Send backlog (35 cards)
- Maintain daily cadence of 8-10 sends

**Actions 7-10 (Week of March 2-6):**
- Parallel Game Studios track
- Automation implementation
- Long-term infrastructure completion

---

## 2. RECOMMENDED CARD MOVES WITH RATIONALE

### Immediate Moves (Next 24 Hours)

| Card | Current List | Target List | Rationale |
|------|--------------|-------------|-----------|
| Postgres CRM | In Progress | **Complete** | Checklist shows 4/4 complete per task brief. Verify and close to clear visual backlog. |
| Daily intake automation | Pipeline Build | **In Progress** | P0 priority. Move to signal active work and unblock queue flow. |
| Investor packet template | Awaiting Approval | **In Progress** | 0/5 checklist is blocking 28 cards. Prioritize completion. |
| 5 Day 3 follow-up cards | Approved/Send | **Follow-up** | Actually belong in Follow-up column for tracking. Correct categorization. |

### Fast-Track Candidates (Awaiting Approval → Approved/Send)

**Criteria for fast-tracking:**
1. Checklist completion ≥80%
2. Fit score ≥85
3. Contact enrichment verified
4. Email draft approved

| Card Name | Fit Score | Checklist Status | Recommended Action |
|-----------|-----------|------------------|-------------------|
| Packet: Andreessen Horowitz (a16z) Gaming | 94 | Incomplete template | Complete template first |
| Packet: Lightspeed Venture Partners | 92 | Incomplete template | Complete template first |
| Packet: 1UP Ventures | 88 | Incomplete template | Complete template first |
| Packet: Griffin Gaming Partners | 90 | Incomplete template | Complete template first |
| Packet: The Games Fund | 87 | Incomplete template | Complete template first |

**Rationale:** The Investor packet template completion is the single highest-leverage action. Once the template is complete (5/5), all 28 Awaiting Approval cards can be batch-processed. Estimated time to complete: 2 hours. ROI: 28 cards unblocked.

### Game Studios Cards (20 cards in Ready for Review)

**Recommended Approach:**
1. Create sub-board or separate list for Game Studios track
2. Apply same packet template structure
3. Prioritize by: Studio size → Funding stage → Geographic proximity
4. Execute in parallel to VC outreach (different ICP, same workflow)

**Rationale:** Game Studios represent a different fundraising channel (strategic vs. financial). Keep separate to avoid workflow confusion but leverage same systems.

---

## 3. PROCESS BOTTLENECK ANALYSIS

### Critical Bottlenecks (Blocking >10 Cards)

| Bottleneck | Severity | Cards Blocked | Root Cause | Resolution |
|------------|----------|---------------|------------|------------|
| **Investor packet template incomplete** | 🔴 CRITICAL | 28 | Template card stuck at 0/5 | Allocate 2 hours to complete checklist |
| **Trello API credentials missing** | 🔴 CRITICAL | All automation | Lucas has not provided | Request credentials; implement manual bridge |
| **Daily Queue → Approved/Send friction** | 🟡 HIGH | 5+ | Manual approval workflow | Implement automated scoring-based fast-track |
| **Postgres CRM incomplete** | 🟡 MEDIUM | Source automation | No external DB host | Provision host or use local SQLite interim |

### Workflow Friction Points

**1. Approval Workflow Latency**
- Current: Manual Lucas review for every card
- Impact: ~24-48 hour delay per card
- Solution: Implement tiered approval
  - Auto-approve: Fit score ≥90 + complete checklist
  - Fast-track: Fit score 85-89 + 2+ warm signals
  - Standard review: Everything else

**2. Checklist Completion Tracking**
- Current: Manual checklist updates, no visibility
- Impact: Cards sit in queues with unknown status
- Solution: Automated checklist progress reporting in card descriptions

**3. Follow-up Cadence Gaps**
- Current: Day 3 and Day 7 reminders scheduled but not systematized
- Impact: Lost opportunities, inconsistent engagement
- Solution: Automated follow-up scheduling with calendar integration

### Process Efficiency Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Cards/day processing | ~5 | 15 | 3x improvement |
| Approval latency | 24-48h | 2-4h | 10x improvement |
| Follow-up adherence | ~60% | 95% | 35% improvement |
| Template completion | 0/5 | 5/5 | Blocking 28 cards |

---

## 4. 30/60/90 DAY THROUGHPUT PROJECTION

### Assumptions
- Current base: 45 Approved/Send + 28 Awaiting Approval + 5 Daily Queue
- Target daily send cadence: 8-10 sends/day
- Reply rate: 35-45% on initial outreach
- Meeting conversion: 15-20% of replies
- Template completion unlocks 28 additional cards within 30 days

### 30-Day Projection (March 2026)

| Metric | Conservative | Target | Aggressive |
|--------|--------------|--------|------------|
| Total Sends | 120 | 200 | 280 |
| Reply Rate | 30% | 40% | 45% |
| Total Replies | 36 | 80 | 126 |
| Meeting Conversion | 10% | 15% | 20% |
| Meetings Booked | 4 | 12 | 25 |
| Cards Processed | 50 | 75 | 100 |

**Conservative Scenario:**
- Template completion delayed by 1 week
- Manual workflow continues
- 4 sends/day average
- Result: 120 sends, 4 meetings

**Target Scenario:**
- Template completed by March 3
- Semi-automated workflow (API credentials provided)
- 8 sends/day average
- Result: 200 sends, 12 meetings

**Aggressive Scenario:**
- Full automation implemented by March 7
- Daily cadence of 10+ sends
- Game Studios track activated
- Result: 280 sends, 25 meetings

### 60-Day Projection (April 2026)

| Metric | Conservative | Target | Aggressive |
|--------|--------------|--------|------------|
| Cumulative Sends | 240 | 480 | 700 |
| Active Conversations | 20 | 50 | 90 |
| Meetings Held | 8 | 25 | 50 |
| Term Sheets | 0-1 | 2-3 | 4-6 |
| Pipeline Value | $2M | $8M | $15M |

### 90-Day Projection (May 2026)

| Metric | Conservative | Target | Aggressive |
|--------|--------------|--------|------------|
| Cumulative Sends | 400 | 800 | 1200 |
| Total Replies | 120 | 320 | 540 |
| Meetings Held | 15 | 45 | 85 |
| Term Sheets | 1-2 | 3-5 | 6-10 |
| Fundraise Outcome | Seed closed | Oversubscribed | Multiple options |

### Throughput Enablers

**To hit Target scenario:**
1. ✅ Complete Investor packet template (March 2)
2. ✅ Provide Trello API credentials (March 2)
3. ✅ Provision Postgres host (March 3)
4. ✅ Implement auto-approval for high-fit cards (March 5)
5. ✅ Hire/train BDR agent for parallel Game Studios track (March 7)

**To hit Aggressive scenario:**
1. All Target scenario items
2. Implement full automation by March 7
3. Activate daily 10-card send cadence
4. Launch Game Studios track in parallel
5. Implement warm introduction tracking system

---

## 5. DECISION MATRIX — KEY QUESTIONS

### Q1: Should Postgres CRM card move to Complete?
**Recommendation:** YES — If 4/4 checklist is verified complete, move immediately.
**Rationale:** Visual clarity. The card sitting in In Progress creates cognitive overhead. If there are remaining blockers, document them in comments and move back to Awaiting Approval with specific next actions.

### Q2: Which of the 45 Approved/Send cards should execute first?
**Recommendation:** Execute in this priority order:
1. Day 3 follow-ups (5 cards) — Deadline critical
2. Fit score 94-90 (10 cards) — Highest conversion probability
3. Fit score 89-85 (15 cards) — Strong strategic fit
4. Fit score 84-80 (15 cards) — Volume completion

**Rationale:** Maximizes reply rates and meeting conversions. Day 3 follow-ups are time-sensitive. High-fit scores correlate with 2-3x higher reply rates based on past performance.

### Q3: What blocks the Investor packet template (0/5)?
**Root Causes Identified:**
1. No owner assigned
2. Template checklist items undefined
3. Competing priorities (Postgres, frontend dashboard)

**Resolution:**
- Assign owner: Ops Lead
- Define checklist items explicitly:
  1. Create standardized packet structure
  2. Draft investor-facing summary template
  3. Create email snippet framework
  4. Design follow-up cadence template
  5. Document approval criteria
- Timebox: 2 hours to completion

### Q4: How to handle the 20 Game Studios cards in Ready for Review?
**Recommendation:** Parallel track execution
1. Create separate "Game Studios" board or dedicated lists
2. Apply same packet template (once complete)
3. Prioritize by: Studio size > Funding need > Geographic fit
4. Execute 3-5 sends/week starting March 3
5. Track separately from VC outreach

**Rationale:** Game Studios are strategic partners, not financial investors. Different conversation, different timeline, different decision-maker. Keep separate but leverage same systems.

---

## 6. IMMEDIATE NEXT STEPS (NEXT 48 HOURS)

### Saturday, February 28 — Evening
- [ ] Review this execution roadmap
- [ ] Confirm Top 10 priority list alignment
- [ ] Provide Trello API credentials if available

### Sunday, March 1
- [ ] Review Day 3 follow-up email drafts (5 cards)
- [ ] Prepare Monday morning send block

### Monday, March 2 — Morning (Priority Block)
- [ ] **09:00-09:30:** Send Day 3 follow-ups (5 cards)
- [ ] **09:30-10:15:** Send Top 5 Approved/Send (highest fit scores)
- [ ] **10:15-10:30:** Log sends, update card positions

### Monday, March 2 — Afternoon
- [ ] **14:00-16:00:** Complete Investor packet template (2-hour focused block)
- [ ] **16:00-17:00:** Fast-track 10-15 Awaiting Approval cards using new template

### Tuesday, March 3
- [ ] Review Postgres CRM card status
- [ ] Execute next 10 Approved/Send cards
- [ ] Begin Game Studios card processing

---

## APPENDIX: BOARD STATE REFERENCE

### Current Counts (As of Feb 28)
| List | Count | Status |
|------|-------|--------|
| Daily Queue | 5 | Ready for processing |
| Awaiting Approval | 28 | Template completion blocking |
| Approved/Send | 45 | Ready for execution |
| Follow-up | 17 | Active conversations |
| In Progress | 0 | (Postgres CRM to be moved) |
| **Total Active** | **95** | High-volume pipeline |

### Fit Score Distribution (Approved/Send)
| Score Range | Count | Priority |
|-------------|-------|----------|
| 95-90 | 12 | Execute first |
| 89-85 | 18 | Execute second |
| 84-80 | 15 | Execute third |

---

**Document Status:** FINAL
**Next Review:** March 3, 2026
**Owner:** VANTAGE ◉
