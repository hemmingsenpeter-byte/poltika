"""Task 32 baseline: scenario, run and artifact tables (ADR-0013).

Revision ID: 0001
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scenario",
        sa.Column("scenario_id", sa.String(64), primary_key=True),
        sa.Column("record_json", sa.Text, nullable=False),
    )
    op.create_table(
        "artifact",
        sa.Column("sha256", sa.String(64), primary_key=True),
        sa.Column("content", sa.LargeBinary, nullable=False),
    )
    op.create_table(
        "run",
        sa.Column("result_id", sa.String(64), primary_key=True),
        sa.Column("scenario_id", sa.String(64), sa.ForeignKey("scenario.scenario_id"), nullable=False),
        sa.Column("manifest_json", sa.Text, nullable=False),
        sa.Column("result_json", sa.Text, nullable=False),
        sa.Column("reproducible", sa.Boolean, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("run")
    op.drop_table("artifact")
    op.drop_table("scenario")
