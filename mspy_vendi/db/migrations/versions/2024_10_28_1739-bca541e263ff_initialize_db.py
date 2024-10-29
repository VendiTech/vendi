"""initialize-db

Revision ID: bca541e263ff
Revises:
Create Date: 2024-10-28 17:39:04.285551

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import enum_exists, index_exists, table_exists

# revision identifiers, used by Alembic.
revision = "bca541e263ff"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("geography"):
        op.create_table(
            "geography",
            sa.Column("name", sa.String(length=255), nullable=False, comment="Name of the geography"),
            sa.Column("postcode", sa.String(length=255), nullable=True, comment="Name of the geography"),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_geography_name"),
        )

    if not table_exists("product_category"):
        op.create_table(
            "product_category",
            sa.Column("name", sa.String(length=255), nullable=False, comment="Name of the product category"),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("user"):
        op.create_table(
            "user",
            sa.Column("firstname", sa.String(length=100), nullable=False),
            sa.Column("lastname", sa.String(length=100), nullable=False),
            sa.Column("company_name", sa.String(length=100), nullable=True),
            sa.Column("job_title", sa.String(length=100), nullable=True),
            sa.Column("role", sa.Enum("admin", "user", name="role_db_enum"), nullable=False),
            sa.Column("phone_number", sa.String(), nullable=True),
            sa.Column("status", sa.Enum("ACTIVE", "SUSPENDED", "DELETED", name="status_db_enum"), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("hashed_password", sa.String(length=1024), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("is_superuser", sa.Boolean(), nullable=False),
            sa.Column("is_verified", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not index_exists("ix_user_email"):
        op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    if not table_exists("machine"):
        op.create_table(
            "machine",
            sa.Column("name", sa.String(length=255), nullable=False, comment="Name of the machine"),
            sa.Column("geography_id", sa.BigInteger(), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["geography_id"], ["geography.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("product"):
        op.create_table(
            "product",
            sa.Column("name", sa.String(length=255), nullable=False, comment="Name of the product"),
            sa.Column("price", sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column("product_category_id", sa.BigInteger(), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["product_category_id"], ["product_category.id"], onupdate="CASCADE", ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("impression"):
        op.create_table(
            "impression",
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("total_impressions", sa.BigInteger(), nullable=False, comment="Total number of impressions"),
            sa.Column("temperature", sa.Integer(), nullable=False),
            sa.Column("rainfall", sa.Integer(), nullable=False),
            sa.Column("source_system", sa.String(length=50), nullable=False, comment="Name of the source system"),
            sa.Column(
                "source_system_id", sa.BigInteger(), nullable=False, comment="ID of the impression in the source system"
            ),
            sa.Column("machine_id", sa.BigInteger(), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["machine_id"], ["machine.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("machine_user"):
        op.create_table(
            "machine_user",
            sa.Column("machine_id", sa.BigInteger(), nullable=True),
            sa.Column("user_id", sa.BigInteger(), nullable=True),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["machine_id"], ["machine.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("machine_id", "user_id", name="uq_machine_user_machine_id_user_id"),
        )

    if not table_exists("sale"):
        op.create_table(
            "sale",
            sa.Column("sale_date", sa.Date(), nullable=False),
            sa.Column("sale_time", sa.Time(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("source_system", sa.String(length=50), nullable=False, comment="Name of the source system"),
            sa.Column(
                "source_system_id", sa.BigInteger(), nullable=False, comment="ID of the sale in the source system"
            ),
            sa.Column("product_id", sa.BigInteger(), nullable=False),
            sa.Column("machine_id", sa.BigInteger(), nullable=False),
            sa.Column("id", sa.BigInteger(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["machine_id"], ["machine.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    if table_exists("sale"):
        op.drop_table("sale")

    if table_exists("machine_user"):
        op.drop_table("machine_user")

    if table_exists("impression"):
        op.drop_table("impression")

    if table_exists("product"):
        op.drop_table("product")

    if table_exists("machine"):
        op.drop_table("machine")

    if table_exists("user"):
        op.drop_index("ix_user_email", table_name="user")

    if table_exists("user"):
        op.drop_table("user")

    if table_exists("product_category"):
        op.drop_table("product_category")

    if table_exists("geography"):
        op.drop_table("geography")

    if enum_exists("role_db_enum"):
        op.execute("DROP TYPE role_db_enum")

    if enum_exists("status_db_enum"):
        op.execute("DROP TYPE status_db_enum")
