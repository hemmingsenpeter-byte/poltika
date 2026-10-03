"""The one place the reporting package touches the microsimulation modules.

Tables, charts and the report consume the structured types re-exported
here, never `scenarios/microsim/*` directly. When the aggregation,
distribution and fiscal modules are replaced or extended (P2-REP-02), this
file is the only one that is repointed.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from poltika.scenarios.microsim.analysis import (
    ChangeClass,
    ChangeSummary,
    ComponentFiscal,
    GroupedTable,
    by_decile,
    by_household_type,
    component_set_unit,
    fiscal,
    overall,
)
from poltika.scenarios.microsim.runner import (
    COMPONENTS,
    UNITS,
    ComponentDelta,
    OverriddenParameter,
    PopulationRun,
)
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.microsim.withdrawal import WithdrawalPath
from poltika.scenarios.microsim.worked_examples import WorkedExample
from poltika.semantics.population import PopulationDataset

__all__ = [
    "COMPONENTS",
    "UNITS",
    "AnalysisResults",
    "ChangeClass",
    "ChangeSummary",
    "ComponentDelta",
    "ComponentFiscal",
    "GroupedTable",
    "OverriddenParameter",
    "PopulationRun",
    "RecordStatus",
    "WithdrawalPath",
    "WorkedExample",
    "analyse",
]


@dataclass(frozen=True)
class AnalysisResults:
    """Everything the standard tables need, for one named component set."""

    components: tuple[str, ...]
    unit: str
    overall: GroupedTable
    deciles: GroupedTable
    household_types: GroupedTable
    fiscal: dict[str, ComponentFiscal]


def analyse(
    population: PopulationDataset, run: PopulationRun, components: Sequence[str]
) -> AnalysisResults:
    unit = component_set_unit(components)
    return AnalysisResults(
        components=tuple(components),
        unit=unit,
        overall=overall(population, run, components),
        deciles=by_decile(population, run, components),
        household_types=by_household_type(population, run, components),
        fiscal=fiscal(run),
    )


def weight_total(run: PopulationRun) -> Decimal:
    return sum((h.weight for h in run.households), Decimal(0))
