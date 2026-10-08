"""Concurrent append-only reform storage against real PostgreSQL."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any

import pytest
from sqlalchemy import create_engine, event

from poltika.common.errors import ImmutableRecordError
from poltika.scenarios.reform_record import reform_run_id, reform_scenario_id, results_sha256
from poltika.scenarios.store import ReformRun, ReformScenario, ScenarioStore

pytestmark = pytest.mark.postgres


def _definition(label: str) -> dict[str, Any]:
    # Storage-only fixture; no statutory values or policy calculation.
    return {"synthetic": True, "options": [{"label": label, "reform": {"test": label}}]}


def _synchronise_inserts(engine: Any, table: str) -> None:
    barrier = Barrier(2)

    @event.listens_for(engine, "before_cursor_execute")
    def before_insert(
        conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
    ) -> None:
        if statement.startswith(f"INSERT INTO {table} "):
            # Both writers reach their first insert before either inserts.
            # With SELECT-then-INSERT both have already observed no row,
            # so this deterministically exercises the duplicate-key race.
            barrier.wait(timeout=10)


def test_concurrent_duplicate_scenarios_keep_the_first_labels(database_url: str) -> None:
    engine = create_engine(database_url)
    store = ScenarioStore(engine)
    definition = _definition("concurrent-scenario")
    scenario_id = reform_scenario_id(definition)
    _synchronise_inserts(engine, "reform_scenario")

    def save(title: str) -> ReformScenario:
        return store.save_reform_scenario(scenario_id, definition, title, f"Description: {title}")

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(save, title) for title in ("First candidate", "Second candidate")]
        saved = [future.result(timeout=20) for future in futures]

    assert saved[0] == saved[1] == store.get_reform_scenario(scenario_id)
    assert saved[0].title in ("First candidate", "Second candidate")
    assert saved[0].description == f"Description: {saved[0].title}"
    engine.dispose()


def test_concurrent_duplicate_runs_are_stored_once(database_url: str) -> None:
    engine = create_engine(database_url)
    store = ScenarioStore(engine)
    definition = _definition("concurrent-run")
    scenario_id = reform_scenario_id(definition)
    store.save_reform_scenario(scenario_id, definition, "Concurrent run", "")
    results = {"synthetic": True, "workbench": {"source_commit": None}, "distribution": []}
    option_ids = ("0" * 64,)
    run_id = reform_run_id(scenario_id, option_ids, results_sha256=results_sha256(results))
    _synchronise_inserts(engine, "reform_run")

    def save() -> ReformRun:
        return store.save_reform_run(run_id, scenario_id, option_ids, results)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(save) for _ in range(2)]
        saved = [future.result(timeout=20) for future in futures]

    assert saved[0] == saved[1] == store.get_reform_run(run_id)
    assert [run.run_id for run in store.runs_of(scenario_id)] == [run_id]
    engine.dispose()


def test_duplicate_ids_still_refuse_different_content(database_url: str) -> None:
    engine = create_engine(database_url)
    store = ScenarioStore(engine)
    definition = _definition("immutable-scenario")
    scenario_id = reform_scenario_id(definition)
    store.save_reform_scenario(scenario_id, definition, "Original", "")
    with pytest.raises(ImmutableRecordError, match="different definition"):
        store.save_reform_scenario(scenario_id, _definition("different"), "Changed", "")

    results = {"synthetic": True, "original": True}
    option_ids = ("0" * 64,)
    run_id = reform_run_id(scenario_id, option_ids, results_sha256=results_sha256(results))
    store.save_reform_run(run_id, scenario_id, option_ids, results)
    with pytest.raises(ImmutableRecordError, match="different results_json"):
        store.save_reform_run(run_id, scenario_id, option_ids, {"synthetic": True, "original": False})
    assert store.get_reform_run(run_id).results == results
    engine.dispose()
