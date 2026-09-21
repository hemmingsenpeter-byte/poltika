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

## Technology stack (settled)

| Layer | Stack |
| --- | --- |
| Core language | Python |
| API/backend | FastAPI |
| Schemas / validation | Pydantic |
| v0.1 frontend | Streamlit |
| Later frontend | Next.js + TypeScript |
| Primary database | PostgreSQL |
| Data transformation | dbt |
| Analytical/scratch data | Parquet, with DuckDB as an internal scratch/query tool |
| Policy parameters | Versioned YAML |
| Simulation | Deterministic Python domain engines behind a common `DomainEngine` interface |
| AI layer | Claude or GPT structured-output/tool-use → validated `ScenarioRequest` |
| Testing | pytest + formula/unit tests + golden/calibration tests + integration tests |
| Lint/type checking | Ruff + mypy |
| Containers | Docker / Docker Compose |
| CI/CD | GitHub Actions |
| Source control | Git + GitHub |
| Dependency locking | `uv.lock` or `poetry.lock` |
| Repo structure | Monorepo |

**v0.1 scope is deliberately lean:** Python + FastAPI + Pydantic + Streamlit + YAML policy specs + pytest/Ruff/mypy. PostgreSQL, dbt, and Docker infrastructure are brought in only where needed, rather than building a large platform prematurely.

**Not yet frozen:** production cloud provider, observability stack, queue system, and final authentication architecture. Multi-tenant auth in particular is deferred beyond the initial demo.

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
Streamlit
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
