"""Task 24.2: regressions for Accommodation Supplement review findings.

Every test here traces to a concrete issue found during Tasks 22-24.1.
These are independent reproductions, not aliases for the general spec or
benchmark cases: their purpose is to make a previously observed mistake
fail under its own durable, searchable name.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    _asset_ceiling_parameter_id,
    _household_category,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.wff import FactStatus
from poltika.policy.loader import (
    ParameterResolution,
    PolicyParameterSet,
    load_policy_parameters,
)
from tests.conftest import AS_MODELLED_DATE, AS_POLICY_DIR, as_parameters_for_case


def _ordinary_as_scenario(**overrides: object) -> AsScenario:
    base: dict[str, object] = {
        "household_eligibility": FactStatus.VERIFIED,
        "claimant_category": ClaimantCategory.JOBSEEKER_SUPPORT,
        "tenure_type": TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        "partner_status": PartnerType.SINGLE,
        "statistical_area_unit": Area.AREA_1,
        "weekly_accommodation_costs": Decimal(200),
        "dependent_children_count": 0,
        "cash_assets": Decimal(1000),
        "exempt_cash_asset_status": FactStatus.VERIFIED,
        "weekly_income": None,
        "ordinary_rate_status": FactStatus.VERIFIED,
        "eldest_dependent_child_under_16": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return AsScenario(**base)  # type: ignore[arg-type]


def _assumed_parameters(
    case_id: str,
    claimant_category: ClaimantCategory,
    *,
    entry_threshold: str = "75",
    income_level: str | None = None,
    partner_status: PartnerType = PartnerType.SINGLE,
    dependent_children_count: int = 0,
) -> PolicyParameterSet:
    """`partner_status`/`dependent_children_count` default to
    `_ordinary_as_scenario()`'s own defaults -- pass the same values a
    test's scenario actually uses whenever they differ, so
    `as_parameters_for_case()` builds the entry-threshold assumption under
    the matching rate-household id (Task 26a repair). The $75 default is the
    threshold these regressions previously reached as 25% of an assumed $300
    base, so every expected amount is unchanged."""
    assumptions = {"entry_threshold": entry_threshold}
    if income_level is not None:
        assumptions["income_level"] = income_level
    return as_parameters_for_case(
        {
            "id": case_id,
            "scenario": {
                "claimant_category": claimant_category.value,
                "partner_status": partner_status.value,
                "dependent_children_count": dependent_children_count,
            },
            "parameter_assumptions": assumptions,
        }
    )


def test_single_claimant_household_category_changes_at_two_dependent_children() -> None:
    """PR #25 self-review: cl 2 covers a single claimant with one child
    (Area 1 cap $235); only a single claimant with 2+ children reaches cl
    1 (Area 1 cap $305). Exercised through the public calculator, not the
    private `_household_category()` helper directly -- a large
    `weekly_accommodation_costs` pushes the cost-based amount to saturate
    whichever area cap applies, so the resulting AS amount alone reveals
    which household category the claimant fell into. Two separate
    parameter sets, one per household (the entry threshold is keyed by the
    rate household and the cap by the cl 1-3 category, so the one-child and two-child
    scenarios need their own matching compound-id assumption, not one
    shared parameters object)."""
    one_child_parameters = _assumed_parameters(
        "regression-household-category-boundary-one-child",
        ClaimantCategory.JOBSEEKER_SUPPORT,
        dependent_children_count=1,
    )
    two_children_parameters = _assumed_parameters(
        "regression-household-category-boundary-two-children",
        ClaimantCategory.JOBSEEKER_SUPPORT,
        dependent_children_count=2,
    )

    one_child = calculate_accommodation_supplement(
        _ordinary_as_scenario(
            dependent_children_count=1,
            cash_assets=Decimal(10000),
            weekly_accommodation_costs=Decimal(2000),
        ),
        one_child_parameters,
    )
    two_children = calculate_accommodation_supplement(
        _ordinary_as_scenario(
            dependent_children_count=2,
            cash_assets=Decimal(10000),
            weekly_accommodation_costs=Decimal(2000),
        ),
        two_children_parameters,
    )

    assert one_child.outcome == "calculated"
    assert one_child.value == Decimal(235), "1 child: cl 2's $235 cap, not cl 1's $305"
    assert two_children.outcome == "calculated"
    assert two_children.value == Decimal(305), "2 children: cl 1's $305 cap, not cl 2's $235"


def test_one_child_single_uses_higher_asset_ceiling_but_cl2_area_cap() -> None:
    """PR #25 self-review: r 15 and Schedule 4 Part 7 deliberately use
    different child-count cutoffs for the same single claimant."""
    parameters = _assumed_parameters(
        "regression-r15-versus-cl2",
        ClaimantCategory.JOBSEEKER_SUPPORT,
        dependent_children_count=1,
    )
    scenario = _ordinary_as_scenario(
        dependent_children_count=1,
        cash_assets=Decimal(10000),
        weekly_accommodation_costs=Decimal(2000),
    )

    ceiling_id = _asset_ceiling_parameter_id(PartnerType.SINGLE, 1)
    assert ceiling_id == "asset_ceiling_relationship_or_dependent_children"
    assert parameters.get(ceiling_id).value == Decimal(16200)
    assert (
        _household_category(PartnerType.SINGLE, 1).value
        == "no_dependent_children_couple_or_sole_parent_one_child"
    )

    result = calculate_accommodation_supplement(scenario, parameters)
    assert result.outcome == "calculated"
    assert result.value == Decimal(235), "the Area 1 cl 2 cap must bind, not cl 1's $305 cap"


def test_unknown_exempt_cash_asset_status_is_unsupported_like_excluded() -> None:
    """PR #25 self-review: UNKNOWN is a considered unsupported outcome,
    not the needs_review convention used by other unknown facts."""
    parameters = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE)

    unknown = calculate_accommodation_supplement(
        _ordinary_as_scenario(exempt_cash_asset_status=FactStatus.UNKNOWN), parameters
    )
    excluded = calculate_accommodation_supplement(
        _ordinary_as_scenario(exempt_cash_asset_status=FactStatus.EXCLUDED), parameters
    )

    assert unknown.outcome == "unsupported"
    assert unknown.value is None
    assert excluded.outcome == "unsupported"
    assert excluded.value is None


def test_non_beneficiary_reduction_cannot_make_the_result_negative() -> None:
    """PR #25 self-review: an income reduction larger than the capped
    cost amount floors the final entitlement at zero."""
    parameters = _assumed_parameters(
        "regression-negative-floor",
        ClaimantCategory.NON_BENEFICIARY,
        income_level="200",
    )
    scenario = _ordinary_as_scenario(
        claimant_category=ClaimantCategory.NON_BENEFICIARY,
        weekly_accommodation_costs=Decimal(100),
        weekly_income=Decimal(1000),
    )

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(0)


def test_real_policy_undeclared_base_rate_and_income_level_need_review() -> None:
    """Task 23 defensive fix: parameters genuinely absent from the real
    approved policy return needs_review rather than raising KeyError. Ids
    follow the Task 26a repair: `_ordinary_as_scenario()`'s default (single,
    no dependent children) maps to the `single_no_dependent_children` rate
    row for both the entry threshold and the income level."""
    real_parameters = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE)

    missing_base = calculate_accommodation_supplement(_ordinary_as_scenario(), real_parameters)
    assert missing_base.outcome == "needs_review"
    assert "as_entry_threshold_jobseeker_support_single_no_dependent_children" in (missing_base.reason or "")

    resolutions = dict(real_parameters.resolutions)
    resolutions["as_entry_threshold_non_beneficiary_single_no_dependent_children"] = ParameterResolution(
        parameter_id="as_entry_threshold_non_beneficiary_single_no_dependent_children",
        outcome="resolved",
        value=Decimal(75),
        unit="NZD_per_week",
        source_id="test-case-assumption",
        locator="Task 24.2 undeclared-income-level regression",
    )
    missing_income_level = calculate_accommodation_supplement(
        _ordinary_as_scenario(
            claimant_category=ClaimantCategory.NON_BENEFICIARY,
            weekly_income=Decimal(250),
        ),
        replace(real_parameters, resolutions=resolutions),
    )
    assert missing_income_level.outcome == "needs_review"
    assert "as_income_level_non_beneficiary_single_no_dependent_children" in (missing_income_level.reason or "")


def test_dec001_uses_exact_fractional_income_excess_not_floor_first() -> None:
    """DEC-001: exact excess gives $74 after final rounding; the rejected
    floor-first convention would give $75 for this scenario."""
    parameters = _assumed_parameters(
        "regression-dec001-exact-excess",
        ClaimantCategory.NON_BENEFICIARY,
        income_level="200",
    )
    scenario = _ordinary_as_scenario(
        claimant_category=ClaimantCategory.NON_BENEFICIARY,
        weekly_accommodation_costs=Decimal("200.10"),
        cash_assets=Decimal(3000),
        weekly_income=Decimal("251.40"),
    )

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "calculated"
    assert result.value == Decimal(74)
    assert result.value != Decimal(75), "the rejected floor-first convention yields $75"


def test_r15_asset_ceiling_preempts_an_unrelated_needs_review_trigger() -> None:
    """Task 24.4 review finding (PR #31): the r 15 assets-ceiling
    `unsupported` exclusion previously lived entirely outside
    `_household_gate_failure()`, reached only after that function had
    already returned `None` -- so it could never actually pre-empt an
    unrelated `needs_review` trigger, contrary to the gate's own
    precedence-discipline docstring. Reproduced against the real approved
    policy: cash_assets at the r 15 ceiling ($8,100, single claimant, no
    dependent children) together with an unrelated unverified fact
    (household_eligibility) must resolve `unsupported` for the evidenced
    asset exclusion, not `needs_review` for the unrelated unverified fact."""
    parameters = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE)
    scenario = _ordinary_as_scenario(
        household_eligibility=FactStatus.UNKNOWN,
        cash_assets=Decimal(8100),
    )

    result = calculate_accommodation_supplement(scenario, parameters)

    assert result.outcome == "unsupported"
    assert "r 15" in (result.reason or "")
    assert "household_eligibility" not in (result.reason or "")
