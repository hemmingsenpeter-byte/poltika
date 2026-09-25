"""Task 29.3: thin runner for policy_specs/wff_as_interaction/golden_households.yaml.

Expected values live in the protected YAML file, not here. Every household
runs through the combined household runner against the real approved
policies with the Task 28.2 dates and no parameter assumptions.
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

GOLDEN_PATH = Path(__file__).resolve().parents[3] / "policy_specs" / "wff_as_interaction" / "golden_households.yaml"
LOOKUP = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
WFF_COMPONENTS = [f.name for f in fields(WffResult)]


def _households() -> list[dict[str, Any]]:
    households: list[dict[str, Any]] = yaml.safe_load(GOLDEN_PATH.read_text())["households"]
    return households


def _check(component: ComponentResult, expected: dict[str, Any], label: str) -> None:
    assert component.outcome == expected["outcome"], f"{label}: {component.reason}"
    if "value" in expected:
        assert component.value == Decimal(expected["value"]), label
    else:
        assert component.value is None, label


def test_golden_file_is_complete_and_assumption_free() -> None:
    households = _households()
    assert len(households) >= 8
    ids = [h["id"] for h in households]
    assert len(ids) == len(set(ids))
    for household in households:
        assert household["why"], household["id"]
        assert "parameter_assumptions" not in household, household["id"]
        assert set(household["expected"]["wff"]) == set(WFF_COMPONENTS), household["id"]
        assert "accommodation_supplement" in household["expected"]


@pytest.mark.parametrize("household", _households(), ids=lambda h: h["id"])
def test_golden_household(household: dict[str, Any]) -> None:
    result = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff_scenario_from_yaml(household["wff"]),
            accommodation_supplement=as_scenario_from_yaml(household["accommodation_supplement"]),
            as_claimant_is_wff_claimant_or_partner=FactStatus(household["precondition"]),
        ),
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )
    expected = household["expected"]
    assert len(result.contradictions) == expected["contradictions"], result.contradictions
    for name in WFF_COMPONENTS:
        _check(getattr(result.wff, name), expected["wff"][name], f"{household['id']} {name}")
    _check(result.accommodation_supplement, expected["accommodation_supplement"], f"{household['id']} AS")
