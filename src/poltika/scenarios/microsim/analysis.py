"""v0.2 Phase 8 (Tasks 8.1-8.5) and Task 4.2: tables from a population run.

Every table is weighted, and every table says what it left out. A
household is counted only where its result supports the figure. Nothing
`needs_review` or `unsupported` is ever counted as zero.

**Component sets.** A household's change is the sum of the deltas of a
named set of components, and only when every one of them was calculated in
both runs. The set must share one unit: WFF components per tax year, or
the Accommodation Supplement per week (D8). This is how a family tax
credit reform is measured while the 2026-27 in-work tax credit is
`needs_review` (R4). The set is named on every table, and a partial set is
never labelled total WFF.

**Classes.** `gain` or `loss` when the change is non-zero, `no_change`
when it is zero, otherwise `needs_review` or `unsupported` (the worse of
its components).

**Deciles** rank households by `gross_household_income` (D3), using
`weighted_quantile_cuts`. A household belongs to decile `k` when its income
is above cut `k-1` and at most cut `k`. Households with unknown income are
left out of the decile table and counted.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import StrEnum

from poltika.scenarios.microsim.runner import COMPONENTS, UNITS, HouseholdResult, PopulationRun
from poltika.scenarios.microsim.weighting import (
    weighted_mean,
    weighted_median,
    weighted_quantile_cuts,
)
from poltika.scenarios.population import dependent_children, household_type
from poltika.semantics.population import PopulationDataset, PopulationHousehold


class ChangeClass(StrEnum):
    GAIN = "gain"
    LOSS = "loss"
    NO_CHANGE = "no_change"
    NEEDS_REVIEW = "needs_review"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class HouseholdChange:
    household_id: str
    weight: Decimal
    change_class: ChangeClass
    change: Decimal | None  # only for gain, loss, no_change


@dataclass(frozen=True)
class ChangeSummary:
    """Winners and losers (8.1) for one group of households."""

    households: int
    weight: Decimal
    by_class: dict[ChangeClass, Decimal]  # weighted households per class
    mean_gain: Decimal | None
    median_gain: Decimal | None
    mean_loss: Decimal | None
    median_loss: Decimal | None
    largest_gain: Decimal | None
    largest_loss: Decimal | None
    total_change: Decimal  # weighted, over calculated households only
    calculated_weight: Decimal


@dataclass(frozen=True)
class GroupedTable:
    component_set: tuple[str, ...]
    unit: str
    dimension: str
    groups: dict[str, ChangeSummary]
    left_out: dict[str, Decimal] = field(default_factory=dict)  # reason -> weight


@dataclass(frozen=True)
class ComponentFiscal:
    """Static entitlement (8.5) for one component, over households whose
    component was calculated in both runs, with its coverage."""

    component: str
    unit: str
    baseline_total: Decimal
    reform_total: Decimal
    delta_total: Decimal
    coverage: dict[str, Decimal]  # delta outcome -> weight


def component_set_unit(components: Sequence[str]) -> str:
    if len(set(components)) != len(components):
        raise ValueError("duplicate components are not allowed")
    unknown = [c for c in components if c not in COMPONENTS]
    if unknown or not components:
        raise ValueError(f"unknown or empty component set: {unknown or components}")
    units = {UNITS[c] for c in components}
    if len(units) != 1:
        raise ValueError(
            f"components {list(components)} mix units {sorted(units)}; they can't be added (D8)"
        )
    return units.pop()


def household_change(result: HouseholdResult, components: Sequence[str]) -> HouseholdChange:
    component_set_unit(components)
    deltas = [result.components[c] for c in components]
    outcomes = {d.outcome for d in deltas}
    if outcomes == {"calculated"}:
        change = sum((d.delta for d in deltas if d.delta is not None), Decimal(0))
        cls = (
            ChangeClass.GAIN
            if change > 0
            else ChangeClass.LOSS
            if change < 0
            else ChangeClass.NO_CHANGE
        )
        return HouseholdChange(result.household_id, result.weight, cls, change)
    cls = ChangeClass.NEEDS_REVIEW if "needs_review" in outcomes else ChangeClass.UNSUPPORTED
    return HouseholdChange(result.household_id, result.weight, cls, None)


def summarise(changes: Sequence[HouseholdChange]) -> ChangeSummary:
    by_class = {c: Decimal(0) for c in ChangeClass}
    for h in changes:
        by_class[h.change_class] += h.weight
    gains = [
        (h.change, h.weight)
        for h in changes
        if h.change_class is ChangeClass.GAIN and h.change is not None
    ]
    losses = [
        (h.change, h.weight)
        for h in changes
        if h.change_class is ChangeClass.LOSS and h.change is not None
    ]
    calculated = [(h.change, h.weight) for h in changes if h.change is not None]
    return ChangeSummary(
        households=len(changes),
        weight=sum((h.weight for h in changes), Decimal(0)),
        by_class=by_class,
        mean_gain=weighted_mean(gains),
        median_gain=weighted_median(gains),
        mean_loss=weighted_mean(losses),
        median_loss=weighted_median(losses),
        largest_gain=max((v for v, _ in gains), default=None),
        largest_loss=min((v for v, _ in losses), default=None),
        total_change=sum((v * w for v, w in calculated), Decimal(0)),
        calculated_weight=sum((w for _, w in calculated), Decimal(0)),
    )


def _grouped(
    population: PopulationDataset,
    run: PopulationRun,
    components: Sequence[str],
    dimension: str,
    key: Callable[[PopulationHousehold, HouseholdResult], str | None],
    left_out_reason: str,
) -> GroupedTable:
    unit = component_set_unit(components)
    by_id = {h.household_id: h for h in population.households}
    groups: dict[str, list[HouseholdChange]] = {}
    left_out: dict[str, Decimal] = {}
    for result in run.households:
        group = key(by_id[result.household_id], result)
        if group is None:
            left_out[left_out_reason] = left_out.get(left_out_reason, Decimal(0)) + result.weight
            continue
        groups.setdefault(group, []).append(household_change(result, components))
    return GroupedTable(
        component_set=tuple(components),
        unit=unit,
        dimension=dimension,
        groups={g: summarise(groups[g]) for g in sorted(groups)},
        left_out=left_out,
    )


def overall(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    table = _grouped(population, run, components, "all", lambda _h, _r: "all", "")
    return replace(table, groups=table.groups or {"all": summarise([])})


def by_decile(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    by_id = {h.household_id: h for h in population.households}
    incomes = [
        (income, r.weight)
        for r in run.households
        if (income := by_id[r.household_id].characteristics.gross_household_income) is not None
    ]
    cuts = weighted_quantile_cuts(incomes, 10) if incomes else []

    def decile(h: PopulationHousehold, _r: HouseholdResult) -> str | None:
        income = h.characteristics.gross_household_income
        if income is None or not cuts:
            return None
        return f"{1 + sum(income > c for c in cuts):02d}"

    return _grouped(
        population, run, components, "gross household income decile", decile, "income unknown"
    )


def by_household_type(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    return _grouped(
        population, run, components, "household type", lambda h, _r: household_type(h).value, ""
    )


def by_children(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    def bucket(h: PopulationHousehold, _r: HouseholdResult) -> str:
        n = dependent_children(h)
        return "3+" if n >= 3 else str(n)

    return _grouped(population, run, components, "dependent children", bucket, "")


def by_region(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    return _grouped(
        population,
        run,
        components,
        "region",
        lambda h, _r: h.characteristics.region,
        "region unknown",
    )


def by_as_area(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> GroupedTable:
    def area(h: PopulationHousehold, _r: HouseholdResult) -> str | None:
        value = h.facts["household"]["accommodation_supplement"].get("statistical_area_unit")
        return None if value is None else str(value)

    return _grouped(
        population, run, components, "Accommodation Supplement area", area, "area unknown"
    )


def fiscal(run: PopulationRun) -> dict[str, ComponentFiscal]:
    """8.5 and 4.2: per component, weighted baseline, reform and delta
    totals over households calculated in both runs, and the weight in each
    delta outcome."""
    table: dict[str, ComponentFiscal] = {}
    for component in COMPONENTS:
        base = reform = delta = Decimal(0)
        coverage = {"calculated": Decimal(0), "needs_review": Decimal(0), "unsupported": Decimal(0)}
        for h in run.households:
            d = h.components[component]
            coverage[d.outcome] += h.weight
            if d.outcome == "calculated":
                assert (
                    d.baseline.value is not None
                    and d.reform.value is not None
                    and d.delta is not None
                )
                base += d.baseline.value * h.weight
                reform += d.reform.value * h.weight
                delta += d.delta * h.weight
        table[component] = ComponentFiscal(
            component, UNITS[component], base, reform, delta, coverage
        )
    return table
