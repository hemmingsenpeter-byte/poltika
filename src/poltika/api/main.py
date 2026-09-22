"""Task 21: the Poltika API's FastAPI app instance.

Per ADR-0010: FastAPI introduced directly, not a placeholder. Registers
explicit exception handlers for `common.errors.PoltikaError` subclasses so
a loader-raised, caller-level structural error never silently collapses
into a 200 -- see each handler's docstring for the specific status chosen.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from poltika.api.wff import router as wff_router
from poltika.common.errors import PolicyVersionMismatchError, PoltikaError

app = FastAPI(title="Poltika API", version="0.1.0")
app.include_router(wff_router)


@app.exception_handler(PolicyVersionMismatchError)
async def _policy_version_mismatch_handler(
    request: Request, exc: PolicyVersionMismatchError
) -> JSONResponse:
    """A caller requested a `policy_version` that does not match the
    deployed `policy.yaml` -- a caller-correctable request problem, not a
    server fault. Mapped to 409 Conflict: the request conflicts with the
    server's current policy state, distinct from a malformed request body
    (422) or an unrelated server-side data problem (500, below)."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(PoltikaError)
async def _poltika_error_handler(request: Request, exc: PoltikaError) -> JSONResponse:
    """Any other `PoltikaError` (unsupported schema version, policy not
    approved, malformed parameter intervals, an unresolved source id, an
    unsafe source catalog) reflects a problem in the deployed
    `policy_specs/` data itself -- not something the caller's request
    could have avoided. Mapped to 500 Internal Server Error, distinct from
    the caller-correctable 409 above. Registered after the more specific
    `PolicyVersionMismatchError` handler; Starlette dispatches to the most
    specific matching handler for a given exception's type."""
    return JSONResponse(status_code=500, content={"detail": str(exc)})
