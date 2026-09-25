"""ADR-0014: every result says why it has no number, and what would resolve it.

A `needs_review` or `unsupported` result carries a `reason_code`, the facts
that are `missing` (named as request fields) and a `resolution`. An
`ineligible` result is an evidenced zero. These tests pin the contract, the
code each kind of blocker reports, and that `missing` names fields a caller
can actually supply.
"""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
import yaml
from pydantic import BaseModel

from poltika.api.accommodation_supplement import AsCalculationRequest
from poltika.api.household import HouseholdCalculationRequest
from poltika.api.wff import ChildFactsRequest, VerifiedIncomeRequest, WffCalculationRequest
from poltika.engines.simulator.accommodation_supplement import (
    AssessmentWeek,
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    ComponentResult,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    WffScenario,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.record import CodeIdentity, run_scenario
from tests.conftest import (
    AS_MODELLED_DATE,
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_parameters_for_case,
    as_scenario_from_yaml,
    load_as_cases,
    load_wff_spec_case,
    wff_scenario_from_yaml,
)
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))


@pytest.fixture(scope="module")
def real_as_parameters() -> PolicyParameterSet:
    return load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE, requested_policy_version=AS_POLICY_VERSION)


def _partnered_household(partner_amount: Decimal | None) -> WffScenario:
    """The ADR-0014 motivating case: a couple with two children, one income
    known. Both children are verified outside Best Start entitlement."""
    child = ChildFacts(
        qualifies_whole_year=FactStatus.VERIFIED,
        best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
        best_start_no_disqualifying_payment=FactStatus.VERIFIED,
    )
    return WffScenario(
        household_eligibility=FactStatus.VERIFIED,
        extra_instalment_status=FactStatus.VERIFIED,
        children=[child, child],
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=VerifiedIncome(claimant_amount=Decimal(55000), partner_amount=partner_amount),
        net_family_scheme_income=Decimal(55000),
        net_family_scheme_income_me3_attested=True,
        in_work_eligibility=FactStatus.VERIFIED,
        ftc_iwtc_protected_or_direct_abatement=FactStatus.VERIFIED,
        mc6a_veterans_payment=FactStatus.VERIFIED,
        mc6b_disqualifying_payment=FactStatus.VERIFIED,
        minimum_family_full_time_earner_weeks=FactStatus.VERIFIED,
        best_start_no_shared_care=FactStatus.VERIFIED,
        best_start_protected_credit=FactStatus.VERIFIED,
    )


def test_unknown_partner_income_names_the_missing_fact_instead_of_assuming_zero(
    real_wff_parameters: PolicyParameterSet,
) -> None:
    result = calculate_wff(_partnered_household(partner_amount=None), real_wff_parameters)

    ftc = result.family_tax_credit
    assert ftc.outcome == "needs_review"
    assert ftc.value is None
    assert ftc.reason_code == "missing_input"
    assert ftc.missing == ("family_scheme_income.partner_amount",)
    assert ftc.resolution is not None and "partner's verified family-scheme income" in ftc.resolution
    # Known: the trace records the claimant's income that was supplied.
    assert ftc.trace is not None
    supplied = {use.name: use.value for use in ftc.trace.inputs}
    assert supplied["family_scheme_income"] == VerifiedIncome(claimant_amount=Decimal(55000))

    # In-work tax credit takes family tax credit's remaining abatement (MD
    # 2(2)(c)), so the same missing fact blocks it; MFTC needs it directly.
    for component in (result.in_work_tax_credit, result.minimum_family_tax_credit):
        assert component.outcome == "needs_review"
        assert component.missing == ("family_scheme_income.partner_amount",)

    # Best Start does not depend on income here: every child is verified
    # outside entitlement, which is an evidenced zero.
    assert result.best_start.outcome == "ineligible"
    assert result.best_start.value == 0
    assert result.total_annual_entitlement() is None


def test_supplying_the_partner_income_resolves_it(real_wff_parameters: PolicyParameterSet) -> None:
    result = calculate_wff(_partnered_household(partner_amount=Decimal(0)), real_wff_parameters)

    assert result.family_tax_credit.outcome == "calculated"
    assert result.minimum_family_tax_credit.outcome == "calculated"


def test_total_counts_an_ineligible_zero(wff_synthetic_all_approved_parameters: PolicyParameterSet) -> None:
    scenario = _partnered_household(partner_amount=Decimal(10000))
    result = calculate_wff(scenario, wff_synthetic_all_approved_parameters)

    assert result.best_start.outcome == "ineligible"
    values = [getattr(result, f.name).value for f in fields(WffResult)]
    assert result.total_annual_entitlement() == sum(values, start=Decimal(0))


# --- the reason code for each kind of blocker ---------------------------------


def test_an_unreviewed_rate_is_an_unresolved_rule(real_wff_parameters: PolicyParameterSet) -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    iwtc = calculate_wff(scenario, real_wff_parameters).in_work_tax_credit

    assert (iwtc.outcome, iwtc.reason_code, iwtc.missing) == ("needs_review", "unresolved_rule", ())
    assert iwtc.resolution is not None and "in_work_base" in iwtc.resolution


def test_a_date_outside_the_reviewed_year_is_an_unsupported_period() -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    result = run_wff_module(WFF_POLICY_DIR, date(2027, 6, 1), scenario, requested_policy_version="0.1.0")

    for f in fields(WffResult):
        component = getattr(result, f.name)
        assert (component.outcome, component.reason_code) == ("needs_review", "unsupported_period")


def test_a_lookup_date_outside_the_assessment_week_is_invalid_input() -> None:
    scenario = as_scenario_from_yaml(_as_case("ordinary_uncapped_jobseeker")["scenario"])
    result = run_as_module(
        AS_POLICY_DIR, date(2026, 6, 10), scenario, requested_policy_version=AS_POLICY_VERSION, assessment_week=WEEK
    )

    assert (result.outcome, result.reason_code) == ("needs_review", "invalid_input")


def test_an_out_of_scope_case_says_no_caller_input_resolves_it(real_wff_parameters: PolicyParameterSet) -> None:
    scenario = wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])
    best_start = calculate_wff(
        replace(scenario, best_start_no_shared_care=FactStatus.EXCLUDED), real_wff_parameters
    ).best_start

    assert (best_start.outcome, best_start.reason_code) == ("unsupported", "outside_scope")
    assert best_start.resolution is not None and "Not resolvable by supplying facts" in best_start.resolution


def test_the_r15_ceiling_names_the_lump_sum_fact_until_it_is_verified(real_as_parameters: PolicyParameterSet) -> None:
    """DEC-004: over the ceiling, an unverified lump-sum limit increase is a
    missing fact; once ruled out, the result is an evidenced $0."""
    scenario = replace(
        as_scenario_from_yaml(_as_case("ordinary_uncapped_jobseeker")["scenario"]), cash_assets=Decimal(20000)
    )
    unverified = calculate_accommodation_supplement(scenario, real_as_parameters)
    verified = calculate_accommodation_supplement(
        replace(scenario, specified_lump_sum_status=FactStatus.VERIFIED), real_as_parameters
    )

    assert (unverified.outcome, unverified.missing) == ("needs_review", ("specified_lump_sum_status",))
    assert unverified.resolution is not None and "Independence Allowance" in unverified.resolution
    assert (verified.outcome, verified.value) == ("ineligible", 0)


def test_zero_accommodation_costs_is_an_ineligible_zero(real_as_parameters: PolicyParameterSet) -> None:
    """DEC-005: s 65(1)(a) requires accommodation costs."""
    scenario = as_scenario_from_yaml(_as_case("ordinary_uncapped_jobseeker")["scenario"])
    result = calculate_accommodation_supplement(
        replace(scenario, weekly_accommodation_costs=Decimal(0)), real_as_parameters
    )

    assert (result.outcome, result.value, result.reason_code) == ("ineligible", 0, None)


# --- the contract ComponentResult enforces ----------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        {"outcome": "calculated"},
        {"outcome": "calculated", "value": Decimal(1), "reason_code": "missing_input"},
        {"outcome": "ineligible", "value": Decimal(5), "reason": "x"},
        {"outcome": "ineligible", "value": Decimal(0)},
        {"outcome": "needs_review", "reason": "x", "resolution": "y"},
        {"outcome": "needs_review", "reason": "x", "reason_code": "outside_scope", "resolution": "y"},
        {"outcome": "needs_review", "reason": "x", "reason_code": "missing_input", "resolution": "y"},
        {"outcome": "needs_review", "reason": "x", "reason_code": "unresolved_rule", "missing": ("a",), "resolution": "y"},
        {"outcome": "needs_review", "reason": "x", "reason_code": "unresolved_rule"},
        {"outcome": "unsupported", "reason": "x", "reason_code": "missing_input", "missing": ("a",), "resolution": "y"},
        {"outcome": "unsupported", "value": Decimal(0), "reason": "x", "reason_code": "outside_scope", "resolution": "y"},
    ],
)
def test_component_result_rejects_an_incomplete_or_inconsistent_result(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        ComponentResult(**kwargs)


# --- every protected case -------------------------------------------------------

_NESTED_REQUESTS: dict[str, type[BaseModel]] = {
    "children[]": ChildFactsRequest,
    "family_scheme_income": VerifiedIncomeRequest,
}


def _is_request_field(name: str, request: type[BaseModel]) -> bool:
    head, _, rest = name.partition(".")
    if not rest:
        return name in request.model_fields or name in HouseholdCalculationRequest.model_fields
    return head.removesuffix("[]") in request.model_fields and rest in _NESTED_REQUESTS[head].model_fields


def _check(label: str, component: ComponentResult, request: type[BaseModel]) -> None:
    if component.outcome in ("needs_review", "unsupported"):
        assert component.reason_code and component.resolution, label
        for name in component.missing:
            assert _is_request_field(name, request), f"{label}: '{name}' is not a request field"
    if component.outcome == "ineligible":
        # The reclassifications decided so far: Best Start (ADR-0014), and
        # AS's r 15 ceiling and $0 costs (DEC-004, DEC-005).
        assert label.endswith(("best_start", "accommodation_supplement")), label
        assert component.value == 0, label


def _as_case(case_id: str) -> dict[str, Any]:
    return next(c for c in load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases") if c["id"] == case_id)


def test_every_wff_spec_case_result_is_explained() -> None:
    cases = yaml.safe_load((WFF_POLICY_DIR / "spec_cases.yaml").read_text())["spec_cases"]
    seen_missing = set()
    for case in cases:
        parameters = load_policy_parameters(
            WFF_POLICY_DIR, case["modelled_date"], requested_policy_version=case["policy_version"]
        )
        result = calculate_wff(wff_scenario_from_yaml(case["scenario"]), parameters)
        for f in fields(WffResult):
            component = getattr(result, f.name)
            _check(f"{case['id']}.{f.name}", component, WffCalculationRequest)
            seen_missing.update(component.missing)
    assert seen_missing, "the spec cases exercise missing_input"


def test_every_as_spec_case_result_is_explained() -> None:
    for case in load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases"):
        result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
        _check(f"{case['id']}.accommodation_supplement", result, AsCalculationRequest)


def test_every_golden_household_result_is_explained() -> None:
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        run = run_scenario(
            record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CodeIdentity("test", None, None, None)
        )
        for f in fields(WffResult):
            _check(f"{household['id']}.{f.name}", getattr(run.result.wff, f.name), WffCalculationRequest)
        _check(f"{household['id']}.accommodation_supplement", run.result.accommodation_supplement, AsCalculationRequest)
