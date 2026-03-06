# Analytics + Metrics Pipeline

Metrics ETL and dashboard API for VC outreach performance tracking.

## Metrics

### Fund Metrics
| Metric | Description | Frequency |
|--------|-------------|-----------|
| total_funds | Total funds in database | Daily |
| funds_by_tier | Distribution by priority tier | Daily |
| avg_fund_score | Average scoring across all funds | Daily |

### Enrichment Metrics
| Metric | Description | Frequency |
|--------|-------------|-----------|
| enrichment_rate | % funds with enriched contacts | Daily |
| avg_contacts_per_fund | Average contacts per fund | Daily |
| email_coverage | % contacts with email | Daily |

### Outreach Metrics
| Metric | Description | Frequency |
|--------|-------------|-----------|
| outreach_response_rate | % outreach with response | Weekly |
| time_to_response | Avg days to response | Weekly |
| meetings_scheduled | Meeting count | Weekly |

## Usage

```bash
# Show dashboard
python scripts/analytics_cli.py dashboard

# Run ETL pipeline
python scripts/analytics_cli.py etl

# List all metrics
python scripts/analytics_cli.py metrics

# Export dashboard to JSON
python scripts/analytics_cli.py dashboard --json dashboard.json
```

## API Endpoints

### GET /api/analytics/dashboard
Returns dashboard data

### GET /api/analytics/metrics
Returns available metrics list

### POST /api/analytics/etl/run
Triggers ETL run
