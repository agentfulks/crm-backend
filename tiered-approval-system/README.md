# Tiered Approval System

A lightweight CLI tool to reduce approval burden by 80%+ through intelligent 3-tier card classification.

## Overview

- **P0**: Urgent review (95+ fit, <3 days)
- **P1**: Batch approval eligible (80-94 fit)
- **P2**: Auto-archive candidates (<80 fit)

## Installation

```bash
cd tiered-approval-system
pip install -e .
# or just run directly with Python
```

## Usage

### Show Dashboard
```bash
python scripts/approval_dashboard.py
```

Displays:
- Card counts by tier
- Top 10 P0 cards requiring urgent review

### Batch Approve by Tier
```bash
python scripts/approval_dashboard.py approve-batch --tier P1 --limit 20
```

Options:
- `--tier {P0,P1,P2}`: Which tier to approve (required)
- `--limit N`: Maximum cards to approve (default: 20)
- `--yes`: Skip confirmation prompt

### Archive Expired Cards
```bash
python scripts/approval_dashboard.py archive-expired --days 14
```

Archives P2 cards that have been in queue longer than the specified days.

Options:
- `--days N`: Minimum days in queue to archive (default: 14)
- `--yes`: Skip confirmation prompt

## Input Format

Create a `trello-state.json` file in the project root:

```json
[
  {
    "id": "card-123",
    "name": "Startup XYZ",
    "description": "AI infrastructure company",
    "fit_score": 96,
    "funding_stage": "Series A",
    "portfolio_match": true,
    "days_in_queue": 1,
    "labels": ["AI", "Infrastructure"]
  }
]
```

Or use a wrapped format:
```json
{
  "cards": [
    {"id": "card-1", "name": "Startup A", "fit_score": 95, "days_in_queue": 2},
    {"id": "card-2", "name": "Startup B", "fit_score": 85, "days_in_queue": 5}
  ]
}
```

## Classification Rules

| Tier | Criteria |
|------|----------|
| P0 | Fit ≥95 AND Days <3 |
| P1 | Fit 80-94 OR (Fit ≥95 AND Days ≥3) |
| P2 | Fit <80 |

## Running Tests

```bash
pytest tests/
```

## Project Structure

```
tiered-approval-system/
├── src/
│   ├── models/
│   │   └── approval_tiers.py    # Data models (CardTier, CardSnapshot, etc.)
│   └── services/
│       ├── tier_classifier.py   # Classification logic
│       └── batch_approver.py    # Batch operations
├── scripts/
│   └── approval_dashboard.py    # CLI interface
├── tests/
│   └── test_tier_classifier.py  # Unit tests
└── README.md
```

## Future Enhancements

- Web dashboard (Phase 2)
- Trello API integration
- Custom classification rules
- Approval history tracking
