"""Task 14: the reform run manifest and the replay check, against a throwaway
real PostgreSQL server. Storage and comparison only: no statutory value."""

from __future__ import annotations

import os
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.household import running_code_identity
from poltika.api.main import app
from poltika.api.microsim import AS_POLICY_DIR, WFF_POLICY_DIR
from poltika.scenarios import store as store_module
from poltika.scenarios.reform_record import reform_run_id, results_sha256
from poltika.scenarios.store import ScenarioStore
from poltika.semantics.population import PopulationDataset
from tests.unit.api.test_v1_scenarios import _blocks, _create, stored  # noqa: F401 (fixture)
from tests.unit.api.test_workbench_api import configured  # noqa: F401 (fixture)

client = TestClient(app)
pytestmark = [pytest.mark.postgres, pytest.mark.usefixtures("stored")]


def _run(sid: str) -> dict[str, Any]:
    response = client.post(f"/api/v1/scenarios/{sid}/runs")
    assert response.status_code == 201, response.text
    return dict(response.json())


def _store(database_url: str) -> ScenarioStore:
    return ScenarioStore.from_url(database_url)


def _population() -> PopulationDataset:
    return PopulationDataset.model_validate_json(Path(os.environ["POLTIKA_POPULATION_PATH"]).read_text())


def _verify(database_url: str, run_id: str) -> Any:
    return _store(database_url).verify_reform_run(
        run_id, _population(), WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
    )


def test_run_id_hash_inputs_are_unchanged() -> None:
    # Pinned from the function as it stood before Task 14 (no manifest input).
    assert (
        reform_run_id("a" * 64, ("b" * 64, "d" * 64), results_sha256="c" * 64)
        == "c1371b9cedca021650d724d8aaee2a12d827287dacc2dc961b92eaa1d76f304b"
    )
    assert (
        results_sha256({"synthetic": True, "x": [1, "2"]})
        == "27ea5e3a911676eae4ac43237227e4e1fc6e39f9b9418915dc2103ae1a8972cc"
    )


def test_the_run_id_is_recomputable_without_the_manifest(
    database_url: str
) -> None:
    created = _run(_create("Pin")["scenario_id"])
    row = _store(database_url).get_reform_run(created["run_id"])
    assert row is not None and row.manifest is not None
    assert created["run_id"] == reform_run_id(
        row.scenario_id, row.option_run_ids, results_sha256=results_sha256(row.results)
    )
    assert "manifest" not in row.results


def test_the_manifest_round_trips_and_uses_only_run_values(
    database_url: str
) -> None:
    created = _run(_create("Round trip")["scenario_id"])
    assert created["manifest_persisted"] is True
    row = _store(database_url).get_reform_run(created["run_id"])
    assert row is not None and row.manifest == created["manifest"]
    m = row.manifest
    assert m["law_baseline_date"] == date(2026, 6, 1).isoformat()
    (option,) = m["options"]
    assert option["option_run_id"] == row.option_run_ids[0]
    assert option["synthetic"] is True
    assert option["population"]["sha256"] == _population().content_sha256()
    assert option["policy_artifacts"] and option["assumptions"]
    assert m["limitations"] and m["units"]


def test_the_same_run_twice_is_stored_once() -> None:
    sid = _create("Twice")["scenario_id"]
    assert _run(sid)["run_id"] == _run(sid)["run_id"]


def test_verify_is_identical_for_unchanged_inputs(database_url: str) -> None:
    created = _run(_create("Identical")["scenario_id"])
    result = _verify(database_url, created["run_id"])
    assert (result.status, result.changed) == ("identical", ())


def test_verify_names_a_changed_policy_artifact(
    database_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = _run(_create("Policy drift")["scenario_id"])
    real = store_module.run_population
    name = created["manifest"]["options"][0]["policy_artifacts"][0]["name"]

    def drifted(*args: Any, **kwargs: Any) -> Any:
        run = real(*args, **kwargs)
        artifacts = tuple((n, "0" * 64 if n == name else s) for n, s in run.policy_artifacts)
        return replace(run, policy_artifacts=artifacts)

    monkeypatch.setattr(store_module, "run_population", drifted)
    result = _verify(database_url, created["run_id"])
    assert result.status == "drifted"
    assert result.changed == (f"option[0].policy_artifact:{name}",)


def test_verify_names_a_changed_population(
    database_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = _run(_create("Population drift")["scenario_id"])
    real = store_module.run_population

    def drifted(*args: Any, **kwargs: Any) -> Any:
        return replace(real(*args, **kwargs), population_sha256="f" * 64)

    monkeypatch.setattr(store_module, "run_population", drifted)
    result = _verify(database_url, created["run_id"])
    assert result.status == "drifted"
    assert "option[0].population_sha256" in result.changed


def test_a_legacy_row_is_not_retained_and_never_backfilled(
    database_url: str
) -> None:
    sid = _create("Legacy")["scenario_id"]
    fresh = _run(sid)
    store = _store(database_url)
    row = store.get_reform_run(fresh["run_id"])
    assert row is not None
    # A legacy row: the same kind of run saved without a manifest.
    legacy_results = {**row.results, "legacy": True}
    legacy_id = reform_run_id(
        sid, row.option_run_ids, results_sha256=results_sha256(legacy_results)
    )
    store.save_reform_run(legacy_id, sid, row.option_run_ids, legacy_results)
    assert _verify(database_url, legacy_id).status == "not_retained"
    # Saving it again with a manifest does not fill the NULL.
    again = store.save_reform_run(
        legacy_id, sid, row.option_run_ids, legacy_results, fresh["manifest"]
    )
    assert again.manifest is None
    assert _verify(database_url, legacy_id).status == "not_retained"


def test_the_audit_tab_states_whether_the_manifest_is_persisted() -> None:
    sid = _create("Audit")["scenario_id"]
    run = _run(sid)
    workspace = client.get(f"/api/v1/scenarios/{sid}/runs/{run['run_id']}").json()
    block = _blocks(workspace, "audit")["manifest"]
    fields = {f["label"]: f for f in block["fields"]}
    assert fields["Manifest persisted"]["value"] == "yes"
    assert fields["Law baseline date"]["value"] == "2026-06-01"
    assert "Manifest (JSON)" in fields
