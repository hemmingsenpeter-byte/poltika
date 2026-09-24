"""Task 26a selector repair (specification.md, DEC-002): required coverage.

The Task 25/26 base-rate id reused the Schedule 4 Part 7 cl 1-3 cap grouping,
which conflates rows MSD's entry-threshold tables keep apart (SPEC_ERROR,
PR #46). These tests pin the repaired contract: a separate rate-household
selector for the published entry threshold and non-beneficiary income level,
the unchanged cap selector, no old-id fallback, and the new fail-closed facts.

Every threshold/income value below is a synthetic, clearly distinct test
number chosen so a selector collision changes the result -- none is a
statutory or MSD figure (Task 26a.2 populates those).
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import Any

import pytest

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.wff import ComponentResult, FactStatus
from poltika.policy.loader import ParameterResolution, PolicyParameterSet, load_policy_parameters
from tests.conftest import AS_MODELLED_DATE, AS_POLICY_DIR, AS_POLICY_VERSION

# Synthetic, distinct per rate household -- NOT statutory values.
THRESHOLDS = {
    "single_no_dependent_children": Decimal(61),
    "sole_parent": Decimal(62),
    "couple_no_dependent_children": Decimal(63),
    "couple_with_dependent_children": Decimal(64),
}
INCOME_LEVELS = {
    "single_no_dependent_children": Decimal(301),
    "sole_parent": Decimal(302),
    "couple_no_dependent_children": Decimal(303),
    "couple_with_dependent_children": Decimal(304),
}
CLAIMANTS = ("jobseeker_support", "sole_parent_support", "supported_living_payment", "non_beneficiary")


def _resolution(parameter_id: str, value: Decimal) -> ParameterResolution:
    return ParameterResolution(
        parameter_id=parameter_id,
        outcome="resolved",
        value=value,
        unit="NZD_per_week",
        source_id="test-selector-assumption",
        locator="synthetic selector-isolation value",
    )


def _parameters(*, thresholds: bool = True, income_levels: bool = True, extra: dict[str, Decimal] | None = None) -> PolicyParameterSet:
    """The real approved AS policy (caps, assets, rates) plus synthetic
    threshold/income values under the repaired ids."""
    base = load_policy_parameters(AS_POLICY_DIR, AS_MODELLED_DATE, requested_policy_version=AS_POLICY_VERSION)
    resolutions = dict(base.resolutions)
    if thresholds:
        for claimant in CLAIMANTS:
            for household, value in THRESHOLDS.items():
                pid = f"as_entry_threshold_{claimant}_{household}"
                resolutions[pid] = _resolution(pid, value)
    if income_levels:
        for household, value in INCOME_LEVELS.items():
            pid = f"as_income_level_non_beneficiary_{household}"
            resolutions[pid] = _resolution(pid, value)
    for pid, value in (extra or {}).items():
        resolutions[pid] = _resolution(pid, value)
    return replace(base, resolutions=resolutions)


def _scenario(**overrides: Any) -> AsScenario:
    base: dict[str, Any] = {
        "household_eligibility": FactStatus.VERIFIED,
        "claimant_category": ClaimantCategory.SUPPORTED_LIVING_PAYMENT,
        "tenure_type": TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
        "partner_status": PartnerType.SINGLE,
        "statistical_area_unit": Area.AREA_1,
        # Low enough that no Area 1 cap binds: result = ceil(0.7 x (costs - threshold)).
        "weekly_accommodation_costs": Decimal(200),
        "dependent_children_count": 0,
        "cash_assets": Decimal(0),
        "exempt_cash_asset_status": FactStatus.VERIFIED,
        "ordinary_rate_status": FactStatus.VERIFIED,
        "eldest_dependent_child_under_16": FactStatus.VERIFIED,
    }
    base.update(overrides)
    return AsScenario(**base)


def _ids(result: ComponentResult) -> list[str]:
    assert result.trace is not None
    return [p.parameter_id for p in result.trace.parameters]


def _consulted(result: ComponentResult, prefix: str) -> list[str]:
    return [pid for pid in _ids(result) if pid.startswith(prefix)]


def _expected(costs: Decimal, threshold: Decimal) -> Decimal:
    """Hand calculation: 70% of the positive excess, rounded up (r 19)."""
    return (Decimal("0.7") * (costs - threshold)).to_integral_value(rounding="ROUND_CEILING")


@pytest.mark.parametrize(
    ("couple_children", "sole_parent_children", "couple_row", "cap_row"),
    [
        # Formerly colliding pair 1: cl 2 cap row, different threshold rows.
        (0, 1, "couple_no_dependent_children", "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area1"),
        # Formerly colliding pair 2: cl 1 cap row, different threshold rows.
        (2, 2, "couple_with_dependent_children", "area_cap_with_dependent_children_area1"),
    ],
)
def test_formerly_colliding_households_use_different_thresholds_but_the_same_cap(
    couple_children: int, sole_parent_children: int, couple_row: str, cap_row: str
) -> None:
    parameters = _parameters()
    couple = calculate_accommodation_supplement(
        _scenario(partner_status=PartnerType.ORDINARY_COUPLE, dependent_children_count=couple_children), parameters
    )
    sole_parent = calculate_accommodation_supplement(
        _scenario(partner_status=PartnerType.SINGLE, dependent_children_count=sole_parent_children), parameters
    )

    assert _consulted(couple, "as_entry_threshold_") == [f"as_entry_threshold_supported_living_payment_{couple_row}"]
    assert _consulted(sole_parent, "as_entry_threshold_") == ["as_entry_threshold_supported_living_payment_sole_parent"]
    assert _consulted(couple, "area_cap_") == _consulted(sole_parent, "area_cap_") == [cap_row]
    assert couple.value == _expected(Decimal(200), THRESHOLDS[couple_row])
    assert sole_parent.value == _expected(Decimal(200), THRESHOLDS["sole_parent"])
    assert couple.value != sole_parent.value


def test_sole_parent_threshold_row_is_unchanged_by_a_second_child_while_the_cap_changes() -> None:
    parameters = _parameters()
    one = calculate_accommodation_supplement(_scenario(dependent_children_count=1, weekly_accommodation_costs=Decimal(2000)), parameters)
    two = calculate_accommodation_supplement(_scenario(dependent_children_count=2, weekly_accommodation_costs=Decimal(2000)), parameters)

    assert _consulted(one, "as_entry_threshold_") == _consulted(two, "as_entry_threshold_")
    assert _consulted(one, "area_cap_") == ["area_cap_no_dependent_children_couple_or_sole_parent_one_child_area1"]
    assert _consulted(two, "area_cap_") == ["area_cap_with_dependent_children_area1"]
    # High costs saturate each cap, so the amounts are the real cl 2 and cl 1 Area 1 caps.
    assert one.value != two.value


@pytest.mark.parametrize(
    ("partner_status", "children", "household"),
    [
        (PartnerType.SINGLE, 0, "single_no_dependent_children"),
        (PartnerType.SINGLE, 1, "sole_parent"),
        (PartnerType.ORDINARY_COUPLE, 0, "couple_no_dependent_children"),
        (PartnerType.ORDINARY_COUPLE, 3, "couple_with_dependent_children"),
    ],
)
def test_non_beneficiary_income_level_selector(partner_status: PartnerType, children: int, household: str) -> None:
    income = INCOME_LEVELS[household] + Decimal(40)  # $40 over this household's synthetic level
    result = calculate_accommodation_supplement(
        _scenario(
            claimant_category=ClaimantCategory.NON_BENEFICIARY,
            partner_status=partner_status,
            dependent_children_count=children,
            weekly_income=income,
        ),
        _parameters(),
    )

    assert _consulted(result, "as_income_level_") == [f"as_income_level_non_beneficiary_{household}"]
    assert _consulted(result, "as_entry_threshold_") == [f"as_entry_threshold_non_beneficiary_{household}"]
    # 70% x (200 - threshold) - 25% x 40, rounded up.
    pre_rounding = Decimal("0.7") * (Decimal(200) - THRESHOLDS[household]) - Decimal("0.25") * Decimal(40)
    assert result.value == pre_rounding.to_integral_value(rounding="ROUND_CEILING")


def test_beneficiary_never_consults_an_income_level() -> None:
    result = calculate_accommodation_supplement(_scenario(), _parameters())
    assert result.outcome == "calculated"
    assert _consulted(result, "as_income_level_") == []


def test_no_fallback_to_old_base_rate_ids() -> None:
    """A policy declaring only the pre-repair ids must not calculate: the
    old ids are not aliases (specification.md, Task 26a repair)."""
    old = {
        "as_base_rate_supported_living_payment_single_no_dependent_children": Decimal(300),
        "as_income_level_non_beneficiary": Decimal(200),
        "as_income_level_supported_living_payment": Decimal(200),
    }
    result = calculate_accommodation_supplement(_scenario(), _parameters(thresholds=False, income_levels=False, extra=old))

    assert result.outcome == "needs_review"
    assert "as_entry_threshold_supported_living_payment_single_no_dependent_children" in (result.reason or "")
    assert not any(pid.startswith("as_base_rate_") for pid in _ids(result))


def test_no_fallback_to_the_claimant_only_income_level_id() -> None:
    old = {"as_income_level_non_beneficiary": Decimal(200)}
    result = calculate_accommodation_supplement(
        _scenario(claimant_category=ClaimantCategory.NON_BENEFICIARY, weekly_income=Decimal(500)),
        _parameters(income_levels=False, extra=old),
    )

    assert result.outcome == "needs_review"
    assert "as_income_level_non_beneficiary_single_no_dependent_children" in (result.reason or "")


@pytest.mark.parametrize(("status", "outcome"), [(FactStatus.UNKNOWN, "needs_review"), (FactStatus.EXCLUDED, "unsupported")])
def test_ordinary_rate_status_gate(status: FactStatus, outcome: str) -> None:
    result = calculate_accommodation_supplement(_scenario(ordinary_rate_status=status), _parameters())
    assert result.outcome == outcome
    assert _consulted(result, "as_entry_threshold_") == []


@pytest.mark.parametrize(
    ("partner_status", "children"),
    [(PartnerType.ORDINARY_COUPLE, 1), (PartnerType.SINGLE, 0), (PartnerType.ORDINARY_COUPLE, 0)],
)
def test_sole_parent_support_without_a_sole_parent_household_is_unsupported(
    partner_status: PartnerType, children: int
) -> None:
    result = calculate_accommodation_supplement(
        _scenario(
            claimant_category=ClaimantCategory.SOLE_PARENT_SUPPORT,
            partner_status=partner_status,
            dependent_children_count=children,
        ),
        _parameters(),
    )
    assert result.outcome == "unsupported"
    assert "Sole Parent Support" in (result.reason or "")
    assert _consulted(result, "as_entry_threshold_") == []


def test_sole_parent_support_for_a_sole_parent_calculates() -> None:
    result = calculate_accommodation_supplement(
        _scenario(claimant_category=ClaimantCategory.SOLE_PARENT_SUPPORT, dependent_children_count=1), _parameters()
    )
    assert result.outcome == "calculated"
    assert _consulted(result, "as_entry_threshold_") == ["as_entry_threshold_sole_parent_support_sole_parent"]


@pytest.mark.parametrize(
    ("status", "outcome"), [(FactStatus.UNKNOWN, "needs_review"), (FactStatus.EXCLUDED, "unsupported")]
)
@pytest.mark.parametrize("partner_status", [PartnerType.SINGLE, PartnerType.ORDINARY_COUPLE])
def test_parent_rows_require_the_eldest_child_under_16(
    status: FactStatus, outcome: str, partner_status: PartnerType
) -> None:
    result = calculate_accommodation_supplement(
        _scenario(partner_status=partner_status, dependent_children_count=1, eldest_dependent_child_under_16=status),
        _parameters(),
    )
    assert result.outcome == outcome
    assert _consulted(result, "as_entry_threshold_") == []


@pytest.mark.parametrize("partner_status", [PartnerType.SINGLE, PartnerType.ORDINARY_COUPLE])
def test_childless_households_do_not_consult_the_child_age_fact(partner_status: PartnerType) -> None:
    result = calculate_accommodation_supplement(
        _scenario(partner_status=partner_status, eldest_dependent_child_under_16=FactStatus.EXCLUDED), _parameters()
    )
    assert result.outcome == "calculated"
    assert result.trace is not None
    assert "eldest_dependent_child_under_16" not in [i.name for i in result.trace.inputs]


def test_threshold_is_subtracted_directly_not_multiplied() -> None:
    result = calculate_accommodation_supplement(_scenario(), _parameters())
    # 0.7 x (200 - 61) = 97.3 -> 98. A 25% multiplication would give 0.7 x (200 - 15.25).
    assert result.value == Decimal(98)
    assert "entry_threshold_rent_board_fraction" not in _ids(result)


def test_costs_exactly_at_the_published_threshold_are_a_calculated_zero() -> None:
    result = calculate_accommodation_supplement(
        _scenario(weekly_accommodation_costs=THRESHOLDS["single_no_dependent_children"]), _parameters()
    )
    assert result.outcome == "calculated"
    assert result.value == Decimal(0)


def test_trace_records_threshold_cap_new_facts_and_dec_002() -> None:
    result = calculate_accommodation_supplement(
        _scenario(partner_status=PartnerType.ORDINARY_COUPLE, dependent_children_count=2), _parameters()
    )
    assert result.trace is not None
    assert _consulted(result, "as_entry_threshold_") == [
        "as_entry_threshold_supported_living_payment_couple_with_dependent_children"
    ]
    assert _consulted(result, "area_cap_") == ["area_cap_with_dependent_children_area1"]
    inputs = [i.name for i in result.trace.inputs]
    assert "ordinary_rate_status" in inputs
    assert "eldest_dependent_child_under_16" in inputs
    assert result.trace.decisions == ("DEC-002",)
    assert any(rule.startswith("DEC-002") for rule in result.trace.calculation_rules)
