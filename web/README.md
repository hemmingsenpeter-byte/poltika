# Poltika web

The web frontend (ADR-0023, Task B0.1). Next.js App Router, React 19,
TypeScript strict, Tailwind CSS. It is built as a static export (`web/out`)
and served by the FastAPI process from the same Docker image: one origin, one
login, no CORS. It only presents values the API returns; it calculates nothing.

## Local development

Node 20.19 or later and npm. In two terminals:

```sh
# 1. the API (from the repository root)
uv run --extra dev uvicorn poltika.api.main:app

# 2. the web app (from web/)
npm ci
npm run dev        # http://localhost:3000
```

`next dev` proxies `/api`, `/workbench`, `/healthz`, `/analyst`,
`/openapi.json`, `/household` and `/microsim` to the API at
`http://localhost:8000` (`next.config.mjs` rewrites). A static export forbids
rewrites, so they exist only under `next dev`; set `POLTIKA_API_ORIGIN` to
point elsewhere. Legacy `/scenarios` requests for JSON also reach the API;
HTML and React navigation requests reach Next.js. If the API has
`POLTIKA_ACCESS_PASSWORD` set, the browser asks
for it once on the first API call.

To try the production arrangement instead:

```sh
cd web && npm run build
cd .. && POLTIKA_WEB_DIR=$PWD/web/out uv run --extra dev uvicorn poltika.api.main:app
# open http://localhost:8000/ in a browser
```

## Commands

| Command | Does |
| --- | --- |
| `npm run lint` | ESLint (`next/core-web-vitals`, no `fetch` outside `src/api`) |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Vitest: formatters, navigation, API client, route ids, a page, the copy scan |
| `npm run build` | Static export to `web/out` |
| `npm run gen:api` | Regenerate `src/api/schema.gen.ts` from `openapi.json` |

After a backend response model changes, regenerate both generated files and
commit them (CI fails if they drift):

```sh
uv run --extra dev python scripts/development/dump_openapi.py
cd web && npm run gen:api
```

## Environment variables

| Variable | Where | Meaning |
| --- | --- | --- |
| `POLTIKA_WEB_DIR` | API process | The export directory to serve. Default `web/out` if it exists; with none, the API serves no pages. The image sets `/app/web`. |
| `POLTIKA_API_ORIGIN` | `next dev` | Where the dev proxy sends API calls (default `http://localhost:8000`). |

The app makes no external call at run time: fonts are fetched and self-hosted
at build time, and there is no analytics.

## How serving works

FastAPI answers a `GET` or `HEAD` with an exported page only when `Accept`
names `text/html` ahead of `application/json` and the path is a declared UI
route (`src/poltika/api/web.py`). API clients sending `application/json` or
`*/*` reach the API unchanged, so `GET /scenarios/{id}` still returns JSON.
Dynamic routes (`/models/{id}`, `/data/{id}`, `/scenarios/{id}`,
`/scenarios/{id}/runs/{id}`) are exported once with the placeholder `_`; a
page reads the real id with `useRouteIds()`, which parses `usePathname()`.
Never use `useParams()` there: it would read `_`. Text built from those ids
should render only after mount (`useMounted()`), because the exported HTML
holds the placeholder.

## Rules

- Components never call `fetch`. They call a service in `src/api/services`,
  usually through `useAsync`. ESLint enforces it.
- Services parse every response with a zod schema typed against the generated
  OpenAPI types (`src/api/schemas.ts`). A mismatch is an
  `ApiError{kind: "invalid_response"}`. Components import types from
  `src/domain`, not from `schema.gen.ts`.
- A missing value is never zero. Use `format/` and the `NotCalculated` marker.
  Money, counts and percentages are formatted only in `src/format`.
- Status is never colour alone: a `Pill` carries an icon and text.
- Components are generic. No component names a model or an instrument.
- Gated terms (`src/copyScan.test.ts` lists them) must not appear in user-facing
  copy, and `tests/unit/api/test_web_static.py` scans the built pages.

## Progressive disclosure

Show the answer first, then the way to inspect it. A page opens with the
headline and its units, the next layer (assumptions, sources, versions) is one
step away, and the technical and audit detail sits deepest. Do not show
everything at once, and do not hide that something is missing: an unavailable
figure says "Not calculated" or "Not yet available" with its reason.

## Adding things

**A page.** Create `src/features/<Name>Page.tsx` (a client component using a
service and the shared states), then a thin `src/app/<route>/page.tsx` that
renders it. For a dynamic segment, export `dynamicParams = false` and
`generateStaticParams()` returning `[{ <param>: "_" }]`, read ids with
`useRouteIds()`, add the pattern to `PATTERNS` in `src/lib/useRouteIds.ts` and
the route to `_UI_ROUTES` in `src/poltika/api/web.py`, with a test in
`tests/unit/api/test_web_static.py`.

**A navigation item.** Add it to `NAVIGATION` in `src/config/navigation.ts`.
Give it a `capability` if it should stay hidden until the API switches that
capability on (`/api/v1/meta`); a hidden item renders no text.

**A model type or a dataset type.** The catalogue pages are generic over the
registry: add the entry on the backend (`model_registry/registry.yaml`, a
dataset manifest) and it appears. If a new field is needed, add it to the
Pydantic response model, regenerate the schema, extend the zod schema in
`src/api/schemas.ts`, then show it in the generic page. Do not add a
model-specific component.

**A service call.** Add a function to a file in `src/api/services` that calls
`getJson(path, schema)`; add its zod schema to `src/api/schemas.ts` with
`satisfies z.ZodType<components["schemas"]["..."]>`.

**A scenario tab or a block type.** The backend owns what a workspace holds
(`src/poltika/api/v1_blocks.py`); the page only shows it.

1. The backend adds the block type (a Pydantic model with a `type` literal) to
   the `Block` union in `v1_blocks.py` and fills it in `v1_scenarios.py`.
2. Regenerate the types: `uv run --extra dev python scripts/development/dump_openapi.py && (cd web && npm run gen:api)`.
3. Add a renderer to the `REGISTRY` in `src/components/blocks/BlockRenderer.tsx`.
   The registry is typed over every block type, so `npm run typecheck` fails
   until the new type has a component. A type the registry does not know shows
   an "Unsupported block" notice rather than failing.
4. Add a fixture to `src/test/fixtures/workspace.ts` and a case to
   `BlockRenderer.test.tsx`.

A new tab id is added to `TabId` in `v1_blocks.py` and to `TAB_IDS` in
`src/features/workspace/WorkspaceView.tsx`; the tab appears with its blocks.
Never compute a value in a component: show the string the API sent, format it
with `src/format`, and show an outcome word (never "0") when it has no value.
A table cell is shown exactly as the server rounded it (`formatExact`).
