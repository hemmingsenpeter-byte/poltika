"""Task 32.2-32.4: the PostgreSQL scenario store, against a throwaway real
PostgreSQL server (never SQLite, per ADR-0013)."""

from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from poltika.common.errors import ImmutableRecordError, StoreError
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.engines.simulator.outcome import FactStatus
from poltika.scenarios.record import CodeIdentity, ScenarioRun, run_scenario
from poltika.scenarios.store import ScenarioStore
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import _household, record_from_yaml

pytestmark = pytest.mark.postgres

CODE = CodeIdentity("0.1.0", None, None, None)


def _copy_policies(tmp_path: Path) -> tuple[Path, Path]:
    wff, as_ = tmp_path / "wff" / "working_for_families", tmp_path / "as" / "accommodation_supplement"
    shutil.copytree(WFF_POLICY_DIR, wff)
    shutil.copytree(AS_POLICY_DIR, as_)
    return wff, as_


def test_save_and_fetch_round_trips_the_record(database_url: str) -> None:
    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)  # identical content: a no-op
    stored = store.get_run(run.result_id)
    assert stored.record == run.record
    assert stored.scenario_id == run.scenario_id
    assert stored.result["accommodation_supplement"]["value"] == "176"


def test_replay_reproduces_after_the_current_policy_files_change(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    # Change the current AS policy after the run (a different threshold).
    policy = as_ / "policy.yaml"
    policy.write_text(policy.read_text().replace("value: 168,", "value: 170,"))
    report = store.replay(run.result_id, tmp_path / "replay", code=CODE)
    assert report.reproduced is True
    # CODE carries no commit, so the code cannot be shown to match.
    assert report.code_matches is False


def test_rerun_against_current_files_is_a_new_run_reporting_drift(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    policy = as_ / "policy.yaml"
    policy.write_text(policy.read_text().replace("value: 168,", "value: 170,"))
    drift = store.rerun_against_current(run.result_id, wff, as_, code=CODE)
    assert drift.changed_artifacts == ("accommodation_supplement/policy.yaml",)
    assert drift.result_changed
    assert drift.new_result_id != run.result_id
    assert store.get_run(run.result_id).result["accommodation_supplement"]["value"] == "176"  # original untouched


def test_drift_is_reported_even_when_amounts_are_unchanged(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    with (wff / "sources.yaml").open("a") as f:
        f.write("\n# catalogue note added\n")
    drift = store.rerun_against_current(run.result_id, wff, as_, code=CODE)
    assert drift.changed_artifacts == ("working_for_families/sources.yaml",)
    assert not drift.result_changed


def test_saving_a_run_whose_files_changed_since_the_run_is_refused(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    with (as_ / "specification.md").open("a") as f:
        f.write("\nedited\n")
    with pytest.raises(StoreError, match="no longer matches"):
        store.save_run(run, wff, as_)


def test_a_stored_id_cannot_be_rewritten(database_url: str) -> None:
    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    forged = replace(run, result=replace(run.result, contradictions=("forged",)))
    with pytest.raises(ImmutableRecordError):
        store.save_run(forged, WFF_POLICY_DIR, AS_POLICY_DIR)


def _reordered_children_runs() -> tuple[ScenarioRun, ScenarioRun]:
    """One household saved twice, its two (distinct) children listed in
    opposite orders."""
    record = record_from_yaml(_household("g2_couple_two_children_income_abated_both"))
    first, second = record.household.wff.children
    distinct = replace(first, best_start_no_disqualifying_payment=FactStatus.UNKNOWN)
    runs = []
    for children in ([distinct, second], [second, distinct]):
        wff = replace(record.household.wff, children=children)
        reordered = replace(record, household=replace(record.household, wff=wff))
        runs.append(run_scenario(reordered, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE))
    return runs[0], runs[1]


def test_the_same_scenario_with_children_reordered_saves_as_the_same_run(database_url: str) -> None:
    """Task 34.3 F10: the scenario id ignores child order, so saving the same
    household with its children in another order is the same record, not a
    conflicting one."""
    store = ScenarioStore.from_url(database_url)
    run_a, run_b = _reordered_children_runs()
    assert (run_a.scenario_id, run_a.result_id) == (run_b.scenario_id, run_b.result_id)
    store.save_run(run_a, WFF_POLICY_DIR, AS_POLICY_DIR)
    original_provenance = store.get_run(run_a.result_id).provenance
    store.save_run(run_b, WFF_POLICY_DIR, AS_POLICY_DIR)
    assert store.get_run(run_a.result_id).scenario_id == run_a.scenario_id
    assert store.get_run(run_a.result_id).provenance == original_provenance


def test_the_original_provenance_is_retained_after_policy_files_change(
    database_url: str, tmp_path: Path
) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(
        record_from_yaml(_household()), wff, as_, code=replace(CODE, package_version="retained-report")
    )
    original = build_combined_provenance_report(run, wff, as_)
    store.save_run(run, wff, as_)
    with (wff / "sources.yaml").open("a") as source:
        source.write("\n# A later source catalogue revision\n")

    retained = store.get_run(run.result_id).provenance
    assert retained == original
    assert retained is not None
    assert retained["working_for_families"]["components"][0]["steps"]


def test_resaving_a_legacy_run_does_not_backfill_its_provenance(database_url: str) -> None:
    from sqlalchemy import create_engine, update

    from poltika.scenarios.store import run_table

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(
        record_from_yaml(_household()),
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=replace(CODE, package_version="legacy-report"),
    )
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    # Simulate a row predating migration 0002, which retained no report.
    with create_engine(database_url).begin() as conn:
        conn.execute(
            update(run_table).where(run_table.c.result_id == run.result_id).values(provenance_json=None)
        )
    assert store.get_run(run.result_id).provenance is None
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    assert store.get_run(run.result_id).provenance is None


@pytest.mark.parametrize("field", ["scenario_id", "result_id", "policy_files", "code"])
def test_a_retained_report_must_match_its_original_run(database_url: str, field: str) -> None:
    from sqlalchemy import create_engine, update

    from poltika.scenarios.record import canonical_json
    from poltika.scenarios.store import run_table

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(
        record_from_yaml(_household()),
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=replace(CODE, package_version=f"mismatched-report-{field}"),
    )
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    provenance = store.get_run(run.result_id).provenance
    assert provenance is not None
    mismatched = {**provenance, field: "different"}
    with create_engine(database_url).begin() as conn:
        conn.execute(
            update(run_table)
            .where(run_table.c.result_id == run.result_id)
            .values(provenance_json=canonical_json(mismatched))
        )
    with pytest.raises(StoreError, match="provenance does not match"):
        store.get_run(run.result_id)


def test_a_stored_scenario_id_cannot_hold_a_different_household(database_url: str) -> None:
    store = ScenarioStore.from_url(database_url)
    run_a, _ = _reordered_children_runs()
    store.save_run(run_a, WFF_POLICY_DIR, AS_POLICY_DIR)
    other = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    forged = replace(other, scenario_id=run_a.scenario_id)
    with pytest.raises(ImmutableRecordError, match="scenario"):
        store.save_run(forged, WFF_POLICY_DIR, AS_POLICY_DIR)


def test_replay_reports_whether_the_running_code_is_the_stored_code(database_url: str, tmp_path: Path) -> None:
    """Task 34.3 F4: replay never relabels itself with the stored identity."""
    store = ScenarioStore.from_url(database_url)
    stored_code = CodeIdentity("0.1.0", "a" * 40, True, "b" * 64)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=stored_code)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    same = store.replay(run.result_id, tmp_path / "same", code=stored_code)
    assert same.reproduced and same.code_matches
    other = store.replay(run.result_id, tmp_path / "other", code=CodeIdentity("0.1.0", "c" * 40, True, "b" * 64))
    assert other.reproduced and not other.code_matches


def test_replay_fails_explicitly_when_an_artifact_is_missing(database_url: str, tmp_path: Path) -> None:
    # Runs last in this file: the deleted artifact is content-addressed and
    # shared by other stored runs in the session database.
    from sqlalchemy import create_engine, delete

    from poltika.scenarios.store import artifact_table

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household("g1_sole_parent_two_children_non_beneficiary")), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    sha = dict(run.manifest.policy_files)["working_for_families/specification.md"]
    with create_engine(database_url).begin() as conn:
        conn.execute(delete(artifact_table).where(artifact_table.c.sha256 == sha))
    with pytest.raises(StoreError, match="missing"):
        store.replay(run.result_id, tmp_path / "replay", code=CODE)
