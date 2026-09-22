# ADR-0010: Task 21 API framework choice — FastAPI now, not a placeholder

**Date:** 22 September 2026
**Status:** accepted

## Context

Task 21 ("Add API") is the first task that introduces an HTTP layer to
Poltika — no API, frontend, or database has existed until now
(ARCHITECTURE.md's "v0.1, as actually implemented so far" table). The
question is whether to build a minimal, dependency-light placeholder for
v0.1 and replace it once more of the API surface is known, or to
introduce the project's actual long-term backend framework directly.

ARCHITECTURE.md already records a long-term target stack (commit
`21dc905`, 22 September 2026) naming FastAPI + Pydantic v2 as the
backend/API choice, "the architecture to build *toward* across v0.1's
remaining tasks and beyond." That same commit explicitly changed the
frontend decision from "v0.1: Streamlit, replace later" to "go straight
to Next.js rather than build and later replace a Streamlit UI" — a
precedent for the same question this ADR answers for the backend.

## Decision

Task 21 introduces FastAPI directly, not a placeholder. `fastapi` and
`pydantic` (already a dependency) are added to `pyproject.toml`'s main
dependencies; `httpx` (required by FastAPI's `TestClient`) and `uvicorn`
(only needed to actually serve the app, not to run tests) are added under
the `dev` extra rather than as hard runtime dependencies, since nothing
yet needs to serve the app outside of tests.

This mirrors the Streamlit→Next.js reasoning already recorded in
ARCHITECTURE.md: building a placeholder API now and replacing it once the
real shape is known would mean doing the integration work twice for no
durable benefit, against a stack choice that's already decided.

## Consequences

- The API layer (`src/poltika/api/`, see `REPOSITORY_STRUCTURE.md`) is
  built once, against the actual target framework, not rebuilt later.
- `fastapi`/`pydantic` become real runtime dependencies from Task 21
  onward; `uvicorn`/`httpx` remain dev-only until something needs to
  actually serve the app (e.g. a later deployment task).
- Later API surface (Accommodation Supplement, cross-policy routing,
  authentication, etc.) extends this same FastAPI app rather than
  requiring a framework migration.
