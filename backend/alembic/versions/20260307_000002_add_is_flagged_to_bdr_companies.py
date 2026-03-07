"""Add is_flagged to bdr_companies.

Revision ID: 20260307_000002
Revises: 20260307_000001
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa

revision = '20260307_000002'
down_revision = '20260307_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'bdr_companies',
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('bdr_companies', 'is_flagged')
