"""Task B0.1.2 (ADR-0023): durable scenarios and the workspace view.

- `GET /api/v1/scenarios`: reform and household scenarios, newest first.
- `POST /api/v1/scenarios`: store a reform scenario (one or two options)
  after the same checks as `POST /workbench/check`.
- `POST /api/v1/scenarios/{id}/runs`: run every option through the
  Workbench path and store the results payload verbatim.
- `GET /api/v1/scenarios/{id}` and `.../runs/{run_id}`: the workspace.

The workspace only places values the engines and the Workbench already
produced into seven tabs (`v1_blocks`). It computes no amount, never adds
WFF to the Accommodation Supplement, and shows a component that was not
calculated as such, never as 0 (ADR-0018). Storage needs
`POLTIKA_DATABASE_URL`; without it these routes answer 503
`scenario_storage_unavailable`.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any, Literal, NoReturn

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi import Path as PathParam
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator
from sqlalchemy.exc import SQLAlchemyError

from poltika.api import workbench_config as config
from poltika.api.household import HouseholdCalculationRequest
from poltika.api.microsim import execute_reform
from poltika.api.v1 import _deployed_policy_dirs, _policy_evidence, _registry, meta
from poltika.api.v1_blocks import (
    TAB_TITLES,
    AuditField,
    AuditRecordBlock,
    Block,
    CalculationChainBlock,
    ChainStep,
    Context,
    MetricBlock,
    MetricValue,
    ModelRefBlock,
    ModelRefItem,
    Notice,
    ProvenanceRef,
    RunHeader,
    RunRef,
    ScenarioHeader,
    SourceCheckOut,
    SourceItem,
    SourcesBlock,
    Tab,
    TabId,
    Unit,
    Workspace,
)
from poltika.api.v1_schemas import ErrorBody
from poltika.api.workbench import (
    STATUS_QUO,
    CheckRequest,
    OptionRequest,
    check,
    payload_and_options,
)
from poltika.api.workbench import ScenarioHeader as WorkbenchHeader
from poltika.api.workbench_export import table_csv, to_xlsx
from poltika.api.workbench_tables import NOT_CALCULATED, distribution_tables
from poltika.common.errors import ImmutableRecordError, StoredRunNotFoundError, StoreError
from poltika.scenarios.microsim.reform import Reform
from poltika.scenarios.reform_record import (
    reform_definition,
    reform_run_id,
    reform_scenario_id,
    results_sha256,
)
from poltika.scenarios.store import ReformRun, ReformScenario, ScenarioStore, database_url


class _ScenarioRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def validated(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError as exc:
                message = "; ".join(
                    f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                    for error in exc.errors()
                )
                _fail(422, "invalid_scenario", message)

        return validated


router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"], route_class=_ScenarioRoute)

ScenarioId = Annotated[str, PathParam(pattern=r"^[0-9a-f]{64}$")]
_ERRORS: dict[int | str, dict[str, Any]] = {
    code: {"model": ErrorBody} for code in (404, 409, 422, 429, 503)
}
_BLOCK: TypeAdapter[Block] = TypeAdapter(Block)
_FORMAT = "poltika-reform-run/1"
_HOUSEHOLD_TITLE = "Household calculation"
_HOUSEHOLD_DESCRIPTION = (
    "One household's Working for Families (2026-27 tax year) and Accommodation Supplement "
    "(weekly) entitlement, from facts the caller asserted."
)


def _fail(
    status: int, code: str, message: str, headers: Mapping[str, str] | None = None
) -> NoReturn:
    raise HTTPException(
        status_code=status,
        detail={"code": code, "message": message},
        headers=dict(headers) if headers else None,
    )


@lru_cache(maxsize=4)
def _store_for(url: str) -> ScenarioStore:
    return ScenarioStore.from_url(url)


def _store() -> ScenarioStore:
    try:
        return _store_for(database_url())
    except StoreError:
        _fail(503, "scenario_storage_unavailable", "Scenario storage is not configured here.")
    except (SQLAlchemyError, ValueError):
        _fail(503, "scenario_storage_unavailable", "Scenario storage is not configured correctly.")


@contextmanager
def _storage() -> Iterator[None]:
    """Database and integrity failures as coded errors, never a bare 500."""
    try:
        yield
    except ImmutableRecordError as exc:
        _fail(409, "immutable_record", str(exc))
    except StoreError as exc:
        _fail(503, "scenario_storage_unavailable", f"Stored scenario data failed a check: {exc}")
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "scenario_storage_unavailable",
                "message": "Scenario storage cannot be reached or is not migrated.",
            },
        ) from exc


# --- contracts ---------------------------------------------------------------------------


class CreateScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=500)
    options: list[OptionRequest] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def _unique_labels(self) -> CreateScenario:
        labels = [o.label for o in self.options]
        if len(set(labels)) != len(labels) or STATUS_QUO in labels:
            raise ValueError(f"option labels must be unique and not '{STATUS_QUO}'")
        return self


class ScenarioItem(BaseModel):
    scenario_id: str
    kind: Literal["reform", "household"]
    title: str
    description: str
    created_at: Any
    runs: int
    latest_run_id: str | None


class ScenarioList(BaseModel):
    items: list[ScenarioItem]
    total: int


class RunCreated(BaseModel):
    scenario_id: str
    run_id: str


# --- routes ------------------------------------------------------------------------------


@router.get("", response_model=ScenarioList, responses=_ERRORS)
def list_scenarios(
    kind: Literal["reform", "household"] | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ScenarioList:
    with _storage():
        items, total = _store().list_scenarios(kind, limit, offset)
    return ScenarioList(
        items=[
            ScenarioItem(
                scenario_id=i.scenario_id,
                kind=i.kind,
                title=i.title or _HOUSEHOLD_TITLE,
                description=(i.description or "") if i.title else _HOUSEHOLD_DESCRIPTION,
                created_at=i.created_at,
                runs=i.runs,
                latest_run_id=i.latest_run_id,
            )
            for i in items
        ],
        total=total,
    )


@router.post("", status_code=201, response_model=ScenarioItem, responses=_ERRORS)
def create_scenario(request: CreateScenario) -> ScenarioItem:
    store = _store()
    problems = []
    for option in request.options:
        result = check(CheckRequest(reform=option.reform))
        problems += [
            f"{option.label}: {p['parameter_id']}: {p['message']}" for p in result["problems"]
        ]
    if problems:
        _fail(422, "invalid_scenario", "; ".join(problems))
    definition = reform_definition(
        config.BASELINE_DATE, [(o.label, o.reform) for o in request.options]
    )
    with _storage():
        stored = store.save_reform_scenario(
            reform_scenario_id(definition), definition, request.title, request.description
        )
        return _item(stored, store)


@router.get("/{scenario_id}/definition", response_model=CreateScenario, responses=_ERRORS)
def scenario_definition(scenario_id: ScenarioId) -> CreateScenario:
    """Copy the retained reform settings into a new, independently checked draft."""
    with _storage():
        scenario = _store().get_reform_scenario(scenario_id)
        if scenario is None:
            _fail(404, "scenario_not_found", "No reform scenario has this id.")
        return CreateScenario(
            title=scenario.title,
            description=scenario.description,
            options=scenario.definition["options"],
        )


@router.get(
    "/{scenario_id}/runs/{run_id}/definition",
    response_model=HouseholdCalculationRequest,
    responses=_ERRORS,
)
def household_definition(
    scenario_id: ScenarioId, run_id: ScenarioId
) -> HouseholdCalculationRequest:
    """Copy stored facts, dates and requested versions without filling missing facts."""
    with _storage():
        try:
            stored = _store().get_run(run_id)
        except StoredRunNotFoundError:
            _fail(404, "run_not_found", "No household run has this id.")
        if stored.scenario_id != scenario_id:
            _fail(404, "run_not_found", "No run with this id belongs to the scenario.")
        record = stored.record
        return HouseholdCalculationRequest.model_validate(
            {
                "wff": {
                    **asdict(record.household.wff),
                    "modelled_date": record.wff_lookup_date,
                    "requested_policy_version": record.requested_wff_policy_version,
                },
                "accommodation_supplement": {
                    **asdict(record.household.accommodation_supplement),
                    "modelled_date": record.as_lookup_date,
                    "assessment_week_start": record.assessment_week.start,
                    "assessment_week_end": record.assessment_week.end,
                    "requested_policy_version": record.requested_as_policy_version,
                },
                "as_claimant_is_wff_claimant_or_partner": record.household.as_claimant_is_wff_claimant_or_partner,
            }
        )


def _retained_reform_run(scenario_id: str, run_id: str) -> ReformRun:
    run = _store().get_reform_run(run_id)
    if run is None or run.scenario_id != scenario_id:
        _fail(404, "run_not_found", "No run with this id belongs to the scenario.")
    return run


@router.get(
    "/{scenario_id}/runs/{run_id}/export.xlsx",
    response_class=Response,
    responses={
        **_ERRORS,
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
    },
)
def stored_workbook(scenario_id: ScenarioId, run_id: ScenarioId) -> Response:
    """Use the existing writer on retained results; no rerun or live policy lookup."""
    with _storage():
        run = _retained_reform_run(scenario_id, run_id)
        return Response(
            content=to_xlsx(run.results["workbench"]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="poltika-{run_id[:12]}.xlsx"'},
        )


@router.get(
    "/{scenario_id}/runs/{run_id}/export/{table_id}.csv",
    response_class=Response,
    responses={
        **_ERRORS,
        200: {"content": {"text/csv": {"schema": {"type": "string", "format": "binary"}}}},
    },
)
def stored_table(
    scenario_id: ScenarioId,
    run_id: ScenarioId,
    table_id: Annotated[str, PathParam(pattern=r"^[a-z0-9_]+$")],
) -> Response:
    with _storage():
        run = _retained_reform_run(scenario_id, run_id)
        text = table_csv(run.results["workbench"], table_id)
        if text is None:
            _fail(404, "table_not_found", "No table with this id belongs to the stored run.")
        return Response(
            content=text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{table_id}.csv"'},
        )


def _item(s: ReformScenario, store: ScenarioStore) -> ScenarioItem:
    runs = store.runs_of(s.scenario_id)
    return ScenarioItem(
        scenario_id=s.scenario_id,
        kind="reform",
        title=s.title,
        description=s.description,
        created_at=s.created_at,
        runs=len(runs),
        latest_run_id=runs[0].run_id if runs else None,
    )


@router.post("/{scenario_id}/runs", status_code=201, response_model=RunCreated, responses=_ERRORS)
def create_run(scenario_id: ScenarioId) -> RunCreated:
    store = _store()
    with _storage():
        scenario = store.get_reform_scenario(scenario_id)
    if scenario is None:
        _fail(404, "scenario_not_found", "No reform scenario has this id.")
    options = [
        (o["label"], Reform.model_validate(o["reform"])) for o in scenario.definition["options"]
    ]
    try:
        labelled = []
        for label, reform in options:
            dataset, run = execute_reform(reform, ["family_tax_credit"])
            labelled.append((label, dataset, run))
        payload, results = payload_and_options(WorkbenchHeader(name=scenario.title[:80]), labelled)
    except HTTPException as exc:
        _coded(exc)
    stored = {
        "format": _FORMAT,
        "workbench": _plain(payload),
        "distribution": _plain(distribution_tables(results)),
        "context": _context(payload).model_dump(mode="json"),
    }
    option_run_ids = tuple(run.run_id for _, _, run in labelled)
    run_id = reform_run_id(scenario_id, option_run_ids, results_sha256=results_sha256(stored))
    with _storage():
        store.save_reform_run(run_id, scenario_id, option_run_ids, stored)
    return RunCreated(scenario_id=scenario_id, run_id=run_id)


def _coded(exc: HTTPException) -> NoReturn:
    codes = {
        429: "run_in_progress",
        422: "invalid_scenario",
        503: "population_unavailable",
        409: "policy_files_changed",
    }
    _fail(exc.status_code, codes.get(exc.status_code, "run_failed"), str(exc.detail), exc.headers)


def _plain(value: Any) -> Any:
    """JSON-safe, with every table cell a string or null."""
    encoded = jsonable_encoder(value)

    def walk(v: Any) -> Any:
        if isinstance(v, dict):
            if v.get("type") == "table":
                v = {**v, "rows": [[None if c is None else str(c) for c in r] for r in v["rows"]]}
            return {k: walk(x) for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v

    return walk(encoded)


@router.get("/{scenario_id}", response_model=Workspace, responses=_ERRORS)
def workspace(scenario_id: ScenarioId) -> Workspace:
    with _storage():
        return _workspace(scenario_id, None)


@router.get("/{scenario_id}/runs/{run_id}", response_model=Workspace, responses=_ERRORS)
def run_workspace(scenario_id: ScenarioId, run_id: ScenarioId) -> Workspace:
    with _storage():
        return _workspace(scenario_id, run_id)


def _workspace(scenario_id: str, run_id: str | None) -> Workspace:
    store = _store()
    runs = store.runs_of(scenario_id)
    refs = [RunRef(run_id=r.run_id, created_at=r.created_at) for r in runs]
    if run_id is not None and run_id not in {r.run_id for r in runs}:
        _fail(404, "run_not_found", "This scenario has no run with this id.")
    chosen = run_id or (runs[0].run_id if runs else None)
    reform = store.get_reform_scenario(scenario_id)
    if reform is not None:
        run = None if chosen is None else store.get_reform_run(chosen)
        return _reform_workspace(reform, run, refs)
    if store.household_scenario_exists(scenario_id):
        return _household_workspace(store, scenario_id, chosen, refs)
    _fail(404, "scenario_not_found", "No scenario has this id.")


# --- reform workspace --------------------------------------------------------------------


def _tab(tab_id: TabId, blocks: list[Any], note: str | None = None) -> Tab:
    return Tab(
        id=tab_id,
        title=TAB_TITLES[tab_id],
        status="available" if blocks else "empty",
        note=note,
        blocks=[b if not isinstance(b, dict) else _BLOCK.validate_python(b) for b in blocks],
    )


def _unavailable(tab_id: TabId, note: str) -> Tab:
    return Tab(id=tab_id, title=TAB_TITLES[tab_id], status="unavailable", note=note)


def _unit(label: str) -> Unit:
    period: Literal["tax_year", "week"] | None = (
        "tax_year"
        if label.endswith("per tax year")
        else "week"
        if label.endswith("per week")
        else None
    )
    return Unit(
        label=label,
        currency="NZD" if label.startswith("NZD") else None,
        period=period,
        basis="nominal" if label.startswith("NZD") else None,
        per="population",
    )


def _context(payload: dict[str, Any] | None) -> Context:
    if payload is not None:
        tabs = {t["id"]: _by_id(t) for t in payload["tabs"]}
        modelled = next(y for y in tabs["fiscal"]["horizon"]["years"] if y["modelled"])
        return Context(
            law_baseline=payload["law_baseline"],
            reference_period=f"{modelled['label']}: {modelled['note']}",
            policy_versions={
                row[0]: row[1] for row in tabs["assumptions"]["parameters_used"]["rows"]
            },
            population_label=payload["population_label"],
            synthetic=bool(payload["synthetic"]),
        )
    modelled = next(y for y in config.FISCAL_YEARS if y.modelled)
    return Context(
        law_baseline=config.BASELINE_LABEL,
        reference_period=f"{modelled.label}: {modelled.note}",
        policy_versions={p.policy_id: p.policy_version or "unversioned" for p in meta().policies},
        population_label=None if payload is None else payload["population_label"],
        synthetic=True if payload is None else bool(payload["synthetic"]),
    )


def _by_id(tab: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {b["id"]: b for b in tab["blocks"]}


def _population_block(block: dict[str, Any]) -> dict[str, Any]:
    """Mark aggregate columns for P3 display without changing stored values."""
    if block["type"] != "table":
        return block
    return {
        **block,
        "columns": [
            {**column, "precision": "population_estimate"} if column["kind"] != "text" else column
            for column in block["columns"]
        ],
    }


def _reform_workspace(s: ReformScenario, run: ReformRun | None, refs: list[RunRef]) -> Workspace:
    header = ScenarioHeader(
        scenario_id=s.scenario_id,
        kind="reform",
        title=s.title,
        description=s.description,
        created_at=s.created_at,
    )
    if run is None:
        note = "This scenario has not been run yet."
        return Workspace(
            scenario=header,
            run=None,
            runs=refs,
            context=_context(None),
            tabs=[_unavailable(t, note) for t in TAB_TITLES],
        )
    payload = run.results["workbench"]
    tabs = {t["id"]: t for t in payload["tabs"]}
    fiscal, households, assumptions = (
        _by_id(tabs[t]) for t in ("fiscal", "households", "assumptions")
    )
    first = payload["runs"][0]
    workspace_tabs = [
        _tab("overview", _overview(payload, assumptions)),
        _tab(
            "fiscal",
            [
                *(_population_block(b) for b in fiscal.values()),
                Notice(
                    id="net_crown_impact",
                    title="Net Crown impact",
                    tone="unavailable",
                    text=(
                        "Not yet available. Direct fiscal accounting (programme Task 22) is "
                        "not built, so there is no net Crown figure and no cumulative, real "
                        "or % of GDP view. Components are never added together."
                    ),
                ),
            ],
        ),
        _tab(
            "distribution",
            [
                *(
                    _population_block(b)
                    for k, b in households.items()
                    if k.startswith("winners_losers_")
                ),
                *(_population_block(b) for b in run.results["distribution"]),
                households["worked_examples"],
            ],
        ),
        _tab("evidence", _evidence_blocks()),
        _tab(
            "assumptions",
            [
                assumptions["parameters_changed"],
                assumptions["decisions"],
                assumptions["limitations"],
                Notice(
                    id="changing_assumptions",
                    tone="info",
                    text=(
                        "Changing an option creates a new scenario with its own id. A stored "
                        "run is never changed."
                    ),
                ),
            ],
        ),
        _tab("technical", [_models("population_runner"), assumptions["parameters_used"]]),
        _tab(
            "audit",
            [
                AuditRecordBlock(
                    id="identity",
                    title="Identity",
                    fields=[
                        AuditField(label="Scenario ID", value=s.scenario_id),
                        AuditField(label="Run ID", value=run.run_id),
                        AuditField(
                            label="Run stored at",
                            value=run.created_at.isoformat() if run.created_at else None,
                        ),
                        AuditField(label="Results SHA-256", value=run.results_sha256),
                        AuditField(
                            label="Reproducible from the source commit",
                            value="yes" if first["reproducible"] else "no",
                            note=(
                                None
                                if first["reproducible"]
                                else "This deployment has no recorded source commit, so the "
                                "run cannot be tied to one."
                            ),
                        ),
                        AuditField(
                            label="Deployed build (display only)",
                            value=meta().build.commit,
                            note="Not part of any scenario or run identity.",
                        ),
                    ],
                ),
                assumptions["run_identity"],
                assumptions["policy_artifacts"],
                Notice(
                    id="calculation_chain",
                    tone="info",
                    text=(
                        "Population runs keep each household's result, not its step-by-step "
                        "calculation. A household scenario shows the full chain from source "
                        "to parameter, rule and result."
                    ),
                ),
            ],
        ),
    ]
    return Workspace(
        scenario=header,
        run=RunHeader(
            run_id=run.run_id, created_at=run.created_at, reproducible=first["reproducible"]
        ),
        runs=refs,
        context=(
            Context.model_validate(run.results["context"])
            if "context" in run.results
            else _context(payload)
        ),
        tabs=workspace_tabs,
    )


def _overview(payload: dict[str, Any], assumptions: dict[str, dict[str, Any]]) -> list[Any]:
    blocks: list[Any] = [
        Notice(id="population", tone="caution", text=payload["population_label"]),
    ]
    measures: dict[str, list[dict[str, Any]]] = {}
    for item in payload["headline"]:
        measures.setdefault(item["measure_id"], []).append(item)
    for measure_id, items in measures.items():
        blocks.append(
            MetricBlock(
                id=f"headline_{measure_id}",
                label=f"{items[0]['measure']}: change in total entitlement",
                unit=_unit(items[0]["unit"]),
                values=[
                    MetricValue(
                        option=i["option"],
                        value=None if i["change_total"] == NOT_CALCULATED else i["change_total"],
                        outcome="not_calculated"
                        if i["change_total"] == NOT_CALCULATED
                        else "calculated",
                    )
                    for i in items
                ],
                precision="population_estimate",
                evidence_class="Model output",
                context=(
                    "Weighted households whose entitlement was calculated before and after the "
                    "change; full take-up, not expenditure."
                ),
                provenance=[
                    ProvenanceRef(tab="fiscal", block_id="fiscal_components"),
                    ProvenanceRef(tab="distribution", block_id=f"winners_losers_{measure_id}"),
                ],
            )
        )
    blocks.append(
        _population_block(
            {
                "type": "table",
                "id": "headline",
                "title": "Who is affected",
                "columns": [
                    {"id": "measure", "label": "Measure", "kind": "text"},
                    {"id": "option", "label": "Option", "kind": "text"},
                    {"id": "better_off", "label": "Better off", "kind": "count"},
                    {"id": "worse_off", "label": "Worse off", "kind": "count"},
                    {"id": "no_change", "label": "No material change", "kind": "count"},
                    {"id": "not_calculated", "label": "Not calculated", "kind": "count"},
                    {
                        "id": "mean_change",
                        "label": "Mean change of those calculated",
                        "kind": "money",
                    },
                    {"id": "unit", "label": "Unit", "kind": "text"},
                ],
                "rows": [
                    [
                        i["measure"],
                        i["option"],
                        i["better_off"],
                        i["worse_off"],
                        i["no_material_change"],
                        i["not_calculated"],
                        i["mean_change"] if i["mean_change"] is not None else NOT_CALCULATED,
                        i["unit"],
                    ]
                    for i in payload["headline"]
                ],
                "notes": [
                    "Weighted households. Better or worse off means a change at or above the threshold shown in Distribution."
                ],
            }
        )
    )
    blocks.append({**assumptions["parameters_changed"], "title": "What was tested"})
    return blocks


def _evidence_blocks() -> list[Any]:
    blocks: list[Any] = [
        Notice(
            id="evidence_scope",
            tone="info",
            text=(
                "The sources catalogued for the policy versions deployed now. The Audit tab "
                "lists the exact policy files this run read, with their hashes."
            ),
        )
    ]
    for policy_dir in _deployed_policy_dirs():
        e = _policy_evidence(policy_dir)
        blocks.append(
            SourcesBlock(
                id=f"sources_{e.policy_id}",
                title=f"Sources: {e.policy_id.replace('_', ' ')}",
                policy_id=e.policy_id,
                policy_version=e.policy_version,
                sources=[
                    SourceItem(
                        id=src.id,
                        title=src.title,
                        url=src.url,
                        kind=src.kind,
                        source_type=src.source_type,
                        authority_rank=src.authority_rank,
                        checked_on=[
                            SourceCheckOut(field=c.field, date=c.date) for c in src.checked_on
                        ],
                        check_evidence=[c.text for c in src.check_evidence],
                    )
                    for src in e.sources
                ],
            )
        )
    return blocks


def _models(model_id: str) -> ModelRefBlock:
    registry = _registry()
    ids: list[str] = []
    stack = [model_id]
    while stack:
        current = stack.pop(0)
        if current not in ids:
            ids.append(current)
            stack.extend(registry.model(current).depends_on)
    return ModelRefBlock(
        id="models",
        title="Current model registry",
        models=[
            ModelRefItem(id=m.id, name=m.name, version=m.version, label=registry.label(m.id))
            for m in (registry.model(i) for i in ids)
        ],
    )


# --- household workspace -------------------------------------------------------------------

_OUTCOMES = ("calculated", "needs_review", "unsupported")


def _household_provenance_blocks(provenance: dict[str, Any] | None) -> list[Any]:
    if provenance is None:
        return [
            Notice(
                id="original_provenance",
                tone="unavailable",
                text="The original calculation steps were not retained for this legacy run.",
            )
        ]
    blocks: list[Any] = []
    for policy_id in ("working_for_families", "accommodation_supplement"):
        report = provenance[policy_id]
        blocks.append(
            {
                "type": "table",
                "id": f"original_sources_{policy_id}",
                "title": f"Original cited sources: {policy_id.replace('_', ' ')}",
                "columns": [
                    {"id": key, "label": label, "kind": "text"}
                    for key, label in (
                        ("id", "Source"),
                        ("title", "Title"),
                        ("url", "Link"),
                        ("checks", "Check evidence"),
                    )
                ],
                "rows": [
                    [
                        source["id"],
                        source["title"],
                        source["url"],
                        "; ".join(c["text"] for c in source["check_evidence"]),
                    ]
                    for source in report["sources"]
                ],
                "notes": ["Cited by the original run, from its retained verified report."],
            }
        )
        for component in report["components"]:
            cid = component["component_id"]
            blocks.append(
                {
                    "type": "table",
                    "id": f"rules_{cid}",
                    "title": f"Specification rules: {cid.replace('_', ' ')}",
                    "columns": [
                        {"id": "id", "label": "Rule", "kind": "text"},
                        {
                            "id": "summary",
                            "label": "Original specification summary",
                            "kind": "text",
                        },
                    ],
                    "rows": [[rule["id"], rule["summary"]] for rule in component["source_rules"]],
                    "notes": [
                        "Applied to the reported result."
                        if component["rules_applied"]
                        else "Original module rules; the reported result was not calculated."
                    ],
                }
            )
            blocks.append(
                {
                    "type": "table",
                    "id": f"parameters_{cid}",
                    "title": f"Parameters consulted: {cid.replace('_', ' ')}",
                    "columns": [
                        {"id": key, "label": label, "kind": "text"}
                        for key, label in (
                            ("parameter_id", "Parameter"),
                            ("outcome", "Outcome"),
                            ("value", "Value"),
                            ("unit", "Unit"),
                            ("review_status", "Review status"),
                            ("source_id", "Source"),
                            ("locator", "Locator"),
                        )
                    ],
                    "rows": [
                        [
                            p[key]
                            for key in (
                                "parameter_id",
                                "outcome",
                                "value",
                                "unit",
                                "review_status",
                                "source_id",
                                "locator",
                            )
                        ]
                        for p in component["parameters"]
                    ],
                    "notes": ["Retained from the original verified provenance report."],
                }
            )
            if component["steps"]:
                unit = "NZD per tax year" if policy_id == "working_for_families" else "NZD per week"
                blocks.append(
                    CalculationChainBlock(
                        id=f"calculation_{cid}",
                        title=f"{cid.replace('_', ' ')} ({unit})",
                        steps=[
                            ChainStep(
                                component_id=cid,
                                inputs={key: str(value) for key, value in step["inputs"].items()},
                                **{
                                    key: step[key]
                                    for key in ("step_id", "rule_id", "description", "result")
                                },
                            )
                            for step in component["steps"]
                        ],
                    )
                )
                if not component["rules_applied"]:
                    blocks.append(
                        Notice(
                            id=f"superseded_{cid}",
                            tone="caution",
                            text=(
                                "These recorded module steps do not establish a calculated "
                                "entitlement. The component's reported outcome explains why."
                            ),
                        )
                    )
    return blocks


def _household_workspace(
    store: ScenarioStore, scenario_id: str, result_id: str | None, refs: list[RunRef]
) -> Workspace:
    header = ScenarioHeader(
        scenario_id=scenario_id,
        kind="household",
        title=_HOUSEHOLD_TITLE,
        description=_HOUSEHOLD_DESCRIPTION,
        created_at=min((r.created_at for r in refs if r.created_at), default=None),
    )
    if result_id is None:
        note = "This scenario has no stored run."
        return Workspace(
            scenario=header,
            run=None,
            runs=refs,
            context=None,
            tabs=[_unavailable(t, note) for t in TAB_TITLES],
        )
    stored = store.get_run(result_id)
    components: list[tuple[str, str, dict[str, Any]]] = [
        (name, "NZD per tax year", c) for name, c in stored.result["wff"].items()
    ] + [("accommodation_supplement", "NZD per week", stored.result["accommodation_supplement"])]
    metrics = [
        MetricBlock(
            id=f"component_{name}",
            label=name.replace("_", " ").capitalize(),
            unit=Unit(
                label=unit,
                currency="NZD",
                period="tax_year" if unit.endswith("tax year") else "week",
                basis="nominal",
                per="household",
            ),
            values=[
                MetricValue(
                    option="This household",
                    value=c["value"] if c["outcome"] == "calculated" else None,
                    outcome=c["outcome"] if c["outcome"] in _OUTCOMES else "not_calculated",
                )
            ],
            precision="household_rule",
            evidence_class="Model output",
            context=c.get("reason") or "",
            provenance=[
                ProvenanceRef(tab="audit", block_id="identity"),
                ProvenanceRef(
                    tab="audit",
                    block_id=f"parameters_{name}" if stored.provenance else "original_provenance",
                ),
            ],
        )
        for name, unit, c in components
    ]
    table = {
        "type": "table",
        "id": "components",
        "title": "This household's components",
        "columns": [
            {"id": "component", "label": "Component", "kind": "text"},
            {"id": "unit", "label": "Unit", "kind": "text"},
            {"id": "outcome", "label": "Outcome", "kind": "text"},
            {"id": "amount", "label": "Amount", "kind": "money"},
            {"id": "reason", "label": "Reason", "kind": "text"},
        ],
        "rows": [
            [
                name,
                unit,
                c["outcome"],
                c["value"] if c["outcome"] == "calculated" else c["outcome"],
                c.get("reason"),
            ]
            for name, unit, c in components
        ],
        "notes": [
            "WFF is per tax year and the Accommodation Supplement per week; they are never added."
        ],
    }
    manifest = stored.manifest
    code = manifest.get("code", {})
    follow_up = "Shown for household scenarios in a later update (Task B0.1, household view)."
    return Workspace(
        scenario=header,
        run=RunHeader(
            run_id=result_id,
            created_at=next((r.created_at for r in refs if r.run_id == result_id), None),
            reproducible=stored.reproducible,
        ),
        runs=refs,
        context=Context(
            law_baseline=(
                f"Policy lookup dates: WFF {stored.record.wff_lookup_date}; "
                f"Accommodation Supplement {stored.record.as_lookup_date}"
            ),
            reference_period=(
                f"WFF {stored.result['wff_period'][0]} to {stored.result['wff_period'][1]}; "
                f"Accommodation Supplement {stored.result['accommodation_supplement_period'][0]} "
                f"to {stored.result['accommodation_supplement_period'][1]} (ends exclusive)"
            ),
            policy_versions={
                "working_for_families": stored.record.requested_wff_policy_version,
                "accommodation_supplement": stored.record.requested_as_policy_version,
            },
            population_label=None,
            synthetic=False,
        ),
        tabs=[
            _tab(
                "overview",
                [
                    Notice(
                        id="conditional",
                        tone="caution",
                        text=(
                            "A conditional simulation from facts the caller asserted, not a "
                            "verified entitlement determination."
                        ),
                    ),
                    *metrics,
                ],
            ),
            _unavailable(
                "fiscal", "Fiscal effects come from population runs; this is one household."
            ),
            _tab("distribution", [table]),
            _tab("evidence", _evidence_blocks()),
            _unavailable("assumptions", follow_up),
            _tab("technical", [_models("combined_runner")]),
            _tab(
                "audit",
                [
                    AuditRecordBlock(
                        id="identity",
                        title="Identity",
                        fields=[
                            AuditField(label="Scenario ID", value=scenario_id),
                            AuditField(label="Result ID", value=result_id),
                            AuditField(label="Package version", value=code.get("package_version")),
                            AuditField(
                                label="Source commit",
                                value=code.get("source_commit") or "not recorded",
                            ),
                            AuditField(
                                label="Dependency lock SHA-256",
                                value=code.get("dependency_lock_sha256") or "not recorded",
                            ),
                            AuditField(
                                label="Reproducible", value="yes" if stored.reproducible else "no"
                            ),
                        ],
                    ),
                    {
                        "type": "table",
                        "id": "policy_files",
                        "title": "Policy files this run read",
                        "columns": [
                            {"id": "file", "label": "File", "kind": "text"},
                            {"id": "sha256", "label": "SHA-256", "kind": "text"},
                        ],
                        "rows": [[f, sha] for f, sha in manifest.get("policy_files", [])],
                        "notes": [
                            "Replay: POST /scenarios/{result_id}/replay re-runs it against these exact files."
                        ],
                    },
                    *_household_provenance_blocks(stored.provenance),
                ],
            ),
        ],
    )
