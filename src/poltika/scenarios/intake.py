"""v0.3 Task 1b.4 (ADR-0016): ask for missing facts before running.

`next_step()` runs the household as it stands and decides the next
question for the components the caller asked about:

- `ready`: nothing blocks them. The run is complete as asked.
- `ask`: the next question, from the fact catalogue, with its admissible
  answers.
- `incomplete`: only facts the caller declined ("don't know") still block
  them. The caller gets a conditional answer (`scenarios/conditional.py`)
  instead of more questions.

Question order is deterministic:

1. finite facts (yes/no or category) that would unblock an asked
   component, by the impact on the asked components;
2. non-branchable facts (amounts, counts, attestations) blocking an
   asked component, in catalogue order;
3. any other finite fact blocking an asked component, by impact.

`apply_answer()` records an answer on the household, typed as the engine
field requires. An answer is the caller's assertion, as every `verified`
input already is. "Don't know" is not an answer: the caller adds the fact's
label to `declined`, so it is never asked again and never defaulted. An
attestation takes only "yes": one that can't be given is declined.

The planner decides what to ask. An LLM front end may only phrase the
catalogue question and map a reply to an admissible answer, with
confirmation (`doctrine/llm_boundaries.md`).
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal

from poltika.policy.loader import PolicyParameterSet
from poltika.scenarios.conditional import (
    COMPONENTS,
    FactIndex,
    MissingFact,
    Slot,
    assign,
    assign_number,
    resolve,
    set_value,
)
from poltika.scenarios.record import ScenarioRecord

Status = Literal["ready", "ask", "incomplete"]


@dataclass(frozen=True)
class IntakeStep:
    status: Status
    question: MissingFact | None
    remaining: tuple[MissingFact, ...]  # everything still blocking the asked components


def next_step(
    record: ScenarioRecord,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    facts: FactIndex,
    *,
    asked: Collection[str] = COMPONENTS,
    declined: Collection[str] = (),
    wff_parameters: PolicyParameterSet | None = None,
    as_parameters: PolicyParameterSet | None = None,
) -> IntakeStep:
    unknown = [c for c in asked if c not in COMPONENTS]
    if unknown or not asked:
        raise ValueError(f"unknown or empty components asked: {unknown or list(asked)}")
    res = resolve(
        record,
        wff_policy_dir,
        as_policy_dir,
        facts,
        max_branches=1,  # the planner needs the ranking, not the branches
        impact_components=asked,
        wff_parameters=wff_parameters,
        as_parameters=as_parameters,
    )
    blocking = tuple(m for m in res.missing if set(m.blocks) & set(asked))
    open_facts = [m for m in blocking if m.slot.label not in declined]
    if not blocking:
        return IntakeStep("ready", None, ())
    if not open_facts:
        return IntakeStep("incomplete", None, blocking)

    ranked = [m for m in res.ranked if m in open_facts]
    unblocking = [m for m in ranked if set(res.unblocks.get(m.slot, ())) & set(asked)]
    catalog_order = {key: i for i, key in enumerate(facts)}
    numeric = sorted(
        (m for m in open_facts if not m.branchable),
        key=lambda m: catalog_order[(m.slot.scope, m.slot.fact_id)],
    )
    rest = [m for m in ranked if m not in unblocking]
    order = [*unblocking, *numeric, *rest]
    return IntakeStep("ask", order[0], blocking)


def slot_from_label(label: str) -> Slot:
    """The slot a `Slot.label` names: `wff.partner_status`,
    `children[0].best_start_cohort`, `household.as_claimant_is_wff_claimant_or_partner`."""
    if label.startswith("children["):
        index, sep, name = label.removeprefix("children[").partition("].")
        if not sep or not index.isascii() or not index.isdigit() or not name:
            raise ValueError(f"'{label}' is not a fact label")
        return Slot("wff", name, int(index))
    scope, sep, name = label.partition(".")
    if not sep or not name or scope not in ("wff", "accommodation_supplement", "household"):
        raise ValueError(f"'{label}' is not a fact label")
    if scope == "wff" and name.startswith("children."):
        raise ValueError(f"'{label}' must name a child using children[index].field")
    return Slot(scope, name)


def fact_for(record: ScenarioRecord, label: str, facts: FactIndex) -> MissingFact:
    """The catalogued fact a label names, for `apply_answer()`. A child
    label must name a child the household has."""
    slot = slot_from_label(label)
    entry = facts.get((slot.scope, slot.fact_id))
    if entry is None:
        raise ValueError(f"'{label}' is not a catalogued fact")
    if slot.child is not None and slot.child >= len(record.household.wff.children):
        raise ValueError(f"'{label}' names a child the household doesn't have")
    return MissingFact(slot, entry, ())


def apply_answer(record: ScenarioRecord, fact: MissingFact, answer: str) -> ScenarioRecord:
    """The household with `answer` recorded for `fact`."""
    entry, slot = fact.entry, fact.slot
    if entry.finite:
        if answer not in entry.domain():
            raise ValueError(
                f"'{answer}' is not an admissible answer to {slot.label}: {list(entry.domain())}"
            )
        return assign(record, slot, answer)
    if entry.kind == "attestation":
        # "No" leaves the fact unmet, so the planner would ask again: the
        # caller declines it instead.
        if answer != "yes":
            raise ValueError(f"{slot.label} takes 'yes'; if it can't be attested, decline it")
        return set_value(record, slot, True)
    if entry.kind == "count":
        if not (answer.isascii() and answer.isdigit()):
            raise ValueError(f"{slot.label} takes a whole number")
        return assign_number(record, slot, int(answer))
    try:
        amount = Decimal(answer)
    except InvalidOperation as exc:
        raise ValueError(f"{slot.label} takes an amount in {entry.unit}") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{slot.label} takes a non-negative amount in {entry.unit}")
    return assign_number(record, slot, amount)
