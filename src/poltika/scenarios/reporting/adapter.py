"""The one place the reporting package touches the microsimulation modules.

Tables, charts and the report consume the structured types re-exported
here, never `scenarios/microsim/*` directly. When the aggregation,
distribution and fiscal modules are replaced or extended (P2-REP-02), this
file is the only one that is repointed.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from poltika.engines.simulator.trace import plain
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
    results_sha256,
)
from poltika.scenarios.microsim.validation import RecordStatus, validate_population
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
    verify_run(population, run)
    unit = component_set_unit(components)
    return AnalysisResults(
        components=tuple(components),
        unit=unit,
        overall=overall(population, run, components),
        deciles=by_decile(population, run, components),
        household_types=by_household_type(population, run, components),
        fiscal=fiscal(run),
    )


def verify_run(population: PopulationDataset, run: PopulationRun) -> None:
    """Check retained input/result consistency, without recalculating policy.

    These hashes are caller-provided consistency evidence, not authentication.
    """
    if population.content_sha256() != run.population_sha256:
        raise ValueError("the population is not the one this run used")
    if (run.population_id, run.population_version, run.synthetic, run.label) != (
        population.population_id,
        population.version,
        population.synthetic,
        population.label,
    ):
        raise ValueError("run population metadata does not match the population")
    if results_sha256(run.households) != run.results_sha256:
        raise ValueError("retained results digest does not match results_sha256")
    identity = {
        "population_sha256": run.population_sha256,
        "reform_sha256": run.reform.reform_sha256(),
        "code": plain(run.code),
        "policy_artifacts": sorted(run.policy_artifacts),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if hashlib.sha256(encoded.encode()).hexdigest() != run.run_id:
        raise ValueError("retained run identity does not match run_id")
    validation = validate_population(population)
    if run.validation != validation:
        raise ValueError("retained validation does not match the population")
    expected = {h.household_id: h for h in validation.households if h.record is not None}
    if len(run.households) != len(expected) or {h.household_id for h in run.households} != set(
        expected
    ):
        raise ValueError("retained results do not cover the validated households")
    for household in run.households:
        checked = expected[household.household_id]
        if (
            household.weight != validation.weights[household.household_id]
            or household.record_status != checked.status
        ):
            raise ValueError("retained household weight/status does not match validation")
        if set(household.components) != set(COMPONENTS):
            raise ValueError("retained household component coverage is incomplete")
        for component in household.components.values():
            for value in (component.baseline.value, component.reform.value, component.delta):
                if value is not None and not value.is_finite():
                    raise ValueError("retained component values must be finite")
            if component.outcome == "calculated":
                before, after = component.baseline, component.reform
                if (
                    before.outcome != "calculated"
                    or after.outcome != "calculated"
                    or before.value is None
                    or after.value is None
                    or component.delta != after.value - before.value
                    or checked.status is RecordStatus.NEEDS_REVIEW
                ):
                    raise ValueError("retained calculated component delta is inconsistent")
            elif component.delta is not None:
                raise ValueError("unresolved retained component must not carry a delta")


def weight_total(run: PopulationRun) -> Decimal:
    return sum((h.weight for h in run.households), Decimal(0))
