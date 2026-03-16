-- ============================================================
-- VC Outreach CRM Analytics Engine - PostgreSQL Schema
-- Phase 2: Core Schema Design
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- CORE ENTITY TABLES
-- ============================================================

-- Startups/Companies being contacted
CREATE TABLE startups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(100),
    stage VARCHAR(50), -- seed, series_a, series_b, etc.
    location VARCHAR(255),
    trello_card_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contacts within startups
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    title VARCHAR(150),
    linkedin_url TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    unsubscribed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(startup_id, email)
);

-- Email campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    sent_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, paused, completed
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ
);

-- Individual emails sent
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(id),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    startup_id UUID REFERENCES startups(id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    tracking_pixel_token UUID DEFAULT uuid_generate_v4(),
    status VARCHAR(50) DEFAULT 'queued', -- queued, sent, delivered, bounced
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexes for common queries
    CONSTRAINT idx_unique_tracking_token UNIQUE (tracking_pixel_token)
);

-- ============================================================
-- ANALYTICS EVENT TABLES
-- ============================================================

-- Email engagement events (opens, clicks, bounces, etc.)
CREATE TABLE email_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_id UUID REFERENCES emails(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- open, click, bounce, spam_report, unsubscribe
    
    -- Event metadata
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    link_url TEXT, -- for click events
    
    -- Timestamping with microsecond precision for ordering
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    received_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Raw event data for extensibility (JSONB)
    metadata JSONB DEFAULT '{}'
);

-- Trello board structure cache
CREATE TABLE trello_lists (
    id VARCHAR(100) PRIMARY KEY, -- Trello list ID
    board_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    position FLOAT,
    list_type VARCHAR(50), -- backlog, in_progress, review, done, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trello cards (opportunities/deals)
CREATE TABLE trello_cards (
    id VARCHAR(100) PRIMARY KEY, -- Trello card ID
    startup_id UUID REFERENCES startups(id),
    list_id VARCHAR(100) REFERENCES trello_lists(id),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    url TEXT,
    position FLOAT,
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Card movement history (for velocity calculations)
CREATE TABLE card_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id VARCHAR(100) REFERENCES trello_cards(id) ON DELETE CASCADE,
    from_list_id VARCHAR(100) REFERENCES trello_lists(id),
    to_list_id VARCHAR(100) REFERENCES trello_lists(id),
    moved_by_user_id VARCHAR(100),
    moved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Calculated fields (can be derived, but cached for performance)
    lead_time_seconds INTEGER, -- time from first in_progress to this movement
    cycle_time_seconds INTEGER  -- time from previous list to this one
);

-- ============================================================
-- AGGREGATE/MATERIALIZED TABLES (for fast queries)
-- ============================================================

-- Pre-computed email metrics by campaign (updated periodically)
CREATE TABLE campaign_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Sent/delivered stats
    total_sent INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    delivery_rate FLOAT DEFAULT 0,
    
    -- Engagement stats
    total_opens INTEGER DEFAULT 0,
    unique_opens INTEGER DEFAULT 0,
    open_rate FLOAT DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0,
    click_rate FLOAT DEFAULT 0,
    click_to_open_rate FLOAT DEFAULT 0,
    
    -- Negative signals
    total_bounces INTEGER DEFAULT 0,
    bounce_rate FLOAT DEFAULT 0,
    total_spam_reports INTEGER DEFAULT 0,
    total_unsubscribes INTEGER DEFAULT 0,
    
    -- Time windows
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    
    UNIQUE(campaign_id, period_start, period_end)
);

-- Pre-computed velocity metrics
CREATE TABLE velocity_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Time period
    period_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Velocity stats
    cards_completed INTEGER DEFAULT 0,
    cards_started INTEGER DEFAULT 0,
    cards_in_progress INTEGER DEFAULT 0,
    
    -- Time metrics (in hours)
    avg_cycle_time_hours FLOAT,
    avg_lead_time_hours FLOAT,
    
    -- Throughput (cards per day)
    throughput_per_day FLOAT,
    
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(period_type, period_start)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- Email event lookups
CREATE INDEX idx_email_events_email_id ON email_events(email_id);
CREATE INDEX idx_email_events_contact_id ON email_events(contact_id);
CREATE INDEX idx_email_events_type ON email_events(event_type);
CREATE INDEX idx_email_events_occurred_at ON email_events(occurred_at);
CREATE INDEX idx_email_events_type_time ON email_events(event_type, occurred_at);

-- Composite index for common analytics query
CREATE INDEX idx_email_events_analytics ON email_events(campaign_id, event_type, occurred_at) 
WHERE campaign_id IS NOT NULL;

-- Card movement lookups
CREATE INDEX idx_card_movements_card_id ON card_movements(card_id);
CREATE INDEX idx_card_movements_to_list ON card_movements(to_list_id);
CREATE INDEX idx_card_movements_moved_at ON card_movements(moved_at);
CREATE INDEX idx_card_movements_time_range ON card_movements(moved_at, to_list_id);

-- Startup/contact lookups
CREATE INDEX idx_contacts_startup ON contacts(startup_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_startups_trello ON startups(trello_card_id);

-- Trello lookups
CREATE INDEX idx_trello_cards_list ON trello_cards(list_id);
CREATE INDEX idx_trello_cards_startup ON trello_cards(startup_id);
CREATE INDEX idx_trello_lists_board ON trello_lists(board_id);

-- ============================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================

-- Real-time campaign stats view
CREATE VIEW v_campaign_stats AS
SELECT 
    c.id AS campaign_id,
    c.name AS campaign_name,
    COUNT(DISTINCT e.id) AS total_emails,
    COUNT(DISTINCT CASE WHEN ee.event_type = 'open' THEN ee.email_id END) AS unique_opens,
    COUNT(DISTINCT CASE WHEN ee.event_type = 'click' THEN ee.email_id END) AS unique_clicks,
    COUNT(DISTINCT CASE WHEN ee.event_type = 'bounce' THEN ee.email_id END) AS bounces,
    ROUND(
        COUNT(DISTINCT CASE WHEN ee.event_type = 'open' THEN ee.email_id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
        2
    ) AS open_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN ee.event_type = 'click' THEN ee.email_id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
        2
    ) AS click_rate_pct
FROM campaigns c
LEFT JOIN emails e ON e.campaign_id = c.id
LEFT JOIN email_events ee ON ee.email_id = e.id
GROUP BY c.id, c.name;

-- Velocity view (last 30 days by day)
CREATE VIEW v_velocity_daily AS
SELECT 
    DATE_TRUNC('day', cm.moved_at) AS day,
    COUNT(DISTINCT cm.card_id) AS cards_completed,
    AVG(cm.cycle_time_seconds / 3600.0) AS avg_cycle_time_hours,
    AVG(cm.lead_time_seconds / 3600.0) AS avg_lead_time_hours
FROM card_movements cm
JOIN trello_lists tl ON tl.id = cm.to_list_id
WHERE tl.list_type = 'done'
    AND cm.moved_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', cm.moved_at)
ORDER BY day DESC;

-- ============================================================
-- FUNCTIONS FOR REAL-TIME UPDATES
-- ============================================================

-- Function to calculate cycle time for a card movement
CREATE OR REPLACE FUNCTION calculate_cycle_time()
RETURNS TRIGGER AS $$
DECLARE
    previous_movement TIMESTAMPTZ;
    first_progress TIMESTAMPTZ;
BEGIN
    -- Get the previous movement time
    SELECT moved_at INTO previous_movement
    FROM card_movements
    WHERE card_id = NEW.card_id AND moved_at < NEW.moved_at
    ORDER BY moved_at DESC
    LIMIT 1;
    
    IF previous_movement IS NOT NULL THEN
        NEW.cycle_time_seconds := EXTRACT(EPOCH FROM (NEW.moved_at - previous_movement))::INTEGER;
    END IF;
    
    -- Get first time card entered 'in_progress'
    SELECT cm.moved_at INTO first_progress
    FROM card_movements cm
    JOIN trello_lists tl ON tl.id = cm.to_list_id
    WHERE cm.card_id = NEW.card_id AND tl.list_type = 'in_progress'
    ORDER BY cm.moved_at ASC
    LIMIT 1;
    
    IF first_progress IS NOT NULL THEN
        NEW.lead_time_seconds := EXTRACT(EPOCH FROM (NEW.moved_at - first_progress))::INTEGER;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_cycle_time
    BEFORE INSERT ON card_movements
    FOR EACH ROW
    EXECUTE FUNCTION calculate_cycle_time();

-- Function to update campaign sent count
CREATE OR REPLACE FUNCTION update_campaign_sent_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'sent' AND OLD.status != 'sent' THEN
        UPDATE campaigns 
        SET sent_count = sent_count + 1
        WHERE id = NEW.campaign_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_sent_count
    AFTER UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_campaign_sent_count();
