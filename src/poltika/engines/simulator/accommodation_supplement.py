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
from datetime import date
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
from poltika.semantics.schemas.policy_spec import ReferencePeriod


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
    """Schedule 4 Part 7 cl 1-3 (rent/board, 25%-of-base-rate entry
    threshold) is the v0.1 supported branch; cl 4-6 (homeowner, 30%,
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
    For AS, an undeclared parameter is the *normal, expected* v0.1 state
    right now: Task 22 deliberately left the claimant-category base rates
    and the r 18(3) income level undeclared, pending Task 24's independent
    recalculation of the dated MSD tables they come from (see
    `policy.yaml`'s own comment above `parameters:`). A bare `KeyError`
    against the real, approved `policy.yaml` would be the wrong failure
    mode for an intentional, documented gap.
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


def _base_rate_parameter_id(
    claimant_category: ClaimantCategory, household_category: _HouseholdCategory
) -> str:
    """Task 25/26: the compound-ID convention for the claimant-category
    base rate, extended to also carry the household-category dimension --
    mirroring `_area_cap_parameter_id()`'s already-established
    `<primary>_<household_category>_<...>` pattern rather than introducing
    a new one.

    Task 24.1's independent verification pass found that MSD's dated rate
    tables select the base rate (and its derived 25%-of-base-rate entry
    threshold) by claimant category *and* household category together --
    e.g. Supported Living Payment has separate single/couple/parent
    thresholds -- while Task 23's original `as_base_rate_<claimant_
    category>` parameter id had no room for that second dimension. Task
    25's schema stress-test concluded the `ParameterSpec`/`PolicySpec`
    Pydantic schema itself needs no revision for this (`id` is already a
    free-form string, and the compound-id pattern already works for area
    caps) -- only this naming convention needed extending, which is what
    this function does. No real values are populated under either the old
    or the new id yet (`as_base_rate_*` remains entirely undeclared,
    Task 22/23's documented gap, pending Task 24's independent
    recalculation of the dated MSD tables) -- this changes what string id
    is looked up, not any approved numeric fact.
    """
    return f"as_base_rate_{claimant_category.value}_{household_category.value}"


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

    # --- needs_review: the three facts the r 15 assets-ceiling check below
    # itself depends on, checked first so that check can run at all ---
    if scenario.cash_assets is None:
        return ComponentResult(outcome="needs_review", reason="cash_assets unverified")
    if scenario.partner_status is None:
        return ComponentResult(outcome="needs_review", reason="partner_status unverified")
    if scenario.dependent_children_count is None:
        return ComponentResult(outcome="needs_review", reason="dependent_children_count unverified")

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
            for parameter_id, rule in _AS_CALCULATION_RULES
            if parameter_id is None or parameter_id in parameter_ids
        )
        decisions = tuple(
            decision for parameter_id, decision in _AS_DECISIONS if parameter_id in parameter_ids
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


# Task 31: the rounding rules a `calculated` result's path applies. A rule
# keyed by a parameter id is attached only when that parameter was consulted
# (its formula step was reached); `None` means every calculated path. The
# wording restates this file's own implementation comments below.
_AS_CALCULATION_RULES: tuple[tuple[str | None, str], ...] = (
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
_AS_DECISIONS: tuple[tuple[str, str], ...] = (("income_reduction_rate", "DEC-001"),)


def _accommodation_supplement(scenario: AsScenario, parameters: PolicyParameterSet) -> ComponentResult:
    """The calculation itself, unchanged from Task 23 -- see
    `calculate_accommodation_supplement()` for the contract."""
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

    # Household category is needed for both the base rate (Task 25/26's
    # compound-id fix) and the area cap below -- computed once, up front.
    household_category = _household_category(scenario.partner_status, scenario.dependent_children_count)

    # Step 3: entry threshold = 25% of the claimant's base rate.
    entry_threshold_fraction = _param_value(parameters, "entry_threshold_rent_board_fraction")
    if isinstance(entry_threshold_fraction, ComponentResult):
        return entry_threshold_fraction
    base_rate_id = _base_rate_parameter_id(scenario.claimant_category, household_category)
    base_rate = _param_value(parameters, base_rate_id)
    if isinstance(base_rate, ComponentResult):
        return base_rate
    entry_threshold = entry_threshold_fraction * base_rate

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
        income_level = _param_value(
            parameters, f"as_income_level_{scenario.claimant_category.value}"
        )
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


def _spans_reference_period(
    value_effective_from: date, value_effective_to: date | None, reference_period: ReferencePeriod
) -> bool:
    """Whether a parameter value's effective interval fully contains the
    policy's reference_period -- not merely the single requested
    modelled_date. Mirrors `wff.py`'s `_spans_reference_period()` exactly
    (Task 19/20's module-boundary invariant (3), now applied to AS)."""
    if value_effective_from > reference_period.from_:
        return False
    return value_effective_to is None or value_effective_to >= reference_period.to


def _as_module_validation_failure(
    policy_dir: Path, modelled_date: date, parameters: PolicyParameterSet
) -> ComponentResult | None:
    """The module-boundary invariants Task 20 established for WFF's
    `run_wff_module()`, applied to AS. Returns the shared `needs_review`
    result to use for the single `accommodation_supplement` component, or
    `None` if every invariant holds.

    Unlike `_wff_module_validation_failure()`, there is no separate
    "every parameter calculate_wff() might look up is declared" check
    here -- that invariant exists for WFF because an undeclared required
    parameter was always a malformed-fixture bug (PR #21 review finding).
    For AS, `calculate_accommodation_supplement()`'s own `_param_value()`
    helper already resolves an undeclared parameter to `needs_review`
    directly (Task 23's documented design: an undeclared parameter is AS's
    normal, expected v0.1 state right now, not a fixture bug) -- adding the
    same check here would be redundant, not defensive.
    """
    spec = load_policy_spec(policy_dir / "policy.yaml")
    reference_period = spec.reference_period

    # Invariant: the loaded parameter set is actually for this module, not
    # an unrelated or stale one -- a caller-supplied policy_dir resolving
    # to a different policy_id would otherwise silently run AS arithmetic
    # against, say, Working for Families' parameters.
    if parameters.policy_id != _AS_MODULE_ID:
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"loaded policy_id '{parameters.policy_id}' does not match the "
                f"'{_AS_MODULE_ID}' module -- a mismatched or foreign parameter set"
            ),
        )

    # Invariant: the requested date actually falls within the period this
    # policy version was reviewed to cover, not merely within some
    # individual parameter's own interval.
    if not _covers(reference_period.from_, reference_period.to, modelled_date):
        return ComponentResult(
            outcome="needs_review",
            reason=(
                f"modelled_date {modelled_date} is outside policy '{parameters.policy_id}''s "
                f"reviewed reference_period [{reference_period.from_}, {reference_period.to})"
            ),
        )

    # Invariant: every parameter actually declared in policy.yaml is
    # rate-covered for the *complete* reference period, not just resolved
    # for the single requested modelled_date. Iterated generically over
    # `spec.parameters` -- never hardcoded to AS's specific parameter ids,
    # the same discipline `_wff_module_validation_failure()` follows.
    for param in spec.parameters:
        resolution = parameters.get(param.id)
        if resolution.outcome != "resolved":
            # Already needs_review/unsupported for its own reason --
            # nothing this invariant would add.
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


def run_as_module(
    policy_dir: Path,
    modelled_date: date,
    scenario: AsScenario,
    *,
    requested_policy_version: str,
) -> ComponentResult:
    """Task 24.7: the Accommodation Supplement module's integration entry
    point, mirroring `wff.py`'s `run_wff_module()` (Task 20) for AS's
    single-component shape.

    Combines Task 11's `load_policy_parameters()` and this file's own
    `calculate_accommodation_supplement()` behind one call, enforcing the
    module contract's `validation_checks` before the component is
    calculated.

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

    validation_failure = _as_module_validation_failure(policy_dir, modelled_date, parameters)
    if validation_failure is not None:
        # No calculation ran, so the trace carries only the policy identity
        # and artifact hashes; the reason says which invariant failed.
        return replace(
            validation_failure,
            trace=ComponentTrace(component_id=_AS_MODULE_ID, **trace_header(parameters, scenario)),
        )

    return calculate_accommodation_supplement(scenario, parameters)
