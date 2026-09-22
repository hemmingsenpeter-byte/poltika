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
    }
    base.update(overrides)
    return AsScenario(**base)  # type: ignore[arg-type]


def _assumed_parameters(
    case_id: str,
    claimant_category: ClaimantCategory,
    *,
    base_rate: str = "300",
    income_level: str | None = None,
) -> PolicyParameterSet:
    assumptions = {"base_rate": base_rate}
    if income_level is not None:
        assumptions["income_level"] = income_level
    return as_parameters_for_case(
        {
            "id": case_id,
            "scenario": {"claimant_category": claimant_category.value},
            "parameter_assumptions": assumptions,
        }
    )


def test_single_claimant_household_category_changes_at_two_dependent_children() -> None:
    """PR #25 self-review: cl 2 covers a single claimant with one child;
    only a single claimant with 2+ children reaches cl 1."""
    one_child = _household_category(PartnerType.SINGLE, 1)
    two_children = _household_category(PartnerType.SINGLE, 2)

    assert one_child.value == "no_dependent_children_couple_or_sole_parent_one_child"
    assert two_children.value == "with_dependent_children"


def test_one_child_single_uses_higher_asset_ceiling_but_cl2_area_cap() -> None:
    """PR #25 self-review: r 15 and Schedule 4 Part 7 deliberately use
    different child-count cutoffs for the same single claimant."""
    parameters = _assumed_parameters(
        "regression-r15-versus-cl2",
        ClaimantCategory.JOBSEEKER_SUPPORT,
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
    approved policy return needs_review rather than raising KeyError."""
    real_parameters = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE)

    missing_base = calculate_accommodation_supplement(_ordinary_as_scenario(), real_parameters)
    assert missing_base.outcome == "needs_review"
    assert "as_base_rate_jobseeker_support" in (missing_base.reason or "")

    resolutions = dict(real_parameters.resolutions)
    resolutions["as_base_rate_non_beneficiary"] = ParameterResolution(
        parameter_id="as_base_rate_non_beneficiary",
        outcome="resolved",
        value=Decimal(300),
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
    assert "as_income_level_non_beneficiary" in (missing_income_level.reason or "")


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
