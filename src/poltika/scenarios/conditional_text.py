"""v0.3 Task 1b.2d (ADR-0016): a conditional answer in plain language.

Rendered from a `Resolution` only, with no LLM, in the v0.1.5 pattern
(`engines/assurance/explanation.py`, `scenarios/microsim/explain.py`): each
sentence carries its figures as data, and `verify()` checks their exact values
against the resolution's branches and bounds, as well as the complete fixed
sentences and figure inventory. The wording always says the answer is conditional:

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
    # Annual entitlements can contain a half-cent. Group digits and remove
    # insignificant trailing zeros without introducing payment rounding.
    whole, _, fraction = f"{value:,f}".partition(".")
    return f"${whole}.{fraction.rstrip('0').ljust(2, '0')}"


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
                status = (
                    "excluded for this answer"
                    if r.outcome == "unsupported" and r.category == "evidenced_exclusion"
                    else _STATUS[r.outcome]
                )
                parts.append(f"{LABELS[name]} {status}")
        sentences.append(Sentence(f"If {condition}: " + "; ".join(parts) + ".", tuple(figures)))
    for name in blocked:
        b = res.bounds[name]
        if b.calculated == 0 or b.low is None or b.high is None:
            sentences.append(
                Sentence(f"{LABELS[name].capitalize()}: no calculated amount in the evaluated branches.")
            )
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
            Sentence("Some fact combinations were not evaluated because the branch limit was reached.")
        )
    if res.next_question is not None:
        sentences.append(
            Sentence(f"The answer that would narrow this most: {res.next_question.entry.question}")
        )
    return tuple(sentences)


def verify(sentences: tuple[Sentence, ...], res: Resolution) -> list[str]:
    """Check exact keyed values and the complete deterministic rendering.

    Metadata alone cannot establish a sentence's component, period, condition
    or caveats. The fixed rendering is also checked, including omissions.
    Empty when the summary is faithful.
    """
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
    canonical = explain_resolution(res)
    if len(sentences) != len(canonical):
        problems.append(f"summary: has {len(sentences)} sentences, expected {len(canonical)}")
    for i, (sentence, required) in enumerate(zip(sentences, canonical, strict=False)):
        if sentence.text != required.text:
            problems.append(f"sentence:{i}: text differs from the resolution's fixed rendering")
        if sentence.figures != required.figures:
            problems.append(f"sentence:{i}: figure inventory differs from the resolution")
    return problems
