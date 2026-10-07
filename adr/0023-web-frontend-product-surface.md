# ADR-0023: Web frontend as the single product surface (Task B0.1)

**Date:** 7 October 2026
**Status:** accepted by Pete on 7 October 2026. Logged in
`docs/decision_log.md` (D24 for Pete's Tier C decisions, D25 for the
engineering choices). It extends ADR-0013 and ADR-0021, and does not accept
ADR-0018 (PETE_QUEUE Q9 stays open).

## Context

Poltika's analyst interfaces are two hand-written HTML pages served by
FastAPI (`/analyst`, `/analyst/microsim`); the Workbench backend (ADR-0018,
proposed) returns JSON blocks with no page. ARCHITECTURE.md records Next.js +
TypeScript, Tailwind + shadcn/ui and Plotly as the frontend destination, and
says a frontend rewrite is not a prerequisite for Pilot 1.
BUILD_PLAN_PROGRAMME.md made the Workbench the first product surface and
ruled out "a parallel product stack" (Phase C).

On 7 October 2026 Pete asked for the first production frontend, deployable at
`https://poltika.onrender.com`, placed at the very beginning of Phase B. It
must be polished enough to show economists, officials and pilot users, and
built so later models, comparisons and explorers do not force a rewrite.

The repository constrains the design:

- The existing `GET /scenarios/{result_id}` is a JSON route, so UI routes
  under `/scenarios` collide with it.
- There is no CORS, the CSP allows `connect-src 'self'`, and Basic auth
  covers every path except `/healthz`. A separate frontend origin would need
  all three changed.
- Population and Workbench runs are held in process memory (ADR-0013), so
  links to them die on restart.
- No list endpoint exists for scenarios, models or datasets, and the image
  carries neither `model_registry/` nor `data/metadata/` beyond the
  population spec.
- CI runs on a self-hosted macOS 12 runner with Node 20 (D21).

## Decision

Pete's decisions (Tier C, approved in session):

1. **The task is programme Task B0.1**, at the head of Phase B. "Task 0.1"
   would collide with v0.3 local 0.1.
2. **The web app is the Workbench's home.** It is the single product
   surface. It renders existing Workbench blocks and adds no calculation.
   Task 15 completes the Workbench workflow inside it. ADR-0018 is not
   accepted by this.
3. **Access is password protected.** The live service runs with
   `POLTIKA_ACCESS_PASSWORD` again.
4. **Render resources:** the existing live web service is reused and a Render
   PostgreSQL is added so scenario links survive restarts.

Engineering choices (Tier A/B, Claude Code):

5. **Static export served by FastAPI.** `web/` holds a Next.js App Router
   project built with `output: 'export'`. The Docker image builds it in a
   Node stage and FastAPI serves it from `POLTIKA_WEB_DIR`: one service,
   one origin, one login.
6. **Navigation fallback.** A `GET` whose `Accept` prefers `text/html` on a
   declared UI route receives the exported page. All other requests,
   including API clients sending `application/json` or `*/*`, reach the API
   unchanged. Dynamic segments are exported once with a placeholder and read
   on the client from the path.
7. **`/api/v1` namespace** for every new endpoint the UI consumes. Legacy
   routes keep their paths and responses.
8. **Contracts are generated, not hand-copied.** Pydantic response models
   produce OpenAPI; TypeScript types are generated from it and CI fails on
   drift; zod validates responses at one service boundary.
9. **Generic blocks.** The workspace view is a list of tabs of typed blocks.
   The frontend maps block types to components and knows no instrument.
10. **Reform scenarios are persisted.** Reform scenario definitions and run
    payloads are stored append-only in PostgreSQL, beside the household
    store, with `created_at` outside every identity hash. This extends
    ADR-0013, which kept population runs in memory. Retained, replayable
    counterfactual contracts remain Task 14.
11. **npm**, because it ships with Node on the runner and in the image.
12. **A narrow data-boundary exception.** `api/` may read dataset
    *metadata* through `data/manifest.py` and `data/registry.py` to list
    datasets, never a data value. The exception is recorded in
    REPOSITORY_STRUCTURE.md's boundary table and its test in B0.1.1. The
    Source Archive stays closed to everything outside `data/acquisition/`
    (ADR-0022), so the Data page shows it as not yet exposed.
13. **No `render.yaml` yet.** The existing service was created in the
    dashboard; its settings are documented in `docs/pilot/HOSTING.md` rather
    than adopted into a Blueprint mid-flight.

## Consequences

- One deployable unit keeps auth, security headers, the body limit and
  `/healthz` exactly where they are. The Next.js server features (SSR, route
  handlers, middleware) are unavailable. Adopting them later means a second
  process or service and its own decision.
- API clients that send `Accept: text/html` to a UI path receive a page.
  `docs/web/FRONTEND.md` documents this, and API clients should send
  `application/json`.
- Docker builds now include a Node stage. Changes under `web/` trigger the
  hosted `pilot-image` job under D21's budget rule.
- npm dependencies are outside pip-audit's coverage, so `security.yml` adds
  `npm audit` and Dependabot gains the npm ecosystem.
- Runs from the image report `reproducible: false` because the image has no
  git checkout. The UI says so rather than substituting the Render commit.
- Gated copy is checked in the frontend's own tests, because the v0.3
  release gate scans only HTML served by FastAPI routes.
- Reversal: delete `web/`, the static-serving module and the `/api/v1`
  router, and restore the single-stage Dockerfile. The `0002` migration's
  tables are additive and can stay. No calculated amount or stored identity
  depends on any of this.
