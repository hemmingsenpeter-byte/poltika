"""v0.2 Tasks 8.6-8.7: withdrawal rates along an income path, and
deterministic parameter sweeps.

**Withdrawal rates (8.6).** For one household, the policy's own income fact
is stepped through a list of values and the household is rerun through
`run_combined_household` at each. The rate between two points is
`-(change in entitlement) / (change in income)`, and only where the
component was calculated at both points.

- WFF steps the claimant's `family_scheme_income` (annual, per tax year),
  with any partner's amount unchanged. A recorded `net_family_scheme_income`
  can't be derived for the new income, so it is cleared. The minimum family
  tax credit, which depends on it, then reads `needs_review` along the path
  rather than using a stale figure.
- The Accommodation Supplement steps `weekly_income` (weekly).

These are *WFF and AS withdrawal rates*, never effective marginal tax
rates: income tax and other benefits aren't modelled (R3). The two policies
define income differently (family scheme income, and chargeable income), so
a combined withdrawal rate needs a stated mapping between them. That
mapping isn't assumed here. Each path is a labelled hypothetical, not a
claim about any real household.

**Sweeps (8.7).** One run per value of one parameter, each an ordinary
`set` reform, so every point has its own `run_id`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from itertools import pairwise
from pathlib import Path
from typing import Literal

from poltika.engines.simulator.wff import VerifiedIncome
from poltika.scenarios.combined import CombinedResult, run_combined_household
from poltika.scenarios.microsim.reform import Operation, Override, Reform
from poltika.scenarios.microsim.runner import (
    AS_COMPONENT,
    WFF_COMPONENTS,
    PopulationRun,
    run_population,
)
from poltika.scenarios.record import CodeIdentity, ScenarioRecord
from poltika.semantics.population import PopulationDataset

IncomePolicy = Literal["working_for_families", "accommodation_supplement"]


@dataclass(frozen=True)
class PathPoint:
    income: Decimal
    values: dict[str, Decimal | None]  # component -> value, None unless calculated


@dataclass(frozen=True)
class WithdrawalStep:
    income_from: Decimal
    income_to: Decimal
    rates: dict[str, Decimal | None]  # component -> rate, None unless calculated at both ends


@dataclass(frozen=True)
class WithdrawalPath:
    policy: IncomePolicy
    income_fact: str
    unit: str
    points: tuple[PathPoint, ...]
    steps: tuple[WithdrawalStep, ...]


def withdrawal_path(
    record: ScenarioRecord,
    policy: IncomePolicy,
    incomes: Sequence[Decimal],
    wff_policy_dir: Path,
    as_policy_dir: Path,
) -> WithdrawalPath:
    ordered = sorted(set(incomes))
    if len(ordered) < 2 or ordered[0] < 0:
        raise ValueError("need at least two distinct non-negative incomes")
    components = WFF_COMPONENTS if policy == "working_for_families" else (AS_COMPONENT,)
    points = []
    for income in ordered:
        result = _run(_with_income(record, policy, income), wff_policy_dir, as_policy_dir)
        values: dict[str, Decimal | None] = {}
        for c in components:
            component = (
                result.accommodation_supplement if c == AS_COMPONENT else getattr(result.wff, c)
            )
            values[c] = component.value if component.outcome == "calculated" else None
        points.append(PathPoint(income, values))
    steps = []
    for a, b in pairwise(points):
        rates: dict[str, Decimal | None] = {}
        for c in components:
            va, vb = a.values[c], b.values[c]
            rates[c] = None if va is None or vb is None else -(vb - va) / (b.income - a.income)
        steps.append(WithdrawalStep(a.income, b.income, rates))
    if policy == "working_for_families":
        fact, unit = "family_scheme_income (claimant; partner unchanged)", "NZD per tax year"
    else:
        fact, unit = "weekly_income", "NZD per week"
    return WithdrawalPath(policy, fact, unit, tuple(points), tuple(steps))


def sweep(
    population: PopulationDataset,
    policy_id: str,
    parameter_id: str,
    values: Sequence[Decimal],
    wff_policy_dir: Path,
    as_policy_dir: Path,
    *,
    code: CodeIdentity,
) -> list[tuple[Decimal, PopulationRun]]:
    runs = []
    for value in values:
        reform = Reform(
            reform_id=f"sweep {policy_id}.{parameter_id}={value}",
            overrides=(
                Override(
                    policy_id=policy_id,
                    parameter_id=parameter_id,
                    operation=Operation.SET,
                    value=value,
                ),
            ),
        )
        runs.append(
            (value, run_population(population, reform, wff_policy_dir, as_policy_dir, code=code))
        )
    return runs


def _with_income(record: ScenarioRecord, policy: IncomePolicy, income: Decimal) -> ScenarioRecord:
    household = record.household
    if policy == "working_for_families":
        current = household.wff.family_scheme_income
        partner = None if current is None else current.partner_amount
        wff = replace(
            household.wff,
            family_scheme_income=VerifiedIncome(income, partner),
            net_family_scheme_income=None,
            net_family_scheme_income_me3_attested=False,
        )
        return replace(record, household=replace(household, wff=wff))
    as_ = replace(household.accommodation_supplement, weekly_income=income)
    return replace(record, household=replace(household, accommodation_supplement=as_))


def _run(record: ScenarioRecord, wff_policy_dir: Path, as_policy_dir: Path) -> CombinedResult:
    return run_combined_household(
        wff_policy_dir,
        as_policy_dir,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )
