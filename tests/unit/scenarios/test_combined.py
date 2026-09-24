"""Task 28.4: the combined WFF + AS household runner, against the Task 28.3
interaction contract (AS specification, "Task 28.3 WFF-AS interaction
contract"). Uses the real approved policies and the Task 28.2 dates."""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from decimal import Decimal

import pytest

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
    run_as_module,
)
from poltika.engines.simulator.wff import (
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    run_wff_module,
)
from poltika.scenarios.combined import (
    CombinedHouseholdScenario,
    CombinedResult,
    run_combined_household,
)
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    load_wff_spec_case,
    wff_scenario_from_yaml,
)

# Task 28.2 decisions (PR #49).
LOOKUP = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
WFF_VERSION = "0.1.0"


def _wff():  # type: ignore[no-untyped-def]
    # A single claimant with one child, in-work eligibility and MC 6(b)
    # verified (no main benefit in the year).
    return wff_scenario_from_yaml(load_wff_spec_case("single_ordinary_low_income")["scenario"])


def _as(**overrides: object) -> AsScenario:
    """The same household for AS: a single non-beneficiary with one child
    (a sole parent), consistent with the WFF scenario."""
    base: dict[str, object] = {
        "household_eligibility": FactStatus.VERIFIED,
        "claimant_category": ClaimantCategory.NON_BENEFICIARY,
        "tenure_type": TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        "partner_status": PartnerType.SINGLE,
        "statistical_area_unit": Area.AREA_1,
        "weekly_accommodation_costs": Decimal(400),
        "dependent_children_count": 1,
        "cash_assets": Decimal(1000),
        "exempt_cash_asset_status": FactStatus.VERIFIED,
        "weekly_income": Decimal(577),
        "ordinary_rate_status": FactStatus.VERIFIED,
        "eldest_dependent_child_under_16": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return AsScenario(**base)  # type: ignore[arg-type]


def _run(  # type: ignore[no-untyped-def]
    wff=None, as_=None, week: AssessmentWeek = WEEK, precondition: FactStatus = FactStatus.VERIFIED
) -> CombinedResult:
    return run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff or _wff(),
            accommodation_supplement=as_ or _as(),
            as_claimant_is_wff_claimant_or_partner=precondition,
        ),
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=week,
        requested_wff_policy_version=WFF_VERSION,
        requested_as_policy_version=AS_POLICY_VERSION,
    )


def _wff_components(result: WffResult) -> list:  # type: ignore[type-arg]
    return [getattr(result, f.name) for f in fields(WffResult)]


def test_consistent_household_returns_each_module_result_unchanged() -> None:
    combined = _run()
    assert combined.contradictions == ()
    assert combined.wff == run_wff_module(WFF_POLICY_DIR, LOOKUP, _wff(), requested_policy_version=WFF_VERSION)
    assert combined.accommodation_supplement == run_as_module(
        AS_POLICY_DIR, LOOKUP, _as(), requested_policy_version=AS_POLICY_VERSION, assessment_week=WEEK
    )
    assert combined.accommodation_supplement.outcome == "calculated"
    assert combined.wff.family_tax_credit.outcome == "calculated"


def test_periods_are_native_and_there_is_no_total() -> None:
    combined = _run()
    assert combined.wff_period == (date(2026, 4, 1), date(2027, 4, 1))
    assert combined.accommodation_supplement_period == (WEEK.start, WEEK.end)
    assert not any("total" in f.name for f in fields(CombinedResult))


def test_no_income_coupling_in_either_direction() -> None:
    """Changing one policy's income input never changes the other's result
    (CW 33(1)(a)/MB 13(2)(l); Schedule 3 cl 8(1)(l), DEC-003)."""
    base = _run()
    # $1,000 is above the sole-parent income level, so AS itself changes.
    higher_as_income = _run(as_=_as(weekly_income=Decimal(1000)))
    assert higher_as_income.wff == base.wff
    assert higher_as_income.accommodation_supplement.value != base.accommodation_supplement.value
    higher_wff_income = _run(wff=replace(_wff(), family_scheme_income=VerifiedIncome(claimant_amount=Decimal(90000))))
    assert higher_wff_income.accommodation_supplement == base.accommodation_supplement
    assert higher_wff_income.wff.family_tax_credit != base.wff.family_tax_credit


@pytest.mark.parametrize(
    ("wff_overrides", "as_overrides", "phrase"),
    [
        ({"partner_status": PartnerStatus.SINGLE}, {"partner_status": PartnerType.ORDINARY_COUPLE}, "partner status"),
        (
            {"partner_status": PartnerStatus.PARTNERED, "family_scheme_income": VerifiedIncome(Decimal(30000), Decimal(0))},
            {"partner_status": PartnerType.SINGLE},
            "partner status",
        ),
        ({}, {"claimant_category": ClaimantCategory.JOBSEEKER_SUPPORT}, "main benefit"),
        ({}, {"dependent_children_count": 2}, "dependent children"),
    ],
)
def test_each_disagreement_flags_every_non_unsupported_component(
    wff_overrides: dict[str, object], as_overrides: dict[str, object], phrase: str
) -> None:
    combined = _run(wff=replace(_wff(), **wff_overrides), as_=_as(**as_overrides))
    assert any(phrase in c for c in combined.contradictions)
    originals = [*_wff_components(combined.original_wff), combined.original_accommodation_supplement]
    for component, original in zip([*_wff_components(combined.wff), combined.accommodation_supplement], originals):
        # Provenance of the underlying module run is kept either way.
        assert component.trace is not None
        if original.outcome == "unsupported":
            assert component == original  # interim precedence: unsupported is kept
            continue
        assert component.outcome == "needs_review"
        assert component.value is None
        assert phrase in (component.reason or "")


def test_main_benefit_names_each_verified_wff_assertion() -> None:
    combined = _run(as_=_as(claimant_category=ClaimantCategory.SUPPORTED_LIVING_PAYMENT))
    assert len(combined.contradictions) == 2
    assert any("in-work eligibility" in c for c in combined.contradictions)
    assert any("MC 6(b)" in c for c in combined.contradictions)


def test_main_benefit_is_not_a_contradiction_when_wff_did_not_assert_no_main_benefit() -> None:
    wff = replace(_wff(), in_work_eligibility=FactStatus.UNKNOWN, mc6b_disqualifying_payment=FactStatus.UNKNOWN)
    combined = _run(wff=wff, as_=_as(claimant_category=ClaimantCategory.JOBSEEKER_SUPPORT))
    assert combined.contradictions == ()


def test_unverified_facts_are_left_to_each_policy() -> None:
    wff = replace(_wff(), partner_status=PartnerStatus.UNKNOWN)
    combined = _run(wff=wff, as_=_as(partner_status=None, dependent_children_count=None))
    assert combined.contradictions == ()
    # Each policy's own gates handle the unverified facts.
    assert combined.accommodation_supplement.outcome == "needs_review"


def test_week_outside_the_wff_year_is_a_contradiction() -> None:
    week = AssessmentWeek(start=date(2026, 3, 30), end=date(2026, 4, 6))
    combined = _run(week=week)
    assert any("not inside the WFF year" in c for c in combined.contradictions)
    assert combined.wff.family_tax_credit.outcome == "needs_review"


@pytest.mark.parametrize(
    "as_overrides",
    [
        {"partner_status": PartnerType.JOINT_TENANCY},
        {"claimant_category": ClaimantCategory.MIXED_BENEFIT_COUPLE},
    ],
)
def test_other_as_couple_forms_are_compared_with_wff_single(as_overrides: dict[str, object]) -> None:
    combined = _run(as_=_as(**as_overrides))
    assert any("partner status" in c for c in combined.contradictions)
    # AS is already unsupported for these forms and keeps that outcome; WFF,
    # which would otherwise publish a single-household result, is flagged.
    assert combined.accommodation_supplement.outcome == "unsupported"
    assert combined.wff.family_tax_credit.outcome == "needs_review"


def test_community_spouse_is_not_compared_pending_petes_decision() -> None:
    combined = _run(as_=_as(partner_status=PartnerType.COMMUNITY_SPOUSE_OR_PARTNER))
    assert not any("partner status" in c for c in combined.contradictions)


def test_unverified_precondition_flags_every_component() -> None:
    combined = _run(precondition=FactStatus.UNKNOWN)
    assert any("precondition" in c for c in combined.contradictions)
    assert combined.accommodation_supplement.outcome == "needs_review"
    assert combined.wff.family_tax_credit.outcome == "needs_review"


def test_excluded_precondition_makes_every_component_unsupported() -> None:
    combined = _run(precondition=FactStatus.EXCLUDED)
    for component in [*_wff_components(combined.wff), combined.accommodation_supplement]:
        assert component.outcome == "unsupported"
        assert component.value is None


def test_original_results_are_preserved_alongside_replacements() -> None:
    combined = _run(as_=_as(dependent_children_count=2))
    assert combined.original_wff == run_wff_module(WFF_POLICY_DIR, LOOKUP, _wff(), requested_policy_version=WFF_VERSION)
    assert combined.original_wff.family_tax_credit.outcome == "calculated"
    assert combined.wff.family_tax_credit.outcome == "needs_review"


def test_structural_errors_propagate() -> None:
    from poltika.common.errors import PolicyVersionMismatchError

    with pytest.raises(PolicyVersionMismatchError):
        run_combined_household(
            WFF_POLICY_DIR,
            AS_POLICY_DIR,
            CombinedHouseholdScenario(wff=_wff(), accommodation_supplement=_as()),
            wff_lookup_date=LOOKUP,
            as_lookup_date=LOOKUP,
            assessment_week=WEEK,
            requested_wff_policy_version=WFF_VERSION,
            requested_as_policy_version="0.1.0",
        )
