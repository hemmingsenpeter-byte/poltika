"""Task 14: migration 0003 (nullable `reform_run.manifest_json`) against a
fresh database on the throwaway PostgreSQL server: upgrade over a row that
already exists at 0002, and downgrade."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

import poltika.scenarios.store as store_module

pytestmark = pytest.mark.postgres

SCENARIO = "a" * 64
RUN = "b" * 64


def _config(url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(Path(store_module.__file__).parent / "migrations"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture
def fresh_url(database_url: str) -> str:
    """An empty database on the same server, so the session database is not
    migrated backwards under other tests."""
    name = "t14_migration"
    admin = create_engine(database_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    admin.dispose()
    return make_url(database_url).set(database=name).render_as_string(hide_password=False)


def _columns(url: str) -> list[str]:
    engine = create_engine(url)
    try:
        return [c["name"] for c in inspect(engine).get_columns("reform_run")]
    finally:
        engine.dispose()


def test_upgrade_keeps_a_0002_row_with_a_null_manifest_and_downgrade_keeps_the_data(
    fresh_url: str,
) -> None:
    config = _config(fresh_url)
    command.upgrade(config, "0002")
    assert "manifest_json" not in _columns(fresh_url)
    engine = create_engine(fresh_url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO reform_scenario (scenario_id, definition_json, title, description) "
                "VALUES (:s, '{}', 't', 'd')"
            ),
            {"s": SCENARIO},
        )
        conn.execute(
            text(
                "INSERT INTO reform_run (run_id, scenario_id, option_run_ids_json, "
                "results_json, results_sha256) VALUES (:r, :s, '[]', :j, :h)"
            ),
            {"r": RUN, "s": SCENARIO, "j": '{"x":1}', "h": "c" * 64},
        )

    command.upgrade(config, "head")
    assert "manifest_json" in _columns(fresh_url)
    with engine.connect() as conn:
        row = conn.execute(text("SELECT results_json, manifest_json FROM reform_run")).one()
    assert row.results_json == '{"x":1}'
    assert row.manifest_json is None  # not backfilled

    command.downgrade(config, "0002")
    assert "manifest_json" not in _columns(fresh_url)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT results_json FROM reform_run")).scalar_one() == '{"x":1}'
    command.upgrade(config, "head")
    assert "manifest_json" in _columns(fresh_url)
    engine.dispose()
