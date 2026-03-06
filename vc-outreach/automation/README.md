# Source Automation v1

Automated ingestion of VC funds from external data sources (Crunchbase, Apollo), with deduplication and scheduled daily syncs.

## Architecture

```
automation/
├── src/
│   ├── models.py         # Pydantic data models
│   ├── dedupe.py         # Deduplication engine
│   ├── fetchers/         # Data source fetchers
│   │   ├── base.py       # Abstract base fetcher
│   │   ├── apollo.py     # Apollo.io fetcher
│   │   └── crunchbase.py # Crunchbase fetcher
│   ├── db_ops.py         # Database operations
│   ├── sync.py           # Sync orchestrator
│   └── scheduler.py      # Cron scheduler
├── tests/                # Unit tests
└── scripts/
    └── sync_cli.py       # Command-line interface
```

## Features

- **Multi-source ingestion**: Apollo.io, Crunchbase
- **Smart deduplication**: Fuzzy name matching, website comparison
- **Configurable filtering**: Sector focus, stage preferences
- **Rate limiting**: Respects API limits
- **Scheduled syncs**: Cron-based automation
- **Dry-run mode**: Test without writing

## Usage

### Environment Setup

```bash
export APOLLO_API_KEY="your_apollo_key"
export CRUNCHBASE_API_KEY="your_crunchbase_key"
```

### Run Sync

```bash
# Sync all sources
python scripts/sync_cli.py sync

# Sync specific source
python scripts/sync_cli.py sync --source apollo

# Dry run (no writes)
python scripts/sync_cli.py sync --dry-run
```

### Test Deduplication

```bash
python scripts/sync_cli.py dedupe-test
```

### View Statistics

```bash
python scripts/sync_cli.py stats
```

### Run Scheduler

```bash
# Default: daily at 6am
python scripts/sync_cli.py schedule

# Custom schedule
python scripts/sync_cli.py schedule --cron "0 */6 * * *"
```

## Deduplication Logic

| Match Type | Confidence | Action |
|------------|------------|--------|
| Exact name match | 1.0 | Update existing |
| Substring match | 0.95 | Update existing |
| High fuzzy match | 0.85-0.95 | Update existing |
| Medium match | 0.70-0.85 | Skip for manual review |
| No match | <0.70 | Create new |

## Testing

```bash
pytest tests/ -v
```
