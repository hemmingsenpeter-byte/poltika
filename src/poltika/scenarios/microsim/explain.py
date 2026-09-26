"""v0.2 Task 9.1: deterministic explanations of a population run.

Like v0.1.5's household explanations (`engines/assurance/explanation.py`),
the text is rendered from recorded figures only, with no LLM. Each sentence
carries its figures as data. `verify()` recomputes every figure from the run
through the analysis functions, and checks that the value matches and that
it appears in the sentence text.

The explanation says:

- what the population is (and that a synthetic one is not New Zealand);
- what the reform changed, and the baseline's source for each value;
- what ran and what was left out;
- the cost by component, largest first, with its coverage;
- who gained and lost for the named component set;
- the largest gaining household type;
- whether the Accommodation Supplement moved, and why not for a WFF-only
  reform (AS-10, WFF DEC-003).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from poltika.scenarios.microsim.analysis import (
    ChangeClass,
    by_household_type,
    component_set_unit,
    fiscal,
    overall,
)
from poltika.scenarios.microsim.runner import AS_COMPONENT, PopulationRun
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.semantics.population import PopulationDataset


@dataclass(frozen=True)
class Figure:
    key: str
    value: Decimal


@dataclass(frozen=True)
class Sentence:
    text: str
    figures: tuple[Figure, ...] = ()


@dataclass(frozen=True)
class PopulationExplanation:
    run_id: str
    component_set: tuple[str, ...]
    sentences: tuple[Sentence, ...]


def fmt(value: Decimal) -> str:
    """Two decimal places with thousands separators, as the text shows it."""
    return f"{value.quantize(Decimal('0.01')):,}"


def explain_population(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> PopulationExplanation:
    unit = component_set_unit(components)
    sentences: list[Sentence] = [Sentence(run.label)] if run.synthetic else []

    for o in run.overridden:
        baseline = (
            f"{fmt(o.baseline_value)}, from `{o.baseline_source_id}` ({o.baseline_locator})"
            if o.baseline_value is not None and o.baseline_outcome == "resolved"
            else f"not calculable in the baseline ({o.baseline_outcome})"
        )
        sentences.append(
            Sentence(
                f"The reform sets `{o.policy_id}.{o.parameter_id}` to {fmt(o.reform_value)} "
                f"({o.unit}) as a scenario assumption. The baseline value is {baseline}.",
                (Figure(f"override:{o.policy_id}.{o.parameter_id}", o.reform_value),),
            )
        )

    summary = run.validation.by_status()
    ran_n, ran_w = len(run.households), sum((h.weight for h in run.households), Decimal(0))
    invalid_n, invalid_w = summary[RecordStatus.INVALID]
    sentences.append(
        Sentence(
            f"{ran_n} households ran, representing a weight of {fmt(ran_w)}. "
            f"{invalid_n} were left out as invalid (weight {fmt(invalid_w)}).",
            (Figure("ran_weight", ran_w), Figure("invalid_weight", invalid_w)),
        )
    )

    table = fiscal(run)
    for component in sorted(table, key=lambda c: (-abs(table[c].delta_total), c)):
        f = table[component]
        sentences.append(
            Sentence(
                f"{component}: static entitlement change of {fmt(f.delta_total)} {f.unit} at full "
                f"take-up, over households calculated in both runs (weight "
                f"{fmt(f.coverage['calculated'])}). Not counted: weight "
                f"{fmt(f.coverage['needs_review'])} needs review and "
                f"{fmt(f.coverage['unsupported'])} is outside the modelled scope.",
                (
                    Figure(f"delta:{component}", f.delta_total),
                    Figure(f"calculated:{component}", f.coverage["calculated"]),
                    Figure(f"needs_review:{component}", f.coverage["needs_review"]),
                    Figure(f"unsupported:{component}", f.coverage["unsupported"]),
                ),
            )
        )

    s = overall(population, run, components).groups["all"]
    names = " + ".join(components)
    sentences.append(
        Sentence(
            f"For {names} ({unit}): weight {fmt(s.by_class[ChangeClass.GAIN])} gains, "
            f"{fmt(s.by_class[ChangeClass.LOSS])} loses, {fmt(s.by_class[ChangeClass.NO_CHANGE])} "
            f"is unchanged, {fmt(s.by_class[ChangeClass.NEEDS_REVIEW])} needs review and "
            f"{fmt(s.by_class[ChangeClass.UNSUPPORTED])} is outside the modelled scope.",
            tuple(Figure(f"class:{c.value}", s.by_class[c]) for c in ChangeClass),
        )
    )
    if s.mean_gain is not None:
        sentences.append(
            Sentence(
                f"The weighted mean gain is {fmt(s.mean_gain)} {unit}.",
                (Figure("mean_gain", s.mean_gain),),
            )
        )

    types = by_household_type(population, run, components).groups
    gaining = {
        t: g.by_class[ChangeClass.GAIN]
        for t, g in types.items()
        if g.by_class[ChangeClass.GAIN] > 0
    }
    if gaining:
        top = max(sorted(gaining), key=lambda t: gaining[t])
        sentences.append(
            Sentence(
                f"The household type with the most gaining weight is {top} ({fmt(gaining[top])}).",
                (Figure(f"top_gaining_type:{top}", gaining[top]),),
            )
        )

    if not any(o.policy_id == "accommodation_supplement" for o in run.overridden):
        as_delta = table[AS_COMPONENT].delta_total
        reason = "WFF tax credits are not Accommodation Supplement chargeable income (AS-10, WFF DEC-003)"
        verdict = "unchanged" if as_delta == 0 else "changed, which needs investigating"
        sentences.append(
            Sentence(
                f"No Accommodation Supplement parameter changed, and {reason}, so its entitlement is "
                f"{verdict}: {fmt(as_delta)} {table[AS_COMPONENT].unit}.",
                (Figure(f"delta:{AS_COMPONENT}", as_delta),),
            )
        )
    return PopulationExplanation(run.run_id, tuple(components), tuple(sentences))


def verify(
    explanation: PopulationExplanation, population: PopulationDataset, run: PopulationRun
) -> list[str]:
    """Every figure recomputed independently from the run, checked for its
    value and its presence in the text. Returns the problems found (empty
    when the explanation is faithful)."""
    expected: dict[str, Decimal] = {}
    for o in run.overridden:
        expected[f"override:{o.policy_id}.{o.parameter_id}"] = o.reform_value
    expected["ran_weight"] = sum((h.weight for h in run.households), Decimal(0))
    expected["invalid_weight"] = run.validation.by_status()[RecordStatus.INVALID][1]
    for c, f in fiscal(run).items():
        expected[f"delta:{c}"] = f.delta_total
        for outcome, weight in f.coverage.items():
            expected[f"{outcome}:{c}"] = weight
    s = overall(population, run, explanation.component_set).groups["all"]
    for cls in ChangeClass:
        expected[f"class:{cls.value}"] = s.by_class[cls]
    if s.mean_gain is not None:
        expected["mean_gain"] = s.mean_gain
    for t, g in by_household_type(population, run, explanation.component_set).groups.items():
        expected[f"top_gaining_type:{t}"] = g.by_class[ChangeClass.GAIN]

    problems = []
    if explanation.run_id != run.run_id:
        problems.append("explanation is for a different run")
    for sentence in explanation.sentences:
        for figure in sentence.figures:
            if figure.key not in expected:
                problems.append(f"{figure.key}: no independent figure to check against")
            elif figure.value != expected[figure.key]:
                problems.append(
                    f"{figure.key}: says {figure.value}, the run gives {expected[figure.key]}"
                )
            if fmt(figure.value) not in sentence.text:
                problems.append(f"{figure.key}: {fmt(figure.value)} is not in its sentence")
    return problems


def render_text(explanation: PopulationExplanation) -> str:
    return "\n".join(s.text for s in explanation.sentences) + "\n"
