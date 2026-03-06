# Scoring + Prioritization Model

VC fund scoring algorithm with configurable weights, priority tiers, and outreach recommendations.

## Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Thesis Alignment | 20% | Gaming + AI focus match |
| Stage Match | 15% | Series A/B alignment |
| Sector Focus | 15% | Target sector overlap |
| Warm Intro Available | 15% | Network connectivity |
| Check Size Match | 10% | Investment range fit |
| Fund Reputation | 10% | Tier/quality score |
| Value-Add | 10% | Strategic value potential |
| Speed | 5% | Expected decision speed |

## Priority Tiers

| Tier | Score Range | Action |
|------|-------------|--------|
| S | 0.90+ | Immediate outreach, warm intro if possible |
| A | 0.75-0.89 | High priority, personalized approach |
| B | 0.60-0.74 | Medium priority, targeted outreach |
| C | 0.40-0.59 | Low priority, standard outreach |
| D | <0.40 | Skip unless strategic reason |

## Usage

```bash
# Score all unscored funds
python scripts/score_cli.py score

# Score specific funds
python scripts/score_cli.py score fund-id-1 fund-id-2

# Show top funds
python scripts/score_cli.py top

# Show top S-tier only
python scripts/score_cli.py top --tier S

# Analyze specific fund
python scripts/score_cli.py analyze fund-id
```

## Reputation Scoring

### Tier 1 Funds (Score: 1.0)
Sequoia, a16z, Accel, Benchmark, Bessemer, Greylock, Index, Insight, Khosla, Kleiner Perkins, Lightspeed, NEA

### Tier 2 Funds (Score: 0.85)
500 Startups, Battery, Craft, DCVC, First Round, Founders Fund, General Catalyst, GV, IVP, Matrix, Menlo

### Gaming Specialists (High Value-Add)
Bitkraft, Griffin, Galaxy, Konvoy, Makers Fund, Hiro Capital, Transcend, Lumikai
