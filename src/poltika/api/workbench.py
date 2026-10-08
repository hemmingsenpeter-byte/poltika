"""The analyst workbench routes, `/workbench/...`.

- `GET /workbench/registry`: instruments, parameters (current value, unit,
  dates, source), sources, decisions, and the presentation config, all read
  from `policy_specs/` and `workbench_config.py`. A new instrument spec
  appears here with no code change.
- `POST /workbench/check`: what each override of a reform would do to its
  parameter, or why it is refused, before any run.
- `POST /workbench/results`: run one or two options (status quo is always
  the baseline) and return the headline and the tab blocks.
- `POST /workbench/export.xlsx` and `POST /workbench/export/{table}.csv`:
  the same blocks, as Excel or CSV, for runs kept by this process.
- `GET /workbench/decisions/{policy}/{decision}`: an interpretation
  decision's Markdown.

Nothing here calculates policy. Runs are `poltika.scenarios.microsim`'s,
kept in memory like `/microsim/runs` (gone after a restart; rerunning the
same inputs gives the same run ID). Exports reject changed policy evidence
and options with different population/code/policy baselines with HTTP 409.
"""

from __future__ import annotations

import hashlib
from datetime import date
from functools import lru_cache
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi import Path as PathParam
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from poltika.api import workbench_config as config
from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.analyst import examples as golden_examples
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.api.microsim import execute_reform, stored_run
from poltika.api.wff import WFF_POLICY_DIR
from poltika.api.workbench_export import table_csv, to_xlsx
from poltika.api.workbench_registry import decision_text, instruments, specs_root
from poltika.api.workbench_tables import FamilyType, OptionResult, build_results
from poltika.policy.loader import load_policy_parameters, load_policy_spec
from poltika.scenarios.microsim.reform import (
    InvalidReformError,
    Reform,
    UnsupportedReformError,
    apply_reform,
)
from poltika.scenarios.microsim.runner import PopulationRun
from poltika.scenarios.microsim.worked_examples import run_examples
from poltika.scenarios.record import ScenarioRecord
from poltika.semantics.population import PopulationDataset

router = APIRouter(prefix="/workbench", tags=["workbench"])

RunId = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
STATUS_QUO = "Status quo"


class ScenarioHeader(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(default="Untitled scenario", min_length=1, max_length=80)
    version: str = Field(default="", max_length=20)
    status: Literal["draft", "final"] = "draft"


def _labels_ok(labels: list[str]) -> None:
    if len(set(labels)) != len(labels) or STATUS_QUO in labels:
        raise ValueError(f"option labels must be unique and not '{STATUS_QUO}'")


class OptionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=40)
    reform: Reform


class ResultsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioHeader = Field(default_factory=ScenarioHeader)
    options: list[OptionRequest] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def _unique_labels(self) -> ResultsRequest:
        _labels_ok([o.label for o in self.options])
        return self


class ExportOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=40)
    run_id: RunId


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioHeader = Field(default_factory=ScenarioHeader)
    options: list[ExportOption] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def _unique_labels(self) -> ExportRequest:
        _labels_ok([o.label for o in self.options])
        return self


class CheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reform: Reform


@lru_cache(maxsize=1)
def _families() -> tuple[tuple[FamilyType, ScenarioRecord], ...]:
    by_id = {e["id"]: e for e in golden_examples()}
    found = []
    for family_id in config.FAMILY_TYPES:
        example = by_id.get(family_id)
        if example is None:
            continue
        record = record_from_request(HouseholdCalculationRequest.model_validate(example["request"]))
        found.append((FamilyType(family_id, example["description"]), record))
    return tuple(found)


@router.get("/registry")
def registry(as_at: date | None = None) -> dict[str, Any]:
    at = as_at or config.BASELINE_DATE
    return {
        "law_baseline": config.BASELINE_LABEL,
        "as_at": at.isoformat(),
        "instruments": instruments(at),
        "tabs": [
            {"id": t.tab_id, "title": t.title, "status": t.status, "note": t.note}
            for t in config.TABS
        ],
        "fiscal_years": [
            {"label": y.label, "modelled": y.modelled, "note": y.note} for y in config.FISCAL_YEARS
        ],
        "measures": [
            {"id": m.measure_id, "label": m.label, "components": list(m.components)}
            for m in config.MEASURES
        ],
        "thresholds": {unit: str(v) for unit, v in config.WINNER_LOSER_THRESHOLDS.items()},
        "family_types": [
            {"id": f.family_id, "description": f.description} for f, _ in _families()
        ],
        "limitations": list(config.LIMITATIONS),
        "max_options": 2,
        "status_quo_label": STATUS_QUO,
        "behavioural": {"available": False, "label": "Behavioural (coming later)"},
    }


@router.post("/check")
def check(request: CheckRequest) -> dict[str, Any]:
    """Each override on its own against the baseline parameters: the value
    it would produce, or why it is refused. Nothing is run."""
    changes: list[dict[str, Any]] = []
    problems: list[dict[str, str]] = []
    for override in request.reform.overrides:
        single = Reform(reform_id=request.reform.reform_id, overrides=(override,))
        where = {"policy_id": override.policy_id, "parameter_id": override.parameter_id}
        try:
            single.check_supported()
            policy_dir = specs_root() / override.policy_id
            baseline = load_policy_parameters(
                policy_dir,
                config.BASELINE_DATE,
                requested_policy_version=load_policy_spec(policy_dir / "policy.yaml").policy_version,
            )
            resulting = apply_reform(baseline, single).get(override.parameter_id)
            before = baseline.get(override.parameter_id)
        except (InvalidReformError, UnsupportedReformError, KeyError) as exc:
            problems.append({**where, "message": str(exc).strip("'\"")})
            continue
        changes.append(
            {
                **where,
                "operation": override.operation.value,
                "operand": str(override.value),
                "baseline": None if before.value is None else str(before.value),
                "resulting": None if resulting.value is None else str(resulting.value),
                "unit": resulting.unit,
            }
        )
    return {"ok": not problems, "changes": changes, "problems": problems}


def _check_bound_artifacts(run: PopulationRun) -> None:
    """Examples and source tables must describe the stored run's policy files."""
    root = specs_root()
    for name, expected in run.policy_artifacts:
        try:
            actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        except OSError:
            actual = None
        if actual != expected:
            raise HTTPException(
                status_code=409,
                detail="the run's policy files have changed; rerun before exporting or comparing",
            )


def _payload(
    scenario: ScenarioHeader, labelled: list[tuple[str, PopulationDataset, PopulationRun]]
) -> dict[str, Any]:
    return payload_and_options(scenario, labelled)[0]


def payload_and_options(
    scenario: ScenarioHeader, labelled: list[tuple[str, PopulationDataset, PopulationRun]]
) -> tuple[dict[str, Any], list[OptionResult]]:
    """The results payload and the option results it was built from (Task
    B0.1.2 stores both the payload and blocks built from the options)."""
    for _, _, run in labelled:
        _check_bound_artifacts(run)
    families = _families()
    records = [(f.family_id, r) for f, r in families]
    options = [
        OptionResult(
            label,
            dataset,
            run,
            run_examples(records, run.reform, WFF_POLICY_DIR, AS_POLICY_DIR),
        )
        for label, dataset, run in labelled
    ]
    try:
        payload = build_results(
            scenario.model_dump(),
            options,
            instruments(config.BASELINE_DATE),
            [f for f, _ in families],
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return payload, options


@router.post("/results")
def results(request: ResultsRequest) -> dict[str, Any]:
    labelled = []
    for option in request.options:
        dataset, run = execute_reform(option.reform, ["family_tax_credit"])
        labelled.append((option.label, dataset, run))
    return _payload(request.scenario, labelled)


def _stored_payload(request: ExportRequest) -> dict[str, Any]:
    labelled = []
    for option in request.options:
        dataset, run = stored_run(option.run_id)
        labelled.append((option.label, dataset, run))
    return _payload(request.scenario, labelled)


@router.post("/export.xlsx")
def export_xlsx(request: ExportRequest) -> Response:
    payload = _stored_payload(request)
    return Response(
        content=to_xlsx(payload),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="poltika-{payload["runs"][0]["run_id"][:12]}.xlsx"'
        },
    )


@router.post("/export/{table_id}.csv")
def export_csv(
    table_id: Annotated[str, PathParam(pattern=r"^[a-z0-9_]+$")], request: ExportRequest
) -> Response:
    text = table_csv(_stored_payload(request), table_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"no table '{table_id}'")
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{table_id}.csv"'},
    )


@router.get("/decisions/{policy_id}/{decision_id}", response_class=PlainTextResponse)
def decision(
    policy_id: Annotated[str, PathParam(pattern=r"^[a-z0-9_]+$")],
    decision_id: Annotated[str, PathParam(pattern=r"^DEC-\d+$")],
) -> str:
    text = decision_text(policy_id, decision_id)
    if text is None:
        raise HTTPException(status_code=404, detail="no such decision")
    return text
