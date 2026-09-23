"""Task 31.5: provenance report tests.

Checks the report against the policy files themselves (sources, rules,
hashes), refuses to build from changed or unresolvable artifacts, and keeps
the JSON and Markdown renderings consistent.
"""

from __future__ import annotations

import hashlib
import json
import shutil
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
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.engines.simulator.wff import ComponentResult, WffResult, calculate_wff, run_wff_module
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
def as_policy_with_assumed_rates(tmp_path: Path) -> Path:
    """A copy of the real AS policy directory with the non-beneficiary
    base rate and income level declared, so a real-file run can reach the
    DEC-001 path. The two values are the spec case's own test assumptions,
    not statutory figures (Task 26a has not populated real ones)."""
    case = _as_case("non_beneficiary_fractional_income_excess_unrounded")
    policy_dir = _copy_policy_dir(AS_POLICY_DIR, tmp_path)
    policy = yaml.safe_load((policy_dir / "policy.yaml").read_text())
    source_id = policy["parameters"][0]["values"][0]["source_id"]
    for parameter_id, value in (
        ("as_base_rate_non_beneficiary_single_no_dependent_children", case["parameter_assumptions"]["base_rate"]),
        ("as_income_level_non_beneficiary", case["parameter_assumptions"]["income_level"]),
    ):
        policy["parameters"].append(
            {
                "id": parameter_id,
                "value_type": "money",
                "unit": "NZD_per_week",
                "values": [
                    {
                        "effective_from": policy["reference_period"]["from"],
                        "effective_to": policy["reference_period"]["to"],
                        "value": value,
                        "source_id": source_id,
                        "locator": "test assumption only -- not a statutory value",
                        "review_status": "approved",
                    }
                ],
            }
        )
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy, sort_keys=False))
    return policy_dir


def test_wff_report_resolves_every_parameter_source_and_rule_from_the_files() -> None:
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR)))
    assert report["format"] == REPORT_FORMAT
    assert report["policy"] == {
        "policy_id": "working_for_families",
        "policy_version": "0.1.0",
        "schema_version": "0.1",
        "modelled_date": WFF_MODELLED_DATE.isoformat(),
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
            source = sources[parameter["source"]["id"]]
            assert parameter["source"]["title"] == source["title"]
            assert parameter["source"]["url"] == source["url"]

    ftc = report["components"][0]
    assert ftc["outcome"] == "calculated"
    assert ftc["value"] == "7921.000"  # Decimal as a string, never a float


def test_report_artifacts_are_the_exact_file_hashes() -> None:
    report = build_provenance_report(WFF_POLICY_DIR, _wff_components(_wff_run(WFF_POLICY_DIR)))
    by_path = {a["path"]: a for a in report["artifacts"]}
    for name, bound_at in (("policy.yaml", "run"), ("sources.yaml", "run"), ("specification.md", "report")):
        assert by_path[name]["sha256"] == hashlib.sha256((WFF_POLICY_DIR / name).read_bytes()).hexdigest()
        assert by_path[name]["bound_at"] == bound_at


@pytest.mark.parametrize("changed_file", ["policy.yaml", "sources.yaml"])
def test_report_refuses_a_run_whose_artifacts_have_since_changed(tmp_path: Path, changed_file: str) -> None:
    policy_dir = _copy_policy_dir(WFF_POLICY_DIR, tmp_path)
    components = _wff_components(_wff_run(policy_dir))
    with (policy_dir / changed_file).open("a") as f:
        f.write("\n# edited after the run\n")
    with pytest.raises(ArtifactHashMismatchError, match=changed_file):
        build_provenance_report(policy_dir, components)


def test_as_real_file_run_reports_dec_001_decision_artifact(as_policy_with_assumed_rates: Path) -> None:
    case = _as_case("non_beneficiary_fractional_income_excess_unrounded")
    result = run_as_module(
        as_policy_with_assumed_rates,
        AS_MODELLED_DATE,
        as_scenario_from_yaml(case["scenario"]),
        requested_policy_version="0.1.0",
    )
    assert result.outcome == "calculated"
    assert result.value == 74  # the spec case's own expected value, unchanged by tracing

    report = build_provenance_report(as_policy_with_assumed_rates, {"accommodation_supplement": result})
    component = report["components"][0]
    assert component["decisions"] == [{"id": "DEC-001", "path": "decisions/DEC-001-income-excess-rounding.md"}]
    decision = next(a for a in report["artifacts"] if a["path"].startswith("decisions/"))
    assert decision["bound_at"] == "report"
    assert (
        decision["sha256"]
        == hashlib.sha256(
            (as_policy_with_assumed_rates / "decisions" / "DEC-001-income-excess-rounding.md").read_bytes()
        ).hexdigest()
    )
    assert "as_income_level_non_beneficiary" in [p["parameter_id"] for p in component["parameters"]]


def test_as_undeclared_parameter_is_reported_without_a_source() -> None:
    case = _as_case("ordinary_uncapped_jobseeker")
    result = run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, as_scenario_from_yaml(case["scenario"]), requested_policy_version="0.1.0"
    )
    report = build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": result})
    component = report["components"][0]
    assert component["outcome"] == "needs_review"
    undeclared = [p for p in component["parameters"] if p["outcome"] == "undeclared"]
    assert [p["parameter_id"] for p in undeclared] == ["as_base_rate_jobseeker_support_single_no_dependent_children"]
    assert undeclared[0]["source"] is None


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


def test_report_refuses_mixed_runs() -> None:
    wff = _wff_run(WFF_POLICY_DIR)
    other = _wff_run(WFF_POLICY_DIR, "partnered_combined_income_drives_abatement")
    # Same policy and files, so these do share a header; a different policy's
    # result must not.
    case = _as_case("ordinary_uncapped_jobseeker")
    as_result = run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, as_scenario_from_yaml(case["scenario"]), requested_policy_version="0.1.0"
    )
    build_provenance_report(WFF_POLICY_DIR, {"family_tax_credit": wff.family_tax_credit, "best_start": other.best_start})
    with pytest.raises(ProvenanceError, match="different runs"):
        build_provenance_report(
            WFF_POLICY_DIR, {"family_tax_credit": wff.family_tax_credit, "accommodation_supplement": as_result}
        )


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
            if parameter["source"] is not None:
                assert f"(`{parameter['source']['id']}`)" in section
        for item in component["inputs"]:
            assert f"`{item['name']}`" in section
