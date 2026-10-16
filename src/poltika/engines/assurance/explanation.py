"""v0.1.5 Phase 3: deterministic explanations of a component result.

An explanation is rendered only from what the calculator recorded: the
result, its reason code and missing facts, and its trace (calculation
steps, parameters consulted, caller-asserted facts). Every number in the
text is a value the calculator carried, formatted exactly (never rounded or
re-computed here), so an explanation cannot disagree with the calculation.
No LLM is involved; templates are fixed per step id.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from poltika.common.errors import ProvenanceError
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.trace import CalculationStep, plain

COMPONENT_LABELS: dict[str, str] = {
    "family_tax_credit": "Family tax credit",
    "in_work_tax_credit": "In-work tax credit",
    "minimum_family_tax_credit": "Minimum family tax credit",
    "best_start": "Best Start",
    "accommodation_supplement": "Accommodation Supplement",
}

COMPONENT_UNITS: dict[str, str] = {
    "family_tax_credit": "a year",
    "in_work_tax_credit": "a year",
    "minimum_family_tax_credit": "a year",
    "best_start": "a year",
    "accommodation_supplement": "a week",
}

# One sentence per step id. Placeholders are the step's own input names and
# `result`; `$` marks a money amount, a bare placeholder a count or rate.
STEP_TEMPLATES: dict[str, str] = {
    "WFF_FTC_GROSS": (
        "Gross family tax credit is ${eldest_child_amount} for the eldest child plus "
        "${additional_child_amount} for each of {additional_children} other children: ${result}."
    ),
    "WFF_FTC_INCOME_EXCESS": (
        "Family scheme income of ${family_scheme_income} is ${result} (in complete dollars) over the "
        "${abatement_threshold} abatement threshold."
    ),
    "WFF_FTC_ABATEMENT": "Abatement is {abatement_rate} per dollar of that ${income_excess}: ${result}.",
    "WFF_FTC_NET": (
        "Family tax credit is the gross ${gross_family_tax_credit} less the ${abatement} abatement, "
        "not below zero: ${result}."
    ),
    "WFF_FTC_REMAINING_ABATEMENT": (
        "Abatement left over for the in-work tax credit is ${result} (the ${abatement} abatement less the "
        "${gross_family_tax_credit} gross family tax credit, not below zero)."
    ),
    "WFF_IWTC_GROSS": (
        "Gross in-work tax credit is the ${in_work_base} base plus ${additional_child_amount} for each of "
        "{children_beyond_three} children beyond three: ${result}."
    ),
    "WFF_IWTC_NET": (
        "In-work tax credit is the gross ${gross_in_work_tax_credit} less the ${remaining_abatement} "
        "abatement left after family tax credit, not below zero: ${result}."
    ),
    "WFF_MFTC_TOPUP": (
        "Minimum family tax credit tops ${net_family_scheme_income} of net family scheme income up to the "
        "${prescribed_amount} prescribed amount: ${result}."
    ),
    "WFF_BS_INCOME_EXCESS": (
        "Family scheme income of ${family_scheme_income} is ${result} (in complete dollars) over the "
        "${abatement_threshold} Best Start threshold."
    ),
    "WFF_BS_ABATEMENT": "Best Start abatement is {abatement_rate} per dollar of that ${income_excess}: ${result}.",
    "WFF_BS_NET": "Best Start is ${annual_amount} less the ${abatement} abatement, not below zero: ${result}.",
    "AS_QUALIFYING_COSTS": "Weekly qualifying accommodation costs are ${result}.",
    "AS_COST_EXCESS": (
        "Costs of ${weekly_qualifying_costs} are ${result} above the ${entry_threshold} entry threshold."
    ),
    "AS_COST_BASED_AMOUNT": "Costs are not above the entry threshold, so the cost-based amount is ${result}.",
    "AS_SUBSIDY": "The subsidy is {subsidy_rate} of the ${cost_excess} excess: ${result}.",
    "AS_AREA_CAP": "The ${subsidy} subsidy is limited to the ${area_maximum} area maximum: ${result}.",
    "AS_ASSET_IMPUTATION": "Cash assets of ${cash_assets} add ${result} of imputed weekly income.",
    "AS_TOTAL_INCOME": (
        "Weekly income for the income test is ${weekly_income} plus ${imputed_income} imputed: ${result}."
    ),
    "AS_INCOME_REDUCTION": (
        "Income of ${total_income} against the ${income_level} income level reduces the amount by ${result}."
    ),
    "AS_REDUCED_AMOUNT": (
        "The ${cost_based_amount} cost-based amount less the ${income_reduction} reduction, not below zero, "
        "is ${result}."
    ),
    "AS_ROUNDING": "${amount_before_rounding} rounded up to the complete dollar is ${result}.",
    # Task 7: the exact Schedule 1 Part A Table 1 band sum, before any final-output method (DEC-004).
    **{
        f"IT_BAND_{row}": "Basic-rate band {band}: ${dollars_in_band} of taxable income at {band_rate} is ${result}."
        for row in range(1, 6)
    },
    "IT_BASIC_TAX_SUM": "The bands for ${taxable_income} of taxable income sum to ${result}, unrounded.",
}


@dataclass(frozen=True)
class ExplanationStep:
    step_id: str
    rule_id: str
    text: str


@dataclass(frozen=True)
class EvidenceUsed:
    parameter_id: str
    value: str | None
    source_id: str | None
    locator: str | None
    effective_from: str | None
    effective_to: str | None
    review_status: str | None


@dataclass(frozen=True)
class Explanation:
    component_id: str
    outcome: str
    value: str | None
    summary: str
    steps: tuple[ExplanationStep, ...]
    # The caller-asserted facts the calculation read: the assumption
    # ledger. Poltika does not verify them (Task 21's conditional-simulation
    # wording); an explanation says so rather than presenting them as facts.
    assumptions: tuple[str, ...]
    evidence: tuple[EvidenceUsed, ...]
    code: str | None
    category: str | None
    missing_facts: tuple[str, ...]


def render_step(step: CalculationStep) -> str:
    """The sentence for one calculation step, from its own recorded values."""
    template = STEP_TEMPLATES.get(step.step_id)
    if template is None:
        raise ProvenanceError(f"no explanation template for calculation step '{step.step_id}'")
    values: dict[str, Any] = {name: plain(value) for name, value in step.inputs}
    values["result"] = plain(step.result)
    try:
        return template.format(**values)
    except KeyError as exc:
        raise ProvenanceError(f"step '{step.step_id}' did not record input {exc}") from None


def explain(component_id: str, result: ComponentResult) -> Explanation:
    """Explain one component result. The result must carry its trace."""
    if result.trace is None:
        raise ProvenanceError(f"component '{component_id}' has no trace to explain")
    label = COMPONENT_LABELS.get(component_id, component_id)
    unit = COMPONENT_UNITS.get(component_id, "")
    value = plain(result.value)
    applied = result.outcome == "calculated"
    steps = tuple(
        ExplanationStep(step_id=s.step_id, rule_id=s.rule_id, text=render_step(s)) for s in result.trace.steps
    ) if applied else ()
    if result.outcome == "calculated":
        summary = f"{label} is ${value} {unit}."
        if not steps:
            summary += " The verified facts establish no entitlement for the whole period, so no arithmetic was needed."
    elif result.outcome == "needs_review":
        summary = f"{label}: no amount is produced. It needs review: {result.reason}."
        if result.missing_facts:
            summary += f" Waiting for: {', '.join(result.missing_facts)}."
    else:
        kind = (
            "the verified facts meet a statutory exclusion"
            if result.category == "evidenced_exclusion"
            else "this case is outside what v0.1 models"
        )
        summary = f"{label} is not calculated, because {kind}: {result.reason}."
    assumptions = tuple(
        f"{use.name} = {_fact(plain(use.value))} (asserted by the {use.asserted_by}, not verified by Poltika)"
        for use in result.trace.inputs
    )
    evidence = tuple(
        EvidenceUsed(
            parameter_id=use.parameter_id,
            value=plain(use.value),
            source_id=use.source_id,
            locator=use.locator,
            effective_from=plain(use.effective_from),
            effective_to=plain(use.effective_to),
            review_status=use.review_status,
        )
        for use in result.trace.parameters
    )
    return Explanation(
        component_id=component_id,
        outcome=result.outcome,
        value=value,
        summary=summary,
        steps=steps,
        assumptions=assumptions,
        evidence=evidence,
        code=result.code,
        category=result.category,
        missing_facts=result.missing_facts,
    )


def explanation_to_dict(explanation: Explanation) -> dict[str, Any]:
    """The JSON form (Task 3.5)."""
    rendered: dict[str, Any] = plain(explanation)
    return rendered


def render_text(explanation: Explanation) -> str:
    """A plain-text rendering of the same content as the JSON form."""
    lines = [explanation.summary]
    if explanation.steps:
        lines += ["", "How it was calculated:"]
        lines += [f"{i}. {s.text} [{s.rule_id}]" for i, s in enumerate(explanation.steps, start=1)]
    if explanation.assumptions:
        lines += ["", "Facts the caller asserted:"]
        lines += [f"- {a}" for a in explanation.assumptions]
    if explanation.evidence:
        lines += ["", "Rates and thresholds used:"]
        for e in explanation.evidence:
            source = f"{e.source_id}, {e.locator}" if e.source_id else "no source (not resolved)"
            value = e.value if e.value is not None else "(no value)"
            lines.append(f"- {e.parameter_id} = {value} ({source}; {e.review_status or 'unresolved'})")
    return "\n".join(lines)


def _fact(value: Any) -> str:
    if isinstance(value, Enum):
        return _fact(value.value)
    if value is None:
        return "(not supplied)"
    if isinstance(value, list):
        return f"{len(value)} item(s)"
    if isinstance(value, dict):
        return ", ".join(f"{k}: {_fact(v)}" for k, v in value.items())
    return str(value)


_NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w])")


def verify(explanation: Explanation, result: ComponentResult) -> list[str]:
    """v0.1.5 Phase 5: the discrepancies between an explanation and the
    result it explains; empty when they agree. Checks that the value and
    outcome match, that the explained steps are exactly the recorded steps
    in order, and that every number in a step's sentence is one of that
    step's own recorded values."""
    problems: list[str] = []
    if result.trace is None:
        return ["result has no trace to verify"]
    expected = explain(result.trace.component_id, result)
    for name in ("component_id", "summary", "assumptions", "evidence", "code", "category", "missing_facts"):
        if getattr(explanation, name) != getattr(expected, name):
            problems.append(f"{name} does not match the recorded result")
    if explanation.outcome != result.outcome:
        problems.append(f"outcome {explanation.outcome} != {result.outcome}")
    if explanation.value != plain(result.value):
        problems.append(f"value {explanation.value} != {plain(result.value)}")
    stated = f"${explanation.value} " in explanation.summary
    if result.outcome == "calculated" and explanation.value is not None and not stated:
        problems.append("summary does not state the calculated value")
    recorded = result.trace.steps if result.trace is not None and result.outcome == "calculated" else ()
    if [s.step_id for s in explanation.steps] != [s.step_id for s in recorded]:
        problems.append("explained steps are not the recorded steps")
        return problems
    for explained, step in zip(explanation.steps, recorded):
        if explained.rule_id != step.rule_id:
            problems.append(f"{step.step_id}: rule does not match the recorded rule")
        if explained.text != render_step(step):
            problems.append(f"{step.step_id}: text does not match the recorded step")
        allowed = {str(plain(v)) for _, v in step.inputs} | {str(plain(step.result))}
        for number in _NUMBER.findall(explained.text.replace("$", " ")):
            if number not in allowed:
                problems.append(f"{step.step_id}: {number} is not a recorded value of this step")
        if str(plain(step.result)) not in explained.text:
            problems.append(f"{step.step_id}: the step's result is not stated")
    return problems
