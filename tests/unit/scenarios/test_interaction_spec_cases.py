"""Task 28.5: thin runner for policy_specs/wff_as_interaction/spec_cases.yaml.

Expected values live in the protected YAML file (ADR-0005), not here. Each
case runs the combined household runner against the real approved policies
with the Task 28.2 dates.
"""

from __future__ import annotations

from dataclasses import fields
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.wff import WffResult
from poltika.scenarios.combined import CombinedHouseholdScenario, run_combined_household
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_scenario_from_yaml,
    wff_scenario_from_yaml,
)

CASES_PATH = Path(__file__).resolve().parents[3] / "policy_specs" / "wff_as_interaction" / "spec_cases.yaml"
LOOKUP = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
WFF_COMPONENTS = [f.name for f in fields(WffResult)]


def _cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = yaml.safe_load(CASES_PATH.read_text())["interaction_cases"]
    return cases


def _check(component: ComponentResult, expected: dict[str, Any], label: str) -> None:
    assert component.outcome == expected["outcome"], f"{label}: {component.reason}"
    if "value" in expected:
        assert component.value == Decimal(expected["value"]), label
    else:
        assert component.value is None, label


def test_case_file_is_non_empty_with_unique_ids_and_complete_expectations() -> None:
    cases = _cases()
    assert cases
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        assert set(case["expected"]["wff"]) == set(WFF_COMPONENTS), case["id"]
        assert "accommodation_supplement" in case["expected"]
        assert "contradictions" in case["expected"]


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_interaction_case(case: dict[str, Any]) -> None:
    result = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff_scenario_from_yaml(case["wff"]),
            accommodation_supplement=as_scenario_from_yaml(case["accommodation_supplement"]),
            as_claimant_is_wff_claimant_or_partner=FactStatus(case["precondition"]),
        ),
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )
    expected = case["expected"]
    assert len(result.contradictions) == expected["contradictions"], result.contradictions
    for name in WFF_COMPONENTS:
        _check(getattr(result.wff, name), expected["wff"][name], f"{case['id']} {name}")
    _check(result.accommodation_supplement, expected["accommodation_supplement"], f"{case['id']} AS")
