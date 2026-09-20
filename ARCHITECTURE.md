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
