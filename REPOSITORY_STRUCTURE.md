# Repository structure

`REPOSITORY_STRUCTURE.md` is the canonical repository map for Poltika. New
production files, modules, and directories must conform to this structure.
If a proposed component doesn't have an obvious location, update this file
deliberately rather than creating an ad-hoc directory — see
[CLAUDE.md](CLAUDE.md).

This file distinguishes the **target architecture** (where things will live
once built) from what is **actually instantiated for v0.1**. Empty
directories scaffolded for hypothetical future features are their own
maintenance burden — a directory is created only when a specific
[BUILD_PLAN.md](BUILD_PLAN.md) task requires it, not in advance.

## Instantiated today

```text
poltika/
├── README.md
├── CLAUDE.md
├── BUILD_PLAN.md
├── ARCHITECTURE.md
├── REPOSITORY_STRUCTURE.md   (this file)
├── ROADMAP.md
├── CHANGELOG.md
├── RESEARCH.md         — external papers/prior art, structural reference only (never a policy source; see doctrine/ip-doctrine.md)
├── pyproject.toml      — dependencies (Pydantic, PyYAML, FastAPI, SQLAlchemy, psycopg, Alembic) and dev tooling (pytest, Hypothesis, Ruff, mypy strict)
├── .python-version     — 3.12, the version CI runs
├── uv.lock
│
├── doctrine/          — process/workflow rules, one file per BUILD_PLAN frozen doctrine section, plus narrow architectural guardrails
├── adr/               — architecture decisions with rationale and context
├── policy_specs/      — per-policy source packs, specification maps, benchmarks, decisions
│                         (plus wff_as_interaction/: Task 28.5 cross-policy spec cases and
│                         Task 29 golden_households.yaml, both watched by the statutory-value guard)
├── review_packets/     — assembled review packet template/instances
├── reviews/           — review and discrepancy records
├── docs/research/     — Task 3's structural-only OpenFisca Aotearoa glance, and the
│                         clean-room comparative review of NZ policy-modelling projects
├── docs/demo/v0_1/    — Task 35.3 demo: walkthrough, request, stored-run summary and
│                         provenance report for the v0.1 demo question
│
├── src/poltika/
│   ├── common/            — errors.py (exception hierarchy)
│   ├── semantics/schemas/ — policy_spec.py (Pydantic models mirroring policy.yaml)
│   ├── policy/            — loader.py (Task 11 parameter loader)
│   ├── engines/simulator/ — outcome.py (the ComponentResult/FactStatus
│   │                        outcome types every module returns, shared by
│   │                        WFF and AS); wff.py (Task 12 calculate_wff(); Task 20
│   │                        run_wff_module(), the module integration
│   │                        entry point over Task 11's loader + Task 12's
│   │                        calculator, per ARCHITECTURE.md's Simulation
│   │                        module contract); accommodation_supplement.py
│   │                        (Task 23 calculate_accommodation_supplement(),
│   │                        same pure-function/ComponentResult pattern;
│   │                        Task 24.7 run_as_module(), the AS module
│   │                        integration entry point mirroring
│   │                        run_wff_module() for AS's single-component
│   │                        shape); trace.py (Task 31: per-component
│   │                        provenance trace types, and the recording
│   │                        helpers that capture which parameters and
│   │                        scenario facts each component consulted)
│   ├── scenarios/         — combined.py (Task 28.4: the combined WFF+AS
│   │                        household runner -- both module entry points,
│   │                        native periods, the Task 28.3 shared-fact
│   │                        contradiction checks; no income coupling);
│   │                        record.py (Task 30: scenario records, artifact
│   │                        manifests, canonical identity, code identity);
│   │                        store.py (Task 32, ADR-0013: append-only
│   │                        PostgreSQL scenario store -- runs, content-
│   │                        addressed artifact bytes, replay, drift re-run;
│   │                        POLTIKA_DATABASE_URL); migrations/ (Alembic)
│   ├── engines/assurance/ — provenance.py (Task 31: builds the provenance
│   │                        report from traced results -- verifies the
│   │                        run's artifact hashes, resolves source/rule/
│   │                        decision ids, renders JSON and Markdown)
│   └── api/               — Task 21/24.8: FastAPI app (ADR-0010). main.py
│                            (app instance, exception handling for
│                            common.errors.PoltikaError subclasses,
│                            startup check for both policy directories),
│                            wff.py (WFF calculation route, wrapping
│                            run_wff_module() directly), and
│                            accommodation_supplement.py (Task 24.8: AS
│                            calculation route, wrapping run_as_module()
│                            directly, mirroring wff.py's pattern exactly
│                            for AS's single-component response shape),
│                            household.py (Task 33.1: combined WFF+AS
│                            route over scenarios/), and scenarios.py
│                            (Task 33.2: create/fetch/replay/re-run over
│                            the Task 32 store; 503 when
│                            POLTIKA_DATABASE_URL is unset) — no llm/
│                            layer yet;
│                            _wff_policy_dir()/_as_policy_dir() each
│                            resolve POLTIKA_POLICY_SPECS_DIR at deploy
│                            time, ADR-0011)
│
└── tests/
    ├── conftest.py        — shared fixtures/helpers (Task 15), used by tests/regression/;
    │                          the throwaway PostgreSQL `database_url` fixture (Task 32)
    ├── unit/
    │   ├── policy/         — loader tests (Task 11)
    │   ├── scenarios/         — combined WFF+AS runner tests (Task 28.4) and
    │   │                        interaction spec-case runner (Task 28.5),
    │   │                        golden household runner (Task 29), store
    │   │                        tests (Task 32; marked postgres, start a
    │   │                        throwaway server from initdb/pg_ctl on PATH,
    │   │                        skipped when absent)
    │   ├── engines/assurance/ — provenance report tests (Task 31)
    │   ├── engines/simulator/ — calculator unit tests (Task 12), spec-case and
    │   │                        benchmark-case loader/runners (Tasks 13-14),
    │   │                        module-integration tests (Task 20),
    │   │                        AS calculator unit tests (Task 23),
    │   │                        AS spec/benchmark tests (Task 24.1),
    │   │                        AS module-integration tests (Task 24.7),
    │   │                        per-component trace tests (Task 31),
    │   │                        AS rate-selector tests (Task 26a repair)
    │   └── api/             — FastAPI TestClient tests (Task 21 WFF,
    │                          Task 24.8 AS, Task 33 household and
    │                          stored scenario routes)
    ├── installed_artifact/ — builds and installs the real wheel into a
    │                          throwaway venv, confirms the API works
    │                          standalone (ADR-0011); marked
    │                          installed_artifact, excluded from the
    │                          default fast suite (pyproject.toml addopts)
    ├── acceptance/         — v0.1 release acceptance suite (GPT/Codex): threshold
    │                          boundaries, Hypothesis-generated invariants, cross-policy
    │                          leakage, explanation equivalence, repeat-run determinism;
    │                          statutory values read from the policy, never restated
    ├── code_replay/        — Task 32.4 replay of a stored run on its retained code
    │                          revision (marked code_replay, opt-in; CI runs it)
    ├── regression/         — known-historical-issue tests (Task 15) and the
    │                          frozen golden-result snapshot check (Task 30.4)
    └── fixtures/           — golden_results_v0_1.json (Task 30.4 frozen golden
                               results with bound policy-file hashes; watched by
                               the statutory-value guard)
```

Only `src/poltika/{data,llm}` (`api/` is now instantiated, Task 21;
`scenarios/` by Task 28.4) and `tests/integration` (`tests/fixtures` by Task 30.4),
plus everything under `data/`, `config/`, and `scripts/`, remain undone
from the target tree below — created incrementally as the BUILD_PLAN.md
tasks that need them are reached, not all at once. `docs/` is partially
instantiated: `docs/research/` and `docs/demo/v0_1/` (above) exist; the
target tree's `docs/{data_model.md,policy_model.md,provenance.md,
assurance.md,glossary.md}` specification files do not exist yet.
`src/poltika/engines/{discovery,hypothesis}` are correctly still empty
placeholders; see below. `engines/assurance/` was instantiated by Task 31
and holds provenance only: Task 30's regression and change attribution
live in `scenarios/record.py` (run identities and manifests) and
`tests/regression/test_golden_result_snapshot.py`.

## Target architecture (create on demand, per task)

```text
poltika/
│
├── docs/
│   ├── research/       — already instantiated; see "Instantiated today" above
│   ├── data_model.md
│   ├── policy_model.md
│   ├── provenance.md
│   ├── assurance.md
│   └── glossary.md
│
├── config/
│   ├── settings.yaml
│   └── models.yaml
│
├── data/
│   ├── README.md
│   ├── raw/            — immutable source snapshots; never manually edited (Data Acquisition Doctrine)
│   │   ├── stats_nz/
│   │   ├── treasury/
│   │   ├── ird/
│   │   └── other/
│   ├── processed/       — machine-generated transformed datasets
│   ├── fixtures/        — frozen datasets used as deterministic/regression fixtures
│   │   └── v0_1/
│   └── metadata/        — dataset manifests, source provenance, canonical mappings
│       ├── datasets/
│       └── variables/
│
├── src/
│   └── poltika/
│       ├── data/            — acquisition, validation, transformation, provenance, registry
│       ├── semantics/       — canonical Poltika variables, schemas, mappings
│       ├── policy/          — parameters, rules, dependencies (POLICY_SPECS-driven)
│       ├── engines/
│       │   ├── simulator/   — deterministic policy calculations (v0.1)
│       │   ├── assurance/   — provenance, regression, change attribution (v0.1)
│       │   ├── discovery/   — capability-driven, post-v0.2 (Roadmap Doctrine)
│       │   └── hypothesis/  — capability-driven, post-v0.2 (Roadmap Doctrine)
│       ├── scenarios/       — scenario definitions, runner, results
│       ├── llm/             — orchestration, prompts, guardrails (never calculates — see doctrine/llm_boundaries.md)
│       ├── api/             — FastAPI app; HTTP request/response boundary only (Task 21, ADR-0010)
│       └── common/          — types, errors, utilities
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── fixtures/
│
├── scripts/
│   ├── ingest/
│   ├── validate/
│   └── development/
│
└── outputs/
```

`engines/discovery/` and `engines/hypothesis/` are placeholders only:
Roadmap Doctrine puts Discovery and Hypothesis capabilities after v0.2, so
these subdirectories should not be created, or populated, for v0.1. Listing
them here is about naming the eventual slot, not authorizing early work.

## The dependency boundary

Downstream code must not reach backwards around these layers:

```text
data/  →  semantics/  →  policy/  →  engines/  →  scenarios/
```

| Directory | May depend on | Must not depend on |
| --- | --- | --- |
| `src/poltika/data/` | `common/` | `engines/`, `policy/`, `semantics/` internals |
| `src/poltika/semantics/` | `common/` | source-specific formats/APIs, `engines/` |
| `src/poltika/policy/` | `semantics/`, `common/` | `data/` (raw or processed), source-specific formats |
| `src/poltika/engines/simulator/` | `semantics/`, `policy/`, `scenarios/`, `common/` | Stats NZ (or any) API, source CSV structures, LLM output |
| `src/poltika/engines/assurance/` | `semantics/`, `policy/`, `scenarios/`, `engines/simulator/`, `common/` | source-specific formats/APIs |
| `src/poltika/scenarios/` | `engines/simulator/`, `engines/assurance/`, `policy/`, `semantics/`, `common/` (Task 28.4: the combined WFF+AS runner calls both module entry points -- downstream of `engines/`, per the layer arrow above) | `data/` (raw or processed), `api/`, `llm/`, source-specific formats. **One-way rule:** `engines/` must never import `scenarios/`'s combined runner; the simulator row's permission to use `scenarios/` covers scenario *definitions* only, so no import cycle can form. |
| `src/poltika/llm/` | `scenarios/` (to build/read a `ScenarioRequest`) | `engines/simulator/` internals, raw/processed data |
| `src/poltika/api/` | `engines/simulator/`, `common/` (Task 21: directly); `scenarios/` and `engines/assurance/` for the Task 33 combined household route (`api/household.py`) and the Task 33.2 stored scenario routes (`api/scenarios.py`, via `scenarios/store.py`); `POLTIKA_POLICY_SPECS_DIR` at deploy time (ADR-0011 -- an operator-set deployment variable, not a per-request caller input) | `data/` (raw or processed), source-specific formats, a *request*-supplied policy directory path (still prohibited -- no HTTP caller may choose the policy directory) |

Concretely: the simulator must never do

```python
requests.get("https://api.stats.govt.nz/...")       # prohibited
pd.read_csv("data/raw/stats_nz/population.csv")     # also prohibited
```

It only knows something like `context.get("demographics.population.total")`
— it does not know whether that number came from a Stats NZ CSV, the Stats
NZ API, Treasury, Postgres, or a source not yet built. This is the same
`raw → processed → canonical variables → simulator` rule as the [Data
Acquisition Doctrine](BUILD_PLAN.md#data-acquisition-doctrine-frozen) and
[ARCHITECTURE.md's data-acquisition section](ARCHITECTURE.md#external-statistical-data-acquisition)
— never `raw → simulator` directly.

## Documentation hierarchy

```text
README.md               "What is Poltika? Where do I start?"
    │
    ▼
BUILD_PLAN.md            "What are we building now?"
    │
    ├── ARCHITECTURE.md          "How does it work?"
    └── REPOSITORY_STRUCTURE.md  "Where does it live?"
              │
              ▼
          doctrine/      "What decisions are fixed?"
              │
              ▼
            docs/        "Detailed specifications" (target only — not yet instantiated)
```

`ROADMAP.md` answers what comes after v0.1.
