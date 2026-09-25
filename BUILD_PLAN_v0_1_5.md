# Poltika v0.1.5 Build Plan: the evidence and explainability bridge

**Date:** 25 September 2026
**Status:** APPROVED 25 September 2026 under Pete's delegation ("approve
each step yourself and keep going"); decisions D1-D4 are recorded at the
end. It is built on the GPT proposal Pete relayed on 25 September 2026,
reconciled with the repository as it stands at `v0.1.0`. `BUILD_PLAN.md`
stays the frozen record of v0.1, and its doctrines still apply here:
primary sources only, the three test classes, the review taxonomy, and the
IP boundary.

**Timebox:** 6-8 weeks from `v0.1.0`.

**Target:** one real pilot user can interrogate a household calculation
without the builders present.

## The release boundary

- v0.1 proves Poltika calculates policy correctly.
- **v0.1.5 proves Poltika can show its work:** where each number came from,
  how it was calculated, what was assumed, and what is missing.
- v0.2 starts population and fiscal scale.

v0.1.5 adds no new policies, no statistical data, no economic simulation,
no Discovery or Hypothesis engines, no LLM-generated numbers, and no full
Policy Interaction Graph.

## What v0.1 already provides

Each task below is marked **exists** (keep and verify), **extend**, or
**new**. The v0.1 starting points:

| Proposal element | Already in v0.1 | Gap left for v0.1.5 |
| --- | --- | --- |
| Evidence sources | `policy_specs/*/sources.yaml`: kind, URL, covered provisions, dated structured checks | No authority rank; no per-source validity period; no coverage report |
| Evidence on parameters | Each value carries `source_id`, `locator`, effective interval and `review_status`; unresolved ids fail the load | None |
| Stable rule ids | WFF-01…09 and AS-01…11 in each `specification.md`, resolved by the provenance report | Ids are per specification row, not per formula step |
| Calculation trace | `ComponentTrace`: parameters and facts consulted, upstream components, rounding rules, decisions, file hashes | No intermediate values (gross credit, abatement, capped amount), no ordered steps |
| Machine-readable explanation | Provenance report as JSON and Markdown, rendered from one dictionary | No plain-language narrative |
| Needs review | Tri-state outcome, never a false zero; the reason is free text | No reason code, missing-fact list or blocking flag |
| Explanation consistency | `test_explanation_values_are_the_recorded_calculation_values` | Only covers surfaced values |
| Invariants and boundaries | Hypothesis properties; ±1 boundary tests at thresholds and the asset ceiling | Mutation tests on trace and explanation |
| Reproducibility | Scenario and result ids, hash-bound artifacts, stored replay, code replay in CI | None |
| Golden cases | 9 golden households and a frozen golden-results snapshot | No golden traces or explanations |

## Adjustments to the proposal

These are needed to fit the doctrines, and each is flagged for Pete:

1. **Evidence registry.** Extend `sources.yaml` (governed by the
   `provenance` skill); don't add a parallel `evidence/registry.yaml`. Two
   catalogues of the same sources would drift apart.
2. **Benchmarks stay where they are.** They remain in
   `policy_specs/*/benchmarks.yaml`, which is protected and watched by the
   guard. Add any missing fields there; moving them would change every
   provenance hash for no gain.
3. **"Assumed" inputs.** An assumption may only be declared by the caller
   and must be recorded. The engine never invents one, and an unknown fact
   is never defaulted (SCHEMA.md). The assumption ledger records what the
   caller asserted.
4. **Analyst UI stack.** ARCHITECTURE.md replaced Streamlit with Next.js on
   22 September 2026. A thin page served by FastAPI (plain HTML over the
   existing JSON) avoids a second stack for a pilot. Pete decides (D2).
5. **Baseline numbers are measured, not assumed.** Today: 429 tests plus
   the installed-artifact and code-replay tests. Coverage is not measured
   yet (Task 0.4 adds it).
6. **Out-of-domain fixtures.** Shared-care, age-transition and other v0.1
   out-of-domain fixtures test for their `unsupported` or `needs_review`
   outcome, not a new calculation.
7. **Claims about legislation are checked before they are used.** The
   proposal says further Accommodation Supplement legislation was enacted
   in September 2026. Poltika's last recorded check of the Act is the
   4 September 2026 version. Task 0.5 verifies this from the primary source
   before anything relies on it (CLAUDE.md: model memory is never
   authority).

## Phase 0 — Baseline

- **0.1 — Pete. Tag `v0.1.0`** on `e41871d`. The session could not push
  tags, so this is done in the GitHub web interface.
- **0.2 — Claude Code. Complete benchmark metadata** (extend). Make sure
  every protected benchmark and spec case states its reference period,
  source, assumptions and reviewer. Missing fields are added in place, as
  above.
- **0.3 — Claude Code. `docs/releases/V0_1_LIMITATIONS.md`** (new). One page
  of what v0.1 doesn't calculate, collected from the specifications'
  unsupported lists, the demo limitations and the README. Every item links
  to its source rule or decision.
- **0.4 — Claude Code. Measured baseline** (new). Add `pytest-cov` and
  record test counts, benchmark count, coverage and the policy-file hashes
  in `docs/releases/V0_1_BASELINE.md`. v0.1.5 must reproduce every v0.1
  result unless a reviewed statutory correction changes it.
- **0.5 — GPT/Codex. Legislation currency check** (new). Re-check the
  Social Security Act and Regulations and the Income Tax Act for
  amendments since the recorded checks, including the September 2026
  Accommodation Supplement claim. Record the results in `sources.yaml`.
- **0.6 — GPT/Codex. In-work tax credit base re-check** (extend Task 26b).
  Check the Order in Council record. If $7,670 is confirmed for the whole
  of 2026-27, propose the `review_status` change through the test-doctrine
  process, and WFF totals become possible.

## Phase 1 — Evidence model

- **1.1 — Claude Code. Source model** (extend). Add `source_type` and an
  authority rank to `sources.yaml` entries, validated by a Pydantic model:
  1. legislation;
  2. regulation or order;
  3. official operational material;
  4. official guidance;
  5. Cabinet or policy document;
  6. secondary;
  7. Poltika assumption.

  Add an optional validity period per source version. Guidance never
  outranks statute.
- **1.2 — GPT/Codex. Classify every existing source.** One review pass.
- **1.3 — Claude Code. Evidence on rules** (extend). Each specification
  rule id already cites sources; make that machine-checked: every rule's
  cited `source_id`s must resolve.
- **1.4 — Claude Code. Evidence coverage report and CI check** (new).
  Every protected value and every rule used on a calculated path has
  evidence of the required rank. CI prints coverage per policy and fails
  if any is missing.

## Phase 2 — Calculation trace

- **2.1 — Claude Code. `CalculationStep`** (extend `ComponentTrace`). An
  ordered list of steps, each with a step id, rule id, operation, inputs,
  result and evidence ids.
- **2.2 — Claude Code. Step recording as instrumentation** (extend), like
  Task 31's recording copies. The arithmetic is not restructured, and a
  test confirms results are unchanged.
- **2.3 — Claude Code with GPT/Codex. Stable step ids.** For example
  `WFF_FTC_ABATEMENT` and `AS_AREA_CAP`, each mapped to a specification
  rule id. GPT/Codex reviews the mapping.
- **2.4 — Claude Code. Intermediate values** (new). Gross credit, complete-
  dollar excess, abatement and remainder; AS qualifying costs, excess,
  70% amount, cap, imputed income and reduction.
- **2.5 — Claude Code. Step dependencies** (extend
  `upstream_components`). A per-result dependency list only; the graph
  engine is v0.3.

## Phase 3 — Deterministic explanations

- **3.1 — Claude Code. `Explanation` model** (new): outcome, summary,
  steps, evidence, assumptions and review reasons.
- **3.2 — Claude Code. Template renderer** (new). Every number and rule in
  the text comes from the trace. No LLM.
- **3.3 — Claude Code. Rule-level explanations** (new): what happened,
  why, inputs, result and authority, for each step.
- **3.4 — Claude Code. Citations** (extend the provenance report): result →
  step → rule → provision → source and version.
- **3.5 — Claude Code. JSON explanation in the API** (extend): add it to
  `/household/calculate` and to stored scenarios.

## Phase 4 — Facts, assumptions and review reasons

- **4.1 — Claude Code. Fact provenance** (extend). Keep `FactStatus` and
  add the fact's origin: caller-verified, caller-assumed, or derived. An
  assumed fact is allowed only where the specification says so, and it
  must be recorded (adjustment 3).
- **4.2 — Claude Code. `NeedsReviewReason`** (new): a code, message,
  blocking flag, affected rules and missing facts, in place of free-text
  reasons. Existing reason text stays as the message.
- **4.3 — Claude Code with GPT/Codex. Hard and soft uncertainty** (new).
  A hard blocker withholds the value, as today. A soft uncertainty lets
  the calculation run with a recorded caveat, but only where the
  specification permits it. GPT/Codex reviews each soft case.
- **4.4 — Claude Code. Needs-review explanation** (new): reason, affected
  calculation, required information, and "no value produced".
- **4.5 — Claude Code. Assumption ledger** (new). Every result lists the
  caller's assumptions, numbered.
- **4.6 — Pete. Machine-readable reason category** inside `unsupported`:
  "not modelled" versus "evidenced exclusion" (DEC-001 option c) (D4).

## Phase 5 — Explanation verification

- **5.1 — Claude Code. Consistency** (extend the existing test): every
  number in every explanation equals its trace value.
- **5.2 — Claude Code. Trace completeness** (new): every explanation claim
  maps to an input, a step, rule metadata or evidence.
- **5.3 — Claude Code. Citation validity** (extend): the source exists, the
  provision is named, and it applies to the period.
- **5.4 — Claude Code. Temporal evidence** (new): no citation to a source
  version outside the modelled date's validity, using the 1.1 validity
  periods.
- **5.5 — Claude Code. Mutation tests** (new): change rate, threshold,
  income, children, area, rent and partner status, and check that the
  result, trace and explanation change consistently.

## Phase 6 — Thin analyst interface

The stack is Pete's choice (D2); functional, not polished.

- **6.1 — Household input form.**
- **6.2 — Results page.** WFF components and total when every component
  is calculated; AS weekly; status per component.
- **6.3 — "Why this number?" panel.** Steps, inputs, intermediate values,
  rules, evidence and assumptions: the signature feature.
- **6.4 — Source panel.** Provision, validity period, check date and link.
- **6.5 — Distinct status display.** `calculated`, `needs_review` and
  `unsupported` must be impossible to confuse.
- **6.6 — Case report export** as JSON and HTML, from the same dictionary.

## Phase 7 — Hardening

- **7.1 — Claude Code. 100+ explanation fixtures** from the 140 existing
  questions. Out-of-domain categories are fixtured for their outcome
  (adjustment 6).
- **7.2 — Claude Code. Golden traces** for the golden households: result,
  steps, assumptions, evidence ids and reason codes. Test the structure,
  not the prose.
- **7.3 — Claude Code. More property tests** (extend the Hypothesis suite):
  - no negative credit;
  - AS never above its cap;
  - more income never raises an income-tested amount;
  - no missing fact becomes zero;
  - irrelevant inputs change nothing.
- **7.4 — Claude Code. Evidence attacks.** Delete, expire or mismatch a
  source, or strip a parameter's evidence, and CI fails.
- **7.5 — Claude Code. Explanation attack.** Engine $200 against an
  explanation saying $201 fails.
- **7.6 — Claude Code. Reproducibility** (exists; extend to cover traces
  and explanations).

## Phase 8 — Pilot and release

- **8.1 — Claude Code. Pilot deployment:** a container image and compose
  file for the API, PostgreSQL and the UI, with migrations and
  `policy_specs/` mounted (ADR-0011).
- **8.2 — Pete. Name one external pilot** with public-policy or tax and
  welfare background.
- **8.3 — Pete. Pilot session:** 10-20 cases, minimal briefing, and a
  challenge to explain one answer (Do you believe it? Where did it come
  from? Which rule? What was assumed? What is missing?).
- **8.4 — Claude Code. `docs/pilot/V0_1_5_PILOT_FINDINGS.md`**, classified:
  P0 wrong answer, P1 misleading explanation, P2 missing evidence, P3
  confusing UX, P4 cosmetic.
- **8.5 — Owner by slice. Fix every P0 and P1**; P2-P4 go to the backlog.
- **8.6 — Claude Code. Release** `v0.1.5`: CHANGELOG, then Pete tags.

## Housekeeping (alongside, not gating)

- **H.1 — Claude Code. Review-record clean-up** (the deferred "taxonomy
  rework"). Put `review_packets/`, `reviews/` and `docs/research/` into
  one structure in `REPOSITORY_STRUCTURE.md`, moved with `git mv`.
- **H.2 — Claude Code. Write the working agreement** into
  `doctrine/development-doctrine.md`:
  - every change reaches `main` through a PR, never a direct push;
  - a PR merges only with CI green and its review recorded;
  - releases are tagged on merge commits.

## Release gate

v0.1.5 ships only when all of these hold:

| Gate | Requirement |
| --- | --- |
| v0.1 results | Every golden, benchmark and spec result unchanged, unless a reviewed statutory correction changes it |
| Protected values | 100% sourced, at the required authority rank |
| Calculated-path rules | 100% evidence-linked |
| Explanation vs result | 100% consistent (tested) |
| Temporal evidence | Passing |
| Missing inputs | Never defaulted |
| Needs review | Structured and explained |
| Trace | Steps available for every calculated result |
| Assumptions | Every assumption surfaced |
| Reproducibility | Result, trace and explanation all reproduce |
| Pilot | At least one external user |
| P0 and P1 defects | None open |

## Suggested order

| Week | Work |
| --- | --- |
| 1 | Phase 0 and Phase 1 |
| 2 | Phase 2 |
| 3 | Phase 3 |
| 4 | Phase 4 |
| 5 | Phase 5 |
| 6 | Phase 6 |
| 7 | Phase 7 |
| 8 | Phase 8 |

Housekeeping runs alongside.

## Decisions (25 September 2026, delegated by Pete)

- **D1: approved,** including adjustments 1-7.
- **D2: a thin page served by FastAPI** for the pilot. No second front-end
  stack in v0.1.5; Next.js stays the long-term target.
- **D3: agreement only,** until the repository is public or on a paid plan.
- **D4: yes.** `unsupported` results carry a machine-readable category:
  `not_modelled` or `evidenced_exclusion` (Task 4.6).
