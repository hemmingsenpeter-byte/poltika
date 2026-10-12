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
- `run_household()` (Task 1.4) runs both policies for a `Household` input.
  It keeps only the pair checks a household can still fail, restated on its
  facts (`HOUSEHOLD_CHECKS`); the ones it makes impossible are retired for
  it (`RETIRED_FOR_HOUSEHOLD`, D36 (4)). The pair format is unchanged and
  keeps every check.

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
from pathlib import Path
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
from poltika.policy.loader import PolicyParameterSet, load_policy_spec
from poltika.scenarios.combined import (
    CombinedHouseholdScenario,
    CombinedResult,
    run_combined_household,
)
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
# Q19 (7), D36: whether the claimant's relationship stayed the same for the
# whole WFF year. A gate, like the engine facts: EXCLUDED (it changed) is
# outside WFF's whole-year domain, so `unsupported`; UNKNOWN changes nothing
# (the engine's `household_eligibility` bundle still gates it).
RELATIONSHIP_FACT = "wff.relationship_unchanged_in_year"


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


def _relationship_refusal(household: Household) -> MappingRefusal | None:
    if _status(household, RELATIONSHIP_FACT) is not FactStatus.EXCLUDED:
        return None
    return MappingRefusal(
        "unsupported",
        "HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR",
        "the claimant's relationship changed during the WFF year; WFF covers a whole year with one "
        "relationship period only (Q19 (7), D36)",
    )


def _invalid(reason: str) -> MappingRefusal:
    return MappingRefusal("needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS", reason)


# The main benefits `scenarios/combined.py` checks against WFF's whole-year
# no-benefit assertions. NZ Super/Veterans' Pension and the AS mixed-benefit
# couple label are not, by themselves, a main-benefit spell for WFF (Q19 (5)).
_WFF_MAIN_BENEFITS = frozenset(
    {hh.BenefitKind.JOBSEEKER_SUPPORT, hh.BenefitKind.SOLE_PARENT_SUPPORT, hh.BenefitKind.SUPPORTED_LIVING_PAYMENT}
)
# WFF assertions that say no main benefit was received in the year (combined.py:
# in-work eligibility, MC 6(b)). The protected-credit assertions stay with
# combined.py's conservative pair check: a benefit week alone does not
# establish a protected month (MD 14, MG 4).
_WFF_NO_MAIN_BENEFIT_FACTS = ("wff.in_work_eligibility", "wff.mc6b_disqualifying_payment")


def _main_benefit_in_year(
    household: Household, person_ids: tuple[str, ...], tax_year: DatePeriod, pair_week: AssessmentWeek | None
) -> MappingRefusal | None:
    """Q19 (5), decided 13 October 2026 (D38): a main-benefit spell of the
    claimant or partner inside the tax year contradicts a verified whole-year
    assertion that no main benefit was received. The check compares dates
    only: nothing is apportioned (Q10, D32), and no part-year entitlement is
    derived. Without such an assertion the spell changes nothing here.

    For a combined pair (`pair_week`), the claimant's spell covering the AS
    week becomes the AS claimant category, and `scenarios/combined.py` flags
    that same contradiction on every component; it is left to that check so
    the pair's result is unchanged. Any other spell is still refused."""
    asserted = [key for key in _WFF_NO_MAIN_BENEFIT_FACTS if _status(household, key) is FactStatus.VERIFIED]
    if not asserted:
        return None
    claimant_id = household.family.claimant_id
    for spell in household.benefit_spells:
        if (
            pair_week is not None
            and spell.person_id == claimant_id
            and spell.benefit in _WFF_MAIN_BENEFITS
            and spell.start <= pair_week.start
            and spell.end >= pair_week.end
        ):
            continue
        if (
            spell.person_id in person_ids
            and spell.benefit in _WFF_MAIN_BENEFITS
            and spell.start < tax_year.end
            and spell.end > tax_year.start
        ):
            return _invalid(
                f"'{spell.person_id}' has {spell.benefit.value} recorded for [{spell.start}, {spell.end}) inside "
                f"the WFF year [{tax_year.start}, {tax_year.end}), but {', '.join(asserted)} asserts no main "
                "benefit in the year"
            )
    return None


# ---------------------------------------------------------------- WFF


def to_wff(household: Household, tax_year: DatePeriod) -> WffScenario | MappingRefusal:
    """The household as WFF's input for `tax_year` (the reviewed WFF
    assessment period, passed explicitly: no default period)."""
    return _to_wff(household, tax_year, None)


def _to_wff(
    household: Household, tax_year: DatePeriod, pair_week: AssessmentWeek | None
) -> WffScenario | MappingRefusal:
    family = household.family
    # First: unsupported outranks every needs_review gate below.
    changed = _relationship_refusal(household)
    if changed is not None:
        return changed
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
    if family.wff_children_complete is not Assertion.VERIFIED:
        return MappingRefusal(
            "needs_review",
            "HOUSEHOLD_CHILD_LIST_INCOMPLETE",
            "the household's dependent-child list is not asserted complete under the WFF definition, "
            "and WFF reads its children list as the complete list",
            ("wff_children_complete",),
        )

    people = tuple(p for p in (family.claimant_id, family.partner_id) if p is not None)
    mismatch = _q10_refusal(household, people, tax_year, _WFF_BASES)
    if mismatch is not None:
        return mismatch
    contradiction = _main_benefit_in_year(household, people, tax_year, pair_week)
    if contradiction is not None:
        return contradiction

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
    # Every spell touching the week is checked, not only covering ones: a
    # covering spell beside any other receipt in the week (r 17 "being paid")
    # is a contradiction, not a pick (MAP-01). Household validation already
    # refuses overlapping benefit spells; this keeps the mapping safe alone.
    in_week = [
        s
        for s in household.benefit_spells
        if s.person_id == family.claimant_id and s.start < week.end and s.end > week.start
    ]
    covering = [s for s in in_week if s.start <= week.start and s.end >= week.end]
    if covering and len(in_week) > 1:
        return _invalid("the claimant has more than one benefit status recorded in the assessment week")
    claimant_category = _CATEGORY_BY_BENEFIT[covering[0].benefit] if covering else None

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
    if family.as_children_complete is Assertion.VERIFIED:
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
            # Q19 (1), D38: the balance the caller asserts for this assessment
            # week; Poltika picks no snapshot date and averages nothing.
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
    """The pair the combined runner takes, with the pair format's checks.
    The claimant link is the household's asserted fact. A household input
    runs through `run_household()` instead (Task 1.4)."""
    wff = _to_wff(household, tax_year, assessment_week)
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


# ---------------------------------------------------------------- household runs (Task 1.4)

# ADR-0017 section 4: the pair checks (`combined.SHARED_FACT_CHECKS`) a household
# can still fail, restated on its facts. In-work eligibility and MC 6(b) are
# refused by `to_wff` against any main-benefit spell in the year (Q19 (5));
# the others flag every component as the pair checks do.
HOUSEHOLD_CHECKS: tuple[str, ...] = (
    "AS assessment week inside the WFF year",
    "main benefit vs WFF in-work eligibility",
    "main benefit vs WFF MC 6(b)",
    "main benefit vs WFF MD 14/15 protected family tax credit",
    "main benefit vs WFF MG 4 protected Best Start",
)
# The pair checks a household makes impossible, and why (D36 (4)). Each
# has a test showing its contradiction can no longer be constructed.
RETIRED_FOR_HOUSEHOLD: dict[str, str] = {
    "precondition: AS claimant is the WFF claimant or their partner": (
        "both mappings read the one family's claimant"
    ),
    "partner status": (
        "both mappings read the one family's partner status, and a mixed-benefit couple spell needs a "
        "family that is not single"
    ),
    "dependent children count": (
        "both mappings read the one child list; each child's AS status is its own fact, so a different "
        "count is a definitional difference, reported in `HouseholdResult.definitional_differences`"
    ),
}
# WFF assertions that no protected month applies, flagged against any
# main-benefit spell in the year: a benefit spell alone does not establish
# or rule out a protected month (MD 14, MG 4), so the flag stays conservative.
_WFF_NO_PROTECTED_MONTH_FACTS = (
    ("wff.ftc_iwtc_protected_or_direct_abatement", "no MD 14/15 protected family tax credit month"),
    ("wff.best_start_protected_credit", "no MG 4 protected Best Start month"),
)


@dataclass(frozen=True)
class HouseholdResult:
    """A household run: both policies' results, as for the pair format,
    plus where two policies' definitions of one concept give different
    figures. A definitional difference is reported, never a disagreement."""

    combined: CombinedResult
    definitional_differences: tuple[str, ...] = ()


def _household_contradictions(
    household: Household, wff_period: tuple[date, date], week: AssessmentWeek
) -> tuple[str, ...]:
    """The kept checks of `HOUSEHOLD_CHECKS` that flag components."""
    found: list[str] = []
    if week.start < wff_period[0] or week.end > wff_period[1]:
        found.append(
            f"AS assessment week [{week.start}, {week.end}) is not inside the WFF "
            f"year [{wff_period[0]}, {wff_period[1]})"
        )
    family = household.family
    people = (family.claimant_id, family.partner_id)
    in_year = [
        s
        for s in household.benefit_spells
        if s.person_id in people
        and s.benefit in _WFF_MAIN_BENEFITS
        and s.start < wff_period[1]
        and s.end > wff_period[0]
    ]
    for key, label in _WFF_NO_PROTECTED_MONTH_FACTS:
        if in_year and _status(household, key) is FactStatus.VERIFIED:
            spell = in_year[0]
            found.append(
                f"main benefit: '{spell.person_id}' has {spell.benefit.value} recorded for "
                f"[{spell.start}, {spell.end}) inside the WFF year, WFF asserts {label} verified"
            )
    return tuple(found)


def run_household(
    household: Household,
    *,
    tax_year: DatePeriod,
    assessment_week: AssessmentWeek,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    wff_lookup_date: date,
    as_lookup_date: date,
    requested_wff_policy_version: str,
    requested_as_policy_version: str,
    wff_parameters: PolicyParameterSet | None = None,
    as_parameters: PolicyParameterSet | None = None,
) -> HouseholdResult | MappingRefusal:
    """Both policies for a household input (ADR-0017 Task 1.4, D36 (4)).
    `tax_year` must be the WFF policy's assessed year. A refusal is
    returned, never a partial run."""
    reference = load_policy_spec(wff_policy_dir / "policy.yaml").reference_period
    if (tax_year.start, tax_year.end) != (reference.from_, reference.to):
        raise ValueError(
            f"tax_year [{tax_year.start}, {tax_year.end}) is not the WFF policy's assessed year "
            f"[{reference.from_}, {reference.to})"
        )
    # unsupported outranks the link's needs_review below.
    changed = _relationship_refusal(household)
    if changed is not None:
        return changed
    # A household needs no claimant link: its one family supplies it. A link
    # fact the household does carry (an adapter copies it from a pair) is
    # honoured: anything but verified is not this household's fact to drop.
    link = household.asserted_facts.get(LINK_FACT)
    if link is Assertion.EXCLUDED:
        return MappingRefusal(
            "unsupported",
            "HOUSEHOLD_PAIR_LINK_EXCLUDED",
            "the household carries the pair format's claimant link as excluded: the AS claimant is not "
            "the WFF claimant or their partner, which one family cannot hold",
        )
    if link is Assertion.UNKNOWN:
        return MappingRefusal(
            "needs_review",
            "HOUSEHOLD_PAIR_LINK_UNVERIFIED",
            "the household carries the pair format's claimant link as unknown",
            (LINK_FACT,),
        )
    wff = _to_wff(household, tax_year, None)
    if isinstance(wff, MappingRefusal):
        return wff
    as_ = to_as(household, assessment_week)
    if isinstance(as_, MappingRefusal):
        return as_

    def checks(
        _scenario: CombinedHouseholdScenario, wff_period: tuple[date, date], week: AssessmentWeek
    ) -> tuple[str, ...]:
        return _household_contradictions(household, wff_period, week)

    combined = run_combined_household(
        wff_policy_dir,
        as_policy_dir,
        CombinedHouseholdScenario(
            wff=wff, accommodation_supplement=as_, as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED
        ),
        wff_lookup_date=wff_lookup_date,
        as_lookup_date=as_lookup_date,
        assessment_week=assessment_week,
        requested_wff_policy_version=requested_wff_policy_version,
        requested_as_policy_version=requested_as_policy_version,
        wff_parameters=wff_parameters,
        as_parameters=as_parameters,
        checks=checks,
    )
    differences: tuple[str, ...] = ()
    if as_.dependent_children_count is not None and as_.dependent_children_count != len(wff.children):
        differences = (
            (
                f"dependent children: {len(wff.children)} under the WFF definition, "
                f"{as_.dependent_children_count} under the AS definition (each child's status is recorded "
                "under each definition)"
            ),
        )
    return HouseholdResult(combined=combined, definitional_differences=differences)


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
    if (
        status is hh.FamilyPartnerStatus.SINGLE
        and as_ is not None
        and as_.claimant_category is ClaimantCategory.MIXED_BENEFIT_COUPLE
    ):
        raise AdapterRefused(
            "partner status: the family is single but AS asserts a mixed-benefit couple; one household holds "
            "one partner fact"
        )

    persons: list[hh.Person] = [hh.Person(person_id="claimant", role=PersonRole.CLAIMANT)]
    if status is hh.FamilyPartnerStatus.PARTNERED:
        persons.append(hh.Person(person_id="partner", role=PersonRole.PARTNER))

    # Dependent children: the WFF list and the AS count are about the same
    # children under two definitions. N AS children among M WFF children
    # (N <= M) is representable (M - N are excluded under the AS definition);
    # N > M is not: the household would need children WFF has no facts for.
    # Q19 (2), D38: marking the first N synthetic children as the AS ones is
    # an engineering device for an unchanged aggregate round trip, not child
    # membership. The counts carry no identities, so which real children are
    # AS children is unknown; nothing may read these ids as that fact.
    wff_children = None if wff is None else wff.children
    as_count = None if as_ is None else as_.dependent_children_count
    # The WFF request's `children` is the caller's complete WFF list (the engine
    # reads an empty list as no dependent child, WFF_NO_DEPENDENT_CHILD); an AS
    # count is complete only under the AS definition.
    wff_complete = Assertion.VERIFIED if wff_children is not None else Assertion.UNKNOWN
    as_complete = Assertion.VERIFIED if as_count is not None else Assertion.UNKNOWN
    if wff_children is not None:
        count = len(wff_children)
        if as_count is not None and as_count > count:
            raise AdapterRefused(f"dependent children: WFF lists {count}, AS asserts {as_count} (more than WFF lists)")
    elif as_count is not None:
        count = as_count
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
                wff_children_complete=wff_complete,
                as_children_complete=as_complete,
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
    "HOUSEHOLD_CHECKS",
    "LINK_FACT",
    "RELATIONSHIP_FACT",
    "RETIRED_FOR_HOUSEHOLD",
    "WFF_FACTS",
    "AdapterRefused",
    "HouseholdResult",
    "MappingRefusal",
    "household_from_as",
    "household_from_combined",
    "household_from_record",
    "household_from_wff",
    "refusal_result",
    "run_household",
    "to_as",
    "to_combined",
    "to_wff",
]
