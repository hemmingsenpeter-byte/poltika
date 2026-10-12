"""ADR-0017 Task 1.4 (D36 (4)): household inputs retire the pair checks a
household makes impossible and keep the rest, restated on its facts. Q19
(7): a relationship change in the WFF year is `unsupported`. The pair format
is unchanged (`test_combined.py`)."""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from itertools import product

import pytest
from pydantic import ValidationError

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek, ClaimantCategory
from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.wff import PartnerStatus, WffResult
from poltika.scenarios.combined import (
    SHARED_FACT_CHECKS,
    CombinedHouseholdScenario,
    run_combined_household,
    shared_fact_contradictions,
)
from poltika.scenarios.household_mappings import (
    HOUSEHOLD_CHECKS,
    LINK_FACT,
    RELATIONSHIP_FACT,
    RETIRED_FOR_HOUSEHOLD,
    AdapterRefused,
    HouseholdResult,
    MappingRefusal,
    household_from_combined,
    run_household,
    to_combined,
    to_wff,
)
from poltika.semantics import household as hh
from poltika.semantics.household import Assertion, DatePeriod, Household
from poltika.semantics.population import PersonRole
from tests.conftest import AS_POLICY_DIR, AS_POLICY_VERSION, WFF_POLICY_DIR
from tests.unit.scenarios.test_combined import LOOKUP, WEEK, WFF_VERSION, _as, _wff

TAX_YEAR = DatePeriod(start=date(2026, 4, 1), end=date(2027, 4, 1))


def _household(**pair: object) -> Household:
    """The test_combined consistent household as a `Household`, without the
    pair format's claimant-link fact (a household needs none)."""
    combined = CombinedHouseholdScenario(
        wff=pair.pop("wff", _wff()),  # type: ignore[arg-type]
        accommodation_supplement=_as(**pair),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    )
    household = household_from_combined(combined, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)
    facts = {k: v for k, v in household.asserted_facts.items() if k != LINK_FACT}
    return household.model_copy(update={"asserted_facts": facts})


def _with(household: Household, **update: object) -> Household:
    """A copy, revalidated (model_copy alone skips validation)."""
    return Household.model_validate({**household.model_dump(), **update})


def _run(household: Household, week: AssessmentWeek = WEEK) -> HouseholdResult | MappingRefusal:
    return run_household(
        household,
        tax_year=TAX_YEAR,
        assessment_week=week,
        wff_policy_dir=WFF_POLICY_DIR,
        as_policy_dir=AS_POLICY_DIR,
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        requested_wff_policy_version=WFF_VERSION,
        requested_as_policy_version=AS_POLICY_VERSION,
    )


def _pair_run(scenario: CombinedHouseholdScenario, week: AssessmentWeek = WEEK):  # type: ignore[no-untyped-def]
    return run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        scenario,
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=week,
        requested_wff_policy_version=WFF_VERSION,
        requested_as_policy_version=AS_POLICY_VERSION,
    )


def _components(result: HouseholdResult) -> list[ComponentResult]:
    combined = result.combined
    return [*(getattr(combined.wff, f.name) for f in fields(WffResult)), combined.accommodation_supplement]


def _originals(result: HouseholdResult) -> list[ComponentResult]:
    combined = result.combined
    return [
        *(getattr(combined.original_wff, f.name) for f in fields(WffResult)),
        combined.original_accommodation_supplement,
    ]


# ---------------------------------------------------------------- the check ledger


def test_every_pair_check_is_either_kept_or_retired_for_households() -> None:
    assert set(HOUSEHOLD_CHECKS) | set(RETIRED_FOR_HOUSEHOLD) == set(SHARED_FACT_CHECKS)
    assert not set(HOUSEHOLD_CHECKS) & set(RETIRED_FOR_HOUSEHOLD)


def _households_over_partner_and_benefit() -> list[Household]:
    """Every one-family household over partner status, arrangement, the
    claimant's benefit in the week and a child's AS status, skipping the
    ones household validation refuses."""
    built: list[Household] = []
    statuses = list(hh.FamilyPartnerStatus)
    arrangements = [None, *hh.PartnerArrangement]
    benefits = [None, *hh.BenefitKind]
    as_child = list(Assertion)
    for status, arrangement, benefit, child in product(statuses, arrangements, benefits, as_child):
        persons = [hh.Person(person_id="claimant", role=PersonRole.CLAIMANT)]
        partnered = status is hh.FamilyPartnerStatus.PARTNERED
        if partnered:
            persons.append(hh.Person(person_id="partner", role=PersonRole.PARTNER))
        persons.append(
            hh.Person(
                person_id="child_1",
                role=PersonRole.DEPENDENT_CHILD,
                child_facts=hh.ChildFacts(qualifies_whole_year=Assertion.VERIFIED, as_dependent_child=child),
            )
        )
        try:
            built.append(
                Household(
                    household_id="h1",
                    persons=tuple(persons),
                    families=(
                        hh.Family(
                            claimant_id="claimant",
                            partner_status=status,
                            partner_id="partner" if partnered else None,
                            dependent_child_ids=("child_1",),
                            wff_children_complete=Assertion.VERIFIED,
                            as_children_complete=Assertion.VERIFIED,
                        ),
                    ),
                    housing=hh.Housing(partner_arrangement=arrangement),
                    benefit_spells=()
                    if benefit is None
                    else (hh.BenefitSpell(person_id="claimant", benefit=benefit, start=WEEK.start, end=WEEK.end),),
                    asserted_facts={LINK_FACT: Assertion.VERIFIED},
                )
            )
        except ValidationError:
            continue
    return built


def test_retired_checks_cannot_be_constructed_from_a_household() -> None:
    # The pair checks run over every mapped household: none can produce a
    # partner-status or claimant-link contradiction, and a different child
    # count only ever means a child excluded under the AS definition.
    households = _households_over_partner_and_benefit()
    assert len(households) > 50
    for household in households:
        mapped = to_combined(household, TAX_YEAR, WEEK)
        assert not isinstance(mapped, MappingRefusal), household
        found = shared_fact_contradictions(mapped, (TAX_YEAR.start, TAX_YEAR.end), WEEK)
        assert not [c for c in found if c.startswith(("partner status", "precondition"))], (household, found)
        count = mapped.accommodation_supplement.dependent_children_count
        if count is not None and count != len(mapped.wff.children):
            child = household.person("child_1").child_facts
            assert child is not None and child.as_dependent_child is Assertion.EXCLUDED


def test_a_mixed_benefit_couple_on_a_single_family_cannot_be_held() -> None:
    household = _household()
    spell = hh.BenefitSpell(
        person_id="claimant", benefit=hh.BenefitKind.MIXED_BENEFIT_COUPLE, start=WEEK.start, end=WEEK.end
    )
    with pytest.raises(ValidationError, match="mixed-benefit couple"):
        _with(household, benefit_spells=(spell,))
    # The pair format can assert it; the adapter refuses it rather than build
    # a household the pair checks would flag (test_combined flags the pair).
    pair = CombinedHouseholdScenario(
        wff=_wff(),
        accommodation_supplement=_as(claimant_category=ClaimantCategory.MIXED_BENEFIT_COUPLE),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    )
    assert any(c.startswith("partner status") for c in shared_fact_contradictions(
        pair, (TAX_YEAR.start, TAX_YEAR.end), WEEK
    ))
    with pytest.raises(AdapterRefused, match="mixed-benefit couple"):
        household_from_combined(pair, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)


# ---------------------------------------------------------------- run_household


def test_a_consistent_household_gives_the_pair_result() -> None:
    household = _household()
    result = _run(household)
    assert isinstance(result, HouseholdResult)
    mapped = to_combined(_with(household, asserted_facts={**household.asserted_facts, LINK_FACT: "verified"}),
                         TAX_YEAR, WEEK)
    assert not isinstance(mapped, MappingRefusal)
    assert result.combined == _pair_run(mapped)
    assert result.combined.contradictions == ()
    assert result.definitional_differences == ()


def test_the_claimant_link_is_structural_and_a_carried_link_is_honoured() -> None:
    household = _household()
    assert LINK_FACT not in household.asserted_facts
    assert isinstance(_run(household), HouseholdResult)

    unknown = _run(_with(household, asserted_facts={**household.asserted_facts, LINK_FACT: "unknown"}))
    assert isinstance(unknown, MappingRefusal)
    assert (unknown.outcome, unknown.code, unknown.missing_facts) == (
        "needs_review", "HOUSEHOLD_PAIR_LINK_UNVERIFIED", (LINK_FACT,)
    )
    excluded = _run(_with(household, asserted_facts={**household.asserted_facts, LINK_FACT: "excluded"}))
    assert isinstance(excluded, MappingRefusal)
    assert (excluded.outcome, excluded.code) == ("unsupported", "HOUSEHOLD_PAIR_LINK_EXCLUDED")


def test_a_definitional_child_difference_is_reported_not_flagged() -> None:
    # Two WFF children, one of them excluded under the AS definition. The pair
    # format flags the count; the household records each child's status, so
    # nothing disagrees and every component keeps its own result.
    wff = replace(_wff(), children=[*_wff().children, *_wff().children])
    pair = CombinedHouseholdScenario(
        wff=wff, accommodation_supplement=_as(), as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED
    )
    assert any(c.startswith("dependent children") for c in _pair_run(pair).contradictions)

    result = _run(_household(wff=wff))
    assert isinstance(result, HouseholdResult)
    assert result.combined.contradictions == ()
    assert _components(result) == _originals(result)
    assert result.definitional_differences == (
        (
            "dependent children: 2 under the WFF definition, 1 under the AS definition (each child's status is "
            "recorded under each definition)"
        ),
    )


def test_a_week_outside_the_year_is_still_flagged() -> None:
    week = AssessmentWeek(start=date(2026, 3, 2), end=date(2026, 3, 9))
    combined = CombinedHouseholdScenario(
        wff=_wff(), accommodation_supplement=_as(), as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED
    )
    household = household_from_combined(combined, household_id="h1", tax_year=TAX_YEAR, assessment_week=week)
    household = household.model_copy(
        update={"asserted_facts": {k: v for k, v in household.asserted_facts.items() if k != LINK_FACT}}
    )
    result = _run(household, week)
    assert isinstance(result, HouseholdResult)
    assert [c for c in result.combined.contradictions if "not inside the WFF year" in c]
    for component, original in zip(_components(result), _originals(result), strict=True):
        assert component.outcome == ("unsupported" if original.outcome == "unsupported" else "needs_review")


def test_a_claimant_benefit_week_against_in_work_eligibility_is_refused() -> None:
    # The pair format flags it on every component; a household refuses it
    # (Q19 (5)): one benefit-receipt fact cannot also be verified absent.
    household = _household(claimant_category=ClaimantCategory.JOBSEEKER_SUPPORT, weekly_income=None)
    result = _run(household)
    assert isinstance(result, MappingRefusal)
    assert (result.outcome, result.code) == ("needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS")


@pytest.mark.parametrize(
    ("fact", "label"),
    [
        ("wff.ftc_iwtc_protected_or_direct_abatement", "no MD 14/15 protected family tax credit month"),
        ("wff.best_start_protected_credit", "no MG 4 protected Best Start month"),
    ],
)
def test_a_benefit_spell_in_the_year_flags_a_verified_no_protected_month(fact: str, label: str) -> None:
    # A partner's Jobseeker spell in the year, outside the AS week, with in-work
    # eligibility and MC 6(b) left unknown so Q19 (5) does not refuse it.
    pair = CombinedHouseholdScenario(
        wff=replace(
            _wff(),
            partner_status=PartnerStatus.PARTNERED,
            in_work_eligibility=FactStatus.UNKNOWN,
            mc6b_disqualifying_payment=FactStatus.UNKNOWN,
        ),
        accommodation_supplement=_as(partner_status=None),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    )
    base = household_from_combined(pair, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)
    facts = {k: v for k, v in base.asserted_facts.items() if k != LINK_FACT}
    for key in ("wff.ftc_iwtc_protected_or_direct_abatement", "wff.best_start_protected_credit"):
        facts[key] = Assertion.UNKNOWN
    facts[fact] = Assertion.VERIFIED
    spell = hh.BenefitSpell(
        person_id="partner", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=date(2026, 9, 7), end=date(2026, 9, 14)
    )
    result = _run(_with(base, asserted_facts=facts, benefit_spells=(*base.benefit_spells, spell)))
    assert isinstance(result, HouseholdResult)
    assert result.combined.contradictions == (
        (
            f"main benefit: 'partner' has jobseeker_support recorded for [2026-09-07, 2026-09-14) inside the "
            f"WFF year, WFF asserts {label} verified"
        ),
    )
    for component, original in zip(_components(result), _originals(result), strict=True):
        assert component.outcome == ("unsupported" if original.outcome == "unsupported" else "needs_review")
        if original.outcome != "unsupported":
            assert component.code == "COMBINED_SHARED_FACTS_DISAGREE"

    # Without the verified assertion the spell flags nothing.
    facts[fact] = Assertion.UNKNOWN
    quiet = _run(_with(base, asserted_facts=facts, benefit_spells=(*base.benefit_spells, spell)))
    assert isinstance(quiet, HouseholdResult) and quiet.combined.contradictions == ()


def test_the_tax_year_must_be_the_policy_year() -> None:
    with pytest.raises(ValueError, match="not the WFF policy's assessed year"):
        run_household(
            _household(),
            tax_year=DatePeriod(start=date(2025, 4, 1), end=date(2026, 4, 1)),
            assessment_week=WEEK,
            wff_policy_dir=WFF_POLICY_DIR,
            as_policy_dir=AS_POLICY_DIR,
            wff_lookup_date=LOOKUP,
            as_lookup_date=LOOKUP,
            requested_wff_policy_version=WFF_VERSION,
            requested_as_policy_version=AS_POLICY_VERSION,
        )


# ---------------------------------------------------------------- Q19 (7)


def test_a_relationship_change_in_the_year_is_unsupported() -> None:
    household = _household()
    changed = _with(household, asserted_facts={**household.asserted_facts, RELATIONSHIP_FACT: "excluded"})
    refusal = to_wff(changed, TAX_YEAR)
    assert isinstance(refusal, MappingRefusal)
    assert (refusal.outcome, refusal.code) == ("unsupported", "HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR")
    run = _run(changed)
    assert isinstance(run, MappingRefusal) and run.code == "HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR"

    # unsupported outranks the needs_review gates (here, an incomplete child list).
    incomplete = _with(
        changed, families=(household.family.model_copy(update={"wff_children_complete": Assertion.UNKNOWN}),)
    )
    refusal = to_wff(incomplete, TAX_YEAR)
    assert isinstance(refusal, MappingRefusal) and refusal.outcome == "unsupported"


@pytest.mark.parametrize("value", ["verified", "unknown"])
def test_an_unchanged_or_unknown_relationship_changes_no_mapping(value: str) -> None:
    household = _household()
    stated = _with(household, asserted_facts={**household.asserted_facts, RELATIONSHIP_FACT: value})
    assert to_wff(stated, TAX_YEAR) == to_wff(household, TAX_YEAR)
