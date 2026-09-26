# Poltika v0.3 Build Plan: tax, benefits and the household graph

**Date:** 26 September 2026
**Status:** Approved 26 September 2026 with ADR-0015 (accepted). Scope
is Tier 1 of the policy kernel coverage map (`ROADMAP_REALIGNMENT.md` W10,
decided 26 September 2026): personal income tax, Jobseeker Support, Sole
Parent Support and Supported Living Payment. Phase 0 sets each one's
supported slice from sources.
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
v0.3 starts the **deterministic policy kernel**: one engine that turns a
household's state into its fiscal position under a policy configuration,

`household state → policy dependency graph → household fiscal position`

rather than a set of separate calculators. A scenario then compares the
same households under two configurations, which gives the change in
disposable income, and with weights the change in Crown cost
(`ROADMAP_REALIGNMENT.md` W10).

The target calculation shape is roughly:

`gross earnings → income tax → main benefits → WFF → AS → (Tier 2: childcare and supplementary assistance) → disposable income`

The actual order is whatever the source-derived edges (Phase 0.3) make
it. That shape is the aim, not an assumed rule. v0.3 delivers:

1. **Personal income tax** on the income types the v0.2 household types
   have.
2. **The three core main benefits**: Jobseeker Support, Sole Parent
   Support and Supported Living Payment (Tier 1).
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
- the Tier 2 and Tier 3 domains of the coverage map (Temporary
  Additional Support, Disability Allowance, childcare subsidies, NZ
  Super, Paid Parental Leave, student support and the rest). Tier 2 ships
  as v0.3.x coverage releases alongside v0.4.

## Phases

### Phase 0: scoping (before any implementation)

- **0.1 — GPT/Codex. Source-scope income tax.** Define the smallest
  supported slice: which income types, which tax year, which
  withholding or annual-assessment basis, and what is out of scope,
  each with primary sources. Record a v0.1-style source pack in
  `policy_specs/income_tax/sources.yaml`.
- **0.2 — GPT/Codex. Source-scope the three core main benefits**
  (Jobseeker Support, Sole Parent Support, Supported Living Payment). For
  each, record its eligibility gates, rate categories, partner and family
  treatment, and income abatement, with a v0.1-style source pack. Set the
  implementation order (proposed: Jobseeker Support, Sole Parent Support,
  Supported Living Payment), unless the sources show a dependency that
  changes it.
- **0.3 — GPT/Codex, Pete deciding. Record every interaction the
  specifications state:**
  - what counts as income for each income test;
  - what is taxable;
  - what each policy excludes.

  Each gets a decision record where the law is ambiguous. These become
  the graph's edges (Phase 4). Restate in the same form the ones the
  specifications already record:
  - WFF-08: a main benefit with family tax credit and Best Start, but
    normally not the in-work or minimum family tax credits;
  - the WFF "Earner and benefits" row;
  - WFF MB 1-2's allocation of main-benefit income into family scheme
    income;
  - AS's claimant-category thresholds by benefit ("Claimant rate class");
  - AS-10 and WFF DEC-003.

  Then add each new one from sources, including which government
  payments enter which income test, and whether and how each main benefit
  is taxed.
- **0.4 — Pete. Confirm each domain's supported slice (D1)**, and the disposable-income
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

Follow the `new-policy` skill's five PRs: sources and specification,
values and expected results, implementation, interactions, release. One
vertical slice:

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

### Phase 3: the three core main benefits (v0.1 method)

The same slice for each benefit in Phase 0.2's order, each as the
`new-policy` skill's five PRs, pipelined (W2.4). GPT/Codex specifies the next
benefit while Claude Code implements the current one. Each benefit's
golden households cover single, couple and sole-parent cases, and at
least one where the benefit's result changes another policy's input.

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
- **4.6 — Claude Code. Calculated, not asserted.** Facts that WFF and AS
  take today as asserted inputs, and that a Tier 1 domain now calculates,
  come from the graph instead:
  - the AS claimant category (which benefit, or non-beneficiary);
  - WFF benefit-status and earner facts, as far as the specifications
    define them.

  An asserted value that contradicts the calculated one is a
  `needs_review` contradiction, as in Task 28.3, never silently
  overridden.

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

- **Income tax and all three core main benefits** are specified,
  implemented, independently reviewed and benchmarked to v0.1's
  standard.
- **The kernel household** is a golden household built from the
  realignment example:
  - a couple aged 32 and 30;
  - children aged 1 and 4;
  - earnings of $48,000 and $15,000;
  - rent of $650 a week;
  - a verified AS statistical area unit (the AS spec forbids inferring
    an area from a city name such as "Auckland");
  - childcare of 25 hours a week;
  - cash assets of $5,000.

  It runs through the kernel to a disposable-income result. Every
  modelled component is calculated or explained, and components outside
  Tier 1 (childcare assistance) are `unsupported` with a named reason,
  never zero. GPT/Codex hand-calculates its expected values
  independently.
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

- **D1:** Each Tier 1 domain's supported slice, from Phase 0's sourcing.
- **D2:** The disposable-income definition (0.4).
- **D3:** The income-adequacy measures to report (5.3).
- **D4 (decided 26 September 2026):** v0.3 ships with all three core
  main benefits (W10 Tier 1). Tier 2 domains follow as v0.3.x coverage
  releases.
