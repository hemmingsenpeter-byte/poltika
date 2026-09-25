"""`docs/ORIENTATION.md`'s examples run as written and reproduce the demo.

Subtask S7 of `reviews/2026-09-26-session-orientation.md`: the orientation
page must fail the build when the contract it shows changes. The expected
results come from the committed demo summary, `docs/demo/v0_1/
response_summary.json`, so no value is restated here. Only outcome and value
are compared, so a new response field does not break the check.
"""

from __future__ import annotations

import json
import re
import runpy
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
ORIENTATION = REPO / "docs" / "ORIENTATION.md"
DEMO = json.loads((REPO / "docs" / "demo" / "v0_1" / "response_summary.json").read_text())


def _examples() -> list[str]:
    return re.findall(r"```python\n(.*?)```", ORIENTATION.read_text(), re.DOTALL)


def _run(code: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Run one example as a reader would: saved to a file, from the repository root."""
    example = tmp_path / "example.py"
    example.write_text(code)
    monkeypatch.chdir(REPO)
    return runpy.run_path(str(example))


def _expected(component: dict[str, Any]) -> tuple[str, Decimal]:
    return component["outcome"], Decimal(component["value"])


def test_orientation_has_its_two_examples() -> None:
    assert len(_examples()) == 2


def test_api_example_reproduces_the_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    response = _run(_examples()[0], tmp_path, monkeypatch)["response"]

    for got, want in (
        (response["wff"]["family_tax_credit"], DEMO["wff"]["family_tax_credit"]),
        (response["accommodation_supplement"], DEMO["accommodation_supplement"]),
    ):
        assert (got["outcome"], Decimal(got["value"])) == _expected(want)


def test_engine_example_reproduces_the_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(_examples()[1], tmp_path, monkeypatch)["result"]

    ftc = result.wff.family_tax_credit
    accommodation = result.accommodation_supplement
    assert (ftc.outcome, ftc.value) == _expected(DEMO["wff"]["family_tax_credit"])
    assert (accommodation.outcome, accommodation.value) == _expected(DEMO["accommodation_supplement"])
    assert result.contradictions == ()
