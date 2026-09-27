"""v0.3 Task 1b.2d: the conditional answer in plain language, verified."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from poltika.engines.simulator.outcome import FactStatus
from poltika.scenarios.conditional_text import Figure, explain_resolution, fmt, verify
from tests.unit.scenarios.test_conditional import GOLDEN, _as, _resolve, _wff

G1 = GOLDEN[0]
CASES = {
    "area": _as(G1, statistical_area_unit=None),
    "category": _as(G1, claimant_category=None),
    "eligibility": _wff(G1, household_eligibility=FactStatus.UNKNOWN),
    "income": _wff(G1, family_scheme_income=None),
    "two facts": _as(_wff(G1, household_eligibility=FactStatus.UNKNOWN), statistical_area_unit=None),
}


@pytest.mark.parametrize("name", list(CASES))
def test_summary_is_verified_against_the_resolution(name: str) -> None:
    res = _resolve(CASES[name])
    sentences = explain_resolution(res)
    assert sentences[0].text.startswith("Poltika can't give one figure without: ")
    assert verify(sentences, res) == []


def test_area_summary_names_each_answer_and_the_range() -> None:
    res = _resolve(CASES["area"])
    text = "\n".join(s.text for s in explain_resolution(res))
    for b in res.branches:
        value = b.result.accommodation_supplement.value
        assert value is not None and fmt(value) in text
    bounds = res.bounds["accommodation_supplement"]
    assert bounds.low is not None and bounds.high is not None
    assert f"between {fmt(bounds.low)} and {fmt(bounds.high)} a week" in text
    assert "(4 of 4 answers)" in text
    assert "The answer that would narrow this most:" in text


def test_unsupported_answers_are_said_not_zeroed() -> None:
    text = "\n".join(s.text for s in explain_resolution(_resolve(CASES["category"])))
    assert "not modelled for this answer" in text and "where calculable" in text


def test_complete_household_has_no_summary() -> None:
    assert explain_resolution(_resolve(G1)) == ()


def test_verify_catches_a_wrong_figure() -> None:
    res = _resolve(CASES["area"])
    sentences = list(explain_resolution(res))
    i = next(i for i, s in enumerate(sentences) if s.figures)
    wrong = replace(sentences[i], figures=(Figure(sentences[i].figures[0].key, Decimal("1.23")),))
    sentences[i] = wrong
    problems = verify(tuple(sentences), res)
    assert any("says 1.23" in p for p in problems) and any("not in its sentence" in p for p in problems)
