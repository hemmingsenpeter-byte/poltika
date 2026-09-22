"""Task 24.1 Accommodation Supplement spec cases."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.wff import FactStatus
from poltika.policy.loader import ParameterResolution, PolicyParameterSet, load_policy_parameters

AS_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "accommodation_supplement"
SPEC_CASES_PATH = AS_POLICY_DIR / "spec_cases.yaml"
MODELLED_DATE = date(2026, 6, 1)
_ALLOWED_PARAMETER_ASSUMPTIONS = {"base_rate", "income_level"}
_INDEPENDENTLY_VERIFIED_PARAMETER_IDS = {
    "area_cap_with_dependent_children_area1",
    "area_cap_with_dependent_children_area2",
    "area_cap_with_dependent_children_area3",
    "area_cap_with_dependent_children_area4",
    "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area1",
    "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area2",
    "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area3",
    "area_cap_no_dependent_children_couple_or_sole_parent_one_child_area4",
    "area_cap_single_no_dependent_children_area1",
    "area_cap_single_no_dependent_children_area2",
    "area_cap_single_no_dependent_children_area3",
    "area_cap_single_no_dependent_children_area4",
    "entry_threshold_rent_board_fraction",
    "asset_ceiling_relationship_or_dependent_children",
    "asset_ceiling_other",
    "asset_imputation_threshold_relationship_or_dependent_children",
    "asset_imputation_threshold_other",
    "asset_imputation_step_size",
    "asset_imputation_amount_per_step",
    "income_reduction_rate",
}


def _load_cases(path: Path, key: str) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text())
    cases: list[dict[str, Any]] = raw[key]
    return cases


def _scenario(raw: dict[str, Any]) -> AsScenario:
    def optional_decimal(key: str) -> Decimal | None:
        value = raw.get(key)
        return Decimal(value) if value is not None else None

    return AsScenario(
        household_eligibility=FactStatus(raw["household_eligibility"]),
        claimant_category=(
            ClaimantCategory(raw["claimant_category"])
            if raw.get("claimant_category")
            else None
        ),
        tenure_type=TenureType(raw["tenure_type"]) if raw.get("tenure_type") else None,
        partner_status=(
            PartnerType(raw["partner_status"]) if raw.get("partner_status") else None
        ),
        statistical_area_unit=(
            Area(raw["statistical_area_unit"])
            if raw.get("statistical_area_unit")
            else None
        ),
        weekly_accommodation_costs=optional_decimal("weekly_accommodation_costs"),
        dependent_children_count=raw.get("dependent_children_count"),
        cash_assets=optional_decimal("cash_assets"),
        exempt_cash_asset_status=FactStatus(raw["exempt_cash_asset_status"]),
        weekly_income=optional_decimal("weekly_income"),
    )


def _parameters(case: dict[str, Any]) -> PolicyParameterSet:
    base = load_policy_parameters(
        AS_POLICY_DIR, MODELLED_DATE, requested_policy_version="0.1.0"
    )
    assumptions = case.get("parameter_assumptions", {})
    assert set(assumptions) <= _ALLOWED_PARAMETER_ASSUMPTIONS, (
        f"{case['id']}: unknown parameter assumption(s) "
        f"{set(assumptions) - _ALLOWED_PARAMETER_ASSUMPTIONS}"
    )
    resolutions = dict(base.resolutions)
    category = case["scenario"].get("claimant_category")
    if "base_rate" in assumptions and category is not None:
        parameter_id = f"as_base_rate_{category}"
        resolutions[parameter_id] = ParameterResolution(
            parameter_id=parameter_id,
            outcome="resolved",
            value=Decimal(assumptions["base_rate"]),
            unit="NZD_per_week",
            source_id="test-case-assumption",
            locator=case["id"],
        )
    if "income_level" in assumptions and category is not None:
        parameter_id = f"as_income_level_{category}"
        resolutions[parameter_id] = ParameterResolution(
            parameter_id=parameter_id,
            outcome="resolved",
            value=Decimal(assumptions["income_level"]),
            unit="NZD_per_week",
            source_id="test-case-assumption",
            locator=case["id"],
        )
    return replace(base, resolutions=resolutions)


_CASES = _load_cases(SPEC_CASES_PATH, "spec_cases")
_CASE_IDS = [case["id"] for case in _CASES]


def test_as_spec_cases_are_complete_and_unique() -> None:
    assert len(_CASES) >= 20
    assert len(_CASE_IDS) == len(set(_CASE_IDS))
    for case in _CASES:
        assert set(case["expected"]) == {"accommodation_supplement"}, (
            f"{case['id']}: expected must name exactly accommodation_supplement"
        )


def test_real_policy_contains_exactly_the_20_independently_verified_parameters() -> None:
    parameters = load_policy_parameters(
        AS_POLICY_DIR, MODELLED_DATE, requested_policy_version="0.1.0"
    )
    assert set(parameters.resolutions) == _INDEPENDENTLY_VERIFIED_PARAMETER_IDS
    assert all(
        resolution.outcome == "resolved"
        for resolution in parameters.resolutions.values()
    )


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_as_spec_case(case: dict[str, Any]) -> None:
    result = calculate_accommodation_supplement(
        _scenario(case["scenario"]), _parameters(case)
    )
    expected = case["expected"]["accommodation_supplement"]
    assert result.outcome == expected["outcome"], (
        f"{case['id']}: expected {expected['outcome']}, "
        f"got {result.outcome} ({result.reason})"
    )
    if expected["outcome"] == "calculated":
        assert result.value == Decimal(expected["value"])
    else:
        assert result.value is None
