"""v0.3 Task 1b.6 (ADR-0016): population ranges for `needs_review` households.

The v0.2 fiscal table (`analysis.fiscal`) counts only households whose
component was calculated in both runs. This adds what can be said about
the rest, without changing the run or its figures:

- For each household with a `needs_review` change, the conditional
  resolver (`scenarios/conditional.py`) branches the household over its
  missing facts under the **baseline** parameters. Each branch's
  assignment is then rerun under the **reform** parameters, so both runs
  of a branch make the same assumption. The branch's change is reform
  minus baseline.
- The household is **bounded** for a component when every branch
  calculated it in both runs and the branch cap wasn't reached. Its
  weighted lowest and highest branch change are added to the range.
- Otherwise it is **unboundable**: a missing amount (no finite branches),
  a rate that is itself `needs_review`, a branch that is unsupported, the
  cap, or a household validation marked `needs_review`.

The result keeps three figures apart, and never adds them: the calculated
total, the low-to-high range from bounded households, and the weight still
unboundable. With the unsupported weight they account for every household
that ran.

This is an analysis over a finished run. `run_id`, `results_sha256` and the
calculated totals are unchanged, and nothing here is labelled calculated.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.combined import run_combined_household
from poltika.scenarios.conditional import FactIndex, assign, component, resolve
from poltika.scenarios.microsim.reform import apply_reform
from poltika.scenarios.microsim.runner import COMPONENTS, UNITS, PopulationRun
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.record import ScenarioRecord

Parameters = tuple[PolicyParameterSet, PolicyParameterSet]  # (baseline, reform)


@dataclass(frozen=True)
class ComponentRange:
    component: str
    unit: str
    calculated_weight: Decimal
    calculated_delta: Decimal  # as analysis.fiscal: households calculated in both runs
    bounded_households: int
    bounded_weight: Decimal
    delta_low: Decimal  # weighted: the sum over bounded households of their lowest branch change
    delta_high: Decimal
    baseline_low: Decimal  # the same for the baseline amount itself
    baseline_high: Decimal
    unboundable_weight: Decimal
    unsupported_weight: Decimal


def population_ranges(
    run: PopulationRun,
    wff_policy_dir: Path,
    as_policy_dir: Path,
    facts: FactIndex,
    *,
    max_branches: int = 32,
) -> dict[str, ComponentRange]:
    """Per component, the three separate figures for a finished run."""
    records = {
        h.household_id: h.record for h in run.validation.households if h.record is not None
    }
    loaded: dict[tuple[str, date, str], Parameters] = {}

    def parameters(policy_dir: Path, lookup: date, version: str) -> Parameters:
        key = (str(policy_dir), lookup, version)
        if key not in loaded:
            baseline = load_policy_parameters(policy_dir, lookup, requested_policy_version=version)
            loaded[key] = (baseline, apply_reform(baseline, run.reform))
        return loaded[key]

    zero = Decimal(0)
    acc = {
        c: {
            "calculated_weight": zero,
            "calculated_delta": zero,
            "bounded_households": zero,
            "bounded_weight": zero,
            "delta_low": zero,
            "delta_high": zero,
            "baseline_low": zero,
            "baseline_high": zero,
            "unboundable_weight": zero,
            "unsupported_weight": zero,
        }
        for c in COMPONENTS
    }
    for h in run.households:
        pending = [c for c in COMPONENTS if h.components[c].outcome == "needs_review"]
        for c in COMPONENTS:
            d = h.components[c]
            if d.outcome == "calculated":
                assert d.delta is not None
                acc[c]["calculated_weight"] += h.weight
                acc[c]["calculated_delta"] += d.delta * h.weight
            elif d.outcome == "unsupported":
                acc[c]["unsupported_weight"] += h.weight
        if not pending:
            continue
        record = records[h.household_id]
        spans = (
            {}
            if h.record_status is RecordStatus.NEEDS_REVIEW
            else _household_spans(
                record, pending, wff_policy_dir, as_policy_dir, facts, parameters, max_branches
            )
        )
        for c in pending:
            span = spans.get(c)
            if span is None:
                acc[c]["unboundable_weight"] += h.weight
                continue
            (d_low, d_high), (b_low, b_high) = span
            acc[c]["bounded_households"] += 1
            acc[c]["bounded_weight"] += h.weight
            acc[c]["delta_low"] += d_low * h.weight
            acc[c]["delta_high"] += d_high * h.weight
            acc[c]["baseline_low"] += b_low * h.weight
            acc[c]["baseline_high"] += b_high * h.weight
    return {
        c: ComponentRange(
            component=c,
            unit=UNITS[c],
            calculated_weight=a["calculated_weight"],
            calculated_delta=a["calculated_delta"],
            bounded_households=int(a["bounded_households"]),
            bounded_weight=a["bounded_weight"],
            delta_low=a["delta_low"],
            delta_high=a["delta_high"],
            baseline_low=a["baseline_low"],
            baseline_high=a["baseline_high"],
            unboundable_weight=a["unboundable_weight"],
            unsupported_weight=a["unsupported_weight"],
        )
        for c, a in acc.items()
    }


Span = tuple[tuple[Decimal, Decimal], tuple[Decimal, Decimal]]


def _household_spans(
    record: ScenarioRecord,
    pending: list[str],
    wff_policy_dir: Path,
    as_policy_dir: Path,
    facts: FactIndex,
    parameters: Callable[[Path, date, str], Parameters],
    max_branches: int,
) -> dict[str, Span]:
    """Per pending component, ((lowest, highest) change, (lowest, highest)
    baseline amount) across branches, when every branch is calculated in
    both runs. A component left out is unboundable."""
    wff_base, wff_reform = parameters(
        wff_policy_dir, record.wff_lookup_date, record.requested_wff_policy_version
    )
    as_base, as_reform = parameters(
        as_policy_dir, record.as_lookup_date, record.requested_as_policy_version
    )
    res = resolve(
        record,
        wff_policy_dir,
        as_policy_dir,
        facts,
        max_branches=max_branches,
        wff_parameters=wff_base,
        as_parameters=as_base,
    )
    if res.capped or not any(b.assignment for b in res.branches):
        return {}  # nothing finite to branch on, or not every branch was reached
    changes: dict[str, list[Decimal]] = {c: [] for c in pending}
    baselines: dict[str, list[Decimal]] = {c: [] for c in pending}
    for branch in res.branches:
        branched = record
        for slot, value in branch.assignment:
            branched = assign(branched, slot, value)
        reformed = run_combined_household(
            wff_policy_dir,
            as_policy_dir,
            branched.household,
            wff_lookup_date=branched.wff_lookup_date,
            as_lookup_date=branched.as_lookup_date,
            assessment_week=branched.assessment_week,
            requested_wff_policy_version=branched.requested_wff_policy_version,
            requested_as_policy_version=branched.requested_as_policy_version,
            wff_parameters=wff_reform,
            as_parameters=as_reform,
        )
        for c in pending:
            before, after = component(branch.result, c), component(reformed, c)
            if (
                before.outcome == "calculated"
                and after.outcome == "calculated"
                and before.value is not None
                and after.value is not None
                and c in changes
            ):
                changes[c].append(after.value - before.value)
                baselines[c].append(before.value)
            else:
                changes.pop(c, None)  # one incomplete branch leaves it unboundable
    return {
        c: ((min(v), max(v)), (min(baselines[c]), max(baselines[c])))
        for c, v in changes.items()
        if v
    }
