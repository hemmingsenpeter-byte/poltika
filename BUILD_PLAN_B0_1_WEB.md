# Poltika web frontend: detailed Task B0.1 lane

**Date:** 7 October 2026
**Status:** Active supporting plan for programme Task B0.1, approved by Pete
on 7 October 2026 ([ADR-0023](adr/0023-web-frontend-product-surface.md);
[decision log](docs/decision_log.md) D24–D25). The sole master build order
remains [BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md).

**Starts:** at the head of Phase B, on the merged WFF/AS, scenario-store,
microsimulation and Workbench backends. It does not wait for Tasks 5–11 and
blocks none of them. It changes no policy specification, engine or
calculated amount.

**Name:** Task B0.1, not "Task 0.1". "0.1" already means v0.3 local 0.1
(income-tax source scoping) in [BUILD_PLAN_v0_3.md](BUILD_PLAN_v0_3.md) and
its records, and "Phase 0" is retired programme wording.

## Purpose

Build the first usable production web frontend for Poltika, served at
`https://poltika.onrender.com` behind the existing pilot password. It is
the single product surface: Phase C Task 15 completes the Analyst Workbench
workflow inside it rather than in a parallel stack.

> A minister should understand the result in 30 seconds. An analyst should
> interrogate it for 30 minutes. An economist should ultimately be able to
> reproduce it.

The interface uses progressive disclosure, so a user can move from "What
happens?" to "Why?" to "Show me exactly how you know":

```text
Simple answer → Result → Breakdown → Calculation → Model
  → Assumptions / parameters → Data → Evidence / statutory source → Audit / provenance
```

Future agents must not flatten this into one dashboard. The surface layer is
sparse; technical detail lives in tabs and drill-downs.

## Fixed constraints

- **The UI calculates nothing.** Every number comes from a deterministic
  engine through the API. No policy logic, formula or statutory value lives
  in TypeScript ([doctrine/llm_boundaries.md](doctrine/llm_boundaries.md);
  ADR-0018). Formatting is the only client-side transformation.
- **ADR-0018's display invariants hold:** WFF and AS are never added; there
  is no WFF total while IWTC is `needs_review`; a component that was not
  calculated shows its outcome or "Not calculated", never 0.
- **P3 display precision:** household Rule outputs keep their legally
  required precision; population and estimate-dependent figures show three
  significant figures with their range. Stored values keep full precision.
- **No fabricated results.** A metric a model cannot produce shows "Not yet
  available". Fixtures and seed data exist only in tests.
- **No unsupported claims.** Copy must not use the terms the v0.3 release
  gate rejects (`tests/acceptance/test_v0_3_release_gate.py`, `GATED_TERMS`)
  unless negated. Future navigation labels obey this too. Examples and
  placeholders name supported instruments only, so no NZ Super example.
- **No LLM.** Natural-language interpretation is Phase P. The Home input
  searches supported analyses; it does not interpret.
- **Synthetic population label** stays visible wherever a population result
  appears: results are not an estimate for New Zealand.
- **Same origin.** The API has no CORS, its CSP allows `connect-src 'self'`,
  and HTTP Basic auth covers every path except `/healthz`.

## Architecture

| Concern | Choice |
| --- | --- |
| Framework | Next.js (App Router) + TypeScript strict, Tailwind + shadcn/ui primitives, Plotly for charts: the recorded stack ([ARCHITECTURE.md](ARCHITECTURE.md)) |
| Build | `output: 'export'` static build, served by FastAPI from the same Docker image: one Render service, one login, no CORS |
| Location | `web/` at the repository root ([REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)) |
| Package manager | npm with a committed `package-lock.json` |
| New API endpoints | `/api/v1/*`, so the UI owns the root path space; legacy routes are unchanged |
| Navigation fallback | A `GET` whose `Accept` prefers `text/html` on a declared UI route receives the exported page; everything else reaches the API. `GET /scenarios/{id}` with `Accept: application/json` (or `*/*`) still returns JSON |
| Dynamic routes | Exported once with a placeholder parameter; FastAPI maps any ID onto that page; the client reads IDs only through `useRouteIds()` (from `usePathname()`) |
| Contracts | Pydantic response models → OpenAPI → generated `web/src/api/schema.gen.ts` (CI fails on drift); zod checks at the service boundary, typed against the generated schema; components see domain types only |
| Presentation contract | The scenario workspace is `tabs[{id, title, status, note, blocks[]}]`, reusing ADR-0018 `table`/`horizon`/`list` blocks and adding `metric`, `sources`, `audit_record`, `calculation_chain` and `model_ref`. A block renderer registry maps type → component; no component knows an instrument |
| Traceability | Every `metric` carries `provenance_ref`, `evidence_class`, `precision`, `unit{currency, period, basis}`, an optional `range` and values keyed by option, so the drill-down and A/B/C comparison can grow without a contract change |
| Persistence | Reform scenarios and their run payloads are stored append-only in PostgreSQL beside the household scenario store; `created_at` sits outside every hash |
| Capabilities | A typed constant (`policy_comparison`, `outcome_explorer`, `evidence_search`, `assurance_dashboard`, `collaboration`, `natural_language_scenarios`, `monte_carlo`, `advanced_distributions`) that `/api/v1/meta` can switch off; navigation items declare the capability they need |

First-release navigation is Home, Scenarios, Models and Data. Explore,
Evidence, Assurance and Admin are declared behind capabilities that are off.
The scenario workspace tabs are Overview, Fiscal, Distribution, Evidence,
Assumptions, Technical and Audit.

## Subtasks

- **B0.1.0 — Claude Code. Plan and governance.** This file, ADR-0023, the
  programme, status, decision-log, queue, structure and architecture edits.
  *Done when:* merged, with Pete's decisions recorded as D24 and the
  engineering choices as D25.
- **B0.1.1 — Claude Code. Read-only catalogue contracts.** `GET
  /api/v1/meta`, `/api/v1/models[/{id}]` (from `model_registry/registry.yaml`
  through `engines/assurance/model_cards.py`), `/api/v1/datasets[/{id}]`
  (dataset manifests and the population spec) and `/api/v1/evidence?policy=`
  (sources with check evidence and the full `evidence_coverage` detail).
  Pydantic response models for the Workbench registry and results payloads.
  A missing catalogue answers `503 {code: "catalogue_unavailable"}`. The
  image copies `model_registry/` and `data/metadata/{datasets,variables}`.
  Today nothing outside `data/` may import it
  (`tests/unit/data/test_boundary.py`), so the dataset endpoint needs a
  deliberate, narrow boundary change: `api/` may read dataset *metadata*
  through `data/manifest.py` and `data/registry.py`, never a data value,
  recorded in [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)'s boundary
  table and its test in the same PR. The Source Archive stays closed:
  nothing outside `data/acquisition/` may name it (ADR-0022), so the Data
  page shows it as not yet exposed until a separate boundary decision.
  *Done when:* each endpoint is tested, typed in OpenAPI and served from the
  image; no existing response changes; the boundary test still passes with
  only the recorded exception.
- **B0.1.2 — Claude Code; GPT/Codex review-queue row. Durable scenarios and
  the workspace view.** Migration `0002`: append-only `reform_scenario` and
  `reform_run`, and a nullable `created_at` on `run`. `GET/POST
  /api/v1/scenarios`, `POST /api/v1/scenarios/{sid}/runs` (through the
  existing Workbench run path, keeping the single-run 429 guard) and `GET
  /api/v1/scenarios/{sid}[/runs/{rid}]` returning the workspace view for
  reform and household runs. Values are assembled from existing payloads,
  never recomputed: headline → Overview; fiscal components, coverage and
  horizon → Fiscal, with "Net Crown impact" and annual/cumulative,
  real/nominal and %GDP views "Not yet available" until Task 22; winners and
  losers plus the population run's grouped tables → Distribution; sources and
  check evidence → Evidence (existing evidence class, review status and
  authority rank, never invented grades); parameters changed and used,
  population assumptions and limitations → Assumptions; model references →
  Technical; run identity, code identity, artifact hashes and provenance
  steps → Audit. The image has no git checkout, so the code commit shows
  "not recorded"; the Render build commit is display-only metadata and never
  enters run identity. Without `POLTIKA_DATABASE_URL` the routes answer
  `503 {code: "scenario_storage_unavailable"}`.
  *Done when:* identities are deterministic and append-only, the view never
  sums across units or turns a non-calculated value into 0, golden household
  and reform views are tested, and the review-queue row clears.
- **B0.1.3 — Claude Code. Web shell.** First prove the deep-link technique
  on a built export served by FastAPI; if Next.js rewrites the URL on
  hydration, stop and log the fallback before building on it. Then: `web/`
  scaffold, design tokens (off-white surfaces, charcoal type, one accent,
  thin borders, tabular numerals), declarative navigation, capabilities,
  central formatters (NZD, $B/$M, %, pp, annual/weekly, nominal, P3
  precision, explicit "Not calculated"/"Not yet available"), the app shell
  with a collapsible sidebar and skip link, loading/error/empty/unavailable/
  stale/validation states keyed to the API error `code`, and Home ("What do
  you want to understand?", supported-analysis search, Analyse a policy
  change, Compare two settings, Explore a household, "Recreate an existing
  policy" marked unavailable, a link to the classic `/analyst` page).
  FastAPI serves `web/out` from `POLTIKA_WEB_DIR` with immutable caching for
  `/_next/static/*` and `no-cache` HTML. Multi-stage Dockerfile; a `web` CI
  job on the self-hosted runner (install, lint, typecheck, schema drift,
  tests, build); `npm audit` in `security.yml`; npm in Dependabot.
  *Done when:* the shell, deep links, cache headers and auth are tested in
  Python and Vitest, a copy scan rejects gated terms in `web/src` and the
  built pages, and every existing page, route and test is unchanged.
- **B0.1.4 — Claude Code. Scenario experience.** `/scenarios` (list),
  `/scenarios/new` (policy-change, two-option comparison and household
  templates, each ending in a confirmation panel showing policy, baseline →
  scenario value with source and locator, reference period, population label
  and limitations before **Run analysis**), `/scenarios/:id` and
  `/scenarios/:id/runs/:runId` (header with IDs, status, period, versions
  and timestamp; re-run, CSV/XLSX export through the existing Workbench
  exports and "Edit as new scenario", which never mutates a stored run;
  seven deep-linkable tabs rendered through the block registry).
  *Done when:* loading, every tab, missing metrics, API failures, the 429
  state and deep routes are tested.
- **B0.1.5 — Claude Code. Models and Data.** Generic model and dataset
  catalogues and detail pages: status, validation level, version basis,
  cases and tests, limitations, risks, change log and dependencies for
  models; publisher, coverage, vintage, retrieval date, checksum, snapshot
  version, transformation, variables and "used by" for datasets. Source
  Archive snapshots appear as a labelled "not yet exposed" state (ADR-0022).
  *Done when:* both catalogues and their detail pages are tested.
- **B0.1.6 — Claude Code. Polish.** Lazy-loaded Plotly bar and series charts
  with units, period, source caption, table alternative and a text summary;
  greyscale-readable patterns; tooltips; responsive passes; empty-state copy;
  an accessibility sweep (jsx-a11y lint and axe in Vitest). A Playwright
  smoke test is optional and local, because Playwright WebKit does not
  support the macOS 12 runner.
  *Done when:* no axe violations on the tested pages and charts never carry
  meaning by colour alone.
- **B0.1.7 — Claude Code; Pete for credentials. Deploy and document.**
  Confirm the Render workspace with Pete, identify the existing
  `poltika.onrender.com` service and confirm its Docker runtime, create the
  approved Render PostgreSQL, set `POLTIKA_DATABASE_URL`, and have Pete set
  `POLTIKA_ACCESS_PASSWORD` as a secret. Health check stays `/healthz`.
  `docs/web/FRONTEND.md` (architecture, progressive disclosure, local
  development, production build, Render, environment variables, API
  boundary, navigation, capabilities, adding a tab, model type or dataset
  type), `web/README.md`, and updates to ORIENTATION, HOSTING, CHANGELOG and
  PROGRAMME_STATUS.
  *Done when:* the live service answers 401 without the password and, with
  it, Home, Scenarios, a created run, Models and Data work, and a run's deep
  link survives a restart.

## PR grouping

1. B0.1.0 — plan and governance (docs only).
2. B0.1.1 — catalogue contracts (backend).
3. B0.1.2 — durable scenarios and workspace view (backend; GPT/Codex row).
4. B0.1.3 — web shell, serving, image and CI.
5. B0.1.4 — scenario experience.
6. B0.1.5 — Models and Data.
7. B0.1.6 — polish.
8. B0.1.7 — deployment and documentation.

Each PR is built in its own worktree off `origin/main` and merges only under
ADR-0020: CI green, branch up to date, `pr-review-preflight`, a
`poltika-reviewer` pass with no unresolved P1/P2, and, for B0.1.2 and any PR
that changes which amounts are shown, a cleared GPT/Codex row in
`review_packets/review_queue.md`. None touches `policy_specs/`,
`engines/simulator/` or a protected value.

## Capability gate

Task B0.1 is done when someone given the address and password can, without
instruction: understand what Poltika does; find or start a scenario; inspect
its headline result, fiscal effect and household/distributional effect where
available; see its evidence and assumptions; inspect the technical model and
the audit/provenance record; and browse the supported models and datasets.
Every number shown must trace to an API value, and every unavailable figure
must say so.

Meeting this gate does not meet Gate C, does not accept ADR-0018 and is not
evidence of an external pilot.

## Open decisions for Pete

- **ADR-0018 design acceptance (PETE_QUEUE Q9)** stays open. The web app
  renders its blocks without accepting its design.
- **Making `web` a required check** in the repository ruleset, unless that
  settings change is delegated (PETE_QUEUE Q15).
- **Render PostgreSQL plan/size and the access password** at deployment
  (PETE_QUEUE Q15).
