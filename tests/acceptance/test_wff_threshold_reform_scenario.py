"""The WFF threshold +$10,000 household scenario (12 October 2026).

Pinned so the figures reported for this scenario fail the build if they
ever stop reproducing. Four couples with two children, at $40,000, $60,000,
$80,000 and $100,000 family scheme income, run on WFF policy 0.1.0 with the
approved parameters and with the family tax credit abatement threshold
raised by $10,000. GPT/Codex sense-checked the reported figures outside the
review queue; that is not a review-queue clearance.

What the figures are: model outputs under stated assumptions, not statutory
expected values. The raised threshold is a `scenario_assumption`. The second
view also assumes the enacted temporary in-work tax credit base applies for
all 52 weeks, which `policy.yaml` holds at `needs_review` (an earlier Order
in Council could reverse it mid-year, and a mid-year reversal would need a
dated calculation with both rates). Neither view is a WFF total: minimum
family tax credit stays unresolved, and there is no income tax module, so
nothing here is a disposable-income figure.

Two checks run side by side. The literal figures are the ones reported, so
changing one means re-issuing the scenario, not editing the test. The hand
formula is written from the WFF specification's calculation sequence
(steps 2 and 3), independently of the engine, with every rate and threshold
read from `policy.yaml`:

    abatement = rate * floor(max(0, income - threshold))
    FTC  = max(0, eldest + additional - abatement)              (two children)
    IWTC = max(0, in_work_base - max(0, abatement - (eldest + additional)))

Author: Claude Code.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_FLOOR, Decimal

import pytest

from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    WffScenario,
    run_wff_module,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters, load_policy_spec
from poltika.scenarios.microsim.reform import Operation, Override, Reform, apply_reform
from tests.conftest import WFF_POLICY_DIR

VERSION = "0.1.0"
LOOKUP = date(2026, 6, 1)
V = FactStatus.VERIFIED
WFF = "working_for_families"

THRESHOLD_PLUS_10K = Override(
    policy_id=WFF,
    parameter_id="family_tax_credit_abatement_threshold",
    operation=Operation.ADD,
    value=Decimal(10000),
)


def _candidate_in_work_base() -> Decimal:
    """The enacted temporary rate from the `needs_review` row of
    `policy.yaml`. The loader never resolves that row, so it is read from
    the specification rather than restated here."""
    spec = load_policy_spec(WFF_POLICY_DIR / "policy.yaml")
    (row,) = next(p for p in spec.parameters if p.id == "in_work_base").values
    assert row.review_status.value == "needs_review"
    return Decimal(row.value)


FULL_YEAR_IN_WORK_BASE = Override(
    policy_id=WFF,
    parameter_id="in_work_base",
    operation=Operation.SET,
    value=_candidate_in_work_base(),
)

BASELINE = load_policy_parameters(WFF_POLICY_DIR, LOOKUP, requested_policy_version=VERSION)
REFORM = apply_reform(
    BASELINE, Reform(reform_id="wff threshold +10000", overrides=(THRESHOLD_PLUS_10K,))
)
BASELINE_IW = apply_reform(
    BASELINE, Reform(reform_id="full-year in-work base", overrides=(FULL_YEAR_IN_WORK_BASE,))
)
REFORM_IW = apply_reform(
    BASELINE,
    Reform(
        reform_id="wff threshold +10000, full-year in-work base",
        overrides=(THRESHOLD_PLUS_10K, FULL_YEAR_IN_WORK_BASE),
    ),
)


def _value(parameters: PolicyParameterSet, name: str) -> Decimal:
    value = parameters.get(name).value
    assert value is not None
    return value


GROSS_FTC = _value(BASELINE, "family_tax_credit_eldest_child") + _value(
    BASELINE, "family_tax_credit_additional_child"
)
RATE = _value(BASELINE, "family_tax_credit_abatement_rate")


def _abatement(income: Decimal, parameters: PolicyParameterSet) -> Decimal:
    threshold = _value(parameters, "family_tax_credit_abatement_threshold")
    return RATE * max(Decimal(0), income - threshold).to_integral_value(rounding=ROUND_FLOOR)


def _hand_ftc(income: Decimal, parameters: PolicyParameterSet) -> Decimal:
    return max(Decimal(0), GROSS_FTC - _abatement(income, parameters))


def _hand_subtotal(income: Decimal, parameters: PolicyParameterSet) -> Decimal:
    remaining = max(Decimal(0), _abatement(income, parameters) - GROSS_FTC)
    iwtc = max(Decimal(0), _value(parameters, "in_work_base") - remaining)
    return _hand_ftc(income, parameters) + iwtc


def _family(income: Decimal, **extra: object) -> WffScenario:
    child = ChildFacts(
        qualifies_whole_year=V,
        best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
        best_start_no_disqualifying_payment=V,
    )
    return WffScenario(
        household_eligibility=V,
        extra_instalment_status=V,
        children=[child, child],
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=VerifiedIncome(income, Decimal(0)),
        in_work_eligibility=V,
        mc6a_veterans_payment=V,
        mc6b_disqualifying_payment=V,
        ftc_iwtc_protected_or_direct_abatement=V,
        best_start_no_shared_care=V,
        best_start_protected_credit=V,
        **extra,  # type: ignore[arg-type]
    )


def _run(income: Decimal | str, parameters: PolicyParameterSet, **extra: object) -> WffResult:
    return run_wff_module(
        WFF_POLICY_DIR,
        LOOKUP,
        _family(Decimal(income), **extra),
        requested_policy_version=VERSION,
        parameters=parameters,
    )


def _subtotal(result: WffResult) -> Decimal:
    ftc, iwtc = result.family_tax_credit, result.in_work_tax_credit
    assert ftc.outcome == iwtc.outcome == "calculated"
    assert ftc.value is not None and iwtc.value is not None
    return ftc.value + iwtc.value


# income: (FTC now, FTC with reform), as reported.
REPORTED_FTC = {
    "40000": ("14375", "14375"),
    "60000": ("10222.5", "12972.5"),
    "80000": ("4722.5", "7472.5"),
    "100000": ("0", "1972.5"),
}
# income: (IWTC now, IWTC with reform, FTC + IWTC now, FTC + IWTC with reform),
# as reported under the full-year in-work base assumption.
REPORTED_SUBTOTAL = {
    "40000": ("7670", "7670", "22045", "22045"),
    "60000": ("7670", "7670", "17892.5", "20642.5"),
    "80000": ("7670", "7670", "12392.5", "15142.5"),
    "100000": ("6892.5", "7670", "6892.5", "9642.5"),
}


@pytest.mark.parametrize("income", sorted(REPORTED_FTC, key=int))
def test_family_tax_credit_with_approved_parameters(income: str) -> None:
    base, new = _run(income, BASELINE), _run(income, REFORM)
    for result, reported in zip((base, new), REPORTED_FTC[income], strict=True):
        assert result.family_tax_credit.outcome == "calculated"
        assert result.family_tax_credit.value == Decimal(reported)
        # The in-work base is unapproved, so no in-work credit and no total.
        assert result.in_work_tax_credit.outcome == "needs_review"
        assert result.in_work_tax_credit.code == "PARAMETER_NEEDS_REVIEW"
        assert result.minimum_family_tax_credit.outcome == "needs_review"
        assert result.best_start.outcome == "calculated" and result.best_start.value == 0
        assert result.total_annual_entitlement() is None
    assert (base.family_tax_credit.value, new.family_tax_credit.value) == (
        _hand_ftc(Decimal(income), BASELINE),
        _hand_ftc(Decimal(income), REFORM),
    )


@pytest.mark.parametrize("income", sorted(REPORTED_SUBTOTAL, key=int))
def test_subtotal_under_the_full_year_in_work_base_assumption(income: str) -> None:
    base, new = _run(income, BASELINE_IW), _run(income, REFORM_IW)
    iw_base, iw_new, sub_base, sub_new = map(Decimal, REPORTED_SUBTOTAL[income])
    assert (base.in_work_tax_credit.value, new.in_work_tax_credit.value) == (iw_base, iw_new)
    assert (_subtotal(base), _subtotal(new)) == (sub_base, sub_new)
    assert _subtotal(base) == _hand_subtotal(Decimal(income), BASELINE_IW)
    assert _subtotal(new) == _hand_subtotal(Decimal(income), REFORM_IW)
    # Still not a WFF total: minimum family tax credit is unresolved.
    assert new.minimum_family_tax_credit.outcome == "needs_review"
    assert new.total_annual_entitlement() is None


def test_at_100000_the_gain_is_split_between_the_two_credits() -> None:
    base, new = _run("100000", BASELINE_IW), _run("100000", REFORM_IW)
    assert new.family_tax_credit.value - base.family_tax_credit.value == Decimal("1972.5")
    assert new.in_work_tax_credit.value - base.in_work_tax_credit.value == Decimal("777.5")
    assert _subtotal(new) - _subtotal(base) == RATE * THRESHOLD_PLUS_10K.value == 2750


def test_assumed_values_are_labelled_and_sourced_values_are_not() -> None:
    uses = {
        use.parameter_id: use
        for use in _run("100000", REFORM_IW).family_tax_credit.trace.parameters
    }
    threshold = uses["family_tax_credit_abatement_threshold"]
    assert threshold.value == 54900
    assert threshold.review_status == "scenario_assumption"
    assert threshold.source_id is None
    assert uses["family_tax_credit_abatement_rate"].review_status == "approved"
    assert uses["family_tax_credit_abatement_rate"].source_id is not None
    in_work = {
        use.parameter_id: use
        for use in _run("100000", REFORM_IW).in_work_tax_credit.trace.parameters
    }["in_work_base"]
    assert in_work.review_status == "scenario_assumption" and in_work.source_id is None


# point: (now, with reform), as reported. Each is the lowest whole-dollar
# income at which the credit is zero.
REPORTED_PHASE_OUT: dict[str, tuple[PolicyParameterSet, PolicyParameterSet, int, int]] = {
    "family_tax_credit": (BASELINE_IW, REFORM_IW, 97173, 107173),
    "ftc_plus_iwtc": (BASELINE_IW, REFORM_IW, 125064, 135064),
}


def _credit(result: WffResult, point: str) -> Decimal:
    if point == "family_tax_credit":
        assert result.family_tax_credit.value is not None
        return result.family_tax_credit.value
    return _subtotal(result)


@pytest.mark.parametrize("point", sorted(REPORTED_PHASE_OUT))
def test_phase_out_points(point: str) -> None:
    base_params, reform_params, base_point, reform_point = REPORTED_PHASE_OUT[point]
    for parameters, income in ((base_params, base_point), (reform_params, reform_point)):
        assert _credit(_run(str(income - 1), parameters), point) > 0
        assert _credit(_run(str(income), parameters), point) == 0
    assert reform_point - base_point == THRESHOLD_PLUS_10K.value


# income: change in FTC + IWTC, under the full-year in-work base assumption.
# Whole dollars at each boundary, and fractional incomes, which abate on
# complete dollars only.
BOUNDARY_GAINS = {
    "44900": "0",
    "44901": "0.275",
    "44901.99": "0.275",
    "54899": "2749.725",
    "54900": "2750",
    "54900.50": "2750",
    "97173": "2750",
    "107173": "2750",
    "125063": "2750",
    "125063.99": "2750",
    "125064": "2749.9",
    "135063": "0.175",
    "135063.99": "0.175",
    "135064": "0",
}


@pytest.mark.parametrize("income", sorted(BOUNDARY_GAINS, key=Decimal))
def test_gain_at_the_boundaries(income: str) -> None:
    gain = _subtotal(_run(income, REFORM_IW)) - _subtotal(_run(income, BASELINE_IW))
    assert gain == Decimal(BOUNDARY_GAINS[income])
    assert gain == _hand_subtotal(Decimal(income), REFORM_IW) - _hand_subtotal(
        Decimal(income), BASELINE_IW
    )


def test_minimum_family_tax_credit_is_unchanged_by_the_reform() -> None:
    # Specification step 4: it "does not abate with the family/in-work
    # credits". The attested net income is a scenario fact chosen to give a
    # positive top-up, not a derived after-tax figure.
    facts = {
        "net_family_scheme_income": Decimal(34000),
        "net_family_scheme_income_me3_attested": True,
        "minimum_family_full_time_earner_weeks": V,
    }
    base, new = _run("40000", BASELINE, **facts), _run("40000", REFORM, **facts)
    assert base.minimum_family_tax_credit.outcome == "calculated"
    assert base.minimum_family_tax_credit.value == new.minimum_family_tax_credit.value
    assert base.minimum_family_tax_credit.value == (
        _value(BASELINE, "minimum_family_prescribed_amount") - 34000
    )
