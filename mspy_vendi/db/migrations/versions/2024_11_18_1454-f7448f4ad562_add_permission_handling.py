"""add-permission-handling

Revision ID: f7448f4ad562
Revises: 70d2b4369078
Create Date: 2024-11-18 14:54:51.227602

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from mspy_vendi.db.migration_helpers import enum_exists, table_has_column

# revision identifiers, used by Alembic.
revision = "f7448f4ad562"
down_revision = "70d2b4369078"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not enum_exists("permission_db_enum"):
        op.execute("CREATE TYPE permission_db_enum AS ENUM ('any', 'read', 'create', 'update', 'delete');")

    if not table_has_column("user", "permissions"):
        op.add_column(
            "user",
            sa.Column(
                "permissions",
                postgresql.ARRAY(sa.Enum("any", "read", "create", "update", "delete", name="permission_db_enum")),
                server_default=sa.text("ARRAY['read'::permission_db_enum]"),
                nullable=False,
            ),
        )

    if table_has_column("user", "is_superuser"):
        op.drop_column("user", "is_superuser")
        op.add_column(
            "user",
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                sa.Computed(
                    "CASE WHEN role = 'admin' AND 'any' = ANY(permissions) THEN true ELSE false END",
                    persisted=True,
                ),
                nullable=False,
            ),
        )


def downgrade() -> None:
    if table_has_column("user", "permissions"):
        op.drop_column("user", "permissions")

    if table_has_column("user", "is_superuser"):
        op.drop_column("user", "is_superuser")
        op.add_column(
            "user",
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                server_default="false",
                nullable=False,
            ),
        )

    if enum_exists("permission_db_enum"):
        op.execute("DROP TYPE permission_db_enum")
