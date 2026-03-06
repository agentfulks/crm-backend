# VC Scoring Model Framework v1.0
**Document Type:** Framework Specification  
**Last Updated:** 2026-02-25  
**Status:** Draft for Review  
**Author:** PLANNING-LEAD

---

## 1. Executive Summary

This document defines the standardized scoring model for prioritizing VC targets in the outreach engine. The model produces a 0-100 score based on 6 weighted factors that measure strategic fit, accessibility, and readiness for outreach.

**Purpose:** Ensure objective, reproducible prioritization of VC targets to maximize daily queue quality.

---

## 2. Scoring Factors & Weights

| Factor | Weight | Max Points | Description |
|--------|--------|------------|-------------|
| **Sector Fit** | 25% | 25 | Alignment with gaming/AI/devtools focus |
| **Stage Fit** | 25% | 25 | Investment stage overlap with target ($0.5-5M) |
| **Check Size Fit** | 15% | 15 | Check size range compatibility |
| **Geo Fit** | 10% | 10 | Geographic alignment and accessibility |
| **Warmth/Strategic** | 15% | 15 | Reputation, network proximity, warm paths |
| **Contact Readiness** | 10% | 10 | Availability of decision-maker contacts |
| **Data Freshness** | -5 | -5 | Penalty for incomplete/outdated records |

**Total Score Range:** 0-100 (clamped)

---

## 3. Factor Definitions

### 3.1 Sector Fit (25 points)

| Criteria | Points |
|----------|--------|
| Pure-play gaming fund | 25 |
| Gaming + adjacent (esports, interactive) | 22 |
| Gaming + broader entertainment | 18 |
| Gaming + tech/infrastructure | 20 |
| AI/devtools focus with gaming application | 18 |
| Generalist with gaming thesis | 12 |
| No gaming focus | 0-5 |

**Keywords for auto-scoring:**
- gaming, game, interactive, esports, immersive, XR
- AI, artificial intelligence, machine learning
- devtools, developer tools, infrastructure
- metaverse, web3, blockchain (gaming context)

### 3.2 Stage Fit (25 points)

| Investment Stage | Points |
|------------------|--------|
| Pre-Seed focus | 25 |
| Pre-Seed + Seed | 24 |
| Seed focus | 23 |
| Seed + Series A | 22 |
| Series A focus | 18 |
| Series A + Series B | 15 |
| Series B+ focus | 10 |
| Multi-stage (all) | 12-20 (scaled) |

### 3.3 Check Size Fit (15 points)

Target range: $500K - $5M

| Overlap | Points |
|---------|--------|
| Full overlap ($500K-5M) | 15 |
| 75-99% overlap | 12 |
| 50-74% overlap | 9 |
| 25-49% overlap | 6 |
| <25% overlap | 3 |
| Unknown | 5 |

### 3.4 Geo Fit (10 points)

| Criteria | Points |
|----------|--------|
| US/Canada HQ | 10 |
| UK HQ | 9 |
| EU Tier 1 (DE, FR, NL, SE, FI, DK, ES, PT) | 7 |
| EU Tier 2 | 5 |
| Asia (Singapore, Japan, South Korea) | 6 |
| Other global with US investments | 5 |
| Local-only focus (non-target market) | 2 |

### 3.5 Warmth/Strategic (15 points)

| Criteria | Points |
|----------|--------|
| Direct connection/warm intro available | 15 |
| Portfolio company founder intro | 12 |
| Shared investor connection | 10 |
| Industry reputation (Tier 1) | 12 |
| Industry reputation (Tier 2) | 8 |
| Emerging fund with strong team | 6 |
| No known connections | 0-5 |

**Tier 1 Gaming Funds:** BITKRAFT, Griffin, Makers Fund, a16z, Lightspeed (gaming)

### 3.6 Contact Readiness (10 points)

| Criteria | Points |
|----------|--------|
| Direct partner email confirmed | 10 |
| General fund email + partner LinkedIn | 7 |
| General fund email only | 5 |
| LinkedIn only (no email) | 4 |
| Contact info unknown | 2 |

### 3.7 Data Freshness Penalty (-5 points)

| Issue | Penalty |
|-------|---------|
| Missing stage AND check size AND contact | -5 |
| Missing 2 of 3 critical fields | -3 |
| Missing 1 critical field | -1 |
| Data >12 months old | -2 |

---

## 4. Score Interpretation

| Score Range | Priority | Action |
|-------------|----------|--------|
| 90-100 | P0 | Immediate outreach, highest priority |
| 80-89 | P1 | Add to daily queue, standard outreach |
| 70-79 | P2 | Secondary queue, outreach as capacity allows |
| 60-69 | P3 | Tertiary queue, monitor for updates |
| <60 | Deprioritized | Do not outreach unless strategic reason |

---

## 5. Implementation

### 5.1 Database Schema

```sql
CREATE TABLE fund_scores (
    id SERIAL PRIMARY KEY,
    fund_id INTEGER REFERENCES funds(id),
    total_score DECIMAL(4,1),
    sector_fit INTEGER,
    stage_fit INTEGER,
    check_size_fit INTEGER,
    geo_fit INTEGER,
    warmth_score INTEGER,
    contact_readiness INTEGER,
    freshness_penalty INTEGER,
    breakdown JSONB,
    calculated_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Calculation Logic

```python
def calculate_fund_score(fund: FundRecord) -> FundScore:
    """
    Calculate comprehensive fund score.
    """
    sector_fit = score_sector_fit(fund.thesis)
    stage_fit = score_stage_fit(fund.stage_focus)
    check_size_fit = score_check_size_overlap(fund.check_min, fund.check_max)
    geo_fit = score_geo_fit(fund.hq_country, fund.target_countries)
    warmth = score_warmth(fund.name, fund.connections)
    contact_readiness = score_contact_readiness(fund.contacts)
    freshness_penalty = calculate_freshness_penalty(fund)
    
    total = (
        sector_fit +
        stage_fit +
        check_size_fit +
        geo_fit +
        warmth +
        contact_readiness +
        freshness_penalty
    )
    
    return FundScore(
        total_score=max(0, min(100, total)),
        breakdown={
            "sector_fit": sector_fit,
            "stage_fit": stage_fit,
            "check_size_fit": check_size_fit,
            "geo_fit": geo_fit,
            "warmth": warmth,
            "contact_readiness": contact_readiness,
            "freshness_penalty": freshness_penalty
        }
    )
```

### 5.3 API Endpoint

```
GET /api/funds/top?limit=5&min_score=75&sector=gaming

Response:
{
  "funds": [
    {
      "id": 1,
      "name": "BITKRAFT Ventures",
      "total_score": 91.2,
      "breakdown": {...},
      "priority": "P1"
    }
  ]
}
```

---

## 6. Backfill Strategy

### Existing Records
All existing funds in CRM should be scored using this framework:

1. **Batch Score:** Run scoring script on all existing funds
2. **Review Thresholds:** Manually review scores 70-85 for accuracy
3. **Update Queues:** Re-prioritize based on new scores
4. **Audit Log:** Record score history and manual overrides

### Timeline
- **Day 1:** Run batch scoring on existing database
- **Day 2:** Manual review of borderline cases (score 70-85)
- **Day 3:** Update daily queue priorities
- **Ongoing:** Auto-score new funds on ingestion

---

## 7. Maintenance & Updates

### Regular Reviews
- **Monthly:** Review score distribution and adjust weights if needed
- **Quarterly:** Validate keyword lists against industry trends
- **Annually:** Comprehensive model review with performance data

### Override Policy
Manual score overrides allowed for:
- Strategic relationship opportunities
- Time-sensitive market opportunities
- Warm introduction availability

All overrides logged to `score_override_log` table.

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Average queue score | >80 |
| Score calculation time | <100ms per fund |
| Manual override rate | <10% |
| Queue refresh frequency | Daily |
| Response rate by tier | P1 >15%, P2 >10% |

---

## 9. Appendix: Current Top Scores (Sample)

| Rank | Fund | Score | Priority |
|------|------|-------|----------|
| 1 | BITKRAFT Ventures | 91.2 | P0 |
| 2 | Konvoy Ventures | 88.4 | P1 |
| 3 | Griffin Gaming Partners | 88.5 | P1 |
| 4 | The Games Fund | 86.0 | P1 |
| 5 | Makers Fund | 85.5 | P1 |
| 6 | Variant | 84.6 | P2 |
| 7 | Hiro Capital | 84.5 | P2 |
| 8 | Collab+Currency | 82.0 | P2 |
| 9 | Transcend Fund | 83.0 | P2 |
| 10 | Mechanism Capital | 79.5 | P3 |
