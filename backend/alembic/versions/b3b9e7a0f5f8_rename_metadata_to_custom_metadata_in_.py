"""Rename metadata to custom_metadata in bdr_companies

Revision ID: b3b9e7a0f5f8
Revises: 20250303_000001
Create Date: 2026-03-03 07:39:18.535554

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3b9e7a0f5f8'
down_revision = '20250303_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Column was already renamed to custom_metadata in the initial schema.
    # This migration is a no-op to preserve the revision chain.
    pass


def downgrade() -> None:
    pass
