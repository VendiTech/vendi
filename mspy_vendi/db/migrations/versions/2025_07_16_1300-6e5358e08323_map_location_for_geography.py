"""map_location_for_geography

Revision ID: 6e5358e08323
Revises: 920c0805fb0e
Create Date: 2025-07-16 13:00:30.587882

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_has_column

# revision identifiers, used by Alembic.
revision = "6e5358e08323"
down_revision = "920c0805fb0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_has_column("geography", "map_location"):
        op.add_column(
            "geography",
            sa.Column(
                "map_location", sa.String(length=255), nullable=True, comment="Identifier to proper location mapping"
            ),
        )


def downgrade() -> None:
    if table_has_column("geography", "map_location"):
        op.drop_column("geography", "map_location")
