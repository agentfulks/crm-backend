# VC Outreach CRM Analytics Engine

Real-time analytics engine for tracking email engagement and Trello card velocity in a VC outreach CRM.

## Architecture

- **PostgreSQL**: Primary datastore with time-series optimized schema
- **FastAPI**: Async Python API for event ingestion and querying
- **TimescaleDB**: Extension for high-volume time-series data (Phase 3)
- **Redis**: Caching layer for real-time metrics (Phase 3)

## Quick Start

```bash
# Start services
docker-compose up -d

# Run migrations
psql -d vc_crm -f schema.sql

# Start API
uvicorn main:app --reload
```

## API Endpoints

### Email Events
- `POST /api/v1/email-events` - Record email event
- `POST /api/v1/email-events/batch` - Batch ingest (high volume)
- `GET /track/pixel/{token}.gif` - Tracking pixel

### Campaign Analytics
- `GET /api/v1/campaigns/{id}/stats` - Campaign statistics
- `GET /api/v1/campaigns/{id}/timeseries` - Time-series data

### Velocity Tracking
- `POST /api/v1/card-movements` - Record card movement
- `GET /api/v1/velocity/current` - Current velocity metrics
- `GET /api/v1/cards/{id}/history` - Card movement history

### Real-time
- `GET /api/v1/analytics/realtime` - Real-time dashboard metrics

## Schema Design

### Email Events Table
- UUID primary key
- Denormalized contact_id for fast queries
- JSONB metadata for extensibility
- Partitioned by time (TimescaleDB hypertable in Phase 3)

### Card Movements Table
- Automatic cycle/lead time calculation via trigger
- References Trello list types (backlog, in_progress, done)
- Indexed for time-range queries

## Phase 3: Scaling to 10k events/sec

See `docs/scaling.md` for high-volume ingestion strategies.
