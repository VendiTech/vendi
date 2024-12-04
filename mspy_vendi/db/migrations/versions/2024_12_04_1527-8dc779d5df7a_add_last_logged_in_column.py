"""add-last-logged-in-column

Revision ID: 8dc779d5df7a
Revises: 2f09e80bc2cf
Create Date: 2024-12-04 15:27:54.052442

"""

import sqlalchemy as sa
from alembic import op

from mspy_vendi.db.migration_helpers import table_has_column

# revision identifiers, used by Alembic.
revision = "8dc779d5df7a"
down_revision = "2f09e80bc2cf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_has_column("user", "last_logged_in"):
        op.add_column("user", sa.Column("last_logged_in", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    if table_has_column("user", "last_logged_in"):
        op.drop_column("user", "last_logged_in")
