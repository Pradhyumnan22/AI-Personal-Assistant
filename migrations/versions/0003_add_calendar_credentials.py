"""Add Google Calendar OAuth credentials."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calendar_credentials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_uri", sa.String(300), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("calendar_credentials")
