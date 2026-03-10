"""Add bdr-compatible fields to contacts table.

Revision ID: 20260309_000001
Revises: 20260308_000001
Create Date: 2026-03-09 00:00:01.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '20260309_000001'
down_revision = '20260308_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('contacts', sa.Column('phone', sa.String(50), nullable=True))
    op.add_column('contacts', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('contacts', sa.Column('seniority_level', sa.String(50), nullable=True))
    op.add_column('contacts', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('contacts', sa.Column('last_contacted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contacts', sa.Column('is_flagged', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('contacts', 'is_flagged')
    op.drop_column('contacts', 'last_contacted_at')
    op.drop_column('contacts', 'email_verified')
    op.drop_column('contacts', 'seniority_level')
    op.drop_column('contacts', 'department')
    op.drop_column('contacts', 'phone')
