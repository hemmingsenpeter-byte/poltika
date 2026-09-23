"""Task 31.5: per-component provenance trace correctness.

Unchanged numerical tests prove the trace did not alter behaviour; they do
not prove the trace is right. These tests check, on representative paths,
that each trace records the parameters, inputs, upstream components, and
rules actually used -- checked against the real `policy.yaml` where a value
or source is involved, never against the trace's own output.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Any

import yaml

from poltika.engines.simulator.accommodation_supplement import (
    AsScenario,
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.engines.simulator.trace import recording_copy, recording_parameters
from poltika.engines.simulator.wff import (
    ComponentResult,
    WffResult,
    WffScenario,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
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

_FTC_PARAMETERS = [
    "family_tax_credit_eldest_child",
    "family_tax_credit_additional_child",
    "family_tax_credit_abatement_threshold",
    "family_tax_credit_abatement_rate",
]


def _policy_values(policy_dir: Any) -> dict[str, dict[str, Any]]:
    """Each parameter's single 2026 value entry, straight from policy.yaml."""
    raw = yaml.safe_load((policy_dir / "policy.yaml").read_text())
    return {p["id"]: p["values"][0] for p in raw["parameters"]}


def _wff_run(case_id: str) -> WffResult:
    scenario = wff_scenario_from_yaml(load_wff_spec_case(case_id)["scenario"])
    return run_wff_module(WFF_POLICY_DIR, WFF_MODELLED_DATE, scenario, requested_policy_version="0.1.0")


def _as_case(case_id: str) -> dict[str, Any]:
    cases = load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")
    return next(c for c in cases if c["id"] == case_id)


def _ids(result: ComponentResult) -> list[str]:
    assert result.trace is not None
    return [p.parameter_id for p in result.trace.parameters]


def _inputs(result: ComponentResult) -> list[str]:
    assert result.trace is not None
    return [i.name for i in result.trace.inputs]


# --- WFF ---


def test_calculated_ftc_records_its_parameters_with_policy_values_and_sources() -> None:
    ftc = _wff_run("single_ordinary_low_income").family_tax_credit
    assert ftc.outcome == "calculated"
    assert ftc.trace is not None
    assert _ids(ftc) == _FTC_PARAMETERS

    policy = _policy_values(WFF_POLICY_DIR)
    for use in ftc.trace.parameters:
        entry = policy[use.parameter_id]
        assert use.outcome == "resolved"
        # YAML parses 0.275 as a float; compare via its text, never float.
        assert use.value == Decimal(str(entry["value"]))
        assert use.source_id == entry["source_id"]
        assert use.locator == entry["locator"]
        assert use.effective_from == entry["effective_from"]
        assert use.effective_to == entry["effective_to"]
        assert use.review_status == entry["review_status"]

    assert {"family_scheme_income", "partner_status", "children"} <= set(_inputs(ftc))
    assert all(i.asserted_by == "caller" for i in ftc.trace.inputs)
    assert any(rule.startswith("MD 13(3)(a)") for rule in ftc.trace.calculation_rules)


def test_trace_header_matches_the_loaded_policy_and_its_file_hashes() -> None:
    import hashlib

    ftc = _wff_run("single_ordinary_low_income").family_tax_credit
    assert ftc.trace is not None
    assert (ftc.trace.policy_id, ftc.trace.policy_version, ftc.trace.schema_version) == (
        "working_for_families",
        "0.1.0",
        "0.1",
    )
    assert ftc.trace.modelled_date == WFF_MODELLED_DATE
    assert dict(ftc.trace.artifact_sha256) == {
        name: hashlib.sha256((WFF_POLICY_DIR / name).read_bytes()).hexdigest()
        # WFF has no DEC-*.md decision files yet, so these three are all.
        for name in ("policy.yaml", "sources.yaml", "specification.md")
    }
    assert len(ftc.trace.scenario_sha256) == 64


def test_iwtc_reaching_md_2_2_c_includes_ftc_as_upstream() -> None:
    iwtc = _wff_run("single_ordinary_low_income").in_work_tax_credit
    # The real policy's in_work_base is needs_review (Task 10.2), and the
    # trace must show that parameter as the cause.
    assert iwtc.outcome == "needs_review"
    assert iwtc.trace is not None
    assert iwtc.trace.upstream_components == ("family_tax_credit",)
    in_work_base = next(p for p in iwtc.trace.parameters if p.parameter_id == "in_work_base")
    assert in_work_base.outcome == "needs_review"
    assert in_work_base.value is None
    assert set(_FTC_PARAMETERS) <= set(_ids(iwtc))
    assert "family_scheme_income" in _inputs(iwtc)
    assert iwtc.trace.calculation_rules == ()


def test_iwtc_excluded_before_md_2_2_c_has_no_ftc_dependency() -> None:
    iwtc = _wff_run("in_work_eligibility_excluded_is_unsupported_not_needs_review").in_work_tax_credit
    assert iwtc.outcome == "unsupported"
    assert iwtc.trace is not None
    assert iwtc.trace.upstream_components == ()
    assert _ids(iwtc) == []
    assert "in_work_eligibility" in _inputs(iwtc)
    assert "family_scheme_income" not in _inputs(iwtc)


def test_calculated_iwtc_records_rule_and_both_parameter_sets(
    wff_synthetic_all_approved_parameters: PolicyParameterSet,
) -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    iwtc = calculate_wff(scenario, wff_synthetic_all_approved_parameters).in_work_tax_credit
    assert iwtc.outcome == "calculated"
    assert iwtc.trace is not None
    assert _ids(iwtc) == ["in_work_base", "in_work_additional_child", *_FTC_PARAMETERS]
    assert iwtc.trace.upstream_components == ("family_tax_credit",)
    assert any(rule.startswith("MD 2(2)(c)") for rule in iwtc.trace.calculation_rules)


def test_household_gate_failure_records_only_gate_inputs() -> None:
    result = _wff_run("household_eligibility_excluded_is_unsupported")
    for component in (
        result.family_tax_credit,
        result.in_work_tax_credit,
        result.minimum_family_tax_credit,
        result.best_start,
    ):
        assert component.outcome == "unsupported"
        assert component.reason
        assert component.trace is not None
        assert _ids(component) == []
        assert "household_eligibility" in _inputs(component)
        assert "family_scheme_income" not in _inputs(component)
        assert component.trace.calculation_rules == ()


def test_best_start_evidenced_zero_consults_no_parameters() -> None:
    best_start = _wff_run("single_ordinary_low_income").best_start
    assert best_start.outcome == "calculated"
    assert best_start.value == 0
    assert best_start.trace is not None
    assert _ids(best_start) == []
    assert "children" in _inputs(best_start)
    assert best_start.trace.calculation_rules == ()


def test_best_start_abatement_path_records_mg_3_rule() -> None:
    best_start = _wff_run("best_start_supported_cohort_with_abatement").best_start
    assert best_start.outcome == "calculated"
    assert best_start.trace is not None
    assert _ids(best_start) == ["best_start_annual_amount", "best_start_abatement_threshold", "best_start_abatement_rate"]
    assert any(rule.startswith("MG 3(2)(a)") for rule in best_start.trace.calculation_rules)


def test_module_validation_failure_carries_header_only_trace() -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    result = run_wff_module(WFF_POLICY_DIR, date(2027, 6, 1), scenario, requested_policy_version="0.1.0")
    ftc = result.family_tax_credit
    assert ftc.outcome in ("needs_review", "unsupported")
    assert ftc.trace is not None
    assert ftc.trace.component_id == "family_tax_credit"
    assert ftc.trace.parameters == ()
    assert ftc.trace.inputs == ()


def test_traces_are_deterministic() -> None:
    first = _wff_run("partnered_combined_income_drives_abatement")
    second = _wff_run("partnered_combined_income_drives_abatement")
    assert first.family_tax_credit.trace == second.family_tax_credit.trace
    assert first.in_work_tax_credit.trace == second.in_work_tax_credit.trace


def test_trace_does_not_affect_result_equality() -> None:
    ftc = _wff_run("single_ordinary_low_income").family_tax_credit
    assert ftc == ComponentResult(outcome="calculated", value=ftc.value)
    assert ftc == replace(ftc, trace=None)


def test_recording_leaves_originals_untouched() -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    parameters = load_policy_parameters(WFF_POLICY_DIR, WFF_MODELLED_DATE)
    calculate_wff(scenario, parameters)
    assert type(scenario) is WffScenario
    assert type(parameters.resolutions) is dict


def test_recording_copy_logs_reads_in_first_read_order_without_construction_reads() -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    copy, reads = recording_copy(scenario)
    assert isinstance(copy, WffScenario)
    assert reads == []  # __post_init__'s own reads are not component reads
    _ = copy.partner_status
    _ = copy.children
    _ = copy.partner_status
    assert reads == ["partner_status", "children"]


def test_recording_parameters_logs_membership_tests_too() -> None:
    parameters = load_policy_parameters(WFF_POLICY_DIR, WFF_MODELLED_DATE)
    recorded, log = recording_parameters(parameters)
    assert "not_a_parameter" not in recorded.resolutions
    recorded.get("in_work_base")
    assert log == ["not_a_parameter", "in_work_base"]


# --- Accommodation Supplement ---


def test_as_real_policy_records_undeclared_base_rate() -> None:
    case = _as_case("ordinary_uncapped_jobseeker")
    result = run_as_module(
        AS_POLICY_DIR, AS_MODELLED_DATE, as_scenario_from_yaml(case["scenario"]), requested_policy_version="0.1.0"
    )
    # The real policy does not declare base rates yet (Task 26a).
    assert result.outcome == "needs_review"
    assert result.trace is not None
    base_rate = next(p for p in result.trace.parameters if p.parameter_id.startswith("as_base_rate_"))
    assert base_rate.parameter_id == "as_base_rate_jobseeker_support_single_no_dependent_children"
    assert base_rate.outcome == "undeclared"
    assert base_rate.source_id is None
    assert result.trace.calculation_rules == ()


def test_as_calculated_beneficiary_applies_only_r19() -> None:
    case = _as_case("ordinary_uncapped_jobseeker")
    result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
    assert result.outcome == "calculated"
    assert result.trace is not None
    assert [r.split(":")[0] for r in result.trace.calculation_rules] == ["r 19"]
    assert result.trace.decisions == ()
    assert "income_reduction_rate" not in _ids(result)
    assert "weekly_income" not in _inputs(result)

    policy = _policy_values(AS_POLICY_DIR)
    area_cap = next(p for p in result.trace.parameters if p.parameter_id.startswith("area_cap_"))
    assert area_cap.value == Decimal(str(policy[area_cap.parameter_id]["value"]))
    assert area_cap.source_id == policy[area_cap.parameter_id]["source_id"]


def test_as_non_beneficiary_path_records_dec_001_and_income_parameters() -> None:
    case = _as_case("non_beneficiary_fractional_income_excess_unrounded")
    result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
    assert result.outcome == "calculated"
    assert result.trace is not None
    assert result.trace.decisions == ("DEC-001",)
    assert [r.split(":")[0] for r in result.trace.calculation_rules] == ["s 423(3)", "r 18(2)", "r 19"]
    assert {
        "as_income_level_non_beneficiary",
        "asset_imputation_step_size",
        "asset_imputation_amount_per_step",
        "income_reduction_rate",
    } <= set(_ids(result))
    assert "weekly_income" in _inputs(result)


def test_as_gate_unsupported_consults_no_parameters() -> None:
    case = _as_case("homeowner_is_unsupported")
    result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
    assert result.outcome == "unsupported"
    assert result.trace is not None
    assert _ids(result) == []
    assert "tenure_type" in _inputs(result)


def test_as_recording_leaves_scenario_type_untouched() -> None:
    case = _as_case("ordinary_uncapped_jobseeker")
    scenario = as_scenario_from_yaml(case["scenario"])
    calculate_accommodation_supplement(scenario, as_parameters_for_case(case))
    assert type(scenario) is AsScenario
