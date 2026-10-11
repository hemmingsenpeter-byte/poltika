# Repository structure

`REPOSITORY_STRUCTURE.md` is the canonical repository map for Poltika. New
production files, modules, and directories must conform to this structure.
If a proposed component doesn't have an obvious location, update this file
deliberately rather than creating an ad-hoc directory — see
[CLAUDE.md](CLAUDE.md).

This file distinguishes the **target architecture** (where things will live
once built) from the **current implementation** reconciled against `e52f5d3`
on 3 October 2026. A production directory is created only when an analytical
task in [BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md) requires it.
The programme migration creates documentation archives, not new production
modules or empty scaffolding.

## Instantiated today

```text
poltika/
├── README.md
├── CLAUDE.md
├── BUILD_PLAN_PROGRAMME.md — sole active master build order: capability Phases A–P (ADR-0021)
├── PROGRAMME_STATUS.md   — live capability/task status, evidence, owner, PR and blocker (ADR-0020)
├── PETE_QUEUE.md        — unresolved Tier C decisions; reserved authority stays with Pete
├── BUILD_PLAN_v0_3.md    — detailed household-economic-model lane for Phase B;
│                          conformance/validation maps to C and survey/secure population work to E
├── BUILD_PLAN_v0_1_6.md  — active statutory-maintenance lane: source currency and policy years
├── BUILD_PLAN_B0_1_WEB.md — detailed lane for programme Task B0.1, the web frontend (ADR-0023)
├── BUILD_PLAN_v0_2.md    — release closeout for existing static microsimulation;
│                          retained while v0.2.0 is untagged, not a competing programme order
├── BUILD_PLAN.md        — historical v0.1 build record; retained frozen doctrine anchors
├── BUILD_PLAN_v0_1_5.md  — historical redirect to the archived explainability plan;
│                          external pilot evidence remains a live capability gate
├── ROADMAP_REALIGNMENT.md — historical redirect to archived W1–W10 planning
├── ARCHITECTURE.md
├── REPOSITORY_STRUCTURE.md   (this file)
├── ROADMAP.md          — high-level direction; the master programme sets execution order
├── CHANGELOG.md
├── RESEARCH.md         — external papers/prior art, structural reference only (never a policy source; see doctrine/ip-doctrine.md)
├── pyproject.toml      — dependencies (Pydantic, PyYAML, FastAPI, SQLAlchemy, psycopg, Alembic) and dev tooling (pytest, Hypothesis, Ruff, mypy strict)
├── .python-version     — 3.12, the version CI runs
├── Dockerfile, compose.yaml, .dockerignore, deploy/entrypoint.sh
│                       — v0.1.5 Task 8.1 pilot container: API + PostgreSQL,
│                         migrations on start, policy_specs/ mounted read-only
├── uv.lock
├── .github/dependabot.yml — weekly grouped minor/patch updates for the uv lock and pinned actions (ADR-0020)
├── .github/workflows/security.yml — pip-audit of the locked dependencies (PR, main, weekly)
├── .github/workflows/static-analysis.yml — Bandit (Python; high-severity gate, all findings retained) and zizmor (all workflow findings gate); private-CI compatible
├── .github/workflows/links.yml    — lychee: offline relative-link and anchor check on `**/*.md` (required), weekly external report
├── AGENTS.md           — the CLAUDE.md rules for non-Claude agents (GPT/Codex)
├── PETE_QUEUE.md       — the open Tier C items only Pete can decide, each with the
│                         smallest action that clears it (ADR-0020)
├── CONTRIBUTING.md     — the route into the repository: worktree flow, tests, review, tiers (ADR-0020), Make targets, where files go
├── SECURITY.md         — what is in scope, how to report privately, supported versions, the automated checks
├── .github/CODEOWNERS  — the owner, and the high-risk paths (policy_specs/, engines/simulator/, tests/fixtures/, workflows)
├── .github/ISSUE_TEMPLATE/ — config.yml (blank issues off) and issue forms: bug or wrong result, source question, programme task and collaborator-visible security report; no secrets/personal data
├── .claude/            — Claude Code skills (`skills/`) and Sonnet subagent definitions
│                         (`agents/`: `poltika-worker` implements one briefed subtask,
│                         `poltika-reviewer` reviews a diff with a fresh context)
│
├── doctrine/          — permanent governing constraints; BUILD_PLAN retains detail not yet extracted
├── adr/               — permanent decision history, including superseded sequencing decisions
├── model_registry/    — Task 1.5 (doctrine/model-governance.md): registry.yaml, one entry per engine or
│                         runner (version, owner, purpose, validation status linked to its cases, evidence
│                         classes, limitations, change log), and cards/, one generated card per entry
│                         (python -m poltika.engines.assurance.model_cards). Its own directory because a
│                         model is neither a policy source pack, nor process, nor a dataset; it is
│                         reviewed YAML like those. tests/unit/engines/assurance/test_model_registry.py
│                         fails CI on an engine with no entry or card
├── policy_specs/      — per-policy source packs, specification maps, benchmarks, decisions
│                         (from v0.3 Phase 1b, facts.yaml: the fact catalogue, ADR-0016)
│                         (plus wff_as_interaction/: Task 28.5 cross-policy spec cases and
│                         Task 29 golden_households.yaml, both watched by the statutory-value guard)
│   ├── income_tax/    — Phase B Task 7 / v0.3 local 0.1 source catalogue;
│                       specification, parameters and implementation remain separately gated
│   ├── jobseeker_support/ — Phase B Task 8 / v0.3 local 0.2 source catalogue only
│   ├── sole_parent_support/ — source catalogue only; separate specification/value gates
│   └── supported_living_payment/ — source catalogue only; separate specification/value gates
├── review_packets/     — assembled review packet template/instances; v0_1_question_set/ also
│                         holds the scripts that produced its recorded results (review evidence,
│                         run by hand from the repository root; not production code, and not
│                         linted or type-checked by CI)
├── reviews/           — review and discrepancy records
├── docs/decision_log.md — every Tier A and Tier B decision made under ADR-0020's
│                         delegated acceptance, with options, rationale and reversal
├── docs/ORIENTATION.md — one-page summary of current v0.1 behaviour for a new session: outcomes,
│                         facts that always hold, inputs, runnable examples, what to read next
├── docs/research/     — Task 3's structural-only OpenFisca Aotearoa glance, and the
│                         clean-room comparative review of NZ policy-modelling projects
├── docs/releases/     — per-release limitations, measured baselines, the v0.1.5 gate map, the v0.2 population methodology and RELEASE_CHECKLIST.md (the gate-based release steps, ending in a PETE_QUEUE.md tagging request)
├── docs/programme/    — repository reconciliation/reference audits, EXECUTION.md (agent roles/bounded cycles) and POLICY_CLAIMS_BUDGET_WORKFLOWS.md (C14a/D16a/F24a/I29a use-case specification; not a second master)
├── docs/archive/      — superseded planning snapshots, never an implementation authority
│   ├── programmes/    — ADR-0019 programme and W1–W10 realignment history
│   ├── roadmaps/      — dated roadmap snapshots
│   ├── status/        — dated programme-status snapshots
│   └── build-plans/   — historical bounded release plans, including v0.1.5
├── docs/web/          — FRONTEND.md: web frontend architecture, build, deployment, environment and extension guide (B0.1.7)
├── docs/pilot/        — v0.1.5 pilot guide, hosting guide (HOSTING.md), and the pilot findings
├── docs/demo/v0_1/    — Task 35.3 demo: walkthrough, request, stored-run summary and
│                         provenance report for the v0.1 demo question
├── data/              — v0.2 Phase 1 data layer (data/README.md): raw/ (immutable
│                         snapshots), metadata/datasets/ (one manifest per snapshot),
│                         metadata/variables/dictionary.yaml, metadata/populations/
│                         (synthetic development population specs); snapshots and manifests
│                         guarded by .github/workflows/data-snapshot-guard.yml
│   └── source_archive/ — ADR-0022 passive source-preservation archive (NOT data/raw/):
│                         README.md (SOURCE PRESERVATION ONLY), sources/<system>.yaml (reviewed
│                         retrieval definitions; stats_nz.yaml), runtime/ (gitignored: blobs/sha256/,
│                         records/, metadata/, advisory/; POLTIKA_SOURCE_ARCHIVE_DIR moves it)
│
├── src/poltika/
│   ├── common/            — errors.py (exception hierarchy); safe_xml.py (the
│   │                        shared standard-library XML guard: refuses any DTD
│   │                        before parsing; used by data/xlsx.py and
│   │                        data/acquisition/stats_nz.py)
│   ├── semantics/schemas/ — policy_spec.py (Pydantic models mirroring policy.yaml);
│   │                        fact_catalog.py (v0.3 Task 1b.1, ADR-0016: the
│   │                        facts.yaml model);
│   │                        source_catalog.py (v0.1.5: sources.yaml model,
│   │                        source type and authority rank derived from kind)
│   ├── semantics/variables.py — v0.2: canonical variable dictionary model,
│   │                        Observation and Lineage, and the CanonicalContext
│   │                        read interface downstream code depends on
│   ├── semantics/population.py — v0.2 Task 2.1: the canonical population
│   │                        schema (weighted households, persons, grouping
│   │                        characteristics, facts in scenario-record form)
│   ├── semantics/units.py — v0.2 Task 2.2: dimensions, units, price bases;
│   │                        exact rescaling by scale only; named, sourced
│   │                        conversion rules (registry empty, so nominal to
│   │                        real is refused)
│   ├── semantics/entities.py — Programme Task 2.4: entity types, identifier
│   │                        schemes (unassigned without a cited rule) and
│   │                        Population definitions
│   ├── semantics/periods.py — Programme Task 2.3: period types, the frozen
│   │                        Period, named period relations with sources, and
│   │                        the v0.2 D8 refusal of unsourced conversions
│   ├── data/              — v0.2 Phase 1: manifest.py (raw-snapshot manifest),
│   │                        registry.py (checksummed dataset registry),
│   │                        metadata_index.py (Task B0.1.1: read-only listing of
│   │                        manifests, population specs and the variable
│   │                        dictionary for the web catalogue; reads no snapshot),
│   │                        transform.py (versioned transformation registry;
│   │                        transforms/ holds one module per dataset),
│   │                        xlsx.py (standard-library reader for published
│   │                        Excel workbooks, v0.2 Task 9.4),
│   │                        context.py (DataContext, the CanonicalContext
│   │                        implementation);
│   │                        acquisition/ (ADR-0022: passive source preservation,
│   │                        upstream of the governed path and never read by it):
│   │                        models.py (descriptors, RetrievalRecord, canonical JSON,
│   │                        hashing, redaction), source.py (FetchRequest, Transport,
│   │                        bounded retrying fetch with a response-size cap (D20),
│   │                        SourceConnector), archive.py
│   │                        (BlobStore protocol, LocalBlobStore, SourceArchive, change
│   │                        detection), catalogue.py (loads reviewed
│   │                        data/source_archive/sources/*.yaml), stats_nz.py (Stats NZ
│   │                        Aotearoa Data Explorer connector), data_govt_nz.py (optional
│   │                        secondary catalogue reference), ingest.py (run one/all
│   │                        entries and the failure policy), enrichment.py (optional
│   │                        OpenRouter advisory metadata, never authoritative)
│   ├── policy/            — loader.py (Task 11 parameter loader); facts.py
│   │                        (v0.3 Task 1b.1: fact catalogue loader)
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
│   │                        manifests, canonical identity, code identity,
│   │                        record_from_plain);
│   │                        reform_record.py (Task B0.1.2: reform scenario
│   │                        and run identities; store.py keeps them in the
│   │                        reform_scenario and reform_run tables, migration 0002);
│   │                        conditional.py (v0.3 Task 1b.2, ADR-0016:
│   │                        conditional answers, i.e. branches, bounds and
│   │                        next question for missing facts, all by engine
│   │                        reruns); conditional_text.py (Task 1b.2d: the
│   │                        verified plain-language summary);
│   │                        intake.py (v0.3 Task 1b.4, ADR-0016: the
│   │                        intake planner, i.e. the next question, typed
│   │                        answers and declined facts);
│   │                        population.py (v0.2 Task 2.2: population
│   │                        household → ScenarioRecord, household types);
│   │                        microsim/ (v0.2 static microsimulation:
│   │                        validation.py record checks, weighting.py
│   │                        weighted statistics, reform.py overrides of
│   │                        loaded parameters, runner.py baseline and
│   │                        reform runs with run identity, analysis.py
│   │                        weighted tables, withdrawal.py withdrawal
│   │                        paths and sweeps, worked_examples.py named
│   │                        households run once under a reform, ranges.py (v0.3 Task 1b.6)
│   │                        needs-review population ranges, explain.py verified
│   │                        population explanations, synthetic.py the
│   │                        seeded synthetic population generator and its
│   │                        CLI, calibration.py the population spec derived
│   │                        from canonical variables, calibrate_cli.py its
│   │                        composition root, crossval.py the Task 9.4
│   │                        comparison with published programme figures,
│   │                        crossval_cli.py its report writer (these two
│   │                        CLIs are the only modules outside poltika.data
│   │                        that build a DataContext) --
│   │                        never a second engine);
│   │                        store.py (Task 32, ADR-0013: append-only
│   │                        PostgreSQL scenario store -- runs, content-
│   │                        addressed artifact bytes, replay, drift re-run;
│   │                        POLTIKA_DATABASE_URL); migrations/ (Alembic)
│   ├── engines/assurance/ — provenance.py (Task 31: builds the provenance
│   │                        report from traced results -- verifies the
│   │                        run's artifact hashes, resolves source/rule/
│   │                        decision ids, renders JSON and Markdown);
│   │                        explanation.py (v0.1.5 Phase 3: deterministic
│   │                        explanations rendered only from the recorded
│   │                        trace, and verify() against the calculation;
│   │                        evidence.py (v0.1.5 Phase 1: evidence coverage
│   │                        report, run in CI);
│   │                        currency.py (v0.1.6 Task 2.1: source-currency
│   │                        report; .github/workflows/source-currency.yml
│   │                        runs it weekly and opens an issue when due))
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
│                            route over scenarios/; v0.3 Task 1b.5:
│                            resolution and POST /household/intake), and scenarios.py
│                            (Task 33.2: create/fetch/replay/re-run over
│                            the Task 32 store; 503 when
│                            POLTIKA_DATABASE_URL is unset), analyst.py
│                            (v0.1.5 Phase 6: the thin analyst page and its
│                            example requests), microsim.py (v0.2 Task
│                            10.1: population, parameters and run routes;
│                            503 when POLTIKA_POPULATION_PATH is unset) and
│                            microsim_page.py (v0.2 Task 10.2: the
│                            /analyst/microsim page); access.py (hosted
│                            pilot password, HTTP Basic, operator-set
│                            POLTIKA_ACCESS_PASSWORD); hardening.py
│                            (security headers and request-size limit);
│                            workbench.py
│                            (the analyst workbench routes under
│                            /workbench: registry, check, results,
│                            Excel/CSV export, decision text) with
│                            workbench_registry.py (instruments,
│                            parameters, sources and decisions read from
│                            the specs directory, so a new instrument
│                            spec appears with no code change),
│                            workbench_tables.py (results as generic
│                            table blocks; the page and both exports
│                            render the same blocks),
│                            workbench_export.py (xlsx and csv writers)
│                            and workbench_config.py (presentation
│                            config only: tabs, fiscal-year slots,
│                            measures, winner/loser thresholds, family
│                            types, limitations; never a policy value);
│                            v1.py and v1_schemas.py (Task B0.1.1, ADR-0023:
│                            the read-only /api/v1 catalogue of meta, models,
│                            datasets and evidence, with typed responses);
│                            v1_scenarios.py and v1_blocks.py (Task B0.1.2:
│                            durable reform scenarios and the seven-tab
│                            workspace view of typed blocks; places stored
│                            values, computes none);
│                            web.py (Task B0.1.3: ASGI middleware serving
│                            the exported web app from POLTIKA_WEB_DIR --
│                            /_next assets, and exported pages for a GET
│                            whose Accept prefers text/html on a declared UI
│                            route; everything else passes through; runs
│                            inside the password check)
│                            — no llm/ layer yet;
│                            _wff_policy_dir()/_as_policy_dir() each
│                            resolve POLTIKA_POLICY_SPECS_DIR at deploy
│                            time, ADR-0011)
│
├── scripts/ingest/        — stats_nz.py: CLI for the source-preservation archive
│                            (--list, --dataset, --all, --dry-run; cron-friendly)
├── scripts/development/   — dump_openapi.py (Task B0.1.3): writes web/openapi.json from
│                            the FastAPI app; CI regenerates and fails on drift
├── web/                   — Task B0.1.3 (ADR-0023): the web frontend. Next.js App Router,
│                            TypeScript strict, Tailwind; `output: 'export'` static build
│                            (web/out) that FastAPI serves from the same image. npm with a
│                            committed package-lock.json. See web/README.md.
│   ├── openapi.json       — generated from the API (scripts/development/dump_openapi.py)
│   └── src/
│       ├── app/           — routes only (thin: dynamic ones export one `_` placeholder)
│       ├── features/      — page-level client components, one per route
│       ├── components/    — layout/, navigation/, ui/, blocks/, states/ (generic; they
│       │                    never call fetch and never name an instrument)
│       ├── domain/        — domain types narrowed from the generated schema
│       ├── api/           — schema.gen.ts (generated), client.ts (the one fetch wrapper),
│       │                    errors.ts, schemas.ts (zod, typed against the generated
│       │                    types) and services/ (the only callers of the client)
│       ├── config/        — navigation.ts and capabilities.ts (declarative)
│       ├── format/        — central, unit-tested formatters
│       ├── lib/           — small hooks and helpers (useRouteIds, useAsync)
│       └── styles/        — globals.css design tokens
│
└── tests/
    ├── conftest.py        — shared fixtures/helpers (Task 15), used by tests/regression/;
    │                          the throwaway PostgreSQL `database_url` fixture (Task 32)
    ├── unit/
    │   ├── common/         — shared guard tests (safe_xml.py; only it parses XML)
    │   ├── data/acquisition/ — ADR-0022 archive tests (synthetic fixtures, no live
    │   │                        network) and test_archive_boundary.py, which adds to
    │   │                        data/test_boundary.py
    │   ├── policy/         — loader tests (Task 11)
    │   ├── semantics/      — vocabulary tests (Programme Tasks 2.3-2.4: periods, entities)
    │   ├── scenarios/         — combined WFF+AS runner tests (Task 28.4) and
    │   │                        interaction spec-case runner (Task 28.5),
    │   │                        golden household runner (Task 29), store
    │   │                        tests (Task 32; marked postgres, start a
    │   │                        throwaway server from initdb/pg_ctl on PATH,
    │   │                        skipped when absent), population schema and
    │   │                        adapter tests (v0.2 Tasks 2.1-2.2); microsim/
    │   │                        validation, weighting and reform tests
    │   ├── data/              — v0.2 Phase 1: manifest, registry, context and
    │   │                        dependency-boundary tests on synthetic snapshots
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
    │                          stored scenario routes; test_web_static.py,
    │                          Task B0.1.3: serving, deep links, caching, auth)
    ├── installed_artifact/ — builds and installs the real wheel into a
    │                          throwaway venv, confirms the API works
    │                          standalone (ADR-0011); marked
    │                          installed_artifact, excluded from the
    │                          default fast suite (pyproject.toml addopts)
    ├── acceptance/         — v0.1 release acceptance suite (GPT/Codex): threshold
    │                          boundaries, Hypothesis-generated invariants, cross-policy
    │                          leakage, explanation equivalence, repeat-run determinism;
    │                          statutory values read from the policy, never restated;
    │                          plus test_orientation_examples.py, which runs docs/ORIENTATION.md's
    │                          examples against the demo summary
    ├── code_replay/        — Task 32.4 replay of a stored run on its retained code
    │                          revision (marked code_replay, opt-in; CI runs it)
    ├── regression/         — known-historical-issue tests (Task 15) and the
    │                          frozen golden-result snapshot check (Task 30.4)
    └── fixtures/           — golden_results_v0_1.json (Task 30.4 frozen golden
                               results with bound policy-file hashes) and
                               golden_traces_v0_1_5.json (v0.1.5 Task 7.2 frozen
                               steps, codes and explanation summaries); both
                               watched by the statutory-value guard
```

Only `src/poltika/llm` (`api/` is now instantiated, Task 21;
`data/` by v0.2 Phase 1;
`scenarios/` by Task 28.4) and `tests/integration` (`tests/fixtures` by Task 30.4),
plus `data/processed/`, `data/fixtures/`, `config/`, and `scripts/{validate,development}/`, remain undone
from the target tree below — created incrementally as the master programme's
analytical tasks need them. `docs/` is partially
instantiated: `docs/ORIENTATION.md`, `docs/research/` and `docs/demo/v0_1/`
(above) exist; the
target tree's `docs/{data_model.md,policy_model.md,provenance.md,
assurance.md,glossary.md}` specification files do not exist yet.
`src/poltika/engines/{discovery,hypothesis}` are correctly still empty
target slots; see below. `engines/assurance/` now holds provenance,
evidence coverage, deterministic explanations and source-currency reports.
Run identities and manifests also live in `scenarios/record.py`; golden
results and traces remain in `tests/regression/` and `tests/fixtures/`.
Migration 0002 also retains each newly stored household run's verified
provenance report in `run.provenance_json`; legacy rows stay NULL.

The existing data and microsimulation modules are development-population
machinery, not evidence that national representativeness has been achieved.
`semantics/population.py` contains grouping/person metadata and policy facts;
it is not yet ADR-0017's shared household economic model. That model grows in
`semantics/` through Phase B's bounded next coding task, with reviewed WFF/AS
mappings and byte-identical existing results and IDs.

## Review and research records (v0.1.5 Task H.1)

Three directories hold the project's evidence about itself. Each record
goes in exactly one of them:

| Directory | Holds | Written by |
| --- | --- | --- |
| `docs/research/` | Source research: what a primary source says, dated checks, prior-art glances (clean-room) | GPT/Codex or Claude Code, before implementation |
| `review_packets/` | Inputs handed to a reviewer: the packet (sources, spec, diff, tests) and any scripts that produced reviewed results; `review_queue.md` lists merged PRs awaiting independent review (the cap is suspended, P17) | The author, before review |
| `reviews/` | A reviewer's output: findings, classifications and dispositions | The reviewer |

Existing records stay where they are. Several protected, hash-bound files
link to them (specifications, a source catalogue, a decision), so moving
them would change those files' hashes and break the historical links for
no gain. New records follow the table.

## Target architecture (create on demand, per task)

```text
poltika/
│
├── docs/
│   ├── ORIENTATION.md  — already instantiated; see "Instantiated today" above
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
│       │   ├── discovery/   — later causal-evidence/research capability (Phases J/P)
│       │   └── hypothesis/  — later hypothesis generation and research (Phase P)
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
├── web/                 — Task B0.1 (ADR-0023): Next.js static-export frontend, served by FastAPI;
│                          presentation only, never calculates; created by B0.1.3
│
└── outputs/
```

`engines/discovery/` and `engines/hypothesis/` are placeholders only:
Their later work supports the causal evidence library and human-gated
research in Phases J/P. Listing them names eventual slots; it does not
authorise early implementation. Assurance validates the path from evidence
through models and simulation to outputs throughout, rather than making
Discovery or Hypothesis the current product's entry point.

Registry extensions follow variables actual models require. Existing source
catalogues, policy specifications and traces suffice for current statutory
evidence links. General evidence/model graphs are earned in Phases J/M;
`NZState` belongs to Phase K. A future accounting spine, historical store,
validation extension or model registry receives a deliberate location here
when its bounded analytical task first requires production code. This
migration changes none of the package layout or dependency permissions.

## The dependency boundary

Downstream code must not reach backwards around these layers:

```text
data/  →  semantics/  →  policy/  →  engines/  →  scenarios/
```

| Directory | May depend on | Must not depend on |
| --- | --- | --- |
| `src/poltika/data/` | `common/`; `semantics/variables.py` (the canonical types it produces) | `engines/`, `policy/`, `scenarios/`, `api/`, `llm/`, other `semantics/` internals. Nothing outside `data/` imports it (`tests/unit/data/test_boundary.py`), except the web catalogue's read of dataset metadata (`api/v1.py` may import only `data/metadata_index.py` and `data/manifest.py`; Task B0.1.1, ADR-0023) |
| `src/poltika/data/acquisition/` (ADR-0022) | `common/`; standard library | `data/registry`, `data/context`, `data/transform`, `data/transforms/`, `data/manifest`'s `DatasetManifest`, `engines/`, `policy/`, `scenarios/`, `api/`, `llm/`. It never writes under `data/raw/` or `data/metadata/`. Inside `data/` but not on the governed path: nothing in the governed path (registry, context, transform, transforms/) reads the archive, and nothing outside `data/acquisition/` may name `data/source_archive` or `POLTIKA_SOURCE_ARCHIVE_DIR` (`tests/unit/data/acquisition/test_archive_boundary.py`) |
| `src/poltika/semantics/` | `common/` | source-specific formats/APIs, `engines/` |
| `src/poltika/policy/` | `semantics/`, `common/` | `data/` (raw or processed), source-specific formats |
| `src/poltika/engines/simulator/` | `semantics/`, `policy/`, `scenarios/`, `common/` | Stats NZ (or any) API, source CSV structures, LLM output |
| `src/poltika/engines/assurance/` | `semantics/`, `policy/`, `scenarios/`, `engines/simulator/`, `common/` | source-specific formats/APIs |
| `src/poltika/scenarios/` | `engines/simulator/`, `engines/assurance/`, `policy/`, `semantics/`, `common/` (Task 28.4: the combined WFF+AS runner calls both module entry points -- downstream of `engines/`, per the layer arrow above) | `data/` (raw or processed), `api/`, `llm/`, source-specific formats. **One-way rule:** `engines/` must never import `scenarios/`'s combined runner; the simulator row's permission to use `scenarios/` covers scenario *definitions* only, so no import cycle can form. |
| `src/poltika/llm/` | `scenarios/` (to build/read a `ScenarioRequest`) | `engines/simulator/` internals, raw/processed data |
| `src/poltika/api/` | `engines/simulator/`, `common/` (Task 21: directly); `scenarios/` and `engines/assurance/` for the Task 33 combined household route (`api/household.py`) and the Task 33.2 stored scenario routes (`api/scenarios.py`, via `scenarios/store.py`); `scenarios/microsim/` and `semantics/population.py` for the v0.2 routes (`api/microsim.py`), reading only the population file an operator sets in `POLTIKA_POPULATION_PATH`; `POLTIKA_POLICY_SPECS_DIR` at deploy time (ADR-0011 -- an operator-set deployment variable, not a per-request caller input); for the `/api/v1` catalogue (`api/v1.py`, Task B0.1.1), `engines/assurance/` model cards, evidence and provenance, and dataset *metadata* through `data/metadata_index.py`, located by the operator-set `POLTIKA_MODEL_REGISTRY_PATH` and `POLTIKA_DATA_METADATA_DIR` | `data/` (raw or processed), source-specific formats, a *request*-supplied policy directory path (still prohibited -- no HTTP caller may choose the policy directory) |

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
BUILD_PLAN_PROGRAMME.md  "What is the sole active build order?" (ADR-0021)
    │
    ├── PROGRAMME_STATUS.md      "What is done, in flight or blocked?"
    ├── PETE_QUEUE.md            "What still needs Pete's decision?"
    ├── BUILD_PLAN_v0_3.md       "How do we implement the household lane?"
    ├── BUILD_PLAN_v0_1_6.md     "How do we maintain statutory currency?"
    ├── BUILD_PLAN_v0_2.md       "What remains before its release tag?"
    ├── ARCHITECTURE.md          "How does it work?"
    └── REPOSITORY_STRUCTURE.md  "Where does it live?"
              │
              ▼
          doctrine/      "What decisions are fixed?"
              │
              ▼
            docs/        "Orientation, research, pilot and permanent release evidence"
```

`ROADMAP.md` describes the direction without owning a second backlog.
`BUILD_PLAN.md` preserves v0.1 history and the frozen doctrine anchors still
needed by live references. `docs/archive/` and the root historical redirects
preserve planning provenance and are non-authoritative. `adr/`, `reviews/`,
`review_packets/`, `docs/releases/` and `docs/decision_log.md` retain decision,
review and release evidence in their established locations.
