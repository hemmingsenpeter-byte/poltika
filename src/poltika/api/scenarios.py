"""Task 33.2: stored scenario routes over the Task 32 PostgreSQL store.

- `POST /scenarios` runs a household exactly as `/household/calculate` does
  and stores the run (append-only, ADR-0013).
- `GET /scenarios/{result_id}` returns the stored record, manifest and result.
- `POST /scenarios/{result_id}/replay` re-runs the stored scenario against its
  own retained policy files and reports whether it reproduces.
- `POST /scenarios/{result_id}/rerun` runs it against the currently deployed
  policy files as a new stored run and reports drift.

The store comes from `POLTIKA_DATABASE_URL` (operator configuration, the
ADR-0011 convention); when it is unset these routes answer 503 and the
stateless routes are unaffected.
"""

from __future__ import annotations

import json
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as PathParam
from pydantic import BaseModel

from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.household import (
    HouseholdCalculationRequest,
    HouseholdCalculationResponse,
    execute,
    record_from_request,
    response_from_run,
    running_code_identity,
)
from poltika.api.wff import WFF_POLICY_DIR
from poltika.common.errors import StoreError
from poltika.scenarios.record import canonical_json
from poltika.scenarios.store import ScenarioStore, database_url

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

ResultId = Annotated[str, PathParam(pattern=r"^[0-9a-f]{64}$")]


@lru_cache(maxsize=4)
def _store_for(url: str) -> ScenarioStore:
    return ScenarioStore.from_url(url)


def get_store() -> ScenarioStore:
    try:
        url = database_url()
    except StoreError as exc:
        raise HTTPException(status_code=503, detail="scenario store is not configured") from exc
    return _store_for(url)


StoreDep = Annotated[ScenarioStore, Depends(get_store)]


class StoredRunResponse(BaseModel):
    result_id: str
    scenario_id: str
    record: dict[str, Any]
    manifest: dict[str, Any]
    result: dict[str, Any]
    reproducible: bool


class ReplayResponse(BaseModel):
    result_id: str
    reproduced: bool
    # Task 34.3 F4: whether the code running now is the stored run's code.
    # A result can reproduce under different code; this says whether it did.
    code_matches: bool


class RerunResponse(BaseModel):
    original_result_id: str
    new_result_id: str
    changed_artifacts: list[str]
    result_changed: bool


@router.post("", status_code=201, response_model=HouseholdCalculationResponse)
def create(request: HouseholdCalculationRequest, store: StoreDep) -> HouseholdCalculationResponse:
    """Run and store a household scenario. **A conditional simulation, not a
    verified entitlement determination** (see `/household/calculate`)."""
    run = execute(record_from_request(request))
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    return response_from_run(run)


@router.get("/{result_id}", response_model=StoredRunResponse)
def fetch(result_id: ResultId, store: StoreDep) -> StoredRunResponse:
    stored = store.get_run(result_id)
    return StoredRunResponse(
        result_id=stored.result_id,
        scenario_id=stored.scenario_id,
        record=json.loads(canonical_json(stored.record)),
        manifest=stored.manifest,
        result=stored.result,
        reproducible=stored.reproducible,
    )


@router.post("/{result_id}/replay", response_model=ReplayResponse)
def replay(result_id: ResultId, store: StoreDep) -> ReplayResponse:
    with tempfile.TemporaryDirectory() as workdir:
        report = store.replay(result_id, Path(workdir), code=running_code_identity())
    return ReplayResponse(result_id=result_id, reproduced=report.reproduced, code_matches=report.code_matches)


@router.post("/{result_id}/rerun", response_model=RerunResponse)
def rerun(result_id: ResultId, store: StoreDep) -> RerunResponse:
    drift = store.rerun_against_current(
        result_id, WFF_POLICY_DIR, AS_POLICY_DIR, code=running_code_identity()
    )
    return RerunResponse(
        original_result_id=drift.original_result_id,
        new_result_id=drift.new_result_id,
        changed_artifacts=list(drift.changed_artifacts),
        result_changed=drift.result_changed,
    )
