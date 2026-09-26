# ADR-0015: Realign the roadmap to the v1.0 critical path

**Date:** 26 September 2026
**Status:** accepted. Pete accepted it on 26 September 2026, with the
recommended decisions in `ROADMAP_REALIGNMENT.md`. Drafted by Claude Code
from its whole-roadmap review.
It amends ADR-0014 and, through it, ADR-0008's sequence.

## Context

ADR-0008 fixed a versioned sequence and allowed a later reordering "only as
a new decision against [its] stated dependency reasoning". ADR-0014 used
that to move static microsimulation into v0.2. A review of the whole
roadmap against `BUILD_PLAN.md`'s testable v1.0 definition found the
following.

1. **The v1.0 definition doesn't need Discovery or Hypothesis.** v1.0 is:

   > ingest a structured package of material fiscal and policy changes
   > ... propagate those interventions through an effective-dated policy
   > interaction graph, and produce reproducible multi-year fiscal,
   > distributional and selected economic/social outcome scenarios with
   > explicit assumptions, uncertainty and source-level provenance.

   Nothing in it depends on the Discovery engine (v0.6) or the Hypothesis
   engine (v0.7). Their gate, `Discovery → Hypothesis → evidence →
   validation → human approval → model specification → tests →
   Simulator`, means nothing they produce reaches the simulator without a
   human-approved specification anyway. The v0.8 system model gets its
   relationships from published evidence and stated assumptions, not
   from a discovery engine. As placed, the two releases sit on the path
   to v1.0 without being part of it.

2. **Policy coverage is the critical path, and no release owns it.** The
   v1.0 definition's "supported NZ policy domains", v0.3's
   PAYE/disposable-income slice, any poverty or effective-tax-rate
   measure, and v0.8's revenue model all need income tax and the main
   benefits specified to v0.1's standard. v0.1 needed Tasks 1-35 and
   58 merged PRs (#1-#81) for two policies, and one of them still has a
   `needs_review` component. Today that work is implied inside other
   releases.

3. **The historical fiscal baseline has no consumer until backtesting.**
   ADR-0014 moved it to v0.3. The first release that uses it is v0.5,
   whose backtesting needs "information available at historical dates".

4. **v0.8's long-term model is a different kind of model.** Connecting
   demography, participation, wages, revenue and debt is feasible and
   checkable as transparent accounting, with exogenous, stated
   assumptions, compared with Treasury's published projections. As a
   behavioural or GDP-forecasting model it would need the behavioural
   and macro work that the roadmap itself places after v1.0 (v2, Economic
   Digital Twin).

## Decision

If accepted, the sequence becomes:

| Release | Scope | Was |
| --- | --- | --- |
| v0.1, v0.1.5, v0.1.6, v0.2 | Unchanged | |
| **v0.3** | Income tax and the main benefits, specified and implemented to v0.1's standard; a shared household model; a household-level dependency graph driven by those policies; the real-data pipeline started (`BUILD_PLAN_v0_3.md`) | Fiscal baseline and generic policy interaction graph |
| **v0.4** | Multi-year, multi-policy scenario engine; the batch-engine decision (ADR by v0.4 start) | Unchanged in scope |
| **v0.5** | Uncertainty and assurance, plus the authoritative historical fiscal baseline and connectors its backtesting needs | Uncertainty and assurance |
| **v0.6** | Long-term NZ fiscal model, as transparent accounting with stated assumptions | Was v0.8 |
| **v0.7** | Decision-intelligence product | Was v0.9 |
| **v1.0** | Production Poltika | Unchanged |
| **After v1.0** | Discovery and Hypothesis join the v2 capability track | Were v0.6 and v0.7 |

Why this order holds:

- **v0.3 before v0.4.** Multi-policy scenarios need the policies, and a
  graph that orders real interactions such as taxable income → benefit
  abatement → family scheme income → WFF.
- **v0.4 before v0.5.** Uncertainty is propagated through the scenario
  engine, and the batch-engine decision must precede Monte Carlo at
  population scale.
- **v0.5 before v0.6.** A long-run model needs the assumption register,
  sensitivity and backtesting first. That is the Scope Doctrine's
  "deterministic correctness before probabilistic sophistication"
  applied one level up, as ADR-0008 did.
- **Discovery and Hypothesis after v1.0.** They are exploratory
  capabilities with a human gate. They extend a hardened system rather
  than being part of hardening it.

The Discovery and Hypothesis content of `ROADMAP.md` is kept, not deleted.
It moves under "Beyond v1.0" with the v2 track, and the Simulator
promotion gate still governs anything they produce.

## Consequences

- Done on acceptance:
  - `BUILD_PLAN.md`'s Roadmap Doctrine sequence, "why this order" and
    connector pin are updated;
  - `ROADMAP.md`'s v0.3-v0.9 sections are rewritten into v0.3-v0.7, with
    Discovery and Hypothesis kept under "Beyond v1.0";
  - `BUILD_PLAN_v0_3.md` is the v0.3 plan.
- Release numbering shortens. v1.0 is reached after v0.7, not v0.9, with
  the same v1.0 definition.
- Two risks the roadmap didn't name become tracked work in
  `ROADMAP_REALIGNMENT.md`:
  - real-data access, an organisational process with a long lead time;
  - population-scale compute for Monte Carlo.
- This decision still holds only while its reasoning does. A later
  reorder is a new ADR against this one.
