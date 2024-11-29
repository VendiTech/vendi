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
    if table_has_column("impressions", "temperature"):
        op.add_column(
            "impression", sa.Column("seconds_exposure", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )
        op.drop_column("impression", "temperature")

    if table_has_column("impressions", "rainfall"):
        op.add_column(
            "impression", sa.Column("advert_playouts", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )
        op.drop_column("impression", "rainfall")

    if table_has_column("impressions", "source_system_id"):
        op.alter_column(
            "impression",
            "source_system_id",
            existing_type=sa.VARCHAR(),
            comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
            """,
            existing_comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
            """,
            existing_nullable=False,
        )


def downgrade() -> None:
    if table_has_column("impressions", "advert_playouts"):
        op.add_column("impression", sa.Column("rainfall", sa.INTEGER(), autoincrement=False, nullable=False))
        op.drop_column("impression", "advert_playouts")

    if table_has_column("impressions", "seconds_exposure"):
        op.add_column("impression", sa.Column("temperature", sa.INTEGER(), autoincrement=False, nullable=False))
        op.drop_column("impression", "seconds_exposure")

    if table_has_column("impressions", "source_system_id"):
        op.alter_column(
            "impression",
            "source_system_id",
            existing_type=sa.VARCHAR(),
            comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
            """,
            existing_comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
            """,
            existing_nullable=False,
        )
