"""Add email_templates table.

Revision ID: 20250303_000001
Revises: 20250225_000003
Create Date: 2025-03-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250303_000001"
down_revision = "20250225_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create email_templates table
    op.create_table(
        "email_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("variables", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
        sa.Column("usage_count", sa.Integer, server_default=sa.text("0"), nullable=False),
    )
    
    # Create index on category
    op.create_index("idx_email_templates_category", "email_templates", ["category"])
    op.create_index("idx_email_templates_is_active", "email_templates", ["is_active"])
    op.create_index("idx_email_templates_is_default", "email_templates", ["is_default"])
    
    # Insert default templates
    op.execute("""
        INSERT INTO email_templates (name, description, category, subject, body, is_default, created_by)
        VALUES 
        (
            'Partnership Introduction',
            'Standard partnership outreach email',
            'introduction',
            'Partnership opportunity - {{studio_name}}',
            'Hi {{first_name}},\n\nI''m reaching out from our platform - we build tools that help mobile game publishers like {{studio_name}} scale operations and improve efficiency.\n\nWe work with studios to:\n• Increase retention through automated live ops\n• Reduce manual campaign management overhead\n• Scale live title portfolios without adding headcount\n• Streamline multi-platform publishing workflows\n\nI''d love to explore if there''s a fit for {{studio_name}}. Worth a brief conversation?\n\nBest,\n{{my_name}}',
            true,
            'system'
        ),
        (
            'Art Tools Introduction',
            'Outreach for art department tools',
            'art_product',
            'Art pipeline optimization for {{studio_name}}',
            'Hi {{first_name}},\n\nI noticed {{studio_name}} has been producing impressive work. I''m reaching out about tools that can help your art team work more efficiently.\n\nOur platform helps art teams:\n• Reduce asset iteration time by 40%\n• Automate repetitive tasks\n• Improve collaboration between artists and developers\n• Maintain consistent art quality at scale\n\nWould you be open to a quick conversation about how this might help {{studio_name}}?\n\nBest,\n{{my_name}}',
            false,
            'system'
        ),
        (
            'LiveOps Tools',
            'Outreach for LiveOps and monetization',
            'liveops',
            'Scaling LiveOps at {{studio_name}}',
            'Hi {{first_name}},\n\nWith {{studio_name}}''s focus on live games, I wanted to reach out about tools that can help your LiveOps team drive better engagement and monetization.\n\nOur platform helps LiveOps teams:\n• Launch events 3x faster\n• A/B test content in real-time\n• Automate player segmentation\n• Increase D7 retention by 25%\n\nWorth exploring how this could work for {{studio_name}}?\n\nBest,\n{{my_name}}',
            false,
            'system'
        )
    """)


def downgrade() -> None:
    op.drop_index("idx_email_templates_is_default", table_name="email_templates")
    op.drop_index("idx_email_templates_is_active", table_name="email_templates")
    op.drop_index("idx_email_templates_category", table_name="email_templates")
    op.drop_table("email_templates")
