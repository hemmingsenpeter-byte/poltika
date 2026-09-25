"""v0.1.5 Phase 7 (Tasks 7.3, 7.6): release-level properties of results,
calculation steps and explanations, over generated households drawn from
the whole input space -- every fact status (verified, excluded, unknown),
missing values, and wide money ranges -- against the real approved
policies. Statutory values are read from the policy, never restated."""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from decimal import ROUND_CEILING, Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from poltika.engines.assurance.explanation import explain, verify
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from tests.conftest import AS_POLICY_DIR, AS_POLICY_VERSION, WFF_POLICY_DIR
from tests.unit.engines.simulator.test_calculation_steps import _recompute

LOOKUP = date(2026, 6, 1)
WFF_PARAMETERS = load_policy_parameters(WFF_POLICY_DIR, LOOKUP, requested_policy_version="0.1.0")
AS_PARAMETERS = load_policy_parameters(AS_POLICY_DIR, LOOKUP, requested_policy_version=AS_POLICY_VERSION)

status = st.sampled_from(list(FactStatus))
mostly_verified = st.one_of(st.just(FactStatus.VERIFIED), status)
money = st.decimals(min_value=0, max_value=400_000, places=2, allow_nan=False, allow_infinity=False)
weekly = st.decimals(min_value=0, max_value=3_000, places=2, allow_nan=False, allow_infinity=False)

children = st.lists(
    st.builds(
        ChildFacts,
        qualifies_whole_year=mostly_verified,
        best_start_cohort=st.sampled_from(list(BestStartCohort)),
        best_start_no_disqualifying_payment=mostly_verified,
    ),
    max_size=6,
)


@st.composite
def wff_scenarios(draw: st.DrawFn) -> WffScenario:
    partner = draw(st.sampled_from(list(PartnerStatus)))
    income = draw(st.one_of(st.none(), money))
    partner_amount = draw(money) if partner == PartnerStatus.PARTNERED and draw(st.booleans()) else None
    return WffScenario(
        household_eligibility=draw(mostly_verified),
        extra_instalment_status=draw(mostly_verified),
        children=draw(children),
        partner_status=partner,
        family_scheme_income=None if income is None else VerifiedIncome(income, partner_amount),
        net_family_scheme_income=draw(st.one_of(st.none(), money)),
        net_family_scheme_income_me3_attested=draw(st.booleans()),
        in_work_eligibility=draw(mostly_verified),
        ftc_iwtc_protected_or_direct_abatement=draw(mostly_verified),
        mc6a_veterans_payment=draw(mostly_verified),
        mc6b_disqualifying_payment=draw(mostly_verified),
        minimum_family_full_time_earner_weeks=draw(mostly_verified),
        best_start_no_shared_care=draw(mostly_verified),
        best_start_protected_credit=draw(mostly_verified),
    )


@st.composite
def as_scenarios(draw: st.DrawFn) -> AsScenario:
    def maybe(strategy: st.SearchStrategy[object]) -> object:
        return draw(st.one_of(st.none(), strategy))

    return AsScenario(
        household_eligibility=draw(mostly_verified),
        claimant_category=maybe(st.sampled_from(list(ClaimantCategory))),  # type: ignore[arg-type]
        tenure_type=maybe(st.sampled_from(list(TenureType))),  # type: ignore[arg-type]
        partner_status=maybe(st.sampled_from(list(PartnerType))),  # type: ignore[arg-type]
        statistical_area_unit=maybe(st.sampled_from(list(Area))),  # type: ignore[arg-type]
        weekly_accommodation_costs=maybe(weekly),  # type: ignore[arg-type]
        dependent_children_count=maybe(st.integers(min_value=0, max_value=6)),  # type: ignore[arg-type]
        cash_assets=maybe(st.decimals(min_value=0, max_value=40_000, places=2)),  # type: ignore[arg-type]
        exempt_cash_asset_status=draw(mostly_verified),
        weekly_income=maybe(weekly),  # type: ignore[arg-type]
        ordinary_rate_status=draw(mostly_verified),
        eldest_dependent_child_under_16=draw(mostly_verified),
    )


def _check_result(component_id: str, result: ComponentResult) -> None:
    # Never a silent zero or a negative amount; a value only when calculated.
    if result.outcome == "calculated":
        assert result.value is not None and result.value >= 0
        assert result.code is None
    else:
        assert result.value is None and result.code and result.reason
    # Every recorded step re-computes from its own inputs.
    assert result.trace is not None
    for step in result.trace.steps:
        expected = _recompute(step)
        if expected is not None:
            assert step.result == expected, step.step_id
    # The explanation agrees with the calculation, and is deterministic.
    explanation = explain(component_id, result)
    assert verify(explanation, result) == []
    assert explain(component_id, result) == explanation


@settings(max_examples=300, deadline=None)
@given(wff_scenarios())
def test_generated_wff_results_steps_and_explanations_are_consistent(scenario: WffScenario) -> None:
    result = calculate_wff(scenario, WFF_PARAMETERS)
    for f in fields(result):
        _check_result(f.name, getattr(result, f.name))
    # 7.6: the same input gives the same result, steps and explanation.
    again = calculate_wff(scenario, WFF_PARAMETERS)
    for f in fields(result):
        first, second = getattr(result, f.name), getattr(again, f.name)
        assert first == second and first.trace == second.trace


@settings(max_examples=300, deadline=None)
@given(as_scenarios())
def test_generated_as_results_steps_and_explanations_are_consistent(scenario: AsScenario) -> None:
    result = calculate_accommodation_supplement(scenario, AS_PARAMETERS)
    _check_result("accommodation_supplement", result)
    if result.outcome == "calculated":
        assert result.value is not None and result.trace is not None
        caps = [s for s in result.trace.steps if s.step_id == "AS_AREA_CAP"]
        # AS never exceeds the applicable maximum (rounded up to the dollar).
        for cap_step in caps:
            area_maximum = dict(cap_step.inputs)["area_maximum"]
            assert result.value <= Decimal(area_maximum).to_integral_value(rounding=ROUND_CEILING)


@settings(max_examples=150, deadline=None)
@given(scenario=as_scenarios(), other_income=weekly)
def test_a_beneficiarys_income_does_not_change_their_accommodation_supplement(
    scenario: AsScenario, other_income: Decimal
) -> None:
    """AS-08: main-benefit claimants have no separate AS income test, so
    their weekly income is irrelevant to the result."""
    if scenario.claimant_category not in (
        ClaimantCategory.JOBSEEKER_SUPPORT,
        ClaimantCategory.SOLE_PARENT_SUPPORT,
        ClaimantCategory.SUPPORTED_LIVING_PAYMENT,
    ):
        return
    before = calculate_accommodation_supplement(scenario, AS_PARAMETERS)
    after = calculate_accommodation_supplement(replace(scenario, weekly_income=other_income), AS_PARAMETERS)
    assert (before.outcome, before.value) == (after.outcome, after.value)


def _single_parent(income: Decimal, n_children: int) -> WffScenario:
    return WffScenario(
        household_eligibility=FactStatus.VERIFIED,
        extra_instalment_status=FactStatus.VERIFIED,
        children=[
            ChildFacts(FactStatus.VERIFIED, BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT, FactStatus.VERIFIED)
        ]
        * n_children,
        partner_status=PartnerStatus.SINGLE,
        family_scheme_income=VerifiedIncome(income),
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


@settings(max_examples=200, deadline=None)
@given(income=money, extra=st.decimals(min_value=0, max_value=50_000, places=2), n=st.integers(1, 6))
def test_more_income_never_raises_family_tax_credit(income: Decimal, extra: Decimal, n: int) -> None:
    lower = calculate_wff(_single_parent(income, n), WFF_PARAMETERS).family_tax_credit
    higher = calculate_wff(_single_parent(income + extra, n), WFF_PARAMETERS).family_tax_credit
    assert lower.value is not None and higher.value is not None
    assert higher.value <= lower.value


def _param(parameters: PolicyParameterSet, parameter_id: str) -> Decimal:
    value = parameters.get(parameter_id).value
    assert value is not None
    return value


@pytest.mark.parametrize("n", [1, 2, 3, 6])
def test_family_tax_credit_at_zero_income_is_the_gross_amount(n: int) -> None:
    result = calculate_wff(_single_parent(Decimal(0), n), WFF_PARAMETERS).family_tax_credit
    eldest = _param(WFF_PARAMETERS, "family_tax_credit_eldest_child")
    additional = _param(WFF_PARAMETERS, "family_tax_credit_additional_child")
    assert result.value == eldest + additional * (n - 1)
