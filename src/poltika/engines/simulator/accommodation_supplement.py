"""Task 23: the pure `calculate_accommodation_supplement()` function.

Implements the "Approved Task 22 scoped calculation contract" in
`policy_specs/accommodation_supplement/specification.md` (accepted by Pete,
Task 22 acceptance, `policy_version: "0.1.0"`) against a `PolicyParameterSet`
produced by Task 11's loader. Deterministic: canonical scenario facts +
resolved policy parameters in, one component outcome + reason out. No I/O,
no network, no LLM call -- same discipline as `wff.py`'s `calculate_wff()`,
which this module deliberately mirrors rather than reinventing.

This module deliberately does not attempt every AS rule in the Social
Security Act/Regulations -- only the narrow v0.1 supported domain Pete
accepted at Task 22: one claimant or an ordinary (non-joint-tenancy,
non-community-spouse) couple, rent/contributions/board tenure only (no
homeowner costs), Jobseeker Support/Sole Parent Support/Supported Living
Payment/non-beneficiary claimant categories (no NZ Superannuation/Veteran's
Pension, no mixed-benefit couple), the plain-case weekly qualifying
accommodation costs formula (no boarder/sub-let accommodation income, no
business-use deduction). Anything outside that domain must resolve to
`unsupported` or `needs_review`, never a silent zero or a guessed number
(CLAUDE.md's "Ground truth" section).

`ComponentResult`, `ComponentOutcome`, and `FactStatus` are imported from
`wff.py` rather than duplicated -- both types are already fully
policy-agnostic (outcome/value/reason; verified/excluded/unknown), and
Architecture Doctrine's "minimum abstraction demanded by two real
policies" is exactly satisfied now that a second policy needs them. This
is a plain import, not a refactor of `wff.py` -- no existing WFF code or
test changes. AS-specific enums (`ClaimantCategory`, `TenureType`,
`PartnerType`, `Area`) are defined here, not shared, since WFF has no
equivalent concepts.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from enum import Enum
from pathlib import Path

from poltika.engines.simulator.trace import (
    ComponentTrace,
    input_uses,
    parameter_uses,
    recording_copy,
    recording_parameters,
    trace_header,
)
from poltika.engines.simulator.wff import ComponentResult, FactStatus
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters, load_policy_spec


class ClaimantCategory(str, Enum):
    """r 18(1)(b)'s income-reduction route applies only to a
    non-beneficiary (r 18, r 17's definition) -- Jobseeker Support, Sole
    Parent Support, and Supported Living Payment claimants have no
    separate AS income test at all (AS-08). NZ Superannuation/Veteran's
    Pension (a different s 67(e)/Schedule 5 income-*limit* exclusion
    route) and a mixed-benefit couple (a separate half-married rate
    table) are unsupported in this branch -- listed here so an unverified
    or unsupported category is a structural fact, not an inferred default.
    """

    JOBSEEKER_SUPPORT = "jobseeker_support"
    SOLE_PARENT_SUPPORT = "sole_parent_support"
    SUPPORTED_LIVING_PAYMENT = "supported_living_payment"
    NON_BENEFICIARY = "non_beneficiary"
    PENSION_OR_VETERANS = "pension_or_veterans"
    MIXED_BENEFIT_COUPLE = "mixed_benefit_couple"


class TenureType(str, Enum):
    """Schedule 4 Part 7 cl 1-3 (rent/board; the published rent/board entry
    threshold per DEC-002) is the v0.1 supported branch; cl 4-6 (homeowner,
    mortgage-security "reasonably required" MSD judgment) is not."""

    RENT_CONTRIBUTIONS_OR_BOARD = "rent_contributions_or_board"
    HOMEOWNER = "homeowner"


class PartnerType(str, Enum):
    """Joint tenancy (s 68) and community spouse/partner (Schedule 4 Part
    7 cl 6A) are both "couple" cases with their own special statutory
    treatment this branch does not model -- distinct from an ordinary
    couple, not a subset of it."""

    SINGLE = "single"
    ORDINARY_COUPLE = "ordinary_couple"
    JOINT_TENANCY = "joint_tenancy"
    COMMUNITY_SPOUSE_OR_PARTNER = "community_spouse_or_partner"


class Area(str, Enum):
    """A verified Statistical Area Unit resolved to Area 1-4
    (`as-msd-areas`). Never inferred from a suburb/city name; never
    silently defaulted to Area 4 -- there is deliberately no default
    member here at all."""

    AREA_1 = "area1"
    AREA_2 = "area2"
    AREA_3 = "area3"
    AREA_4 = "area4"


class _HouseholdCategory(str, Enum):
    """Internal: which of Schedule 4 Part 7 cl 1/2/3's three household
    categories applies, derived from `partner_status` and
    `dependent_children_count` -- not itself a scenario input."""

    WITH_DEPENDENT_CHILDREN = "with_dependent_children"
    NO_DEPENDENT_CHILDREN_COUPLE_OR_SOLE_PARENT_ONE_CHILD = (
        "no_dependent_children_couple_or_sole_parent_one_child"
    )
    SINGLE_NO_DEPENDENT_CHILDREN = "single_no_dependent_children"


class _RateHousehold(str, Enum):
    """Internal: the household row of MSD's published entry-threshold and
    income-level tables (DEC-002; specification.md's "Task 26a selector and
    threshold repair"). Deliberately separate from `_HouseholdCategory`,
    the Schedule 4 Part 7 cl 1-3 cap grouping: the tables split households
    differently -- e.g. a childless couple and a sole parent with one child
    share a cap row but not a threshold row (PR #46 finding). Derived from
    verified `partner_status` and `dependent_children_count`; never a
    caller-selected input."""

    SINGLE_NO_DEPENDENT_CHILDREN = "single_no_dependent_children"
    SOLE_PARENT = "sole_parent"
    COUPLE_NO_DEPENDENT_CHILDREN = "couple_no_dependent_children"
    COUPLE_WITH_DEPENDENT_CHILDREN = "couple_with_dependent_children"


@dataclass(frozen=True)
class AsScenario:
    """The v0.1 supported-domain scenario facts
    `calculate_accommodation_supplement()` accepts. Every field traces to
    a named input in `policy_specs/accommodation_supplement/policy.yaml`'s
    `inputs` list. Fields are canonical Poltika facts, already resolved
    from whatever upstream source supplied them -- this module never
    reads a raw source itself (REPOSITORY_STRUCTURE.md's dependency
    boundary).
    """

    # policy.yaml's `household_eligibility_facts` input: bundles the
    # social housing exclusion (s 66), every other-funding exclusion
    # paragraph this branch cares about including s 67(b) Student
    # Allowance and s 67(d) disability/care (s 67), and s 69 discretionary
    # refusal/reduction/cancellation grounds into one opaque household-
    # level fact, matching WFF's own `eligibility_facts` bundling
    # convention -- policy.yaml declares exactly one input for this
    # bundle, not four separate ones.
    household_eligibility: FactStatus

    # `None` means unverified (needs_review); the two unsupported values
    # are real, evidenced facts, not a scope limitation to guess around.
    claimant_category: ClaimantCategory | None = None
    tenure_type: TenureType | None = None
    partner_status: PartnerType | None = None
    statistical_area_unit: Area | None = None

    # policy.yaml's `weekly_accommodation_costs` input -- the plain-case
    # formula only (no accommodation income, no business-use deduction;
    # a claimant with either is unsupported, per
    # `accommodation_income_or_business_use_qualifying_costs` below).
    weekly_accommodation_costs: Decimal | None = None

    dependent_children_count: int | None = None

    # policy.yaml's `cash_assets` input (a stock amount, not a rate).
    cash_assets: Decimal | None = None
    # r 16/Schedule 8 Part 1 exempt-asset determination is not modelled in
    # this branch at all (specification.md: "exemptions must be verified,
    # not assumed absent") -- VERIFIED means verified that no exemption
    # applies (the plain `cash_assets` figure is trustworthy as given);
    # both EXCLUDED (an exemption verified to apply) and UNKNOWN
    # (unverified either way) are `unsupported`, not `needs_review` --
    # this branch does not attempt exemption determination at all, unlike
    # an ordinary unverified fact.
    exempt_cash_asset_status: FactStatus = FactStatus.UNKNOWN

    # Required only for the non-beneficiary r 18 income-reduction route
    # (policy.yaml: `required_for: accommodation_supplement`, but only
    # reached when claimant_category == NON_BENEFICIARY); combined weekly
    # income of claimant and partner, before the s 423(3) asset-imputation
    # addition (r 18(2A)).
    weekly_income: Decimal | None = None

    # Task 26a repair (specification.md, DEC-002): the ordinary published
    # rate row applies for the whole week -- no protected Jobseeker
    # woman-alone rate, mixed-benefit rate, special care/residential rate or
    # other unrepresented subtype. For a single beneficiary under 25,
    # VERIFIED includes applicability of r 17(2)(a)'s age-25 rate. EXCLUDED
    # (a known subtype outside this branch) is unsupported; UNKNOWN is
    # needs_review. General household eligibility does not imply it.
    ordinary_rate_status: FactStatus = FactStatus.UNKNOWN

    # Parent rows only (one or more dependent children): the eldest
    # qualifying dependent child is under 16 throughout the week. A
    # conservative scope restriction, not a finding that older-child
    # households lack entitlement. Not consulted when the count is zero.
    eldest_dependent_child_under_16: FactStatus = FactStatus.UNKNOWN

    def __post_init__(self) -> None:
        if self.weekly_accommodation_costs is not None and self.weekly_accommodation_costs < 0:
            raise ValueError(
                "AsScenario.weekly_accommodation_costs must not be negative, got "
                f"{self.weekly_accommodation_costs}"
            )
        if self.cash_assets is not None and self.cash_assets < 0:
            raise ValueError(f"AsScenario.cash_assets must not be negative, got {self.cash_assets}")
        if self.weekly_income is not None and self.weekly_income < 0:
            raise ValueError(f"AsScenario.weekly_income must not be negative, got {self.weekly_income}")
        if self.dependent_children_count is not None and self.dependent_children_count < 0:
            raise ValueError(
                "AsScenario.dependent_children_count must not be negative, got "
                f"{self.dependent_children_count}"
            )


def _param_value(parameters: PolicyParameterSet, parameter_id: str) -> ComponentResult | Decimal:
    """Looks up one resolved parameter. Returns its `Decimal` value if
    resolved, or the `ComponentResult` to use verbatim if it isn't --
    callers propagate that result rather than proceeding.

    Unlike `wff.py`'s equivalent helper, this also treats a parameter
    that is not *declared* in `policy.yaml` at all as `needs_review`
    rather than letting `PolicyParameterSet.get()` raise `KeyError`. For
    WFF, an undeclared required parameter was always a malformed-fixture
    bug (PR #21) -- every real parameter has been declared since Task 10.
    For AS, an undeclared parameter is an expected state: the published
    entry thresholds and income levels (Task 26a repair, DEC-002) are
    declared only for supported rows, and until Task 26a.2 populates them
    none is declared (see `policy.yaml`'s comment above `parameters:`). A
    bare `KeyError` would be the wrong failure mode for an intentional,
    documented gap.
    """
    if parameter_id not in parameters.resolutions:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"parameter '{parameter_id}' is not yet declared in policy "
                f"'{parameters.policy_id}' -- pending independent recalculation "
                "of its dated source table (Task 24)"
            ),
        )
    resolution = parameters.get(parameter_id)
    if resolution.outcome != "resolved":
        assert resolution.outcome in ("needs_review", "unsupported")
        return ComponentResult(
            outcome=resolution.outcome,
            reason=resolution.reason or f"parameter '{parameter_id}' is {resolution.outcome}",
        )
    assert resolution.value is not None
    return resolution.value


def _household_category(
    partner_status: PartnerType, dependent_children_count: int
) -> _HouseholdCategory:
    is_couple = partner_status == PartnerType.ORDINARY_COUPLE
    if is_couple:
        if dependent_children_count >= 1:
            return _HouseholdCategory.WITH_DEPENDENT_CHILDREN
        return _HouseholdCategory.NO_DEPENDENT_CHILDREN_COUPLE_OR_SOLE_PARENT_ONE_CHILD
    # Single claimant: a sole parent with 2+ dependent children falls in
    # the same cl 1 bucket as a couple with 1+; a sole parent with exactly
    # 1 child shares cl 2 with a childless couple; a single claimant with
    # no dependent children is cl 3's "any other person".
    #
    # Self-review flag (author preflight, not independently verified):
    # this treats every SINGLE claimant with dependent_children_count >= 1
    # as a "sole parent" for Schedule 4 Part 7 cl 1/2 purposes -- the v0.1
    # PartnerType/dependent_children_count input contract has no separate
    # "sole parent" fact distinct from "single + has children". This is a
    # reasonable reading (sole parent ordinarily means a single caregiver
    # with dependent children in NZ benefit law) but is an implicit
    # modelling assumption, not something specification.md's contract
    # states as its own named input -- flag for the reviewer, don't take
    # it as settled.
    if dependent_children_count >= 2:
        return _HouseholdCategory.WITH_DEPENDENT_CHILDREN
    if dependent_children_count == 1:
        return _HouseholdCategory.NO_DEPENDENT_CHILDREN_COUPLE_OR_SOLE_PARENT_ONE_CHILD
    return _HouseholdCategory.SINGLE_NO_DEPENDENT_CHILDREN


def _asset_ceiling_parameter_id(partner_status: PartnerType, dependent_children_count: int) -> str:
    # r 15(1)(a): a person in a relationship, OR a single person with 1+
    # dependent children -- $16,200. r 15(1)(b): any other case -- $8,100.
    if partner_status == PartnerType.ORDINARY_COUPLE or dependent_children_count >= 1:
        return "asset_ceiling_relationship_or_dependent_children"
    return "asset_ceiling_other"


def _asset_imputation_threshold_parameter_id(
    partner_status: PartnerType, dependent_children_count: int
) -> str:
    # s 423(3)(a)/(b) use the identical relationship-or-dependent-child
    # split as r 15(1)(a)/(b).
    if partner_status == PartnerType.ORDINARY_COUPLE or dependent_children_count >= 1:
        return "asset_imputation_threshold_relationship_or_dependent_children"
    return "asset_imputation_threshold_other"


def _area_cap_parameter_id(household_category: _HouseholdCategory, area: Area) -> str:
    return f"area_cap_{household_category.value}_{area.value}"


def _rate_household(partner_status: PartnerType, dependent_children_count: int) -> _RateHousehold:
    """The published-table household row (specification.md's Task 26a
    repair). Unlike `_household_category()`, a sole parent's row does not
    change with a second child, and a couple's row does."""
    if partner_status == PartnerType.ORDINARY_COUPLE:
        if dependent_children_count >= 1:
            return _RateHousehold.COUPLE_WITH_DEPENDENT_CHILDREN
        return _RateHousehold.COUPLE_NO_DEPENDENT_CHILDREN
    if dependent_children_count >= 1:
        return _RateHousehold.SOLE_PARENT
    return _RateHousehold.SINGLE_NO_DEPENDENT_CHILDREN


def _entry_threshold_parameter_id(claimant_category: ClaimantCategory, rate_household: _RateHousehold) -> str:
    """The published rent/board entry threshold, NZD per week, subtracted
    directly from qualifying costs (DEC-002). Replaces the Task 25/26
    `as_base_rate_<claimant>_<cap household>` id, which conflated distinct
    table rows (SPEC_ERROR, PR #46); there is no fallback to it."""
    return f"as_entry_threshold_{claimant_category.value}_{rate_household.value}"


def _income_level_parameter_id(rate_household: _RateHousehold) -> str:
    """r 18(3) sets the non-beneficiary income level by household; the
    published income-threshold column supplies it (DEC-002). There is no
    claimant-only fallback id."""
    return f"as_income_level_non_beneficiary_{rate_household.value}"


def _household_gate_failure(
    scenario: AsScenario, parameters: PolicyParameterSet
) -> ComponentResult | None:
    """Checks that apply before any calculation step. Returns the shared
    failure result, or `None` if the household may proceed. `unsupported`
    (a known structural exclusion) takes precedence over `needs_review`
    (an unverified fact) when both are present, matching `wff.py`'s
    `_household_gate_failure()` precedence discipline -- including the r 15
    assets-ceiling exclusion below, which (unlike every other check here)
    needs `parameters` as well as `scenario`: it cannot be evaluated at all
    until `cash_assets`, `partner_status`, and `dependent_children_count`
    are known and the ceiling parameter itself resolves. Those three facts'
    own `needs_review` checks therefore run immediately before the ceiling
    check, ahead of every other `needs_review` trigger in this gate -- not
    because they matter more, but because the ceiling check has no way to
    run without them (Task 24.4 review finding: the ceiling check
    previously lived entirely outside this function, after it returned
    `None`, so it could never actually pre-empt an unrelated `needs_review`
    trigger the way this docstring already claimed it did).
    """
    # --- unsupported / EXCLUDED conditions first ---
    if scenario.household_eligibility == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason=(
                "household_eligibility_facts verified outside the v0.1 domain "
                "(social housing exclusion s 66, an other-funding exclusion "
                "under s 67 including the Student Allowance or disability/care "
                "branches, or an applicable s 69 discretionary ground)"
            ),
        )
    if scenario.claimant_category in (
        ClaimantCategory.PENSION_OR_VETERANS,
        ClaimantCategory.MIXED_BENEFIT_COUPLE,
    ):
        return ComponentResult(
            outcome="unsupported",
            reason=(
                f"claimant category '{scenario.claimant_category.value}' is outside the "
                "v0.1 supported categories (Jobseeker Support, Sole Parent Support, "
                "Supported Living Payment, non-beneficiary)"
            ),
        )
    if scenario.tenure_type == TenureType.HOMEOWNER:
        return ComponentResult(
            outcome="unsupported",
            reason="homeowner accommodation costs (Schedule 4 Part 7 cl 4-6) are outside the v0.1 rent/board-only branch",
        )
    if scenario.partner_status in (
        PartnerType.JOINT_TENANCY,
        PartnerType.COMMUNITY_SPOUSE_OR_PARTNER,
    ):
        return ComponentResult(
            outcome="unsupported",
            reason=(
                f"partner status '{scenario.partner_status.value}' (joint tenancy s 68, or "
                "community spouse/partner Schedule 4 Part 7 cl 6A) needs its own "
                "specification, not the ordinary single-or-couple branch"
            ),
        )
    if scenario.ordinary_rate_status == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason=(
                "a rate subtype outside the ordinary published row applies (e.g. the protected "
                "Jobseeker woman-alone rate, a mixed-benefit or special care/residential rate) -- "
                "not modelled in this branch (DEC-002)"
            ),
        )
    if scenario.exempt_cash_asset_status != FactStatus.VERIFIED:
        # Self-review flag (author preflight): this maps BOTH EXCLUDED
        # (an exemption verified to apply) AND UNKNOWN (unverified either
        # way) to unsupported -- deliberately, per specification.md's "not
        # modelled in this branch... exemptions must be verified, not
        # assumed absent" (this branch attempts no exemption determination
        # at all, so an unverified status is equally out of scope, not
        # merely an unresolved fact). This deviates from every other
        # UNKNOWN check in this file (and from wff.py's convention), which
        # map UNKNOWN to needs_review, not unsupported -- a reviewer
        # should treat this as a specific, considered exception, not an
        # accidental inconsistency, and confirm the reading holds.
        return ComponentResult(
            outcome="unsupported",
            reason=(
                "an exempt cash asset (r 16, Schedule 8 Part 1) is not modelled in this "
                "branch -- exemptions must be verified, not assumed absent, and this "
                "branch does not attempt exemption determination"
            ),
        )

    # --- needs_review: partner status and child count, which the unsupported
    # checks immediately below and the r 15 ceiling check both depend on ---
    if scenario.partner_status is None:
        return ComponentResult(outcome="needs_review", reason="partner_status unverified")
    if scenario.dependent_children_count is None:
        return ComponentResult(outcome="needs_review", reason="dependent_children_count unverified")

    # --- unsupported conditions that need partner status and child count.
    # They run before the cash_assets check, which they do not need, so a
    # known outside-domain case is never hidden behind an unrelated
    # unverified fact (PR #50 fresh-context review). ---
    if scenario.claimant_category == ClaimantCategory.SOLE_PARENT_SUPPORT and not (
        scenario.partner_status == PartnerType.SINGLE and scenario.dependent_children_count >= 1
    ):
        return ComponentResult(
            outcome="unsupported",
            reason=(
                "Sole Parent Support with a partner or without a dependent child has no published "
                "ordinary rate row in this branch (DEC-002)"
            ),
        )
    if scenario.dependent_children_count >= 1 and scenario.eldest_dependent_child_under_16 == FactStatus.EXCLUDED:
        return ComponentResult(
            outcome="unsupported",
            reason=(
                "the eldest dependent child is not under 16 throughout the week -- outside this "
                "branch's parent rows (a scope restriction, not a finding of no entitlement; DEC-002)"
            ),
        )

    # --- needs_review: the last fact the r 15 ceiling check needs ---
    if scenario.cash_assets is None:
        return ComponentResult(outcome="needs_review", reason="cash_assets unverified")

    # --- assets requirement (r 15): a genuine, evidenced exclusion, not a
    # scope limitation -- evaluated as soon as the facts above make it
    # possible, so it can actually pre-empt every needs_review trigger
    # below, not just the ones textually after it.
    ceiling_id = _asset_ceiling_parameter_id(scenario.partner_status, scenario.dependent_children_count)
    ceiling = _param_value(parameters, ceiling_id)
    if isinstance(ceiling, ComponentResult):
        return ceiling
    if scenario.cash_assets >= ceiling:
        return ComponentResult(
            outcome="unsupported",
            reason=(
                f"cash assets ({scenario.cash_assets}) meet or exceed the r 15 ceiling "
                f"({ceiling}) -- the assets requirement (r 15) fails"
            ),
        )

    # --- remaining needs_review / unverified conditions ---
    if scenario.household_eligibility == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review",
            reason="household_eligibility_facts (social housing, other-funding, s 69 grounds) unverified",
        )
    if scenario.claimant_category is None:
        return ComponentResult(outcome="needs_review", reason="claimant_category unverified")
    if scenario.ordinary_rate_status == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review",
            reason="ordinary_rate_status unverified -- the ordinary published rate row is not established",
        )
    if scenario.dependent_children_count >= 1 and scenario.eldest_dependent_child_under_16 == FactStatus.UNKNOWN:
        return ComponentResult(
            outcome="needs_review",
            reason="eldest_dependent_child_under_16 unverified for a parent rate row",
        )
    if scenario.tenure_type is None:
        return ComponentResult(outcome="needs_review", reason="tenure_type unverified")
    if scenario.statistical_area_unit is None:
        return ComponentResult(
            outcome="needs_review",
            reason="statistical_area_unit unverified -- never defaulted to Area 4",
        )
    if scenario.weekly_accommodation_costs is None:
        return ComponentResult(outcome="needs_review", reason="weekly_accommodation_costs unverified")

    return None


def calculate_accommodation_supplement(
    scenario: AsScenario, parameters: PolicyParameterSet
) -> ComponentResult:
    """Task 23: the pure AS calculator.

    `parameters` must already be resolved for the modelled date by Task
    11's `load_policy_parameters()` -- this function performs no date
    arithmetic of its own and makes no network or file access. Returns
    the single `accommodation_supplement` component's outcome; unlike
    WFF's four components, AS has exactly one.

    The result carries a `ComponentTrace` (Task 31) recording the
    parameters and scenario facts consulted. Recording wraps the
    calculation; `_accommodation_supplement()` itself is unchanged.
    """
    recorded_scenario, input_names = recording_copy(scenario)
    recorded_parameters, parameter_ids = recording_parameters(parameters)
    result = _accommodation_supplement(recorded_scenario, recorded_parameters)

    rules: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    if result.outcome == "calculated":
        rules = tuple(
            rule
            for prefix, rule in _AS_CALCULATION_RULES
            if prefix is None or any(parameter_id.startswith(prefix) for parameter_id in parameter_ids)
        )
        decisions = tuple(
            dict.fromkeys(
                decision
                for prefix, decision in _AS_DECISIONS
                if any(parameter_id.startswith(prefix) for parameter_id in parameter_ids)
            )
        )
    return replace(
        result,
        trace=ComponentTrace(
            component_id=_AS_MODULE_ID,
            **trace_header(parameters, scenario),
            parameters=parameter_uses(parameters, parameter_ids),
            inputs=input_uses(scenario, input_names),
            calculation_rules=rules,
            decisions=decisions,
        ),
    )


# Task 31: the rules a `calculated` result's path applies. A rule keyed by a
# parameter-id prefix is attached only when a matching parameter was
# consulted (its formula step was reached); `None` means every calculated
# path. The wording restates this file's own implementation comments below.
_AS_CALCULATION_RULES: tuple[tuple[str | None, str], ...] = (
    (
        "as_entry_threshold_",
        (
            "DEC-002: the published MSD rent/board entry threshold is subtracted directly "
            "(no base rate or 25% multiplication is computed)"
        ),
    ),
    (
        "as_income_level_non_beneficiary_",
        "DEC-002: the published non-beneficiary income threshold for the household row is the r 18(3) level",
    ),
    (
        "asset_imputation_step_size",
        "s 423(3): imputed income counts only complete steps of cash assets over the threshold (floored)",
    ),
    (
        "income_reduction_rate",
        "r 18(2): the reduction rate applies to the exact, unrounded income excess (DEC-001)",
    ),
    (None, "r 19: a positive final weekly amount is rounded up to the complete dollar"),
)
_AS_DECISIONS: tuple[tuple[str, str], ...] = (
    ("as_entry_threshold_", "DEC-002"),
    ("as_income_level_non_beneficiary_", "DEC-002"),
    ("income_reduction_rate", "DEC-001"),
)


def _accommodation_supplement(scenario: AsScenario, parameters: PolicyParameterSet) -> ComponentResult:
    """The calculation itself -- see `calculate_accommodation_supplement()`
    for the contract. Step 3 and the r 18(3) income level follow the Task
    26a selector repair (specification.md, DEC-002)."""
    gate_failure = _household_gate_failure(scenario, parameters)
    if gate_failure is not None:
        return gate_failure

    # Narrowed by the gate above: every Optional field is now non-None,
    # and claimant_category/tenure_type/partner_status are confirmed
    # in-domain. mypy doesn't know that, so assert it explicitly rather
    # than silence the checker with a blind cast.
    assert scenario.claimant_category is not None
    assert scenario.tenure_type is not None
    assert scenario.partner_status is not None
    assert scenario.statistical_area_unit is not None
    assert scenario.weekly_accommodation_costs is not None
    assert scenario.dependent_children_count is not None
    assert scenario.cash_assets is not None

    zero = Decimal(0)

    # Step 2 (plain case): qualifying costs are the claimant's verified
    # weekly accommodation costs, unreduced (Schedule 4 Part 7 cl 7,
    # b = c = d = f = 0 -- accommodation income/business-use scenarios are
    # already excluded by the household gate above).
    qualifying_costs = scenario.weekly_accommodation_costs

    # Two separate household selectors (Task 26a repair): the published
    # table row for the entry threshold and income level, and the Schedule
    # 4 Part 7 cl 1-3 grouping for the cap.
    rate_household = _rate_household(scenario.partner_status, scenario.dependent_children_count)
    household_category = _household_category(scenario.partner_status, scenario.dependent_children_count)

    # Step 3: the published rent/board entry threshold, subtracted directly
    # (DEC-002) -- never a base rate multiplied by the entry fraction.
    entry_threshold = _param_value(
        parameters, _entry_threshold_parameter_id(scenario.claimant_category, rate_household)
    )
    if isinstance(entry_threshold, ComponentResult):
        return entry_threshold

    # Step 4: 70% of the positive excess, capped by household/area.
    area_cap_id = _area_cap_parameter_id(household_category, scenario.statistical_area_unit)
    area_cap = _param_value(parameters, area_cap_id)
    if isinstance(area_cap, ComponentResult):
        return area_cap

    excess = qualifying_costs - entry_threshold
    if excess <= 0:
        cost_based_amount = zero
    else:
        cost_based_amount = min(Decimal("0.7") * excess, area_cap)

    # Step 5: r 18 income reduction -- non-beneficiary route only
    # (AS-08: other supported categories have no separate AS income test).
    if scenario.claimant_category == ClaimantCategory.NON_BENEFICIARY:
        if scenario.weekly_income is None:
            return ComponentResult(
                outcome="needs_review",
                reason="weekly_income unverified -- required for the non-beneficiary income-reduction step",
            )
        income_level = _param_value(parameters, _income_level_parameter_id(rate_household))
        if isinstance(income_level, ComponentResult):
            return income_level

        imputation_threshold_id = _asset_imputation_threshold_parameter_id(
            scenario.partner_status, scenario.dependent_children_count
        )
        imputation_threshold = _param_value(parameters, imputation_threshold_id)
        if isinstance(imputation_threshold, ComponentResult):
            return imputation_threshold
        imputation_step = _param_value(parameters, "asset_imputation_step_size")
        if isinstance(imputation_step, ComponentResult):
            return imputation_step
        imputation_amount_per_step = _param_value(parameters, "asset_imputation_amount_per_step")
        if isinstance(imputation_amount_per_step, ComponentResult):
            return imputation_amount_per_step

        # s 423(3): $1 (imputation_amount_per_step) per *complete* $100
        # (imputation_step) of assets over the threshold -- floor the
        # count of complete steps, per specification.md's reading of
        # "every $100... over $X".
        asset_excess = scenario.cash_assets - imputation_threshold
        if asset_excess <= 0:
            imputed_income = zero
        else:
            complete_steps = (asset_excess / imputation_step).to_integral_value(rounding=ROUND_FLOOR)
            imputed_income = complete_steps * imputation_amount_per_step

        total_income = scenario.weekly_income + imputed_income

        income_reduction_rate = _param_value(parameters, "income_reduction_rate")
        if isinstance(income_reduction_rate, ComponentResult):
            return income_reduction_rate

        # DEC-001: apply the rate to the exact, unrounded income excess --
        # do NOT floor it to a whole dollar first.
        income_excess = total_income - income_level
        if income_excess <= 0:
            reduction = zero
        else:
            reduction = income_reduction_rate * income_excess

        pre_rounding_amount = max(zero, cost_based_amount - reduction)
    else:
        pre_rounding_amount = cost_based_amount

    # Step 6: r 19 -- round the final positive amount up to the complete
    # dollar. This is the one and only rounding step; nothing above rounds.
    if pre_rounding_amount <= 0:
        final_amount = zero
    else:
        final_amount = pre_rounding_amount.to_integral_value(rounding=ROUND_CEILING)

    return ComponentResult(outcome="calculated", value=final_amount)


_AS_MODULE_ID = "accommodation_supplement"


def _covers(value_effective_from: date, value_effective_to: date | None, target_date: date) -> bool:
    """Same interval-membership test as `wff.py`'s own `_covers()` (itself
    duplicated from `poltika.policy.loader`'s private helper) -- duplicated
    again here rather than imported across sibling simulator files, for the
    same reason: this is a small, self-contained predicate, not a shared
    abstraction two real policies are asking for."""
    if target_date < value_effective_from:
        return False
    return value_effective_to is None or target_date < value_effective_to


@dataclass(frozen=True)
class AssessmentWeek:
    """The AS assessment week a calculation is for: `[start, end)`.

    AS is assessed per week (specification.md; `policy.yaml`'s
    `assessment.membership_period: assessment_week`), so the module needs
    the week itself, not only a lookup date inside it (Task 28.2 research,
    PR #41: "a lookup date alone does not identify it"). The caller states
    both ends explicitly. No weekday convention is assumed here -- which
    week a scenario uses is a Task 28.2 decision, not something this type
    infers. The only structural rule is that a week is seven consecutive
    days.
    """

    start: date
    end: date  # exclusive

    def __post_init__(self) -> None:
        if self.end - self.start != timedelta(days=7):
            raise ValueError(
                f"AssessmentWeek must span exactly 7 days [start, end), got {self.start} to {self.end}"
            )


def _covers_week(value_effective_from: date, value_effective_to: date | None, week: AssessmentWeek) -> bool:
    """Whether a parameter value's effective interval contains the whole
    assessment week. A value that starts or ends inside the week covers
    only part of it, so it cannot be used as that week's rate."""
    if value_effective_from > week.start:
        return False
    return value_effective_to is None or value_effective_to >= week.end


def _as_module_validation_failure(
    policy_dir: Path, modelled_date: date, assessment_week: AssessmentWeek, parameters: PolicyParameterSet
) -> ComponentResult | None:
    """The AS module-boundary invariants. Returns the shared `needs_review`
    result for the single `accommodation_supplement` component, or `None`
    if every invariant holds.

    AS is assessed per week, so parameter coverage is checked against the
    assessment week, not against the policy's whole reference period. An
    earlier version (Task 24.7) copied WFF's annual rule and required every
    value to span the entire reference period, which gated a genuinely
    April-effective weekly rate for every week (CODE_ERROR found in the Task
    28.2 research, PR #41). WFF keeps its full-year rule: WFF is assessed
    per tax year.

    Unlike `_wff_module_validation_failure()`, there is no separate
    "every parameter is declared" check: `calculate_accommodation_supplement()`'s
    own `_param_value()` resolves an undeclared parameter to `needs_review`
    (Task 23's documented design).
    """
    spec = load_policy_spec(policy_dir / "policy.yaml")
    reference_period = spec.reference_period

    # The loaded parameter set is actually for this module, not an
    # unrelated or stale one.
    if parameters.policy_id != _AS_MODULE_ID:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"loaded policy_id '{parameters.policy_id}' does not match the "
                f"'{_AS_MODULE_ID}' module -- a mismatched or foreign parameter set"
            ),
        )

    # The whole week falls within the period this policy version was
    # reviewed to cover.
    if assessment_week.start < reference_period.from_ or assessment_week.end > reference_period.to:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"assessment week [{assessment_week.start}, {assessment_week.end}) is not wholly within "
                f"policy '{parameters.policy_id}''s reviewed reference_period "
                f"[{reference_period.from_}, {reference_period.to})"
            ),
        )

    # Parameters are looked up at a date inside the week they are for.
    if not _covers(assessment_week.start, assessment_week.end, modelled_date):
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"parameter lookup date {modelled_date} is outside the assessment week "
                f"[{assessment_week.start}, {assessment_week.end})"
            ),
        )

    # Every declared parameter's selected value covers the whole week.
    # Iterated generically over `spec.parameters`, never hardcoded to AS's
    # parameter ids.
    for param in spec.parameters:
        resolution = parameters.get(param.id)
        if resolution.outcome != "resolved":
            # Already needs_review/unsupported for its own reason.
            continue
        matching_value = next(
            (v for v in param.values if _covers(v.effective_from, v.effective_to, modelled_date)),
            None,
        )
        assert matching_value is not None, (
            f"parameter '{param.id}' resolved for {modelled_date} but no matching interval "
            "found on re-check -- load_policy_parameters()/load_policy_spec() disagree"
        )
        if not _covers_week(matching_value.effective_from, matching_value.effective_to, assessment_week):
            return ComponentResult(
                outcome="needs_review",
                reason=(
                    f"parameter '{param.id}' value effective {matching_value.effective_from}"
                    f"-{matching_value.effective_to} changes inside the assessment week "
                    f"[{assessment_week.start}, {assessment_week.end}) -- a value covering only "
                    "part of the week is not that week's rate"
                ),
            )

    return None


def run_as_module(
    policy_dir: Path,
    modelled_date: date,
    scenario: AsScenario,
    *,
    requested_policy_version: str,
    assessment_week: AssessmentWeek,
) -> ComponentResult:
    """Task 24.7: the Accommodation Supplement module's integration entry
    point, mirroring `wff.py`'s `run_wff_module()` (Task 20) for AS's
    single-component shape.

    Combines Task 11's `load_policy_parameters()` and this file's own
    `calculate_accommodation_supplement()` behind one call, enforcing the
    module contract's `validation_checks` before the component is
    calculated.

    `assessment_week` is required too: AS is assessed per week, and each
    parameter value used must cover the whole week (see
    `_as_module_validation_failure()`). `modelled_date` is the parameter
    lookup date and must fall inside that week. The week is recorded on the
    result's trace (`ComponentTrace.assessment_period`).

    `requested_policy_version` is a required keyword argument, not an
    optional one, for the same reason as `run_wff_module()`'s: module
    identity has two halves (`policy_id`, checked unconditionally against
    `_AS_MODULE_ID` below, and `policy_version`, checked by
    `load_policy_parameters()` whenever a caller supplies one to check
    against) -- an optional parameter defaulting to `None` would let a
    caller silently skip the version half of that guarantee by omission.

    A schema-version, approval-status, or requested/actual `policy_version`
    mismatch still raises exactly as `load_policy_parameters()` already
    does (unchanged, caller-level structural errors) -- only the
    module-specific invariants above resolve to `needs_review` rather than
    raising, consistent with `calculate_accommodation_supplement()`'s
    existing "never a silent zero, always a reason" discipline.

    No cross-module `dependencies` -- like WFF, AS v0.1 is single-module
    integration (ARCHITECTURE.md's Simulation module contract notes
    cross-module dependencies are v0.3's job, not this task's).
    """
    parameters = load_policy_parameters(
        policy_dir, modelled_date, requested_policy_version=requested_policy_version
    )

    assessment_period = (assessment_week.start, assessment_week.end)
    validation_failure = _as_module_validation_failure(policy_dir, modelled_date, assessment_week, parameters)
    if validation_failure is not None:
        # No calculation ran, so the trace carries only the run identity;
        # the reason says which invariant failed.
        return replace(
            validation_failure,
            trace=ComponentTrace(
                component_id=_AS_MODULE_ID,
                **trace_header(parameters, scenario),
                assessment_period=assessment_period,
            ),
        )

    result = calculate_accommodation_supplement(scenario, parameters)
    assert result.trace is not None
    return replace(result, trace=replace(result.trace, assessment_period=assessment_period))
