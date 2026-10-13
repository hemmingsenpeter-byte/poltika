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


def test_the_link_cannot_fire_partner_status_only_via_a_mixed_couple_and_child_count_is_definitional() -> None:
    # The pair checks run over every mapped household. None can produce a
    # claimant-link contradiction; the only partner-status one is a single
    # family whose claimant has a mixed-benefit couple benefit (kept, narrowed);
    # a different child count only ever means a child excluded under AS.
    households = _households_over_partner_and_benefit()
    assert len(households) > 50
    for household in households:
        mapped = to_combined(household, TAX_YEAR, WEEK)
        assert not isinstance(mapped, MappingRefusal), household
        found = shared_fact_contradictions(mapped, (TAX_YEAR.start, TAX_YEAR.end), WEEK)
        assert not [c for c in found if c.startswith("precondition")], (household, found)
        mixed_on_single = household.family.partner_status is hh.FamilyPartnerStatus.SINGLE and any(
            s.benefit is hh.BenefitKind.MIXED_BENEFIT_COUPLE for s in household.benefit_spells
        )
        assert bool([c for c in found if c.startswith("partner status")]) == mixed_on_single, (household, found)
        count = mapped.accommodation_supplement.dependent_children_count
        if count is not None and count != len(mapped.wff.children):
            child = household.person("child_1").child_facts
            assert child is not None and child.as_dependent_child is Assertion.EXCLUDED


def test_a_mixed_benefit_couple_on_a_single_family_is_flagged_as_the_pair_is() -> None:
    # The AS spec case mixed_benefit_couple_is_unsupported is such a household,
    # so it must stay representable (ADR-0017 section 3's round trip).
    pair = CombinedHouseholdScenario(
        wff=_wff(),
        accommodation_supplement=_as(claimant_category=ClaimantCategory.MIXED_BENEFIT_COUPLE),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    )
    pair_result = _pair_run(pair)
    assert any(c.startswith("partner status") for c in pair_result.contradictions)
    result = _run(_household(claimant_category=ClaimantCategory.MIXED_BENEFIT_COUPLE))
    assert isinstance(result, HouseholdResult)
    assert result.combined.contradictions == (
        "partner status: the family is single, the claimant's benefit in the week is a mixed-benefit couple's",
    )
    assert result.combined.original_wff == pair_result.original_wff
    assert result.combined.original_accommodation_supplement == pair_result.original_accommodation_supplement
    for component, original in zip(_components(result), _originals(result), strict=True):
        assert component.outcome == ("unsupported" if original.outcome == "unsupported" else "needs_review")


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


def _two_listed_one_counted() -> tuple[object, Household]:
    """Two WFF list entries, an AS count of one: the pair, and the household
    the adapter builds from it (AS statuses derived from the count)."""
    wff = replace(_wff(), children=[*_wff().children, *_wff().children])
    pair = CombinedHouseholdScenario(
        wff=wff, accommodation_supplement=_as(), as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED
    )
    return pair, _household(wff=wff)


def test_a_count_derived_child_difference_keeps_the_pair_gate() -> None:
    # Codex #218 R1: the adapter's first-N marking is not membership (Q19 (2),
    # D38), so the household path flags it exactly as the pair path does.
    pair, household = _two_listed_one_counted()
    assert household.family.as_child_statuses_from_count
    pair_result = _pair_run(pair)  # type: ignore[arg-type]
    result = _run(household)
    assert isinstance(result, HouseholdResult)
    assert result.combined.contradictions == ("dependent children: WFF lists 2, AS asserts 1",)
    assert result.definitional_differences == ()
    assert [c.outcome for c in _components(result)] == [
        *(getattr(pair_result.wff, f.name).outcome for f in fields(WffResult)),
        pair_result.accommodation_supplement.outcome,
    ]
    assert not [c for c in _components(result) if c.outcome == "calculated"]


def test_a_supplied_per_child_difference_is_reported_not_flagged() -> None:
    # The same facts with each child's AS status supplied by the caller: nothing
    # disagrees, so every component keeps its own result.
    _, adapted = _two_listed_one_counted()
    family = adapted.family.model_copy(update={"as_child_statuses_from_count": False})
    result = _run(_with(adapted, families=(family,)))
    assert isinstance(result, HouseholdResult)
    assert result.combined.contradictions == ()
    assert _components(result) == _originals(result)
    assert result.definitional_differences == (
        (
            "dependent children: 2 entries in the WFF child list (whole-year qualification verified for 2), "
            "1 counted under the AS definition; the household records each child's status under each definition"
        ),
    )


def test_the_difference_does_not_present_unverified_entries_as_children() -> None:
    # Codex #218 R4: an entry whose whole-year qualification is unknown is
    # counted as an entry, not as an established WFF child.
    _, adapted = _two_listed_one_counted()
    persons = tuple(
        p.model_copy(update={"child_facts": p.child_facts.model_copy(update={"qualifies_whole_year": Assertion.UNKNOWN})})
        if p.person_id == "child_2" and p.child_facts is not None
        else p
        for p in adapted.persons
    )
    family = adapted.family.model_copy(update={"as_child_statuses_from_count": False})
    result = _run(_with(adapted, persons=persons, families=(family,)))
    assert isinstance(result, HouseholdResult)
    assert "whole-year qualification verified for 1" in result.definitional_differences[0]
    assert result.combined.wff.family_tax_credit.outcome == "needs_review"


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


@pytest.mark.parametrize("refused", [False, True])
def test_the_tax_year_must_be_the_policy_year(refused: bool) -> None:
    # Checked before anything runs, so a refusal cannot hide a wrong year.
    household = _household()
    if refused:
        household = _with(household, asserted_facts={**household.asserted_facts, RELATIONSHIP_FACT: "excluded"})
    with pytest.raises(ValueError, match="not the WFF policy's assessed year"):
        run_household(
            household,
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


def test_a_relationship_change_outranks_a_carried_unknown_link() -> None:
    household = _household()
    both = _with(
        household,
        asserted_facts={**household.asserted_facts, RELATIONSHIP_FACT: "excluded", LINK_FACT: "unknown"},
    )
    refusal = _run(both)
    assert isinstance(refusal, MappingRefusal)
    assert (refusal.outcome, refusal.code) == ("unsupported", "HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR")


def test_the_named_evidence_does_not_depend_on_spell_order() -> None:
    # Codex #218 R3: the same household (same content hash) listed in another
    # order names the same spell.
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
    spells = (
        hh.BenefitSpell(
            person_id="claimant", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=date(2026, 9, 7), end=date(2026, 9, 14)
        ),
        hh.BenefitSpell(
            person_id="partner",
            benefit=hh.BenefitKind.SUPPORTED_LIVING_PAYMENT,
            start=date(2026, 10, 5),
            end=date(2026, 10, 12),
        ),
    )
    forward = _with(base, asserted_facts=facts, benefit_spells=spells)
    reverse = _with(base, asserted_facts=facts, benefit_spells=spells[::-1])
    assert forward.content_sha256() == reverse.content_sha256()
    first, second = _run(forward), _run(reverse)
    assert isinstance(first, HouseholdResult) and isinstance(second, HouseholdResult)
    assert first.combined.contradictions == second.combined.contradictions
    assert "'claimant' has jobseeker_support" in first.combined.contradictions[0]
    assert _components(first) == _components(second)


def test_the_q19_5_refusal_does_not_depend_on_spell_order() -> None:
    # Codex #216 P3: a claimant Jobseeker week and a partner SLP week with
    # verified in-work eligibility; reversing the spells (same content hash)
    # names the same spell.
    pair = CombinedHouseholdScenario(
        wff=replace(_wff(), partner_status=PartnerStatus.PARTNERED),
        accommodation_supplement=_as(partner_status=None),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    )
    base = household_from_combined(pair, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)
    spells = (
        hh.BenefitSpell(
            person_id="claimant", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=date(2026, 6, 1), end=date(2026, 6, 8)
        ),
        hh.BenefitSpell(
            person_id="partner",
            benefit=hh.BenefitKind.SUPPORTED_LIVING_PAYMENT,
            start=date(2026, 9, 1),
            end=date(2026, 9, 8),
        ),
    )
    forward = _with(base, benefit_spells=spells)
    reverse = _with(base, benefit_spells=spells[::-1])
    assert forward.content_sha256() == reverse.content_sha256()
    first, second = to_wff(forward, TAX_YEAR), to_wff(reverse, TAX_YEAR)
    assert isinstance(first, MappingRefusal) and first == second
    assert first.code == "HOUSEHOLD_MAPPING_INVALID_FACTS"
    assert first.reason.startswith("'claimant' has jobseeker_support")
