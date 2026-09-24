"""Task 31.6: provenance for combined household runs (Tasks 28.4/30)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from poltika.common.errors import ArtifactHashMismatchError
from poltika.engines.assurance.provenance import (
    COMBINED_REPORT_FORMAT,
    build_combined_provenance_report,
    render_combined_markdown,
)
from poltika.scenarios.record import CodeIdentity, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

CODE = CodeIdentity("0.1.0", None, None, None)


def _golden(household_id: str) -> dict:  # type: ignore[type-arg]
    return next(h for h in yaml.safe_load(GOLDEN_PATH.read_text())["households"] if h["id"] == household_id)


def test_both_calculated_household_keeps_both_native_periods() -> None:
    run = run_scenario(record_from_yaml(_golden("g2_couple_two_children_income_abated_both")), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    report = build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    assert report["format"] == COMBINED_REPORT_FORMAT
    assert (report["scenario_id"], report["result_id"]) == (run.scenario_id, run.result_id)
    assert report["contradictions"] == []
    assert report["working_for_families"]["policy"]["assessment_period"] == {"from": "2026-04-01", "to": "2027-04-01"}
    assert report["accommodation_supplement"]["policy"]["assessment_period"] == {"from": "2026-06-01", "to": "2026-06-08"}
    assert report["accommodation_supplement"]["components"][0]["value"] == "220"
    assert {f["path"] for f in report["policy_files"]} == {p for p, _ in run.manifest.policy_files}
    markdown = render_combined_markdown(report)
    assert "Working for Families (annual)" in markdown and "Accommodation Supplement (weekly)" in markdown
    assert "no combined total" in markdown
    assert run.result_id in markdown


def test_disagreement_is_reported_and_replacements_keep_their_provenance() -> None:
    household = _golden("g1_sole_parent_two_children_non_beneficiary")
    household = {**household, "accommodation_supplement": {**household["accommodation_supplement"], "dependent_children_count": 3}}
    run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    report = build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    assert any("dependent children" in c for c in report["contradictions"])
    ftc = report["working_for_families"]["components"][0]
    assert ftc["outcome"] == "needs_review" and "dependent children" in ftc["reason"]
    assert ftc["parameters"], "the replaced component still reports the parameters its module consulted"
    assert "dependent children" in render_combined_markdown(report)


def test_report_refuses_a_policy_file_changed_after_the_run(tmp_path: Path) -> None:
    wff_copy, as_copy = tmp_path / "working_for_families", tmp_path / "accommodation_supplement"
    shutil.copytree(WFF_POLICY_DIR, wff_copy)
    shutil.copytree(AS_POLICY_DIR, as_copy)
    run = run_scenario(record_from_yaml(_golden("g2_couple_two_children_income_abated_both")), wff_copy, as_copy, code=CODE)
    with (as_copy / "policy.yaml").open("a") as f:
        f.write("\n# edited after the run\n")
    with pytest.raises(ArtifactHashMismatchError):
        build_combined_provenance_report(run, wff_copy, as_copy)


def test_report_refuses_a_manifest_that_does_not_match_the_verified_files() -> None:
    from dataclasses import replace

    from poltika.common.errors import ProvenanceError

    run = run_scenario(record_from_yaml(_golden("g2_couple_two_children_income_abated_both")), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    tampered = replace(run, manifest=replace(run.manifest, policy_files=run.manifest.policy_files[1:]))
    with pytest.raises(ProvenanceError, match="manifest"):
        build_combined_provenance_report(tampered, WFF_POLICY_DIR, AS_POLICY_DIR)
