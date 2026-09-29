# Poltika Roadmap

This is Poltika's master technical roadmap: the release-level direction,
not an implementation backlog. The 33 steps, what already exists against
each, the tasks, gates and decisions are in `BUILD_PLAN_PROGRAMME.md`.
Detailed tasks for each release are in its own plan:

- `BUILD_PLAN.md` remains the frozen authority for v0.1;
- `BUILD_PLAN_v0_1_5.md`, `BUILD_PLAN_v0_1_6.md` and `BUILD_PLAN_v0_2.md`
  hold theirs;
- `BUILD_PLAN_v0_3.md` holds v0.3's, which now also covers Phase 0;
- later releases get a detailed plan when they start.

## Planning status

Operative from 29 September 2026. ADR-0018 records Pete's master build
order: 33 steps in eight phases, a permanent layer, and a validation gate
at every stage, with targets in months. It supersedes ADR-0015's sequence
(and through it ADR-0008's and ADR-0014's). Nothing here changes v0.1's
scope, approvals or acceptance criteria, or anything already built.

## The question

Poltika is built to answer increasingly difficult versions of one
question:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

It starts small: represent one piece of New Zealand correctly, then two,
then ten; connect them; show that the connections reproduce reality;
make predictions; let reality prove them wrong; improve.

## North star

New Zealand's open, evidence-linked policy intelligence infrastructure: a
computational representation of how policy, people, businesses,
government and physical systems interact, used to test interventions,
discover trade-offs and learn from what actually happens.

It serves long-run prosperity, resilience and living standards within
fiscal, distributional, environmental, institutional and physical
constraints. People choose the objectives and trade-offs. Poltika
measures consequences; it doesn't decide what New Zealand ought to value.

The motivating baseline: Treasury's He Tirohanga Mokopuna 2025 projects
net core Crown debt at 200.0% of GDP by 2065 under unchanged fiscal
policy, a projection rather than a prediction.

## The journey in one line

`Rules → Evidence → Conformance → Population → Accounting → Historical State → Baseline → Causality → Validation → National State → Domain Models → Federation → Calibration → Digital Twin → Decision Intelligence → Policy Search → Public Infrastructure → AI Scientific Layer`

What Poltika progressively learns to answer:

`What are the rules? → Who do they affect? → What do they cost? → How does New Zealand work? → Why do outcomes change? → What happens under different futures? → Where are we wrong? → What information are we missing? → What feasible choices exist? → What are their trade-offs?`

The current work (WFF and the Accommodation Supplement, then evidence and
explainability) sits at the start of Phase 1, not on a detour from the
eventual digital twin.

## The master build order

Months are targets from M0 = October 2026. Validation gates and
milestones decide when something is done.

### Phase 0 - Foundations (M0-M2)

1. **Epistemic Constitution and Model Governance.** Fact against rule
   against estimate against assumption against scenario; provenance;
   reproducibility; uncertainty; model-change controls; Māori data
   governance; privacy and security; and the principle that AI can never
   become an unsourced source of truth.
2. **National Variable Registry and Common Schemas.** Poltika's canonical
   language for New Zealand: variables, units, stocks and flows, time
   periods, geography, populations, entities, price bases and
   identifiers. Every quantity carries its value, uncertainty and
   evidence: X = (x̂, D_x, E_x). It starts small and expands continuously.

### Phase 1 - Executable New Zealand (M0-M9)

3. **Deterministic Statutory Kernel.** New Zealand legislation and policy
   rules as executable logic: WFF and the Accommodation Supplement, then
   income tax, benefits, NZ Super, childcare support, KiwiSaver
   interactions and other major systems.
4. **Evidence Intelligence and Evidence Graph.** Every rule, parameter
   and assumption connected to its source, effective period, evidence
   class and downstream dependencies.
5. **Legislation Conformance Suite.** Sourced golden, boundary,
   contradiction and regression cases. Eventually the specifications and
   fixtures are published as an independent executable standard.
6. **Validation Framework and Forward Prediction Ledger v0.** Benchmark
   comparisons, model scoring and immutable ex-ante predictions. The
   ledger begins small and grows with Poltika.

**Milestone:** Poltika can reliably answer "What does current New Zealand
policy actually do?"

### Phase 2 - Population and Fiscal Effects (M3-M9)

7. **Household Microsimulation Engine.** From individual households to
   representative New Zealand populations and distributional analysis.
8. **Fiscal and Shared Accounting Spine.** Households, the Crown, firms,
   the financial sector and eventually the external sector, with
   consistent stocks and flows and accounting invariants.
9. **Historical NZ State Store.** Versioned snapshots of New Zealand's
   historical economic, demographic, fiscal and eventually physical
   state.

**Milestone:** "Who gains or loses, and what does this cost the Crown?"

### Phase 3 - Baseline New Zealand (M6-M13)

10. **National Baseline Engine.** Internally consistent reference
    trajectories for population, economy and Crown finances.
11. **Uncertainty and Sensitivity Framework.** Parameter distributions,
    confidence ranges, scenario uncertainty, model-form uncertainty and
    global sensitivity analysis.
12. **Causal Evidence Library.** Behavioural relationships, each
    classified `NZ_CAUSAL`, `NZ_OBSERVATIONAL`,
    `INTERNATIONAL_TRANSFERRED`, `EXPERT_ASSUMPTION` or
    `SCENARIO_ASSUMPTION`.
13. **Historical Validation Laboratory.** Backcasting, policy replay,
    shock replay, and comparison with naive, statistical and government
    benchmarks.

**Milestone:** "What happens if policy X changes, and how confident
should we be?" This is v1.0.

### Phase 4 - First National System Model (M11-M22)

14. **National State Transition Engine.** S_t → S_t+1, with an explicit
    `NZState` containing population, households, economy, the Crown,
    housing, health, infrastructure and more. This is where Pete finds
    MIT's Andorra architecture most relevant.
15. **Canonical NZ Scenario Library.** Reference, low and high
    productivity, demographic pressure, global shocks, infrastructure
    constraints, technology upside and other standard scenarios.
16. **Priority Domain Models,** built one after another: NZ Super and
    ageing, health, housing and land, labour and migration, productivity
    and capital, infrastructure, energy, trade. Each domain earns
    integration through validation.

**Milestone:** Poltika can simulate interacting long-term New Zealand
trajectories, rather than isolated policies.

### Phase 5 - Federated New Zealand (M16-M28)

17. **Federated Model Graph.** Validated domain models connected through
    the National State and the accounting spine.
18. **Continuous State Estimation.** New observations continuously
    reconciled with Poltika's estimate of the current state, using
    statistical and Bayesian methods.
19. **Synthetic Population Programme.** Increasingly realistic synthetic
    households and firms, supported by strong enough microdata and
    governance, rather than pretending public marginal distributions are
    adequate.
20. **Spatial and Physical Twin.** Land, housing, infrastructure capacity,
    transport, energy, water and regional constraints.

**Milestone:** an operational national digital twin. Poltika isn't called
one before this.

### Phase 6 - Decision Intelligence (M22-M30)

21. **Cost-of-Delay Engine.** How delaying an intervention changes the
    size of the future adjustment needed.
22. **Value-of-Information Engine.** Which uncertainties matter most, and
    what research or data would most improve a decision.
23. **Policy-Space Search and Inverse Solver.** Search large combinations
    under user-defined constraints, instead of testing one policy at a
    time.
24. **Pareto Frontier Engine.** Feasible trade-offs, for example across
    fiscal sustainability, incomes, distribution, housing and emissions,
    never a single "optimal" political answer.

**Milestone:** "Given these objectives and constraints, what feasible
trajectories exist?"

### Phase 7 - National Decision Infrastructure (M26-M34)

25. **Public NZ Futures Laboratory.** Every result shows: why? source?
    assumptions? uncertainty? who is affected? what would change it?
26. **Policy and Manifesto Analysis Interface.** Common assumptions
    applied to documented proposals, showing their modelled fiscal,
    economic and distributional consequences without political scoring.
27. **Constraint-Based Negotiation Sandbox.** Stakeholders state
    constraints, and Poltika finds the feasible intersection.
28. **Research and Institutional APIs.** Treasury, councils, universities,
    consultancies and other authorised users work programmatically with
    Poltika's models and evidence.

A trust gate comes first: production hardening, independent scrutiny,
and a published forecast record.

### Phase 8 - AI Scientific Layer (M30-M38)

29. **Natural-Language Policy Interface.** Human questions translated
    into structured model queries.
30. **AI Hypothesis Discovery.** Proposed mechanisms, relationships and
    research questions, never promoted into a model without validation.
31. **AI Model Orchestration.** Selecting and coordinating validated
    models, scenarios, evidence and simulations.
32. **AI Explanation and Research Agent.** Explanations drawn from the
    executed model trace and the evidence graph, never plausible
    after-the-fact stories.
33. **Autonomous Research Loop, with human gates.**
    `Prediction → Observation → Error → Hypothesis → Evidence → Test → Human review → Model update`

## The permanent layer

Not phases. These run through Steps 1-33 for the life of Poltika:

- evidence and provenance;
- validation and benchmarking;
- forward prediction scoring;
- uncertainty and model risk;
- versioning and reproducibility;
- Māori data governance;
- privacy and security;
- human oversight;
- model governance.

**Every stage has a validation gate.** Poltika doesn't move from "built"
to "trusted" because the code works. Each milestone is claimed only on
validation evidence, and can be lost when the evidence stops supporting
it.

Some things can't be compressed, whatever the pace: the 1 April rate
year, forecast resolution, microdata access, independent human scrutiny,
Māori data governance engagement and Pete's decisions.

## Releases

| Release | Steps | Milestone |
| --- | --- | --- |
| v0.1, v0.1.5 | Done: WFF and the Accommodation Supplement, with evidence and explainability | |
| v0.2 | Ready to tag: static microsimulation on a synthetic development population | |
| v0.1.6 | The 2027-28 year, by 1 April 2027 | |
| v0.3 | Phase 0; income tax and the core benefits | |
| v0.4 | Steps 4-6 | Phase 1 |
| v0.5 | Steps 7-9 | Phase 2 |
| v0.6, v0.7 | Steps 10-13 | |
| v1.0 | Gates 1-13 | Phase 3 |
| v1.x, v2.0 | Steps 14-16 | Phase 4 |
| v2.x, v3.0 | Steps 17-20 | Phase 5 |
| v3.x, v4.0 | Steps 21-24 | Phase 6 |
| v5 | Steps 25-28 | Phase 7 |
| v6 | Steps 29-33 | Phase 8 |

## Policy kernel coverage

The kernel covers New Zealand's household tax-and-transfer system, then
the taxes and classifications the accounting spine needs, one reviewed
domain at a time (`BUILD_PLAN_PROGRAMME.md` Step 3):

- **Lane 3A, v0.3:** personal income tax, Jobseeker Support, Sole Parent
  Support, Supported Living Payment.
- **Lane 3C:** NZ Superannuation, Childcare and OSCAR Subsidies,
  KiwiSaver interactions, Paid Parental Leave.
- **Lane 3D:** student support, ACC levies and earnings compensation,
  Temporary Additional Support, Disability Allowance, other MSD
  assistance, Child Support.
- **Lane 3E:** GST, company tax, other tax regimes, selected regulatory
  costs, Crown revenue and expenditure classifications.

Each domain adds a yearly update, so coverage grows only as fast as it
can be kept current.

## What Poltika never builds

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP.
- No silently changing models.
- No point estimate where the uncertainty is large.
- No synthetic population presented as reality.
- No policy search before causal relationships are credible.
- No "digital twin" branding before Phase 5's milestone.
- No AI claim promoted into a model without validation.
- Never optimise the model instead of the country.

AI is used throughout development. It operates the instrument; it is
never the instrument.
