-- ============================================================
-- VC Outreach CRM Analytics Engine - PHASE 3 SCALING
-- Optimizations for 10k events/sec ingestion
-- ============================================================

-- Enable TimescaleDB extension (requires TimescaleDB installed)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================
-- HYPERTABLE CONVERSION (Time-series partitioning)
-- ============================================================

-- Convert email_events to hypertable for automatic partitioning
-- This creates chunks by time, dramatically improving write/query performance
SELECT create_hypertable('email_events', 'occurred_at', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Convert card_movements to hypertable
SELECT create_hypertable('card_movements', 'moved_at',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================
-- WRITE-OPTIMIZED INDEXES (Partial, BRIN for time-series)
-- ============================================================

-- BRIN index for time-series data (very small, efficient for ordered data)
CREATE INDEX idx_email_events_occurred_brin ON email_events 
    USING BRIN (occurred_at) WITH (pages_per_range = 128);

-- Partial indexes for hot queries (only recent data)
CREATE INDEX idx_email_events_recent_opens ON email_events (email_id, occurred_at)
    WHERE event_type = 'open' AND occurred_at > NOW() - INTERVAL '30 days';

-- Compressed chunks for older data (save storage, maintain query speed)
ALTER TABLE email_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'email_id, event_type'
);

-- Compress chunks older than 7 days automatically
SELECT add_compression_policy('email_events', INTERVAL '7 days');

-- ============================================================
-- CONTINUOUS AGGREGATES (Pre-computed rollups)
-- ============================================================

-- Hourly email metrics materialized view (auto-refreshed)
CREATE MATERIALIZED VIEW email_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', occurred_at) AS bucket,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT email_id) AS unique_emails,
    COUNT(DISTINCT contact_id) AS unique_contacts
FROM email_events
GROUP BY bucket, event_type
WITH NO DATA;

-- Refresh policy: every 5 minutes
SELECT add_continuous_aggregate_policy('email_metrics_hourly',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '5 minutes'
);

-- Daily velocity metrics materialized view
CREATE MATERIALIZED VIEW velocity_metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', cm.moved_at) AS day,
    COUNT(DISTINCT cm.card_id) FILTER (WHERE tl.list_type = 'done') AS cards_completed,
    COUNT(DISTINCT cm.card_id) AS total_movements,
    AVG(cm.cycle_time_seconds) FILTER (WHERE cm.cycle_time_seconds IS NOT NULL) AS avg_cycle_time,
    AVG(cm.lead_time_seconds) FILTER (WHERE cm.lead_time_seconds IS NOT NULL) AS avg_lead_time
FROM card_movements cm
JOIN trello_lists tl ON tl.id = cm.to_list_id
GROUP BY day
WITH NO DATA;

SELECT add_continuous_aggregate_policy('velocity_metrics_daily',
    start_offset => INTERVAL '3 months',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour'
);

-- ============================================================
-- HIGH-VOLUME INGESTION TABLE (Staging for bulk loads)
-- ============================================================

-- Unlogged table for temporary high-speed ingestion
-- Data is copied to main table and truncated periodically
CREATE UNLOGGED TABLE email_events_staging (
    LIKE email_events INCLUDING ALL
);

-- Fast path: Insert into staging, then bulk move to main table
CREATE OR REPLACE FUNCTION flush_event_staging()
RETURNS INTEGER AS $$
DECLARE
    inserted_count INTEGER;
BEGIN
    INSERT INTO email_events 
        SELECT * FROM email_events_staging
        ON CONFLICT DO NOTHING;
    
    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    
    TRUNCATE email_events_staging;
    
    RETURN inserted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- RETENTION POLICY (Auto-cleanup old data)
-- ============================================================

-- Drop raw events after 90 days (aggregates kept longer)
SELECT add_retention_policy('email_events', INTERVAL '90 days');

-- Drop card movements after 1 year
SELECT add_retention_policy('card_movements', INTERVAL '1 year');
