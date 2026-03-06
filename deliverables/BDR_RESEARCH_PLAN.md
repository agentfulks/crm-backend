# BDR Studio Research Continuation Plan

**Date:** March 3, 2026  
**Scope:** 36 studios in Research Queue  
**Target:** 10 studios/day (3.6 days to clear backlog)  
**Context:** Previous BDR_STRATEGIST timed out after 4 minutes — need resilient batch execution

---

## 1. Research Priority Framework

### Tiering Logic (Applied Before Research Begins)

**Priority Order for Processing Queue:**

| Priority | Criteria | Rationale |
|----------|----------|-----------|
| **P0** | Studios with recent funding news (last 90 days) | Hot timing, budget confirmed |
| **P1** | Studios 50-200 employees + known live ops titles | Sweet spot: budget + need |
| **P2** | Studios 20-50 employees with breakout hits | High growth trajectory |
| **P3** | Studios 200-500 employees | Larger org, longer sales cycle |
| **P4** | Studios with unclear live ops model | Requires more validation |

### Pre-Research Signals (Quick Triage)

**Fast-Qualify Checks (30 seconds/studio):**
1. App Annie / data.ai ranking in casual/hyper-casual
2. LinkedIn headcount range
3. Recent TechCrunch/PocketGamer coverage
4. Job postings for Live Ops, Monetization, or Partnerships roles

**Auto-Bump to Front of Queue:**
- Funding announcement within 30 days
- Hiring spree for Live Ops roles
- New game launch with battle pass/seasonal content
- Acquisition or merger activity

### Contact Strategy by Studio Size

| Studio Size | Primary Target | Secondary Target | Rationale |
|-------------|---------------|------------------|-----------|
| 20-75 employees | CEO / CPO | VP Product | Decision-maker accessible |
| 75-200 employees | VP Partnerships / BD | Head of Live Ops | Operational owner |
| 200-500 employees | Director of Partnerships | Live Ops Manager | Entry point for enterprise |

---

## 2. Batch Execution Plan

### Batch Structure (Resilient to Timeout)

**Problem:** Previous agent timed out after 4 minutes with full workflow  
**Solution:** Decompose into atomic, resumable batches

#### Batch Size Recommendation

| Batch Type | Studios | Estimated Time | Timeout Risk |
|------------|---------|----------------|--------------|
| **Discovery-only** | 10-12 | 3-4 min | Low |
| **Deep research** | 3-4 | 4-5 min | Medium |
| **Contact enrichment** | 2-3 | 4-5 min | Medium |
| **Full stack** | 1-2 | 4-6 min | High |

**Recommended Approach:** Discovery-first batching

### Phase 1: Discovery Sprint (Day 1)
**Goal:** Qualify and tier all 36 studios  
**Output:** Ranked list with go/no-go decisions

```
Batch 1.1: Studios 1-12 (discovery + triage)
Batch 1.2: Studios 13-24 (discovery + triage)
Batch 1.3: Studios 25-36 (discovery + triage)
```

**Per-Studio Output:**
- Qualification status (qualified / disqualified)
- Preliminary tier (P0-P4)
- Key signals (funding, headcount, titles)
- Research priority score (1-10)

### Phase 2: Deep Research (Days 2-3)
**Goal:** Complete research for top 20 qualified studios  
**Input:** Ranked list from Phase 1

```
Day 2:
  Batch 2.1: Top 7 studios (deep research + contact ID)
  
Day 3:
  Batch 2.2: Next 7 studios (deep research + contact ID)
  Batch 2.3: Remaining 6 studios (deep research + contact ID)
```

**Per-Studio Output:**
- Complete Studio Entity data model
- 1-2 identified contacts with titles
- Outreach angle hypothesis
- Trigger events identified

### Phase 3: Contact Enrichment (Days 3-4)
**Goal:** Verify emails and draft outreach  
**Input:** Studios with contacts identified

```
Batch 3.1: Tier-1 studios (email verification + draft)
Batch 3.2: Tier-2 studios (email verification + draft)
Batch 3.3: Tier-3 studios (email verification + draft)
```

**Per-Studio Output:**
- Complete Contact Entity data model
- Verified/pattern-confirmed email
- Draft outreach message
- Trello-ready card

### Recovery Protocol (If Timeout Occurs)

**Checkpoint After Each Batch:**
1. Write progress to file (`progress/batch_X_complete.json`)
2. Log which studios completed vs remaining
3. Note partial completions (e.g., "Studio Y: contact found, email pending")

**Resume Logic:**
- Read last checkpoint
- Skip completed studios
- Continue from next in queue
- Preserve partial progress

---

## 3. Output Format Specification for Trello Cards

### Card Title Format

```
[{TIER}] {Studio Name} — {Primary Contact Name} — {Angle}
```

**Examples:**
```
[Tier-1] Voodoo — Alexandre Yazdi — Live Ops Partnership
[Tier-2] SayGames — Egor Vaihanski — AI Content Velocity
```

### Card Description Template

```markdown
## Studio Profile
| Field | Value |
|-------|-------|
| **Name** | {studio_name} |
| **Website** | {website} |
| **Location** | {headquarters_location} |
| **Size** | {employee_count} employees |
| **Downloads** | {total_downloads_estimate} |
| **Key Titles** | {key_titles} |
| **Live Ops Evidence** | {live_ops_evidence} |
| **LinkedIn** | {linkedin_company_url} |

## Primary Contact
| Field | Value |
|-------|-------|
| **Name** | {full_name} |
| **Title** | {title} |
| **Seniority** | {seniority_level} |
| **Department** | {department} |
| **Email** | `{email}` |
| **Email Source** | {email_source} |
| **Verification** | {email_verification_status} |
| **LinkedIn** | {linkedin_profile_url} |
| **Verified** | {linkedin_verified} |

## Secondary Contact
[Same table format if applicable, else "N/A"]

## Qualification
| Field | Value |
|-------|-------|
| **Tier** | {tier} |
| **Priority** | {priority_level} |
| **Notes** | {qualification_notes} |

## Outreach Context
| Field | Value |
|-------|-------|
| **Targeting Angle** | {targeting_angle} |
| **Recent News/Trigger** | {recent_news_or_trigger} |
| **Why Now** | {why_now} |
| **Pain/Opportunity Hypothesis** | {hypothesis_of_pain_or_opportunity} |
| **Personalization Hook** | {personalization_hook} |

## Draft Message
**Subject:** {subject_line}

```
{email_body}
```

## Data Sources
- Studio research: {source_list}
- Contact research: {source_list}
- Email verification: {verification_method}

## Researcher Notes
[Any additional context for reviewer]
```

### Labels (Exact Names)

| Label | Color | Usage |
|-------|-------|-------|
| `Tier-1` | Green | Top 20% — highest priority |
| `Tier-2` | Yellow | Good fit, moderate signal |
| `Tier-3` | Blue | Stretch/lower priority |
| `Ready for Review` | Red | Research complete, awaiting approval |
| `Research Complete` | Purple | All fields populated |
| `Needs Contact` | Orange | Studio qualified, email pending |
| `Disqualified` | Black | Does not meet ICP |

### Checklist (Card Attachments)

```markdown
## Research Quality Checklist
- [ ] ICP validated (size, focus, downloads)
- [ ] Live ops model confirmed
- [ ] At least one qualified contact identified
- [ ] Email source documented
- [ ] Email verified or pattern-confirmed
- [ ] Personalization hook identified
- [ ] Outreach drafted (75-125 words)
- [ ] CTA clear and low-friction
- [ ] Sources logged
- [ ] Tier assigned
```

### Due Date Staggering

| Tier | Due Date Offset | Rationale |
|------|-----------------|-----------|
| Tier-1 | +2 days | Fastest follow-up |
| Tier-2 | +4 days | Moderate priority |
| Tier-3 | +7 days | Fill pipeline gaps |

---

## 4. Quality Criteria for "Ready for Review"

### Mandatory Fields (All Must Be Present)

**Studio Entity:**
- [ ] `studio_name` — exact legal name
- [ ] `website` — working URL
- [ ] `headquarters_location` — city, country
- [ ] `employee_count` — number or range
- [ ] `total_downloads_estimate` — "100M+", "500M+", "1B+"
- [ ] `key_titles` — at least 2 with download counts
- [ ] `live_ops_evidence` — specific, verifiable evidence
- [ ] `linkedin_company_url` — direct link
- [ ] `tier` — Tier-1, Tier-2, or Tier-3
- [ ] `qualification_notes` — why qualified

**Contact Entity:**
- [ ] `full_name` — first and last
- [ ] `title` — exact job title
- [ ] `seniority_level` — C-Level / VP / Director / Manager
- [ ] `department` — Business Dev / Partnerships / LiveOps / Leadership
- [ ] `email` — complete address
- [ ] `email_source` — specific source (not "internet")
- [ ] `email_verification_status` — Verified / Pattern-Confirmed / Unverified
- [ ] `linkedin_profile_url` — direct link
- [ ] `linkedin_verified` — true if profile viewed

**Outreach Context:**
- [ ] `targeting_angle` — one clear angle
- [ ] `recent_news_or_trigger` — specific event or "ongoing"
- [ ] `why_now` — timing rationale
- [ ] `hypothesis_of_pain_or_opportunity` — specific problem
- [ ] `personalization_hook` — unique detail for opener

### Quality Gates (Pass All Before Moving to "Ready")

#### Gate 1: Data Integrity
- No fabricated data — every claim source-backed
- No placeholder text (e.g., "TODO", "TBD")
- No unverified assumptions marked as fact
- Email verification status accurate (not optimistic)

#### Gate 2: Email Quality
- **Verified:** Email found on website, press release, or verified database
- **Pattern-Confirmed:** Email follows company pattern (e.g., firstname@company.com) AND pattern confirmed via multiple sources
- **Unverified:** Marked clearly if no validation possible
- No Gmail/Outlook/Yahoo unless no alternative exists

#### Gate 3: Outreach Quality
- **Word count:** 75-125 words (strict)
- **Subject line:** Specific, contextual (not generic)
- **First line:** Proves research (references their work/news)
- **Value prop:** Specific problem/opportunity (not generic "we help studios grow")
- **CTA:** Low friction ("15 min?" not "let's discuss")
- **No buzzwords:** "synergy", "leverage", "optimize" only if justified

#### Gate 4: Personalization Depth
- **Strong:** References specific game, recent news, or unique detail (8-10/10)
- **Acceptable:** References studio type + portfolio focus (6-7/10)
- **Weak:** Generic "love your games" (reject — revise)

#### Gate 5: Strategic Fit
- Studio matches ICP (casual/hyper-casual, 20-500 employees)
- Live ops model confirmed (not assumed)
- Contact is appropriate seniority for studio size
- Timing trigger present (funding, launch, hiring)

### Self-Verification Scorecard

Before marking "Ready for Review," score 1-10:

| Category | Score | Threshold |
|----------|-------|-----------|
| Data completeness | __ | ≥ 8 |
| Email quality | __ | ≥ 8 |
| Personalization depth | __ | ≥ 7 |
| Strategic fit | __ | ≥ 8 |
| Trello readiness | __ | ≥ 9 |

**If any category below threshold:** Revise before submitting.

### Rejection Criteria (Send Back to Research)

A card should be moved to "Needs Revision" (not "Ready for Review") if:
- Missing any mandatory field
- Email marked "Verified" without evidence
- Outreach > 125 words or < 75 words
- Personalization is generic or templated
- Live ops model not confirmed
- No clear timing trigger
- Sources not documented

---

## 5. Execution Schedule

### Daily Targets

| Day | Phase | Studios | Deliverable |
|-----|-------|---------|-------------|
| Day 1 | Discovery | 36 qualified/tiered | Ranked priority list |
| Day 2 | Deep Research | 10 | 10 cards with contacts identified |
| Day 3 | Deep Research | 10 | 10 cards with contacts identified |
| Day 4 | Contact Enrichment | 10 | 10 cards ready for review |
| Day 5 | Buffer/Overflow | Remaining | Complete backlog |

### Agent Delegation Pattern

```
MAIN AGENT
├── Spawn DISCOVERY_AGENT → 36 studios triaged
├── Review triage output
├── Spawn RESEARCH_AGENT batches (3-4 studios each)
│   ├── Batch 1: Studios 1-4
│   ├── Batch 2: Studios 5-8
│   └── ...
├── Review research outputs
├── Spawn ENRICHMENT_AGENT batches (2-3 studios each)
│   ├── Batch 1: Tier-1 studios
│   ├── Batch 2: Tier-2 studios
│   └── Batch 3: Tier-3 studios
└── Final review → Trello upload
```

### Checkpoint Files

Create after each batch:
- `progress/discovery_complete.json` — all 36 studios with triage
- `progress/research_batch_X.json` — 3-4 studios with deep research
- `progress/enrichment_batch_X.json` — 2-3 studios with verified emails + drafts

---

## 6. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Agent timeout | Discovery-first batching, checkpoints every 3-4 studios |
| Data inconsistency | Strict data model enforcement, mandatory fields |
| Email verification gaps | Clear status labels (Verified/Pattern/Unverified) |
| Quality drift | Self-verification scorecard, rejection criteria |
| Duplicates | Cross-check against existing Trello before research |
| Lucas bandwidth | Stagger due dates, prioritize Tier-1 |

---

## Summary

This plan enables:
1. **Resilient execution** via discovery-first batching and checkpoints
2. **Consistent output** via strict data models and quality gates
3. **Scalable throughput** via parallel agent delegation
4. **High-quality cards** via self-verification and rejection criteria

**Next Action:** Execute Phase 1 (Discovery Sprint) to qualify and tier all 36 studios.
