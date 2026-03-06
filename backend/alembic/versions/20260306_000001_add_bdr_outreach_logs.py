"""Add bdr_outreach_logs table.

Revision ID: 20260306_000001
Revises: 20250303_000001
Create Date: 2026-03-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260306_000001'
down_revision = 'b3b9e7a0f5f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'bdr_outreach_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('subject', sa.Text(), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['contact_id'], ['bdr_contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_bdr_outreach_logs_contact_id', 'bdr_outreach_logs', ['contact_id'])


def downgrade() -> None:
    op.drop_index('ix_bdr_outreach_logs_contact_id', table_name='bdr_outreach_logs')
    op.drop_table('bdr_outreach_logs')
