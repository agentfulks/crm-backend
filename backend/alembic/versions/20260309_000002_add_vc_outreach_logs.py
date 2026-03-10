"""Add vc_outreach_logs table.

Revision ID: 20260309_000002
Revises: 20260309_000001
Create Date: 2026-03-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260309_000002'
down_revision = '20260309_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # contacts.id is character varying, so contact_id must also be VARCHAR
    op.create_table(
        'vc_outreach_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column(
            'contact_id',
            sa.String(36),
            sa.ForeignKey('contacts.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('subject', sa.Text, nullable=True),
        sa.Column('body', sa.Text, nullable=True),
        sa.Column('sent_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_vc_outreach_logs_contact_id', 'vc_outreach_logs', ['contact_id'])


def downgrade() -> None:
    op.drop_index('ix_vc_outreach_logs_contact_id', table_name='vc_outreach_logs')
    op.drop_table('vc_outreach_logs')
