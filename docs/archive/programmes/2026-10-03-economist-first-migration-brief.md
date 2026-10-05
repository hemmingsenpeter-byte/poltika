# Poltika — Repository Reconciliation, Archival, and Master Build-Plan Migration

You are working inside the **Poltika** repository.

Your task is to reconcile the repository's current planning hierarchy with a newly approved **economist-first, pilot-driven, vertical-slice build strategy**.

This is primarily a **programme-governance and documentation migration**, not an architectural rewrite and not a codebase reset.

The objective is to end with:

1. exactly **one active master build order**;
2. preserved historical planning and decision provenance;
3. no loss of completed work;
4. no contradictory instructions for Claude Code, Codex, GPT, or future contributors;
5. the existing technical architecture preserved where still valid;
6. near-term development redirected toward:
   - household economic modelling;
   - economist-grade static analysis;
   - external pilots;
   - representative population microsimulation;
   - fiscal/distributional analysis;
   - then progressive expansion toward the national digital twin.

Do not begin by editing files.

First reconcile the current repository state.

---

# 1. The strategic change

The previous programme, principally ADR-0019 and `BUILD_PLAN_PROGRAMME.md`, organised Poltika around a 33-step national-system build:

- epistemic foundations;
- National Variable Registry;
- statutory kernel;
- evidence graph;
- conformance;
- validation;
- population;
- accounting;
- historical state;
- baseline;
- uncertainty;
- causality;
- state transitions;
- domains;
- federation;
- digital twin;
- decision intelligence;
- AI.

That architecture contains many sound long-term ideas.

The problem is the **execution order**.

The new programme optimises for:

> **the shortest technically rigorous path from the current repository to economist-grade output, credible external pilots, and cumulative progress toward the long-term economic/policy digital twin.**

The new governing principle is:

> **Build complete analytical vertical slices, validate them, put them in front of real users, and generalise infrastructure only when multiple real models require it.**

The digital twin remains the long-term destination.

What changes is how Poltika earns its way there.

---

# 2. Do not discard working architecture

This migration must preserve working code and sound architectural decisions.

The repository already contains substantial valuable capability, including where present:

- Working for Families;
- Accommodation Supplement;
- deterministic statutory calculation;
- source and parameter provenance;
- calculation traces;
- deterministic explanations;
- scenario records;
- scenario replay;
- PostgreSQL scenario persistence;
- canonical population schemas;
- data manifests and dataset registry;
- synthetic population tooling;
- weighting/calibration machinery;
- static microsimulation;
- cross-validation;
- FastAPI APIs;
- hosted pilot hardening;
- analyst interfaces;
- analyst workbench;
- CSV/Excel export;
- assurance tests;
- regression/golden cases;
- independent review machinery.

None of this should be rebuilt merely because the programme order changes.

The migration should maximise reuse.

---

# 3. Long-term target remains

The eventual system is still approximately:

```text
AUTHORITATIVE SOURCES + DATA
              ↓
SEMANTIC / EPISTEMIC CONTRACTS
              ↓
MODELS
statutory
statistical
behavioural
causal
domain
              ↓
SCENARIOS
baseline
reform
assumptions
population
time
              ↓
SIMULATION / ORCHESTRATION
              ↓
ACCOUNTING + SHARED STATE
              ↓
ASSURANCE
conformance
benchmarking
historical validation
uncertainty
prediction record
              ↓
ANALYTICAL OUTPUTS
              ↓
ANALYST / API / EVENTUAL AI
```

Later:

```text
observations
     ↓
state estimation
     ↓
NZState(t)
     ↓
connected validated models
     ↓
state transitions
     ↓
NZState(t+1)
     ↓
new observations
     ↓
validation / recalibration
```

Do not remove this destination from `ARCHITECTURE.md`.

What changes is the implementation sequence.

---

# 4. First task: repository reconnaissance

Before proposing any changes, inspect the actual repository.

Read at minimum:

- `CLAUDE.md`
- `AGENTS.md`
- `README.md`
- `ARCHITECTURE.md`
- `REPOSITORY_STRUCTURE.md`
- `BUILD_PLAN.md`
- `BUILD_PLAN_v0_1_5.md`
- `BUILD_PLAN_v0_1_6.md`
- `BUILD_PLAN_v0_2.md`
- `BUILD_PLAN_v0_3.md`
- `BUILD_PLAN_PROGRAMME.md`
- `ROADMAP.md`
- `ROADMAP_REALIGNMENT.md`
- `PROGRAMME_STATUS.md`
- `PETE_QUEUE.md`
- `CHANGELOG.md`

Read relevant doctrine:

- `doctrine/epistemic-constitution.md`
- `doctrine/architecture-doctrine.md`
- `doctrine/development-doctrine.md`
- `doctrine/review-doctrine.md`
- `doctrine/test-doctrine.md`
- `doctrine/deterministic_core.md`
- `doctrine/llm_boundaries.md`
- `doctrine/ip-doctrine.md`
- `doctrine/scope-doctrine.md`

Read at minimum ADRs:

- ADR-0014;
- ADR-0015;
- ADR-0017;
- ADR-0018;
- ADR-0019;
- ADR-0020;

and any newer ADRs that exist.

Also inspect:

- current open PRs;
- recent merged PRs;
- active/in-flight branches;
- review queue;
- `docs/decision_log.md`;
- current test/release gates;
- actual source-tree state.

Do not rely on plan prose when current code or merged PRs show otherwise.

---

# 5. Produce a reconciliation report before modifying anything

Your first output must classify every major planning artifact into one of:

### A. Active authority
Still governs current or future implementation.

### B. Active supporting plan
Still useful for a bounded implementation lane but no longer sets the overall programme order.

### C. Historical / archive
Superseded planning state retained for provenance.

### D. Decision record
Must remain where it is because it documents why a decision was taken, even if later superseded.

### E. Release evidence
Must remain permanently available.

For each file, provide:

- current role;
- whether it is still authoritative;
- what supersedes it;
- recommended final location;
- whether references must be updated.

Do not move/delete anything until this reconciliation is complete.

---

# 6. Expected archival policy

The target repository should distinguish:

```text
doctrine/            permanent governing constraints
adr/                 permanent decision history
docs/releases/       release evidence
reviews/             review history
review_packets/      review evidence
docs/decision_log.md delegated decisions

BUILD_PLAN_PROGRAMME.md
                     current master build order

PROGRAMME_STATUS.md  current live status

BUILD_PLAN_v0_3.md   current detailed household-economic-model lane
BUILD_PLAN_v0_1_6.md current statutory-maintenance lane

docs/archive/        superseded planning documents
```

Planning documents may move to archive.

Decision history must not be erased.

---

# 7. Specific archival recommendations to verify

Verify these against actual repository state.

Do not blindly apply them if the repository now shows something different.

## ROADMAP_REALIGNMENT.md

Expected action:

> Archive as historical planning.

Its sequencing was already superseded by ADR-0019.

Retain it for the W1-W10 historical reasoning.

Suggested destination:

```text
docs/archive/programmes/2026-09-26-roadmap-realignment.md
```

---

## BUILD_PLAN_PROGRAMME.md

Expected action:

> Preserve a historical snapshot, then rewrite the live filename as the new single master build order.

Archive the ADR-0019 programme before replacement.

Suggested historical copy:

```text
docs/archive/programmes/2026-09-29-adr0019-master-programme.md
```

The root:

```text
BUILD_PLAN_PROGRAMME.md
```

must remain the current build-order authority.

---

## ROADMAP.md

Expected action:

> Preserve a dated ADR-0019 snapshot, then rewrite root `ROADMAP.md` to reflect the new build philosophy.

Suggested historical copy:

```text
docs/archive/roadmaps/2026-09-29-roadmap-adr0019.md
```

Root `ROADMAP.md` should stay high-level and should not duplicate the full programme backlog.

---

## PROGRAMME_STATUS.md

Expected action:

> Preserve a dated snapshot and rebuild the live file around the new capability gates.

Suggested archive:

```text
docs/archive/status/2026-10-03-programme-status-adr0019.md
```

Do not copy stale statuses into the new file without reconciling them against GitHub.

---

## BUILD_PLAN_v0_1_5.md

Expected action:

> Archive or clearly mark completed historical release plan.

v0.1.5 is not active programme direction.

Its release evidence stays in `docs/releases/`.

---

## BUILD_PLAN_v0_2.md

Expected action:

> Keep until v0.2.0 is actually tagged.

If the tag is already present, archive it as a completed release plan.

If the tag is still outstanding, keep it live until release completion.

Do not confuse a completed implementation with a completed release record.

---

## BUILD_PLAN.md

Expected action:

> Keep available as the frozen v0.1 historical build record until all living doctrine references have been cleanly migrated.

Do not move this file yet if existing doctrine or code references depend on anchors inside it.

However:

- stop describing it as "what is being built now";
- make clear it is the historical v0.1 plan;
- prefer future doctrine references to `doctrine/*`.

This may become archive-eligible in a later cleanup once all authoritative doctrine has been extracted.

---

## BUILD_PLAN_v0_1_6.md

Expected action:

> Keep active.

Treat it as a statutory-maintenance lane:

- source currency;
- new policy years;
- effective-dated updates;
- enacted rule changes.

It is not a competing product roadmap.

---

## BUILD_PLAN_v0_3.md

Expected action:

> Keep active and re-home it under the new master programme.

This plan contains much of the immediate next product work:

- shared household model;
- personal income tax;
- Jobseeker Support;
- Sole Parent Support;
- Supported Living Payment;
- household dependency graph;
- disposable income;
- EMTRs;
- incentive measures.

Do not archive it merely because its old programme mapping changes.

Instead update its redirect/header so it is the detailed plan for the new household-economic-model phase.

---

# 8. ADR handling

Do not delete or move ADRs simply because they have been superseded.

## ADR-0019

Create a new ADR, expected to be ADR-0021 unless a newer number is required.

The new ADR should state:

> ADR-0019's execution sequence is superseded.

But retain ADR-0019's enduring principles where still accepted.

These include, where compatible:

- common semantics;
- epistemic classification;
- model governance;
- validation gates;
- uncertainty as an explicit concern;
- digital-twin branding only after sufficient validation;
- human control of objectives/trade-offs;
- AI late and never authoritative for calculations;
- model composition;
- long-run national-system goal.

ADR-0019 should be updated only enough to show:

```text
Status: superseded for programme sequencing by ADR-00XX.
Architectural principles remain unless explicitly superseded.
```

Do not rewrite its historical content.

---

## ADR-0015

Retain as historical decision context.

Its sequence was already superseded.

---

## ADR-0014

Retain.

The decision to implement static microsimulation remains useful and has already produced substantial code.

---

## ADR-0017

Retain as operative unless repository inspection reveals otherwise.

The shared household model is a core near-term requirement.

---

## ADR-0018

Inspect carefully.

The repository appears to have implemented the workbench design.

If ADR-0018 still says `proposed` while implementation/review have effectively adopted it, reconcile that status through the appropriate decision process.

Do not silently mark it accepted without the authority required by ADR-0020.

If acceptance needs Pete, place the minimum decision in `PETE_QUEUE.md`.

The new programme should explicitly promote the Analyst Workbench to a first-product surface.

---

## ADR-0020

Keep active.

Delegated acceptance, Tier A/B/C boundaries, review requirements and Pete's retained decisions remain in force.

The new programme does not override them.

---

# 9. The new programme structure

Replace the old 33-step execution sequence with the following capability-oriented phases.

Do not necessarily use version numbers as the primary organising principle.

Use **capability gates**.

---

# PHASE A — Stabilise

1. Finish only the small amount of governance/professional-baseline work already substantially in flight.
2. Reconcile current open PRs and review debt.
3. Establish/tag the current release baseline where appropriate.
4. Stop expanding abstract Phase 0 infrastructure.

Gate:

> The repository is safe enough to focus on economic models.

---

# PHASE B — Household economic kernel

5. Complete only the semantic contracts needed for current household modelling.
6. Complete the shared household model.
7. Implement personal income tax.
8. Implement:
   - Jobseeker Support;
   - Sole Parent Support;
   - Supported Living Payment.
9. Build the household computational dependency graph.
10. Build canonical household disposable income.
11. Build:
   - EMTRs;
   - withdrawal profiles;
   - replacement/participation measures where supported.

Gate:

> Poltika can calculate the connected household tax-transfer position rather than isolated entitlements.

---

# PHASE C — Assurance and analyst product

12. Bring legislation conformance forward.
13. Bring model/benchmark validation forward.
14. Complete the counterfactual scenario contract.
15. Promote/complete the Analyst Workbench as an end-to-end analytical workflow.

Gate:

> An external analyst can define a reform, run cases, inspect evidence, understand calculations and export results.

---

# PHASE D — Pilot 1

16. Run a real external analyst pilot.

The pilot should test:

- usefulness;
- speed;
- comprehension;
- reproducibility;
- auditability;
- workflow friction;
- missing capabilities.

Do not require national population estimates first.

Gate:

> At least one external user demonstrates that the workflow solves a real analytical problem.

Record evidence.

---

# PHASE E — Representative population microsimulation

17. Harden the canonical `PopulationDataset` contract.
18. Harden the batch microsimulation engine.
19. Implement robust weighting/calibration.
20. Validate against authoritative external aggregates.
21. Build national distributional outputs.

Gate:

> Poltika can estimate direct population-level policy effects with transparent representativeness and validation.

---

# PHASE F — Fiscal and economist-grade output

22. Build the first direct fiscal accounting spine.
23. Combine distributional and fiscal analysis.
24. Produce a deterministic economist-style report package.

Minimum report content:

- policy specification;
- baseline;
- reform;
- fiscal effect;
- affected population;
- winners/losers;
- income-group results;
- household-type results;
- incentive effects;
- data;
- assumptions;
- validation;
- provenance;
- limitations.

Gate:

> Poltika produces independently challengeable economist-grade static policy analysis.

---

# PHASE G — Pilot 2

25. Run an external population-level policy-analysis pilot.

Evaluate whether users:

- trust the estimates;
- understand limitations;
- would use the output professionally;
- find it faster/better than current Excel/R/Python workflows.

Gate:

> External validation justifies broader investment.

---

# PHASE H — Expand statutory coverage

26. Add new policy domains according to real analytical demand.

Potential examples:

- NZ Superannuation;
- childcare support;
- KiwiSaver interactions;
- Paid Parental Leave;
- student support;
- ACC;
- supplementary assistance;
- Child Support.

Do not implement the list mechanically.

External/use-case pull determines order.

---

# PHASE I — Historical validation

27. Add historical policy/data states.
28. Build `as_of` execution.
29. Build historical replay.
30. Build the prediction/model-error ledger.

Gate:

> Poltika can demonstrate where its models reproduce reality and where they fail.

---

# PHASE J — Behaviour and causality

31. Build the structured Causal Evidence Library.
32. Add behavioural models one mechanism at a time.
33. Preserve:
   - mechanical result;
   - behaviour-adjusted result.
34. Add formal uncertainty propagation.

Gate:

> Behavioural results are empirically sourced, separable from statutory results and uncertainty-aware.

---

# PHASE K — Dynamic national model

35. Introduce `NZState(t)` only once real requirements exist.
36. Build state transitions.
37. Build a National Baseline Engine.
38. Validate against historical/official trajectories.

Gate:

> Poltika can produce defensible multi-year conditional trajectories.

---

# PHASE L — Domain models

39. Add high-value domains vertically.

Examples:

- labour;
- housing;
- health;
- education;
- infrastructure;
- firms/productivity;
- environment;
- transport;
- energy.

Every model declares:

- requires;
- provides;
- parameters;
- time step;
- evidence;
- uncertainty;
- validation.

---

# PHASE M — Digital twin infrastructure

40. Generalise the model dependency graph when necessary.
41. Federate only when models genuinely require independent execution.
42. Build continuous state estimation.
43. Add spatial state.
44. Add production synthetic populations where justified.
45. Use agent-based models only for domains where interactions require them.

Gate:

> Poltika maintains a validated, periodically reconciled computational representation of New Zealand.

Only then use "digital twin" operationally.

---

# PHASE N — Decision intelligence

46. Cost-of-delay.
47. Value-of-information.
48. Policy-space search.
49. Pareto-frontier analysis.

People specify objectives and constraints.

Poltika calculates consequences/trade-offs.

---

# PHASE O — Public / research infrastructure

50. Research APIs.
51. Policy-analysis interfaces.
52. Futures laboratory.
53. Scenario/negotiation tools.

Only once validation/trust permits.

---

# PHASE P — AI layer

54. Natural-language scenario interface.
55. AI explanation over verified results.
56. AI model orchestration over validated models.
57. AI hypothesis generation.
58. Human-gated autonomous research loop.

AI remains above the modelling system.

It does not become the numerical source of truth.

---

# 10. Explicit old-to-new mapping

The new master programme should contain a migration table mapping every old ADR-0019 step 1–33 to:

- new phase;
- retained;
- split;
- moved earlier;
- moved later;
- absorbed;
- deferred.

Expected examples:

### Old Step 1 — Epistemic constitution/model governance

Retain completed work.

Finish bounded work already underway.

Then treat governance as a permanent constraint, not a blocking development phase.

---

### Old Step 2 — National Variable Registry

Split.

Keep the concept.

Implement incrementally from real model requirements.

Do not block tax/benefit work on universal registry completion.

---

### Old Step 3 — Statutory kernel

Move to the immediate centre of the critical path.

---

### Old Step 4 — Evidence graph

Defer general graph implementation.

Retain existing provenance/evidence structures.

Revisit the richer graph when causal/economic evidence makes it useful.

---

### Old Step 5 — Conformance

Move earlier.

Build alongside the household kernel.

---

### Old Step 6 — Validation + prediction ledger

Split:

- validation moves earlier;
- prediction ledger/historical forecasting evidence moves later.

---

### Old Step 7 — Microsimulation

Recognise that substantial v0.2 capability already exists.

Harden it after Pilot 1 rather than treating it as greenfield work.

---

### Old Step 8 — Accounting

Narrow initially to direct fiscal scoring.

Broaden later.

---

### Old Steps 9–10 — historical store/baseline

Move later.

They no longer block the first economist-grade product.

---

### Old Step 11 — uncertainty

Semantic accommodation may exist early.

Full propagation comes later with empirical/behavioural models.

---

### Old Step 12 — causal evidence

Retain later.

---

### Old Step 13 — historical validation

Retain and make strategically important before sophisticated forecasting.

---

### Old Step 14 — state transition

Retain later.

---

### Old Step 15 — scenario library

Split:

- core scenario/counterfactual contract moves very early;
- broad canonical national scenario library stays later.

---

### Old Step 16 — domain models

Retain and make demand-driven.

---

### Old Steps 17–20

Retain as digital-twin infrastructure.

Do not build early.

---

### Old Steps 21–24

Retain as decision intelligence.

---

### Old Steps 25–28

Retain as public/institutional product layer.

---

### Old Steps 29–33

Retain as late AI layer.

Do not place AI discovery on the critical path to core simulation.

---

# 11. Architecture changes to document

Do not fundamentally replace `ARCHITECTURE.md`.

Update it to remove stale "what exists today" statements.

For example, verify whether statements such as:

- no data pipeline;
- no container setup;
- no population modelling;
- no workbench;

are now false.

Separate:

## Release architecture
What v0.1 actually shipped.

from:

## Current architecture
What exists on `main` today.

from:

## Long-term target architecture
Where Poltika is going.

---

# 12. Core engine hierarchy

Where old architectural diagrams imply:

```text
Discovery
→ Hypothesis
→ Simulator
→ Assurance
```

replace the primary hierarchy conceptually with:

```text
Evidence
   ↓
Models
   ↓
Simulator
   ↓
Outputs
   ↓
Assurance
```

with:

```text
Discovery
Hypothesis
AI research
```

as later workflows around the validated modelling core.

Do not necessarily rename/delete existing packages merely for documentation consistency.

Change physical structure only if current code actually benefits.

---

# 13. Evidence graph treatment

Do not delete the idea.

Current statutory provenance can remain implemented using existing:

- `sources.yaml`;
- rule/source links;
- parameter source IDs;
- trace structures;
- evidence coverage;
- provenance reports.

The richer evidence/causal graph becomes justified when empirical relationships need to represent:

- intervention;
- outcome;
- estimate;
- source;
- population;
- jurisdiction;
- identification method;
- uncertainty;
- external validity.

Defer graph-specific infrastructure until then.

---

# 14. National Variable Registry treatment

Keep the registry concept.

Change its programme role from:

> build the national vocabulary before models

to:

> grow the national vocabulary from actual model contracts.

Example:

```text
WFF requires variables
        ↓
register them
        ↓
AS reuses/adds
        ↓
tax reuses/adds
        ↓
benefits reuses/adds
        ↓
population adds
        ↓
fiscal adds
        ↓
domain models expand
```

Do not delete already built registry/schema work.

Do not force every future quantity into a universal schema before it is needed.

---

# 15. Workbench treatment

The Analyst Workbench becomes strategically important.

It should be recognised as the first commercial/analyst product surface.

Existing work should be reused.

The target workflow is:

```text
baseline
   +
reform
   +
household/population
   +
assumptions
        ↓
scenario
        ↓
simulation
        ↓
comparison
        ↓
verified analytical blocks
        ↓
screen / CSV / Excel / report / trace
```

Do not create a parallel product stack.

Build on the existing workbench contracts.

---

# 16. Pilot gates

Add formal pilot gates to the programme.

## Pilot 1

Before representative national modelling.

Question:

> Can an external analyst use Poltika productively to analyse supported household reforms?

Required evidence should include:

- real external user;
- real analytical question;
- workflow completion;
- feedback;
- missing features;
- usefulness assessment.

---

## Pilot 2

After national static microsimulation and fiscal/distributional outputs.

Question:

> Will an external analyst trust and use Poltika's national policy estimates professionally?

Record findings.

Expansion beyond this point should increasingly be earned by external demand.

---

# 17. Programme-status migration

Rebuild `PROGRAMME_STATUS.md`.

Do not erase completed work.

Map existing code into the new programme.

Examples that may already count as complete/partial assets:

- WFF;
- AS;
- provenance;
- trace;
- evidence coverage;
- deterministic explanations;
- scenario identity;
- scenario store;
- population schema;
- population runner;
- weighting;
- calibration;
- synthetic population;
- cross-validation;
- analyst APIs;
- workbench backend;
- hosted pilot hardening.

For every new phase/task assign:

- status;
- owner;
- relevant PR(s);
- blockers;
- evidence;
- old task mapping if useful.

Use statuses consistent with ADR-0020.

---

# 18. PETE_QUEUE migration

Reconcile `PETE_QUEUE.md`.

Keep valid Tier C items.

Expected treatment:

## Q1 repository ruleset

Keep.

## Māori data governance

Keep.

But ensure it blocks:

- Māori-specific claims/outputs;
- microdata use where applicable;

not unrelated deterministic household-policy work unless doctrine requires otherwise.

## IDI access

Keep for later population/microdata work.

## v0.3 D1–D3

Retain/rewrite as the immediate required decisions once sourcing is available:

- supported income-tax slice;
- benefit slices;
- disposable-income definition;
- relevant household economic measures.

## Historical horizon

Retain but remove artificial near-term urgency if historical state no longer sits early on the critical path.

## v0.2 release tag

Close if completed.

Keep if outstanding.

## Old programme decisions P6/P7/etc.

Do not leave opaque obsolete step references.

Map each surviving decision to the new capability/phase.

---

# 19. CLAUDE.md and AGENTS.md

This is critical.

These files currently instruct agents which plan to follow.

Update them in the same migration so:

> planning, sequencing and new implementation work begins with the **new `BUILD_PLAN_PROGRAMME.md`**.

They should then read the relevant detailed active plan.

Do not leave language such as:

> "follow ADR-0019's 33-step master order"

once the new ADR is active.

Any stale instruction of that form is a P1/P2 documentation/governance defect because it can cause agents to implement the wrong programme.

Search globally for:

- `ADR-0019`;
- `33 steps`;
- `Phase 0`;
- `BUILD_PLAN_PROGRAMME.md`;
- superseded release mappings;
- old roadmap sequence claims.

Classify every match.

Do not blindly replace historical references inside ADRs/reviews.

Update only operational/current references.

---

# 20. README.md

Rewrite the "Where to start" section so a new contributor has an unambiguous hierarchy.

Target structure:

1. `docs/ORIENTATION.md`
2. `ARCHITECTURE.md`
3. `REPOSITORY_STRUCTURE.md`
4. `BUILD_PLAN_PROGRAMME.md`
5. `PROGRAMME_STATUS.md`
6. relevant active detailed plan
7. `PETE_QUEUE.md`
8. doctrine/ADRs as necessary.

Do not present completed release plans as active build instructions.

---

# 21. REPOSITORY_STRUCTURE.md

Update planning-file descriptions.

Add the archive hierarchy if created.

Do not alter production package layout merely because programme sequencing changed.

Document:

```text
docs/archive/
```

as non-authoritative historical planning.

Agents must never use archive documents to determine the next implementation task.

---

# 22. ROADMAP.md after migration

Keep this concise.

It should explain:

### Near term

```text
statutory household system
→ analyst workbench
→ Pilot 1
→ representative population microsimulation
→ fiscal/distributional analysis
→ Pilot 2
```

### Medium term

```text
historical validation
→ causal/behavioural modelling
→ uncertainty
→ dynamic state
→ domain models
```

### Long term

```text
federation
→ state estimation
→ spatialisation
→ validated digital twin
→ decision intelligence
→ AI
```

Avoid reproducing the entire implementation backlog.

That belongs in `BUILD_PLAN_PROGRAMME.md`.

---

# 23. New critical path

The new programme must prominently identify:

```text
1. Repository stabilisation
2. Release baseline
3. Minimum household semantics
4. Shared household model
5. Income tax
6. Core benefits
7. Household dependency graph
8. Disposable income
9. EMTR / incentive measures
10. Conformance
11. Validation
12. Analyst Workbench
13. Scenario contract
14. Pilot 1
15. PopulationDataset
16. Batch microsimulation
17. Population calibration
18. External aggregate validation
19. Distributional outputs
20. Direct fiscal accounting
21. Economist-grade report
22. Pilot 2
23. Historical validation
24. Causal / behavioural models
25. Uncertainty propagation
26. Dynamic state
27. National baseline
28. Domain models
29. Federation
30. State estimation
31. Spatial/synthetic population
32. Digital twin
33. Decision intelligence
34. AI layer
```

Exact task numbering may be adjusted during reconciliation.

The dependency intent must not change.

---

# 24. Do not prematurely implement architecture

During this migration, do not start building:

- Neo4j;
- general knowledge graph;
- full evidence graph;
- universal ontology;
- microservices;
- Kubernetes;
- Kafka;
- Spark;
- distributed orchestration;
- large agent frameworks;
- broad national state schema;
- ABM;
- Monte Carlo infrastructure;
- policy optimisation;
- natural-language model orchestration.

The migration PR should primarily realign:

- planning;
- status;
- references;
- architecture prose;
- active task priority.

Separate actual model implementation into later bounded PRs.

---

# 25. Migration PR strategy

Do not put an uncontrolled repository rewrite into one enormous PR.

Propose a safe sequence.

Recommended structure:

## PR 1 — ADR and historical snapshots

- create new programme ADR;
- mark ADR-0019 sequencing superseded;
- copy old programme/roadmap/status into archive;
- add archive README explaining historical/non-authoritative status.

No production code.

---

## PR 2 — master programme replacement

Update:

- `BUILD_PLAN_PROGRAMME.md`;
- `ROADMAP.md`;
- `PROGRAMME_STATUS.md`.

Use the new plan.

Reconcile statuses from actual Git history.

---

## PR 3 — operational reference migration

Update:

- `CLAUDE.md`;
- `AGENTS.md`;
- `README.md`;
- `REPOSITORY_STRUCTURE.md`;
- `PETE_QUEUE.md`;
- current-plan references in `ARCHITECTURE.md`;
- active build-plan redirect notes.

Search for stale operational ADR-0019/33-step instructions.

---

## PR 4 — detailed active plan reconciliation

Update `BUILD_PLAN_v0_3.md` to serve as the detailed household-economic-kernel plan under the new programme.

Preserve:

- source-scoping;
- clean-room policy onboarding;
- tax;
- benefits;
- shared household model;
- dependency graph;
- disposable income;
- EMTRs;
- relevant gates.

Remove or redirect only old programme dependencies that no longer gate execution.

Do not rewrite implementation history.

---

# 26. Preserve Git history

Do not destroy historical context.

Where feasible use `git mv` for archive moves.

Do not squash history manually or recreate historical documents from memory.

Archive exact pre-migration documents.

Do not modify archived snapshots after creation except to fix an obvious archival metadata error.

Prefer an `archive/README.md` that states:

> These files are historical planning records. They are retained for decision provenance and must not be used as the current build order. See the root `BUILD_PLAN_PROGRAMME.md`.

---

# 27. No production-code behaviour changes during programme migration

Unless a tiny change is unavoidable to repair a broken reference/check, the programme migration should not alter:

- calculated amounts;
- policy rules;
- statutory values;
- engine behaviour;
- protected expected values;
- population calculations;
- API semantics.

If implementation defects are discovered, log them separately and create bounded follow-up PRs.

Do not hide them inside the planning migration.

---

# 28. Tests/checks for the migration

Add or update mechanical checks where useful so contradictory planning state does not recur.

Possible checks:

### Current master uniqueness

Operational docs should refer to one master build programme.

### Archive isolation

No operational agent instruction should tell an agent to use `docs/archive/` as current planning.

### Active-plan references

`CLAUDE.md`, `AGENTS.md`, `README.md` and `PROGRAMME_STATUS.md` should agree on the current master.

### ADR status consistency

ADR-0019 should no longer be presented as active sequencing authority after the new ADR is accepted.

### Release-state consistency

Where practical, release documentation and programme status should not contradict existing tags/review state.

Avoid brittle tests over prose unless they prevent a genuine governance failure.

---

# 29. Review current open/in-flight work before migration

Before starting, inspect all current PRs/branches.

Do not duplicate or overwrite active work.

Likely categories include:

- evidence-class tooling;
- security CI;
- governance files;
- hosting/documentation;
- programme-governance work.

Determine whether each should:

- merge before programme migration;
- be retargeted;
- be closed because already satisfied;
- continue independently.

The new strategy says:

> finish bounded professional-baseline work already substantially underway, then stop expanding foundations.

Apply that rule.

---

# 30. One specific branch to scrutinise

If a parked/general quantity-type branch such as:

```text
claude/step2-quantity
```

or equivalent still exists, do not merge it merely because old ADR-0019 Step 2 scheduled it next.

Review it against the immediate household-model requirements.

Ask:

- does income tax need it?
- do benefits need it?
- does disposable income need it?
- does the population simulator need it now?
- does it create genuine reuse?
- or is it premature generalisation?

Keep/reduce/defer accordingly.

Do not discard useful code purely because its motivation changed.

---

# 31. Expected final authority hierarchy

After migration, the repository should have a clear hierarchy:

## Level 1 — doctrine and accepted ADRs

What cannot be silently violated.

## Level 2 — architecture

`ARCHITECTURE.md`

`REPOSITORY_STRUCTURE.md`

What the system is and where things belong.

## Level 3 — current programme

`BUILD_PLAN_PROGRAMME.md`

The single authoritative current build order.

## Level 4 — active detailed lanes

Initially expected:

- `BUILD_PLAN_v0_3.md` — household economic kernel;
- `BUILD_PLAN_v0_1_6.md` — statutory maintenance.

Later phases gain detailed plans when they begin.

## Level 5 — live execution state

`PROGRAMME_STATUS.md`

## Level 6 — Pete-only decisions

`PETE_QUEUE.md`

## Level 7 — historical planning

`docs/archive/`

Never active authority.

---

# 32. Final reconciliation report required

Before implementing the migration, provide Pete with the following.

## 1. Repository planning map

For every current planning file:

- active;
- supporting;
- archive;
- historical decision;
- release evidence.

## 2. Proposed archive moves

Exact old path → new path.

## 3. ADR changes

Exact status changes.

## 4. Old programme → new programme mapping

Every ADR-0019 step mapped to the new phase.

## 5. Existing code reuse map

Identify which new phases already have substantial implementation.

## 6. In-flight work

List PRs/branches and recommendation for each.

## 7. Stale/conflicting documentation

List each current operational contradiction discovered.

## 8. Migration PR sequence

State the exact PRs you recommend.

## 9. Risks

Especially:

- losing useful task detail;
- breaking doc links;
- accidentally changing doctrine;
- agents continuing to read old sequencing;
- confusing archived scope with abandoned scope;
- misreporting completed work.

## 10. Recommended immediate next coding task after migration

Exactly one task.

It should be the highest-value unblocked task on the new critical path.

Do not begin that implementation until the programme migration is complete unless Pete explicitly directs otherwise.

---

# 33. Governing decision rule

Where there is conflict between:

### A

building more abstract infrastructure because the long-term digital twin may eventually need it,

and:

### B

building the smallest rigorous reusable capability needed to answer a real economist/policy question,

choose **B**.

Design A so it remains possible later.

Do not implement A prematurely.

---

# 34. Final objective

After this migration, a new Claude Code or Codex session should be able to enter the repository, read the normal orientation files and conclude unambiguously:

> **The current mission is to connect Poltika's existing statutory, population, provenance, microsimulation and workbench capabilities into a credible household economic-analysis product; prove external usefulness through pilots; then progressively add population, fiscal, behavioural, dynamic and domain capabilities until the validated connected system earns the description of a New Zealand policy/economic digital twin.**

There must be no competing active master roadmap saying otherwise.