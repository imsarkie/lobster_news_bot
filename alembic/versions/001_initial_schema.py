"""initial schema: create sent_stories table

Revision ID: 001
Revises:
Create Date: 2026-04-21 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sent_stories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("story_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("story_id", name="uq_sent_stories_story_id"),
    )
    op.create_index("ix_sent_stories_story_id", "sent_stories", ["story_id"])


def downgrade() -> None:
    op.drop_index("ix_sent_stories_story_id", table_name="sent_stories")
    op.drop_table("sent_stories")
