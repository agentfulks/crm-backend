"""Add BDR game studios outreach tables."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250225_000001"
down_revision = "702832c52976"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums using raw SQL with IF NOT EXISTS
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'studio_size_enum') THEN
                CREATE TYPE studio_size_enum AS ENUM ('INDIE', 'MID', 'LARGE');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'studio_status_enum') THEN
                CREATE TYPE studio_status_enum AS ENUM ('NEW', 'RESEARCHING', 'CONTACT_FOUND', 'MESSAGE_DRAFTED', 'READY_FOR_REVIEW', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contact_role_enum') THEN
                CREATE TYPE contact_role_enum AS ENUM ('CEO', 'CPO', 'CTO', 'LIVE_OPS', 'PARTNERSHIPS', 'UA', 'OTHER');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'game_genre_enum') THEN
                CREATE TYPE game_genre_enum AS ENUM ('HYPER_CASUAL', 'CASUAL', 'HYBRID_CASUAL', 'MIDCORE', 'MUSIC', 'PUZZLE', 'ARCADE', 'OTHER');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outreach_msg_status') THEN
                CREATE TYPE outreach_msg_status AS ENUM ('DRAFT', 'REVIEW', 'APPROVED', 'SENT', 'RESPONDED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outreach_channel') THEN
                CREATE TYPE outreach_channel AS ENUM ('EMAIL', 'LINKEDIN');
            END IF;
        END
        $$;
    """)

    # Check if tables already exist
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'game_studios')"))
    if result.scalar():
        return  # Tables already exist

    # Create tables using raw SQL to avoid enum creation issues
    op.execute("""
        CREATE TABLE game_studios (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL UNIQUE,
            size studio_size_enum NOT NULL DEFAULT 'INDIE',
            status studio_status_enum NOT NULL DEFAULT 'NEW',
            hq_city VARCHAR(100),
            hq_country VARCHAR(100),
            website_url TEXT,
            linkedin_url TEXT,
            twitter_url TEXT,
            app_store_url TEXT,
            play_store_url TEXT,
            notable_games TEXT[],
            genres TEXT[],
            download_count VARCHAR(50),
            revenue_estimate VARCHAR(100),
            employee_count INTEGER,
            has_live_ops BOOLEAN DEFAULT FALSE,
            is_hyper_casual BOOLEAN DEFAULT FALSE,
            is_publicly_traded BOOLEAN DEFAULT FALSE,
            parent_company VARCHAR(255),
            overview TEXT,
            data_source VARCHAR(100),
            trello_card_id VARCHAR(100),
            trello_card_url TEXT,
            tags JSONB DEFAULT '{}'::jsonb,
            priority INTEGER DEFAULT 5,
            score NUMERIC(5,2),
            last_contacted_at TIMESTAMPTZ,
            first_contacted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        );
        
        CREATE INDEX idx_game_studios_status ON game_studios(status);
        CREATE INDEX idx_game_studios_size ON game_studios(size);
        CREATE INDEX idx_game_studios_priority ON game_studios(priority);
    """)
    
    op.execute("""
        CREATE TABLE studio_contacts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            studio_id UUID NOT NULL REFERENCES game_studios(id) ON DELETE CASCADE,
            full_name VARCHAR(255) NOT NULL,
            title VARCHAR(255),
            role contact_role_enum,
            email VARCHAR(320),
            linkedin_url TEXT,
            twitter_url TEXT,
            is_primary BOOLEAN DEFAULT FALSE NOT NULL,
            is_decision_maker BOOLEAN DEFAULT FALSE,
            timezone VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        );
        
        CREATE INDEX idx_studio_contacts_studio ON studio_contacts(studio_id);
        CREATE INDEX idx_studio_contacts_role ON studio_contacts(role);
    """)
    
    op.execute("""
        CREATE TABLE studio_outreach (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            studio_id UUID NOT NULL REFERENCES game_studios(id) ON DELETE CASCADE,
            contact_id UUID REFERENCES studio_contacts(id) ON DELETE SET NULL,
            trello_card_id VARCHAR(100),
            subject VARCHAR(255),
            body TEXT,
            body_preview TEXT,
            personalization_notes TEXT,
            status outreach_msg_status NOT NULL DEFAULT 'DRAFT',
            channel outreach_channel,
            sent_at TIMESTAMPTZ,
            responded_at TIMESTAMPTZ,
            response_notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        );
        
        CREATE INDEX idx_studio_outreach_status ON studio_outreach(status);
    """)
    
    op.execute("""
        CREATE TABLE bdr_batches (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            batch_date DATE NOT NULL,
            target_count INTEGER NOT NULL DEFAULT 10,
            completed_count INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS bdr_batches")
    op.execute("DROP TABLE IF EXISTS studio_outreach")
    op.execute("DROP TABLE IF EXISTS studio_contacts")
    op.execute("DROP TABLE IF EXISTS game_studios")
    
    # Drop enums
    for enum_name in (
        "outreach_channel",
        "outreach_msg_status",
        "game_genre_enum",
        "contact_role_enum",
        "studio_status_enum",
        "studio_size_enum",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
