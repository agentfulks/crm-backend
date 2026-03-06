# Source Automation v1 - Implementation Plan
**Document Type:** Technical Implementation Plan  
**Last Updated:** 2026-02-25  
**Status:** Ready for Implementation  
**Author:** PLANNING-LEAD

---

## 1. Executive Summary

This document outlines the implementation plan for Source Automation v1, which automates the ingestion, deduplication, and daily queue population of VC targets. The system ensures ≥5 new VC packets are queued daily while maintaining data quality and minimizing manual intervention.

**Goal:** Fully automated daily pipeline from raw sources to Trello Daily Queue.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│ CSV Uploads │ Crunchbase  │ OpenVC API  │ Manual Entries        │
│ Dealroom    │ PitchBook   │ LinkedIn    │ Partner Referrals     │
└──────┬──────┴──────┬──────┴──────┬──────┴───────────┬───────────┘
       │             │             │                  │
       └─────────────┴─────────────┴──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  INGESTION  │  ← ingest_funds.py
                    │   SERVICE   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ DEDUPE &    │  ← dedupe_funds.py
                    │  ENRICH     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   SCORING   │  ← rank_funds.py
                    │   ENGINE    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    CRM      │  ← PostgreSQL
                    │   DATABASE  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    DAILY    │  ← daily_queue.py
                    │    QUEUE    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   TRELLO    │  ← trello_client.py
                    │   CARDS     │
                    └─────────────┘
```

---

## 3. Component Specifications

### 3.1 Ingestion Service (ingest_funds.py)

**Purpose:** Normalize and validate incoming fund data from multiple sources.

**Inputs:**
- CSV files (gaming_vc_list.csv format)
- API responses (Crunchbase, OpenVC)
- Manual entry forms

**Outputs:**
- Normalized FundRecord objects
- Validation reports
- Error logs

**Key Functions:**
```python
async def ingest_from_csv(file_path: str) -> List[FundRecord]
async def ingest_from_api(source: str, params: dict) -> List[FundRecord]
async def validate_fund_record(record: FundRecord) -> ValidationResult
```

**Implementation Status:** Partially Complete (70%)
- CSV ingestion: ✅ Complete
- API ingestion: ⬜ Pending (need API keys)
- Validation: ✅ Complete

---

### 3.2 Deduplication Engine (dedupe_funds.py)

**Purpose:** Identify and merge duplicate fund records across sources.

**Matching Criteria:**
1. Exact name match (normalized)
2. Website domain match
3. LinkedIn company URL match
4. Fuzzy name matching (80%+ similarity)

**Merge Strategy:**
- Most recent data wins
- Non-empty fields preferred
- Manual entries override automated
- Audit trail preserved

**Key Functions:**
```python
def find_duplicates(funds: List[FundRecord]) -> List[DuplicateGroup]
def merge_funds(group: DuplicateGroup) -> FundRecord
def calculate_match_score(fund1: FundRecord, fund2: FundRecord) -> float
```

**Implementation Status:** Not Started (0%)

**QA Sample Size:** 20 entries for initial validation

---

### 3.3 Scoring Engine (rank_funds.py)

**Purpose:** Calculate priority scores for all funds (see scoring_model_framework.md).

**Implementation Status:** Complete (90%)
- Scoring algorithm: ✅ Complete
- CLI interface: ✅ Complete
- API endpoint: ⬜ Pending (/api/funds/top)

---

### 3.4 Daily Queue Generator (daily_queue.py)

**Purpose:** Select top 5 funds for daily outreach and create Trello cards.

**Selection Logic:**
1. Query funds with score ≥75
2. Exclude funds contacted in last 30 days
3. Exclude funds in active pipeline
4. Sort by score descending
5. Select top 5
6. Mark as "queued"

**Key Functions:**
```python
async def generate_daily_queue(count: int = 5) -> List[Fund]
async def mark_as_queued(fund_ids: List[int])
async def get_queue_eligible_funds() -> List[Fund]
```

**Implementation Status:** Partially Complete (40%)

---

### 3.5 Trello Integration (trello_client.py)

**Purpose:** Create and manage Trello cards for daily queue.

**Card Template:**
```
Title: [INVESTOR] {Fund Name} - {Score}/100
Description:
- Fund: {Name}
- Score: {Score}
- Stage: {Stage Focus}
- Check Size: {Check Range}
- Contact: {Primary Contact}
- Packet: {Link to investor packet}

Checklist:
□ Contact enriched
□ Packet created
□ Approved for send
□ Outreach sent
□ Response logged
```

**Implementation Status:** Blocked (0%)
- Blocker: Trello API credentials needed
- Card creation: ⬜ Pending
- List management: ⬜ Pending

---

## 4. Implementation Timeline

### Phase 1: Core Pipeline (Week 1)
| Task | Owner | Status | ETA |
|------|-------|--------|-----|
| Complete dedupe logic | Backend | ⬜ | Day 2 |
| Daily queue generator | Backend | ⬜ | Day 3 |
| Trello API integration | Backend | ⬜ | Day 4 |
| End-to-end test | QA | ⬜ | Day 5 |

### Phase 2: Automation (Week 2)
| Task | Owner | Status | ETA |
|------|-------|--------|-----|
| Schedule daily runs (cron) | DevOps | ⬜ | Day 1 |
| Monitoring & alerting | DevOps | ⬜ | Day 2 |
| Error handling & retries | Backend | ⬜ | Day 3 |
| QA sample validation (20 entries) | QA | ⬜ | Day 5 |

### Phase 3: Integration (Week 3)
| Task | Owner | Status | ETA |
|------|-------|--------|-----|
| API endpoint for top funds | Backend | ⬜ | Day 2 |
| Frontend integration | Frontend | ⬜ | Day 4 |
| Production deployment | DevOps | ⬜ | Day 5 |

---

## 5. Daily Run Schedule

```cron
# Daily queue generation - 6:00 AM CST
0 6 * * * cd /app && uv run python scripts/daily_queue.py --create-cards

# Scoring refresh - 5:00 AM CST (before queue gen)
0 5 * * * cd /app && uv run python scripts/rank_funds.py --refresh

# Data ingestion (weekly) - Sundays at 4:00 AM CST
0 4 * * 0 cd /app && uv run python scripts/ingest_funds.py --source=all
```

---

## 6. QA Sample Validation

### Sample Selection Criteria
- 5 high-score funds (≥85)
- 10 medium-score funds (70-84)
- 5 low-score funds (<70)

### Validation Checklist
| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Data accuracy | Manual verification | 100% correct |
| Deduplication | Cross-reference sources | 0 duplicates |
| Contact quality | Email validation | 80% deliverable |
| Score consistency | Manual re-scoring | ±5 points |
| Card creation | Trello verification | 100% created |

---

## 7. Error Handling

| Error Type | Handling Strategy | Alert |
|------------|-------------------|-------|
| Source API failure | Retry 3x, use cached data | Slack |
| Duplicate detection failure | Log for manual review | Email |
| Trello API failure | Queue for retry | Slack |
| <5 funds in queue | Alert + manual intervention | Slack + Email |
| Scoring failure | Use last known score | Log only |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily queue size | ≥5 funds | Daily count |
| Data freshness | <7 days | Average age |
| Duplicate rate | <2% | Records / unique funds |
| Queue generation success | >99% | Uptime |
| QA sample pass rate | 100% | Per validation |
| Trello card creation | 100% | Cards created / funds queued |

---

## 9. Blockers & Dependencies

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Trello API credentials | Cannot create cards | Lucas to provide |
| PostgreSQL hosting | Cannot persist data | Infrastructure pending |
| Crunchbase API key | Limited enrichment | Evaluate cost/benefit |
| LinkedIn API access | Contact enrichment blocked | Alternative sources |

---

## 10. Next Actions

### Immediate (This Week)
1. [ ] Obtain Trello API credentials from Lucas
2. [ ] Complete deduplication engine implementation
3. [ ] Build daily queue generator
4. [ ] Create QA validation script

### Short Term (Next 2 Weeks)
1. [ ] Complete Trello integration
2. [ ] Schedule automated runs
3. [ ] Validate QA sample of 20 entries
4. [ ] Deploy to production

### Medium Term (Month 2)
1. [ ] Add API data sources
2. [ ] Implement contact enrichment automation
3. [ ] Build monitoring dashboard
4. [ ] Optimize scoring based on response data
