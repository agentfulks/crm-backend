"""Add meetings and notes tables.

Revision ID: 20250225_000003
Revises: 20250225_000002
Create Date: 2026-02-25 18:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250225_000003'
down_revision = '20250225_000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums using raw SQL with IF NOT EXISTS
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'meeting_status_enum') THEN
                CREATE TYPE meeting_status_enum AS ENUM ('PLANNED', 'COMPLETED', 'NO_SHOW', 'CANCELLED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'note_visibility_enum') THEN
                CREATE TYPE note_visibility_enum AS ENUM ('INTERNAL', 'EXTERNAL');
            END IF;
        END
        $$;
    """)

    # Create meetings table
    op.create_table('meetings',
        sa.Column('id', sa.String(length=255), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column('fund_id', sa.String(length=255), nullable=False),
        sa.Column('contact_id', sa.String(length=255), nullable=True),
        sa.Column('packet_id', sa.String(length=255), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PLANNED', 'COMPLETED', 'NO_SHOW', 'CANCELLED', name='meeting_status_enum'), nullable=False),
        sa.Column('meeting_url', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['fund_id'], ['funds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['packet_id'], ['packets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.String(length=255), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column('fund_id', sa.String(length=255), nullable=False),
        sa.Column('contact_id', sa.String(length=255), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('visibility', sa.Enum('INTERNAL', 'EXTERNAL', name='note_visibility_enum'), nullable=False),
        sa.Column('pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['fund_id'], ['funds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_meetings_fund_id', 'meetings', ['fund_id'])
    op.create_index('idx_meetings_contact_id', 'meetings', ['contact_id'])
    op.create_index('idx_meetings_status', 'meetings', ['status'])
    op.create_index('idx_meetings_scheduled_at', 'meetings', ['scheduled_at'])
    op.create_index('idx_notes_fund_id', 'notes', ['fund_id'])
    op.create_index('idx_notes_contact_id', 'notes', ['contact_id'])
    op.create_index('idx_notes_pinned', 'notes', ['pinned'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('idx_notes_pinned', table_name='notes')
    op.drop_index('idx_notes_contact_id', table_name='notes')
    op.drop_index('idx_notes_fund_id', table_name='notes')
    op.drop_index('idx_meetings_scheduled_at', table_name='meetings')
    op.drop_index('idx_meetings_status', table_name='meetings')
    op.drop_index('idx_meetings_contact_id', table_name='meetings')
    op.drop_index('idx_meetings_fund_id', table_name='meetings')
    op.drop_table('notes')
    op.drop_table('meetings')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS note_visibility_enum")
    op.execute("DROP TYPE IF EXISTS meeting_status_enum")
