# Architecture

This repository is organized around a disciplined source-first workflow.

## Core intent

- Capture authoritative policy sources and traceability
- Define policy specifications in a schema-driven format
- Maintain review and discrepancy standards
- Implement policy logic only after source-grounded derivation

## Where things live

See [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) for the canonical
directory map, the target architecture, and the dependency boundaries
between layers (data → semantics → policy → engines → scenarios).

## Design principle

Poltika does not treat model memory or external implementations as authoritative policy sources. Evidence and source packaging come first.

---

## Technology stack

### v0.1, as actually implemented

This is what exists in the repo today: the lean subset of the long-term
stack below that v0.1's tasks have needed, not the full target.

| Layer | Stack |
| --- | --- |
| Core language | Python 3.12 (managed via `uv`; `.python-version`, `requires-python >= 3.12`) |
| Schemas / validation | Pydantic v2 |
| Data format | PyYAML (`policy.yaml`, `spec_cases.yaml`, `benchmarks.yaml`, `sources.yaml`, `golden_households.yaml`) |
| Backend/API | FastAPI (ADR-0010); policy directory set at deploy time (ADR-0011) |
| Database | PostgreSQL via SQLAlchemy 2 + psycopg, migrations by Alembic (ADR-0013); used only by the stored `/scenarios` routes |
| Testing | pytest + Hypothesis (the v0.1 acceptance suite) |
| Lint/type checking | Ruff + mypy (`strict = true`) |
| Build | setuptools, `src/` layout |
| CI/CD | GitHub Actions: `tests.yml` (lint, strict mypy, full suite with PostgreSQL, installed artifact, code replay) and `statutory-value-guard.yml`; both visibility only, neither can block merge (ADR-0007) |

There is no frontend, LLM layer, `data/` pipeline or container setup yet;
those rows of the target stack below are built when a BUILD_PLAN.md or
ROADMAP.md task needs them, not before.

### Long-term target stack

Recorded 2026-09-22 (Pete, relaying GPT's stack recommendation) as the
architecture to build *toward* across v0.1's remaining tasks and beyond —
this supersedes the previous "v0.1 frontend: Streamlit" line below; the
decision is to go straight to Next.js rather than build and later replace
a Streamlit UI. Optimises for four things: **determinism, auditability,
developer speed, and an architecture that can expand into the
multi-engine system (`BUILD_PLAN_PROGRAMME.md`'s state transition engine
and federated model graph, Steps 14 and 17) without a rewrite.**

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3.13 | Policy modelling, statistics, simulation and data ecosystem |
| Package/env | `uv` | Fast, simple dependency + virtual-env management |
| Backend/API | FastAPI + Pydantic v2 | Typed contracts around the deterministic engine |
| Database | PostgreSQL | Scenarios, parameters, provenance, datasets, model versions |
| ORM | SQLAlchemy 2 + Alembic | Explicit DB models + migrations |
| Data processing | Polars + PyArrow | Fast tabular processing without prematurely introducing Spark |
| Numerical | NumPy + SciPy | Simulation, distributions, sensitivity calculations — **v0.2+ per Scope Doctrine, not v0.1** |
| Statistical | statsmodels | Transparent statistical modelling where required — **v0.2+**, same reason |
| Schemas | Pydantic | Canonical variables and engine boundaries |
| Policy rules | Pure Python functions + declarative YAML/JSON metadata | Rules stay deterministic, testable and inspectable |
| Graph | NetworkX | Policy interaction graph (ROADMAP.md's v0.3) — don't deploy a graph database |
| Front end | Next.js + TypeScript | A proper UI, not coupled to Python |
| UI | Tailwind + shadcn/ui | Fast interface development |
| Charts | Plotly | Scenario distributions, sensitivities and comparisons |
| LLM | Provider abstraction over OpenAI/Anthropic APIs | Orchestrates/explains; never calculates — see the invariant below |
| Testing | pytest + Hypothesis | Unit tests plus property-based testing of policy rules |
| Quality | Ruff + mypy + pre-commit | Strong Python discipline |
| Containers | Docker + Docker Compose | Reproducibility |
| CI/CD | GitHub Actions | Tests/type checks/migrations on every change |
| Hosting | Cloud Run + Cloud SQL (later) | Don't over-engineer deployment during the first build |

Several rows (NumPy/SciPy, statsmodels, the Discovery/Hypothesis engines
NetworkX's graph feeds) name capabilities the Scope Doctrine explicitly
defers past v0.1 ("Deterministic correctness before probabilistic
sophistication. No Monte Carlo, no sensitivity analysis in v0.1"). Their
presence in this table records the long-term destination; it is not
authorization to add them to `pyproject.toml` now. Each is adopted only
when the BUILD_PLAN.md task that actually needs it is reached, per the
Architecture Doctrine's "minimum abstraction demanded by two real
policies" and REPOSITORY_STRUCTURE.md's "create on demand, per task"
discipline — the same discipline `engines/discovery/` and
`engines/hypothesis/` are already held to as named-but-unpopulated
placeholders.

**Deliberately not used in v0.1 or its near-term successors:** Kubernetes,
Kafka, microservices, Neo4j, Spark, Airflow, vector databases, fine-tuned
models, multi-agent frameworks (CrewAI, AutoGen), and a general-purpose
data lake. Each would mainly increase the surface area to build and debug
before it's earned; any of them may become justified later, but that is a
new, explicit architecture decision when it happens, not a default.
Likewise, OpenFisca is not adopted as Poltika's runtime architecture — see
"OpenFisca Aotearoa / BetterRules" below, unchanged by this stack update.

**Not yet frozen:** production cloud provider (Cloud Run/Cloud SQL above
is a working assumption, not a commitment), observability stack, queue
system, and final authentication architecture. Multi-tenant auth in
particular is deferred beyond the initial demo.

### A modular monolith, not agents, for v0.1

v0.1 is **not** built around autonomous agents talking to each other:

```text
Agent → Agent → Agent → Agent        (NOT this, for v0.1)
```

It is a modular Python monolith whose internal module boundaries are
drawn so that Discovery, Hypothesis, Simulator, and Assurance *can* later
become independent services or agents without a rewrite — paying that
distributed-systems tax only when a real capability (the federated
domain engines, `BUILD_PLAN_PROGRAMME.md` Step 17) actually needs it, not
up front. Those module boundaries already exist in REPOSITORY_STRUCTURE.md's canonical
tree (`src/poltika/{data,semantics,policy,engines/{simulator,assurance,
discovery,hypothesis},scenarios,llm,common}`) — this principle names why
that tree is shaped the way it is; it does not introduce a second,
competing tree. The one gap it surfaces: v0.3's policy interaction graph
(NetworkX, table above) has no named slot yet in REPOSITORY_STRUCTURE.md,
consistent with that file's "create on demand" discipline — add a `graph/`
entry there when v0.3 actually needs it, not now.

The layered request path this modular monolith serves:

```text
Next.js UI
      │
      ▼
FastAPI
      │
      ▼
Application / Orchestration Layer
      │
 ┌────┴─────────────────────────────┐
 │                                  │
 ▼                                  ▼
LLM services                  Deterministic Core
(explain/orchestrate)         (authoritative)
                                     │
                      ┌──────────────┼──────────────┐
                      ▼              ▼              ▼
                  Policy Rules    Simulation     Assurance
                      │              │              │
                      └──────────────┼──────────────┘
                                     ▼
                            Semantic Data Layer
                                     │
                              PostgreSQL/Data
```

### The hard invariant

> **LLMs may propose, retrieve, classify, orchestrate and explain. They may
> not produce authoritative numerical policy outcomes. Every published
> quantitative result must be reproducible from versioned inputs,
> deterministic calculation code and recorded assumptions.**

This is not new policy — it is the same rule the "Critical architectural
rule" section below already enforces (and Tasks 11-14 already built to).
It is stated here as a named, quotable invariant because it is the single
rule most load-bearing for Poltika's credibility to Treasury, ministries,
and other government users: everything else in this document is
negotiable engineering detail against that baseline.

### Critical architectural rule: the LLM never calculates policy outcomes

The LLM's job is limited to translation and explanation, never arithmetic or policy logic:

```text
"Increase WFF FTC by 10%"
          ↓
Claude/GPT
          ↓
ScenarioRequest(...)
          ↓
FastAPI / orchestration
          ↓
Python policy engines
          ↓
Postgres / versioned parameters
          ↓
Deterministic result + provenance
          ↓
Next.js UI
```

Natural language → structured Pydantic `ScenarioRequest` → deterministic Python engines → calculated result → LLM explanation. All policy calculation happens in deterministic, testable Python engines; the AI layer never produces a number.

### Simulation module contract

The stack table names a "common `DomainEngine` interface" for domain
engines. This section is that interface's minimal field list — written down
before Task 12 builds `calculate_wff()`, so WFF becomes the first instance
of a general contract rather than something the Simulator quietly becomes
synonymous with. It is documentation, not code: no base class, ABC, or
`Protocol` is introduced by this section, and none should be until a second
module (Accommodation Supplement, Task 23) actually exercises the contract
— consistent with Architecture Doctrine's "minimum abstraction demanded by
two real policies."

It does not introduce new fields. Every module-contract concept below maps
onto a field `policy.yaml` (`policy_specs/SCHEMA.md`) already has, or onto
something Task 10/22's process already produces — the contract is a thin
function-signature convention over data that already exists, not a parallel
schema:

| Contract field | Comes from | Notes |
| --- | --- | --- |
| `module_id` | `policy.yaml`'s `policy_id` | e.g. `working_for_families` |
| `module_version` | `policy.yaml`'s `policy_version` | `null` until the Task 10/22 review gate passes and `status: approved` is set |
| `schema_version` | `policy.yaml`'s `schema_version` | checked before `module_version`, per SCHEMA.md's Task 7 review response |
| `required_inputs` | `policy.yaml`'s `inputs` | named facts: owner, type, unit, period, `missing_outcome` |
| `parameters` | `policy.yaml`'s `parameters` | effective-dated, source-linked |
| `produced_outputs` | `policy.yaml`'s `outputs` | components plus outcome state: `calculated` / `unsupported` / `needs_review` — never a silent zero |
| `assumptions` | `specification.md`'s cited source-rule IDs and "review gates and source checks" | no separate assumptions ledger yet; one may be needed once modules with genuinely competing assumptions coexist (post-v0.1) |
| `data_dependencies` | canonical variable IDs referenced by `inputs`, per the Data Acquisition Doctrine | e.g. the Stats NZ Statistical Area Unit lookup AS's Task 22a needs; WFF has none identified so far |
| `dependencies` | **new concept** — other `module_id`s this module's inputs or outputs connect to | empty for WFF v0.1 (Task 20 is single-module simulator integration, not cross-module); becomes real content at v0.3's policy interaction graph, not before |
| `calculate()` / `run()` | the pure function itself (e.g. `calculate_wff()`) | deterministic, canonical inputs + versioned parameters in, output + outcome state out; no I/O, no network, no LLM — the existing "LLM never calculates" rule applies at the module boundary, not just the top-level architecture |
| `validation_checks` | **new concept** — the schema-version and `status == "approved"` gates already specified in SCHEMA.md's Task 7 review response, plus any module-specific invariant a module chooses to add | not a new mechanism; naming the existing gates as a module-contract field |
| `provenance` | `source_catalog` plus the Data Acquisition Doctrine's 11-field raw-snapshot manifest | resolved per-input, not accumulated per-module — a module doesn't carry its own separate provenance store |

`dependencies` is the one field with no content yet, correctly — WFF is the
only module being built, so there is nothing for it to depend on. That's
expected, not a gap: cross-module dependencies are v0.3's job
(`ROADMAP.md`), not something to simulate now with an empty list that means
nothing yet.

### OpenFisca Aotearoa / BetterRules

Neither OpenFisca Aotearoa nor the historical BetterRules implementation is the chosen runtime or framework for Poltika. They are structural/pattern references only, subject to the timing rules in the [IP Doctrine](BUILD_PLAN.md#ip-doctrine-frozen) — never a source of policy logic or values.

### External statistical data acquisition

Poltika depends on authoritative external data (Stats NZ, Treasury, IRD, MSD,
etc.), not on any live statistical API. The acquisition mechanism is
replaceable; the canonical data contract is stable. See the [Data Acquisition
Doctrine](BUILD_PLAN.md#data-acquisition-doctrine-frozen) for the frozen
rule; this section is the conceptual picture.

**v0.1:**

```text
Authoritative source
        ↓
Manual acquisition
        ↓
Immutable/versioned raw snapshot
        ↓
Transformation + validation
        ↓
Canonical Poltika variables
        ↓
Simulator
        ↓
Assurance
```

**Later (same downstream layers, different acquisition mechanism):**

```text
Authoritative source API
        ↓
Automated connector
        ↓
Immutable/versioned raw snapshot
        ↓
SAME transformation + validation
        ↓
SAME canonical Poltika variables
        ↓
SAME simulator
        ↓
SAME Assurance system
```

The simulator never depends on a Stats NZ API response, CSV structure,
endpoint, or other source-specific representation — only on canonical
Poltika variables. v0.1 uses only the minimum datasets a given policy
vertical actually needs to run and validate, not a full agency catalogue.

Raw snapshot provenance must identify: source organisation, dataset/series,
source URL or identifier where appropriate, retrieval date,
observation/reference period, units, geography/population where applicable,
retrieval method, raw snapshot/version, transformation/version, and canonical
Poltika variable mapping. v0.1's retrieval method is `manual_download`; a
later `stats_nz_api` method can replace it without changing the canonical
variable or simulator interface.

This is parameterisation/calibration of a deterministic system using
versioned data — not "training Poltika" on it. The LLM layer is never relied
on to memorise or calculate these values.

Frozen v0.1 datasets double as regression fixtures, inside the existing
Assurance/provenance architecture rather than a separate system: the same
scenario against the same input snapshot must produce the same deterministic
result, and an output change must be attributable to source data updates,
transformation changes, parameter changes, policy-rule changes, or
simulation-code changes.

### Coding workflow

Pete + VS Code/Claude Code handle repo implementation. GPT acts as the architecture/policy-model/review layer, with independent review used to catch implementation drift. See the Roles section of [BUILD_PLAN.md](BUILD_PLAN.md) for the full division of responsibilities.

### Future consideration: Jev (structured decision model)

Jev, from TypeSafe AI, is a "System 1" decision model: given program state (text, logs, JSON) plus fixed typed questions, it returns calibrated yes/no answers, rubric scores, or multiple-choice selections in a single ~70–500ms pass, instead of generating prose. It cannot hallucinate free text because it only selects from a predefined schema of options.

That profile does not fit the fresh-context adversarial reviewer role (BUILD_PLAN.md's "Fresh-context reviewer") — that role requires independently deriving expected behaviour from primary sources and prose reasoning, which is exactly what Jev is not built for. Jev is a better structural fit for narrower, high-volume, schema-bound checks elsewhere in the pipeline, for example:

- **Discrepancy pre-triage** — a fast first-pass classification into the Review Doctrine's taxonomy (CODE_ERROR, TEST_ERROR, SPEC_ERROR, etc.) before a model or Pete confirms it, not a replacement for that confirmation
- **Agent/tool routing** — deciding which `DomainEngine` or workflow path an orchestration layer should invoke for a given `ScenarioRequest`
- **CI gate checks** — rubric-style pass/fail evals on structured test output, distinct from the statutory-value protection mechanism itself

This is not scoped or decided for v0.1 — it's a noted possibility for later capability phases (most plausibly alongside the AI layer / orchestration work, not the source-interpretation or adversarial-review roles), and would need the same explicit-approval treatment as any other architecture change before adoption.
