"""Final executable acceptance checks for the deterministic v0.1 core.

The lower-level suite remains the authority for individual statutory rules,
official examples, scope gates, persistence and replay. These tests exercise
the release-level properties that cut across those slices: threshold
boundaries, generated invariants, cross-policy isolation, explanation
equivalence and repeatability.
"""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from poltika.engines.assurance.provenance import (
    build_combined_provenance_report,
    render_combined_markdown,
)
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.combined import CombinedHouseholdScenario, run_combined_household
from poltika.scenarios.record import CodeIdentity, ScenarioRecord, result_payload, run_scenario
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_scenario_from_yaml,
    wff_scenario_from_yaml,
)

MODELLED_DATE = date(2026, 6, 1)
ASSESSMENT_WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / "policy_specs"
    / "wff_as_interaction"
    / "golden_households.yaml"
)
MONEY_BOUNDARY_OFFSETS = (
    Decimal(-1),
    Decimal("-0.01"),
    Decimal(0),
    Decimal("0.01"),
    Decimal(1),
)


@pytest.fixture(scope="session")
def real_as_parameters() -> PolicyParameterSet:
    return load_policy_parameters(
        AS_POLICY_DIR,
        MODELLED_DATE,
        requested_policy_version=AS_POLICY_VERSION,
    )


def _value(parameters: PolicyParameterSet, parameter_id: str) -> Decimal:
    """A resolved statutory value, read from the policy rather than restated
    here: these tests live outside the statutory-value guard's paths, so a
    literal copy of a protected value could drift unnoticed."""
    value = parameters.get(parameter_id).value
    assert value is not None, parameter_id
    return value


def _ordinary_wff(income: Decimal) -> WffScenario:
    return WffScenario(
        household_eligibility=FactStatus.VERIFIED,
        extra_instalment_status=FactStatus.VERIFIED,
        children=[
            ChildFacts(
                qualifies_whole_year=FactStatus.VERIFIED,
                best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
                best_start_no_disqualifying_payment=FactStatus.VERIFIED,
            )
        ],
        partner_status=PartnerStatus.SINGLE,
        family_scheme_income=VerifiedIncome(claimant_amount=income),
        net_family_scheme_income=income,
        net_family_scheme_income_me3_attested=True,
        in_work_eligibility=FactStatus.VERIFIED,
        ftc_iwtc_protected_or_direct_abatement=FactStatus.VERIFIED,
        mc6a_veterans_payment=FactStatus.VERIFIED,
        mc6b_disqualifying_payment=FactStatus.VERIFIED,
        minimum_family_full_time_earner_weeks=FactStatus.VERIFIED,
        best_start_no_shared_care=FactStatus.VERIFIED,
        best_start_protected_credit=FactStatus.VERIFIED,
    )


def _ordinary_as(
    *, weekly_costs: Decimal, cash_assets: Decimal = Decimal(0)
) -> AsScenario:
    return AsScenario(
        household_eligibility=FactStatus.VERIFIED,
        claimant_category=ClaimantCategory.JOBSEEKER_SUPPORT,
        tenure_type=TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        partner_status=PartnerType.SINGLE,
        statistical_area_unit=Area.AREA_4,
        weekly_accommodation_costs=weekly_costs,
        dependent_children_count=0,
        cash_assets=cash_assets,
        exempt_cash_asset_status=FactStatus.VERIFIED,
        ordinary_rate_status=FactStatus.VERIFIED,
    )


def _golden_household(household_id: str) -> dict[str, Any]:
    households: list[dict[str, Any]] = yaml.safe_load(GOLDEN_PATH.read_text())["households"]
    return next(household for household in households if household["id"] == household_id)


def _record(household: dict[str, Any]) -> ScenarioRecord:
    return ScenarioRecord(
        household=CombinedHouseholdScenario(
            wff=wff_scenario_from_yaml(household["wff"]),
            accommodation_supplement=as_scenario_from_yaml(household["accommodation_supplement"]),
            as_claimant_is_wff_claimant_or_partner=FactStatus(household["precondition"]),
        ),
        wff_lookup_date=MODELLED_DATE,
        as_lookup_date=MODELLED_DATE,
        assessment_week=ASSESSMENT_WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )


@pytest.mark.parametrize("offset", MONEY_BOUNDARY_OFFSETS, ids=str)
def test_wff_abatement_threshold_five_point_boundary(
    offset: Decimal,
    wff_synthetic_all_approved_parameters: PolicyParameterSet,
) -> None:
    params = wff_synthetic_all_approved_parameters
    threshold = _value(params, "family_tax_credit_abatement_threshold")
    income = threshold + offset
    result = calculate_wff(_ordinary_wff(income), params)
    complete_dollars = max(Decimal(0), income - threshold).to_integral_value(
        rounding=ROUND_FLOOR
    )

    assert result.family_tax_credit.value == _value(
        params, "family_tax_credit_eldest_child"
    ) - complete_dollars * _value(params, "family_tax_credit_abatement_rate")


@pytest.mark.parametrize("offset", MONEY_BOUNDARY_OFFSETS, ids=str)
def test_as_entry_threshold_five_point_boundary(
    offset: Decimal,
    real_as_parameters: PolicyParameterSet,
) -> None:
    threshold = _value(
        real_as_parameters, "as_entry_threshold_jobseeker_support_single_no_dependent_children"
    )
    costs = threshold + offset
    result = calculate_accommodation_supplement(_ordinary_as(weekly_costs=costs), real_as_parameters)
    rate = _value(real_as_parameters, "rent_board_subsidy_rate")
    expected = (rate * max(Decimal(0), offset)).to_integral_value(
        rounding=ROUND_CEILING
    )

    assert result.outcome == "calculated"
    assert result.value == expected


@pytest.mark.parametrize("offset", MONEY_BOUNDARY_OFFSETS, ids=str)
def test_as_asset_ceiling_five_point_boundary(
    offset: Decimal,
    real_as_parameters: PolicyParameterSet,
) -> None:
    result = calculate_accommodation_supplement(
        _ordinary_as(
            weekly_costs=Decimal(250),
            cash_assets=_value(real_as_parameters, "asset_ceiling_other") + offset,
        ),
        real_as_parameters,
    )

    # r 15(1): cash assets "must not exceed" the ceiling -- exactly at it passes.
    if offset <= 0:
        assert result.outcome == "calculated"
        assert result.value is not None
    else:
        assert result.outcome == "unsupported"
        assert result.value is None


@settings(max_examples=500, derandomize=True, deadline=None)
@given(income_cents=st.integers(min_value=0, max_value=50_000_000))
def test_generated_wff_entitlements_obey_accounting_invariants(
    income_cents: int,
    wff_synthetic_all_approved_parameters: PolicyParameterSet,
) -> None:
    income = Decimal(income_cents) / 100
    result = calculate_wff(_ordinary_wff(income), wff_synthetic_all_approved_parameters)
    components = [getattr(result, field.name) for field in fields(WffResult)]

    assert all(component.outcome == "calculated" for component in components)
    assert all(component.value is not None and component.value >= 0 for component in components)
    assert result.total_annual_entitlement() == sum(
        (component.value for component in components if component.value is not None),
        start=Decimal(0),
    )
    assert result.family_tax_credit.value is not None
    assert result.family_tax_credit.value <= _value(
        wff_synthetic_all_approved_parameters, "family_tax_credit_eldest_child"
    )


@settings(max_examples=500, derandomize=True, deadline=None)
@given(
    # From 1 cent: $0 costs are an s 65AAA exclusion (unsupported), tested
    # in test_zero_accommodation_costs_is_unsupported_not_zero.
    first_cost_cents=st.integers(min_value=1, max_value=200_000),
    second_cost_cents=st.integers(min_value=1, max_value=200_000),
)
def test_generated_as_cost_increases_are_monotonic_and_capped(
    first_cost_cents: int,
    second_cost_cents: int,
    real_as_parameters: PolicyParameterSet,
) -> None:
    lower, upper = sorted((Decimal(first_cost_cents) / 100, Decimal(second_cost_cents) / 100))
    lower_result = calculate_accommodation_supplement(
        _ordinary_as(weekly_costs=lower), real_as_parameters
    )
    upper_result = calculate_accommodation_supplement(
        _ordinary_as(weekly_costs=upper), real_as_parameters
    )

    assert lower_result.outcome == upper_result.outcome == "calculated"
    assert lower_result.value is not None and upper_result.value is not None
    cap = _value(real_as_parameters, "area_cap_single_no_dependent_children_area4")
    assert Decimal(0) <= lower_result.value <= upper_result.value <= cap
    # Exact oracle for this no-income-test beneficiary: r 19 rounds up
    # min(rate x positive excess, cap); catches rate errors the <= $1
    # boundary offsets cannot (rounding up masks them there).
    threshold = _value(
        real_as_parameters, "as_entry_threshold_jobseeker_support_single_no_dependent_children"
    )
    rate = _value(real_as_parameters, "rent_board_subsidy_rate")
    for costs, result in ((lower, lower_result), (upper, upper_result)):
        oracle = min(rate * max(Decimal(0), costs - threshold), cap)
        assert result.value == oracle.to_integral_value(rounding=ROUND_CEILING)
    assert lower_result.value == lower_result.value.to_integral_value()
    assert upper_result.value == upper_result.value.to_integral_value()


def test_cross_policy_inputs_cannot_leak_between_modules() -> None:
    record = _record(_golden_household("g2_couple_two_children_income_abated_both"))
    baseline = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )

    changed_as_household = replace(
        record.household,
        accommodation_supplement=replace(
            record.household.accommodation_supplement,
            weekly_accommodation_costs=Decimal(800),
            weekly_income=Decimal(1500),
        ),
    )
    changed_as = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        changed_as_household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )
    assert changed_as.wff == baseline.wff
    assert changed_as.accommodation_supplement != baseline.accommodation_supplement

    changed_wff_household = replace(
        record.household,
        wff=replace(
            record.household.wff,
            family_scheme_income=VerifiedIncome(
                claimant_amount=Decimal(60000), partner_amount=Decimal(20000)
            ),
            net_family_scheme_income=Decimal(80000),
        ),
    )
    changed_wff = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        changed_wff_household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )
    assert changed_wff.wff != baseline.wff
    assert changed_wff.accommodation_supplement == baseline.accommodation_supplement


def test_explanation_values_are_the_recorded_calculation_values() -> None:
    record = _record(_golden_household("g2_couple_two_children_income_abated_both"))
    run = run_scenario(
        record,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("0.1.0", None, None, None),
    )
    report = build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    markdown = render_combined_markdown(report)
    payload = result_payload(run.result)

    for component in report["working_for_families"]["components"]:
        recorded = payload["wff"][component["component_id"]]
        assert (component["outcome"], component["value"], component["reason"]) == (
            recorded["outcome"],
            recorded["value"],
            recorded["reason"],
        )
        if component["value"] is not None:
            assert f"Value: {component['value']}" in markdown

    (as_component,) = report["accommodation_supplement"]["components"]
    recorded_as = payload["accommodation_supplement"]
    assert (as_component["outcome"], as_component["value"], as_component["reason"]) == (
        recorded_as["outcome"],
        recorded_as["value"],
        recorded_as["reason"],
    )
    assert f"Value: {as_component['value']}" in markdown


def test_same_input_and_versions_repeat_identically() -> None:
    record = _record(_golden_household("g2_couple_two_children_income_abated_both"))
    identity = CodeIdentity("0.1.0", "frozen-test-commit", True, "frozen-lock")
    expected = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=identity)

    for _ in range(100):
        repeated = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=identity)
        assert repeated.scenario_id == expected.scenario_id
        assert repeated.result_id == expected.result_id
        assert result_payload(repeated.result) == result_payload(expected.result)
