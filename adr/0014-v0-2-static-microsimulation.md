# ADR-0014: v0.2 becomes static population microsimulation

**Date:** 26 September 2026
**Status:** accepted. Pete accepted it on 26 September 2026
(`BUILD_PLAN_v0_2.md` D1). Drafted by Claude Code from Pete's pasted v0.2
specification.

## Context

ADR-0008 fixed the sequence: v0.2 data foundation, v0.3 policy interaction
graph, v0.4 scenario engine. It argued that no scenario comparison is
possible "without real data and a dependency graph to propagate a parameter
change through first". It also said a later reordering is allowed, but only
as a new decision against that reasoning.

Pete's v0.2 specification makes v0.2 a static microsimulation: WFF and
Accommodation Supplement reforms run across a weighted population, with
fiscal, distributional and household-type results. That pulls part of
v0.4 forward, ahead of v0.3.

Checked against ADR-0008's reasoning:

- **The graph is not a prerequisite for these two policies.** AS-10 and
  WFF DEC-003 exclude WFF tax credits from Accommodation Supplement
  chargeable income, and IRD excludes the Accommodation Supplement from WFF
  family income. With no feedback between them, the Task 28 combined runner
  already calculates both, and a reform only needs the same runner called
  twice. A graph is needed once modelled policies feed each other (income
  tax, benefits, wages). That is still v0.3.
- **Data still comes first, but only the part the population needs.** A
  population and its calibration tables are datasets, so the data layer
  (manifests, registry, canonical variables) stays at the start of v0.2.
  The historical macro baseline (revenue, debt, GDP) serves none of v0.2's
  questions.

## Decision

If accepted:

1. v0.2 is *static population microsimulation* for WFF and the
   Accommodation Supplement, as `BUILD_PLAN_v0_2.md` sets out. It is built
   on a data-layer phase and a synthetic development population.
2. The historical fiscal and macro baseline moves from v0.2 to v0.3, beside
   the policy interaction graph.
3. v0.4's scenario engine keeps what v0.2 does not deliver: multi-year
   trajectories, phased and indexed policies, new or removed policies,
   multi-policy packages and macro result schemas.
4. v0.4 onwards are otherwise unchanged. The proposal's further reordering
   (behaviour at v0.4, the graph at v0.6) is not adopted here. It needs its
   own decision and dependency reasoning.

## Consequences

- `BUILD_PLAN.md`'s Roadmap Doctrine sequence, its "why this order"
  paragraph and its connector pin are updated to match, as ADR-0008's were.
  So are `ROADMAP.md`'s v0.2-v0.4 sections.
- The Stats NZ and Treasury connectors move to v0.3 with the baseline.
- Scenario results arrive before real data. Every v0.2 output must carry the
  synthetic-population label, and no v0.2 figure may be presented as a New
  Zealand estimate.
- The reordering holds only while modelled policies don't feed each other's
  income tests. The first policy that does (income tax is the obvious one)
  needs the v0.3 graph before it joins the microsimulation.
