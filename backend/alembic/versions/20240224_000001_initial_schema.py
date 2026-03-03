"""Initial CRM schema."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20240224_000001"
down_revision = None
branch_labels = None
depends_on = None


priority_enum = sa.Enum("A", "B", "C", name="priority_enum")
fund_status_enum = sa.Enum(
    "NEW",
    "RESEARCHING",
    "READY",
    "APPROVED",
    "SENT",
    "FOLLOW_UP",
    "CLOSED",
    name="fund_status_enum",
)
packet_status_enum = sa.Enum(
    "QUEUED",
    "AWAITING_APPROVAL",
    "APPROVED",
    "SENT",
    "FOLLOW_UP",
    "CLOSED",
    name="packet_status_enum",
)
outreach_channel_enum = sa.Enum(
    "EMAIL",
    "INTRO",
    "SOCIAL",
    "MEETING",
    name="outreach_channel_enum",
)
outreach_status_enum = sa.Enum(
    "DRAFT",
    "SENT",
    "RESPONDED",
    "FAILED",
    "CLOSED",
    name="outreach_status_enum",
)
meeting_status_enum = sa.Enum(
    "PLANNED",
    "COMPLETED",
    "NO_SHOW",
    "CANCELLED",
    name="meeting_status_enum",
)
note_visibility_enum = sa.Enum("INTERNAL", "EXTERNAL", name="note_visibility_enum")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create enums using raw SQL with IF NOT EXISTS to avoid conflicts
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_enum') THEN
                CREATE TYPE priority_enum AS ENUM ('A', 'B', 'C');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fund_status_enum') THEN
                CREATE TYPE fund_status_enum AS ENUM ('NEW', 'RESEARCHING', 'READY', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'packet_status_enum') THEN
                CREATE TYPE packet_status_enum AS ENUM ('QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outreach_channel_enum') THEN
                CREATE TYPE outreach_channel_enum AS ENUM ('EMAIL', 'INTRO', 'SOCIAL', 'MEETING');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outreach_status_enum') THEN
                CREATE TYPE outreach_status_enum AS ENUM ('DRAFT', 'SENT', 'RESPONDED', 'FAILED', 'CLOSED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'meeting_status_enum') THEN
                CREATE TYPE meeting_status_enum AS ENUM ('PLANNED', 'COMPLETED', 'NO_SHOW', 'CANCELLED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'note_visibility_enum') THEN
                CREATE TYPE note_visibility_enum AS ENUM ('INTERNAL', 'EXTERNAL');
            END IF;
        END
        $$;
    """)

    op.create_table(
        "funds",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("firm_type", sa.String(length=100)),
        sa.Column("hq_city", sa.String(length=100)),
        sa.Column("hq_region", sa.String(length=100)),
        sa.Column("hq_country", sa.String(length=100)),
        sa.Column("stage_focus", postgresql.ARRAY(sa.String())),
        sa.Column("check_size_min", sa.Numeric(18, 2)),
        sa.Column("check_size_max", sa.Numeric(18, 2)),
        sa.Column("check_size_currency", sa.String(length=10)),
        sa.Column("target_countries", postgresql.ARRAY(sa.String())),
        sa.Column("website_url", sa.Text()),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("twitter_url", sa.Text()),
        sa.Column("funding_requirements", sa.Text()),
        sa.Column("overview", sa.Text()),
        sa.Column("contact_email", sa.String(length=320)),
        sa.Column("score", sa.Numeric(5, 2)),
        sa.Column("priority", priority_enum, nullable=False, server_default="B"),
        sa.Column("status", fund_status_enum, nullable=False, server_default="NEW"),
        sa.Column("data_source", sa.String(length=100)),
        sa.Column("source_row_id", sa.String(length=100)),
        sa.Column("tags", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True)),
        sa.Column("first_contacted_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "contacts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "fund_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("funds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255)),
        sa.Column("email", sa.String(length=320)),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("timezone", sa.String(length=100)),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "packets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "fund_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("funds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("trello_card_id", sa.String(length=100)),
        sa.Column("trello_card_url", sa.Text()),
        sa.Column("status", packet_status_enum, nullable=False, server_default="QUEUED"),
        sa.Column("priority", priority_enum, nullable=False, server_default="B"),
        sa.Column("score_snapshot", sa.Numeric(5, 2)),
        sa.Column("created_by", sa.String(length=100)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("follow_up_due", sa.DateTime(timezone=True)),
        sa.Column("crm_status", postgresql.JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "outreach_attempts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "packet_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("packets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
        ),
        sa.Column("channel", outreach_channel_enum, nullable=False),
        sa.Column("status", outreach_status_enum, nullable=False),
        sa.Column("subject", sa.String(length=255)),
        sa.Column("body_preview", sa.Text()),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "meetings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "fund_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("funds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "packet_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("packets.id", ondelete="SET NULL"),
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("status", meeting_status_enum, nullable=False),
        sa.Column("meeting_url", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "notes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "fund_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("funds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
        ),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("visibility", note_visibility_enum, nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("payload", postgresql.JSONB),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    for table in (
        "audit_log",
        "notes",
        "meetings",
        "outreach_attempts",
        "packets",
        "contacts",
        "funds",
    ):
        op.drop_table(table)

    bind = op.get_bind()
    for enum in (
        note_visibility_enum,
        meeting_status_enum,
        outreach_status_enum,
        outreach_channel_enum,
        packet_status_enum,
        fund_status_enum,
        priority_enum,
    ):
        enum.drop(bind, checkfirst=True)
