"""Task 30.1-30.3: scenario records, artifact manifests, canonical identity,
and determinism (including across separate processes)."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import FactStatus
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import (
    CodeIdentity,
    ScenarioRecord,
    canonical_json,
    detect_code_identity,
    result_payload,
    run_scenario,
    scenario_id,
)
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_scenario_from_yaml,
    wff_scenario_from_yaml,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
GOLDEN_PATH = REPO_ROOT / "policy_specs" / "wff_as_interaction" / "golden_households.yaml"
FIXED_CODE = CodeIdentity("0.1.0", "0" * 40, True, "0" * 64)


def _household(household_id: str = "g7_sole_parent_asset_imputation_and_income_reduction") -> dict[str, Any]:
    households = yaml.safe_load(GOLDEN_PATH.read_text())["households"]
    household: dict[str, Any] = next(h for h in households if h["id"] == household_id)
    return household


def record_from_yaml(household: dict[str, Any]) -> ScenarioRecord:
    return ScenarioRecord(
        household=CombinedHouseholdScenario(
            wff=wff_scenario_from_yaml(household["wff"]),
            accommodation_supplement=as_scenario_from_yaml(household["accommodation_supplement"]),
            as_claimant_is_wff_claimant_or_partner=FactStatus(household["precondition"]),
        ),
        wff_lookup_date=date(2026, 6, 1),
        as_lookup_date=date(2026, 6, 1),
        assessment_week=AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8)),
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )


def test_repeated_runs_have_identical_identities_and_payloads() -> None:
    record = record_from_yaml(_household())
    first = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)
    second = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)
    assert first.scenario_id == second.scenario_id
    assert first.result_id == second.result_id
    assert canonical_json(result_payload(first.result)) == canonical_json(result_payload(second.result))


def test_identity_is_the_same_in_a_separate_process() -> None:
    """Byte-identical canonical output from a fresh interpreter: nothing in
    the identity depends on process state (hash seeds, ordering)."""
    record = record_from_yaml(_household())
    here = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)
    script = (
        f"import sys; sys.path.insert(0, {str(REPO_ROOT)!r})\n"
        "from tests.unit.scenarios.test_scenario_record import record_from_yaml, _household, FIXED_CODE\n"
        "from tests.conftest import WFF_POLICY_DIR, AS_POLICY_DIR\n"
        "from poltika.scenarios.record import run_scenario, canonical_json, result_payload\n"
        "run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)\n"
        "print(run.scenario_id); print(run.result_id); print(canonical_json(result_payload(run.result)))\n"
    )
    out = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True, env={"PYTHONHASHSEED": "12345"}
    ).stdout.splitlines()
    assert out == [here.scenario_id, here.result_id, canonical_json(result_payload(here.result))]


def test_yaml_key_order_does_not_change_the_scenario_identity() -> None:
    household = _household()
    reordered = {
        **household,
        "wff": dict(reversed(list(household["wff"].items()))),
        "accommodation_supplement": dict(reversed(list(household["accommodation_supplement"].items()))),
    }
    assert scenario_id(record_from_yaml(household)) == scenario_id(record_from_yaml(reordered))


def test_any_changed_fact_or_period_changes_the_scenario_identity() -> None:
    record = record_from_yaml(_household())
    changed_fact = replace(
        record,
        household=replace(
            record.household,
            accommodation_supplement=replace(record.household.accommodation_supplement, weekly_income=None),
        ),
    )
    changed_week = replace(record, assessment_week=AssessmentWeek(start=date(2026, 6, 2), end=date(2026, 6, 9)))
    ids = {scenario_id(record), scenario_id(changed_fact), scenario_id(changed_week)}
    assert len(ids) == 3


def test_manifest_names_the_exact_bound_policy_files() -> None:
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)
    files = dict(run.manifest.policy_files)
    for policy_dir in (WFF_POLICY_DIR, AS_POLICY_DIR):
        for name in ("policy.yaml", "sources.yaml", "specification.md"):
            key = f"{policy_dir.name}/{name}"
            assert files[key] == hashlib.sha256((policy_dir / name).read_bytes()).hexdigest(), key
    assert "accommodation_supplement/decisions/DEC-002-published-thresholds-and-rate-scope.md" in files


def test_code_identity_changes_the_result_identity_but_not_the_scenario_identity() -> None:
    record = record_from_yaml(_household())
    a = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=FIXED_CODE)
    b = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=replace(FIXED_CODE, source_commit="1" * 40))
    assert a.scenario_id == b.scenario_id
    assert a.result_id != b.result_id


def test_reproducibility_needs_a_clean_committed_tree() -> None:
    assert FIXED_CODE.reproducible
    assert not replace(FIXED_CODE, source_tree_clean=False).reproducible
    assert not replace(FIXED_CODE, source_commit=None, source_tree_clean=None).reproducible


def test_detect_code_identity_in_this_checkout() -> None:
    code = detect_code_identity(REPO_ROOT)
    assert code.dependency_lock_sha256 == hashlib.sha256((REPO_ROOT / "uv.lock").read_bytes()).hexdigest()
    assert code.source_commit is None or len(code.source_commit) == 40


def test_detect_code_identity_outside_git_is_not_reproducible(tmp_path: Path) -> None:
    code = detect_code_identity(tmp_path)
    assert code.source_commit is None
    assert not code.reproducible


def test_code_identity_needs_the_running_package_to_be_this_checkouts_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Task 34.3 F4: a wheel installed in a venv inside the checkout must not
    inherit the checkout's commit."""
    import poltika.scenarios.record as record_module

    monkeypatch.setattr(record_module, "_running_package_dir", lambda: tmp_path / "site-packages" / "poltika")
    code = detect_code_identity(REPO_ROOT)
    assert code.source_commit is None
    assert not code.reproducible


def test_child_order_does_not_change_identity() -> None:
    """Task 34.3 F10: the calculators ignore child order; so do the ids."""
    record = record_from_yaml(_household("g2_couple_two_children_income_abated_both"))
    first, second = record.household.wff.children
    distinct = replace(first, best_start_no_disqualifying_payment=FactStatus.UNKNOWN)
    wff_a = replace(record.household.wff, children=(distinct, second))
    wff_b = replace(record.household.wff, children=(second, distinct))
    record_a = replace(record, household=replace(record.household, wff=wff_a))
    record_b = replace(record, household=replace(record.household, wff=wff_b))
    assert scenario_id(record_a) == scenario_id(record_b)


def test_policy_files_outside_the_committed_repository_are_not_reproducible(tmp_path: Path) -> None:
    import shutil

    wff_copy, as_copy = tmp_path / "working_for_families", tmp_path / "accommodation_supplement"
    shutil.copytree(WFF_POLICY_DIR, wff_copy)
    shutil.copytree(AS_POLICY_DIR, as_copy)
    code = detect_code_identity(REPO_ROOT)
    run = run_scenario(record_from_yaml(_household()), wff_copy, as_copy, code=code)
    assert not run.manifest.policy_files_committed
    assert not run.manifest.reproducible


def test_committed_file_lookups_run_git_once_per_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    """A long-running API must not run `git show` for every bound file on
    every request: a commit's content never changes, so a lookup is kept."""
    import poltika.scenarios.record as record_module

    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    code = CodeIdentity("0.1.0", head, True, None)
    record = record_from_yaml(_household())
    first = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=code)

    calls: list[list[str]] = []
    real_run = subprocess.run

    def counting_run(args: list[str], **kwargs: Any) -> Any:
        calls.append(args)
        return real_run(args, **kwargs)

    monkeypatch.setattr(record_module.subprocess, "run", counting_run)
    second = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=code)
    assert calls == []
    assert second.manifest.policy_files_committed == first.manifest.policy_files_committed


def test_committed_policy_files_verify_against_head() -> None:
    code = detect_code_identity(REPO_ROOT)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=code)
    # Holds whenever the checkout's policy files equal HEAD (true in CI and in
    # a clean checkout); a locally edited policy file would make this False.
    if code.source_tree_clean:
        assert run.manifest.policy_files_committed
        assert run.manifest.reproducible
