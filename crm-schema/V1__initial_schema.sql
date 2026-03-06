-- V1__initial_schema.sql
-- Initial schema for VC Outreach CRM
-- Created: 2025-02-25

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- FIRMS TABLE
-- VC firms and investment entities
-- =====================================================
CREATE TABLE firms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(512),
    location VARCHAR(255),
    check_size_min NUMERIC(15, 2),
    check_size_max NUMERIC(15, 2),
    stage_focus VARCHAR(100)[] DEFAULT '{}',
    sector_focus VARCHAR(100)[] DEFAULT '{}',
    aum NUMERIC(15, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for firms table
CREATE INDEX idx_firms_name ON firms(name);
CREATE INDEX idx_firms_location ON firms(location);
CREATE INDEX idx_firms_stage_focus ON firms USING GIN(stage_focus);
CREATE INDEX idx_firms_sector_focus ON firms USING GIN(sector_focus);
CREATE INDEX idx_firms_created_at ON firms(created_at);

-- =====================================================
-- CONTACTS TABLE
-- People associated with firms
-- =====================================================
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    email VARCHAR(255),
    linkedin VARCHAR(512),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for contacts table
CREATE INDEX idx_contacts_firm_id ON contacts(firm_id);
CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_is_primary ON contacts(is_primary);
CREATE INDEX idx_contacts_created_at ON contacts(created_at);

-- Unique constraint: only one primary contact per firm
CREATE UNIQUE INDEX idx_contacts_one_primary_per_firm 
ON contacts(firm_id) 
WHERE is_primary = TRUE;

-- =====================================================
-- OUTREACH ATTEMPTS TABLE
-- Track all outreach activities
-- =====================================================
CREATE TABLE outreach_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    method VARCHAR(50) NOT NULL CHECK (method IN ('email', 'linkedin', 'twitter', 'warm_intro', 'phone', 'in_person', 'other')),
    status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'delivered', 'opened', 'replied', 'bounced', 'unsubscribed', 'no_response')),
    sent_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    meeting_booked BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for outreach_attempts table
CREATE INDEX idx_outreach_firm_id ON outreach_attempts(firm_id);
CREATE INDEX idx_outreach_contact_id ON outreach_attempts(contact_id);
CREATE INDEX idx_outreach_method ON outreach_attempts(method);
CREATE INDEX idx_outreach_status ON outreach_attempts(status);
CREATE INDEX idx_outreach_sent_at ON outreach_attempts(sent_at);
CREATE INDEX idx_outreach_replied_at ON outreach_attempts(replied_at);
CREATE INDEX idx_outreach_meeting_booked ON outreach_attempts(meeting_booked);
CREATE INDEX idx_outreach_created_at ON outreach_attempts(created_at);

-- =====================================================
-- NOTES TABLE
-- Free-form notes about firms
-- =====================================================
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_by VARCHAR(255) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for notes table
CREATE INDEX idx_notes_firm_id ON notes(firm_id);
CREATE INDEX idx_notes_created_by ON notes(created_by);
CREATE INDEX idx_notes_created_at ON notes(created_at);

-- =====================================================
-- AUTO-UPDATE TRIGGER FUNCTION
-- Updates updated_at timestamp on row modification
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER trigger_firms_updated_at
    BEFORE UPDATE ON firms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_outreach_attempts_updated_at
    BEFORE UPDATE ON outreach_attempts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE firms IS 'VC firms and investment entities';
COMMENT ON TABLE contacts IS 'People associated with VC firms';
COMMENT ON TABLE outreach_attempts IS 'Outreach activities and their outcomes';
COMMENT ON TABLE notes IS 'Free-form notes about firms';

COMMENT ON COLUMN firms.check_size_min IS 'Minimum check size in USD';
COMMENT ON COLUMN firms.check_size_max IS 'Maximum check size in USD';
COMMENT ON COLUMN firms.stage_focus IS 'Array of investment stages (e.g., seed, series_a, growth)';
COMMENT ON COLUMN firms.sector_focus IS 'Array of sectors (e.g., saas, fintech, healthcare)';
COMMENT ON COLUMN firms.aum IS 'Assets under management in USD';
COMMENT ON COLUMN contacts.is_primary IS 'Whether this is the primary contact for the firm';
COMMENT ON COLUMN outreach_attempts.method IS 'Channel used for outreach';
COMMENT ON COLUMN outreach_attempts.meeting_booked IS 'Whether a meeting was booked as a result of this outreach';
