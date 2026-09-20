---
name: poltika-skill-roadmap
description: Use when deciding whether a Poltika-specific skill already exists for the task at hand, whether a new one should be built before proceeding, or when starting a BUILD_PLAN.md task and checking what governs it. Also use when asked what skills this project has, needs, or should build next.
---

# Poltika skill roadmap

This is the map of Poltika-specific skills: which exist, which are planned,
what each one governs, and roughly when to build the ones that don't exist
yet. Keep this file updated whenever a skill in this list is built, skipped,
or its scope changes — it's the thing a fresh session should read to avoid
either re-deriving a skill that already exists, or building one for a task
that isn't reached yet.

Do not build a skill speculatively just because it's listed here as
"planned" — build it when the task column's BUILD_PLAN item is actually
about to start, per the reactive-build approach this list follows.

| Skill | Status | Governs | Build when |
| --- | --- | --- | --- |
| `clean-room-research` | Built | How to inspect external policy engines (OpenFisca Aotearoa, PolicyEngine NZ, BetterRules, etc.) without letting them become a source of Poltika policy logic — the IP Doctrine's external-research rule, operationalised. | Built ahead of Task 3/16 external-inspection work. |
| `provenance` | Built | Provenance requirements for policy sources (`sources.yaml`) and external statistical datasets (raw-snapshot manifests, the 11-field list from the Data Acquisition Doctrine). | Built ahead of Task 4/10a/10b/22a dataset and schema work. |
| `policy-rule-implementation` | Not built | The pipeline a NZ policy rule must follow when it's actually implemented (primary source → provenance record → parameter → deterministic rule → unit test → historical validation → Assurance) and what's explicitly prohibited (inventing a formula, copying OpenFisca/PolicyEngine logic, treating a blog as an authoritative parameter). | Build right before Task 11/12 (WFF parameter loader + `calculate_wff()`) starts. |
| `deterministic-simulation` | Not built | Rules for `src/poltika/engines/simulator/`: pure functions, no I/O, no source-specific formats, the `DomainEngine` interface shape, the "LLM never calculates" boundary from `doctrine/llm_boundaries.md` at the simulator's edge. | Build alongside or just after `policy-rule-implementation`, once Task 12/20 (simulator integration) is close. |
| `canonical-data-model` | Not built | Conventions for `src/poltika/semantics/`: what makes a variable "canonical," how entities (person vs. assessment unit — see the G1 gap in `docs/research/nz_policy_engines_review.md`) and periods are represented, independent of any source format. | Build when Task 4's schema work starts turning into actual `semantics/` code — likely early Weeks 1-2. |
| `assurance` | Not built | Regression-fixture registration, change attribution (source data vs. transformation vs. parameter vs. policy-rule vs. code), and the provenance report shape — `src/poltika/engines/assurance/`. | Build when Task 15 (regression tests) or Task 31 (full calculation provenance report) is close. |
| `poltika-architecture` | Skipped (for now) | Would restate BUILD_PLAN.md/ARCHITECTURE.md/REPOSITORY_STRUCTURE.md orientation. | Only build if CLAUDE.md's existing "read these files first" instruction turns out to be insufficient in practice — no evidence of that yet. |
| `nz-legislation` | Skipped (for now) | Would cover NZ legislation.govt.nz citation/effective-dating conventions. | Primary-source gathering is GPT's role per BUILD_PLAN.md's Roles section, not something run from a Claude Code session — reconsider only if that division changes. |

## Official (non-Poltika) plugins — same reactive principle

Not tracked row-by-row here since they're Anthropic-maintained, not
project-authored, but the same timing logic applies:

- Low-risk to install now: `commit-commands`, `security-guidance`.
- Hold until `src/` actually has Python in it: `pyright-lsp`, `code-review`,
  `pr-review-toolkit`, `code-simplifier` — nothing for them to check yet.

## If you're not sure a skill is needed at all

Prefer no skill over a speculative one. A skill earns its place when it
prevents a mistake that's actually about to become possible (there's code or
data for it to govern), not because the capability is philosophically
relevant to Poltika's architecture.
