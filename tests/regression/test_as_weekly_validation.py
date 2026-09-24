"""Regression: AS module validation used WFF's annual coverage rule.

Found in GPT/Codex's Task 28.2 research (PR #41) and reproduced
independently by Claude Code. `_as_module_validation_failure()` (Task 24.7)
required every parameter value to span AS's whole reference period
`[2026-03-02, 2027-04-01)`. AS is assessed per week, and MSD's dated rate
tables start on 1 April 2026, so a genuinely April-effective rate gated
every week. Each test below is one of the two reproductions, kept under a
durable name so the mistake cannot return unnoticed.

The first test uses the real policy's own 1 April 2026 thresholds (Task
26a.2); the second moves the real policy's first cap start, keeping its
value, as a synthetic interval diagnostic.
"""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from poltika.engines.simulator.accommodation_supplement import (
    AssessmentWeek,
    calculate_accommodation_supplement,
    run_as_module,
)
from poltika.policy.loader import load_policy_parameters
from tests.conftest import AS_POLICY_DIR, as_scenario_from_yaml, load_as_cases

# A June test week -- not Task 28.2's selected week, which Pete has not chosen.
JUNE_WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
LOOKUP_DATE = date(2026, 6, 1)


def _case(case_id: str) -> dict[str, Any]:
    cases = load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")
    return next(c for c in cases if c["id"] == case_id)


def _policy_copy(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    policy_dir = tmp_path / "accommodation_supplement"
    shutil.copytree(AS_POLICY_DIR, policy_dir)
    return policy_dir, yaml.safe_load((policy_dir / "policy.yaml").read_text())


def _write(policy_dir: Path, policy: dict[str, Any]) -> None:
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy, sort_keys=False))


def test_april_effective_entry_threshold_calculates_for_a_june_week() -> None:
    """Claude Code's reproduction: a rate effective from 1 April returned
    `needs_review` for every June week. Since Task 26a.2 the real policy's
    published thresholds are themselves effective from 1 April 2026, so the
    real policy is the reproduction: a June week must calculate, using a
    threshold whose interval starts on 1 April."""
    case = _case("real_policy_jobseeker_single_published_threshold")

    result = run_as_module(
        AS_POLICY_DIR,
        LOOKUP_DATE,
        as_scenario_from_yaml(case["scenario"]),
        requested_policy_version="0.1.1",
        assessment_week=JUNE_WEEK,
    )

    assert result.outcome == "calculated", result.reason
    assert str(result.value) == case["expected"]["accommodation_supplement"]["value"]
    assert result.trace is not None
    threshold = next(p for p in result.trace.parameters if p.parameter_id.startswith("as_entry_threshold_"))
    assert threshold.effective_from == date(2026, 4, 1)


def test_april_effective_area_cap_passes_module_validation(tmp_path: Path) -> None:
    """GPT/Codex's reproduction: moving the first area cap's start from
    2 March to 1 April, keeping its value and end, gated a June run with a
    "full-year rate" reason. The module must now reach the calculator."""
    case = _case("ordinary_uncapped_jobseeker")
    policy_dir, policy = _policy_copy(tmp_path)
    first_cap = next(p for p in policy["parameters"] if p["id"].startswith("area_cap_"))
    first_cap["values"][0]["effective_from"] = date(2026, 4, 1)
    _write(policy_dir, policy)
    scenario = as_scenario_from_yaml(case["scenario"])

    result = run_as_module(
        policy_dir, LOOKUP_DATE, scenario, requested_policy_version="0.1.1", assessment_week=JUNE_WEEK
    )

    direct = calculate_accommodation_supplement(
        scenario, load_policy_parameters(policy_dir, LOOKUP_DATE, requested_policy_version="0.1.1")
    )
    assert result == direct
    assert "full-year" not in (result.reason or "")
