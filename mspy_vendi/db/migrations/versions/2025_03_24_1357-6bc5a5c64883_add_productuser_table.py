"""add-ProductUser-table

Revision ID: 6bc5a5c64883
Revises: 8dc779d5df7a
Create Date: 2025-03-24 13:57:50.803083

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_exists

# revision identifiers, used by Alembic.
revision = "6bc5a5c64883"
down_revision = "8dc779d5df7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("product_user"):
        op.create_table(
            "product_user",
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column("product_id", sa.BigInteger(), nullable=True),
            sa.Column("user_id", sa.BigInteger(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("product_id", "user_id", name="uq_product_user_product_id_user_id"),
        )


def downgrade() -> None:
    if table_exists("product_user"):
        op.drop_table("product_user")
