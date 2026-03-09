"""Add kanban_cards table.

Revision ID: 20260308_000001
Revises: 20260307_000002
Create Date: 2026-03-08 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260308_000001'
down_revision = '20260307_000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'kanban_cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('column', sa.String(length=50), nullable=False, server_default='backlog'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('card_type', sa.String(length=50), nullable=False, server_default='custom'),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('source_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', sa.String(length=10), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kanban_cards_column', 'kanban_cards', ['column'], unique=False)
    op.create_index('ix_kanban_cards_card_type', 'kanban_cards', ['card_type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_kanban_cards_card_type', table_name='kanban_cards')
    op.drop_index('ix_kanban_cards_column', table_name='kanban_cards')
    op.drop_table('kanban_cards')
