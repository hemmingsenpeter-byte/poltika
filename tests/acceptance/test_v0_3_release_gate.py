"""v0.3 exit gate (BUILD_PLAN_v0_3.md), one test per row, built up as the
phases land (Task 7.1). A row whose phase isn't built yet skips with its
reason. A green run with no skips means the gate is met.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.acceptance.review_queue import open_reviews

ROOT = Path(__file__).resolve().parents[2]
CATALOGUES = sorted((ROOT / "policy_specs").glob("*/facts.yaml"))


# Row 1: every modelled component can say what it is missing. Catalogue
# completeness is held by tests/unit/policy/test_fact_catalogs.py, and the
# intake replay by tests/unit/scenarios/test_intake.py. This row adds the
# wording check (Task 1b.1c).
@pytest.mark.parametrize("catalogue", CATALOGUES, ids=lambda p: p.parent.name)
def test_every_shipped_catalogue_has_reviewed_wording(catalogue: Path) -> None:
    status = yaml.safe_load(catalogue.read_text())["wording_status"]
    assert status == "reviewed", f"{catalogue.parent.name}: question wording is {status}"


def test_catalogues_exist_for_the_modelled_policies() -> None:
    assert {p.parent.name for p in CATALOGUES} >= {
        "working_for_families",
        "accommodation_supplement",
        "wff_as_interaction",
    }


@pytest.mark.parametrize(
    "row",
    [
        "income tax and the three core main benefits (Phases 2-3)",
        "the kernel household to disposable income (Phases 1-5)",
        "every golden household through the shared household model and graph (Phases 1, 4)",
        "one policy's output feeding another's input, explained (Phase 4)",
        "disposable income and effective marginal tax rates (Phase 5)",
        "a population run by decile and household type (Phases 5-6)",
        "the secure-environment runner exports only checked aggregates (Phase 6)",
    ],
)
def test_rows_for_later_phases(row: str) -> None:
    pytest.skip(f"not built yet: {row}")


def test_independent_review_complete() -> None:
    pending = open_reviews("v0.3")
    if pending:
        pytest.skip(f"release gate not yet met: awaiting independent review {', '.join(pending)}")
