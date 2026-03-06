# Contact Enrichment Workflow

Automated contact discovery and enrichment using Apollo.io and Hunter.io APIs.

## Features

- **Multi-provider enrichment**: Apollo.io + Hunter.io
- **Smart filtering**: Confidence scoring, role-based filtering
- **Email verification**: Validate discovered emails
- **Deduplication**: Prevents duplicate contacts
- **Dry-run mode**: Test without database writes

## Usage

### Environment Setup

```bash
export APOLLO_API_KEY="your_apollo_key"
export HUNTER_API_KEY="your_hunter_key"
```

### Enrich Specific Funds

```bash
# Enrich specific funds by ID
python scripts/enrich_cli.py enrich fund-id-1 fund-id-2

# Use specific sources only
python scripts/enrich_cli.py enrich fund-id --sources apollo

# Dry run (test without saving)
python scripts/enrich_cli.py enrich fund-id --dry-run

# Verbose output
python scripts/enrich_cli.py enrich fund-id -v
```

### Enrich All Funds

```bash
# Enrich all funds without primary contacts
python scripts/enrich_cli.py enrich-all

# Limit contacts per fund
python scripts/enrich_cli.py enrich-all --max-contacts 3

# Higher confidence threshold
python scripts/enrich_cli.py enrich-all --min-confidence 0.8
```

## Contact Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Email found | +20% | Has email address |
| Email verified | +20% | Passed verification |
| Data sources | +20% | Multiple sources confirm |
| Name complete | +10% | First and last name |
| Title present | +10% | Has job title |

## Role Detection

Automatically classifies contacts as:
- Managing Partner
- General Partner
- Partner
- Principal
- VP
- Associate
- Analyst

## Testing

```bash
pytest tests/ -v
```
