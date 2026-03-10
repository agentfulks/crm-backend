"""Add template_type to email_templates table.

Revision ID: 20260309_000004
Revises: 20260309_000003
Create Date: 2026-03-09 00:00:04.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260309_000004'
down_revision = '20260309_000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'email_templates',
        sa.Column('template_type', sa.String(length=20), nullable=False, server_default='studio'),
    )
    op.alter_column('email_templates', 'template_type', server_default=None)


def downgrade() -> None:
    op.drop_column('email_templates', 'template_type')
