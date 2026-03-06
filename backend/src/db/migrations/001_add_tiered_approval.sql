-- Migration: Add tiered approval system tables and columns
-- Created: March 5, 2026

-- Add new columns to approval_cards table (if exists)
-- Or create the table if it doesn't exist

CREATE TABLE IF NOT EXISTS approval_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trello_card_id VARCHAR(255),
    type VARCHAR(10) NOT NULL CHECK (type IN ('BDR', 'VC')),
    company_name VARCHAR(255) NOT NULL,
    company_id VARCHAR(255),
    icp_score INTEGER NOT NULL CHECK (icp_score >= 1 AND icp_score <= 5),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_linkedin VARCHAR(500),
    contact_role VARCHAR(255),
    signals JSONB DEFAULT '[]',
    investment_stage VARCHAR(100),
    sector TEXT[],
    fund_size BIGINT,
    partner_type VARCHAR(50),
    
    -- Tiered approval fields
    tier INTEGER CHECK (tier IN (1, 2, 3)),
    confidence_score DECIMAL(5,2),
    auto_approved BOOLEAN DEFAULT FALSE,
    auto_approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'ESCALATED')),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    reviewed_by VARCHAR(255),
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_approval_cards_tier ON approval_cards(tier);
CREATE INDEX IF NOT EXISTS idx_approval_cards_auto_approved ON approval_cards(auto_approved);
CREATE INDEX IF NOT EXISTS idx_approval_cards_status ON approval_cards(status);
CREATE INDEX IF NOT EXISTS idx_approval_cards_type ON approval_cards(type);
CREATE INDEX IF NOT EXISTS idx_approval_cards_created_at ON approval_cards(created_at);
CREATE INDEX IF NOT EXISTS idx_approval_cards_trello_card_id ON approval_cards(trello_card_id);

-- Create audit log table
CREATE TABLE IF NOT EXISTS approval_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES approval_cards(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    tier INTEGER,
    confidence DECIMAL(5,2),
    rules_triggered JSONB DEFAULT '[]',
    performed_by VARCHAR(255) DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_card_id ON approval_audit_log(card_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON approval_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON approval_audit_log(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_approval_cards_updated_at ON approval_cards;
CREATE TRIGGER update_approval_cards_updated_at
    BEFORE UPDATE ON approval_cards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE approval_cards IS 'Cards in the tiered approval system for BDR and VC outreach';
COMMENT ON COLUMN approval_cards.tier IS 'Approval tier: 1 (auto-approve), 2 (quick review), 3 (deep review)';
COMMENT ON COLUMN approval_cards.confidence_score IS 'Confidence score from rules engine (0-100)';
COMMENT ON COLUMN approval_cards.auto_approved IS 'Whether the card was automatically approved by the system';
COMMENT ON TABLE approval_audit_log IS 'Audit trail for all approval actions';
