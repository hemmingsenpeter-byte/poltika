"""Task 14: the reform run manifest and the replay check, against a throwaway
real PostgreSQL server. Storage and comparison only: no statutory value."""

from __future__ import annotations

import os
import shutil
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.household import running_code_identity
from poltika.api.main import app
from poltika.api.microsim import AS_POLICY_DIR, WFF_POLICY_DIR
from poltika.scenarios.microsim.reform import Reform
from poltika.scenarios.microsim.runner import run_population
from poltika.scenarios.reform_manifest import ReformVerification, verify_manifest
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
    created = _run(_create("Pin", "60001")["scenario_id"])
    row = _store(database_url).get_reform_run(created["run_id"])
    assert row is not None and row.manifest is not None
    assert created["run_id"] == reform_run_id(
        row.scenario_id, row.option_run_ids, results_sha256=results_sha256(row.results)
    )
    assert "manifest" not in row.results


def test_the_manifest_round_trips_and_uses_only_run_values(
    database_url: str
) -> None:
    created = _run(_create("Round trip", "60002")["scenario_id"])
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
    sid = _create("Twice", "60003")["scenario_id"]
    assert _run(sid)["run_id"] == _run(sid)["run_id"]


def test_verify_is_identical_for_unchanged_inputs(database_url: str) -> None:
    created = _run(_create("Identical", "60004")["scenario_id"])
    result = _verify(database_url, created["run_id"])
    assert (result.status, result.changed) == ("identical", ())


def test_verify_names_a_changed_policy_file(database_url: str, tmp_path: Path) -> None:
    created = _run(_create("Policy drift", "60005")["scenario_id"])
    # A real change to a copy of the WFF policy directory: a trailing YAML comment.
    wff = tmp_path / "wff"
    shutil.copytree(WFF_POLICY_DIR, wff)
    with (wff / "policy.yaml").open("a") as f:
        f.write("\n# edited after the run\n")
    result = _store(database_url).verify_reform_run(
        created["run_id"], _population(), wff, AS_POLICY_DIR, code=running_code_identity()
    )
    assert result.status == "drifted"
    assert result.changed
    assert all(c.startswith("option[0].policy_artifact:") for c in result.changed)


def test_verify_names_exactly_a_changed_population_version(database_url: str) -> None:
    created = _run(_create("Population drift", "60006")["scenario_id"])
    store = _store(database_url)
    changed = _population().model_copy(update={"version": _population().version + 1})
    result = store.verify_reform_run(
        created["run_id"], changed, WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
    )
    assert result.status == "drifted"
    # The content hash covers the version, so both change; nothing else does.
    assert sorted(result.changed) == [
        "option[0].population_sha256",
        "option[0].population_version",
    ]


def test_verify_names_exactly_a_changed_population_id(database_url: str) -> None:
    created = _run(_create("Population id drift", "60009")["scenario_id"])
    changed = _population().model_copy(update={"population_id": "another_population"})
    result = _store(database_url).verify_reform_run(
        created["run_id"], changed, WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
    )
    assert result.status == "drifted"
    assert sorted(result.changed) == [
        "option[0].population_population_id",  # sic: the key is prefixed twice in verify_manifest
        "option[0].population_sha256",
    ]


def test_verify_names_a_changed_code_identity(database_url: str) -> None:
    created = _run(_create("Code drift", "60010")["scenario_id"])
    code = replace(running_code_identity(), source_commit="a" * 40)
    result = _store(database_url).verify_reform_run(
        created["run_id"], _population(), WFF_POLICY_DIR, AS_POLICY_DIR, code=code
    )
    assert result.status == "drifted"
    assert "option[0].code" in result.changed


def _rerun(database_url: str, created: dict[str, Any]) -> tuple[dict[str, Any], list[Any]]:
    """The stored manifest and a fresh run of the same options."""
    store = _store(database_url)
    row = store.get_reform_run(created["run_id"])
    assert row is not None and row.manifest is not None
    scenario = store.get_reform_scenario(row.scenario_id)
    assert scenario is not None
    runs = [
        run_population(
            _population(),
            Reform.model_validate(option["reform"]),
            WFF_POLICY_DIR,
            AS_POLICY_DIR,
            code=running_code_identity(),
        )
        for option in scenario.definition["options"]
    ]
    return row.manifest, runs


def test_an_option_count_mismatch_is_drift_in_options(database_url: str) -> None:
    created = _run(_create("Count", "60011")["scenario_id"])
    manifest, runs = _rerun(database_url, created)
    assert verify_manifest(manifest, runs).status == "identical"
    extra = {**manifest, "options": [*manifest["options"], manifest["options"][0]]}
    assert verify_manifest(extra, runs) == ReformVerification("drifted", ("options",))
    assert verify_manifest({**manifest, "options": []}, runs) == ReformVerification(
        "drifted", ("options",)
    )


def test_results_alone_changing_is_reported_as_results(database_url: str) -> None:
    created = _run(_create("Results", "60012")["scenario_id"])
    manifest, runs = _rerun(database_url, created)
    stale = {
        **manifest,
        "options": [{**manifest["options"][0], "option_results_sha256": "0" * 64}],
    }
    assert verify_manifest(stale, runs) == ReformVerification("drifted", ("option[0].results",))


def test_results_are_not_added_when_a_named_input_already_explains_the_drift(
    database_url: str,
) -> None:
    created = _run(_create("No results double count", "60013")["scenario_id"])
    manifest, runs = _rerun(database_url, created)
    option = {
        **manifest["options"][0],
        "option_results_sha256": "0" * 64,
        "reform_sha256": "1" * 64,
    }
    result = verify_manifest({**manifest, "options": [option]}, runs)
    assert result.changed == ("option[0].reform_sha256",)


def test_a_legacy_row_is_not_retained_and_never_backfilled(
    database_url: str
) -> None:
    sid = _create("Legacy", "60007")["scenario_id"]
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
    sid = _create("Audit", "60008")["scenario_id"]
    run = _run(sid)
    workspace = client.get(f"/api/v1/scenarios/{sid}/runs/{run['run_id']}").json()
    block = _blocks(workspace, "audit")["manifest"]
    fields = {f["label"]: f for f in block["fields"]}
    assert fields["Manifest persisted"]["value"] == "yes"
    assert fields["Law baseline date"]["value"] == "2026-06-01"
    assert "Manifest (JSON)" in fields
