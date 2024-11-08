"""update-total-impression

Revision ID: bd83bd5aa1bd
Revises: 97ad8930d432
Create Date: 2024-11-08 09:13:08.724238

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_has_column

# revision identifiers, used by Alembic.
revision = "bd83bd5aa1bd"
down_revision = "97ad8930d432"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if table_has_column("impression", "total_impressions"):
        op.alter_column(
            "impression",
            "total_impressions",
            existing_type=sa.BIGINT(),
            type_=sa.DECIMAL(precision=10, scale=1),
            existing_comment="Total number of impressions",
            existing_nullable=False,
        )


def downgrade() -> None:
    if table_has_column("impression", "total_impressions"):
        op.alter_column(
            "impression",
            "total_impressions",
            existing_type=sa.DECIMAL(precision=10, scale=1),
            type_=sa.BIGINT(),
            existing_comment="Total number of impressions",
            existing_nullable=False,
        )
