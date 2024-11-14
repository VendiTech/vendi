"""add-unique-constraint

Revision ID: 70d2b4369078
Revises: bd83bd5aa1bd
Create Date: 2024-11-14 12:20:26.038551

"""

from alembic import op

from mspy_vendi.db.migration_helpers import constraint_exists

# revision identifiers, used by Alembic.
revision = "70d2b4369078"
down_revision = "bd83bd5aa1bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not constraint_exists("uq_machine_impression_machine_id_impression_device_number"):
        op.create_unique_constraint(
            "uq_machine_impression_machine_id_impression_device_number",
            "machine_impression",
            ["machine_id", "impression_device_number"],
        )


def downgrade() -> None:
    if constraint_exists("uq_machine_impression_machine_id_impression_device_number"):
        op.drop_constraint(
            "uq_machine_impression_machine_id_impression_device_number", "machine_impression", type_="unique"
        )
