"""entity_log_model

Revision ID: 8f93580f5a06
Revises: 6e5358e08323
Create Date: 2025-07-27 12:01:21.108777

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from mspy_vendi.db.migration_helpers import table_exists

# revision identifiers, used by Alembic.
revision = "8f93580f5a06"
down_revision = "6e5358e08323"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("entity_log"):
        op.create_table(
            "entity_log",
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "entity_type",
                sa.Enum("Geography", "Product Category", "Product", "Sale", "Machine", name="entity_type_enum"),
                nullable=False,
            ),
            sa.Column(
                "old_value",
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column(
                "new_value",
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    if table_exists("entity_log"):
        op.drop_table("entity_log")
