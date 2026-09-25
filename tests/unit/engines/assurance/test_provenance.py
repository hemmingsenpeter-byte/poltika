"""Task 31.5: provenance report tests.

Checks the report against the policy files themselves (sources, rules,
hashes), refuses to build from changed or unresolvable artifacts, and keeps
the JSON and Markdown renderings consistent.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.common.errors import ArtifactHashMismatchError, ProvenanceError
from poltika.engines.assurance.provenance import (
    REPORT_FORMAT,
    build_provenance_report,
    render_json,
    render_markdown,
)
from poltika.engines.simulator.accommodation_supplement import (
    AssessmentWeek,
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.engines.simulator.wff import (
    ComponentResult,
    FactStatus,
    WffResult,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import load_policy_parameters
from tests.conftest import (
    AS_MODELLED_DATE,
    AS_POLICY_DIR,
    WFF_MODELLED_DATE,
    WFF_POLICY_DIR,
    as_parameters_for_case,
    as_scenario_from_yaml,
    load_as_cases,
    load_wff_spec_case,
    wff_scenario_from_yaml,
)

# A test week containing the modelled date -- not Task 28.2's selected week,
# which Pete has not chosen yet.
TEST_ASSESSMENT_WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))

_WFF_COMPONENTS = ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start")


def _wff_components(result: WffResult) -> dict[str, ComponentResult]:
    return {name: getattr(result, name) for name in _WFF_COMPONENTS}


def _wff_run(policy_dir: Path, case_id: str = "single_ordinary_low_income") -> WffResult:
    scenario = wff_scenario_from_yaml(load_wff_spec_case(case_id)["scenario"])
    return run_wff_module(policy_dir, WFF_MODELLED_DATE, scenario, requested_policy_version="0.1.0")


def _as_case(case_id: str) -> dict[str, Any]:
    cases = load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")
    return next(c for c in cases if c["id"] == case_id)


def _copy_policy_dir(source: Path, tmp_path: Path) -> Path:
    target = tmp_path / source.name
    shutil.copytree(source, target)
    return target


@pytest.fixture()
def as_policy_copy(tmp_path: Path) -> Path:
    """A file copy of the real AS policy directory. Since Task 26a.2 the real
    policy declares the published thresholds and income levels, so a
    real-file run reaches the DEC-001 path without any added assumption."""
    return _copy_policy_dir(AS_POLICY_DIR, tmp_path)


def test_wff_report_resolves_every_parameter_source_and_rule_from_the_files() -> None:
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR)))
    assert report["format"] == REPORT_FORMAT
    assert report["policy"] == {
        "policy_id": "working_for_families",
        "policy_version": "0.1.0",
        "schema_version": "0.1",
        "modelled_date": WFF_MODELLED_DATE.isoformat(),
        # WFF is assessed for the policy's whole tax year.
        "assessment_period": {"from": "2026-04-01", "to": "2027-04-01"},
    }

    sources = {s["id"]: s for s in yaml.safe_load((WFF_POLICY_DIR / "sources.yaml").read_text())["sources"]}
    policy = yaml.safe_load((WFF_POLICY_DIR / "policy.yaml").read_text())
    rule_ids = {c["id"]: c["source_rule_ids"] for c in policy["components"]}
    spec_text = (WFF_POLICY_DIR / "specification.md").read_text()

    for component in report["components"]:
        assert [r["id"] for r in component["source_rules"]] == rule_ids[component["component_id"]]
        for rule in component["source_rules"]:
            assert f"| {rule['id']} | {rule['summary']}" in spec_text
        for parameter in component["parameters"]:
            assert parameter["source_id"] in sources
    cited = {s["id"]: s for s in report["sources"]}
    assert set(cited) == {p["source_id"] for c in report["components"] for p in c["parameters"]}
    for source_id, entry in cited.items():
        assert entry["title"] == sources[source_id]["title"]
        assert entry["url"] == sources[source_id]["url"]

    ftc = report["components"][0]
    assert ftc["outcome"] == "calculated"
    assert ftc["value"] == "7921.000"  # Decimal as a string, never a float


def test_report_artifacts_are_the_exact_file_hashes() -> None:
    report = build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": _as_real_run()})
    expected = {
        name: hashlib.sha256((AS_POLICY_DIR / name).read_bytes()).hexdigest()
        for name in (
            "policy.yaml",
            "sources.yaml",
            "specification.md",
            "decisions/DEC-001-income-excess-rounding.md",
            "decisions/DEC-002-published-thresholds-and-rate-scope.md",
            "decisions/DEC-003-msd-paid-wff-income-exclusion.md",
        )
    }
    assert {a["path"]: a["sha256"] for a in report["artifacts"]} == expected


def _as_real_run() -> ComponentResult:
    case = _as_case("ordinary_uncapped_jobseeker")
    return run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, as_scenario_from_yaml(case["scenario"]), requested_policy_version="0.1.1", assessment_week=TEST_ASSESSMENT_WEEK
    )


@pytest.mark.parametrize("changed_file", ["policy.yaml", "sources.yaml", "specification.md"])
def test_report_refuses_a_run_whose_artifacts_have_since_changed(tmp_path: Path, changed_file: str) -> None:
    policy_dir = _copy_policy_dir(WFF_POLICY_DIR, tmp_path)
    components = _wff_components(_wff_run(policy_dir))
    with (policy_dir / changed_file).open("a") as f:
        f.write("\n# edited after the run\n")
    with pytest.raises(ArtifactHashMismatchError, match=changed_file):
        build_provenance_report(policy_dir, components)


def test_report_refuses_a_changed_rule_summary(tmp_path: Path) -> None:
    # Codex's PR #40 reproduction: editing WFF-03's wording after the run
    # must not reach the report.
    policy_dir = _copy_policy_dir(WFF_POLICY_DIR, tmp_path)
    components = _wff_components(_wff_run(policy_dir))
    spec = policy_dir / "specification.md"
    text = spec.read_text()
    assert "| WFF-03 | " in text
    spec.write_text(text.replace("| WFF-03 | ", "| WFF-03 | EDITED ", 1))
    with pytest.raises(ArtifactHashMismatchError, match="specification.md"):
        build_provenance_report(policy_dir, components)


def test_report_refuses_a_changed_decision_file(as_policy_copy: Path) -> None:
    case = _as_case("real_policy_non_beneficiary_single_income_reduction")
    result = run_as_module(
        as_policy_copy,
        AS_MODELLED_DATE,
        as_scenario_from_yaml(case["scenario"]),
        requested_policy_version="0.1.1", assessment_week=TEST_ASSESSMENT_WEEK,
    )
    decision = as_policy_copy / "decisions" / "DEC-001-income-excess-rounding.md"
    with decision.open("a") as f:
        f.write("\nEdited after the run.\n")
    with pytest.raises(ArtifactHashMismatchError, match="DEC-001"):
        build_provenance_report(as_policy_copy, {"accommodation_supplement": result})


def test_as_real_file_run_reports_dec_001_decision_artifact(as_policy_copy: Path) -> None:
    case = _as_case("real_policy_non_beneficiary_single_income_reduction")
    result = run_as_module(
        as_policy_copy,
        AS_MODELLED_DATE,
        as_scenario_from_yaml(case["scenario"]),
        requested_policy_version="0.1.1", assessment_week=TEST_ASSESSMENT_WEEK,
    )
    assert result.outcome == "calculated"
    assert str(result.value) == case["expected"]["accommodation_supplement"]["value"]

    report = build_provenance_report(as_policy_copy, {"accommodation_supplement": result})
    component = report["components"][0]
    assert component["decisions"] == [
        {"id": "DEC-002", "path": "decisions/DEC-002-published-thresholds-and-rate-scope.md"},
        {"id": "DEC-001", "path": "decisions/DEC-001-income-excess-rounding.md"},
    ]
    decision = next(a for a in report["artifacts"] if a["path"].startswith("decisions/DEC-001"))
    assert (
        decision["sha256"]
        == hashlib.sha256(
            (as_policy_copy / "decisions" / "DEC-001-income-excess-rounding.md").read_bytes()
        ).hexdigest()
    )
    assert "as_income_level_non_beneficiary_single_no_dependent_children" in [
        p["parameter_id"] for p in component["parameters"]
    ]


def test_as_undeclared_parameter_is_reported_without_a_source(as_policy_copy: Path) -> None:
    """A parameter the run's policy does not declare is reported as
    `undeclared` with no source. The real policy now declares every
    supported threshold (Task 26a.2), so this removes one from a copy."""
    threshold_id = "as_entry_threshold_jobseeker_support_single_no_dependent_children"
    policy = yaml.safe_load((as_policy_copy / "policy.yaml").read_text())
    policy["parameters"] = [p for p in policy["parameters"] if p["id"] != threshold_id]
    (as_policy_copy / "policy.yaml").write_text(yaml.safe_dump(policy, sort_keys=False))
    case = _as_case("ordinary_uncapped_jobseeker")
    result = run_as_module(
        as_policy_copy,
        AS_MODELLED_DATE,
        as_scenario_from_yaml(case["scenario"]),
        requested_policy_version="0.1.1",
        assessment_week=TEST_ASSESSMENT_WEEK,
    )
    report = build_provenance_report(as_policy_copy, {"accommodation_supplement": result})
    component = report["components"][0]
    assert component["outcome"] == "needs_review"
    undeclared = [p for p in component["parameters"] if p["outcome"] == "undeclared"]
    assert [p["parameter_id"] for p in undeclared] == ["as_entry_threshold_jobseeker_support_single_no_dependent_children"]
    assert undeclared[0]["source_id"] is None


def test_report_refuses_an_unresolvable_source_id() -> None:
    # as_parameters_for_case() injects test assumptions citing
    # "test-case-assumption", which is not in the real source catalogue.
    case = _as_case("ordinary_uncapped_jobseeker")
    result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
    with pytest.raises(ProvenanceError, match="test-case-assumption"):
        build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": result})


def test_report_refuses_a_result_without_a_trace() -> None:
    with pytest.raises(ProvenanceError, match="no trace"):
        build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": ComponentResult(outcome="needs_review")})


def test_report_refuses_a_hand_built_parameter_set(
    wff_synthetic_all_approved_parameters: Any,
) -> None:
    # The session fixture is loaded from a temp directory, so it does carry
    # hashes; strip them to model a hand-built set.
    from dataclasses import replace

    parameters = replace(wff_synthetic_all_approved_parameters, artifact_sha256={})
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    with pytest.raises(ProvenanceError, match="no artifact hashes"):
        build_provenance_report(WFF_POLICY_DIR, _wff_components(calculate_wff(scenario, parameters)))


def test_report_refuses_components_from_different_households() -> None:
    # Codex's PR #40 reproduction: same policy, same date, different
    # household. IWTC's trace names FTC as upstream, so pairing it with
    # another household's FTC would assert a false dependency.
    single = _wff_run(WFF_POLICY_DIR)
    partnered = _wff_run(WFF_POLICY_DIR, "partnered_combined_income_drives_abatement")
    assert partnered.in_work_tax_credit.trace is not None
    assert partnered.in_work_tax_credit.trace.upstream_components == ("family_tax_credit",)
    with pytest.raises(ProvenanceError, match="different runs"):
        build_provenance_report(
            WFF_POLICY_DIR,
            {"family_tax_credit": single.family_tax_credit, "in_work_tax_credit": partnered.in_work_tax_credit},
        )


def test_report_refuses_components_from_different_policies() -> None:
    wff = _wff_run(WFF_POLICY_DIR)
    with pytest.raises(ProvenanceError, match="different runs"):
        build_provenance_report(
            WFF_POLICY_DIR, {"family_tax_credit": wff.family_tax_credit, "accommodation_supplement": _as_real_run()}
        )


def test_components_of_one_run_share_a_scenario_identity() -> None:
    first = _wff_run(WFF_POLICY_DIR)
    again = _wff_run(WFF_POLICY_DIR)
    other = _wff_run(WFF_POLICY_DIR, "partnered_combined_income_drives_abatement")
    ids = {c.trace.scenario_sha256 for c in _wff_components(first).values() if c.trace is not None}
    assert len(ids) == 1
    assert first.best_start.trace is not None and again.best_start.trace is not None
    assert first.best_start.trace.scenario_sha256 == again.best_start.trace.scenario_sha256
    assert other.best_start.trace is not None
    assert other.best_start.trace.scenario_sha256 not in ids


def test_sources_carry_their_own_check_evidence_not_the_catalogue_date() -> None:
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR)))
    catalogue = {s["id"]: s for s in yaml.safe_load((WFF_POLICY_DIR / "sources.yaml").read_text())["sources"]}
    for source in report["sources"]:
        # Structured check dates come only from mapping-valued checks with a
        # checked_on; never from free text or the catalogue's as_of.
        raw_entry = catalogue[source["id"]]
        expected_dates = sorted(
            (str(value["checked_on"]), key)
            for key, value in raw_entry.items()
            if isinstance(value, dict) and "checked_on" in value
        )
        assert [(c["date"], c["field"]) for c in source["checked_on"]] == expected_dates
        raw = catalogue[source["id"]]
        evidence_fields = {e["field"] for e in source["check_evidence"]}
        for key in raw:
            if key not in {"id", "kind", "title", "url", "audit_version_url", "covers", "locator"}:
                assert key in evidence_fields
    tax_credit_order = next(s for s in report["sources"] if s["id"] == "wff-tax-credit-order-2025")
    assert tax_credit_order["check_evidence"], "a cited source with recorded check notes must carry them"


def test_json_is_canonical_and_deterministic() -> None:
    first = render_json(build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR))))
    second = render_json(build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR))))
    assert first == second
    assert json.loads(first)["components"][0]["value"] == "7921.000"


def test_markdown_carries_the_same_content_as_json() -> None:
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR)))
    markdown = render_markdown(report)
    for artifact in report["artifacts"]:
        assert artifact["sha256"] in markdown
    for component in report["components"]:
        section = markdown.split(f"## {component['component_id']}\n", 1)[1].split("\n## ", 1)[0]
        assert f"Outcome: **{component['outcome']}**" in section
        if component["reason"]:
            assert component["reason"] in section
        for rule in component["source_rules"]:
            assert f"{rule['id']}: " in section
        for rule in component["calculation_rules"]:
            assert rule in section
        for parameter in component["parameters"]:
            assert f"`{parameter['parameter_id']}`" in section
            if parameter["value"] is not None:
                assert f"| {parameter['value']} |" in section
            if parameter["source_id"] is not None:
                assert f"`{parameter['source_id']}`" in section
        for item in component["inputs"]:
            assert f"`{item['name']}`" in section
    sources_section = markdown.split("## Sources cited\n", 1)[1].split("\n## ", 1)[0]
    for source in report["sources"]:
        assert f"(`{source['id']}`)" in sources_section
        assert source["url"] in sources_section
        for note in source["check_evidence"]:
            assert f"- {note['field']}: " in sources_section


def test_structured_checked_on_is_reported_with_its_check_and_free_text_is_not_parsed(tmp_path: Path) -> None:
    """A mapping-valued check with a structured `checked_on` (the shape PR
    #41 introduces) is reported as that source's check date, naming the
    check. A date inside free text is never parsed, and a non-date
    `checked_on` is left as evidence only."""
    policy_dir = _copy_policy_dir(WFF_POLICY_DIR, tmp_path)
    catalogue_path = policy_dir / "sources.yaml"
    catalogue = yaml.safe_load(catalogue_path.read_text())
    cited = {
        "wff-tax-credit-order-2025": {
            "task_a_check": {"checked_on": "2026-09-24", "claim": "synthetic test check"},
            "task_b_check": {"checked_on": date(2026, 9, 22), "claim": "synthetic test check"},
            "task_c_check": {"checked_on": "sometime in September", "claim": "not a date"},
            "free_text_note": "Checked 2026-09-01 by hand.",
        }
    }
    for source in catalogue["sources"]:
        source.update(cited.get(source["id"], {}))
    catalogue_path.write_text(yaml.safe_dump(catalogue, sort_keys=False))

    catalogue_by_id = {s["id"]: s for s in catalogue["sources"]}
    report = build_provenance_report(policy_dir, _wff_components(_wff_run(policy_dir)))
    source = next(s for s in report["sources"] if s["id"] == "wff-tax-credit-order-2025")
    assert source["checked_on"] == [
        {"field": "task_b_check", "date": "2026-09-22"},
        {"field": "task_a_check", "date": "2026-09-24"},
    ]
    evidence = {e["field"]: e["text"] for e in source["check_evidence"]}
    assert evidence["free_text_note"] == "Checked 2026-09-01 by hand."
    assert json.loads(evidence["task_c_check"]) == {"checked_on": "sometime in September", "claim": "not a date"}

    markdown = render_markdown(report)
    assert "- Checked on: 2026-09-22 (task_b_check)" in markdown
    assert "- Checked on: 2026-09-24 (task_a_check)" in markdown
    # A cited source whose catalogue entry has no mapping-valued check
    # reports no structured date.
    unchecked = [
        s
        for s in report["sources"]
        if not any(isinstance(v, dict) and "checked_on" in v for v in catalogue_by_id[s["id"]].values())
    ]
    assert unchecked, "fixture should keep at least one cited source without a structured check"
    assert all(s["checked_on"] == [] for s in unchecked)


def test_as_report_states_the_assessment_week() -> None:
    report = build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": _as_real_run()})
    assert report["policy"]["assessment_period"] == {"from": "2026-06-01", "to": "2026-06-08"}
    assert "Assessment period: 2026-06-01 to 2026-06-08 (end exclusive)" in render_markdown(report)


def test_report_refuses_the_same_household_for_different_weeks() -> None:
    case = _as_case("ordinary_uncapped_jobseeker")
    scenario = as_scenario_from_yaml(case["scenario"])
    first = run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, scenario, requested_policy_version="0.1.1", assessment_week=TEST_ASSESSMENT_WEEK
    )
    other_week = AssessmentWeek(start=date(2026, 5, 29), end=date(2026, 6, 5))
    second = run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, scenario, requested_policy_version="0.1.1", assessment_week=other_week
    )
    assert first.trace is not None and second.trace is not None
    assert first.trace.scenario_sha256 == second.trace.scenario_sha256
    assert first.trace.assessment_period != second.trace.assessment_period
    # Two single-component results can only be mixed by listing both; the
    # header check must still tell the runs apart.
    with pytest.raises(ProvenanceError, match="different runs"):
        build_provenance_report(
            AS_POLICY_DIR, {"accommodation_supplement": first, "accommodation_supplement_again": second}
        )


def test_report_says_when_no_assessment_period_was_stated() -> None:
    """A bare calculator call is not told its period; the report must say
    so rather than invent one (PR #43 fresh-context review)."""
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    parameters = load_policy_parameters(WFF_POLICY_DIR, WFF_MODELLED_DATE)
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(calculate_wff(scenario, parameters)))
    assert report["policy"]["assessment_period"] is None
    assert "Assessment period: not stated (results did not come through a module entry point)" in render_markdown(
        report
    )


def test_combined_report_marks_superseded_rules_and_shows_combined_inputs() -> None:
    """Task 34.3 F9: a component the combined runner replaced keeps its module
    trace, but its rules are not reported as applied; the runner's own
    caller-asserted input and checks are shown."""
    from dataclasses import replace as _replace

    from poltika.engines.assurance.provenance import (
        build_combined_provenance_report,
        render_combined_markdown,
    )
    from poltika.scenarios.record import CodeIdentity, run_scenario
    from tests.unit.scenarios.test_scenario_record import _household, record_from_yaml

    record = record_from_yaml(_household("g1_sole_parent_two_children_non_beneficiary"))
    record = _replace(
        record,
        household=_replace(record.household, as_claimant_is_wff_claimant_or_partner=FactStatus.UNKNOWN),
    )
    run = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=CodeIdentity("0.1.0", None, None, None))
    report = build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    (as_component,) = report["accommodation_supplement"]["components"]
    assert as_component["outcome"] == "needs_review"
    assert as_component["calculation_rules"]  # the original module trace is kept
    assert as_component["rules_applied"] is False
    assert report["combined_inputs"] == [
        {"name": "as_claimant_is_wff_claimant_or_partner", "value": "unknown", "asserted_by": "caller"}
    ]
    markdown = render_combined_markdown(report)
    assert "Calculation rules from the superseded module result (not applied)" in markdown
    assert "Calculation rules applied" not in markdown.split("## Accommodation Supplement")[1]
    assert "as_claimant_is_wff_claimant_or_partner: unknown (asserted by caller)" in markdown
