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
├── pyproject.toml      — dependencies (Pydantic, PyYAML) and dev tooling (pytest, Ruff, mypy strict)
├── uv.lock
│
├── doctrine/          — process/workflow rules, one file per BUILD_PLAN frozen doctrine section, plus narrow architectural guardrails
├── adr/               — architecture decisions with rationale and context
├── policy_specs/      — per-policy source packs, specification maps, benchmarks, decisions
├── review_packets/     — assembled review packet template/instances
├── reviews/           — review and discrepancy records
│
├── src/poltika/
│   ├── common/            — errors.py (exception hierarchy)
│   ├── semantics/schemas/ — policy_spec.py (Pydantic models mirroring policy.yaml)
│   ├── policy/            — loader.py (Task 11 parameter loader)
│   └── engines/simulator/ — wff.py (Task 12 calculate_wff())
│
└── tests/
    ├── conftest.py        — shared fixtures/helpers (Task 15), used by tests/regression/
    ├── unit/
    │   ├── policy/         — loader tests (Task 11)
    │   └── engines/simulator/ — calculator unit tests (Task 12), spec-case and
    │                            benchmark-case loader/runners (Tasks 13-14)
    └── regression/         — known-historical-issue tests (Task 15)
```

Only `src/poltika/{data,scenarios,llm}` and `tests/{integration,fixtures}`,
plus everything under `data/`, `config/`, `docs/`, and `scripts/`, remain
undone from the target tree below — created incrementally as the
BUILD_PLAN.md tasks that need them are reached, not all at once.
`src/poltika/engines/{assurance,discovery,hypothesis}` are correctly still
empty placeholders; see below.

## Target architecture (create on demand, per task)

```text
poltika/
│
├── docs/
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
| `src/poltika/llm/` | `scenarios/` (to build/read a `ScenarioRequest`) | `engines/simulator/` internals, raw/processed data |

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
