"""Task 24.1 Accommodation Supplement spec cases."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from poltika.engines.simulator.accommodation_supplement import calculate_accommodation_supplement
from poltika.policy.loader import load_policy_parameters
from tests.conftest import (
    AS_MODELLED_DATE,
    as_parameters_for_case,
    as_scenario_from_yaml,
    load_as_cases,
)

AS_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "accommodation_supplement"
SPEC_CASES_PATH = AS_POLICY_DIR / "spec_cases.yaml"
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


_CASES = load_as_cases(SPEC_CASES_PATH, "spec_cases")
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
        AS_POLICY_DIR, AS_MODELLED_DATE, requested_policy_version="0.1.0"
    )
    assert set(parameters.resolutions) == _INDEPENDENTLY_VERIFIED_PARAMETER_IDS
    assert all(resolution.outcome == "resolved" for resolution in parameters.resolutions.values())


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_as_spec_case(case: dict[str, Any]) -> None:
    result = calculate_accommodation_supplement(
        as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case)
    )
    expected = case["expected"]["accommodation_supplement"]
    assert result.outcome == expected["outcome"], (
        f"{case['id']}: expected {expected['outcome']}, got {result.outcome} ({result.reason})"
    )
    if expected["outcome"] == "calculated":
        assert result.value == Decimal(expected["value"])
    else:
        assert result.value is None
