"""Drop game_studios tables (using bdr_* instead)."""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20250225_000002"
down_revision = "20250225_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the game_studios tables (keeping bdr_* and VC tables)
    op.execute("DROP TABLE IF EXISTS studio_outreach")
    op.execute("DROP TABLE IF EXISTS studio_contacts")
    op.execute("DROP TABLE IF EXISTS game_studios")
    
    # Drop the enums if they exist
    for enum_name in (
        "outreach_channel",
        "outreach_msg_status",
        "game_genre_enum",
        "contact_role_enum",
        "studio_status_enum",
        "studio_size_enum",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")


def downgrade() -> None:
    # Cannot restore dropped tables easily - would need to recreate from 20250225_000001
    pass
