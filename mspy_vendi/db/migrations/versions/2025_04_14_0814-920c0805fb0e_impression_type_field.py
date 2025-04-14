"""impression_type_field

Revision ID: 920c0805fb0e
Revises: 90e33aaccc85
Create Date: 2025-04-14 08:14:21.745754

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import constraint_exists, enum_exists, table_has_column

# revision identifiers, used by Alembic.
revision = "920c0805fb0e"
down_revision = "90e33aaccc85"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not enum_exists("impression_entity_type_enum"):
        sa.Enum(
            "Impressions",
            "Near Zone",
            "Far Zone",
            "Immediate Zone",
            "Remote Zone",
            name="impression_entity_type_enum",
        ).create(op.get_bind())

    if not table_has_column("impression", "type"):
        op.add_column(
            "impression",
            sa.Column(
                "type",
                sa.Enum(
                    "Impressions",
                    "Near Zone",
                    "Far Zone",
                    "Immediate Zone",
                    "Remote Zone",
                    name="impression_entity_type_enum",
                ),
                server_default="Impressions",
                nullable=False,
            ),
        )

    if constraint_exists("uq_impression_source_system_id"):
        op.drop_constraint("uq_impression_source_system_id", "impression", type_="unique")

    if not constraint_exists("uq_impression_source_system_id_type"):
        op.create_unique_constraint("uq_impression_source_system_id_type", "impression", ["source_system_id", "type"])


def downgrade() -> None:
    if constraint_exists("uq_impression_source_system_id_type"):
        op.drop_constraint("uq_impression_source_system_id", "impression", type_="unique")

    if not constraint_exists("uq_impression_source_system_id"):
        op.create_unique_constraint("uq_impression_source_system_id", "impression", ["source_system_id"])

    if table_has_column("impression", "type"):
        op.drop_column("impression", "type")

    if enum_exists("impression_entity_type_enum"):
        op.execute("DROP TYPE impression_entity_type_enum")
