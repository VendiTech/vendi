"""add-machine-impression-table

Revision ID: 97ad8930d432
Revises: bca541e263ff
Create Date: 2024-11-04 07:34:25.620513

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import constraint_exists, index_exists, table_exists, table_has_column

# revision identifiers, used by Alembic.
revision = "97ad8930d432"
down_revision = "bca541e263ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if constraint_exists("impression_machine_id_fkey"):
        op.drop_constraint("impression_machine_id_fkey", "impression", type_="foreignkey")

    if table_has_column("impression", "machine_id"):
        op.drop_column("impression", "machine_id")

    if table_has_column("impression", "id"):
        op.execute(sa.text("ALTER TABLE impression ALTER COLUMN id DROP IDENTITY"))
        op.alter_column(
            "impression",
            "id",
            existing_type=sa.BIGINT(),
            server_default=None,
            type_=sa.String(),
            existing_nullable=False,
        )

    if table_has_column("impression", "source_system_id"):
        op.alter_column(
            "impression",
            "source_system_id",
            existing_type=sa.BIGINT(),
            type_=sa.String(),
            existing_comment="ID of the impression in the source system",
            existing_nullable=False,
        )

    if not table_exists("machine_impression"):
        op.create_table(
            "machine_impression",
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("machine_id", sa.BigInteger(), nullable=False),
            sa.Column("impression_id", sa.String(), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["impression_id"], ["impression.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["machine_id"], ["machine.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not index_exists("machine_impression_machine_id"):
        op.create_index("idx_machine_impression_machine_id", "machine_impression", ["machine_id"])

    if not index_exists("machine_impression_impression_id"):
        op.create_index("idx_machine_impression_impression_id", "machine_impression", ["impression_id"])


def downgrade() -> None:
    if not table_has_column("impression", "machine_id"):
        op.add_column("impression", sa.Column("machine_id", sa.BIGINT(), autoincrement=False, nullable=False))

    if not constraint_exists("impression_machine_id_fkey"):
        op.create_foreign_key(
            "impression_machine_id_fkey",
            "impression",
            "machine",
            ["machine_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )

    if table_exists("machine_impression"):
        op.drop_table("machine_impression")

    if table_has_column("impression", "id"):
        op.alter_column(
            "impression",
            "id",
            existing_type=sa.String(),
            type_=sa.BIGINT(),
            existing_comment="ID of the impression in the source system",
            existing_nullable=False,
            drop_default=True,
        )

    if table_has_column("impression", "source_system_id"):
        op.alter_column(
            "impression",
            "source_system_id",
            existing_type=sa.String(),
            type_=sa.BIGINT(),
            existing_comment="ID of the impression in the source system",
            existing_nullable=False,
        )
