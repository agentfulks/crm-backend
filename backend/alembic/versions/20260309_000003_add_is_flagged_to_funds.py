"""Add is_flagged to funds table.

Revision ID: 20260309_000003
Revises: 20260309_000002
Create Date: 2026-03-09 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260309_000003'
down_revision = '20260309_000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('funds', sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='FALSE'))
    op.alter_column('funds', 'is_flagged', server_default=None)


def downgrade() -> None:
    op.drop_column('funds', 'is_flagged')
