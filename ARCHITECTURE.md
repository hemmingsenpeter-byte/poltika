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

The primary computational path is:

```text
Authoritative sources and versioned data
    → semantic contracts required by the model
    → source-grounded models
    → scenarios and deterministic simulation
    → analytical outputs and analyst interfaces

Assurance validates sources, models, runs and outputs throughout.
```

The active execution order is [BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md)
(ADR-0021). Complete analytical vertical slices earn shared infrastructure.
Current source catalogues, policy specifications, calculation traces and
benchmarks support the household work without a general evidence graph.
Discovery, Hypothesis and AI are later capabilities above the modelling
system; the Simulator and reviewed models remain the numerical authority.

For the long-term shape of the whole system (NZState, the variable registry,
evidence graph, accounting spine, orchestrator and decision layers), see
[Long-term target architecture](#long-term-target-architecture-one-layered-system)
at the end of this file. It is a destination, not a build authorisation.

---

## Technology stack

### Released v0.1 foundation

This is the foundation at tag `v0.1.0` (release published 26 September 2026). It is a
historical baseline, rather than a description of every capability now on
`main`. [BUILD_PLAN.md](BUILD_PLAN.md) retains its build record and frozen
doctrine anchors.

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

### Current implementation on main

Reconciled against `e52f5d3` on 3 October 2026. The release foundation is
reused by the following merged capabilities; their existence does not imply
that each release or external-user gate has passed.

| Capability | Current implementation and limits |
| --- | --- |
| Household policy calculations | Scoped WFF and AS engines, combined runner and conservative shared-fact checks; no income tax, main-benefit calculators, shared household economic model or combined disposable income yet |
| Assurance | Source ranks and evidence checks; parameter provenance, calculation steps, reason codes, deterministic explanations and verification; source-currency reporting |
| Scenario identity and replay | Hash-bound scenario records and retained-code replay; append-only PostgreSQL scenario persistence |
| Data | Manifest-tracked immutable snapshots, checksummed dataset registry, versioned transformations and canonical variable dictionary |
| Population simulation | Canonical `PopulationDataset`, synthetic generator, weighting statistics, baseline/reform runner, grouped analysis, per-policy withdrawal paths and published-aggregate comparisons |
| Population limits | Synthetic development population explicitly labelled as not an estimate for New Zealand; independent marginals and equal weights do not establish representativeness or robust calibration |
| Analyst interfaces | HTML analyst and microsimulation pages served by FastAPI; intake questions and conditional answers |
| Analyst Workbench | Spec-derived instrument registry, reform checks, tabular results and CSV/XLSX export backend; complete workbench UI remains to be delivered; ADR-0018 acceptance remains a recorded decision gate |
| Pilot deployment | Docker/Compose, password protection, security headers, request limits and CI image smoke test; deployment readiness is separate from evidence of an external pilot |
| Quality | Ruff, strict mypy, pytest/Hypothesis, evidence coverage, PostgreSQL, installed-artifact and retained-code replay checks; statutory-value visibility and immutable-snapshot guards |

The Python runtime remains 3.12. Population runs are kept in process memory;
the existing PostgreSQL store persists household scenarios. There is no
Next.js application or LLM implementation. Phase B reuses the household
engines and their identities; Phase C completes the analyst workflow;
Phase E hardens existing population machinery.

### Long-term target stack

Recorded 2026-09-22 (Pete, relaying GPT's stack recommendation) as the
architecture to build *toward*. The recorded frontend destination is
Next.js rather than Streamlit. Existing HTML analyst pages and the workbench
backend are reused; a frontend rewrite is not a prerequisite for Pilot 1.
Optimises for four things: **determinism, auditability,
developer speed, and an architecture that can expand into the
multi-engine system (`BUILD_PLAN_PROGRAMME.md`'s dynamic model in Phase K
and model composition in Phase M) without a rewrite.**

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3.13 | Policy modelling, statistics, simulation and data ecosystem |
| Package/env | `uv` | Fast, simple dependency + virtual-env management |
| Backend/API | FastAPI + Pydantic v2 | Typed contracts around the deterministic engine |
| Database | PostgreSQL | Scenarios, parameters, provenance, datasets, model versions |
| ORM | SQLAlchemy 2 + Alembic | Explicit DB models + migrations |
| Data processing | Polars + PyArrow | Fast tabular processing without prematurely introducing Spark |
| Numerical | NumPy + SciPy | Adopt only when an analytical slice requires them; formal uncertainty belongs to Phase J |
| Statistical | statsmodels | Transparent statistical modelling where a reviewed model requires it |
| Schemas | Pydantic | Canonical variables and engine boundaries |
| Policy rules | Pure Python functions + declarative YAML/JSON metadata | Rules stay deterministic, testable and inspectable |
| Graph | NetworkX | Household dependency graph when Phase B requires it; broader evidence/model graphs follow real needs in Phases J/M |
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
when the master programme's analytical task needs it, per the
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
distributed-systems tax only when a real capability (model federation,
`BUILD_PLAN_PROGRAMME.md` Phase M) actually needs it, not
up front. Those module boundaries already exist in REPOSITORY_STRUCTURE.md's canonical
tree (`src/poltika/{data,semantics,policy,engines/{simulator,assurance,
discovery,hypothesis},scenarios,llm,common}`) — this principle names why
that tree is shaped the way it is; it does not introduce a second,
competing tree. The one gap it surfaces: Phase B's household dependency graph
(NetworkX, table above) has no named slot yet in REPOSITORY_STRUCTURE.md,
consistent with that file's "create on demand" discipline — add a `graph/`
entry there when the household calculation actually needs it, not now.

The eventual layered request path is below. Existing HTML clients call
FastAPI directly; the LLM path belongs to Phase P.

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

The eventual Phase P path is natural language → structured Pydantic
`ScenarioRequest` → deterministic Python engines → calculated result → LLM
explanation. Current explanations are deterministic templates without an
LLM. All policy calculation happens in deterministic, testable Python
engines; AI does not become a numerical source.

### Simulation module contract

This section records the minimal policy-module contract originally written
before Task 12 built `calculate_wff()`. WFF and Accommodation Supplement now
exercise its pure-function, parameter and outcome pattern. The contract is
documentation: it does not introduce a `DomainEngine` base class, ABC or
`Protocol`. A shared interface is added only when multiple actual models
require it, under the Architecture Doctrine.

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
| `assumptions` | `specification.md`'s cited source-rule IDs and "review gates and source checks" | Caller assertions are recorded in traces and reform overrides in run records; a broader assumption registry is introduced only when actual models require it |
| `data_dependencies` | canonical variable IDs referenced by `inputs`, per the Data Acquisition Doctrine | e.g. the Stats NZ Statistical Area Unit lookup AS's Task 22a needs; WFF has none identified so far |
| `dependencies` | Other `module_id`s this module's inputs or outputs connect to | WFF/AS currently have shared-fact checks and no income coupling; add source-derived dependency content when Phase B's connected household calculations require it |
| `calculate()` / `run()` | the pure function itself (e.g. `calculate_wff()`) | deterministic, canonical inputs + versioned parameters in, output + outcome state out; no I/O, no network, no LLM — the existing "LLM never calculates" rule applies at the module boundary, not just the top-level architecture |
| `validation_checks` | **new concept** — the schema-version and `status == "approved"` gates already specified in SCHEMA.md's Task 7 review response, plus any module-specific invariant a module chooses to add | not a new mechanism; naming the existing gates as a module-contract field |
| `provenance` | `source_catalog` plus the Data Acquisition Doctrine's 11-field raw-snapshot manifest | resolved per-input, not accumulated per-module — a module doesn't carry its own separate provenance store |

The existing WFF and AS slices have no modelled income-coupling edges;
the combined runner checks their shared asserted facts. Phase B's household
dependency graph adds only the edges its independently sourced
specifications establish.

### OpenFisca Aotearoa / BetterRules

Neither OpenFisca Aotearoa nor the historical BetterRules implementation is the chosen runtime or framework for Poltika. They are structural/pattern references only, subject to the timing rules in the [IP Doctrine](BUILD_PLAN.md#ip-doctrine-frozen) — never a source of policy logic or values.

### External statistical data acquisition

Poltika depends on authoritative external data (Stats NZ, Treasury, IRD, MSD,
etc.), not on any live statistical API. The acquisition mechanism is
replaceable; the canonical data contract is stable. See the [Data Acquisition
Doctrine](BUILD_PLAN.md#data-acquisition-doctrine-frozen) for the frozen
rule; this section is the conceptual picture.

**Released acquisition contract, reused by the current data layer:**

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

**Later automated acquisition (same downstream layers):**

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

---

## Long-term target architecture: one layered system

Recorded 2026-09-30 (Pete), retained under ADR-0021. This is the long-term
shape of Poltika. It
describes where the roadmap leads, not what exists today. It does not
authorise building any layer, store, registry or model it names. Each piece
is built only when a task in the active master programme needs it, under the
same "create on demand" discipline and Scope Doctrine that govern the
long-term stack table above. The hard invariant and the "LLM never
calculates" rule above apply unchanged at every layer. Figures in the
examples below (debt ratios, dollar amounts, variance shares, model
versions) are illustrative. They are not Poltika outputs or sourced values.

The destination is one layered computational system. The following diagram
describes its eventual layers, not the order in which they must be built.
Its inputs remain authoritative evidence and data; models and the Simulator
produce numerical outcomes; Assurance validates the whole path. The
capability gates in the master programme determine when a layer is earned:

```text
┌──────────────────────────────────────────────────────────────┐
│                     HUMAN DECISION LAYER                     │
│ Public Futures Lab │ Analysts │ Govt │ Researchers │ APIs    │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                  AI / QUERY / EXPLANATION LAYER              │
│ Natural language │ Research │ Hypotheses │ Explanation       │
│                AI proposes; models execute                   │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    DECISION INTELLIGENCE                     │
│ Scenario comparison │ Cost of delay │ VoI │ Policy search    │
│ Sensitivity │ Pareto frontiers │ Robustness                  │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    SIMULATION ORCHESTRATOR                   │
│ Runs models │ Resolves dependencies │ Time steps │ Reconcile │
└───────────┬──────────────────┼───────────────────┬───────────┘
            │                  │                   │
     ┌──────▼──────┐    ┌──────▼──────┐    ┌───────▼─────┐
     │ Household   │    │    Macro    │    │   Spatial   │
     │ / Fiscal    │    │             │    │ / Physical  │
     ├─────────────┤    ├─────────────┤    ├─────────────┤
     │ Tax         │    │ GDP         │    │ Housing     │
     │ WFF         │    │ Prices      │    │ Transport   │
     │ Benefits    │    │ Wages       │    │ Energy      │
     │ NZ Super    │    │ Employment  │    │ Water       │
     └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
            │                  │                  │
     ┌──────▼──────┐    ┌──────▼──────┐           │
     │   Health    │    │ Firms/Labour│           │
     │ / Demography│    │ / Migration │           │
     └──────┬──────┘    └──────┬──────┘           │
            └──────────────────┼──────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                SHARED STATE + ACCOUNTING SPINE               │
│ NZState │ Sector ledgers │ Stocks/flows │ Reconciliation     │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                     MICRO / POLICY ENGINE                    │
│ Statutory kernel │ Microsimulation │ Synthetic population    │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                     KNOWLEDGE / EVIDENCE                     │
│ Evidence graph │ Causal library │ Variable registry          │
│ Assumptions │ Legislation │ Parameters │ Provenance          │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                         DATA PLATFORM                        │
│ Official data │ Microdata │ Spatial │ Admin │ High-frequency │
│ Historical State Store │ Versioned snapshots                 │
└──────────────────────────────────────────────────────────────┘
     ║ Validation ║ Uncertainty ║ Prediction Ledger ║
     ║ Governance ║ Security    ║ Reproducibility   ║
              CUT THROUGH EVERY LAYER
```

At national scale, connected models communicate through a common
representation of New Zealand. Near-term household calculations use the
bounded household contract and source-derived dependencies. They do not
require a national state schema or federation before serving analysts.

### 1. The centre of Poltika: NZState

This is Phase K's dynamic national-model contract, introduced only when
real state-transition requirements justify it. It is not a Phase B
household-model prerequisite.

At time `t`, `S_t` is Poltika's best representation of New Zealand at time
`t`. Conceptually:

```text
NZState
├── population   people, households, age structure, migration, health states
├── economy      GDP, production, productivity, prices, wages, employment
├── crown        revenue, expenditure, assets, liabilities, debt
├── firms        industries, employment, investment, balance sheets
├── households   incomes, taxes, transfers, housing, wealth/debt
├── physical     housing stock, transport, electricity, water, infrastructure
└── external     trade, capital flows, exchange rates, global conditions
```

NZState is not one enormous database table. It is a contract defining the
variables different models can read and write.

### 2. Underneath NZState: the National Variable Registry

The existing canonical variable dictionary is the seed. Phase B extends
only the units, periods, entities and variables its household models use.
Broader registry coverage grows from actual models rather than an exhaustive
national catalogue built before the first product.

Every variable in NZState has exactly one canonical definition. For example:

```yaml
id: NZ.CROWN.NET_CORE_CROWN_DEBT
type: stock
unit: NZD
frequency: quarterly
geography: NZ
price_basis: nominal
source:
  organisation: Treasury
uncertainty: ...
dependencies: ...
versions: ...
```

```yaml
id: NZ.POPULATION.AGE_65_PLUS
type: stock
unit: persons
frequency: annual
source:
  organisation: Stats NZ
dependencies: ...
```

This prevents a future where the fiscal model means one thing by "income",
the household model another and a Stats NZ pipeline a third; where the
health model works in calendar years and the fiscal model in fiscal years;
or where the housing model uses nominal dollars and the macro model real
ones. The Registry is Poltika's common language. It extends the canonical
Poltika variables the Data Acquisition Doctrine already requires (see
"External statistical data acquisition" above); it does not replace them.

### 3. Beneath that: the Evidence Graph

Current statutory source maps, decisions, parameters and calculation traces
provide the needed household evidence links. General causal/evidence graph
infrastructure is earned by behavioural mechanisms in Phase J and broader
model composition in Phase M, rather than blocking Phases B–D.

The Variable Registry says what things mean. The Evidence Graph says why
Poltika believes them:

```text
Income tax legislation
  → Tax threshold rule
  → Statutory kernel
  → Household disposable income
  → Consumption response
  → GST revenue
  → Crown revenue
  → Debt trajectory
```

Every edge carries metadata: source, equation, parameter, evidence class,
population, reference period, uncertainty and validation status. So a
question like "Why does Policy X reduce 2040 debt by $7.2b?" can be answered
by traversing the graph backwards.

NZState represents the world. The Evidence Graph represents Poltika's
knowledge about the world.

### 4. The statutory kernel changes policy settings

This is the bottom of the policy machinery, and where v0.1's work sits. A
policy change is not represented as "WFF increases". It becomes executable,
effective-dated, source-cited parameters and rules:

```text
family_tax_credit_rate = X
abatement_threshold    = Y
abatement_rate         = Z
effective_date         = <date>
```

Those rules execute against households:

```text
POLICY → STATUTORY KERNEL → HOUSEHOLD ENTITLEMENTS → HOUSEHOLD INCOME
```

The Ground Truth rules in CLAUDE.md and the doctrine apply here without
change: every statutory value comes from a cited primary NZ source.

### 5. Microsimulation translates rules into population effects

The statutory kernel answers "What happens to this household?".
Microsimulation asks "What happens to 2 million households?":

```text
PolicyRules + Household_i → Outcome_i,   for i = 1 … N
```

then aggregates:

```text
Policy
  → synthetic/weighted population
  → household outcomes
  → by income decile, age group, region, family type,
    housing tenure, employment type
  → national totals
```

This produces both fiscal and distributional effects.

### 6. The accounting spine prevents the models cheating

It sits immediately around the shared state. A $2b government transfer
cannot be written as `HouseholdIncome += $2b`. The spine requires both
sides:

```text
Crown cash       −$2b
Household cash   +$2b
```

Behavioural models then determine what happens next (consumption, saving,
debt repayment, imports, investment → GST, firm revenue, bank deposits,
trade balance → second-round effects). Every financial flow must reconcile.
That is what keeps federation sane.

### 7. Domain models become plug-ins

Poltika does not contain one universal simulation algorithm. The
orchestrator runs domain models (demography, housing, health, labour,
energy, fiscal, trade, macro, transport, …), each implementing a common
contract:

```text
INPUT:   NZState_t, PolicyState_t, ScenarioState_t
OUTPUT:  ProposedStateChanges, FinancialFlows, Diagnostics,
         Uncertainty, EvidenceReferences
```

A weak housing model can later be replaced without rewriting the health
system. This is the long-term extension of the "Simulation module contract"
above, which stays the binding contract for policy modules until a real
cross-module need changes it through an explicit architecture decision.

### 8. The orchestrator controls causality and time

Models cannot run in arbitrary order. The orchestrator owns dependency
resolution, time stepping, iteration/convergence, model versions, scenario
configuration and accounting reconciliation. For one year:

```text
2029 STATE
  → Demographics
  → Migration / labour supply
  → Production / wages
  → Household incomes
  → Tax + transfer engine
  → Consumption / housing
  → Health / infrastructure demand
  → Crown accounts
  → Macro feedback
  → Reconciliation
  → 2030 STATE
```

Some feedback relationships may need iteration within a year until the
system converges. The core of mature Poltika is then:

```text
S_{t+1} = F(S_t, P_t, X_t, θ)

S_t  national state
P_t  policy settings
X_t  external/scenario variables
θ    model parameters
```

### 9. The baseline is one special simulation

There is no separate "forecast model" and "policy model". Define
`P_baseline` and simulate `S_2027 → S_2028 → … → S_2065`; that is the
baseline. Change the policy to `P_reform` and simulate again. The policy
effect is:

```text
ΔS_t = S_t(reform) − S_t(baseline)
```

This is the fundamental comparative operation throughout Poltika.

### 10. Causal evidence supplies behavioural parameters

The statutory kernel is deterministic; behaviour is not. If household
disposable income rises 10%, the consumption response comes from the Causal
Evidence Library:

```text
MARGINAL_PROPENSITY_TO_CONSUME
  NZ causal estimate:          ...
  NZ observational estimate:   ...
  International estimate:      ...
  Chosen parameter:            ...
  Reason:                      ...
  Distribution:                ...
  External-validity rating:    ...
```

The domain model consumes the parameter. It does not invent it:

```text
Evidence → Parameter → Model        (this)
Model → convenient parameter        (never this)
```

### 11. Uncertainty propagates through everything

With uncertain parameters (for example productivity, migration and
health-cost growth), Poltika runs ensembles across plausible values and
scenarios instead of a single `F(S, P, θ)`:

```text
2065 Crown debt   (illustrative)
  Median       78% GDP
  50% range    68–91%
  90% range    51–126%
```

Sensitivity analysis then asks why the range is so wide (for example: real
interest rate 29%, productivity 24%, health-cost growth 21%, migration 12%,
other 14%). That feeds directly into Value of Information. Per the Scope
Doctrine, none of this is v0.1.

### 12. Validation is a parallel architecture

Poltika runs two systems side by side:

```text
PRODUCTION:   Data → State → Models → Simulation → Result
                                  │
                                  ▼
VALIDATION:   Tests, historical replay, benchmark comparison,
              prediction ledger, calibration scoring, model diagnostics
```

Every model carries a validation record as part of its metadata, for
example:

```text
HousingModel v4.2   (illustrative)
  Statutory tests       PASS
  Regression tests      PASS
  Historical fit        GOOD
  Shock replay          MODERATE
  Forward predictions   73 resolved
  Calibration           GOOD
  Known limitations     [...]
```

This grows out of the existing three test classes (spec, benchmark,
regression) and the Assurance engine.

### 13. Continuous state estimation closes the loop

Once real data arrives:

```text
REAL NZ → OBSERVATIONS → STATE ESTIMATOR ← previous state
                               │
                               ▼
                           NZState_t → POLTIKA → FORECAST → REAL NZ ↺
```

That is the point where Poltika becomes operational rather than
periodically reconstructed.

### 14. Decision intelligence sits above simulation

Cost of Delay, Value of Information, Policy Search and Pareto frontiers are
not separate models. They are algorithms operating one underlying
simulator. Cost of Delay runs `Policy_2028`, `Policy_2031` and
`Policy_2034` and compares outcomes. Value of Information manipulates
uncertainty distributions. Policy Search repeatedly modifies `P` and runs
Poltika.

### 15. Policy search is an inverse problem

Normal Poltika maps policy to outcomes. Policy Search reverses it:

```text
DESIRED CONSTRAINTS → SEARCH ENGINE → POLTIKA → RESULTS → SEARCH ENGINE ↺
```

For example, with constraints such as debt < X, poverty ≤ baseline,
GDP/person > baseline, emissions < Y and infrastructure spend ≥ Z, the
search engine proposes policies, Poltika simulates them, and the optimiser
learns where feasible regions exist:

```text
10,000,000 candidate policies → simulation → constraints
  → 18,400 feasible → Pareto dominance → 47 trajectories   (illustrative)
```

Humans choose among the survivors.

### 16. AI sits above all of this and never bypasses it

A user asks: "What combination of housing, migration and tax changes could
raise median real disposable income without worsening the 2045 fiscal
position?" The LLM converts that into a structured request:

```yaml
objective: maximize median_real_disposable_income
constraints:
  - fiscal_balance_2045 >= baseline
allowed_policy_domains: [housing, migration, taxation]
```

```text
LLM → Query planner → Policy Search → Poltika simulator
    → Evidence Graph → Results → LLM explanation
```

The LLM is the interface and research assistant. It does not calculate the
answer. This is the hard invariant above, applied at full scale.

### 17. Three graphs

- **State graph: what exists?** People, households, firms, government,
  housing, infrastructure, money, resources.
- **Causal/evidence graph: what affects what, and why do we believe it?**
  For example tax → disposable income → consumption → firm revenue →
  employment, with evidence attached to every edge.
- **Accounting graph: where did everything go?** Government −$1 →
  household +$1.

Every major simulation must satisfy all three at once. That is a much
stronger architecture than a "giant economic model".

### 18. Five logical stores

1. **Evidence store**: legislation, papers, reports, sources.
2. **Data store**: observed historical NZ data.
3. **State store**: versioned NZState snapshots.
4. **Model registry**: models, parameters, dependencies, versions,
   validation status.
5. **Run store**: scenarios, inputs, outputs, traces, uncertainty,
   predictions. The Prediction Ledger can be an immutable subset of it.

These are logical stores, not a decision to deploy five databases. The
"Deliberately not used" list above still stands.

### 19. Worked example: NZ Super eligibility from 65 to 67

A hypothetical proposal shows one run touching almost the whole
architecture:

1. **Policy**: the statutory kernel encodes the proposed transition
   schedule.
2. **Population**: the demographic model identifies affected cohorts.
3. **Microsimulation**: the household engine calculates lost NZ Super
   payments and other benefit and tax interactions.
4. **Behaviour**: the Causal Library supplies evidence on retirement,
   labour participation and savings responses.
5. **Labour**: the labour model estimates employment changes.
6. **Macro**: additional labour affects output, wages and tax bases.
7. **Household**: income changes feed consumption and saving.
8. **Crown**: the fiscal model calculates NZ Super savings, additional
   taxes, other benefit spending and debt servicing.
9. **Accounting**: the spine reconciles all flows.
10. **Health**: where retirement behaviour affects relevant health
    utilisation, the health model propagates supported effects.
11. **Long-run state**: everything propagates `2028 → 2029 → … → 2065`.
12. **Uncertainty**: plausible behavioural, demographic and economic
    parameters are run as an ensemble.
13. **Distribution**: effects by age, income, household type and other
    supported dimensions.
14. **Evidence**: every material pathway is traceable.
15. **Validation**: relevant submodels have historical and forward
    performance records.
16. **Decision layer**: compare 65, 66, 67, indexation alternatives,
    transition schedules and other user-specified scenarios; Cost of Delay
    compares implementation dates.

### The deepest principle: four kinds of truth

There are four kinds of truth inside Poltika, and they must never be
blurred:

- **Observed**: what happened.
- **Deterministic**: what laws and accounting identities mathematically
  require.
- **Estimated**: what evidence suggests about behaviour and causal
  relationships.
- **Simulated**: what follows when those are combined under specified
  assumptions.

Every number Poltika produces should know which category it belongs to.
The approved [epistemic constitution](doctrine/epistemic-constitution.md)
provides the operational eight-class taxonomy. Caller assertions are
Scenarios, explicit assumptions are Assumptions, and calculated results are
Model outputs. The `calculated` / `unsupported` / `needs_review` states are
calculation gates, distinct from those evidence classes. The four categories
above remain a conceptual description of the long-term system.

### The architecture in one sentence

Poltika maintains an evidence-linked representation of New Zealand's
state; deterministic rules and validated domain models transform that state
through time; a shared accounting spine reconciles their interactions;
observations continuously test and update the system; decision-intelligence
algorithms explore alternative futures; and AI lets humans interrogate the
machinery without becoming the machinery itself.

### First-class concepts

The fundamental concepts of the eventual technical architecture are:
`NationalVariable`, `Evidence`, `PolicyRule`, `NZState`, `Model`,
`Parameter`, `Flow`, `Scenario`, `SimulationRun` and `ValidationRecord`.
The long-term capabilities in [ROADMAP.md](ROADMAP.md) can ultimately
use those concepts. As with the rest of
this section, none of them is introduced as code until a task needs it,
and a second real use justifies the abstraction.
