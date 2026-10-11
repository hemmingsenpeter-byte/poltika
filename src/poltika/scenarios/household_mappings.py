"""Pass 1 (ADR-0017, BUILD_PLAN_v0_3.md Phase 1 Tasks 1.2-1.3): the named
mappings between the canonical `Household` and each policy's input type.

- `to_wff(household, tax_year)` and `to_as(household, assessment_week)`
  derive `WffScenario` and `AsScenario`; `to_combined()` builds the pair the
  combined runner takes. Every field cites the specification rule or
  definition it follows (rule ids are those in
  `policy_specs/working_for_families/specification.md` WFF-01..09 and
  `policy_specs/accommodation_supplement/specification.md` AS-01..11, with
  decision ids DEC-001..003).
- A mapping never guesses. An unknown fact is passed on as unknown (the
  engine then returns `needs_review`). Where the household cannot supply a
  field exactly, the mapping returns a `MappingRefusal` naming the reason.
- `household_from_combined()`, `household_from_wff()`, `household_from_as()`
  and `household_from_record()` are the adapters in the other direction: the
  existing request formats enter the household path through them. They
  raise `AdapterRefused` where the scenario pair cannot be held as one set
  of facts (see each rule below).

Where the mapping and the adapters meet, the convention is fixed here:

- Facts that are bundles a policy defines (`household_eligibility`,
  `in_work_eligibility` and so on) are household-level asserted facts, keyed
  `wff.<name>`, `as.<name>` or `combined.<name>`. They are asserted, not
  derived: deriving them from spells is policy logic the later policies and
  Task 1.4 own (backlog P2-HH-02).
- Figures a policy defines in its own terms are spells whose `basis` is that
  policy's (WFF family scheme income per person, ME 3 net family scheme
  income and AS weekly income as family figures held on the claimant).
  Earnings by type are never turned into a policy's income figure here: the
  definition (WFF-02 subpart MB, AS-07 chargeable income) is not implemented
  from spells, so such a household maps to `None`, which the engine reports
  as `needs_review` (backlog P2-HH-03).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from poltika.common.errors import PoltikaError
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
)
from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
)
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import ScenarioRecord
from poltika.semantics import household as hh
from poltika.semantics.household import Assertion, DatePeriod, Household
from poltika.semantics.population import PersonRole

# Household-level asserted fact ids (see the module docstring).
WFF_FACTS: tuple[str, ...] = (
    "household_eligibility",
    "extra_instalment_status",
    "in_work_eligibility",
    "ftc_iwtc_protected_or_direct_abatement",
    "mc6a_veterans_payment",
    "mc6b_disqualifying_payment",
    "minimum_family_full_time_earner_weeks",
    "best_start_no_shared_care",
    "best_start_protected_credit",
)
AS_FACTS: tuple[str, ...] = (
    "household_eligibility",
    "exempt_cash_asset_status",
    "ordinary_rate_status",
    "eldest_dependent_child_under_16",
)
LINK_FACT = "combined.as_claimant_is_wff_claimant_or_partner"


@dataclass(frozen=True)
class MappingRefusal:
    """The household cannot supply a field exactly. Never a zero, never a
    guess: the caller turns it into a component outcome (`refusal_result`)."""

    outcome: Literal["needs_review", "unsupported"]
    code: str
    reason: str
    missing_facts: tuple[str, ...] = ()


class AdapterRefused(PoltikaError):
    """An existing-format scenario cannot enter the household path exactly."""


def refusal_result(refusal: MappingRefusal) -> ComponentResult:
    """A refusal as the component result the engines would have returned for
    the same gap (`needs_review`/`unsupported`, a code and a reason)."""
    return ComponentResult(
        outcome=refusal.outcome,
        code=refusal.code,
        reason=refusal.reason,
        missing_facts=refusal.missing_facts,
        category="not_modelled" if refusal.outcome == "unsupported" else None,
    )


def _status(household: Household, key: str) -> FactStatus:
    return FactStatus(household.asserted_facts.get(key, Assertion.UNKNOWN).value)


def _period(week: AssessmentWeek) -> DatePeriod:
    return DatePeriod(start=week.start, end=week.end)


_WFF_BASES = frozenset(
    {hh.IncomeBasis.WFF_FAMILY_SCHEME, hh.IncomeBasis.WFF_NET_FAMILY_SCHEME_ME3_ATTESTED, hh.IncomeBasis.NET_OF_TAX}
)
_AS_BASES = frozenset({hh.IncomeBasis.AS_CHARGEABLE_WEEKLY})


def _q10_refusal(
    household: Household, person_ids: tuple[str, ...], period: DatePeriod, bases: frozenset[hh.IncomeBasis]
) -> MappingRefusal | None:
    """A spell that extends past the policy period would need an
    annualisation or apportionment, which no sourced rule allows (v0.2 D8/D9;
    PETE_QUEUE Q10). Refused, never scaled."""
    for spell in household.income_spells:
        if spell.person_id in person_ids and spell.basis in bases and hh.straddling_spells((spell,), period):
            return MappingRefusal(
                "needs_review",
                "HOUSEHOLD_SPELL_PERIOD_MISMATCH",
                f"an income spell [{spell.start}, {spell.end}) extends past the policy period "
                f"[{period.start}, {period.end}); converting it needs a sourced rule (PETE_QUEUE Q10, "
                "v0.2 D8/D9) and none exists",
            )
    return None


def _invalid(reason: str) -> MappingRefusal:
    return MappingRefusal("needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS", reason)


# ---------------------------------------------------------------- WFF


def to_wff(household: Household, tax_year: DatePeriod) -> WffScenario | MappingRefusal:
    """The household as WFF's input for `tax_year` (the reviewed WFF
    assessment period, passed explicitly: no default period)."""
    family = household.family
    children = tuple(household.person(child_id) for child_id in family.dependent_child_ids)

    # policy.yaml `children`; WFF-01 (dependent child, whole-year care),
    # WFF-06 (Best Start cohort, MC 6(c) payment). A child with no recorded
    # facts is unknown on every fact, never verified.
    child_facts = [
        ChildFacts(
            qualifies_whole_year=FactStatus(c.child_facts.qualifies_whole_year.value),
            best_start_cohort=BestStartCohort(c.child_facts.best_start_cohort.value),
            best_start_no_disqualifying_payment=FactStatus(c.child_facts.best_start_no_disqualifying_payment.value),
        )
        if c.child_facts is not None
        else ChildFacts(qualifies_whole_year=FactStatus.UNKNOWN)
        for c in children
    ]

    # WFF reads its `children` list as complete. A household whose child list
    # may be incomplete cannot supply it: a missing child is never a known count.
    if family.dependent_children_complete is not Assertion.VERIFIED:
        return MappingRefusal(
            "needs_review",
            "HOUSEHOLD_CHILD_LIST_INCOMPLETE",
            "the household's dependent-child list is not asserted complete, and WFF reads its children "
            "list as the complete list",
            ("dependent_children_complete",),
        )

    people = tuple(p for p in (family.claimant_id, family.partner_id) if p is not None)
    mismatch = _q10_refusal(household, people, tax_year, _WFF_BASES)
    if mismatch is not None:
        return mismatch

    # WFF-01/02 domain: a stable partner status. Unknown stays unknown.
    partner_status = PartnerStatus(family.partner_status.value)

    # WFF-02: family scheme income per person, as resolved by the caller
    # (basis WFF_FAMILY_SCHEME) for the whole tax year. A spell set that does
    # not cover the year is unverified (`None`), not zero.
    def fsi(person_id: str | None) -> Decimal | None:
        if person_id is None:
            return None
        return household.annual_amount(
            person_id, hh.IncomeType.UNSPLIT_TOTAL, tax_year, basis=hh.IncomeBasis.WFF_FAMILY_SCHEME
        )

    claimant_income = fsi(family.claimant_id)
    partner_income = fsi(family.partner_id)
    family_scheme_income: VerifiedIncome | None = None
    if claimant_income is None and partner_income is not None:
        return _invalid(
            "the partner's family scheme income is recorded without the claimant's; WFF-02 needs each "
            "person's amount, and a partner figure alone is not a verified family scheme income"
        )

    # WFF-05 (ME 3): net family scheme income is a family figure held on the
    # claimant. Attested only when its basis says so; the engine gates on it.
    def net(basis: hh.IncomeBasis) -> Decimal | None:
        return household.annual_amount(family.claimant_id, hh.IncomeType.UNSPLIT_TOTAL, tax_year, basis=basis)

    attested_net = net(hh.IncomeBasis.WFF_NET_FAMILY_SCHEME_ME3_ATTESTED)
    plain_net = net(hh.IncomeBasis.NET_OF_TAX)
    if attested_net is not None and plain_net is not None:
        return _invalid("both an ME 3 attested net family scheme income and a plain net figure are recorded")
    net_income = attested_net if attested_net is not None else plain_net

    try:
        if claimant_income is not None:
            family_scheme_income = VerifiedIncome(claimant_amount=claimant_income, partner_amount=partner_income)
        return WffScenario(
            household_eligibility=_status(household, "wff.household_eligibility"),
            extra_instalment_status=_status(household, "wff.extra_instalment_status"),
            children=child_facts,
            partner_status=partner_status,
            family_scheme_income=family_scheme_income,
            net_family_scheme_income=net_income,
            net_family_scheme_income_me3_attested=attested_net is not None,
            in_work_eligibility=_status(household, "wff.in_work_eligibility"),
            ftc_iwtc_protected_or_direct_abatement=_status(household, "wff.ftc_iwtc_protected_or_direct_abatement"),
            mc6a_veterans_payment=_status(household, "wff.mc6a_veterans_payment"),
            mc6b_disqualifying_payment=_status(household, "wff.mc6b_disqualifying_payment"),
            minimum_family_full_time_earner_weeks=_status(household, "wff.minimum_family_full_time_earner_weeks"),
            best_start_no_shared_care=_status(household, "wff.best_start_no_shared_care"),
            best_start_protected_credit=_status(household, "wff.best_start_protected_credit"),
        )
    except ValueError as exc:
        # A negative income or a partner amount on a single claimant is
        # malformed input, not a policy outcome (the engine type says so).
        return _invalid(str(exc))


# ---------------------------------------------------------------- AS

_CATEGORY_BY_BENEFIT = {
    hh.BenefitKind.JOBSEEKER_SUPPORT: ClaimantCategory.JOBSEEKER_SUPPORT,
    hh.BenefitKind.SOLE_PARENT_SUPPORT: ClaimantCategory.SOLE_PARENT_SUPPORT,
    hh.BenefitKind.SUPPORTED_LIVING_PAYMENT: ClaimantCategory.SUPPORTED_LIVING_PAYMENT,
    hh.BenefitKind.NZ_SUPER_OR_VETERANS_PENSION: ClaimantCategory.PENSION_OR_VETERANS,
    hh.BenefitKind.MIXED_BENEFIT_COUPLE: ClaimantCategory.MIXED_BENEFIT_COUPLE,
    hh.BenefitKind.NO_BENEFIT: ClaimantCategory.NON_BENEFICIARY,
}
_BENEFIT_BY_CATEGORY = {v: k for k, v in _CATEGORY_BY_BENEFIT.items()}
_PARTNER_TYPE_BY_ARRANGEMENT = {
    hh.PartnerArrangement.ORDINARY_COUPLE: PartnerType.ORDINARY_COUPLE,
    hh.PartnerArrangement.JOINT_TENANCY: PartnerType.JOINT_TENANCY,
    hh.PartnerArrangement.COMMUNITY_SPOUSE_OR_PARTNER: PartnerType.COMMUNITY_SPOUSE_OR_PARTNER,
}
_ARRANGEMENT_BY_PARTNER_TYPE = {v: k for k, v in _PARTNER_TYPE_BY_ARRANGEMENT.items()}


def to_as(household: Household, assessment_week: AssessmentWeek) -> AsScenario | MappingRefusal:
    """The household as the Accommodation Supplement's input for
    `assessment_week` (AS is assessed per week: AS-01..AS-11)."""
    family = household.family
    week = _period(assessment_week)
    housing = household.housing

    # AS-08 (claimant on a main benefit has no separate income test) and the
    # claimant categories of `ClaimantCategory`: the claimant's benefit
    # receipt over the whole assessment week. One spell must cover the whole
    # week; a week not wholly covered is not a verified category (`None`).
    # Two different benefits covering the week is a contradiction, not a pick.
    categories = {
        s.benefit
        for s in household.benefit_spells
        if s.person_id == family.claimant_id and s.start <= week.start and s.end >= week.end
    }
    if len(categories) > 1:
        return _invalid("the claimant has different benefits recorded for the whole assessment week")
    claimant_category = _CATEGORY_BY_BENEFIT[next(iter(categories))] if categories else None

    # Schedule 4 Part 7 cl 1-3 household categories, AS-09 couple types: a
    # single family is SINGLE; a partnered family takes the recorded
    # arrangement (ordinary, joint tenancy, community partner); no
    # arrangement recorded or an unknown partner status is unverified.
    partner_type: PartnerType | None
    if family.partner_status is hh.FamilyPartnerStatus.SINGLE:
        partner_type = PartnerType.SINGLE
    elif family.partner_status is hh.FamilyPartnerStatus.PARTNERED and housing.partner_arrangement is not None:
        partner_type = _PARTNER_TYPE_BY_ARRANGEMENT[housing.partner_arrangement]
    else:
        partner_type = None

    # The AS dependent-child count (AS-03/Schedule 4 Part 7 cl 7 costs formula input),
    # held separately from WFF's child list because the definitions are separate facts.
    # The count is verified only when the child list is complete and every
    # listed child is verified or excluded under the AS definition.
    dependent_children_count: int | None = None
    if family.dependent_children_complete is Assertion.VERIFIED:
        statuses = []
        for child_id in family.dependent_child_ids:
            facts = household.person(child_id).child_facts
            statuses.append(Assertion.UNKNOWN if facts is None else facts.as_dependent_child)
        if Assertion.UNKNOWN not in statuses:
            dependent_children_count = statuses.count(Assertion.VERIFIED)

    mismatch = _q10_refusal(household, (family.claimant_id,), week, _AS_BASES)
    if mismatch is not None:
        return mismatch

    # AS-07 (r 18): combined weekly income of claimant and partner, a family
    # figure held on the claimant with basis AS_CHARGEABLE_WEEKLY.
    weekly_income = household.weekly_amount(
        family.claimant_id, hh.IncomeType.UNSPLIT_TOTAL, week, basis=hh.IncomeBasis.AS_CHARGEABLE_WEEKLY
    )

    try:
        return AsScenario(
            household_eligibility=_status(household, "as.household_eligibility"),
            claimant_category=claimant_category,
            tenure_type=None if housing.tenure is None else TenureType(housing.tenure.value),
            partner_status=partner_type,
            statistical_area_unit=None if housing.area is None else Area(housing.area.value),
            weekly_accommodation_costs=housing.weekly_housing_costs,
            dependent_children_count=dependent_children_count,
            cash_assets=housing.cash_assets,
            exempt_cash_asset_status=_status(household, "as.exempt_cash_asset_status"),
            weekly_income=weekly_income,
            ordinary_rate_status=_status(household, "as.ordinary_rate_status"),
            eldest_dependent_child_under_16=_status(household, "as.eldest_dependent_child_under_16"),
        )
    except ValueError as exc:
        return _invalid(str(exc))


def to_combined(
    household: Household, tax_year: DatePeriod, assessment_week: AssessmentWeek
) -> CombinedHouseholdScenario | MappingRefusal:
    """The pair the combined runner takes. The claimant link is the
    household's asserted fact: Task 1.4 retires the pairwise checks, this
    task keeps them (backlog P2-HH-02)."""
    wff = to_wff(household, tax_year)
    if isinstance(wff, MappingRefusal):
        return wff
    as_ = to_as(household, assessment_week)
    if isinstance(as_, MappingRefusal):
        return as_
    return CombinedHouseholdScenario(
        wff=wff,
        accommodation_supplement=as_,
        as_claimant_is_wff_claimant_or_partner=_status(household, LINK_FACT),
    )


# ---------------------------------------------------------------- adapters


def household_from_combined(
    combined: CombinedHouseholdScenario, *, household_id: str, tax_year: DatePeriod, assessment_week: AssessmentWeek
) -> Household:
    """An existing-format scenario pair as a household. Raises
    `AdapterRefused` where the pair asserts one fact two different ways, so
    one household cannot reproduce both halves exactly."""
    return _household_from(
        combined.wff,
        combined.accommodation_supplement,
        combined.as_claimant_is_wff_claimant_or_partner,
        household_id,
        tax_year,
        assessment_week,
    )


def household_from_record(record: ScenarioRecord, *, household_id: str, tax_year: DatePeriod) -> Household:
    """A stored scenario record as a household. The record carries the AS
    week but not the WFF tax year (the policy file defines it), so the caller
    passes it."""
    return household_from_combined(
        record.household, household_id=household_id, tax_year=tax_year, assessment_week=record.assessment_week
    )


def household_from_wff(wff: WffScenario, *, household_id: str, tax_year: DatePeriod) -> Household:
    """A WFF-only scenario as a household. AS facts stay unknown."""
    return _household_from(wff, None, FactStatus.UNKNOWN, household_id, tax_year, None)


def household_from_as(as_: AsScenario, *, household_id: str, assessment_week: AssessmentWeek) -> Household:
    """An AS-only scenario as a household. WFF facts stay unknown."""
    return _household_from(None, as_, FactStatus.UNKNOWN, household_id, None, assessment_week)


def _merge_partner(
    wff: WffScenario | None, as_: AsScenario | None
) -> tuple[hh.FamilyPartnerStatus, hh.PartnerArrangement | None]:
    """One partner status from the two halves. AS's partner types are
    tenancy kinds, so the arrangement is a housing fact."""
    wff_status = None if wff is None else wff.partner_status
    as_type = None if as_ is None else as_.partner_status

    def from_as(value: PartnerType | None) -> tuple[hh.FamilyPartnerStatus, hh.PartnerArrangement | None]:
        if value is None:
            return hh.FamilyPartnerStatus.UNKNOWN, None
        if value is PartnerType.SINGLE:
            return hh.FamilyPartnerStatus.SINGLE, None
        return hh.FamilyPartnerStatus.PARTNERED, _ARRANGEMENT_BY_PARTNER_TYPE[value]

    if wff is None:
        return from_as(as_type)
    if as_ is None:
        return hh.FamilyPartnerStatus(wff_status.value if wff_status else "unknown"), None
    assert wff_status is not None
    if wff_status is PartnerStatus.PARTNERED and as_type is None:
        return hh.FamilyPartnerStatus.PARTNERED, None
    if wff_status is PartnerStatus.UNKNOWN and as_type is None:
        return hh.FamilyPartnerStatus.UNKNOWN, None
    from_as_status, arrangement = from_as(as_type)
    if from_as_status.value == wff_status.value and as_type is not None:
        return from_as_status, arrangement
    raise AdapterRefused(
        f"partner status: WFF says {wff_status.value}, AS says {None if as_type is None else as_type.value}; "
        "one household holds one partner fact with one verification state"
    )


def _household_from(
    wff: WffScenario | None,
    as_: AsScenario | None,
    link: FactStatus,
    household_id: str,
    tax_year: DatePeriod | None,
    assessment_week: AssessmentWeek | None,
) -> Household:
    status, arrangement = _merge_partner(wff, as_)

    persons: list[hh.Person] = [hh.Person(person_id="claimant", role=PersonRole.CLAIMANT)]
    if status is hh.FamilyPartnerStatus.PARTNERED:
        persons.append(hh.Person(person_id="partner", role=PersonRole.PARTNER))

    # Dependent children: the WFF list and the AS count are about the same
    # children under two definitions. N AS children among M WFF children
    # (N <= M) is representable (M - N are excluded under the AS definition);
    # N > M is not: the household would need children WFF has no facts for.
    wff_children = None if wff is None else wff.children
    as_count = None if as_ is None else as_.dependent_children_count
    complete = Assertion.UNKNOWN
    if wff_children is not None:
        count = len(wff_children)
        if as_count is not None and as_count > count:
            raise AdapterRefused(f"dependent children: WFF lists {count}, AS asserts {as_count} (more than WFF lists)")
        # The WFF request's `children` is the caller's complete list: the engine
        # reads an empty list as no dependent child (WFF_NO_DEPENDENT_CHILD).
        complete = Assertion.VERIFIED
    elif as_count is not None:
        count = as_count
        complete = Assertion.VERIFIED
    else:
        count = 0
    child_ids: list[str] = []
    for index in range(count):
        child_id = f"child_{index + 1}"
        child_ids.append(child_id)
        wff_child = None if wff_children is None else wff_children[index]
        if as_count is None:
            as_status = Assertion.UNKNOWN
        else:
            as_status = Assertion.VERIFIED if index < as_count else Assertion.EXCLUDED
        persons.append(
            hh.Person(
                person_id=child_id,
                role=PersonRole.DEPENDENT_CHILD,
                child_facts=hh.ChildFacts(
                    qualifies_whole_year=(
                        Assertion.UNKNOWN if wff_child is None else Assertion(wff_child.qualifies_whole_year.value)
                    ),
                    best_start_cohort=(
                        hh.BestStartCohort.UNKNOWN
                        if wff_child is None
                        else hh.BestStartCohort(wff_child.best_start_cohort.value)
                    ),
                    best_start_no_disqualifying_payment=(
                        Assertion.UNKNOWN
                        if wff_child is None
                        else Assertion(wff_child.best_start_no_disqualifying_payment.value)
                    ),
                    as_dependent_child=as_status,
                ),
            )
        )

    spells: list[hh.IncomeSpell] = []
    asserted: dict[str, Assertion] = {}
    if wff is not None:
        assert tax_year is not None
        for name in WFF_FACTS:
            asserted[f"wff.{name}"] = Assertion(getattr(wff, name).value)
        income = wff.family_scheme_income
        if income is not None:
            spells.append(_spell("claimant", tax_year, income.claimant_amount, hh.IncomeBasis.WFF_FAMILY_SCHEME))
            if income.partner_amount is not None:
                if status is not hh.FamilyPartnerStatus.PARTNERED:
                    raise AdapterRefused("a partner income is supplied but the partner status is not partnered")
                spells.append(_spell("partner", tax_year, income.partner_amount, hh.IncomeBasis.WFF_FAMILY_SCHEME))
        if wff.net_family_scheme_income is not None:
            basis = (
                hh.IncomeBasis.WFF_NET_FAMILY_SCHEME_ME3_ATTESTED
                if wff.net_family_scheme_income_me3_attested
                else hh.IncomeBasis.NET_OF_TAX
            )
            spells.append(_spell("claimant", tax_year, wff.net_family_scheme_income, basis))
        elif wff.net_family_scheme_income_me3_attested:
            raise AdapterRefused("the ME 3 attestation is set without a net family scheme income to attest")

    benefit_spells: list[hh.BenefitSpell] = []
    housing = hh.Housing(partner_arrangement=arrangement)
    if as_ is not None:
        assert assessment_week is not None
        for name in AS_FACTS:
            asserted[f"as.{name}"] = Assertion(getattr(as_, name).value)
        if as_.weekly_income is not None:
            spells.append(
                _spell(
                    "claimant", _period(assessment_week), as_.weekly_income, hh.IncomeBasis.AS_CHARGEABLE_WEEKLY
                )
            )
        if as_.claimant_category is not None:
            benefit_spells.append(
                hh.BenefitSpell(
                    person_id="claimant",
                    benefit=_BENEFIT_BY_CATEGORY[as_.claimant_category],
                    start=assessment_week.start,
                    end=assessment_week.end,
                )
            )
        housing = hh.Housing(
            tenure=None if as_.tenure_type is None else hh.Tenure(as_.tenure_type.value),
            weekly_housing_costs=as_.weekly_accommodation_costs,
            partner_arrangement=arrangement,
            area=None if as_.statistical_area_unit is None else hh.AsArea(as_.statistical_area_unit.value),
            cash_assets=as_.cash_assets,
        )
    if wff is not None and as_ is not None:
        asserted[LINK_FACT] = Assertion(link.value)

    return Household(
        household_id=household_id,
        persons=tuple(persons),
        families=(
            hh.Family(
                claimant_id="claimant",
                partner_status=status,
                partner_id="partner" if status is hh.FamilyPartnerStatus.PARTNERED else None,
                dependent_child_ids=tuple(child_ids),
                dependent_children_complete=complete,
            ),
        ),
        housing=housing,
        income_spells=tuple(spells),
        benefit_spells=tuple(benefit_spells),
        asserted_facts=asserted,
    )


def _spell(person_id: str, period: DatePeriod | AssessmentWeek, amount: Decimal, basis: hh.IncomeBasis) -> hh.IncomeSpell:
    start: date = period.start
    end: date = period.end
    return hh.IncomeSpell(
        person_id=person_id,
        income_type=hh.IncomeType.UNSPLIT_TOTAL,
        start=start,
        end=end,
        amount=amount,
        basis=basis,
    )


__all__ = [
    "AS_FACTS",
    "LINK_FACT",
    "WFF_FACTS",
    "AdapterRefused",
    "MappingRefusal",
    "household_from_as",
    "household_from_combined",
    "household_from_record",
    "household_from_wff",
    "refusal_result",
    "to_as",
    "to_combined",
    "to_wff",
]
