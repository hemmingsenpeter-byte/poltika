"""Pass 1, BUILD_PLAN_v0_3.md Task 1.1/1.2: the canonical household and its mappings."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from poltika.engines.simulator import wff as wff_engine
from poltika.engines.simulator.accommodation_supplement import (
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import PartnerStatus, WffScenario
from poltika.scenarios.household_mappings import (
    MappingRefusal,
    refusal_result,
    to_as,
    to_combined,
    to_wff,
)
from poltika.semantics import household as hh
from poltika.semantics.household import (
    Assertion,
    DatePeriod,
    Household,
    UnsupportedHousehold,
)
from poltika.semantics.population import PersonRole

YEAR = DatePeriod(start=date(2026, 4, 1), end=date(2027, 4, 1))
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
WEEK_PERIOD = DatePeriod(start=WEEK.start, end=WEEK.end)


def _household(children_complete: Assertion = Assertion.UNKNOWN, **overrides: object) -> Household:
    fields: dict[str, object] = {
        "household_id": "h1",
        "persons": (
            hh.Person(person_id="a", role=PersonRole.CLAIMANT),
            hh.Person(person_id="p", role=PersonRole.PARTNER),
            hh.Person(person_id="c1", role=PersonRole.DEPENDENT_CHILD, child_facts=hh.ChildFacts()),
        ),
        "families": (
            hh.Family(
                claimant_id="a",
                partner_status=hh.FamilyPartnerStatus.PARTNERED,
                partner_id="p",
                dependent_child_ids=("c1",),
                wff_children_complete=children_complete,
                as_children_complete=children_complete,
            ),
        ),
    }
    fields.update(overrides)
    return Household(**fields)  # type: ignore[arg-type]


def _spell(person: str, start: date, end: date, amount: str, **kw: object) -> hh.IncomeSpell:
    return hh.IncomeSpell(
        person_id=person,
        income_type=kw.pop("income_type", hh.IncomeType.EMPLOYMENT_EARNINGS),  # type: ignore[arg-type]
        start=start,
        end=end,
        amount=Decimal(amount),
        **kw,  # type: ignore[arg-type]
    )


# --- construction and refusal -------------------------------------------------


def test_a_household_holds_one_family_and_its_people() -> None:
    household = _household()
    assert household.family.claimant_id == "a"
    assert [p.role for p in household.persons] == [
        PersonRole.CLAIMANT,
        PersonRole.PARTNER,
        PersonRole.DEPENDENT_CHILD,
    ]


def test_a_multi_family_household_is_refused_with_a_reason() -> None:
    second = hh.Family(claimant_id="b")
    persons = (
        hh.Person(person_id="a", role=PersonRole.CLAIMANT),
        hh.Person(person_id="b", role=PersonRole.CLAIMANT),
    )
    with pytest.raises(UnsupportedHousehold, match="2 families.*one family per household"):
        Household(household_id="h2", persons=persons, families=(hh.Family(claimant_id="a"), second))


def test_family_must_refer_to_people_the_household_holds() -> None:
    with pytest.raises(ValidationError, match="does not hold"):
        _household(families=(hh.Family(claimant_id="nobody"),))


def test_spells_must_refer_to_people_and_not_overlap() -> None:
    with pytest.raises(ValidationError, match="unknown person"):
        _household(income_spells=(_spell("zz", date(2026, 4, 1), date(2026, 5, 1), "1"),))
    overlapping = (
        _spell("a", date(2026, 4, 1), date(2026, 6, 1), "1"),
        _spell("a", date(2026, 5, 1), date(2026, 7, 1), "1"),
    )
    with pytest.raises(ValidationError, match="overlap"):
        _household(income_spells=overlapping)
    # Different bases of the same income may overlap.
    _household(
        income_spells=(
            overlapping[0],
            _spell("a", date(2026, 5, 1), date(2026, 7, 1), "1", basis=hh.IncomeBasis.NET_OF_TAX),
        )
    )


def test_identity_ignores_the_order_of_people_and_spells() -> None:
    s1 = _spell("a", date(2026, 4, 1), date(2026, 5, 1), "1")
    s2 = _spell("a", date(2026, 5, 1), date(2026, 6, 1), "2")
    household = _household(income_spells=(s1, s2))
    shuffled = _household(income_spells=(s2, s1), persons=tuple(reversed(household.persons)))
    assert household.content_sha256() == shuffled.content_sha256()
    assert household.content_sha256() != _household(income_spells=(s1,)).content_sha256()


def test_annual_amount_over_a_tax_year_adds_spells_that_cover_it() -> None:
    household = _household(
        income_spells=(
            _spell("a", date(2026, 4, 1), date(2026, 10, 1), "20000"),
            _spell("a", date(2026, 10, 1), date(2027, 4, 1), "25000"),
        )
    )
    assert household.annual_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, YEAR) == Decimal(45000)


def test_a_gap_in_the_spells_is_unknown_never_zero() -> None:
    household = _household(income_spells=(_spell("a", date(2026, 4, 1), date(2026, 10, 1), "20000"),))
    assert household.annual_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, YEAR) is None
    assert household.annual_amount("a", hh.IncomeType.SELF_EMPLOYMENT_INCOME, YEAR) is None
    zero = _household(income_spells=(_spell("a", YEAR.start, YEAR.end, "0"),))
    assert zero.annual_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, YEAR) == Decimal(0)


def test_a_spell_straddling_the_period_is_not_scaled() -> None:
    spell = _spell("a", date(2026, 6, 1), date(2026, 6, 11), "100")
    household = _household(income_spells=(spell,))
    inside = DatePeriod(start=date(2026, 6, 3), end=date(2026, 6, 7))
    assert household.annual_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, inside) is None
    assert hh.straddling_spells((spell,), inside) == (spell,)


def test_weekly_amount_for_a_week_inside_a_longer_spell_is_unknown() -> None:
    household = _household(income_spells=(_spell("a", date(2026, 6, 1), date(2026, 6, 29), "2800"),))
    assert household.weekly_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, WEEK_PERIOD) is None


def test_weekly_amount_needs_a_seven_day_period() -> None:
    household = _household()
    with pytest.raises(ValueError, match="7 days"):
        household.weekly_amount("a", hh.IncomeType.EMPLOYMENT_EARNINGS, YEAR)


def test_every_income_type_the_policies_need_exists() -> None:
    assert {t.value for t in hh.IncomeType} >= {
        "employment_earnings",
        "self_employment_income",
        "main_benefit_income",
        "other_taxable_income",
        "non_taxable_income",
    }


# --- the semantics enums mirror the engines' values ------------------------------


def test_semantics_enums_match_the_engines_by_value() -> None:
    assert {a.value for a in Assertion} == {s.value for s in FactStatus}
    assert {c.value for c in hh.BestStartCohort} == {c.value for c in wff_engine.BestStartCohort}
    assert {s.value for s in hh.FamilyPartnerStatus} == {s.value for s in PartnerStatus}


# --- mappings: unknown stays unknown --------------------------------------------


def test_unknown_facts_stay_unknown_through_both_mappings() -> None:
    household = _household(Assertion.VERIFIED)
    wff = to_wff(household, YEAR)
    assert isinstance(wff, WffScenario)
    assert wff.household_eligibility is FactStatus.UNKNOWN
    assert wff.in_work_eligibility is FactStatus.UNKNOWN
    assert wff.partner_status is PartnerStatus.PARTNERED
    assert wff.family_scheme_income is None
    assert wff.children[0].qualifies_whole_year is FactStatus.UNKNOWN
    as_ = to_as(household, WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.household_eligibility is FactStatus.UNKNOWN
    assert as_.claimant_category is None
    assert as_.partner_status is None  # partnered, arrangement not recorded
    assert as_.dependent_children_count is None  # the child's AS status is unknown
    assert as_.weekly_income is None
    assert as_.weekly_accommodation_costs is None


def test_a_missing_partner_income_is_not_a_zero() -> None:
    household = _household(
        Assertion.VERIFIED,
        income_spells=(
            _spell(
                "a",
                YEAR.start,
                YEAR.end,
                "50000",
                income_type=hh.IncomeType.UNSPLIT_TOTAL,
                basis=hh.IncomeBasis.WFF_FAMILY_SCHEME,
            ),
        )
    )
    wff = to_wff(household, YEAR)
    assert isinstance(wff, WffScenario)
    assert wff.family_scheme_income is not None
    assert wff.family_scheme_income.claimant_amount == Decimal(50000)
    assert wff.family_scheme_income.partner_amount is None


def test_earnings_by_type_do_not_become_family_scheme_income() -> None:
    # WFF-02: family scheme income needs the subpart MB adjustments, which are
    # not derived from spells. The mapping leaves it unverified.
    household = _household(Assertion.VERIFIED, income_spells=(_spell("a", YEAR.start, YEAR.end, "50000"),))
    wff = to_wff(household, YEAR)
    assert isinstance(wff, WffScenario)
    assert wff.family_scheme_income is None


def test_a_partner_figure_without_the_claimants_is_refused() -> None:
    household = _household(
        Assertion.VERIFIED,
        income_spells=(
            _spell(
                "p",
                YEAR.start,
                YEAR.end,
                "20000",
                income_type=hh.IncomeType.UNSPLIT_TOTAL,
                basis=hh.IncomeBasis.WFF_FAMILY_SCHEME,
            ),
        )
    )
    refusal = to_wff(household, YEAR)
    assert isinstance(refusal, MappingRefusal)
    assert refusal.outcome == "needs_review"
    result = refusal_result(refusal)
    assert result.outcome == "needs_review" and result.value is None


def test_a_negative_income_is_refused_not_clamped() -> None:
    household = _household(
        Assertion.VERIFIED,
        income_spells=(
            _spell(
                "a",
                YEAR.start,
                YEAR.end,
                "-5",
                income_type=hh.IncomeType.UNSPLIT_TOTAL,
                basis=hh.IncomeBasis.WFF_FAMILY_SCHEME,
            ),
        )
    )
    assert isinstance(to_wff(household, YEAR), MappingRefusal)


def test_wff_needs_a_child_list_asserted_complete() -> None:
    # WFF reads its children list as complete, so an incomplete list is not a
    # known count: not a calculation on the children listed, and not
    # WFF_NO_DEPENDENT_CHILD for an empty list.
    for household in (
        _household(),
        _household(
            persons=(hh.Person(person_id="a", role=PersonRole.CLAIMANT),),
            families=(hh.Family(claimant_id="a", partner_status=hh.FamilyPartnerStatus.SINGLE),),
        ),
    ):
        refusal = to_wff(household, YEAR)
        assert isinstance(refusal, MappingRefusal)
        assert refusal.outcome == "needs_review"
        assert refusal.code == "HOUSEHOLD_CHILD_LIST_INCOMPLETE"
        assert refusal.missing_facts == ("wff_children_complete",)



def test_an_as_complete_child_list_is_not_a_complete_wff_list() -> None:
    # The two definitions are separate facts: an AS-only household with no AS
    # dependent children says nothing about WFF's children.
    household = _household(
        persons=(hh.Person(person_id="a", role=PersonRole.CLAIMANT),),
        families=(
            hh.Family(
                claimant_id="a",
                partner_status=hh.FamilyPartnerStatus.SINGLE,
                as_children_complete=Assertion.VERIFIED,
            ),
        ),
    )
    refusal = to_wff(household, YEAR)
    assert isinstance(refusal, MappingRefusal)
    assert refusal.code == "HOUSEHOLD_CHILD_LIST_INCOMPLETE"
    as_ = to_as(household, WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.dependent_children_count == 0


# --- the AS mapping: benefit spells, week view, children ---------------------------


def test_claimant_category_comes_from_a_benefit_spell_covering_the_whole_week() -> None:
    claimant = "a"
    covering = hh.BenefitSpell(
        person_id=claimant, benefit=hh.BenefitKind.SOLE_PARENT_SUPPORT, start=date(2026, 5, 1), end=date(2026, 7, 1)
    )
    as_ = to_as(_household(benefit_spells=(covering,)), WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.claimant_category is ClaimantCategory.SOLE_PARENT_SUPPORT
    part_week = hh.BenefitSpell(
        person_id=claimant, benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=date(2026, 6, 3), end=date(2026, 7, 1)
    )
    partial = to_as(_household(benefit_spells=(part_week,)), WEEK)
    assert not isinstance(partial, MappingRefusal)
    assert partial.claimant_category is None  # a part-week is not a verified category


def test_no_benefit_spell_is_a_verified_non_beneficiary_and_conflicts_are_refused() -> None:
    none = hh.BenefitSpell(person_id="a", benefit=hh.BenefitKind.NO_BENEFIT, start=WEEK.start, end=WEEK.end)
    as_ = to_as(_household(benefit_spells=(none,)), WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.claimant_category is ClaimantCategory.NON_BENEFICIARY
    both = (
        none,
        hh.BenefitSpell(person_id="a", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=WEEK.start, end=WEEK.end),
    )
    with pytest.raises(ValidationError, match="benefit spells for a overlap"):
        _household(benefit_spells=both)
    # The mapping refuses on its own too, for a household built without validation.
    unvalidated = _household().model_copy(update={"benefit_spells": both})
    assert isinstance(to_as(unvalidated, WEEK), MappingRefusal)


def test_benefit_spells_for_one_person_may_not_overlap() -> None:
    def spell(person_id: str, kind: hh.BenefitKind, start: date, end: date) -> hh.BenefitSpell:
        return hh.BenefitSpell(person_id=person_id, benefit=kind, start=start, end=end)

    with pytest.raises(ValidationError, match="benefit spells for a overlap"):
        _household(
            benefit_spells=(
                spell("a", hh.BenefitKind.JOBSEEKER_SUPPORT, date(2026, 5, 1), date(2026, 6, 10)),
                spell("a", hh.BenefitKind.JOBSEEKER_SUPPORT, date(2026, 6, 1), date(2026, 7, 1)),
            )
        )
    # Adjacent spells (end exclusive) do not overlap: a mid-week change is
    # recorded, and the week's category stays unverified rather than picked.
    changed = _household(
        benefit_spells=(
            spell("a", hh.BenefitKind.NO_BENEFIT, date(2026, 5, 1), date(2026, 6, 3)),
            spell("a", hh.BenefitKind.JOBSEEKER_SUPPORT, date(2026, 6, 3), date(2026, 7, 1)),
        )
    )
    as_ = to_as(changed, WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.claimant_category is None


def test_as_mapping_refuses_a_covering_spell_beside_part_week_receipt() -> None:
    covering = hh.BenefitSpell(person_id="a", benefit=hh.BenefitKind.NO_BENEFIT, start=WEEK.start, end=WEEK.end)
    one_day = hh.BenefitSpell(
        person_id="a", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=date(2026, 6, 3), end=date(2026, 6, 4)
    )
    unvalidated = _household().model_copy(update={"benefit_spells": (covering, one_day)})
    refusal = to_as(unvalidated, WEEK)
    assert isinstance(refusal, MappingRefusal)
    assert refusal.code == "HOUSEHOLD_MAPPING_INVALID_FACTS"
    # A spell outside the week is not receipt in it.
    later = hh.BenefitSpell(
        person_id="a", benefit=hh.BenefitKind.JOBSEEKER_SUPPORT, start=WEEK.end, end=date(2026, 7, 1)
    )
    as_ = to_as(_household(benefit_spells=(covering, later)), WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.claimant_category is ClaimantCategory.NON_BENEFICIARY


def test_partner_arrangement_gives_the_as_partner_type() -> None:
    household = _household(housing=hh.Housing(partner_arrangement=hh.PartnerArrangement.JOINT_TENANCY))
    as_ = to_as(household, WEEK)
    assert not isinstance(as_, MappingRefusal)
    assert as_.partner_status is PartnerType.JOINT_TENANCY


def test_dependent_child_count_applies_the_as_definition_per_child() -> None:
    persons = (
        hh.Person(person_id="a", role=PersonRole.CLAIMANT),
        hh.Person(
            person_id="c1",
            role=PersonRole.DEPENDENT_CHILD,
            child_facts=hh.ChildFacts(as_dependent_child=Assertion.VERIFIED),
        ),
        hh.Person(
            person_id="c2",
            role=PersonRole.DEPENDENT_CHILD,
            child_facts=hh.ChildFacts(as_dependent_child=Assertion.EXCLUDED),
        ),
    )

    def count(complete: Assertion) -> int | None:
        household = Household(
            household_id="h3",
            persons=persons,
            families=(
                hh.Family(
                    claimant_id="a",
                    partner_status=hh.FamilyPartnerStatus.SINGLE,
                    dependent_child_ids=("c1", "c2"),
                    as_children_complete=complete,
                ),
            ),
        )
        as_ = to_as(household, WEEK)
        assert not isinstance(as_, MappingRefusal)
        return as_.dependent_children_count

    assert count(Assertion.VERIFIED) == 1  # WFF counts two children, AS one
    assert count(Assertion.UNKNOWN) is None


def test_to_combined_carries_the_claimant_link_fact() -> None:
    household = _household(
        Assertion.VERIFIED,
        asserted_facts={"combined.as_claimant_is_wff_claimant_or_partner": Assertion.VERIFIED},
    )
    combined = to_combined(household, YEAR, WEEK)
    assert not isinstance(combined, MappingRefusal)
    assert combined.as_claimant_is_wff_claimant_or_partner is FactStatus.VERIFIED
    unlinked = to_combined(_household(Assertion.VERIFIED), YEAR, WEEK)
    assert not isinstance(unlinked, MappingRefusal)
    assert unlinked.as_claimant_is_wff_claimant_or_partner is FactStatus.UNKNOWN
