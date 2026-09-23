"""Task 12: the pure `calculate_wff()` function.

Implements the "Approved Task 10 scoped calculation contract" in
`policy_specs/working_for_families/specification.md` (accepted by Pete,
Task 10.4, `policy_version: "0.1.0"`) against a `PolicyParameterSet` produced
by Task 11's loader. Deterministic: canonical scenario facts + resolved
policy parameters in, per-component outcome + reason out. No I/O, no network,
no LLM call, per REPOSITORY_STRUCTURE.md's dependency boundary and
`doctrine/llm_boundaries.md`.

This module deliberately does not attempt every WFF rule in the Income Tax
Act -- only the narrow v0.1 supported domain Pete accepted: one claimant and
a stable partner status, a stable dependent-child set, residence and
principal-care arrangement for the *whole* 2026-27 tax year, no shared care,
no relationship change, no competing caregiver. Anything outside that domain
must resolve to `unsupported` or `needs_review`, never a silent zero or a
guessed number (SCHEMA.md; CLAUDE.md's "Ground truth" section).

MC 6(b)'s component mapping (an earlier version of this file left as an
unresolved primary-source gap) is now checked directly against the official
Income Tax Act 2007 text (legislation.govt.nz, Part M, s MC 6, fetched
2026-09-21): "a person does not qualify for -- ... (b) an in-work tax
credit, parental tax credit, or minimum family tax credit if, during the
relationship period, they receive -- (i) a main benefit; or ... (iii) a
parent's allowance or a children's pension". This is distinct from MC 6(a),
which excludes "an abating WFF tax credit or a Best Start tax credit" (family
tax credit, in-work tax credit, and Best Start -- the credits that abate --
but not minimum family tax credit, which doesn't). MC 6(b) therefore gates
in-work tax credit *and* minimum family tax credit; parental tax credit is
out of v0.1 scope and not modelled.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from decimal import ROUND_FLOOR, Decimal
from enum import Enum
from pathlib import Path
from typing import Literal

from poltika.engines.simulator.trace import (
    ComponentTrace,
    input_uses,
    merge_ids,
    parameter_uses,
    recording_copy,
    recording_parameters,
    trace_header,
)
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters, load_policy_spec
from poltika.semantics.schemas.policy_spec import ReferencePeriod

ComponentOutcome = Literal["calculated", "needs_review", "unsupported"]


class FactStatus(str, Enum):
    """Tri-state for any fact that gates a component.

    One shared tri-state covers both flavours of gate this contract uses:

    - A **domain/eligibility precondition** (e.g. "in-work eligibility
      established"): `VERIFIED` means the condition holds and the branch may
      proceed; `EXCLUDED` means it's verified *not* to hold, so the scenario
      is structurally outside this branch (`unsupported`); `UNKNOWN` means
      it hasn't been verified either way (`needs_review`).
    - A **known exclusion trigger** (e.g. MD 14/15 protected credit):
      `VERIFIED` means verified that the trigger does *not* apply (the
      ordinary branch proceeds); `EXCLUDED` means verified that it *does*
      apply (`unsupported` -- the protected/direct-abatement/etc. pathway
      needs its own specification, per specification.md); `UNKNOWN` means
      unverified applicability (`needs_review`, per specification.md's
      explicit "unknown applicability is needs_review" language repeated
      for every one of these triggers).

    Never a bare `bool`: SCHEMA.md forbids silently defaulting a missing
    fact to a value that would yield entitlement, and a bool has no way to
    represent "not verified" distinctly from "verified false".
    """

    VERIFIED = "verified"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


class BestStartCohort(str, Enum):
    """A child's Best Start birth-cohort classification. Not a bool: a child
    can be genuinely outside Best Start entitlement altogether (too old --
    outside the first-three-years window entirely), or within that general
    window but in a birth cohort/period specification.md explicitly puts
    outside the v0.1 calculable branch ("later birth cohorts ... require
    separate review; do not apply this branch to them") -- collapsing those
    two into one `bool` would silently treat "out of this narrow branch,
    entitlement genuinely unknown" the same as "verified zero entitlement",
    which is exactly the false-zero bug this type exists to prevent.
    """

    # Born 2024-04-01 through 2025-03-31 inclusive, eligible for the entire
    # 2026-27 tax year -- the one cohort specification.md step 5 calculates.
    IN_SUPPORTED_COHORT = "in_supported_cohort"
    # Verified genuinely outside Best Start entitlement altogether (e.g.
    # older than the first-three-years window for the whole tax year) --
    # a real, evidenced zero, not a scope limitation.
    OUTSIDE_BEST_START_ENTITLEMENT = "outside_best_start_entitlement"
    # Within Best Start's general eligibility window but a birth cohort or
    # in-year birth/third-birthday period specification.md excludes from
    # this narrow v0.1 branch (e.g. born on/after 2025-04-01, a first-year
    # pre-2026-04-01 birth, or an in-year birth/third birthday) -- entitlement
    # is real law, just not something this branch calculates.
    OTHER_COHORT_UNSUPPORTED = "other_cohort_unsupported"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ChildFacts:
    """One child's facts, per policy.yaml's `children` input
    (`list_of_dated_child_facts`).

    `qualifies_whole_year` is the v0.1 domain precondition from
    specification.md: "under 18 ... throughout the tax year" and in the
    claimant's full care. If this is not `VERIFIED` for *any* child in the
    scenario, the whole household falls outside the v0.1 branch (not just
    that child) -- specification.md states this as a household-wide
    precondition, not a per-child inclusion/exclusion choice.
    """

    qualifies_whole_year: FactStatus
    best_start_cohort: BestStartCohort = BestStartCohort.UNKNOWN
    # MC 6(c) disqualifying payment for *this* child (same-child parental
    # leave/preterm-baby payment, parental tax credit, or specified
    # veterans' payment) -- specification.md WFF-06.
    best_start_no_disqualifying_payment: FactStatus = FactStatus.UNKNOWN


class PartnerStatus(str, Enum):
    """Whether the claimant has a partner, per specification.md's "one
    claimant and a stable partner status" domain precondition -- a
    household-level fact, independent of `VerifiedIncome`.

    This exists because `VerifiedIncome.partner_amount is None` is
    ambiguous on its own: it's the correct shape both for a genuinely single
    claimant (no partner to verify) *and* for a partnered claimant whose
    partner's income simply wasn't supplied. Those are not the same case --
    the second one must be `needs_review`, not silently treated as the
    first. `PartnerStatus` is the independent fact that resolves the
    ambiguity; see `_partner_income_gap_reason`.
    """

    SINGLE = "single"
    PARTNERED = "partnered"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VerifiedIncome:
    """A verified `family_scheme_income` figure, per specification.md's
    partnered-income boundary: "For a partnered claimant, the verification
    must also show each person's family-scheme income and their combined
    amount. The ordinary combined-income abatement branch ... is used only
    when both individual amounts are non-negative ... an unexplained
    household total is never enough."

    `partner_amount is None` here means only "no partner amount was
    supplied" -- it does NOT by itself mean "single claimant". Whether that
    absence is correct (a genuinely single claimant) or a verification gap
    (a partnered claimant whose partner's income wasn't captured) depends on
    `WffScenario.partner_status`, which this type has no access to -- see
    `PartnerStatus` and `_partner_income_gap_reason`. Structurally, this
    type still makes it impossible to supply a bare combined total without
    going through per-person verification -- there is no "just give me a
    number" constructor -- and `__post_init__` enforces the
    non-negative-per-person requirement the ordinary branch depends on.
    """

    claimant_amount: Decimal
    partner_amount: Decimal | None = None

    def __post_init__(self) -> None:
        if self.claimant_amount < 0:
            raise ValueError(f"VerifiedIncome.claimant_amount must not be negative, got {self.claimant_amount}")
        if self.partner_amount is not None and self.partner_amount < 0:
            raise ValueError(f"VerifiedIncome.partner_amount must not be negative, got {self.partner_amount}")

    @property
    def combined(self) -> Decimal:
        return self.claimant_amount + (self.partner_amount if self.partner_amount is not None else Decimal(0))


@dataclass(frozen=True)
class WffScenario:
    """The v0.1 supported-domain scenario facts `calculate_wff()` accepts.

    Every field traces to a named input in `policy_specs/working_for_families/
    policy.yaml`'s `inputs` list or a specific exclusion trigger named in
    specification.md's calculation sequence (steps 2-5) and Task 10.3's
    review finding. Fields are canonical Poltika facts, already resolved
    from whatever upstream source supplied them -- this module never reads
    a raw source itself (REPOSITORY_STRUCTURE.md's dependency boundary).
    """

    # --- Household-wide domain gates (policy.yaml's `eligibility_facts`
    # input): MC 5(2) residence, MC 10(1) principal care, no competing
    # caregiver / MC 7 allocation, no relationship change -- collapsed into
    # one gate because policy.yaml declares exactly one opaque
    # `eligibility_facts` input for this bundle, not five separate ones.
    household_eligibility: FactStatus

    # Tax Administration Act s 80KW: an applicable 27-fortnight/53-week
    # extra-instalment year. Household-wide: specification.md says an
    # applicable case is `unsupported` "in this first branch rather than the
    # ordinary annual amount" for the whole calculation, not per component.
    extra_instalment_status: FactStatus

    # policy.yaml's `children` input.
    children: list[ChildFacts] = field(default_factory=list)

    # Whether the claimant has a partner -- independent of
    # `family_scheme_income`'s shape; see `PartnerStatus`'s docstring for
    # why this can't be inferred from `VerifiedIncome.partner_amount` alone.
    # Defaults to UNKNOWN, never SINGLE: SCHEMA.md forbids silently
    # defaulting a missing fact to a value that would let a partnered
    # household's unverified partner income pass as though there were no
    # partner to verify.
    partner_status: PartnerStatus = PartnerStatus.UNKNOWN

    # policy.yaml's `family_scheme_income` input (NZD_per_tax_year). `None`
    # means unverified -- policy.yaml's `missing_outcome: needs_review`.
    # `VerifiedIncome`, not a bare `Decimal`: see that type's docstring --
    # this is what enforces the partnered-income verification boundary,
    # together with `partner_status` above.
    family_scheme_income: VerifiedIncome | None = None

    # policy.yaml's `net_family_scheme_income` input (NZD_per_tax_year_
    # after_tax), required_for minimum_family_tax_credit only.
    net_family_scheme_income: Decimal | None = None
    # specification.md: "the input must attest to this derivation, not
    # merely carry an after-tax label" (ME 3's adjusted-income/adjusted-
    # tax-liability/MB 1(2)/(3) formula). A bare Decimal can't carry that
    # attestation, so it's a separate explicit flag the caller must set --
    # this makes the requirement enforceable in code rather than silently
    # trusted (CLAUDE.md: "do not silently resolve policy interpretation
    # ambiguity").
    net_family_scheme_income_me3_attested: bool = False

    # WFF-04: full-year qualifying salary/wage earner, no main benefit or
    # Student Allowance period, no unpaid work break (policy.yaml's
    # `work_and_payment_facts` input).
    in_work_eligibility: FactStatus = FactStatus.UNKNOWN
    # MD 14/15 protected family-tax-credit / in-work direct-abatement
    # pathway trigger (specification.md step 2/3; shared between FTC/IWTC
    # since MD 14/15 is a family-tax-credit-level protection that also
    # blocks the ordinary in-work abatement path).
    ftc_iwtc_protected_or_direct_abatement: FactStatus = FactStatus.UNKNOWN
    # MC 6(a): a specified veterans' payment for the relationship period.
    # specification.md: "can disqualify abating WFF and Best Start" -- i.e.
    # family tax credit, in-work tax credit, and Best Start, but NOT
    # minimum family tax credit (which does not abate and is not described
    # as MC 6(a)-affected in specification.md).
    mc6a_veterans_payment: FactStatus = FactStatus.UNKNOWN
    # MC 6(b): a main benefit, or a parent's allowance/children's pension,
    # received during the relationship period. Per the official Act text
    # (checked 2026-09-21): excludes in-work tax credit and minimum family
    # tax credit (also parental tax credit, out of v0.1 scope) -- distinct
    # from MC 6(a) above, which excludes family tax credit, in-work tax
    # credit, and Best Start, but not minimum family tax credit.
    mc6b_disqualifying_payment: FactStatus = FactStatus.UNKNOWN

    # MA 7 / ME 2: 52 verified full-time-earner weeks with no ME 2(2)-(4)
    # Commissioner-determined employment period or part-week case. MA 7's
    # threshold itself is 20 solo hours or 30 combined partnered hours per
    # week, so this alone isn't enough -- `_minimum_family_tax_credit` also
    # checks `partner_status` below, since VERIFIED here doesn't say which
    # threshold was applied.
    minimum_family_full_time_earner_weeks: FactStatus = FactStatus.UNKNOWN

    # Best Start: "no shared care" (household-wide, specification.md step 5).
    best_start_no_shared_care: FactStatus = FactStatus.UNKNOWN
    # MG 4 protected Best Start credit month.
    best_start_protected_credit: FactStatus = FactStatus.UNKNOWN

    def __post_init__(self) -> None:
        # A negative verified_amount is not a policy outcome to resolve
        # (needs_review/unsupported) -- it's malformed input. Silently
        # accepting it would be dangerous: `_complete_dollar_excess` floors
        # a negative excess to zero, so a sign error upstream would quietly
        # read as "no abatement" instead of surfacing the bad data.
        # (family_scheme_income's non-negativity is enforced by
        # VerifiedIncome.__post_init__ itself, per person, at construction.)
        if self.net_family_scheme_income is not None and self.net_family_scheme_income < 0:
            raise ValueError(
                f"WffScenario.net_family_scheme_income must not be negative, got {self.net_family_scheme_income}"
            )
        # A SINGLE claimant with a partner_amount is a structural
        # contradiction, not a policy outcome -- reject it rather than
        # silently including an amount that shouldn't exist in the combined
        # figure (or silently ignoring it, which would be just as wrong).
        if (
            self.partner_status == PartnerStatus.SINGLE
            and self.family_scheme_income is not None
            and self.family_scheme_income.partner_amount is not None
        ):
            raise ValueError(
                "WffScenario.partner_status is SINGLE but family_scheme_income.partner_amount "
                f"is set ({self.family_scheme_income.partner_amount}) -- a single claimant "
                "cannot have a verified partner amount"
            )


@dataclass(frozen=True)
class ComponentResult:
    """One component's outcome. `value` is populated only when
    `outcome == "calculated"` -- Task 12's equivalent of Task 11's
    `ParameterResolution` contract: never treat a missing value as zero.
    """

    outcome: ComponentOutcome
    value: Decimal | None = None
    reason: str | None = None
    # Task 31: what this result was computed from. Excluded from equality,
    # so attaching a trace never changes whether two results compare equal.
    trace: ComponentTrace | None = field(default=None, compare=False)


@dataclass(frozen=True)
class WffResult:
    family_tax_credit: ComponentResult
    in_work_tax_credit: ComponentResult
    minimum_family_tax_credit: ComponentResult
    best_start: ComponentResult

    def total_annual_entitlement(self) -> Decimal | None:
        """The sum of all four components, or `None` if any component is not
        `calculated`. specification.md: "Do not sum a partial result and
        present it as total WFF entitlement" -- this method is the one place
        that's allowed to sum, and it refuses to unless every component has
        an actual value.
        """
        components = (
            self.family_tax_credit,
            self.in_work_tax_credit,
            self.minimum_family_tax_credit,
            self.best_start,
        )
        if any(c.outcome != "calculated" for c in components):
            return None
        total = Decimal(0)
        for c in components:
            assert c.value is not None  # guaranteed by outcome == "calculated"
            total += c.value
        return total


def _partner_income_gap_reason(scenario: WffScenario) -> str | None:
    """`None` if `family_scheme_income.combined` can be trusted as the
    ordinary branch's amount; otherwise the `needs_review` reason. Closes
    the gap `VerifiedIncome` alone can't: `partner_amount is None` is the
    right shape for a genuinely single claimant, but also the wrong-looking
    -- and indistinguishable -- shape for a partnered claimant whose
    partner's income was never verified. Only `WffScenario.partner_status`,
    checked here, can tell those two apart.
    """
    if scenario.partner_status == PartnerStatus.UNKNOWN:
        return (
            "partner status (single vs partnered) is unverified -- cannot confirm "
            "family_scheme_income represents the correct ordinary-branch amount"
        )
    if (
        scenario.partner_status == PartnerStatus.PARTNERED
        and scenario.family_scheme_income is not None
        and scenario.family_scheme_income.partner_amount is None
    ):
        return "partnered claimant but the partner's family-scheme income has not been separately verified"
    return None


def _complete_dollar_excess(amount: Decimal, threshold: Decimal) -> Decimal:
    """`floor(max(0, amount - threshold))`. specification.md: the abatement
    rate applies to "complete dollars" of income *excess*, not the credit
    amount -- MD 13(3)(a)/MG 3(2)(a).
    """
    excess = amount - threshold
    if excess <= 0:
        return Decimal(0)
    return excess.to_integral_value(rounding=ROUND_FLOOR)


def _household_gate_failure(scenario: WffScenario) -> ComponentResult | None:
    """Checks that apply to every component before any component-specific
    logic. Returns the shared failure result, or `None` if the household may
    proceed. `unsupported` (a known structural exclusion) takes precedence
    over `needs_review` (an unverified fact) when both are present, since an
    unsupported finding reflects a definite fact rather than an absence of
    one.
    """
    if not scenario.children:
        return ComponentResult(
            outcome="unsupported",
            reason="no dependent child in the scenario -- outside WFF's family-scheme membership domain",
        )

    if any(c.qualifies_whole_year == FactStatus.EXCLUDED for c in scenario.children):
        return ComponentResult(
            outcome="unsupported",
            reason="a child does not qualify for the whole tax year (age, care, or dependency) -- outside the v0.1 whole-year branch",
        )

    if scenario.household_eligibility == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="household eligibility_facts verified outside the v0.1 domain (e.g. shared care, relationship change, competing caregiver, or an unsupported residence pathway)",
        )

    if scenario.extra_instalment_status == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="Tax Administration Act s 80KW extra-instalment year applies -- the ordinary annual-entitlement branch does not cover this case",
        )

    if any(c.qualifies_whole_year == FactStatus.UNKNOWN for c in scenario.children):
        return ComponentResult(
            outcome="needs_review",
            reason="a child's whole-year qualification (age, care, dependency) is unverified",
        )

    if scenario.household_eligibility == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review",
            reason="household eligibility_facts (residence, principal care, competing caregiver) unverified",
        )

    if scenario.extra_instalment_status == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review",
            reason="Tax Administration Act s 80KW extra-instalment applicability unverified",
        )

    return None


def _param_value(parameters: PolicyParameterSet, parameter_id: str) -> ComponentResult | Decimal:
    """Looks up one resolved parameter. Returns its `Decimal` value if
    resolved, or the `ComponentResult` to use verbatim if it isn't --
    callers propagate that result rather than proceeding.
    """
    resolution = parameters.get(parameter_id)
    if resolution.outcome != "resolved":
        assert resolution.outcome in ("needs_review", "unsupported")
        return ComponentResult(
            outcome=resolution.outcome,
            reason=resolution.reason or f"parameter '{parameter_id}' is {resolution.outcome}",
        )
    assert resolution.value is not None
    return resolution.value


def _family_tax_credit(
    scenario: WffScenario, parameters: PolicyParameterSet
) -> tuple[ComponentResult, Decimal]:
    """Returns the FTC component result and `remaining_abatement` -- MD
    2(2)(c) applies abatement to family tax credit first, then passes any
    remainder to in-work tax credit, so the caller (`calculate_wff`) needs
    both even when FTC itself is `calculated`.
    """
    zero = Decimal(0)

    if scenario.mc6a_veterans_payment == FactStatus.EXCLUDED:
        return (
            ComponentResult(
                outcome="unsupported",
                reason="MC 6(a) veterans' payment disqualifies abating WFF for this relationship period",
            ),
            zero,
        )
    if scenario.ftc_iwtc_protected_or_direct_abatement == FactStatus.EXCLUDED:
        return (
            ComponentResult(
                outcome="unsupported",
                reason="MD 14/15 protected family-tax-credit case applies -- needs its own specification, not the ordinary abatement formula",
            ),
            zero,
        )
    if scenario.mc6a_veterans_payment == FactStatus.UNKNOWN:
        return (
            ComponentResult(outcome="needs_review", reason="MC 6(a) veterans' payment applicability unverified"),
            zero,
        )
    if scenario.ftc_iwtc_protected_or_direct_abatement == FactStatus.UNKNOWN:
        return (
            ComponentResult(
                outcome="needs_review",
                reason="MD 14/15 protected-credit applicability unverified",
            ),
            zero,
        )
    if scenario.family_scheme_income is None:
        return (
            ComponentResult(outcome="needs_review", reason="family_scheme_income not verified"),
            zero,
        )
    partner_income_gap = _partner_income_gap_reason(scenario)
    if partner_income_gap is not None:
        return (ComponentResult(outcome="needs_review", reason=partner_income_gap), zero)

    eldest = _param_value(parameters, "family_tax_credit_eldest_child")
    if isinstance(eldest, ComponentResult):
        return eldest, zero
    additional = _param_value(parameters, "family_tax_credit_additional_child")
    if isinstance(additional, ComponentResult):
        return additional, zero
    threshold = _param_value(parameters, "family_tax_credit_abatement_threshold")
    if isinstance(threshold, ComponentResult):
        return threshold, zero
    rate = _param_value(parameters, "family_tax_credit_abatement_rate")
    if isinstance(rate, ComponentResult):
        return rate, zero

    additional_children = len(scenario.children) - 1
    family_credit_base = eldest + additional * additional_children
    abatement = rate * _complete_dollar_excess(scenario.family_scheme_income.combined, threshold)
    family_credit = max(zero, family_credit_base - abatement)
    remaining_abatement = max(zero, abatement - family_credit_base)

    return ComponentResult(outcome="calculated", value=family_credit), remaining_abatement


def _in_work_tax_credit(
    scenario: WffScenario,
    parameters: PolicyParameterSet,
    ftc_result: ComponentResult,
    remaining_abatement: Decimal,
) -> ComponentResult:
    zero = Decimal(0)

    if scenario.mc6a_veterans_payment == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MC 6(a) veterans' payment disqualifies abating WFF for this relationship period",
        )
    if scenario.ftc_iwtc_protected_or_direct_abatement == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="direct-abatement pathway applies (family tax credit unavailable for a child due to a different payment) -- needs its own specification",
        )
    if scenario.in_work_eligibility == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="in-work eligibility test fails (main benefit/Student Allowance period, unpaid break, or not a qualifying full-year earner)",
        )
    if scenario.mc6b_disqualifying_payment == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MC 6(b): a main benefit or a parent's allowance/children's pension was received during the relationship period",
        )
    if scenario.mc6a_veterans_payment == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="MC 6(a) veterans' payment applicability unverified")
    if scenario.ftc_iwtc_protected_or_direct_abatement == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review", reason="direct-abatement pathway applicability unverified"
        )
    if scenario.in_work_eligibility == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="in-work eligibility unverified")
    if scenario.mc6b_disqualifying_payment == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="MC 6(b) disqualifying-payment status unverified")

    if ftc_result.outcome != "calculated":
        # MD 2(2)(c): abatement applies to family tax credit first, then any
        # *remainder* to in-work tax credit -- if family tax credit's own
        # abatement couldn't be determined (e.g. unverified income), the
        # remainder is equally undetermined. Assuming zero remaining
        # abatement here would silently overstate in-work tax credit.
        return ComponentResult(
            outcome=ftc_result.outcome,
            reason=(
                "family tax credit's abatement could not be determined, and MD 2(2)(c) "
                f"passes any remainder to in-work tax credit: {ftc_result.reason}"
            ),
        )

    base = _param_value(parameters, "in_work_base")
    if isinstance(base, ComponentResult):
        return base
    additional = _param_value(parameters, "in_work_additional_child")
    if isinstance(additional, ComponentResult):
        return additional

    num_children = len(scenario.children)
    children_beyond_three = max(0, num_children - 3)
    iwtc_base = base + additional * children_beyond_three
    iwtc = max(zero, iwtc_base - remaining_abatement)

    return ComponentResult(outcome="calculated", value=iwtc)


def _minimum_family_tax_credit(scenario: WffScenario, parameters: PolicyParameterSet) -> ComponentResult:
    if scenario.minimum_family_full_time_earner_weeks == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="ME 2(2)-(4) Commissioner-determined employment period or a part-week case applies -- outside the 52-verified-week v0.1 branch",
        )
    if scenario.mc6b_disqualifying_payment == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MC 6(b): a main benefit or a parent's allowance/children's pension was received during the relationship period",
        )
    if scenario.minimum_family_full_time_earner_weeks == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="full-time-earner weeks (MA 7 / ME 2) unverified")
    if scenario.partner_status == PartnerStatus.UNKNOWN:
        # MA 7's full-time-earner test itself depends on partner status --
        # specification.md: "at least 20 hours for a single person or 30
        # combined hours for partners per week". minimum_family_full_time_
        # earner_weeks being VERIFIED doesn't establish *which* threshold
        # was actually applied; without knowing single vs partnered, that
        # verification can't be trusted for this branch.
        return ComponentResult(
            outcome="needs_review",
            reason="partner status (single vs partnered) is unverified -- MA 7's full-time-earner threshold (20 solo hours vs 30 combined) depends on it",
        )
    if scenario.mc6b_disqualifying_payment == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="MC 6(b) disqualifying-payment status unverified")
    if scenario.family_scheme_income is None:
        # ME 3(3)(a)(i): the net family-scheme-income formula's own
        # "adjusted income" item starts from the person's family scheme
        # income -- net income is derived from it, not an independently
        # suppliable figure. specification.md's accepted input boundary
        # names a separately verified family-scheme-income input as part
        # of the whole domain, not scoped away from this component (Task
        # 17 review finding).
        return ComponentResult(outcome="needs_review", reason="family_scheme_income not verified")
    partner_income_gap = _partner_income_gap_reason(scenario)
    if partner_income_gap is not None:
        return ComponentResult(outcome="needs_review", reason=partner_income_gap)
    if not scenario.net_family_scheme_income_me3_attested:
        return ComponentResult(
            outcome="needs_review",
            reason="net_family_scheme_income not attested as an ME 3 derivation (adjusted income minus adjusted tax liability plus MB 1(2)/(3) amounts)",
        )
    if scenario.net_family_scheme_income is None:
        return ComponentResult(outcome="needs_review", reason="net_family_scheme_income not verified")

    prescribed = _param_value(parameters, "minimum_family_prescribed_amount")
    if isinstance(prescribed, ComponentResult):
        return prescribed

    mftc = max(Decimal(0), prescribed - scenario.net_family_scheme_income)
    return ComponentResult(outcome="calculated", value=mftc)


def _best_start(scenario: WffScenario, parameters: PolicyParameterSet) -> ComponentResult:
    if scenario.mc6a_veterans_payment == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MC 6(a) veterans' payment disqualifies Best Start for this relationship period",
        )
    if scenario.best_start_no_shared_care == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported", reason="shared care applies -- outside the v0.1 no-shared-care branch"
        )
    if scenario.best_start_protected_credit == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MG 4 protected Best Start credit month applies -- needs its own specification",
        )
    if scenario.mc6a_veterans_payment == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="MC 6(a) veterans' payment applicability unverified")
    if scenario.best_start_no_shared_care == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="shared-care status unverified")
    if scenario.best_start_protected_credit == FactStatus.UNKNOWN:
        return ComponentResult(outcome="needs_review", reason="MG 4 protected Best Start credit applicability unverified")

    supported_cohort_children = [
        c for c in scenario.children if c.best_start_cohort == BestStartCohort.IN_SUPPORTED_COHORT
    ]

    # A child in a birth cohort/period specification.md excludes from this
    # narrow branch has real, unresolved entitlement -- not a zero (Task 12
    # review finding: an earlier version of this file collapsed "out of the
    # v0.1 branch" and "verified zero" into the same bool, which is the
    # false-zero bug this check exists to prevent).
    if any(c.best_start_cohort == BestStartCohort.OTHER_COHORT_UNSUPPORTED for c in scenario.children):
        return ComponentResult(
            outcome="unsupported",
            reason="a child's Best Start birth cohort/period is outside the v0.1 narrow calculable branch (e.g. a later birth cohort, or an in-year birth/third birthday) -- real entitlement, not calculated here",
        )
    if any(c.best_start_cohort == BestStartCohort.UNKNOWN for c in scenario.children):
        return ComponentResult(
            outcome="needs_review", reason="a child's Best Start birth-cohort status is unverified"
        )
    if len(supported_cohort_children) > 1:
        return ComponentResult(
            outcome="unsupported",
            reason="more than one Best Start birth-cohort-eligible child -- multi-child apportionment is outside the v0.1 single-child branch",
        )
    if not supported_cohort_children:
        # Every child is verified OUTSIDE_BEST_START_ENTITLEMENT (the only
        # remaining case once OTHER_COHORT_UNSUPPORTED/UNKNOWN are ruled out
        # above) -- a genuine, evidenced zero, not a scope limitation, per
        # specification.md's "may yield zero for that component" for an
        # evidenced eligibility-test failure.
        return ComponentResult(outcome="calculated", value=Decimal(0))

    child = supported_cohort_children[0]
    if child.best_start_no_disqualifying_payment == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason="MC 6(c) disqualifying payment applies for the Best Start child",
        )
    if child.best_start_no_disqualifying_payment == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review", reason="MC 6(c) disqualifying-payment status unverified for the Best Start child"
        )
    if scenario.family_scheme_income is None:
        return ComponentResult(outcome="needs_review", reason="family_scheme_income not verified")
    partner_income_gap = _partner_income_gap_reason(scenario)
    if partner_income_gap is not None:
        return ComponentResult(outcome="needs_review", reason=partner_income_gap)

    annual_amount = _param_value(parameters, "best_start_annual_amount")
    if isinstance(annual_amount, ComponentResult):
        return annual_amount
    threshold = _param_value(parameters, "best_start_abatement_threshold")
    if isinstance(threshold, ComponentResult):
        return threshold
    rate = _param_value(parameters, "best_start_abatement_rate")
    if isinstance(rate, ComponentResult):
        return rate

    abatement = rate * _complete_dollar_excess(scenario.family_scheme_income.combined, threshold)
    best_start = max(Decimal(0), annual_amount - abatement)

    return ComponentResult(outcome="calculated", value=best_start)


def calculate_wff(scenario: WffScenario, parameters: PolicyParameterSet) -> WffResult:
    """Task 12: the pure WFF calculator.

    `parameters` must already be resolved for the modelled date by Task 11's
    `load_policy_parameters()` -- this function performs no date arithmetic
    of its own and makes no network or file access. Every component resolves
    independently to `calculated`, `needs_review`, or `unsupported`; see
    `WffResult.total_annual_entitlement()` for the one place a total may be
    computed, and only when every component is `calculated`.

    Each component's result carries a `ComponentTrace` (Task 31) recording
    the parameters and scenario facts it consulted. Recording wraps each
    component call; the component functions themselves are unchanged.
    """
    gate_scenario, gate_reads = recording_copy(scenario)
    gate_failure = _household_gate_failure(gate_scenario)
    if gate_failure is not None:
        return WffResult(
            **{
                component_id: _traced(gate_failure, component_id, scenario, parameters, gate_reads, [])
                for component_id in _WFF_COMPONENT_IDS
            }
        )

    ftc_scenario, ftc_reads = recording_copy(scenario)
    ftc_parameters, ftc_params = recording_parameters(parameters)
    ftc_result, remaining_abatement = _family_tax_credit(ftc_scenario, ftc_parameters)

    iwtc_scenario, iwtc_reads = recording_copy(scenario)
    iwtc_parameters, iwtc_params = recording_parameters(parameters)
    # Recording copy of FTC's result: if in-work tax credit reads it, it has
    # reached MD 2(2)(c)'s dependency on FTC's remaining abatement, so FTC's
    # own parameters and inputs become part of its trace too.
    ftc_seen_by_iwtc, ftc_result_reads = recording_copy(ftc_result)
    iwtc_result = _in_work_tax_credit(iwtc_scenario, iwtc_parameters, ftc_seen_by_iwtc, remaining_abatement)
    iwtc_used_ftc = bool(ftc_result_reads)

    mftc_scenario, mftc_reads = recording_copy(scenario)
    mftc_parameters, mftc_params = recording_parameters(parameters)
    mftc_result = _minimum_family_tax_credit(mftc_scenario, mftc_parameters)

    best_start_scenario, best_start_reads = recording_copy(scenario)
    best_start_parameters, best_start_params = recording_parameters(parameters)
    best_start_result = _best_start(best_start_scenario, best_start_parameters)

    return WffResult(
        family_tax_credit=_traced(
            ftc_result, "family_tax_credit", scenario, parameters, merge_ids(gate_reads, ftc_reads), ftc_params
        ),
        in_work_tax_credit=_traced(
            iwtc_result,
            "in_work_tax_credit",
            scenario,
            parameters,
            merge_ids(gate_reads, iwtc_reads, ftc_reads if iwtc_used_ftc else []),
            merge_ids(iwtc_params, ftc_params if iwtc_used_ftc else []),
            upstream=("family_tax_credit",) if iwtc_used_ftc else (),
        ),
        minimum_family_tax_credit=_traced(
            mftc_result, "minimum_family_tax_credit", scenario, parameters, merge_ids(gate_reads, mftc_reads), mftc_params
        ),
        best_start=_traced(
            best_start_result,
            "best_start",
            scenario,
            parameters,
            merge_ids(gate_reads, best_start_reads),
            best_start_params,
        ),
    )


_WFF_COMPONENT_IDS = ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start")

# Task 31: the rounding and ordering rules a `calculated` component's path
# applies, keyed by component. Each rule is attached only when the parameter
# named with it was consulted -- i.e. the formula step it governs was reached.
# Citations are the ones this file's own implementation already carries
# (`_complete_dollar_excess()`, `_in_work_tax_credit()`), not new policy text.
_WFF_CALCULATION_RULES: dict[str, tuple[tuple[str, str], ...]] = {
    "family_tax_credit": (
        (
            "family_tax_credit_abatement_rate",
            (
                "MD 13(3)(a): the abatement rate applies to complete dollars of family scheme income over "
                "the threshold (excess floored to a whole dollar)"
            ),
        ),
        (
            "family_tax_credit_abatement_rate",
            "MD 2(2)(c): abatement applies to family tax credit first; any remainder passes to in-work tax credit",
        ),
    ),
    "in_work_tax_credit": (
        (
            "in_work_base",
            "MD 2(2)(c): reduced only by the abatement remaining after family tax credit",
        ),
    ),
    "best_start": (
        (
            "best_start_abatement_rate",
            (
                "MG 3(2)(a): the abatement rate applies to complete dollars of family scheme income over "
                "the threshold (excess floored to a whole dollar)"
            ),
        ),
    ),
}


def _traced(
    result: ComponentResult,
    component_id: str,
    scenario: WffScenario,
    parameters: PolicyParameterSet,
    input_names: list[str],
    parameter_ids: list[str],
    *,
    upstream: tuple[str, ...] = (),
) -> ComponentResult:
    rules: tuple[str, ...] = ()
    if result.outcome == "calculated":
        rules = tuple(
            rule for parameter_id, rule in _WFF_CALCULATION_RULES.get(component_id, ()) if parameter_id in parameter_ids
        )
    return replace(
        result,
        trace=ComponentTrace(
            component_id=component_id,
            **trace_header(parameters, scenario),
            parameters=parameter_uses(parameters, parameter_ids),
            inputs=input_uses(scenario, input_names),
            upstream_components=upstream,
            calculation_rules=rules,
        ),
    )


# --- Task 20: module integration, per ARCHITECTURE.md's "Simulation module
# contract" -- combines Task 11's load_policy_parameters() and this file's
# own calculate_wff() behind one call, adding the module contract's
# `validation_checks`: the schema-version/approval-status gates
# load_policy_parameters() already enforces, plus the module-specific
# invariants below. Task 17's independent review found that a resolved
# parameter's interval was never checked against the policy's complete
# reference_period, only against the single requested modelled_date
# (ARCHITECTURE_ISSUE). Pete decided (22 September 2026, recorded in
# BUILD_PLAN.md Task 19) to keep Task 11's loader general-purpose and
# deliberately free of any hardcoded assessment-period assumption --
# tests/unit/policy/test_loader.py's test_open_ended_final_interval_resolves
# already establishes that as intentional, not an oversight -- and to place
# this responsibility here instead, at the module integration boundary,
# where a specific caller's assumption "this is a full 2026-27 WFF
# calculation" actually applies.

_WFF_MODULE_ID = "working_for_families"

# Every parameter id calculate_wff()'s component functions look up via
# _param_value() -- kept as one explicit list so the module boundary can
# confirm each one actually resolves *before* calculate_wff() runs, rather
# than letting PolicyParameterSet.get() raise a bare KeyError partway
# through a component calculation for a policy.yaml that simply never
# declared one of them (PR #21 review finding).
_WFF_REQUIRED_PARAMETER_IDS = frozenset(
    {
        "family_tax_credit_eldest_child",
        "family_tax_credit_additional_child",
        "family_tax_credit_abatement_threshold",
        "family_tax_credit_abatement_rate",
        "in_work_base",
        "in_work_additional_child",
        "minimum_family_prescribed_amount",
        "best_start_annual_amount",
        "best_start_abatement_threshold",
        "best_start_abatement_rate",
    }
)


def _covers(value_effective_from: date, value_effective_to: date | None, target_date: date) -> bool:
    """Same interval-membership test as `poltika.policy.loader`'s private
    `_covers()` -- duplicated deliberately, not imported: that function is
    a loader implementation detail, and this file must not reach into it
    (REPOSITORY_STRUCTURE.md's dependency boundary is one-directional,
    engines/simulator -> policy, not the reverse of poking at policy's
    private helpers)."""
    if target_date < value_effective_from:
        return False
    return value_effective_to is None or target_date < value_effective_to


def _spans_reference_period(
    value_effective_from: date, value_effective_to: date | None, reference_period: ReferencePeriod
) -> bool:
    """Whether a parameter value's effective interval fully contains the
    policy's reference_period -- not merely the single requested
    modelled_date. Module-boundary invariant (3): a value whose interval
    starts partway through the reference period, or ends before it, must
    not be treated as a verified full-year rate even though it covers one
    requested `modelled_date`."""
    if value_effective_from > reference_period.from_:
        return False
    return value_effective_to is None or value_effective_to >= reference_period.to


def _wff_module_validation_failure(
    policy_dir: Path, modelled_date: date, parameters: PolicyParameterSet
) -> ComponentResult | None:
    """The three Task 20 module-specific `validation_checks`, in addition
    to the schema-version/approval-status gates `load_policy_parameters()`
    already enforced by the time this runs. Returns the shared
    `needs_review` result to use for all four `WffResult` components, or
    `None` if every invariant holds.
    """
    spec = load_policy_spec(policy_dir / "policy.yaml")
    reference_period = spec.reference_period

    # Invariant (2): the loaded parameter set is actually for this module,
    # not an unrelated or stale one -- a caller-supplied policy_dir
    # resolving to a different policy_id would otherwise silently run WFF
    # arithmetic against, say, Accommodation Supplement's parameters.
    if parameters.policy_id != _WFF_MODULE_ID:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"loaded policy_id '{parameters.policy_id}' does not match the "
                f"'{_WFF_MODULE_ID}' module -- a mismatched or foreign parameter set"
            ),
        )

    # Invariant (2b): every parameter calculate_wff() might look up is
    # actually declared by this policy.yaml -- a policy.yaml that omits
    # one (e.g. an incomplete or malformed authoring pass) must not reach
    # calculate_wff() and crash with KeyError partway through a component;
    # it must resolve to the same needs_review contract every other
    # module-boundary failure does (PR #21 review finding).
    missing_parameter_ids = sorted(_WFF_REQUIRED_PARAMETER_IDS - parameters.resolutions.keys())
    if missing_parameter_ids:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"policy '{parameters.policy_id}' does not declare required parameter(s) "
                f"{missing_parameter_ids} -- calculate_wff() cannot run against an incomplete "
                "parameter set"
            ),
        )

    # Invariant (1): the requested date actually falls within the period
    # this policy version was reviewed to cover, not merely within some
    # individual parameter's own interval.
    if not _covers(reference_period.from_, reference_period.to, modelled_date):
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"modelled_date {modelled_date} is outside policy '{parameters.policy_id}''s "
                f"reviewed reference_period [{reference_period.from_}, {reference_period.to})"
            ),
        )

    # Invariant (3): every parameter this calculation could draw on is
    # rate-covered for the *complete* reference period, not just resolved
    # for the single requested modelled_date.
    for param in spec.parameters:
        resolution = parameters.get(param.id)
        if resolution.outcome != "resolved":
            # Already needs_review/unsupported for its own reason (e.g.
            # in_work_base's live rate-status gate) -- nothing this
            # invariant would add.
            continue
        matching_value = next(
            (v for v in param.values if _covers(v.effective_from, v.effective_to, modelled_date)),
            None,
        )
        assert matching_value is not None, (
            f"parameter '{param.id}' resolved for {modelled_date} but no matching interval "
            "found on re-check -- load_policy_parameters()/load_policy_spec() disagree"
        )
        if not _spans_reference_period(matching_value.effective_from, matching_value.effective_to, reference_period):
            return ComponentResult(
                outcome="needs_review",
                reason=(
                    f"parameter '{param.id}' value effective {matching_value.effective_from}"
                    f"-{matching_value.effective_to} covers the requested {modelled_date} but "
                    f"does not span the complete reference period {reference_period.from_}-"
                    f"{reference_period.to} -- a point-in-time match cannot verify a full-year "
                    "rate"
                ),
            )

    return None


def run_wff_module(
    policy_dir: Path,
    modelled_date: date,
    scenario: WffScenario,
    *,
    requested_policy_version: str,
) -> WffResult:
    """Task 20: the WFF module's integration entry point.

    Combines Task 11's `load_policy_parameters()` and this file's own
    `calculate_wff()` behind one call, enforcing the module contract's
    `validation_checks` before any component is calculated.

    `requested_policy_version` is a required keyword argument, not an
    optional one -- module identity has two halves, `policy_id` (checked
    unconditionally against `_WFF_MODULE_ID` below) and `policy_version`
    (checked by `load_policy_parameters()`, but only when a caller
    actually supplies a version to check against). An optional parameter
    defaulting to `None` would let a caller silently skip the version half
    of that guarantee by omission -- exactly the gap the "annual module
    needs an explicit version-selection contract" review finding named
    (PR #21). Every integration caller must state which `policy_version`
    it was built against; there is no implicit "whatever's in the
    directory" fallback.

    A schema-version, approval-status, or requested/actual `policy_version`
    mismatch still raises exactly as `load_policy_parameters()` already
    does (unchanged, caller-level structural errors) -- only the
    module-specific invariants above resolve to `needs_review` rather than
    raising, consistent with this module's existing "never a silent zero,
    always a reason" discipline.

    No cross-module `dependencies` -- WFF v0.1 is single-module
    integration (ARCHITECTURE.md's Simulation module contract explicitly
    notes cross-module dependencies are v0.3's job, not this task's).
    """
    parameters = load_policy_parameters(
        policy_dir, modelled_date, requested_policy_version=requested_policy_version
    )

    validation_failure = _wff_module_validation_failure(policy_dir, modelled_date, parameters)
    if validation_failure is not None:
        # No component ran, so the trace carries only the policy identity
        # and artifact hashes; the reason says which invariant failed.
        return WffResult(
            **{
                component_id: replace(
                    validation_failure,
                    trace=ComponentTrace(component_id=component_id, **trace_header(parameters, scenario)),
                )
                for component_id in _WFF_COMPONENT_IDS
            }
        )

    return calculate_wff(scenario, parameters)
