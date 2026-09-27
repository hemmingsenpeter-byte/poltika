"""v0.3 Task 1b.2d (ADR-0016): a conditional answer in plain language.

Rendered from a `Resolution` only, with no LLM, in the v0.1.5 pattern
(`engines/assurance/explanation.py`, `scenarios/microsim/explain.py`): each
sentence carries its figures as data, and `verify()` recomputes every figure
from the resolution's branches and bounds and checks that it appears in the
sentence text. The wording always says the answer is conditional:

    Poltika can't give one figure without: <question>.
    If <fact> is <answer>: <component> $X a year; ...
    <component>: between $A and $B where calculable (n of m answers).
    The answer that would narrow this most: <question>

Only the components a missing fact blocks are described; the others are
unchanged and reported as usual.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from poltika.scenarios.conditional import (
    AS_COMPONENT,
    COMPONENTS,
    Resolution,
    component,
)

LABELS = {
    "family_tax_credit": "family tax credit",
    "in_work_tax_credit": "in-work tax credit",
    "minimum_family_tax_credit": "minimum family tax credit",
    "best_start": "Best Start",
    "accommodation_supplement": "Accommodation Supplement",
}
_STATUS = {"needs_review": "needs review", "unsupported": "not modelled for this answer"}


@dataclass(frozen=True)
class Figure:
    key: str
    value: Decimal


@dataclass(frozen=True)
class Sentence:
    text: str
    figures: tuple[Figure, ...] = ()


def fmt(value: Decimal) -> str:
    return f"${value.quantize(Decimal('0.01')):,}"


def _per(name: str) -> str:
    return "a week" if name == AS_COMPONENT else "a year"


def _blocked(res: Resolution) -> list[str]:
    names = {b for m in res.missing for b in m.blocks}
    return [c for c in COMPONENTS if c in names]


def explain_resolution(res: Resolution) -> tuple[Sentence, ...]:
    if not res.missing:
        return ()
    blocked = _blocked(res)
    sentences = [
        Sentence(
            "Poltika can't give one figure without: "
            + "; ".join(m.entry.question for m in res.missing)
        )
    ]
    labels = {m.slot: (m.entry.answers or m.entry.values or {}) for m in res.missing}
    for i, branch in enumerate(res.branches):
        if not branch.assignment:
            continue
        condition = ", and ".join(
            f"{slot.label} is {labels.get(slot, {}).get(value, value)}"
            for slot, value in branch.assignment
        )
        parts, figures = [], []
        for name in blocked:
            r = component(branch.result, name)
            if r.outcome == "calculated" and r.value is not None:
                parts.append(f"{LABELS[name]} {fmt(r.value)} {_per(name)}")
                figures.append(Figure(f"branch:{i}:{name}", r.value))
            else:
                parts.append(f"{LABELS[name]} {_STATUS[r.outcome]}")
        sentences.append(Sentence(f"If {condition}: " + "; ".join(parts) + ".", tuple(figures)))
    for name in blocked:
        b = res.bounds[name]
        if b.calculated == 0 or b.low is None or b.high is None:
            sentences.append(Sentence(f"{LABELS[name].capitalize()}: not calculable under any answer."))
            continue
        where = "" if b.complete else " where calculable"
        caveat = "; values at these points, not bounds" if b.kind == "points" else ""
        span = (
            f"{fmt(b.low)} {_per(name)}"
            if b.low == b.high
            else f"between {fmt(b.low)} and {fmt(b.high)} {_per(name)}"
        )
        sentences.append(
            Sentence(
                f"{LABELS[name].capitalize()}: {span}{where} "
                f"({b.calculated} of {b.branches} answers{caveat}).",
                (Figure(f"low:{name}", b.low), Figure(f"high:{name}", b.high)),
            )
        )
    if res.capped:
        sentences.append(
            Sentence("There are too many combinations to show: only the facts that matter most are branched.")
        )
    if res.next_question is not None:
        sentences.append(
            Sentence(f"The answer that would narrow this most: {res.next_question.entry.question}")
        )
    return tuple(sentences)


def verify(sentences: tuple[Sentence, ...], res: Resolution) -> list[str]:
    """Every figure recomputed from the resolution, checked for its value
    and its presence in the text. Empty when the summary is faithful."""
    expected: dict[str, Decimal] = {}
    for i, branch in enumerate(res.branches):
        for name in COMPONENTS:
            r = component(branch.result, name)
            if r.outcome == "calculated" and r.value is not None:
                expected[f"branch:{i}:{name}"] = r.value
    for name, b in res.bounds.items():
        if b.low is not None and b.high is not None:
            expected[f"low:{name}"], expected[f"high:{name}"] = b.low, b.high
    problems = []
    for sentence in sentences:
        for figure in sentence.figures:
            if figure.key not in expected:
                problems.append(f"{figure.key}: no figure in the resolution to check against")
            elif figure.value != expected[figure.key]:
                problems.append(f"{figure.key}: says {figure.value}, the resolution gives {expected[figure.key]}")
            if fmt(figure.value) not in sentence.text:
                problems.append(f"{figure.key}: {fmt(figure.value)} is not in its sentence")
    return problems
