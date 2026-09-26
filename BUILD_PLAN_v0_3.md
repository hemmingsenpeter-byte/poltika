# Poltika v0.3 Build Plan: tax, benefits and the household graph

**Date:** 26 September 2026
**Status:** DRAFT. It depends on ADR-0015 (proposed) and on decision D2
in `ROADMAP_REALIGNMENT.md`, which scopes the new policies from sources.
**Starts:** after v0.2 ships and W1's review queue is below its cap.
Phase 0 can start as soon as ADR-0015 is accepted.

`BUILD_PLAN.md`'s doctrines apply unchanged: primary sources only, the
three test classes, protected values changed only through the test
doctrine, ambiguity escalated, and no external implementation as a source
of policy logic. Every statutory rule, rate, threshold and interaction
below is established by a phase's sourcing task. This plan names none of
them.

## What v0.3 delivers

v0.2 runs two policies that don't feed each other (AS-10, WFF DEC-003).
v0.3 adds the policies almost every later capability needs, and the
machinery for policies that do feed each other:

1. **Income tax** on the income types the v0.2 household types have.
2. **The main benefits** needed for disposable income, scoped in Phase 0
   (D2).
3. **One household model** that every policy reads, replacing per-policy
   input types.
4. **A household-level dependency graph** whose edges come only from the
   specifications, so one policy's output feeds another's input in a
   stated, explained order.
5. **Disposable income** for supported households, and with it the
   measures v0.2 couldn't offer (R3): effective marginal tax rates, and
   income-adequacy measures on a sourced definition.
6. **The real-data pipeline.** Poltika runs inside a secure environment
   and exports only checked aggregates (W3), ready for access when it's
   granted.

**Not in v0.3:**

- multi-year scenarios (v0.4);
- uncertainty or Monte Carlo (v0.5);
- the historical fiscal baseline (v0.5, per ADR-0015);
- GST, company tax or other revenue (the v0.6 long-term model);
- behavioural responses;
- any policy beyond Phase 0's scope.

## Phases

### Phase 0: scoping (before any implementation)

- **0.1 — GPT/Codex. Source-scope income tax.** Define the smallest
  supported slice: which income types, which tax year, which
  withholding or annual-assessment basis, and what is out of scope,
  each with primary sources. Record a v0.1-style source pack in
  `policy_specs/income_tax/sources.yaml`.
- **0.2 — GPT/Codex. Source-scope the main benefits.** Which benefits are
  needed to compute disposable income for v0.2's household types, and for
  each its eligibility gates, rates and abatement. Rank them by coverage,
  so v0.3 can ship with the first and add the rest.
- **0.3 — GPT/Codex, Pete deciding. Record every interaction the
  specifications state:**
  - what counts as income for each income test;
  - what is taxable;
  - what each policy excludes.

  Each gets a decision record where the law is ambiguous. These become
  the graph's edges (Phase 4). The existing ones (AS-10, WFF DEC-003) are
  restated in the same form.
- **0.4 — Pete. Decide the scope (D2)**, and the disposable-income
  definition used for measures. It must be a sourced definition (for
  example an official statistical one), recorded as a decision, not
  assumed.
- **0.5 — Claude Code.** Apply the onboarding skill (W2.2) to plan each
  policy's tasks, with the W2.1 cost baseline as the estimate.

### Phase 1: shared household model (W6)

- **1.1 — Claude Code. Canonical household model** in `semantics/`:
  persons, family and household, holding each fact once (partner status,
  children and their ages, income by type, housing costs, benefit
  receipt). It extends v0.2's population schema, and population records
  read it directly.
- **1.2 — Claude Code, reviewed by GPT/Codex. Per-policy mappings.** Each
  policy's input is derived from the household model by a named mapping
  function. The mapping for WFF and AS reproduces today's `WffScenario`
  and `AsScenario` exactly.
- **1.3 — Claude Code. Byte-identical proof.** Every golden household,
  spec case and golden snapshot runs through the new path with
  identical results and result ids. The existing request formats stay
  as adapters onto the household model.
- **1.4 — Claude Code.** Retire the Task 28.3 pairwise contradiction
  checks only where the single-fact model makes them impossible. Any
  check that still means something (for example two agencies' different
  definitions of the same concept) is kept and named.

### Phase 2: income tax (v0.1 method)

Follow the W2.2 onboarding skill, one vertical slice:

- sources (0.1);
- specification with rule ids;
- `policy.yaml` with dated, approved values;
- spec cases hand-calculated by GPT/Codex;
- benchmarks from official worked examples;
- golden households;
- evidence and currency coverage;
- calculation steps and explanation templates;
- review;
- release-gate rows.

### Phase 3: main benefits (v0.1 method)

The same slice for the first benefit in Phase 0's ranking, then each
further benefit in scope, one bounded PR sequence per benefit.

### Phase 4: household dependency graph (W7)

- **4.1 — Claude Code.** A graph of policy calculations per household.
  Each edge is one Phase 0.3 interaction, citing its decision record or
  rule id. There are no edges without a source.
- **4.2 — Claude Code.** Order the graph topologically. A cycle is refused
  (`unsupported`, with the cycle named) unless a specification defines
  how the law resolves it, in which case that resolution is implemented
  and tested as its own rule.
- **4.3 — Claude Code.** Carry outcomes along edges. A `needs_review` or
  `unsupported` input makes every dependent result the same, with the
  chain named in its reason. It is never zero.
- **4.4 — Claude Code.** Explain dependency chains: "this benefit fell by
  X because taxable income rose by Y (rule …), which …". Explanations are
  tested against the calculation, as in v0.1.5.
- **4.5 — Claude Code.** The combined runner becomes the graph runner.
  WFF and AS, which have no edge between them, keep byte-identical
  results.

### Phase 5: disposable income and measures

- **5.1 — Claude Code.** Disposable income per household on the Phase
  0.4 definition, with its components listed and its coverage reported.
- **5.2 — Claude Code.** Effective marginal tax rates along an income
  path, now across tax and transfers. This replaces v0.2's per-policy
  withdrawal rates where every component is modelled, and resolves v0.2
  D9 through the household model's single income.
- **5.3 — GPT/Codex, Pete deciding.** Which income-adequacy measures to
  report, each on a sourced official definition, as decision records.
  None is invented.
- **5.4 — Claude Code.** Add those measures to the population analysis
  and explanations, with coverage.

### Phase 6: real-data pipeline (W3.3-W3.5)

- **6.1** Secure-environment runner: no network, no repository writes,
  configured population path, aggregate-only export.
- **6.2** Output checks from W3.1's published rules.
- **6.3** Survey adapter onto the household model, with GPT/Codex review.
- **6.4** A synthetic population extended to the new policies' facts.
  Every result keeps the synthetic label until real data runs.

### Phase 7: release

- **7.1** Release-gate test, including W1's review-queue row.
- **7.2** CHANGELOG, `docs/releases/` limitations, the maintenance line
  per policy (W5.4), and throughput actuals (W2.5).
- **7.3** Pete tags `v0.3.0`.

## Sequence

| Sprint | Work |
| --- | --- |
| 0 | Phase 0 (sourcing and decisions); W4.2 prototype in parallel |
| 1 | Phase 1; Phase 2 sources and specification |
| 2 | Phase 2 implementation; Phase 3 sources and specification (pipelined, W2.4) |
| 3 | Phase 3 implementation; Phase 4 |
| 4 | Phase 5; Phase 6 |
| 5 | Phase 7 |

## Exit gate

- **Income tax and at least the first main benefit** are specified,
  implemented, independently reviewed and benchmarked to v0.1's
  standard.
- **Every golden household** runs through the shared household model and
  the dependency graph. WFF and AS results are byte-identical to v0.2.
- **One policy's output feeds another's input.** For a household where
  that happens, the chain is calculated in source-derived order and
  explained, and the explanation is verified against the calculation.
- **Disposable income and effective marginal tax rates** are produced for
  supported households, with coverage reported. `needs_review` is never
  counted as zero.
- **A population run** reports disposable-income changes by decile and
  household type for a reform, labelled synthetic until real data runs.
- **The secure-environment runner** exports only checked aggregates, and a
  test proves no household-level record can leave.
- **No release-scope PR** is left without independent review (W1).

## Open decisions for Pete

- **D1:** The Phase 0 scope (from `ROADMAP_REALIGNMENT.md` D2).
- **D2:** The disposable-income definition (0.4).
- **D3:** The income-adequacy measures to report (5.3).
- **D4:** Whether v0.3 ships with one main benefit or waits for all of
  Phase 0's ranked list. Recommended: ship with the first, and add the
  rest as v0.3.x releases, so each one is a bounded, reviewed slice.
