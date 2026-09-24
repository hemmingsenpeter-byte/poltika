"""Alembic environment for the Task 32 store (ADR-0013). Configured
programmatically by `poltika.scenarios.store.migrate()`; no alembic.ini."""

from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool

from poltika.scenarios.store import metadata

config = context.config
connectable = engine_from_config(
    config.get_section(config.config_ini_section) or {}, prefix="sqlalchemy.", poolclass=pool.NullPool
)
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        context.run_migrations()
