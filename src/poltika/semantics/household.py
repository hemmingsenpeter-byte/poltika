"""Pass 1 (ADR-0017, BUILD_PLAN_v0_3.md Phase 1 Task 1.1): the canonical household.

A `Household` holds each fact once, with its own verification status and,
where time matters, its period. Each policy's input type (`WffScenario`,
`AsScenario` and the ones income tax and the main benefits add) is derived
from it by a named mapping in `scenarios/household_mappings.py`. The engines
do not change.

What it holds:

- people (`Person`): a stable id, a role, the per-child facts WFF asks for, and a generic map of asserted
  facts (fact id -> verified/excluded/unknown) for facts a policy needs that
  have no typed field here;
- one family (`Family`): the claimant, the partner (or none, or unknown),
  the dependent children. A household with more than one family is refused
  with a reason, not guessed (ADR-0017 D6 answer 2);
- housing (`Housing`): tenure, weekly costs, the AS area, cash assets;
- dated spells (ADR-0017 D6 answer 1): `IncomeSpell` for income by type and
  `BenefitSpell` for main-benefit receipt. Each policy's period view is
  derived in its own mapping; `Household.annual_amount` and
  `Household.weekly_amount` give the plain arithmetic view of a spell set;
- household-level asserted facts, keyed like the per-person ones.

An `Assertion` is `verified`, `excluded` or `unknown`, with the same
meaning as `FactStatus` in the engines (`engines/simulator/outcome.py`).
`semantics/` cannot import `engines/`, so the enum is repeated here and the
mappings convert by value. Unknown stays unknown through every mapping: a
missing fact is never zero.

Spell semantics (documented once, here):

- A spell's `amount` is the total over `[start, end)`, `end` exclusive.
- A period view is `None` unless the spells of one (person, income type,
  basis) cover the whole period. A gap is an unknown, never a zero. A
  verified zero is a spell with amount 0.
- No scaling, ever. A period view adds only spells that lie wholly inside
  the period and tile it with no gap. A spell that extends past the period
  edge is not apportioned: that would convert an amount between periods
  without a sourced rule (v0.2 D8/D9, PETE_QUEUE Q10, `periods.convert_amount`
  refuses). The view is then `None` (unknown) and `straddling_spells` names
  the offenders so a mapping can refuse with the reason.
- `basis` says what the figure is. Figures a policy defines in its own
  terms (WFF family scheme income, AS weekly income) cannot be derived from
  earnings by type without that policy's definition, so they enter as
  figures the caller already resolved, with their own basis. Spells of the
  same person, income type and basis may not overlap; spells of different
  bases may.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from decimal import Decimal
from enum import Enum
from itertools import pairwise
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from poltika.common.errors import PoltikaError
from poltika.semantics.population import PersonRole

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_FACT_ID = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


class UnsupportedHousehold(PoltikaError):
    """The household is outside what Pass 1 models. Carries the reason."""


class Assertion(str, Enum):
    """verified / excluded / unknown, the same values as the engines'
    `FactStatus`. The meaning of `verified` and `excluded` is the engine
    fact's own (a gate: holds / verified not to hold; an exclusion trigger:
    verified not to apply / verified to apply)."""

    VERIFIED = "verified"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


class BestStartCohort(str, Enum):
    """Same members and values as WFF's `BestStartCohort`."""

    IN_SUPPORTED_COHORT = "in_supported_cohort"
    OUTSIDE_BEST_START_ENTITLEMENT = "outside_best_start_entitlement"
    OTHER_COHORT_UNSUPPORTED = "other_cohort_unsupported"
    UNKNOWN = "unknown"


class FamilyPartnerStatus(str, Enum):
    SINGLE = "single"
    PARTNERED = "partnered"
    UNKNOWN = "unknown"


class PartnerArrangement(str, Enum):
    """The kind of couple, where it matters to a housing benefit (Accommodation
    Supplement: ordinary couple, joint tenancy, community spouse or partner).
    Recorded as a housing fact, because it is about the tenancy."""

    ORDINARY_COUPLE = "ordinary_couple"
    JOINT_TENANCY = "joint_tenancy"
    COMMUNITY_SPOUSE_OR_PARTNER = "community_spouse_or_partner"


class Tenure(str, Enum):
    RENT_CONTRIBUTIONS_OR_BOARD = "rent_contributions_or_board"
    HOMEOWNER = "homeowner"


class AsArea(str, Enum):
    """A verified Statistical Area Unit resolved to Accommodation Supplement
    Area 1-4. Never inferred, never defaulted."""

    AREA_1 = "area1"
    AREA_2 = "area2"
    AREA_3 = "area3"
    AREA_4 = "area4"


class IncomeType(str, Enum):
    EMPLOYMENT_EARNINGS = "employment_earnings"
    SELF_EMPLOYMENT_INCOME = "self_employment_income"
    MAIN_BENEFIT_INCOME = "main_benefit_income"
    OTHER_TAXABLE_INCOME = "other_taxable_income"
    NON_TAXABLE_INCOME = "non_taxable_income"
    # Adapters only: a total the caller already resolved under a policy's own
    # definition (see `IncomeBasis`), with no split by type known.
    UNSPLIT_TOTAL = "unsplit_total"


class IncomeBasis(str, Enum):
    GROSS = "gross"  # before tax, as received
    NET_OF_TAX = "net_of_tax"  # after tax
    # Figures resolved under a policy's own definition by the caller (the
    # existing request formats supply them this way). Which person holds them
    # is stated in `scenarios/household_mappings.py`.
    WFF_FAMILY_SCHEME = "wff_family_scheme"  # WFF-02: per person, subpart MB adjustments applied
    WFF_NET_FAMILY_SCHEME_ME3_ATTESTED = "wff_net_family_scheme_me3_attested"  # WFF-05: family figure, ME 3
    AS_CHARGEABLE_WEEKLY = "as_chargeable_weekly"  # AS-07: family figure, weekly


class BenefitKind(str, Enum):
    JOBSEEKER_SUPPORT = "jobseeker_support"
    SOLE_PARENT_SUPPORT = "sole_parent_support"
    SUPPORTED_LIVING_PAYMENT = "supported_living_payment"
    NZ_SUPER_OR_VETERANS_PENSION = "nz_super_or_veterans_pension"
    # Adapter label: AS records a mixed-benefit couple as a claimant
    # category; held on the claimant until the benefit specifications say how
    # a couple's benefits are split.
    MIXED_BENEFIT_COUPLE = "mixed_benefit_couple"
    # Verified that no benefit is received in the spell.
    NO_BENEFIT = "no_benefit"


class DatePeriod(BaseModel):
    """`[start, end)`, `end` exclusive."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    start: date
    end: date

    @model_validator(mode="after")
    def _ordered(self) -> DatePeriod:
        if self.end <= self.start:
            raise ValueError(f"a period must end after it starts, got [{self.start}, {self.end})")
        return self

    @property
    def days(self) -> int:
        return (self.end - self.start).days


def _check_fact_ids(facts: dict[str, Assertion]) -> dict[str, Assertion]:
    bad = sorted(k for k in facts if not _FACT_ID.match(k))
    if bad:
        raise ValueError(f"fact ids must look like 'policy.fact_name', got {bad}")
    return facts


class ChildFacts(BaseModel):
    """The per-child facts WFF asks for, plus the AS dependent-child status
    (the two definitions differ, so each child carries both: ADR-0017 section 2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    qualifies_whole_year: Assertion = Assertion.UNKNOWN
    best_start_cohort: BestStartCohort = BestStartCohort.UNKNOWN
    best_start_no_disqualifying_payment: Assertion = Assertion.UNKNOWN
    # Counts as a dependent child under the Accommodation Supplement's own
    # definition, which can differ from WFF's (its source is the AS
    # specification; the mapping review checks it, not this model).
    as_dependent_child: Assertion = Assertion.UNKNOWN


class Person(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    role: PersonRole
    child_facts: ChildFacts | None = None
    asserted_facts: dict[str, Assertion] = Field(default_factory=dict)

    @field_validator("person_id")
    @classmethod
    def _id(cls, value: str) -> str:
        if not _ID.match(value):
            raise ValueError(f"'{value}' is not a valid person id")
        return value

    @field_validator("asserted_facts")
    @classmethod
    def _facts(cls, value: dict[str, Assertion]) -> dict[str, Assertion]:
        return _check_fact_ids(value)

    @model_validator(mode="after")
    def _consistent(self) -> Person:
        if self.child_facts is not None and self.role is not PersonRole.DEPENDENT_CHILD:
            raise ValueError("child_facts belong to a dependent child")
        return self


class Family(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    claimant_id: str
    partner_status: FamilyPartnerStatus = FamilyPartnerStatus.UNKNOWN
    partner_id: str | None = None
    dependent_child_ids: tuple[str, ...] = ()
    # Whether `dependent_child_ids` holds every dependent child under each
    # policy's own definition: WFF's and AS's are separate facts (ADR-0017), so
    # completeness is asserted per definition. VERIFIED: complete under that
    # definition, so a count is verified (including zero). UNKNOWN: it may be
    # incomplete, so no count is verified. A missing fact is never zero.
    wff_children_complete: Assertion = Assertion.UNKNOWN
    as_children_complete: Assertion = Assertion.UNKNOWN

    @model_validator(mode="after")
    def _consistent(self) -> Family:
        if self.partner_status is FamilyPartnerStatus.PARTNERED and self.partner_id is None:
            raise ValueError("a partnered family names its partner")
        if self.partner_status is not FamilyPartnerStatus.PARTNERED and self.partner_id is not None:
            raise ValueError("only a partnered family has a partner id")
        if Assertion.EXCLUDED in (self.wff_children_complete, self.as_children_complete):
            raise ValueError("child-list completeness is verified or unknown")
        return self


class Housing(BaseModel):
    """`None` means unverified."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenure: Tenure | None = None
    weekly_housing_costs: Decimal | None = Field(default=None, ge=0)
    partner_arrangement: PartnerArrangement | None = None
    area: AsArea | None = None
    cash_assets: Decimal | None = Field(default=None, ge=0)


class IncomeSpell(BaseModel):
    """`amount` is the total over `[start, end)`. See the module docstring."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    income_type: IncomeType
    start: date
    end: date
    amount: Decimal
    basis: IncomeBasis = IncomeBasis.GROSS

    @model_validator(mode="after")
    def _valid(self) -> IncomeSpell:
        if self.end <= self.start:
            raise ValueError(f"a spell must end after it starts, got [{self.start}, {self.end})")
        if not self.amount.is_finite():
            raise ValueError("a spell amount must be finite")
        return self


class BenefitSpell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    benefit: BenefitKind
    start: date
    end: date

    @model_validator(mode="after")
    def _valid(self) -> BenefitSpell:
        if self.end <= self.start:
            raise ValueError(f"a spell must end after it starts, got [{self.start}, {self.end})")
        return self


def straddling_spells(spells: tuple[IncomeSpell, ...], period: DatePeriod) -> tuple[IncomeSpell, ...]:
    """Spells that overlap `period` but extend past its edge."""
    return tuple(
        s
        for s in spells
        if max(s.start, period.start) < min(s.end, period.end) and (s.start < period.start or s.end > period.end)
    )


def amount_in_period(spells: tuple[IncomeSpell, ...], period: DatePeriod) -> Decimal | None:
    """The sum of `spells` (one person, income type and basis) that lie wholly
    inside `period` and tile it exactly, or `None`. No spell is scaled: a
    straddling spell or a gap gives `None` (unknown, never zero)."""
    inside = sorted((s for s in spells if s.start >= period.start and s.end <= period.end), key=lambda s: s.start)
    cursor = period.start
    for spell in inside:
        if spell.start != cursor:
            return None
        cursor = spell.end
    if not inside or cursor != period.end:
        return None
    return sum((s.amount for s in inside), Decimal(0))


class Household(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    persons: tuple[Person, ...] = Field(min_length=1)
    families: tuple[Family, ...] = Field(min_length=1)
    housing: Housing = Housing()
    income_spells: tuple[IncomeSpell, ...] = ()
    benefit_spells: tuple[BenefitSpell, ...] = ()
    asserted_facts: dict[str, Assertion] = Field(default_factory=dict)

    @field_validator("household_id")
    @classmethod
    def _id(cls, value: str) -> str:
        if not _ID.match(value):
            raise ValueError(f"'{value}' is not a valid household id")
        return value

    @field_validator("asserted_facts")
    @classmethod
    def _facts(cls, value: dict[str, Assertion]) -> dict[str, Assertion]:
        return _check_fact_ids(value)

    @model_validator(mode="after")
    def _consistent(self) -> Household:
        # Refuse first, with the reason: a multi-family household is outside
        # Pass 1 (ADR-0017 D6 answer 2), not an invalid one.
        if len(self.families) > 1:
            raise UnsupportedHousehold(
                f"household '{self.household_id}' has {len(self.families)} families; Pass 1 models one "
                "family per household (ADR-0017 D6), so it is refused rather than guessed"
            )
        by_id = {p.person_id: p for p in self.persons}
        if len(by_id) != len(self.persons):
            raise ValueError(f"household '{self.household_id}' lists a person twice")
        family = self.families[0]

        def person(person_id: str, role: PersonRole) -> None:
            found = by_id.get(person_id)
            if found is None or found.role is not role:
                raise ValueError(f"family refers to '{person_id}' as {role.value}, which the household does not hold")

        person(family.claimant_id, PersonRole.CLAIMANT)
        if family.partner_id is not None:
            person(family.partner_id, PersonRole.PARTNER)
        for child_id in family.dependent_child_ids:
            person(child_id, PersonRole.DEPENDENT_CHILD)
        if len(set(family.dependent_child_ids)) != len(family.dependent_child_ids):
            raise ValueError("a dependent child is listed twice")
        in_family = {family.claimant_id, family.partner_id, *family.dependent_child_ids}
        for p in self.persons:
            if p.role is not PersonRole.OTHER and p.person_id not in in_family:
                raise ValueError(f"'{p.person_id}' has role {p.role.value} but is not in the household's family")
        if self.housing.partner_arrangement is not None and family.partner_status is not FamilyPartnerStatus.PARTNERED:
            raise ValueError("a partner arrangement needs a partnered family")
        spell_people = {*(s.person_id for s in self.income_spells), *(s.person_id for s in self.benefit_spells)}
        for unknown in sorted(spell_people - by_id.keys()):
            raise ValueError(f"a spell refers to unknown person '{unknown}'")
        seen: dict[tuple[str, IncomeType, IncomeBasis], list[IncomeSpell]] = {}
        for spell in self.income_spells:
            seen.setdefault((spell.person_id, spell.income_type, spell.basis), []).append(spell)
        for key, group in seen.items():
            ordered = sorted(group, key=lambda s: s.start)
            for earlier, later in pairwise(ordered):
                if later.start < earlier.end:
                    raise ValueError(f"income spells for {key[0]}/{key[1].value}/{key[2].value} overlap")
        return self

    @property
    def family(self) -> Family:
        return self.families[0]

    def person(self, person_id: str) -> Person:
        return next(p for p in self.persons if p.person_id == person_id)

    def income_spells_for(
        self, person_id: str, income_type: IncomeType, basis: IncomeBasis = IncomeBasis.GROSS
    ) -> tuple[IncomeSpell, ...]:
        return tuple(
            s
            for s in self.income_spells
            if s.person_id == person_id and s.income_type is income_type and s.basis is basis
        )

    def annual_amount(
        self, person_id: str, income_type: IncomeType, period: DatePeriod, *, basis: IncomeBasis = IncomeBasis.GROSS
    ) -> Decimal | None:
        """The person's income of this type and basis over `period` (a year,
        by the caller's choice of period), or `None` if the spells do not
        cover the whole period."""
        return amount_in_period(self.income_spells_for(person_id, income_type, basis), period)

    def weekly_amount(
        self, person_id: str, income_type: IncomeType, week: DatePeriod, *, basis: IncomeBasis = IncomeBasis.GROSS
    ) -> Decimal | None:
        """As `annual_amount`, for a seven-day period."""
        if week.days != 7:
            raise ValueError(f"a week spans exactly 7 days, got [{week.start}, {week.end})")
        return amount_in_period(self.income_spells_for(person_id, income_type, basis), week)

    def content_sha256(self) -> str:
        """The household's identity: a hash of its canonical content, with
        people and spells in a fixed order."""

        def key(item: dict[str, Any]) -> str:
            return json.dumps(item, sort_keys=True, separators=(",", ":"))

        content = self.model_dump(mode="json")
        content["persons"].sort(key=lambda p: p["person_id"])
        content["income_spells"].sort(key=key)
        content["benefit_spells"].sort(key=key)
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
