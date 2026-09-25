"""Task 12/13 (spec tests): `calculate_wff()` against the accepted Task 10
scoped calculation contract in `policy_specs/working_for_families/
specification.md`. Expected values are hand-derived independently from that
contract's formulas (MD 2(2)(c) ordering, MD 13(3)(a)/MG 3(2)(a) complete-
dollar abatement, exact Decimal arithmetic), not copied from an
implementation or an external engine, per the Review Doctrine.

Runs through Task 11's real loader throughout, but against two fixtures:
`parameters` is a synthetic policy.yaml carrying the real approved WFF rates
with every parameter (including `in_work_base`) approved, isolating the
arithmetic under test from the separate, already-scenario-specific in-work
rate-status gate; `real_wff_parameters` is the actual approved
`policy_specs/working_for_families/policy.yaml`, used only for the test that
exercises that live gate. Both go through the real loader, not a hand-built
`PolicyParameterSet` -- this is a spec/integration test of the whole Task 11
+ Task 12 pipeline, not a calculator-only unit test.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import load_policy_parameters

WFF_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "working_for_families"
MODELLED_DATE = date(2026, 6, 1)


@pytest.fixture()
def real_wff_parameters():
    """The real, approved WFF policy.yaml -- used only where a test's whole
    point is that `in_work_base`'s live `needs_review` status (Task 10.2's
    rate-status contract) must actually reach the calculator, which is the
    one thing a synthetic fixture with every parameter approved cannot
    exercise."""
    return load_policy_parameters(WFF_POLICY_DIR, MODELLED_DATE)


@pytest.fixture()
def parameters(tmp_path: Path):
    """A synthetic policy.yaml with the same statutory rates as the real,
    approved WFF spec, but with `in_work_base` also `approved` (rather than
    the real spec's live `needs_review`) -- isolates the arithmetic under
    test from the separate, already-covered concern of the in-work
    rate-status gate (see `real_wff_parameters` above and
    `test_in_work_base_needs_review_propagates_from_loader`)."""
    policy = {
        "schema_version": "0.1",
        "policy_id": "test_wff",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            _param("family_tax_credit_eldest_child", "money", "NZD_per_tax_year", "7921"),
            _param("family_tax_credit_additional_child", "money", "NZD_per_tax_year", "6454"),
            _param("family_tax_credit_abatement_threshold", "money", "NZD_per_tax_year", "44900"),
            _param(
                "family_tax_credit_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.275",
            ),
            _param("in_work_base", "money", "NZD_per_tax_year", "7670"),
            _param("in_work_additional_child", "money", "NZD_per_tax_year", "780"),
            _param(
                "minimum_family_prescribed_amount",
                "money",
                "NZD_per_tax_year_after_tax",
                "36604",
            ),
            _param(
                "best_start_annual_amount", "money", "NZD_per_child_per_tax_year", "4041"
            ),
            _param("best_start_abatement_threshold", "money", "NZD_per_tax_year", "79000"),
            _param(
                "best_start_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.21",
            ),
        ],
        "components": [],
        "outputs": {},
    }
    policy_dir = tmp_path
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return load_policy_parameters(policy_dir, MODELLED_DATE)


def _param(param_id: str, value_type: str, unit: str, value: str) -> dict:
    return {
        "id": param_id,
        "value_type": value_type,
        "unit": unit,
        "values": [
            {
                "effective_from": "2026-04-01",
                "effective_to": "2027-04-01",
                "value": value,
                "source_id": "test-source",
                "locator": "s 1",
                "review_status": "approved",
            }
        ],
    }


def _income(claimant_amount: object, *, partner_amount: object = None) -> VerifiedIncome:
    return VerifiedIncome(
        claimant_amount=Decimal(claimant_amount),
        partner_amount=Decimal(partner_amount) if partner_amount is not None else None,
    )


def _qualifying_child(**overrides: object) -> ChildFacts:
    base: dict[str, object] = {
        "qualifies_whole_year": FactStatus.VERIFIED,
        "best_start_cohort": BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
        "best_start_no_disqualifying_payment": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return ChildFacts(**base)


def _base_scenario(**overrides: object) -> WffScenario:
    base: dict[str, object] = {
        "household_eligibility": FactStatus.VERIFIED,
        "extra_instalment_status": FactStatus.VERIFIED,
        "children": [_qualifying_child()],
        "partner_status": PartnerStatus.SINGLE,
        "family_scheme_income": _income(30000),
        "net_family_scheme_income": Decimal(30000),
        "net_family_scheme_income_me3_attested": True,
        "in_work_eligibility": FactStatus.VERIFIED,
        "ftc_iwtc_protected_or_direct_abatement": FactStatus.VERIFIED,
        "mc6a_veterans_payment": FactStatus.VERIFIED,
        "mc6b_disqualifying_payment": FactStatus.VERIFIED,
        "minimum_family_full_time_earner_weeks": FactStatus.VERIFIED,
        "best_start_no_shared_care": FactStatus.VERIFIED,
        "best_start_protected_credit": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return WffScenario(**base)


# --- The ordinary full-year branch, exact-decimal arithmetic ------------------


def test_below_all_thresholds_full_entitlement(parameters):
    """Income below every abatement threshold: every component calculates at
    its full statutory rate, with no abatement at all."""
    scenario = _base_scenario(family_scheme_income=_income(30000))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "calculated"
    assert result.family_tax_credit.value == Decimal(7921)  # eldest only, no additional child
    assert result.in_work_tax_credit.outcome == "calculated"
    assert result.in_work_tax_credit.value == Decimal(7670)  # 1 child, no abatement remainder
    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.minimum_family_tax_credit.value == Decimal(6604)  # 36604 - 30000
    assert result.best_start.outcome == "calculated"
    assert result.best_start.value == Decimal(0)  # no cohort child in this scenario
    assert result.total_annual_entitlement() == Decimal(7921) + Decimal(7670) + Decimal(6604)


def test_half_cent_abatement_result_preserved_exactly(parameters):
    """specification.md: the 27.5-cent rate 'can produce a half-cent annual
    result'; the calculation core must preserve it exactly, not round."""
    # income = threshold + 1 -> excess = 1 complete dollar -> abatement = 0.275
    scenario = _base_scenario(family_scheme_income=_income(44901))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.value == Decimal(7921) - Decimal("0.275")
    assert result.family_tax_credit.value == Decimal("7920.725")


def test_abatement_excess_uses_complete_dollars_not_cents(parameters):
    """MD 13(3)(a): the rate applies to complete dollars of excess -- $0.99
    of excess must not itself trigger any abatement."""
    scenario = _base_scenario(family_scheme_income=_income("44900.99"))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.value == Decimal(7921)  # floor(0.99) == 0 -> no abatement


def test_additional_children_and_family_tax_credit_amounts(parameters):
    scenario = _base_scenario(
        children=[_qualifying_child(), _qualifying_child(), _qualifying_child()],
        family_scheme_income=_income(30000),
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.value == Decimal(7921) + 2 * Decimal(6454)


def test_in_work_additional_child_beyond_three(parameters):
    """4 qualifying children: base rate covers 1-3, the 4th adds $780."""
    scenario = _base_scenario(
        children=[_qualifying_child() for _ in range(4)],
        family_scheme_income=_income(20000),  # well under threshold, no abatement
    )

    result = calculate_wff(scenario, parameters)

    assert result.in_work_tax_credit.value == Decimal(7670) + Decimal(780)


def test_abatement_carries_from_family_credit_to_in_work_credit(parameters):
    """MD 2(2)(c): abatement is applied to family tax credit first; once it
    exceeds the family credit base, the *remainder* reduces in-work tax
    credit. Family tax credit floors at zero -- it must never go negative."""
    # 1 child: family_credit_base = 7921. Choose income so abatement clearly
    # exceeds that base: excess = 35100 (income 80000) -> abatement = 9652.5.
    scenario = _base_scenario(family_scheme_income=_income(80000))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "calculated"
    assert result.family_tax_credit.value == Decimal(0)  # floored, not negative
    # remaining_abatement = 9652.5 - 7921 = 1731.5; iwtc = 7670 - 1731.5
    assert result.in_work_tax_credit.outcome == "calculated"
    assert result.in_work_tax_credit.value == Decimal("5938.5")


def test_in_work_credit_floors_at_zero_when_remaining_abatement_exceeds_it(parameters):
    scenario = _base_scenario(family_scheme_income=_income(200000))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.value == Decimal(0)
    assert result.in_work_tax_credit.value == Decimal(0)


def test_minimum_family_tax_credit_zero_at_or_above_prescribed_amount(parameters):
    """specification.md: 'A verified net income at or above $36,604 yields no
    positive top-up' -- an explicit, calculated zero, not needs_review."""
    scenario = _base_scenario(net_family_scheme_income=Decimal(36604))

    result = calculate_wff(scenario, parameters)

    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.minimum_family_tax_credit.value == Decimal(0)


def test_best_start_single_cohort_child_with_abatement(parameters):
    scenario = _base_scenario(
        children=[_qualifying_child(best_start_cohort=BestStartCohort.IN_SUPPORTED_COHORT)],
        family_scheme_income=_income(80000),  # excess over 79000 = 1000 -> abate 210
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "calculated"
    assert result.best_start.value == Decimal(4041) - Decimal(210)


def test_best_start_no_cohort_child_is_a_real_calculated_zero(parameters):
    """No Best Start-eligible child is a genuine, evidenced zero -- not a
    scope limitation -- distinct from the multi-child case below, which is
    genuinely out of the v0.1 branch."""
    scenario = _base_scenario(children=[_qualifying_child(best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT)])

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "calculated"
    assert result.best_start.value == Decimal(0)


# --- unsupported: known structural exclusions ----------------------------------


def test_no_children_is_unsupported(parameters):
    scenario = _base_scenario(children=[])

    result = calculate_wff(scenario, parameters)

    for component in (
        result.family_tax_credit,
        result.in_work_tax_credit,
        result.minimum_family_tax_credit,
        result.best_start,
    ):
        assert component.outcome == "unsupported"
        assert component.value is None


def test_household_eligibility_excluded_is_unsupported_for_all_components(parameters):
    scenario = _base_scenario(household_eligibility=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    for component in (
        result.family_tax_credit,
        result.in_work_tax_credit,
        result.minimum_family_tax_credit,
        result.best_start,
    ):
        assert component.outcome == "unsupported"


def test_extra_instalment_status_applies_is_unsupported_for_all_components(parameters):
    """s 80KW: an applicable extra-instalment year is unsupported for the
    ordinary annual-entitlement branch -- for every component, not just one."""
    scenario = _base_scenario(extra_instalment_status=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    for component in (
        result.family_tax_credit,
        result.in_work_tax_credit,
        result.minimum_family_tax_credit,
        result.best_start,
    ):
        assert component.outcome == "unsupported"
        assert "80KW" in (component.reason or "")


def test_child_not_qualifying_whole_year_is_unsupported_for_whole_household(parameters):
    """A single non-qualifying child invalidates the whole scenario, per
    specification.md's whole-year-for-every-child domain precondition --
    not just an exclusion of that one child from the count."""
    scenario = _base_scenario(
        children=[_qualifying_child(), _qualifying_child(qualifies_whole_year=FactStatus.EXCLUDED)]
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "unsupported"


def test_mc6a_veterans_payment_disqualifies_ftc_iwtc_and_best_start_not_mftc(parameters):
    """specification.md: MC 6(a) 'can disqualify abating WFF and Best Start'
    -- family tax credit, in-work tax credit, Best Start. Minimum family tax
    credit does not abate and specification.md does not name it as MC 6(a)
    affected, so it must still calculate normally."""
    scenario = _base_scenario(mc6a_veterans_payment=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "unsupported"
    assert result.in_work_tax_credit.outcome == "unsupported"
    assert result.best_start.outcome == "unsupported"
    assert result.minimum_family_tax_credit.outcome == "calculated"


def test_md14_15_protected_credit_unsupported_for_ftc_and_iwtc(parameters):
    scenario = _base_scenario(ftc_iwtc_protected_or_direct_abatement=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "unsupported"
    assert result.in_work_tax_credit.outcome == "unsupported"
    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


def test_in_work_eligibility_excluded_only_affects_in_work_credit(parameters):
    scenario = _base_scenario(in_work_eligibility=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.in_work_tax_credit.outcome == "unsupported"
    assert result.family_tax_credit.outcome == "calculated"
    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


def test_me2_employment_exclusion_unsupported_only_for_minimum_family_credit(parameters):
    scenario = _base_scenario(minimum_family_full_time_earner_weeks=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.minimum_family_tax_credit.outcome == "unsupported"
    assert result.family_tax_credit.outcome == "calculated"


def test_mc6b_disqualifying_payment_unsupported_for_iwtc_and_mftc_not_ftc_or_best_start(parameters):
    """Task 12 review finding 1, confirmed against the official Act text
    (Income Tax Act 2007 s MC 6, checked 2026-09-21): MC 6(b) excludes
    in-work tax credit and minimum family tax credit when a main benefit or
    a parent's allowance/children's pension is received during the
    relationship period -- distinct from MC 6(a), which excludes family tax
    credit, in-work tax credit, and Best Start, but not minimum family tax
    credit. Before this fix, minimum family tax credit had no MC 6(b) check
    at all and could return a positive number regardless."""
    scenario = _base_scenario(mc6b_disqualifying_payment=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.in_work_tax_credit.outcome == "unsupported"
    assert "MC 6(b)" in (result.in_work_tax_credit.reason or "")
    assert result.minimum_family_tax_credit.outcome == "unsupported"
    assert "MC 6(b)" in (result.minimum_family_tax_credit.reason or "")
    assert result.family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


def test_mc6b_disqualifying_payment_unknown_is_needs_review_for_iwtc_and_mftc(parameters):
    scenario = _base_scenario(mc6b_disqualifying_payment=FactStatus.UNKNOWN)

    result = calculate_wff(scenario, parameters)

    assert result.in_work_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


def test_best_start_shared_care_unsupported_only_for_best_start(parameters):
    scenario = _base_scenario(best_start_no_shared_care=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "unsupported"
    assert result.family_tax_credit.outcome == "calculated"


def test_mg4_protected_credit_unsupported_only_for_best_start(parameters):
    scenario = _base_scenario(best_start_protected_credit=FactStatus.EXCLUDED)

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "unsupported"


def test_mc6c_disqualifying_payment_unsupported_only_for_best_start(parameters):
    scenario = _base_scenario(
        children=[
            _qualifying_child(
                best_start_cohort=BestStartCohort.IN_SUPPORTED_COHORT,
                best_start_no_disqualifying_payment=FactStatus.EXCLUDED,
            )
        ],
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "unsupported"
    assert result.family_tax_credit.outcome == "calculated"


def test_multiple_best_start_cohort_children_unsupported(parameters):
    scenario = _base_scenario(
        children=[
            _qualifying_child(best_start_cohort=BestStartCohort.IN_SUPPORTED_COHORT),
            _qualifying_child(best_start_cohort=BestStartCohort.IN_SUPPORTED_COHORT),
        ],
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "unsupported"
    assert "multi-child" in (result.best_start.reason or "") or "more than one" in (result.best_start.reason or "")


def test_best_start_other_cohort_child_is_unsupported_not_zero(parameters):
    """Task 12 review finding 2: a child outside the narrow 2024-04-01..
    2025-03-31 v0.1 cohort is NOT proven to have zero Best Start entitlement
    -- specification.md explicitly says later birth cohorts 'require
    separate review; do not apply this branch to them'. Before this fix,
    the only non-cohort state was a bool default False, which this same
    scenario would have silently reported as a calculated zero."""
    scenario = _base_scenario(
        children=[_qualifying_child(best_start_cohort=BestStartCohort.OTHER_COHORT_UNSUPPORTED)]
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "unsupported"
    assert result.best_start.value is None
    assert "narrow" in (result.best_start.reason or "") or "birth cohort" in (result.best_start.reason or "")
    # Every other component is unaffected by Best Start's own cohort facts.
    assert result.family_tax_credit.outcome == "calculated"


def test_best_start_unknown_cohort_child_is_needs_review_not_zero(parameters):
    scenario = _base_scenario(children=[_qualifying_child(best_start_cohort=BestStartCohort.UNKNOWN)])

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "needs_review"
    assert result.best_start.value is None


def test_best_start_genuine_zero_requires_verified_outside_entitlement(parameters):
    """The only state that yields a calculated zero is every child verified
    OUTSIDE_BEST_START_ENTITLEMENT -- distinguishing this from the two tests
    above (OTHER_COHORT_UNSUPPORTED, UNKNOWN) is the whole point of the fix:
    a real, evidenced absence of entitlement, not a default or a scope gap."""
    scenario = _base_scenario(
        children=[_qualifying_child(best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT)]
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "calculated"
    assert result.best_start.value == Decimal(0)


# --- needs_review: unverified facts, never a silent value or zero -------------


def test_household_eligibility_unknown_is_needs_review(parameters):
    scenario = _base_scenario(household_eligibility=FactStatus.UNKNOWN)

    result = calculate_wff(scenario, parameters)

    for component in (
        result.family_tax_credit,
        result.in_work_tax_credit,
        result.minimum_family_tax_credit,
        result.best_start,
    ):
        assert component.outcome == "needs_review"
        assert component.value is None


def test_missing_family_scheme_income_is_needs_review_not_zero(parameters):
    scenario = _base_scenario(family_scheme_income=None)

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.family_tax_credit.value is None


def test_missing_income_propagates_to_in_work_credit_via_md2_ordering(parameters):
    """Regression for a real bug caught during development: in-work tax
    credit's abatement depends on family tax credit's remaining_abatement
    (MD 2(2)(c)). If family tax credit can't be calculated at all (e.g.
    unverified income), in-work tax credit must not silently assume zero
    abatement and calculate a full, un-netted amount."""
    scenario = _base_scenario(family_scheme_income=None)

    result = calculate_wff(scenario, parameters)

    assert result.in_work_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.value is None


def test_missing_net_family_scheme_income_is_needs_review_only_for_mftc(parameters):
    scenario = _base_scenario(net_family_scheme_income=None)

    result = calculate_wff(scenario, parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.family_tax_credit.outcome == "calculated"


def test_unattested_net_income_is_needs_review_even_if_a_number_is_present(parameters):
    """specification.md: the input 'must attest to this derivation, not
    merely carry an after-tax label' -- an unattested number must not be
    silently trusted as ME 3-derived."""
    scenario = _base_scenario(
        net_family_scheme_income=Decimal(20000),
        net_family_scheme_income_me3_attested=False,
    )

    result = calculate_wff(scenario, parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"


def test_in_work_base_needs_review_propagates_from_loader(real_wff_parameters):
    """The loader resolves `in_work_base` to needs_review for any full-year
    2026-27 request (Task 10.2 rate-status contract) -- calculate_wff() must
    surface that, never a silent $7,670. Uses the real approved WFF
    policy.yaml, not the synthetic all-approved fixture, since that's
    exactly the live gate under test."""
    result = calculate_wff(_base_scenario(), real_wff_parameters)

    assert result.in_work_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.value is None
    assert "in_work_base" in (result.in_work_tax_credit.reason or "")

    # Every other component is unaffected by in_work_base's status -- they
    # still calculate normally against the real spec.
    assert result.family_tax_credit.outcome == "calculated"
    assert result.minimum_family_tax_credit.outcome == "calculated"
    assert result.best_start.outcome == "calculated"


# --- unsupported takes precedence over needs_review when both are present -----


def test_unsupported_takes_precedence_over_needs_review_at_household_gate(parameters):
    scenario = _base_scenario(
        household_eligibility=FactStatus.EXCLUDED,
        extra_instalment_status=FactStatus.UNKNOWN,
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "unsupported"


def test_unsupported_takes_precedence_over_needs_review_within_a_component(parameters):
    """The same precedence rule applies *within* one component's own checks,
    not just at the household gate: if one fact is a known exclusion
    (unsupported) and a different, independently-checked fact for the same
    component is merely unverified (needs_review), the component must report
    unsupported -- a definite finding, not the weaker unverified one."""
    scenario = _base_scenario(
        ftc_iwtc_protected_or_direct_abatement=FactStatus.EXCLUDED,  # checked first
        mc6a_veterans_payment=FactStatus.UNKNOWN,  # checked second
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "unsupported"
    assert "MD 14/15" in (result.family_tax_credit.reason or "")
    assert result.in_work_tax_credit.outcome == "unsupported"
    # mc6a_veterans_payment is UNKNOWN (not excluded) in this scenario, and
    # best_start does not depend on ftc_iwtc_protected_or_direct_abatement at
    # all -- it correctly reports needs_review for its own, independent
    # reason rather than inheriting family tax credit's unsupported finding.
    assert result.best_start.outcome == "needs_review"
    assert "MC 6(a)" in (result.best_start.reason or "")
    assert result.minimum_family_tax_credit.outcome == "calculated"


# --- total_annual_entitlement() never sums a partial result -------------------


def test_total_is_none_when_any_component_is_not_calculated(parameters):
    scenario = _base_scenario(family_scheme_income=None)

    result = calculate_wff(scenario, parameters)

    assert result.total_annual_entitlement() is None


def test_total_sums_only_when_every_component_is_calculated(parameters):
    scenario = _base_scenario(family_scheme_income=_income(30000))

    result = calculate_wff(scenario, parameters)

    total = result.total_annual_entitlement()
    assert total is not None
    assert total == (
        result.family_tax_credit.value
        + result.in_work_tax_credit.value
        + result.minimum_family_tax_credit.value
        + result.best_start.value
    )


# --- malformed input is rejected structurally, not resolved as a policy outcome


def test_negative_claimant_income_rejected() -> None:
    with pytest.raises(ValueError, match="claimant_amount"):
        VerifiedIncome(claimant_amount=Decimal(-1))


def test_negative_partner_income_rejected() -> None:
    with pytest.raises(ValueError, match="partner_amount"):
        VerifiedIncome(claimant_amount=Decimal(30000), partner_amount=Decimal(-1))


def test_negative_net_family_scheme_income_rejected() -> None:
    with pytest.raises(ValueError, match="net_family_scheme_income"):
        _base_scenario(net_family_scheme_income=Decimal(-1))


# --- partnered income: combined-branch verification boundary (Task 12 review finding 3)


def test_single_claimant_combined_equals_claimant_amount(parameters):
    """No partner: `combined` is just the claimant's verified amount, and the
    ordinary branch proceeds exactly as for a single scalar figure."""
    scenario = _base_scenario(family_scheme_income=_income(30000))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "calculated"
    assert result.family_tax_credit.value == Decimal(7921)  # below threshold, no abatement


def test_partnered_combined_income_used_for_abatement(parameters):
    """specification.md: the ordinary branch uses the combined amount once
    each person's individual amount is verified non-negative."""
    # claimant 30000 + partner 20000 = 50000 combined; excess over 44900 = 5100
    scenario = _base_scenario(
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=_income(30000, partner_amount=20000),
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "calculated"
    expected_abatement = Decimal("0.275") * Decimal(5100)
    assert result.family_tax_credit.value == Decimal(7921) - expected_abatement


# --- partner status: closes the gap where VerifiedIncome alone can't tell
# --- "no partner" from "partnered but partner income unverified" (Task 12
# --- review finding, PR #14)


def test_partnered_missing_partner_income_is_needs_review_not_a_number(parameters):
    """The blocking gap from the second PR #14 re-review: a partnered
    claimant whose partner's income was never verified must not produce a
    numeric result using the claimant's amount alone -- that would silently
    understate (or otherwise misstate) the combined figure specification.md
    requires."""
    scenario = _base_scenario(
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=_income(30000),  # no partner_amount supplied
    )

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "needs_review"
    assert result.family_tax_credit.value is None
    assert "partner" in (result.family_tax_credit.reason or "").lower()


def test_partnered_missing_partner_income_needs_review_for_best_start_too(parameters):
    scenario = _base_scenario(
        partner_status=PartnerStatus.PARTNERED,
        family_scheme_income=_income(30000),
        children=[_qualifying_child(best_start_cohort=BestStartCohort.IN_SUPPORTED_COHORT)],
    )

    result = calculate_wff(scenario, parameters)

    assert result.best_start.outcome == "needs_review"
    assert result.best_start.value is None


def test_unknown_partner_status_is_needs_review_even_with_a_single_income_figure(parameters):
    """If partner status itself is unverified, a claimant-only income figure
    can't be trusted as the correct ordinary-branch amount either -- it
    might be missing a partner's income that was never asked for."""
    scenario = _base_scenario(partner_status=PartnerStatus.UNKNOWN, family_scheme_income=_income(30000))

    result = calculate_wff(scenario, parameters)

    assert result.family_tax_credit.outcome == "needs_review"
    assert "partner status" in (result.family_tax_credit.reason or "")


def test_unknown_partner_status_is_needs_review_for_minimum_family_tax_credit_too(parameters):
    """Second PR #14 re-review finding: minimum family tax credit's own MA 7
    full-time-earner test has a different hour threshold for a single
    claimant (20 hours) than for a partnered one (30 combined hours) --
    specification.md. A `minimum_family_full_time_earner_weeks: VERIFIED`
    fact alone doesn't say which threshold was actually applied, so an
    unverified partner status must still block a numeric result here, even
    though minimum family tax credit doesn't use combined income at all
    (unlike family tax credit / Best Start, which the first partner-status
    fix already covered)."""
    scenario = _base_scenario(partner_status=PartnerStatus.UNKNOWN)

    result = calculate_wff(scenario, parameters)

    assert result.minimum_family_tax_credit.outcome == "needs_review"
    assert result.minimum_family_tax_credit.value is None
    assert "full-time-earner" in (result.minimum_family_tax_credit.reason or "")
    # family tax credit is needs_review too (the first partner-status fix,
    # via _partner_income_gap_reason), and in-work tax credit inherits that
    # via the existing MD 2(2)(c) remaining-abatement propagation -- not a
    # new partner-status check on in-work tax credit itself.
    assert result.family_tax_credit.outcome == "needs_review"
    assert result.in_work_tax_credit.outcome == "needs_review"


def test_single_claimant_with_partner_amount_rejected() -> None:
    """A structural contradiction, not a policy outcome: SINGLE means no
    partner exists to have a verified amount at all."""
    with pytest.raises(ValueError, match="partner_amount"):
        _base_scenario(
            partner_status=PartnerStatus.SINGLE,
            family_scheme_income=_income(30000, partner_amount=10000),
        )



def test_zero_floor_keeps_the_components_decimal_scale(real_wff_parameters) -> None:  # type: ignore[no-untyped-def]
    """v0.1 question set QS-3: a floored credit read `0` while its unfloored
    neighbour read `7920.725`; the zero now keeps the component's scale."""
    from tests.conftest import wff_scenario_from_yaml

    scenario = wff_scenario_from_yaml(
        {
            "household_eligibility": "verified", "extra_instalment_status": "verified",
            "partner_status": "single", "family_scheme_income": {"claimant_amount": "500000"},
            "in_work_eligibility": "verified", "ftc_iwtc_protected_or_direct_abatement": "verified",
            "mc6a_veterans_payment": "verified", "mc6b_disqualifying_payment": "verified",
            "minimum_family_full_time_earner_weeks": "verified",
            "best_start_no_shared_care": "verified", "best_start_protected_credit": "verified",
            "children": [{"qualifies_whole_year": "verified", "best_start_cohort": "in_supported_cohort",
                          "best_start_no_disqualifying_payment": "verified"}],
        }
    )
    result = calculate_wff(scenario, real_wff_parameters)
    assert result.family_tax_credit.value == 0
    assert str(result.family_tax_credit.value) == "0.000"
    assert str(result.best_start.value) == "0.00"


def test_mftc_excluded_full_time_earner_weeks_reason_covers_not_a_full_time_earner(real_wff_parameters) -> None:  # type: ignore[no-untyped-def]
    """v0.1 question set QS-5: `excluded` is also how a caller says "not a
    full-time earner", but the reason named only the ME 2(2)-(4) case. The
    outcome stays `unsupported` pending Pete's interpretation decision."""
    from dataclasses import replace

    from tests.conftest import wff_scenario_from_yaml

    base = wff_scenario_from_yaml(
        {
            "household_eligibility": "verified", "extra_instalment_status": "verified",
            "partner_status": "single", "family_scheme_income": {"claimant_amount": "30000"},
            "net_family_scheme_income": "30000", "net_family_scheme_income_me3_attested": True,
            "in_work_eligibility": "verified", "ftc_iwtc_protected_or_direct_abatement": "verified",
            "mc6a_veterans_payment": "verified", "mc6b_disqualifying_payment": "verified",
            "minimum_family_full_time_earner_weeks": "verified",
            "best_start_no_shared_care": "verified", "best_start_protected_credit": "verified",
            "children": [{"qualifies_whole_year": "verified", "best_start_cohort": "outside_best_start_entitlement",
                          "best_start_no_disqualifying_payment": "verified"}],
        }
    )
    result = calculate_wff(
        replace(base, minimum_family_full_time_earner_weeks=FactStatus.EXCLUDED), real_wff_parameters
    )
    assert result.minimum_family_tax_credit.outcome == "unsupported"
    assert "not a full-time earner" in (result.minimum_family_tax_credit.reason or "")
