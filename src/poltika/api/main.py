"""Task 21: the Poltika API's FastAPI app instance.

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
immediately at startup if the resolved directory has no `policy.yaml`,
whichever way it was resolved -- the safety net Task 21 built is
unchanged, only what feeds `WFF_POLICY_DIR` changed.
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
    where `WFF_POLICY_DIR` expects it -- whether that's the source-
    checkout-relative default or a `POLTIKA_POLICY_SPECS_DIR` override
    (ADR-0011, see this module's docstring)."""
    if not (WFF_POLICY_DIR / "policy.yaml").is_file():
        raise RuntimeError(
            f"WFF_POLICY_DIR ({WFF_POLICY_DIR}) has no policy.yaml -- set "
            "POLTIKA_POLICY_SPECS_DIR to the directory containing "
            "working_for_families/policy.yaml if running from an installed "
            "artifact rather than a source checkout (see poltika.api.main's "
            "module docstring, ADR-0011)"
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
