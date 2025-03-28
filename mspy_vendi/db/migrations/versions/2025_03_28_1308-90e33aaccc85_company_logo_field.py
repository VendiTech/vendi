"""company_logo_field

Revision ID: 90e33aaccc85
Revises: 6bc5a5c64883
Create Date: 2025-03-28 13:08:19.840274

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_has_column

# revision identifiers, used by Alembic.
revision = "90e33aaccc85"
down_revision = "6bc5a5c64883"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_has_column("user", "company_logo_image"):
        op.add_column("user", sa.Column("company_logo_image", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    if table_has_column("user", "company_logo_image"):
        op.drop_column("user", "company_logo_image")
