"""Task B0.1.2 (ADR-0023): reform scenarios, their runs, and run times.

Adds `reform_scenario` and `reform_run` (append-only, like 0001's tables)
and nullable `created_at` and `provenance_json` on `run`. Rows stored before
this migration keep both NULL: their time and report were not retained,
and neither is invented.

Revision ID: 0002
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "run",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Only rows written from now on get a time.
    op.alter_column("run", "created_at", server_default=sa.func.now())
    op.add_column("run", sa.Column("provenance_json", sa.Text, nullable=True))
    op.create_table(
        "reform_scenario",
        sa.Column("scenario_id", sa.String(64), primary_key=True),
        sa.Column("definition_json", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "reform_run",
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column(
            "scenario_id",
            sa.String(64),
            sa.ForeignKey("reform_scenario.scenario_id"),
            nullable=False,
        ),
        sa.Column("option_run_ids_json", sa.Text, nullable=False),
        sa.Column("results_json", sa.Text, nullable=False),
        sa.Column("results_sha256", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("reform_run_scenario_id", "reform_run", ["scenario_id"])


def downgrade() -> None:
    op.drop_index("reform_run_scenario_id", table_name="reform_run")
    op.drop_table("reform_run")
    op.drop_table("reform_scenario")
    op.drop_column("run", "provenance_json")
    op.drop_column("run", "created_at")
