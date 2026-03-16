# ============================================================
# Phase 3: Scaling to 10,000 Events/Second
# Architecture & Deployment Guide
# ============================================================

## Performance Targets

- **Ingestion**: 10,000 events/second sustained
- **Query Latency**: < 50ms for real-time dashboards
- **Data Retention**: 90 days raw, 1 year aggregates
- **Availability**: 99.9% uptime

## Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │          Client Applications         │
                    │    (Email service, Trello webhooks)  │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                           Load Balancer (nginx)                       │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │  API Pod 1  │    │  API Pod 2  │    │  API Pod N  │
       │  (FastAPI)  │    │  (FastAPI)  │    │  (FastAPI)  │
       └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
           ┌─────────────┐             ┌─────────────┐
           │    Kafka    │             │    Redis    │
           │   Cluster   │             │    Cache    │
           │  (3 brokers)│             │   (HA mode) │
           └──────┬──────┘             └─────────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │  Consumer Group     │
       │  (3-10 instances)   │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │  TimescaleDB        │
       │  (Primary + Replica)│
       └─────────────────────┘
```

## Key Scaling Strategies

### 1. Database Layer (TimescaleDB)

**Hypertables**: Automatic time-based partitioning
- `email_events`: 1-day chunks, compressed after 7 days
- `card_movements`: 7-day chunks, compressed after 30 days

**Indexes**:
- BRIN indexes on time columns (tiny size, fast sequential scans)
- Partial indexes for hot queries (recent data only)

**Continuous Aggregates**: Pre-computed rollups
- Hourly metrics (5-min refresh)
- Daily velocity (1-hour refresh)

**Retention**:
- Raw events: 90 days (via drop_chunks)
- Aggregates: 1 year

### 2. Caching Layer (Redis)

**Cache Strategy**:
- Real-time dashboard: 30-second TTL
- Campaign stats: 5-minute TTL  
- Velocity metrics: 1-hour TTL
- Counters: Incremental updates with 1-hour TTL

**Benefits**:
- Reduces database load by ~80%
- < 10ms cache hit latency
- Automatic eviction

### 3. Message Queue (Kafka)

**Why Kafka?**
- Buffer during database slowdowns (backpressure)
- Replay capability for debugging
- Partitioning by email_id maintains per-email ordering
- Horizontal scaling via consumer groups

**Configuration**:
- Topic: `email-events` (10 partitions)
- Replication: 3
- Retention: 7 days
- Compression: gzip

**Producer Settings**:
- Batch size: 64KB
- Linger: 10ms
- Compression: gzip
- Acks: all

### 4. Application Layer

**FastAPI + asyncpg**:
- Async I/O for high concurrency
- Connection pooling (min: 10, max: 100)
- Batch COPY for ingestion

**Consumer Scaling**:
- 3-10 consumer instances
- Each processes 1000-event batches
- Auto-commit offsets after DB write

## Benchmarking

### Expected Performance

| Component | Throughput | Latency |
|-----------|-----------|---------|
| API (single) | 2,000 req/s | 10ms p99 |
| Kafka | 100,000 msg/s | 5ms |
| Consumer (each) | 5,000 events/s | - |
| PostgreSQL COPY | 50,000 rows/s | - |
| Redis | 100,000 ops/s | 1ms |

### Total Capacity (3-node setup)

- **Events/sec**: 15,000+ (3 consumers × 5,000)
- **Concurrent connections**: 300 (3 API × 100 pool)
- **Storage**: ~50GB/day (compressible to ~5GB with TimescaleDB)

## Deployment Commands

```bash
# Start infrastructure
docker-compose up -d postgres redis kafka

# Run schema migrations
docker-compose exec postgres psql -U vc_crm -d vc_crm -f /docker-entrypoint-initdb.d/01-schema.sql
docker-compose exec postgres psql -U vc_crm -d vc_crm -f /docker-entrypoint-initdb.d/02-schema_phase3.sql

# Scale API tier
docker-compose up -d --scale api=3

# Scale consumers
docker-compose up -d --scale consumer=5

# Monitor
docker-compose logs -f consumer
```

## Kubernetes Deployment (Production)

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vc-crm-api
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: api
        image: vc-crm-analytics:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

## Monitoring

**Key Metrics**:
- `events_ingested_per_second`
- `consumer_lag` (Kafka)
- `db_connection_pool_usage`
- `cache_hit_rate`
- `api_response_time_p99`

**Alerts**:
- Consumer lag > 100,000 messages
- DB connections > 80%
- API errors > 1%
- Cache hit rate < 80%

## Cost Estimates (AWS)

| Component | Instance | Monthly Cost |
|-----------|----------|--------------|
| PostgreSQL | db.r6g.xlarge | $350 |
| ElastiCache | cache.r6g.large | $150 |
| MSK (Kafka) | 3× kafka.m5.large | $600 |
| ECS/Fargate | 5 tasks | $200 |
| **Total** | | **~$1,300/mo** |

## Migration Path

### Phase 2 → Phase 3

1. **Add TimescaleDB** (no downtime)
   ```sql
   CREATE EXTENSION timescaledb;
   SELECT create_hypertable('email_events', 'occurred_at');
   ```

2. **Add Kafka** (dual-write)
   - Write to both DB and Kafka
   - Verify consistency
   - Switch reads to Kafka

3. **Add Redis** (gradual)
   - Enable caching
   - Tune TTL values
   - Monitor hit rates

4. **Scale horizontally**
   - Add API replicas
   - Add consumers
   - Monitor partition balance
