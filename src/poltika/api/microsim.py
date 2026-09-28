"""v0.2 Task 10.1: the microsimulation routes.

The population is the operator's choice, never the caller's: the JSON file
named by `POLTIKA_POPULATION_PATH` at deploy time. That is the same rule as
the policy directory (ADR-0011). Without it, these routes return 503 and
the other routes still work.

- `GET /microsim/population`: what the population is, including its label.
- `GET /microsim/parameters`: the parameters a reform can override, with
  their baseline values, for the population's lookup dates.
- `POST /microsim/runs`: run a reform, and return the run identity, the
  validation summary, fiscal and grouped tables for a component set, and
  the verified explanation.
- `GET /microsim/runs/{run_id}`: a run returned earlier by this process.
  `component_set` query parameters select the measure (family tax credit
  by default), independently of other callers' requests for the same run.
  Runs are kept in memory only, so they are gone after a restart.
  Rerunning the same inputs gives the same `run_id` and `results_sha256`.

Everything is computed by `scenarios/microsim/`. These routes only
translate.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query
from fastapi import Path as PathParam
from pydantic import BaseModel, ConfigDict, Field

from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.household import facts, running_code_identity
from poltika.api.wff import WFF_POLICY_DIR
from poltika.engines.simulator.trace import plain
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.explain import explain_population, render_text, verify
from poltika.scenarios.microsim.ranges import population_ranges
from poltika.scenarios.microsim.reform import InvalidReformError, Reform, UnsupportedReformError
from poltika.scenarios.microsim.runner import COMPONENTS, UNITS, PopulationRun, run_population
from poltika.scenarios.population import InvalidHouseholdFacts, scenario_record
from poltika.semantics.population import PopulationDataset

router = APIRouter(prefix="/microsim", tags=["microsim"])

RunId = Annotated[str, PathParam(pattern=r"^[0-9a-f]{64}$")]
_RUNS: dict[str, tuple[PopulationDataset, PopulationRun]] = {}
_RUN_LIMIT = 32


@lru_cache(maxsize=2)
def _load(path: str, mtime_ns: int) -> PopulationDataset:
    return PopulationDataset.model_validate(json.loads(Path(path).read_text()))


def population() -> PopulationDataset:
    path = os.environ.get("POLTIKA_POPULATION_PATH")
    if not path or not Path(path).is_file():
        raise HTTPException(
            status_code=503, detail="no population is configured (POLTIKA_POPULATION_PATH)"
        )
    return _load(path, Path(path).stat().st_mtime_ns)


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reform: Reform
    component_set: list[str] = Field(default_factory=lambda: ["family_tax_credit"], min_length=1)


@router.get("/population")
def describe_population() -> dict[str, Any]:
    p = population()
    return {
        "population_id": p.population_id,
        "version": p.version,
        "synthetic": p.synthetic,
        "label": p.label,
        "households": len(p.households),
        "total_weight": str(sum(h.weight for h in p.households)),
        "content_sha256": p.content_sha256(),
    }


@router.get("/parameters")
def parameters() -> list[dict[str, Any]]:
    p = population()
    seen: set[tuple[str, Any, str]] = set()
    rows: list[dict[str, Any]] = []
    for household in p.households:
        try:
            record = scenario_record(household)
        except InvalidHouseholdFacts:
            continue  # reported by validation when a run is made
        for policy_dir, lookup, version in (
            (WFF_POLICY_DIR, record.wff_lookup_date, record.requested_wff_policy_version),
            (AS_POLICY_DIR, record.as_lookup_date, record.requested_as_policy_version),
        ):
            key = (str(policy_dir), lookup, version)
            if key in seen:
                continue
            seen.add(key)
            params = load_policy_parameters(policy_dir, lookup, requested_policy_version=version)
            for pid, r in sorted(params.resolutions.items()):
                rows.append(
                    {
                        "policy_id": params.policy_id,
                        "parameter_id": pid,
                        "modelled_date": lookup.isoformat(),
                        "unit": r.unit,
                        "outcome": r.outcome,
                        "value": None if r.value is None else str(r.value),
                        "source_id": r.source_id,
                    }
                )
    return rows


def execute_reform(
    reform: Reform, component_set: list[str]
) -> tuple[PopulationDataset, PopulationRun]:
    """Run `reform` on the configured population and keep the run for
    `fetch_run`. Shared by `POST /microsim/runs` and the workbench routes."""
    p = population()
    try:
        analysis.component_set_unit(component_set)
        run = run_population(
            p, reform, WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
        )
    except (UnsupportedReformError, InvalidReformError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if run.run_id not in _RUNS and len(_RUNS) >= _RUN_LIMIT:
        _RUNS.pop(next(iter(_RUNS)))
    _RUNS[run.run_id] = (p, run)
    return p, run


def stored_run(run_id: str) -> tuple[PopulationDataset, PopulationRun]:
    if run_id not in _RUNS:
        raise HTTPException(
            status_code=404, detail=f"no run {run_id} in this process; rerun it to reproduce it"
        )
    return _RUNS[run_id]


@router.post("/runs")
def create_run(request: RunRequest) -> dict[str, Any]:
    p, run = execute_reform(request.reform, request.component_set)
    return _summary(p, run, request.component_set)


@router.get("/runs/{run_id}")
def fetch_run(
    run_id: RunId,
    component_set: Annotated[list[str] | None, Query()] = None,
) -> dict[str, Any]:
    p, run = stored_run(run_id)
    components = ["family_tax_credit"] if component_set is None else component_set
    try:
        analysis.component_set_unit(components)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _summary(p, run, components)


def _summary(p: PopulationDataset, run: PopulationRun, components: list[str]) -> dict[str, Any]:
    explanation = explain_population(p, run, components)
    tables = {
        name: plain(fn(p, run, components))
        for name, fn in (
            ("overall", analysis.overall),
            ("decile", analysis.by_decile),
            ("household_type", analysis.by_household_type),
            ("children", analysis.by_children),
            ("region", analysis.by_region),
            ("as_area", analysis.by_as_area),
        )
    }
    return {
        "run_id": run.run_id,
        "results_sha256": run.results_sha256,
        "synthetic": run.synthetic,
        "label": run.label,
        "population": {
            "id": run.population_id,
            "version": run.population_version,
            "sha256": run.population_sha256,
        },
        "reform": run.reform.model_dump(mode="json"),
        "reform_sha256": run.reform.reform_sha256(),
        "overridden": plain(run.overridden),
        "code": plain(run.code),
        "policy_artifacts": [list(a) for a in run.policy_artifacts],
        "validation": {
            status.value: [n, str(w)] for status, (n, w) in run.validation.by_status().items()
        },
        "component_set": components,
        "units": {c: UNITS[c] for c in COMPONENTS},
        "fiscal": plain(analysis.fiscal(run)),
        # v0.3 Task 1b.6 (ADR-0016): needs_review households' range and the
        # weight still unboundable, kept apart from the calculated totals.
        "fiscal_ranges": plain(population_ranges(run, WFF_POLICY_DIR, AS_POLICY_DIR, facts())),
        "tables": tables,
        "explanation": render_text(explanation),
        "explanation_problems": verify(explanation, p, run),
        "take_up": "full take-up (static entitlement), not expenditure",
    }
