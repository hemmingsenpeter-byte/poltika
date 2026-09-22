"""Task 21: the Poltika API's FastAPI app instance.

Per ADR-0010: FastAPI introduced directly, not a placeholder. Registers
explicit exception handlers for `common.errors.PoltikaError` subclasses so
a loader-raised, caller-level structural error never silently collapses
into a 200 -- see each handler's docstring for the specific status chosen.

**Known packaging limitation, not fixed by this task (PR #22 review
finding):** `poltika.api.wff.WFF_POLICY_DIR` locates `policy_specs/`
relative to this source file, which only resolves inside a source
checkout -- `policy_specs/` lives at the repo root, outside
`src/poltika/`, and `pyproject.toml`'s `[tool.setuptools.packages.find]`
only packages `src/`, so a normally `pip install`-ed wheel would not
carry `policy_specs/` at all and this API would fail to start. Embedding
policy data inside the installed package (e.g. moving `policy_specs/`
under `src/poltika/`) is a packaging/deployment architecture decision
well beyond this task's single-module HTTP-wrapper scope, and touches
every existing reference to `policy_specs/`'s current repo-root location
(tests, `wff.py`, `benchmarks.yaml`/`spec_cases.yaml` tooling) -- it needs
its own explicit decision before this API is ever deployed outside a
source checkout, not a silent fix here. `_startup_policy_directory_check`
below only makes the failure loud and immediate (at process startup) if
that directory is ever missing, rather than a confusing failure on the
first request.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from poltika.api.wff import WFF_POLICY_DIR
from poltika.api.wff import router as wff_router
from poltika.common.errors import PolicyVersionMismatchError, PoltikaError

logger = logging.getLogger("poltika.api")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Fail loudly and immediately at startup if `policy_specs/` isn't
    where `WFF_POLICY_DIR` expects it -- see this module's docstring for
    why that can happen (a `pip install`-ed deployment, not a source
    checkout) and why fixing it is out of this task's scope."""
    if not (WFF_POLICY_DIR / "policy.yaml").is_file():
        raise RuntimeError(
            f"WFF_POLICY_DIR ({WFF_POLICY_DIR}) has no policy.yaml -- this API only "
            "runs from a source checkout today (see poltika.api.main's module docstring "
            "for the known packaging limitation)"
        )
    yield


app = FastAPI(
    title="Poltika API",
    version="0.1.0",
    description=(
        "Deterministic NZ policy calculations. Every input marked "
        "'verified' (household_eligibility, income, etc.) is the "
        "caller's own assertion that the underlying fact has been "
        "verified elsewhere -- this API does not itself confirm any "
        "fact against a government record or other authoritative "
        "source. A result is therefore a conditional simulation given "
        "the facts the caller asserted, not an independently verified "
        "entitlement determination; a `calculated` outcome is only as "
        "reliable as the caller's own verification of its inputs."
    ),
    lifespan=_lifespan,
)
app.include_router(wff_router)


@app.exception_handler(PolicyVersionMismatchError)
async def _policy_version_mismatch_handler(
    request: Request, exc: PolicyVersionMismatchError
) -> JSONResponse:
    """A caller requested a `policy_version` that does not match the
    deployed `policy.yaml` -- a caller-correctable request problem, not a
    server fault. Mapped to 409 Conflict: the request conflicts with the
    server's current policy state, distinct from a malformed request body
    (422) or an unrelated server-side data problem (500, below). Safe to
    return verbatim: this message only ever contains version strings, no
    filesystem paths."""
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
    specific matching handler for a given exception's type.

    The exception is logged server-side with its full text and traceback,
    but NOT included in the response body: `InvalidSourceCatalogError` in
    particular embeds absolute resolved filesystem paths (PR #22 review
    finding), and no `PoltikaError` message is written assuming it will
    ever reach an untrusted caller. A 500 gets a fixed, generic detail
    instead -- unlike the 409 above, whose message is safe by
    construction (version strings only)."""
    logger.error("Unhandled PoltikaError on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error: the deployed policy configuration is invalid."},
    )
