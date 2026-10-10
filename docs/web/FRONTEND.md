# Poltika web frontend

Architecture and operating guide for the web app (ADR-0023, Task B0.1). The
commands and file-level conventions live in [web/README.md](../../web/README.md);
this page is the map above them. It describes what is on `main` today. Pages
that arrive with B0.1.4 or B0.1.5 are named as such and not described.

## Architecture

One image, one origin, one login.

- `web/` is a Next.js App Router project (React 19, strict TypeScript,
  Tailwind). `next build` produces a static export in `web/out`
  (`web/next.config.mjs`: `output: "export"`).
- The Docker image builds that export in a Node stage and copies it to
  `/app/web` (`Dockerfile`). FastAPI serves it from the same process
  (`src/poltika/api/web.py`), behind the same HTTP Basic login as the API
  (`src/poltika/api/access.py`, middleware order in `src/poltika/api/main.py`).
  No CORS, no second service.
- The frontend calculates nothing. Every figure, status and unit comes from the
  API; a missing value is shown as "Not calculated" with its reason, never zero.
- Page selection: a `GET` or `HEAD` whose `Accept` names `text/html` ahead of
  `application/json`, on a declared UI route, receives the exported page. Any
  other request reaches the API unchanged.

Layout of `web/src`:

| Path | Role |
| --- | --- |
| `app/` | Route files, thin wrappers that render a feature |
| `features/` | One component per page (Home, Models, Model detail, Data, Dataset detail, Scenarios, New scenario, Scenario workspace) |
| `components/` | Shell (`layout/AppShell.tsx`, `MetaProvider.tsx`), navigation, shared states, generic UI parts |
| `api/` | The only code that calls `fetch` (`client.ts`), zod schemas (`schemas.ts`), generated OpenAPI types (`schema.gen.ts`) and one service file per area |
| `config/` | `navigation.ts` and `capabilities.ts` |
| `domain/` | Types the components import (not the generated file directly) |
| `format/` | The only place money, counts and percentages are formatted |

## Progressive disclosure

The first screen carries the answer and its units. Assumptions, sources and
versions are one step further, technical and audit detail deepest. Nothing that
is missing is hidden: an unavailable figure states that it is unavailable and
why. The seven-tab scenario workspace that applies this to a run lands with
B0.1.4; until then `features/ScenarioWorkspacePage.tsx` shows only the scenario
and run ids a URL names, so deep links can be checked.

## Local development

Two terminals: the API (`uv run --extra dev uvicorn poltika.api.main:app`) and
`npm run dev` in `web/`, which proxies `/api`, `/workbench` and `/healthz` to
`http://localhost:8000` (rewrites exist only under `next dev`). The exact
steps, the production-like local run and all `npm` commands are in
[web/README.md](../../web/README.md).

## Production build

`npm run build` in `web/` writes `web/out`. After any backend response-model
change, regenerate `web/openapi.json` and `web/src/api/schema.gen.ts`
(`scripts/development/dump_openapi.py`, `npm run gen:api`); CI fails on drift
(the `web` job in `.github/workflows/tests.yml`). The image build repeats the
export; nothing is copied from a developer machine (`.dockerignore` excludes
`web/out` and `web/node_modules`).

## Render

The service is the Docker image (see [docs/pilot/HOSTING.md](../pilot/HOSTING.md)):
runtime Docker, health check `/healthz`, a PostgreSQL database for stored
scenarios, and secrets set by Pete in the Render dashboard. A Blueprint file is
not used. The container applies database migrations at start
(`deploy/entrypoint.sh`) and refuses to start without a password.

## Environment variables

| Variable | Process | Meaning |
| --- | --- | --- |
| `POLTIKA_ACCESS_PASSWORD` | API | Required on a hosted image; every route except `/healthz` needs it. Secret. |
| `POLTIKA_ACCESS_USER` | API | Optional username (default `pilot`) |
| `POLTIKA_REQUIRE_ACCESS_PASSWORD` | API | `1` in the image: refuse to start with no password |
| `POLTIKA_DATABASE_URL` | API | PostgreSQL URL for stored scenarios; without it `/api/v1/scenarios` answers 503. Secret (it holds a password). |
| `POLTIKA_WEB_DIR` | API | Export directory; the image sets `/app/web` |
| `POLTIKA_API_ORIGIN` | `next dev` | Dev proxy target (default `http://localhost:8000`) |

Other API variables (policy directory, population, model registry, dataset
metadata) are set by the image; see `Dockerfile` and `docs/pilot/HOSTING.md`.

## API boundary

- Components call a service; a service calls `api/client.ts`, which parses the
  response with zod and turns failures into a typed `ApiError`
  (`api/errors.ts`). ESLint forbids `fetch` elsewhere.
- Catalogue routes on `main`: `GET /api/v1/meta`, `/models`, `/models/{id}`,
  `/datasets`, `/datasets/{id}`, `/evidence` (`src/poltika/api/v1.py`).
  Scenario routes: `/api/v1/scenarios` (list, create), `/{id}` and
  `/{id}/runs[/{run_id}]` (`src/poltika/api/v1_scenarios.py`).
- Error bodies are `{"detail": {"code", "message"}}`, with legacy routes
  returning a plain string; `parseErrorBody` handles both.
- Sign-in is the browser's own Basic-auth prompt. There is a single shared
  identity and no per-user ownership of stored scenarios (see "Data allowed on
  the hosted pilot" in HOSTING.md).

## Navigation and capabilities

`config/navigation.ts` declares every item. Home, Scenarios, Models and Data
are always shown. Explore, Evidence, Assurance and Admin are declared with a
capability and render nothing until `/api/v1/meta` switches that capability on.
`config/capabilities.ts` lists the eight capability ids; only
`policy_comparison` is on by default. Unknown ids from the API are ignored.

## Adding a tab, a model type or a dataset type

- **A top-level tab (navigation item and page).** Add a feature component and
  a thin `app/<route>/page.tsx`; add the item to `NAVIGATION`; for a dynamic
  segment export the `_` placeholder and register the pattern in
  `lib/useRouteIds.ts` and `_UI_ROUTES` in `src/poltika/api/web.py`, with a test
  in `tests/unit/api/test_web_static.py`. Step-by-step: web/README.md, "Adding
  things".
- **A workspace tab inside a scenario run** (the seven-tab view): lands with
  B0.1.4. The backend already returns the tabs in the run workspace response;
  how the page renders them is not described here until that code is on `main`.
- **A model type or dataset type.** Add the registry entry on the backend
  (`model_registry/registry.yaml`, a dataset manifest under
  `data/metadata/datasets`); the generic catalogue pages list it. A new field
  needs the Pydantic response model, regenerated schema, zod schema and the
  generic page; never a model-specific component.

## Not on `main` yet

Charts and accessibility work (B0.1.5/B0.1.6), the scenario workspace page
(B0.1.4) and any screen using them. Update this file when they land.
