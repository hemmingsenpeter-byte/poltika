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
| `new-policy` | Built (26 September 2026) | Onboarding a policy domain into the kernel: the standard five-PR structure (sources and specification, values and expected results, implementation, interactions, release), file set, owners, exit checks, review depth, annual updates and v0.1's lessons. Supersedes the planned `policy-rule-implementation` skill, whose pipeline (source → provenance → parameter → rule → test → validation → Assurance) it contains. | Built for `ROADMAP_REALIGNMENT.md` W2.2 and W2.6, ahead of v0.3 Tier 1. |
| `evidence-classes` | Built (29 September 2026) | Applying the epistemic constitution (`doctrine/epistemic-constitution.md`): which of the eight evidence classes a value belongs to, the eleven fields every number carries, the precision rule, and the AI-hypothesis gate. | Built with `BUILD_PLAN_PROGRAMME.md` Step 1.8, alongside the constitution. |
| `prediction-ledger` | Not built | Registering a forecast: target definition, resolution source named in advance, interval not point, naive baselines, model version and data cutoff, append-only, never revised. | Build with `BUILD_PLAN_PROGRAMME.md` Step 6.4, before the first entry is registered. |
| `deterministic-simulation` | Not built | Rules for `src/poltika/engines/simulator/`: pure functions, no I/O, no source-specific formats, the `DomainEngine` interface shape, the "LLM never calculates" boundary from `doctrine/llm_boundaries.md` at the simulator's edge. | Build alongside or just after `policy-rule-implementation`, once Task 12/20 (simulator integration) is close. |
| `canonical-data-model` | Not built | Conventions for `src/poltika/semantics/`: what makes a variable "canonical," how entities (person vs. assessment unit — see the G1 gap in `docs/research/nz_policy_engines_review.md`) and periods are represented, independent of any source format. | Build when Task 4's schema work starts turning into actual `semantics/` code — likely early Weeks 1-2. |
| `assurance` | Not built | Regression-fixture registration, change attribution (source data vs. transformation vs. parameter vs. policy-rule vs. code), and the provenance report shape — `src/poltika/engines/assurance/`. | Build when Task 15 (regression tests) or Task 31 (full calculation provenance report) is close. |
| `poltika-architecture` | Skipped (for now) | Would restate BUILD_PLAN.md/ARCHITECTURE.md/REPOSITORY_STRUCTURE.md orientation. | Only build if CLAUDE.md's existing "read these files first" instruction turns out to be insufficient in practice — no evidence of that yet. |
| `nz-legislation` | Skipped (for now) | Would cover NZ legislation.govt.nz citation/effective-dating conventions. | Primary-source gathering is GPT's role per BUILD_PLAN.md's Roles section, not something run from a Claude Code session — reconsider only if that division changes. |

## Official (non-Poltika) plugins — same reactive principle

Not tracked row-by-row here since they're Anthropic-maintained, not
project-authored, but the same timing logic applies:

- Low-risk to install now: `commit-commands`.
- Hold until there's actual attack surface — `src/` code, `data/` acquisition
  scripts, or credentials/API keys: `pyright-lsp`, `code-review`,
  `pr-review-toolkit`, `code-simplifier`, `security-guidance` — nothing for
  any of them to check yet.
- **`security-review`** is already available in every session as a built-in
  skill, no install needed — it reviews pending changes on the current
  branch. Fine to invoke on demand any time; just hasn't had application
  code to review yet.

## If you're not sure a skill is needed at all

Prefer no skill over a speculative one. A skill earns its place when it
prevents a mistake that's actually about to become possible (there's code or
data for it to govern), not because the capability is philosophically
relevant to Poltika's architecture.
