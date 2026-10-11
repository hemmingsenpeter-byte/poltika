"""Task 14: a typed manifest beside each reform run.

Adds a nullable `manifest_json` to `reform_run`. Runs stored before this
migration keep it NULL: their manifest was not retained, and none is
invented or backfilled.

Revision ID: 0003
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reform_run", sa.Column("manifest_json", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("reform_run", "manifest_json")
