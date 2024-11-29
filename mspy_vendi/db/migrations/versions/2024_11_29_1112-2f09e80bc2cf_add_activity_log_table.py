"""add-activity-log-table

Revision ID: 2f09e80bc2cf
Revises: a726039113cd
Create Date: 2024-11-29 11:12:42.109664

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from mspy_vendi.db.migration_helpers import enum_exists, index_exists, table_exists

# revision identifiers, used by Alembic.
revision = "2f09e80bc2cf"
down_revision = "a726039113cd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("activity_log"):
        op.create_table(
            "activity_log",
            sa.Column("user_id", sa.BigInteger(), nullable=True),
            sa.Column(
                "event_type",
                sa.Enum(
                    "user_register",
                    "user_email_verified",
                    "user_forgot_password",
                    "user_reset_password",
                    "user_deleted",
                    "user_edited",
                    "user_schedule_creation",
                    "user_schedule_deletion",
                    name="event_type_enum",
                ),
                nullable=False,
            ),
            sa.Column(
                "event_context",
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], onupdate="CASCADE", ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not index_exists("ix_activity_log_user_id"):
        op.create_index("ix_activity_log_user_id", "activity_log", ["user_id"], unique=False)


def downgrade() -> None:
    if table_exists("activity_log"):
        op.drop_table("activity_log")

    if enum_exists("event_type_enum"):
        op.execute("DROP TYPE event_type_enum")
