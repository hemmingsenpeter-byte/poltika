"""v0.1.5 Task 0.2: every protected case carries the metadata a reviewer
needs to re-derive it. Checked here rather than by rewriting the protected
files: the existing field names already hold it."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

SPECS = Path(__file__).resolve().parents[3] / "policy_specs"


def _cases(relative: str, key: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = yaml.safe_load((SPECS / relative).read_text())[key]
    return cases


@pytest.mark.parametrize(
    ("relative", "source_field"),
    [
        ("working_for_families/benchmarks.yaml", "ird_source"),
        ("accommodation_supplement/benchmarks.yaml", "msd_source"),
    ],
)
def test_benchmarks_name_their_published_source_and_assumptions(relative: str, source_field: str) -> None:
    for case in _cases(relative, "benchmarks"):
        assert case.get(source_field), (relative, case["id"])
        assert case.get("source_note"), (relative, case["id"])
        # Facts the published example leaves implicit are stated, never guessed.
        assert "assumed_facts" in case, (relative, case["id"])


def test_wff_spec_cases_state_their_period_version_and_source() -> None:
    for case in _cases("working_for_families/spec_cases.yaml", "spec_cases"):
        assert case.get("modelled_date") and case.get("policy_version"), case["id"]
        assert case.get("source_note"), case["id"]


def test_every_calculated_as_case_shows_its_derivation() -> None:
    """A case expecting an amount carries the hand derivation behind it; a
    gate case (unsupported or needs_review) has no arithmetic to derive."""
    calculated = 0
    for case in _cases("accommodation_supplement/spec_cases.yaml", "spec_cases"):
        if case["expected"]["accommodation_supplement"]["outcome"] == "calculated":
            calculated += 1
            assert case.get("derivation"), case["id"]
    assert calculated > 0


def test_interaction_cases_show_their_derivation_and_precondition() -> None:
    for case in _cases("wff_as_interaction/spec_cases.yaml", "interaction_cases"):
        assert case.get("derivation") and case.get("precondition"), case["id"]
