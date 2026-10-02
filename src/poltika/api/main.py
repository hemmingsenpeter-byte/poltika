"""Task 21/24.8: the Poltika API's FastAPI app instance.

Per ADR-0010: FastAPI introduced directly, not a placeholder. Registers
explicit exception handlers for `common.errors.PoltikaError` subclasses so
a loader-raised, caller-level structural error never silently collapses
into a 200 -- see each handler's docstring for the specific status chosen.

**Deployment gate, resolved (ADR-0011, 23 September 2026):**
`policy_specs/` is confirmed absent from a built wheel (`pyproject.toml`'s
`[tool.setuptools.packages.find]` only packages `src/`) -- embedding it
under `src/poltika/` instead would touch 12+ existing file references,
three CI glob patterns, and `REPOSITORY_STRUCTURE.md`'s whole documented
tree for a packaging concern, and would blur the existing distinction
between `policy_specs/` (reviewed, independently-versioned policy
content) and `src/` (code). Pete decided: `policy_specs/` is deploy-time
configuration, not package data -- supplied via the `POLTIKA_POLICY_SPECS_
DIR` environment variable (`poltika.api.wff._wff_policy_dir()`), the same
way this project already treats `data/`'s raw snapshots as external to
the code package. Local development is unaffected -- the environment
variable is optional and falls back to the source-checkout-relative path
Task 21 originally used. `_lifespan` below still fails loudly and
immediately at startup if either resolved policy directory has no
`policy.yaml`, whichever way it was resolved -- the safety net Task 21
built is unchanged and now also covers Task 24.8's AS route
(`poltika.api.accommodation_supplement._as_policy_dir()`), the same
convention, not a second one.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from poltika.api.access import BasicAuthMiddleware, configured_credentials
from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.accommodation_supplement import router as as_router
from poltika.api.analyst import router as analyst_router
from poltika.api.hardening import SECURITY_HEADERS, BodyLimitMiddleware, SecurityHeadersMiddleware
from poltika.api.household import router as household_router
from poltika.api.microsim import router as microsim_router
from poltika.api.microsim_page import router as microsim_page_router
from poltika.api.scenarios import router as scenarios_router
from poltika.api.wff import WFF_POLICY_DIR
from poltika.api.wff import router as wff_router
from poltika.api.workbench import router as workbench_router
from poltika.common.errors import (
    ImmutableRecordError,
    PolicyVersionMismatchError,
    PoltikaError,
    StoredRunNotFoundError,
)

logger = logging.getLogger("poltika.api")


def _missing_policy_dir_error(name: str, policy_dir: object, module_name: str) -> RuntimeError:
    return RuntimeError(
        f"{name} ({policy_dir}) has no policy.yaml -- set POLTIKA_POLICY_SPECS_DIR to "
        f"the directory containing {module_name}/policy.yaml if running from an "
        "installed artifact rather than a source checkout (see poltika.api.main's "
        "module docstring, ADR-0011)"
    )


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Fail loudly and immediately at startup if either policy directory
    isn't where it's expected -- whether that's the source-checkout-
    relative default or a `POLTIKA_POLICY_SPECS_DIR` override (ADR-0011,
    see this module's docstring)."""
    if not (WFF_POLICY_DIR / "policy.yaml").is_file():
        raise _missing_policy_dir_error("WFF_POLICY_DIR", WFF_POLICY_DIR, "working_for_families")
    if not (AS_POLICY_DIR / "policy.yaml").is_file():
        raise _missing_policy_dir_error(
            "AS_POLICY_DIR", AS_POLICY_DIR, "accommodation_supplement"
        )
    configured_credentials()  # a hosted image refuses to start without a password
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
app.include_router(as_router)
app.include_router(household_router)
app.include_router(scenarios_router)
app.include_router(analyst_router)
app.include_router(microsim_router)
app.include_router(microsim_page_router)
app.include_router(workbench_router)
# The last added runs first: headers go on every response, 401 and 413 too.
app.add_middleware(BasicAuthMiddleware)
app.add_middleware(BodyLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    """For a hosting platform's health check. Open without a password
    (`api/access.py`), so it says nothing but that the process is up."""
    return {"status": "ok"}


@app.exception_handler(StoredRunNotFoundError)
async def _stored_run_not_found_handler(request: Request, exc: StoredRunNotFoundError) -> JSONResponse:
    """Task 33.2: an unknown result id. The message holds only the id."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ImmutableRecordError)
async def _immutable_record_handler(request: Request, exc: ImmutableRecordError) -> JSONResponse:
    """Task 33.2: an id already stored with different content (ADR-0013).
    The message holds only table and id names, never paths."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


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


@app.exception_handler(Exception)
async def _unexpected_error_handler(request: Request, exc: Exception) -> Response:
    """Unhandled errors reach Starlette's outer server-error middleware,
    outside the response-header middleware. Keep that response generic
    and apply the same headers; the server still logs the raised error."""
    return Response(
        "Internal Server Error",
        status_code=500,
        media_type="text/plain",
        headers={name.decode("ascii"): value.decode("ascii") for name, value in SECURITY_HEADERS},
    )
