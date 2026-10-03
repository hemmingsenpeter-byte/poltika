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


@pytest.mark.parametrize(
    ("value", "text"),
    [
        ("1.005", "$1.005"),
        ("-12.345", "$-12.345"),
        ("1234.5000", "$1,234.50"),
        ("0", "$0.00"),
        ("1E+4", "$10,000.00"),
    ],
)
def test_formatting_preserves_exact_synthetic_amounts(value: str, text: str) -> None:
    # Formatting mechanics, not statutory expected values or payment rounding.
    assert fmt(Decimal(value)) == text
    assert Decimal(text.removeprefix("$").replace(",", "")) == Decimal(value)


@pytest.mark.parametrize("missing", ["income", "capped area"])
def test_unevaluated_answers_are_not_declared_impossible(missing: str) -> None:
    res = (
        _resolve(CASES["income"])
        if missing == "income"
        else _resolve(CASES["area"], max_branches=1)
    )
    text = "\n".join(s.text for s in explain_resolution(res))
    assert "not calculable under any answer" not in text
    assert "no calculated amount in the evaluated branches" in text
    assert any(b.unresolved for b in res.branches)
    # Supplying the original facts can calculate: this is missing evidence,
    # not an exhaustive finding that all possible answers fail.
    full = _resolve(G1)
    component = "family_tax_credit" if missing == "income" else "accommodation_supplement"
    assert full.bounds[component].calculated > 0


def test_evidenced_exclusions_keep_their_distinct_label() -> None:
    res = _resolve(_wff(G1, mc6a_veterans_payment=FactStatus.UNKNOWN))
    text = "\n".join(s.text for s in explain_resolution(res))
    assert "family tax credit excluded for this answer" in text
    assert "family tax credit not modelled for this answer" not in text


@pytest.mark.parametrize(
    "change",
    ["added amount", "stripped metadata", "extended token", "wrong attribution", "unconditional", "omitted branch"],
)
def test_verify_rejects_tampered_sentences(change: str) -> None:
    res = _resolve(CASES["area"])
    sentences = list(explain_resolution(res))
    i = next(i for i, sentence in enumerate(sentences) if sentence.figures)
    original = sentences[i]
    if change == "added amount":
        sentences[i] = replace(original, text=original.text + " Also $9,999.00.")
    elif change == "stripped metadata":
        sentences[i] = replace(original, text="$9,999.00", figures=())
    elif change == "extended token":
        amount = fmt(original.figures[0].value)
        sentences[i] = replace(original, text=original.text.replace(amount, amount + "0"))
    elif change == "wrong attribution":
        sentences[i] = replace(
            original,
            text=original.text.replace("Accommodation Supplement", "in-work tax credit").replace("a week", "a year"),
        )
    elif change == "unconditional":
        sentences[i] = replace(original, text=original.text.replace("If ", "", 1))
    else:
        del sentences[i]
    assert verify(tuple(sentences), res)


def test_verify_rejects_omitted_where_calculable_caveat() -> None:
    res = _resolve(CASES["category"])
    sentences = tuple(
        replace(sentence, text=sentence.text.replace(" where calculable", ""))
        for sentence in explain_resolution(res)
    )
    assert verify(sentences, res)
