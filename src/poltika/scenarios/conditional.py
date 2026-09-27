"""v0.3 Task 1b.2 (ADR-0016): conditional answers when facts are missing.

`resolve()` runs a household and, for every component blocked by an unknown
fact with a finite domain (a `fact_status` or `enum` catalogue entry),
reruns the household once per admissible answer. It does this jointly,
applying one assignment to the whole household, and expands further as
each branch reveals the next blocking fact, up to `max_branches`. It never
calculates anything itself. Every branch is an ordinary
`run_combined_household` call on the household with those facts filled
in.

What it returns (`Resolution`):

- `base`: the household's own result, unchanged. A blocked component is
  still `needs_review`, and nothing here is ever marked `calculated`.
- `missing`: every unknown fact blocking the base result, with its
  catalogue question and whether it can be branched on.
- `branches`: one per joint assignment. Each has the full combined result
  and any facts it still couldn't resolve (numeric facts, or facts left
  when the cap was reached).
- `bounds`: per component, and for the WFF total, the range of calculated
  values across branches and how many branches were calculated. A range
  is complete only when every branch is calculated.
- `next_question`: the unknown fact whose answer matters most. Facts that
  unblock the most components come first, then those that change the most
  outcomes, then those with the widest spread of amounts, then rule and
  catalogue order. Impact is measured by rerunning the household once per
  admissible value of each fact.

Numeric facts (income, costs, assets, counts) have no finite domain. With
no range they are listed as missing, without branches. With a range
(`ranges`, v0.3 Task 1b.2b), the household is also branched at each
range's two endpoints, jointly with the finite facts. Each component's
`Bounds.kind` then says what its range means:

- `bounds`: every ranged fact's catalogue entry declares this component
  monotone in it, with a rule id, so the endpoints give true bounds: any
  value inside the ranges gives a result inside them. A property test
  checks each declaration against the engine.
- `points`: some ranged fact has no such declaration, so the figures are
  values at the endpoints only, not bounds.

Branches over unresolved rate values are a later ADR-0016 task (1b.2c).
"""

from __future__ import annotations

import types
import typing
from collections.abc import Collection
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from poltika.engines.simulator.outcome import ComponentResult, FactStatus
from poltika.engines.simulator.wff import BestStartCohort, PartnerStatus, VerifiedIncome
from poltika.policy.loader import PolicyParameterSet
from poltika.scenarios.combined import CombinedResult, run_combined_household
from poltika.scenarios.record import ScenarioRecord
from poltika.semantics.schemas.fact_catalog import FactEntry

WFF_COMPONENTS = (
    "family_tax_credit",
    "in_work_tax_credit",
    "minimum_family_tax_credit",
    "best_start",
)
AS_COMPONENT = "accommodation_supplement"
COMPONENTS = (*WFF_COMPONENTS, AS_COMPONENT)
WFF_TOTAL = "wff_total"
_UNKNOWN = (None, FactStatus.UNKNOWN, PartnerStatus.UNKNOWN, BestStartCohort.UNKNOWN)

FactIndex = dict[tuple[str, str], FactEntry]


class UncataloguedFactError(LookupError):
    """An engine reported a missing fact that has no catalogue entry."""


class IncompatibleAssignmentError(ValueError):
    """An enum answer contradicts facts already supplied to the scenario."""


@dataclass(frozen=True, order=True)
class Slot:
    """One place a fact is unknown: a household-, WFF- or AS-level field,
    or a field of one child."""

    scope: str
    field: str
    child: int | None = None

    @property
    def fact_id(self) -> str:
        return f"children.{self.field}" if self.child is not None else self.field

    @property
    def label(self) -> str:
        return (
            f"children[{self.child}].{self.field}"
            if self.child is not None
            else f"{self.scope}.{self.field}"
        )


@dataclass(frozen=True)
class MissingFact:
    slot: Slot
    entry: FactEntry
    blocks: tuple[str, ...]  # components it blocks in the base result

    @property
    def branchable(self) -> bool:
        return self.entry.finite


@dataclass(frozen=True)
class Branch:
    assignment: tuple[tuple[Slot, str], ...]
    result: CombinedResult
    unresolved: tuple[str, ...]  # slot labels still unknown in this branch


BoundsKind = typing.Literal["bounds", "points"]


@dataclass(frozen=True)
class Bounds:
    low: Decimal | None
    high: Decimal | None
    calculated: int
    branches: int
    # "points" when a ranged numeric fact isn't declared monotone for this
    # component: the figures are values at the range endpoints, not bounds.
    kind: BoundsKind = "bounds"

    @property
    def complete(self) -> bool:
        return self.calculated == self.branches and self.branches > 0


@dataclass(frozen=True)
class Resolution:
    base: CombinedResult
    known: dict[str, Decimal]  # components calculated regardless
    missing: tuple[MissingFact, ...]
    branches: tuple[Branch, ...]
    bounds: dict[str, Bounds]
    capped: bool
    next_question: MissingFact | None
    ranked: tuple[MissingFact, ...]  # finite missing facts, highest impact first
    unblocks: dict[Slot, tuple[str, ...]]  # components each finite fact can unblock


def resolve(
    record: ScenarioRecord,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    facts: FactIndex,
    *,
    max_branches: int = 32,
    impact_components: Collection[str] = COMPONENTS,
    ranges: typing.Mapping[Slot, tuple[Decimal, Decimal]] | None = None,
    wff_parameters: PolicyParameterSet | None = None,
    as_parameters: PolicyParameterSet | None = None,
) -> Resolution:
    """Resolve all components; `impact_components` limits only question
    ranking. `ranges` gives (low, high) for missing numeric facts."""
    if max_branches < 1:
        raise ValueError("max_branches must be at least 1")
    unknown = set(impact_components) - set(COMPONENTS)
    if unknown or not impact_components:
        raise ValueError(f"unknown or empty impact components: {sorted(unknown)}")
    ranked_components = tuple(c for c in COMPONENTS if c in impact_components)

    def run(r: ScenarioRecord) -> CombinedResult:
        return run_combined_household(
            wff_policy_dir,
            as_policy_dir,
            r.household,
            wff_lookup_date=r.wff_lookup_date,
            as_lookup_date=r.as_lookup_date,
            assessment_week=r.assessment_week,
            requested_wff_policy_version=r.requested_wff_policy_version,
            requested_as_policy_version=r.requested_as_policy_version,
            wff_parameters=wff_parameters,
            as_parameters=as_parameters,
        )

    base = run(record)
    missing = _missing(record, base, facts)
    order, unblocks = _impact_order(
        record, base, [m for m in missing if m.branchable], run, ranked_components
    )

    ranged = _check_ranges(ranges or {}, missing, max_branches)
    leaves: list[tuple[tuple[tuple[Slot, str], ...], ScenarioRecord, CombinedResult]] = [
        ((), record, base)
    ]
    for slot, (low, high) in ranged.items():
        ends = (low,) if low == high else (low, high)
        leaves = [
            ((*assignment, (slot, str(end))), rec2, run(rec2))
            for assignment, rec, _ in leaves
            for end in ends
            for rec2 in (assign_number(rec, slot, end),)
        ]
    capped = False
    while True:
        expanded = False
        next_leaves: list[tuple[tuple[tuple[Slot, str], ...], ScenarioRecord, CombinedResult]] = []
        for i, (assignment, rec, result) in enumerate(leaves):
            candidates, _ = _impact_order(
                rec, result, [m for m in _missing(rec, result, facts) if m.branchable],
                run, ranked_components,
            )
            if not candidates:
                next_leaves.append((assignment, rec, result))
                continue
            slot = candidates[0].slot
            assignments = _assignments(rec, candidates[0])
            projected = len(next_leaves) + len(assignments) + (len(leaves) - i - 1)
            if projected > max_branches:
                capped = True
                next_leaves.append((assignment, rec, result))
                continue
            for value, branch_record in assignments:
                next_leaves.append(
                    ((*assignment, (slot, value)), branch_record, run(branch_record))
                )
            expanded = True
        leaves = next_leaves
        if not expanded:
            break

    branches = tuple(
        Branch(
            assignment=assignment,
            result=result,
            unresolved=tuple(sorted(m.slot.label for m in _missing(rec, result, facts))),
        )
        for assignment, rec, result in leaves
    )
    known = {
        c: r.value
        for c in COMPONENTS
        if (r := component(base, c)).outcome == "calculated" and r.value is not None
    }
    return Resolution(
        base=base,
        known=known,
        missing=tuple(missing),
        branches=branches,
        bounds=_bounds(branches, _kinds(ranged, facts)),
        capped=capped,
        next_question=order[0] if order else (next((m for m in missing), None)),
        ranked=tuple(order),
        unblocks=unblocks,
    )


def component(result: CombinedResult, name: str) -> ComponentResult:
    return result.accommodation_supplement if name == AS_COMPONENT else getattr(result.wff, name)


def assign(record: ScenarioRecord, slot: Slot, value: str) -> ScenarioRecord:
    """The record with one unknown fact set to an admissible value, typed as
    the engine field requires."""
    household = record.household
    if slot.scope == "household":
        return replace(record, household=_set(household, slot.field, value))
    if slot.scope == "accommodation_supplement":
        return replace(
            record,
            household=replace(
                household,
                accommodation_supplement=_set(
                    household.accommodation_supplement, slot.field, value
                ),
            ),
        )
    wff = household.wff
    if slot.child is None:
        return replace(record, household=replace(household, wff=_set(wff, slot.field, value)))
    children = list(wff.children)
    children[slot.child] = _set(children[slot.child], slot.field, value)
    return replace(record, household=replace(household, wff=replace(wff, children=children)))


def assign_number(record: ScenarioRecord, slot: Slot, value: Decimal | int) -> ScenarioRecord:
    """The record with a numeric fact set (a money amount or a count). The
    claimant's family scheme income keeps any partner amount, and the
    partner's needs the claimant's first."""
    if slot.field == "family_scheme_income":
        current = record.household.wff.family_scheme_income
        partner = None if current is None else current.partner_amount
        return set_value(record, slot, VerifiedIncome(Decimal(value), partner))
    if slot.field == "family_scheme_income.partner_amount":
        current = record.household.wff.family_scheme_income
        if current is None:
            raise ValueError("record the claimant's family scheme income before the partner's")
        return set_value(
            record,
            Slot("wff", "family_scheme_income"),
            VerifiedIncome(current.claimant_amount, Decimal(value)),
        )
    return set_value(record, slot, value)


def set_value(record: ScenarioRecord, slot: Slot, value: Any) -> ScenarioRecord:
    """The record with one household-, WFF- or AS-level field set directly."""
    household = record.household
    changes: dict[str, Any] = {slot.field: value}
    if slot.scope == "accommodation_supplement":
        as_ = replace(household.accommodation_supplement, **changes)
        return replace(record, household=replace(household, accommodation_supplement=as_))
    if slot.scope == "wff" and slot.child is None:
        return replace(record, household=replace(household, wff=replace(household.wff, **changes)))
    raise ValueError(f"{slot.label} can't take a direct value")


def _set(obj: Any, name: str, value: str) -> Any:
    typed = _enum_type(type(obj), name)(value)
    try:
        return replace(obj, **{name: typed})
    except ValueError as exc:
        raise IncompatibleAssignmentError(str(exc)) from exc


def _assignments(record: ScenarioRecord, missing: MissingFact) -> list[tuple[str, ScenarioRecord]]:
    assignments = []
    for value in missing.entry.domain():
        try:
            assigned = assign(record, missing.slot, value)
        except IncompatibleAssignmentError:
            # Keep supplied facts intact; only structurally valid scenarios can run.
            continue
        assignments.append((value, assigned))
    if not assignments:
        raise ValueError(f"No compatible answers for {missing.slot.label}")
    return assignments


def _enum_type(cls: type, name: str) -> type[Enum]:
    hint = typing.get_type_hints(cls)[name]
    candidates = (
        typing.get_args(hint)
        if isinstance(hint, types.UnionType) or typing.get_origin(hint) is typing.Union
        else (hint,)
    )
    for candidate in candidates:
        if isinstance(candidate, type) and issubclass(candidate, Enum):
            return candidate
    raise TypeError(f"{cls.__name__}.{name} is not an enum field")


def _entry(facts: FactIndex, scope: str, fact_id: str) -> tuple[str, FactEntry]:
    """The catalogue entry for a reported fact. Household-level facts (the
    combined run's claimant link) are looked up in the household scope."""
    for s in (scope, "household"):
        if (s, fact_id) in facts:
            return s, facts[(s, fact_id)]
    raise UncataloguedFactError(f"'{fact_id}' reported by {scope} has no fact catalogue entry")


def _slots(record: ScenarioRecord, scope: str, entry: FactEntry) -> list[Slot]:
    household = record.household
    if entry.kind not in ("fact_status", "enum"):
        return [Slot(scope, entry.id)]  # numeric: one slot, never branched
    if scope == "household":
        return [Slot(scope, entry.id)] if getattr(household, entry.id) in _UNKNOWN else []
    if scope == "accommodation_supplement":
        return (
            [Slot(scope, entry.id)]
            if getattr(household.accommodation_supplement, entry.id) in _UNKNOWN
            else []
        )
    if entry.id.startswith("children."):
        name = entry.id.removeprefix("children.")
        return [
            Slot(scope, name, i)
            for i, c in enumerate(household.wff.children)
            if getattr(c, name) in _UNKNOWN
        ]
    return [Slot(scope, entry.id)] if getattr(household.wff, entry.id) in _UNKNOWN else []


def _missing(record: ScenarioRecord, result: CombinedResult, facts: FactIndex) -> list[MissingFact]:
    found: dict[Slot, tuple[FactEntry, set[str]]] = {}
    for name in COMPONENTS:
        r = component(result, name)
        if r.outcome != "needs_review":
            continue
        own_scope = AS_COMPONENT if name == AS_COMPONENT else "wff"
        for fact_id in r.missing_facts:
            scope, entry = _entry(facts, own_scope, fact_id)
            for slot in _slots(record, scope, entry):
                found.setdefault(slot, (entry, set()))[1].add(name)
    catalog_order = {key: i for i, key in enumerate(facts)}
    ordered = sorted(
        found.items(),
        key=lambda item: (
            item[1][0].rule,
            catalog_order[(item[0].scope, item[0].fact_id)],
            item[0],
        ),
    )
    return [
        MissingFact(slot, entry, tuple(sorted(blocks)))
        for slot, (entry, blocks) in ordered
    ]


def _impact_order(
    record: ScenarioRecord,
    base: CombinedResult,
    candidates: list[MissingFact],
    run: typing.Callable[[ScenarioRecord], CombinedResult],
    components: tuple[str, ...],
) -> tuple[list[MissingFact], dict[Slot, tuple[str, ...]]]:
    unblocks: dict[Slot, tuple[str, ...]] = {}

    def impact(m: MissingFact) -> tuple[int, int, Decimal]:
        results = [run(assigned) for _, assigned in _assignments(record, m)]
        unblocked_names: list[str] = []
        changed = 0
        spread = Decimal(0)
        for name in components:
            outs = [component(r, name) for r in results]
            if component(base, name).outcome == "needs_review" and any(
                o.outcome != "needs_review" for o in outs
            ):
                unblocked_names.append(name)
            if len({(o.outcome, o.value) for o in outs}) > 1:
                changed += 1
            values = [o.value for o in outs if o.outcome == "calculated" and o.value is not None]
            if values:
                spread += max(values) - min(values)
        unblocks[m.slot] = tuple(unblocked_names)
        return len(unblocked_names), changed, spread

    scored = [(impact(m), m) for m in candidates]
    ordered = [
        m
        for score, m in sorted(scored, key=lambda sm: (-sm[0][0], -sm[0][1], -sm[0][2]))
    ]
    return ordered, unblocks


def _check_ranges(
    ranges: typing.Mapping[Slot, tuple[Decimal, Decimal]],
    missing: list[MissingFact],
    max_branches: int,
) -> dict[Slot, tuple[Decimal | int, Decimal | int]]:
    """Ranges only for missing numeric facts, well formed, within the cap."""
    numeric = {m.slot: m.entry for m in missing if not m.branchable}
    checked: dict[Slot, tuple[Decimal | int, Decimal | int]] = {}
    for slot, (low, high) in sorted(ranges.items()):
        entry = numeric.get(slot)
        if entry is None or entry.kind not in ("money", "count"):
            raise ValueError(f"{slot.label} is not a missing amount or count, so it can't take a range")
        lo, hi = Decimal(low), Decimal(high)
        if not (lo.is_finite() and hi.is_finite()) or lo < 0 or lo > hi:
            raise ValueError(f"{slot.label}: a range needs 0 <= low <= high, got {low} to {high}")
        if entry.kind == "count":
            if lo != lo.to_integral_value() or hi != hi.to_integral_value():
                raise ValueError(f"{slot.label} is a count: its range must be whole numbers")
            checked[slot] = (int(lo), int(hi))
        else:
            checked[slot] = (lo, hi)
    corners = 1
    for ends in checked.values():
        corners *= 1 if ends[0] == ends[1] else 2
    if corners > max_branches:
        raise ValueError(f"{len(checked)} ranges need {corners} runs, over the cap of {max_branches}")
    return checked


def _kinds(
    ranged: typing.Mapping[Slot, object], facts: FactIndex
) -> dict[str, BoundsKind]:
    """`bounds` where every ranged fact is declared monotone for the
    component; the WFF total also needs its components to agree in direction."""
    declared = [facts[(s.scope, s.fact_id)].monotone or {} for s in ranged]
    kinds: dict[str, BoundsKind] = {
        c: "bounds" if all(c in d for d in declared) else "points" for c in COMPONENTS
    }
    total_ok = all(
        all(c in d for c in WFF_COMPONENTS)
        and len({d[c].direction for c in WFF_COMPONENTS}) == 1
        for d in declared
    )
    kinds[WFF_TOTAL] = "bounds" if total_ok else "points"
    return kinds


def _bounds(branches: tuple[Branch, ...], kinds: dict[str, BoundsKind]) -> dict[str, Bounds]:
    out: dict[str, Bounds] = {}
    for name in (*COMPONENTS, WFF_TOTAL):
        values: list[Decimal] = []
        for b in branches:
            if name == WFF_TOTAL:
                total = b.result.wff.total_annual_entitlement()
                if total is not None:
                    values.append(total)
            else:
                r = component(b.result, name)
                if r.outcome == "calculated" and r.value is not None:
                    values.append(r.value)
        out[name] = Bounds(
            min(values, default=None),
            max(values, default=None),
            len(values),
            len(branches),
            kinds[name],
        )
    return out
