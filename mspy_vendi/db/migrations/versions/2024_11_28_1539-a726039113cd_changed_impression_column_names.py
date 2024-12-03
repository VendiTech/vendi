"""changed-impression-column-names

Revision ID: a726039113cd
Revises: f7448f4ad562
Create Date: 2024-11-28 15:39:16.743657

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_has_column

# revision identifiers, used by Alembic.
revision = "a726039113cd"
down_revision = "f7448f4ad562"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if table_has_column("impression", "temperature"):
        op.drop_column("impression", "temperature")

    if not table_has_column("impression", "seconds_exposure"):
        op.add_column(
            "impression", sa.Column("seconds_exposure", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )

    if table_has_column("impression", "rainfall"):
        op.drop_column("impression", "rainfall")

    if not table_has_column("impression", "advert_playouts"):
        op.add_column(
            "impression", sa.Column("advert_playouts", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )


def downgrade() -> None:
    if table_has_column("impression", "advert_playouts"):
        op.drop_column("impression", "advert_playouts")

    if not table_has_column("impression", "rainfall"):
        op.add_column(
            "impression",
            sa.Column("rainfall", sa.INTEGER(), autoincrement=False, nullable=False, server_default=sa.text("0")),
        )

    if table_has_column("impression", "seconds_exposure"):
        op.drop_column("impression", "seconds_exposure")

    if not table_has_column("impression", "temperature"):
        op.add_column(
            "impression",
            sa.Column("temperature", sa.INTEGER(), autoincrement=False, nullable=False, server_default=sa.text("0")),
        )
