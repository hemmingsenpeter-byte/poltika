# Poltika master build order and programme plan

**Date:** 29 September 2026
**Status:** Pete's master technical roadmap, set on 29 September 2026
(ADR-0019). It consolidates the whole planning thread of that day,
including Pete's lessons from MIT's work in Andorra, into 33 steps with
Phase 0 foundations and eight delivery phases. It replaces two earlier
versions from the same day (20
steps, then 22). Pete approved the first version with its recommended
decisions ("Approve and proceed all"), and those decisions carry over
unless marked otherwise ("Decisions"). The reconciliation, month targets,
tasks and release mapping are Claude Code's drafting to Pete's order.
**Supersedes:** ADR-0015's release sequence and `ROADMAP_REALIGNMENT.md`
W9. `BUILD_PLAN.md` stays the frozen record of v0.1. `BUILD_PLAN_v0_3.md`
stays the task list for v0.3, which now covers Phase 0 and the first tier
of Step 3 ("What changes in the current plans").

`BUILD_PLAN.md`'s doctrines apply unchanged: primary sources only, the
three test classes, protected values changed only through the test
doctrine, ambiguity escalated, and no external implementation as a source
of policy logic. This plan names no statutory rule, rate, threshold or
interaction. Each is set by the sourcing task that needs it.

## The mandate and the question

**Mandate:** build Poltika to help New Zealand maximise sustainable
prosperity and quality of life for current and future generations.

Poltika is built to answer increasingly difficult versions of one
question:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

**North star:** New Zealand's open, evidence-linked policy intelligence
infrastructure. It is a computational representation of how policy,
people, businesses, government and physical systems interact, used to
test interventions, discover trade-offs and learn from what actually
happens.

What Poltika serves is long-run prosperity, resilience and living
standards, within fiscal, distributional, environmental, institutional
and physical constraints. Debt alone or GDP alone is not the objective.
**People choose the objectives and trade-offs. Poltika measures
consequences. It doesn't decide what New Zealand ought to value.**

**Why now:** Treasury's [He Tirohanga Mokopuna 2025](https://www.treasury.govt.nz/publications/ltfp/he-tirohanga-mokopuna-2025)
projects net core Crown debt, excluding NZSF and advances, at 200.0% of
GDP by 2065 in its unchanged-policy LTFM baseline (Table 2, p. 38).
The executive summary (p. 2) calls this a projection, not a prediction.
Published 24 September 2025; retrieved 29 September 2026 and rechecked
2 October 2026. Step 10 reproduces that baseline or explains where
Poltika's differs.

## The journey in one line

`Rules → Evidence → Conformance → Population → Accounting → Historical State → Baseline → Causality → Validation → National State → Domain Models → Federation → Calibration → Digital Twin → Decision Intelligence → Policy Search → Public Infrastructure → AI Scientific Layer`

In terms of what Poltika progressively learns to answer:

1. What are the rules?
2. Who do they affect?
3. What do they cost?
4. How does New Zealand work?
5. Why do outcomes change?
6. What happens under different futures?
7. Where are we wrong?
8. What information are we missing?
9. What feasible choices exist?
10. What are their trade-offs?

The work now under way (WFF and the Accommodation Supplement, then
evidence and explainability) sits at the start of Phase 1. It is the
beginning of the digital twin, not a detour from it.

## Phases, milestones and validation gates

| Phase | Steps | Milestone: Poltika can reliably answer | Target |
| --- | --- | --- | --- |
| 0. Foundations | 1-2 | (the rules and language every later step obeys) | M0-M2 |
| 1. Executable New Zealand | 3-6 | "What does current New Zealand policy actually do?" | M0-M9 |
| 2. Population and fiscal effects | 7-9 | "Who gains or loses, and what does this cost the Crown?" | M3-M9 |
| 3. Baseline New Zealand | 10-13 | "What happens if policy X changes, and how confident should we be?" | M6-M13 |
| 4. First national system model | 14-16 | Interacting long-term New Zealand trajectories, not isolated policies | M11-M22 |
| 5. Federated New Zealand | 17-20 | An operational national digital twin | M16-M28 |
| 6. Decision intelligence | 21-24 | "Given these objectives and constraints, what feasible trajectories exist?" | M22-M30 |
| 7. National decision infrastructure | 25-28 | Anyone authorised can ask, publicly or programmatically, with every result explained | M26-M34 |
| 8. AI scientific layer | 29-33 | Poltika progressively improves its own representation of New Zealand, under human gates | M30-M38 |

**Every stage has a validation gate.** Poltika doesn't move from "built"
to "trusted" because the code works. Each step's exit gate is a
validation gate, and each phase's milestone is claimed only when
validation evidence shows Poltika can reliably answer its question:

- **Graduation** to a milestone is a decision by Pete, recorded against
  the validation evidence (Step 6). The tolerances are set when each
  milestone is first reached (P18).
- **Demotion.** A milestone can be lost when the evidence stops
  supporting it, and outputs are relabelled.
- **Labels.** Every output carries the validation status of the least
  mature model it relies on.
- **Language follows evidence.** Nothing is described as predictive
  before the ledger's record supports it. Poltika is not called a
  digital twin before Phase 5's milestone.

## The permanent layer

These are not phases. They run through Steps 1-33 for the life of
Poltika, start early, and never have a finished version.

| Capability | Exists now | Established by | Grows into |
| --- | --- | --- | --- |
| Evidence and provenance | Per-result traces, source locators and ranks, data lineage, verified explanations (v0.1.5) | Evidence graph (Step 4) | Behavioural, economic and fiscal edges (Steps 8, 12); public click-through (Step 25); AI explanation through the graph (Step 32) |
| Validation and benchmarking | Spec cases, benchmarks, golden households, v0.2 cross-validation, stored-run code replay | Validation framework (Step 6); conformance suite (Step 5) | Published aggregates (Step 7); historical replay (Step 13); domain integration gates (Step 16) |
| Forward prediction scoring | None | Ledger v0 (Step 6) | Every model registers forecasts; the record behind Phase 5's milestone |
| Uncertainty and model risk | Conditional bounds and population ranges (ADR-0016) | Uncertainty in every quantity (Step 2) | Distributions, model-form uncertainty and global sensitivity (Step 11) |
| Versioning and reproducibility | Code identity, policy file hashes, run ids, result hashes, immutable snapshots, code replay | Model and variable registry versions (Steps 1, 2) | As-of runs (Steps 9, 13); state transition runs (Step 14) |
| Māori data governance | None | Interim rule and sourcing (Step 1) | An agreed process covering microdata (Steps 7, 19) and public outputs (Step 25) |
| Privacy and security | Password-protected pilot; operator-set population; no unit records committed | Secure-environment runner and output checks (Step 7) | Production hardening before public and institutional use (Steps 25, 28) |
| Human oversight | Pete's decisions; independent review; people choose objectives | Constitution (Step 1) | Human gates in the research loop (Step 33) |
| Model governance | Doctrines, independent review, the review queue | Model registry and change control (Step 1) | Diagnosed updates under continuous estimation (Step 18); AI orchestration of validated models only (Step 31) |

Validation scales through the same doctrine. It starts with "does this
WFF spec case produce the legally correct answer?", then asks "can the
household microsimulation reproduce published aggregates?", then
"starting in 2015, can the fiscal model reproduce 2016-2025, given the
shocks that actually happened?", and finally "did the forecast registered
in 2029 land inside its interval?".

## What changes now, and what doesn't

The statutory kernel and the evidence and explainability work stay
exactly where they are. What changes now is that the early architecture
anticipates what later steps need, so v0.x isn't torn apart later. v0.3
adds Phase 0:

- **Evidence classes, model governance and data governance** (Step 1):
  what kind of claim every number is; a registry of models with
  versions, validation status and change control; privacy, security and
  Māori data governance as constraints from the start.
- **The National Variable Registry** (Step 2): one definition for every
  variable, unit, stock or flow, period, geography, population, entity,
  price basis and identifier, before several models each invent their
  own. The shared household model (ADR-0017) is its first full instance.
- **Uncertainty in the data model** (Step 2): every quantity is
  X = (x̂, D_x, E_x), where x̂ is the value, D_x its uncertainty and E_x
  the evidence for it. The types accept intervals and distributions now,
  though distributions are propagated only from Step 11.
- **One dependency graph** (Steps 3 and 4): the household policy graph
  and the evidence graph share node ids.
- **The validation framework's shape** (Step 6): today's tests and
  comparisons become validation cases, so later validation extends them.

## How to read this plan

- **33 steps with Phase 0 foundations and eight delivery phases, in Pete's
  order.** A step's exit gate needs
  the earlier gates, except where a step says it starts early. The
  permanent layer starts in the step named, then grows.
- **Months are targets**, counted from M0 = October 2026 (M3 = January
  2027, M6 = April 2027, M12 = October 2027, M24 = October 2028, M36 =
  October 2029). Steps overlap. Gates and milestones, not dates, decide
  when something is done. The code is rarely the constraint: v0.1 took
  seven calendar days (`docs/research/policy_onboarding_cost.md`).
  Sourcing, independent review and Pete's decisions set the pace.
- **Some things can't be compressed**, whatever the pace:
  - every rate year starts on 1 April; 2027-28 must be in by 1 April 2027
    (M6), and every domain adds a yearly update;
  - a forecast resolves no sooner than its horizon, so a predictive
    record takes calendar time;
  - microdata (IDI) access is an external approval with its own lead
    time;
  - independent human scrutiny, Māori data governance engagement and
    Pete's decisions take the time they take.
- **Owners** follow the working roles: GPT/Codex for sources,
  interpretation and independent review; Claude Code for implementation;
  Pete for decisions and anything that needs a person.
- **Detail matches distance.** Steps 1-10 have tasks with a "done when".
  Steps 11-33 have scope and a gate, and each gets its own detailed plan
  when it starts.

## Where Poltika stands (29 September 2026)

What is already built, against each step. "Partial" means a real part of
the step exists and is reused, not rebuilt.

| # | Step | What exists | State |
| --- | --- | --- | --- |
| 1 | Epistemic constitution and model governance | CLAUDE.md's ground truth; doctrines (deterministic core, LLM boundaries, test, review, IP, scope, development); `calculated`/`unsupported`/`needs_review`, and a missing fact is never zero; source ranks; `review_status`, with `scenario_assumption` for reform values; the caller-asserted fact ledger; independent review and the review queue | Partial. Missing: evidence classes on every output, a precision rule, the AI gate written down, the never-build list, data governance, a model registry and change control |
| 2 | National Variable Registry and common schemas | `CanonicalVariable` (unit, frequency, price basis, stock or flow, geography and population, validity) with 60 registered variables; `Observation` and `Lineage`; the population schema; `DataContext` with vintages; ADR-0017 accepted | Partial: external data only. Missing: engine inputs and outputs, unit, period, entity and geography registries, identifiers, the quantity type, the household model, the state schema |
| 3 | Deterministic statutory kernel | WFF 2026-27 (in-work tax credit `needs_review`) and the Accommodation Supplement, to v0.1's standard; fact catalogues, intake questions and conditional answers (v0.3 Phase 1b, mostly done); reforms as overrides; the source-currency report | Partial: 2 of about 24 domains |
| 4 | Evidence Intelligence and evidence graph | Sources with locators and ranks; rule ids; decision records; traces; provenance reports; verified explanations; evidence coverage check; data lineage | Partial: forward, per result. Missing: the graph, reverse queries, click-through |
| 5 | Legislation conformance suite | Spec cases (WFF 23, AS 26, interaction 5), benchmarks, 9 golden households, golden traces, 100+ explanation fixtures, statutory-value guard, properties, shared-fact contradiction checks | Partial. Missing: per-rule matrix with boundary and contradiction classes, portable fixtures, harness, publication |
| 6 | Validation framework and prediction ledger v0 | The three test classes; v0.2 cross-validation against IRD and MSD (untuned); code replay; immutable snapshots under a CI guard | Partial. Missing: a common framework, scoring, the ledger |
| 7 | Household microsimulation engine | v0.2, ready to tag: synthetic development population, reforms, distributional and fiscal tables, withdrawal rates, sweeps, cross-validation, population ranges, `/microsim` | Partial: development grade |
| 8 | Fiscal and shared accounting spine | Static annual cost per component with coverage; stored scenarios; the scaling model | Minimal |
| 9 | Historical NZ State Store | Five Stats NZ snapshots; `DataContext.get(variable, on, vintage)` | Minimal |
| 10 | National Baseline Engine | None | None |
| 11 | Uncertainty and sensitivity framework | Conditional bounds, population ranges, deterministic sweeps | Minimal |
| 12 | Causal Evidence Library | Discovery and Hypothesis placeholders; the promotion gate | None |
| 13 | Historical Validation Laboratory | v0.2's one-year cross-validation | Minimal |
| 14 | National State Transition Engine | None | None |
| 15 | Canonical NZ Scenario Library | Deterministic reforms and sweeps (not scenarios in this sense) | None |
| 16 | Priority domain models | None | None |
| 17 | Federated Model Graph | ARCHITECTURE.md's module contract, with an empty `dependencies` field | None |
| 18 | Continuous State Estimation | The currency report flags rule changes (for rules only) | None |
| 19 | Synthetic Population Programme | v0.2's synthetic development population and its calibration report | Minimal |
| 20 | Spatial and physical twin | AS areas as a policy geography | None |
| 21 | Cost-of-delay engine | None | None |
| 22 | Value-of-information engine | The intake planner ranks missing facts by impact: the household-scale version | None |
| 23 | Policy-space search and inverse solver | Deterministic sweeps (not search) | None |
| 24 | Pareto frontier engine | None | None |
| 25 | Public NZ Futures Laboratory | Internal analyst pages; a password-protected hosted pilot | None |
| 26 | Policy and manifesto analysis interface | None | None |
| 27 | Constraint-based negotiation sandbox | None | None |
| 28 | Research and institutional APIs | The FastAPI routes (internal, password-protected when hosted) | Minimal |
| 29 | Natural-language policy interface | `doctrine/llm_boundaries.md`; the intake page limits any LLM to phrasing catalogue questions | None |
| 30 | AI hypothesis discovery | The promotion gate | None |
| 31 | AI model orchestration | None | None |
| 32 | AI explanation and research agent | Deterministic explanations verified against the calculation (`verify()`) | Minimal |
| 33 | Autonomous research loop, with human gates | None | None |

## Schedule

| Phase | # | Step | Target | Release |
| --- | --- | --- | --- | --- |
| 0 | 1 | Epistemic constitution and model governance | M0-M1 | v0.3 |
| 0 | 2 | National Variable Registry and common schemas | M0-M2, then grows | v0.3 |
| 1 | 3 | Deterministic statutory kernel | M0-M9, then yearly | v0.3 (Tier 1), then v0.4-v0.6 |
| 1 | 4 | Evidence Intelligence and evidence graph | M1-M4, then grows | v0.4 |
| 1 | 5 | Legislation conformance suite | M1-M4 | v0.3 (Tier 1 matrix), v0.4 |
| 1 | 6 | Validation framework and prediction ledger v0 | M2-M4; ledger live by M3 | v0.4 |
| 2 | 7 | Household microsimulation engine | M3-M7; IDI when granted | v0.5 |
| 2 | 8 | Fiscal and shared accounting spine | M4-M8 | v0.5 |
| 2 | 9 | Historical NZ State Store | M5-M9 | v0.5 |
| 3 | 10 | National Baseline Engine | M6-M10 | v0.6 |
| 3 | 11 | Uncertainty and sensitivity framework | M7-M10 | v0.6 |
| 3 | 12 | Causal Evidence Library | M8-M12, then continuous | v0.7 |
| 3 | 13 | Historical Validation Laboratory | M9-M13 | v0.7 |
| 4 | 14 | National State Transition Engine | M11-M14 | v1.x |
| 4 | 15 | Canonical NZ Scenario Library | M12-M14, then grows | v1.x |
| 4 | 16 | Priority domain models | M13-M22, one at a time | v1.x, v2.0 |
| 5 | 17 | Federated Model Graph | M16-M24 | v2.x |
| 5 | 18 | Continuous State Estimation | M18-M24 | v2.x |
| 5 | 19 | Synthetic Population Programme | M9-M28, paced by microdata access | v2.x |
| 5 | 20 | Spatial and physical twin | M18-M28 | v3.0 |
| 6 | 21 | Cost-of-delay engine | M22-M24 | v3.x |
| 6 | 22 | Value-of-information engine | M23-M26 | v3.x |
| 6 | 23 | Policy-space search and inverse solver | M25-M29 | v4.0 |
| 6 | 24 | Pareto frontier engine | M26-M30 | v4.0 |
| 7 | 25 | Public NZ Futures Laboratory | M26-M30 | v5.0 |
| 7 | 26 | Policy and manifesto analysis interface | M28-M31 | v5.x |
| 7 | 27 | Constraint-based negotiation sandbox | M29-M32 | v5.x |
| 7 | 28 | Research and institutional APIs | M27-M34 | v5.x |
| 8 | 29 | Natural-language policy interface | M30-M32 | v6.0 |
| 8 | 30 | AI hypothesis discovery | M31-M34 | v6.x |
| 8 | 31 | AI model orchestration | M32-M35 | v6.x |
| 8 | 32 | AI explanation and research agent | M32-M35 | v6.x |
| 8 | 33 | Autonomous research loop, with human gates | M34-M38, then continuous | v6.x |

Three things start before their place in the order. The prediction ledger
(Step 6) starts early so the clock on an external track record starts
early. Uncertainty representation starts in Phase 0 (Step 2) so no later
model is built on an implicit assumption of point values. The Synthetic
Population Programme (Step 19) starts early, with the microdata access
application, because its lead time is external.

---

# Phase 0: Foundations

## Step 1: Epistemic Constitution and Model Governance (M0-M1)

The rules Poltika must always obey: fact against rule against estimate
against assumption against scenario; provenance; reproducibility;
uncertainty; model-change controls; Māori data governance; privacy and
security; and the principle that AI can never become an unsourced source
of truth.

- **1.1 — Claude Code drafts, Pete approves.
  `doctrine/epistemic-constitution.md`.**
  - The eight evidence classes:
    - **Fact:** a directly sourced observation;
    - **Rule:** deterministic law, regulation or accounting identity;
    - **Estimate:** an empirically estimated relationship;
    - **Transferred estimate:** evidence borrowed from another
      population or country;
    - **Assumption:** something we don't know;
    - **Scenario:** a deliberately chosen hypothetical;
    - **Model output:** a calculated consequence;
    - **AI hypothesis:** generated for investigation, never
      automatically promoted to fact.
  - Every quantity is X = (x̂, D_x, E_x), carrying eleven fields: value,
    unit, reference period, geography, population, source, method,
    evidence class, uncertainty, model version, dependencies.
  - The four non-negotiables: no result without provenance; no false
    precision; no AI-generated claim enters a model without validation;
    no model expansion without tests.
  - People choose objectives. Poltika holds no default or hidden
    objective, and scores no party or plan.
  - The never-build list ("What Poltika never builds").
  - A mapping from today's concepts to the classes (for example, P2: a
    caller-asserted household fact is a Scenario input).

  *Done when:* Pete has approved it and CLAUDE.md's "Ground truth"
  points to it.
- **1.2 — Claude Code, GPT/Codex reviewing. The AI gate.** AI is never an
  unsourced source of truth. Everything Claude Code or GPT/Codex drafts
  (sources, specifications, values, interactions, estimates) is an AI
  hypothesis until it has a cited primary source and an independent
  review, and, for protected values and interpretations, Pete's decision.
  *Done when:* the constitution names the gate for each kind of
  artifact, and each gate is enforced by an existing or new check.
- **1.3 — Claude Code. The precision rule (P3).** A single household's
  Rule output keeps the precision the law sets. Population, baseline and
  estimate-dependent figures are shown to three significant figures with
  their range. Stored values keep full precision. It is implemented with
  the quantity type (2.6).
- **1.4 — Pete, with the people Pete engages; GPT/Codex sources. Māori
  data governance, privacy and security as architecture.**
  - From the [Algorithm Charter for Aotearoa New Zealand](https://www.data.govt.nz/toolkit/data-ethics/government-algorithm-transparency-and-accountability/algorithm-charter), the Privacy Act
    2020, Stats NZ's microdata and IDI rules and published Māori data
    governance frameworks, record the constraints Poltika must meet.
  - Record who decides about Māori data and outputs about Māori, which
    disaggregations need that decision, confidentiality, security, and
    human oversight.
  - The interim rule (P5) holds until then: no output disaggregated by
    ethnicity or iwi.

  *Done when:* `doctrine/data-governance.md` records each constraint
  with its source, and a test enforces the interim rule.
- **1.5 — Claude Code drafts, Pete approves. Model governance**
  (`doctrine/model-governance.md` and a model registry; location set in
  REPOSITORY_STRUCTURE.md by this task).
  - Every model and engine has a registry entry: the WFF and AS engines,
    the combined runner and the population runner now, then every later
    model. Each entry records:
    - id, version, owner and purpose;
    - its validation status, linked to its validation cases (Step 6);
    - the evidence classes it consumes;
    - known limitations and model risks;
    - a change log.
  - Model-change controls: every material change to a rule, parameter,
    relationship or engine has a change record (what changed, why, the
    evidence, the validation re-run, the approval). Nothing changes
    silently.
  - Model cards: methods, validation, limitations and known failure
    modes, generated from the registry and validation reports.
  - Validation gates, graduation, demotion, labels and language, as in
    "Phases, milestones and validation gates".

  *Done when:* every existing engine has an entry and a card, and CI
  fails on an engine without one.
- **1.6 — Claude Code. Mechanical never-build checks.** A release-gate
  row checks that every population result carries its grade, that no
  output schema scores or ranks a party or plan, and that no
  user-facing page claims a milestone Poltika hasn't reached (for
  example, "digital twin" before Phase 5's).
- **1.7 — Claude Code. An `evidence-classes` skill**, so every later task
  applies the constitution the same way.

**Validation gate:** the constitution, model governance and interim data
governance are approved; every existing engine is registered with its
validation status and a card; the interim governance rule and the
mechanical checks run in CI.

## Step 2: National Variable Registry and Common Schemas (M0-M2, then grows)

Poltika's canonical language for New Zealand: variables, units, stocks
and flows, time periods, geography, populations, entities, price bases
and identifiers. It starts small and expands continuously, and is never
finished.

- **2.1 — Claude Code, GPT/Codex reviewing. The registry covers every
  variable a model reads or writes,** not only external data. It extends
  `semantics/variables.py`'s `CanonicalVariable` and dictionary with:
  - the entity it describes (person, family, household, firm, sector,
    the Crown, New Zealand);
  - stock or flow (`Measure` exists) and price basis (`PriceBasis`
    exists);
  - its unit, period type and geography type, each from 2.2-2.5;
  - its identifier scheme.

  Engine inputs (fact-catalogue entries) and outputs (components) are
  registered alongside the Stats NZ variables.
- **2.2 — Claude Code. Units and price bases.** Each unit has a dimension
  (money, persons, households, ratio, percent) and a price basis. A
  conversion (for example nominal to real) exists only as a named,
  sourced rule with its deflator variable, and is never implicit.
- **2.3 — Claude Code. Time periods.** Tax year, assessment week,
  quarter, calendar year and point in time. A conversion between period
  types is a named rule citing its source. For example, the AS week sits
  inside the WFF year (Task 28.3), and a WFF income can't become an AS
  weekly income without a stated rule (v0.2 D9).
- **2.4 — Claude Code. Populations, entities and identifiers:** person,
  family, household, firm, sector and the Crown, each with an identifier
  scheme. v0.3 keeps one family per household (ADR-0017).
- **2.5 — Claude Code, GPT/Codex sourcing concordances. Geography:** New
  Zealand, regions, statistical areas and AS areas, with dated
  concordances. A geography is never inferred from a name (the AS
  specification forbids inferring an area from "Auckland").
- **2.6 — Claude Code. The quantity type, X = (x̂, D_x, E_x)**, in
  `semantics/`:
  - x̂, the value, at full stored precision;
  - D_x, the uncertainty: `exact`, `interval` (true bounds or points, as
    `Bounds` records), `distribution` (quantiles at least, so any later
    method can report into it), or `unquantified` with a reason;
  - E_x, the evidence: evidence class, sources, method, dependencies and
    model version;
  - plus unit, reference period, geography and population from the
    registry.

  `Observation` with `Lineage`, and `ComponentResult` with its trace, map
  onto it through adapters. The engines don't change.
  *Done when:* every existing output type has an adapter, round-trip
  tests pass, and every result and result id is byte-identical.
- **2.7 — Claude Code. The shared household model** (ADR-0017;
  `BUILD_PLAN_v0_3.md` Phase 1) as the registry's first full instance.
  Each household fact is a registered variable.
- **2.8 — Claude Code drafts, GPT/Codex reviewing. State schema v0:** the
  first version of `NZState` (Step 14), the registered stocks that define
  New Zealand's state S_t, and the flows between S_t and S_t+1. Version 0
  covers what the kernel, microsimulation and spine use, and it grows
  with each step.
- **2.9 — Claude Code. Every shown or stored number is a quantity.**
  Every figure the API returns carries its quantity, and every stored run
  can produce its quantities, without changing stored results. A
  response with an unclassed number is refused, as a failing `verify()`
  is. The precision rule (1.3) applies to what is shown.
- **2.10 — Claude Code. Registry checks.** CI fails on a variable used in
  code but not registered, or on a unit or period mismatch in a mapping.

**Validation gate:** every number any engine reads or writes is a
registered variable with its unit, period, entity and geography; every
output is a quantity with D_x and E_x; state schema v0 is defined.

---

# Phase 1: Executable New Zealand

**Milestone:** Poltika can reliably answer "What does current New Zealand
policy actually do?", for the domains it covers.

## Step 3: Deterministic Statutory Kernel (M0-M9, then yearly)

New Zealand legislation and policy rules as executable logic. Given
household state, a date and policy settings, Poltika returns the legally
correct result, explains exactly why, and names what is uncertain or
missing. It started with WFF and the Accommodation Supplement. Each
domain follows the `new-policy` skill's five PRs, and is born with its
fact catalogue, its registry entries (Step 2), its conformance matrix
(Step 5) and its model-registry entry (Step 1.5). Each carries a yearly
update line (W5.4).

**Lanes:**

- **3A — Income tax and the core benefits, M0-M3.** `BUILD_PLAN_v0_3.md`
  unchanged:
  - Phase 0 scoping;
  - the rest of Phase 1b (1b.2c candidate values, 1b.3e, and GPT/Codex's
    monotone declarations);
  - Phase 2, income tax;
  - Phase 3, Jobseeker Support, Sole Parent Support and Supported
    Living Payment;
  - Phase 4, the dependency graph, whose nodes share ids with the
    evidence graph (Step 4);
  - Phase 5, disposable income and effective marginal tax rates.

  Phase 1, the household model, is Step 2.7.
- **3B — Dates.**
  - Multi-year parameters, M1 (W8, v0.1.6 Task 4.3).
  - The 2027-28 year, M4-M6 (v0.1.6, calendar-bound).
  - Historical years for the state store and replays (Steps 9 and 13),
    sourced with each domain once P11 sets the horizon.
- **3C — Next major systems, M2-M6,** in the direction's order:
  - NZ Superannuation;
  - childcare support (Childcare and OSCAR Subsidies);
  - KiwiSaver interactions;
  - Paid Parental Leave, early because Best Start already reads it
    (WFF-06).
- **3D — Other major household systems, M4-M8:**
  - student support (Student Allowance, student loan repayment);
  - ACC levies and ACC earnings compensation;
  - Temporary Additional Support;
  - Disability Allowance;
  - other MSD assistance;
  - Child Support.
- **3E — Taxes and classifications the spine needs, M5-M9:**
  - GST: the statute is a Rule, but a household's spending is a Fact or
    an Estimate from survey data, and scoping says which;
  - company tax, which needs a firm state in the registry, with the
    Longitudinal Business Database as its real-data target;
  - other tax regimes (PIE, RWT and trust tax);
  - selected regulatory costs (chosen at scoping);
  - Crown revenue and expenditure classifications: every kernel output
    gets a payer and a payee, for Step 8.

About 22 domains remain to add. At 5-8 PRs each (W2.6) that is roughly
110-180 PRs, with sourcing kept one domain ahead of implementation
(W2.4).

**Validation gate:** the kernel household (`BUILD_PLAN_v0_3.md`, "Exit
gate") runs to disposable income for every sourced year, and every
domain passes its conformance matrix and independent review.

## Step 4: Evidence Intelligence and Evidence Graph (M1-M4, then grows)

Every rule, parameter and assumption connected to its source, effective
period, evidence class and downstream dependencies. It began with v0.1.5
and grows for the life of Poltika. Pete sees it as the first product
Poltika could sell (P8).

- **4.1 — Claude Code. Graph schema.**
  - Node kinds:
    - LAW (source and provision);
    - DECISION;
    - RULE;
    - PARAMETER (value and effective period);
    - VARIABLE (a registry entry);
    - FACT (catalogue entry);
    - CALCULATION (step template, component);
    - HOUSEHOLD (record);
    - RESULT (component result, run);
    - DATASET and OBSERVATION;
    - ASSUMPTION;
    - MODEL (a model-registry entry);
    - VALIDATION CASE and LEDGER ENTRY.
  - Reserved for later steps: BEHAVIOURAL RESPONSE (Step 12), ECONOMIC
    EFFECT (Steps 10, 16), FISCAL EFFECT (Step 8).
  - Every edge carries source id, locator, evidence class and review
    status. Node ids are shared with the household dependency graph (3A).
- **4.2 — Claude Code. Built from what exists, never by hand:** sources,
  specification rule tables, `policy.yaml`, decisions, fact catalogues,
  the variable and model registries, traces, run records and data
  manifests. A test rebuilds the graph and compares.
  *Done when:* every node a golden household's result touches is in it.
- **4.3 — Claude Code. Queries in both directions.** "What does this
  figure rest on", down to the law. "What rests on this", for every
  result, stored run, validation case and ledger entry that depends on a
  source, parameter, decision, assumption, dataset or model version.
  *Done when:* a property test shows both directions agree on every
  golden household and a population run.
- **4.4 — Claude Code. Change impact.** A currency-report finding, a
  `review_status` change, a new data vintage or a model change lists what
  it affects, and which validation cases must re-run.
- **4.5 — Claude Code. Click-through** from any figure to its law and
  evidence, and from any assumption to what depends on it, in the API and
  the analyst page.
- **4.6 — GPT/Codex. Completeness review:** no rule, parameter or
  decision in a specification is missing from the graph.

**Validation gate:** a reader reaches the law and evidence behind any
figure Poltika shows, and Poltika lists everything a given assumption or
model version affects. Both are tested.

## Step 5: Legislation Conformance Suite (M1-M4)

Sourced golden cases, boundary cases, contradiction tests and regression
fixtures, for every encoded rule. Eventually the specifications and test
fixtures are published as an independent executable standard.

- **5.1 — Claude Code. A coverage matrix per rule id:**
  - golden: hand-calculated from sources;
  - boundary: each threshold and date boundary, one unit either side;
  - contradiction: inconsistent inputs refused or flagged, an asserted
    fact that contradicts a calculated one, and two rules that would give
    different answers;
  - regression: golden traces.

  CI fails on a rule with a missing class, unless the gap is named and
  Pete has accepted it.
- **5.2 — GPT/Codex. Backfill WFF and the Accommodation Supplement,**
  hand-calculating the missing cases through the test doctrine. The
  `new-policy` skill adds the matrix, so every later domain starts
  complete.
- **5.3 — Claude Code. Portable fixtures.** An implementation-independent
  format using registry variable ids: inputs, a date and policy settings;
  expected outcome, value, reason code and rule ids. It has a JSON Schema,
  is versioned with the specification and is generated from the YAML,
  and a test round-trips it.
- **5.4 — Claude Code. The harness.** It runs any calculator through a
  thin adapter against the fixtures and writes a conformance report.
  Poltika is its first subject, reached only through the harness.
- **5.5 — Pete (P6), GPT/Codex checking the IP Doctrine. Publication as
  an independent executable standard:** what is published
  (specifications and fixtures, not necessarily the implementation),
  under which licence, where, and how it is versioned.

**Validation gate:** every kernel rule has all four classes or an
accepted, named gap, and the published package certifies Poltika through
the harness alone.

## Step 6: Validation Framework and Forward Prediction Ledger v0 (M2-M4)

The machinery for benchmark comparisons, model scoring and immutable
ex-ante predictions, established before Poltika builds impressive models.
The ledger begins small and grows with Poltika.

- **6.1 — Claude Code. The validation case.** One schema for every
  validity claim:
  - the claim, and the step or milestone it supports;
  - the target, as a registered variable and period;
  - the reference: a Fact, a hand calculation or an official figure,
    with its source;
  - the tolerance, and why it is that;
  - the model id and version;
  - the result and its date.

  Existing checks become validation cases without changing: spec cases
  and benchmarks, v0.2's cross-validation, and stored-run replay.
- **6.2 — Claude Code. Model scoring.** Validation reports per model set
  its validation status in the model registry, and are the evidence for
  each gate and milestone.
- **6.3 — Claude Code. Benchmark comparators.** Naive baselines (last
  value, trend, seasonal naive) are computed beside every validation
  against history and every forecast, so skill is always measured against
  something simple. Statistical and government benchmarks join in Step
  13.
- **6.4 — Claude Code. Ledger v0.**
  - Each entry records:
    - id and registration timestamp;
    - target: a registered variable, with its definition, unit,
      geography, population and period;
    - the resolution source, named in advance;
    - the forecast as an interval or distribution (D_x), never a point
      alone;
    - naive baselines;
    - model id and version, and its validation status;
    - data cutoff and run id.
  - Entries are append-only. A CI guard, like the data-snapshot guard,
    refuses edits, and resolutions and diagnoses are appended records.
  - Entries are registered publicly with a third-party hash timestamp
    (P7).
  - Scoring: calibration, bias, mean absolute error, Brier scores and
    interval coverage, by model, horizon and against baselines. The
    report is generated and published, misses included.
- **6.5 — Pete picks, Claude Code registers. First entries,** as soon as
  Poltika produces a genuinely predictive output, and not before. They
  are small, testable predictions, such as a published administrative
  figure predicted before its release (P7).

**Validation gate:** every existing test and comparison is a validation
case in one framework, each model's report sets its status, and the
ledger accepts, freezes, timestamps and scores entries. Phase 1's
milestone is then claimed for the covered domains, on this evidence.

---

# Phase 2: Population and Fiscal Effects

**Milestone:** Poltika can reliably answer "Who gains or loses, and what
does this cost the Crown?"

## Step 7: Household Microsimulation Engine (M3-M7; IDI when granted)

From individual households to representative New Zealand populations and
distributional analysis, without presenting a synthetic population as
reality.

- **7.1 — Pete. Tag `v0.2.0`.** It is ready (`BUILD_PLAN_v0_2.md` 10.3).
- **7.2 — Claude Code, criteria from P4. A confidence grade on every
  population and run:**
  - **Development:** today's independent-marginals population, not an
    estimate for New Zealand;
  - **Public-data (MODERATE);**
  - **IDI-calibrated (HIGHER).**

  A grade is assigned only when its criteria pass. It is never inferred.
- **7.3 — Claude Code, reviewed by GPT/Codex. Public-data calibration**
  (W3.6) to published cross-tabulations, graded Public-data only if P4's
  criteria pass. The longer programme of realistic synthetic households
  and firms is Step 19.
- **7.4 — Claude Code. Validation against published aggregates,** as
  validation cases.
- **7.5 — Claude Code.** Each kernel domain's facts join the population
  as the domain lands.
- **7.6 — Claude Code. Secure-environment runner, output checks and
  survey adapter** (`BUILD_PLAN_v0_3.md` Phase 6; W3.3-W3.5), with Step
  1.4's constraints enforced at export.
- **7.7 — GPT/Codex, then Pete. IDI and Longitudinal Business Database
  access** (W3.1-W3.2, P12). Start at M0, because the lead time is
  external.
- **7.8 — Claude Code.** Results by decile, household type, area and age,
  each with coverage and grade.

**Validation gate:** a Public-data population runs the whole available
kernel, reproduces the published aggregates it is checked against within
stated tolerances, and carries its grade. The secure runner passes its
tests, and the access application is lodged.

## Step 8: Fiscal and Shared Accounting Spine (M4-M8)

Households, the Crown, firms, the financial sector and eventually the
external sector, connected through consistent stocks and flows with
accounting invariants. A dollar cannot disappear: if government pays
$1b, some other sector receives $1b, before behaviour.

- **8.1 — GPT/Codex. Source the classifications** from Treasury's
  publications, with decision records where ambiguous:
  - Crown revenue and expense lines;
  - balance-sheet items;
  - net core Crown debt;
  - the NZ Super Fund.
- **8.2 — Claude Code. Sector accounts in the state schema (2.8):**
  households, firms, government, the financial sector and the rest of
  the world. The last two are defined now and populated later.
  - Every flow has a payer and a payee.
  - Stocks change only through flows and stated revaluations.
  - The invariants are property tests: flows net to zero across sectors,
    balance sheets reconcile, and no unbalanced entry is accepted.
- **8.3 — Claude Code. Crown accounts on the spine:**
  - revenue and expenditure;
  - operating balance;
  - assets and liabilities;
  - debt and debt servicing;
  - the NZ Super Fund.
- **8.4 — Claude Code.** Map every kernel output to its Crown line and
  household flow (lane 3E).
- **8.5 — Claude Code. Multi-year scenarios** (ADR-0015's v0.4 scope):
  identity, baseline, interventions, timing, phasing, indexation,
  packages, persistence, comparison and deterministic run ids.
- **8.6 — Claude Code drafts, Pete decides (P10). The batch engine**
  (W4.2 prototype, W4.3 ADR) by M4, before multi-year population runs.
  The per-household engine stays the reference.
- **8.7 — Claude Code. Static fiscal scoring:** a reform through weighted
  household changes to Crown flows by year, then to the operating balance
  and debt. Results are labelled static and explained through the
  evidence graph.
- **8.8 — Claude Code. Reconciliation with the Crown's published
  statements,** as validation cases.

**Validation gate:** a multi-year reform is scored statically, with
household, distributional, Crown line and debt effects, and every
invariant holds. The accounts reconcile with published Crown figures
within stated tolerances.

## Step 9: Historical NZ State Store (M5-M9)

Versioned snapshots of New Zealand's historical economic, demographic,
fiscal and eventually physical state, built on the variable registry.

- **9.1 — Claude Code, GPT/Codex reviewing the mappings. Connectors** for
  Stats NZ, Treasury and agency publications beneath the data layer.
  Scheduled refreshes propose new vintages for review.
- **9.2 — Claude Code. State snapshots:** for each past period, S_t under
  the state schema, per vintage. Snapshots are immutable, and each value
  is a quantity with its lineage.
- **9.3 — Claude Code. As-of queries:** S_t as it was known on a given
  date, for replays (Step 13) and ledger scoring (Step 6).
- **9.4 — Claude Code. Gaps are explicit.** A missing state variable is
  labelled missing, never filled silently. An imputed one is an
  assumption, with its method.
- **9.5 — Claude Code. Validation:** the store reproduces its sources
  exactly, as validation cases.

**Validation gate:** for every year in the horizon (P11), the store
returns S_t with lineage, as known at any vintage date, and reproduces
its sources. With Steps 7 and 8, this is the evidence for Phase 2's
milestone.

---

# Phase 3: Baseline New Zealand

**Milestone:** Poltika can reliably answer "What happens if policy X
changes, and how confident should we be?". This is v1.0.

## Step 10: National Baseline Engine (M6-M10)

Internally consistent reference trajectories for population, economy and
Crown finances.

- **10.1 — Claude Code. Population engine:** age, sex, fertility,
  mortality and migration by cohort, and household formation, starting
  from the state store's latest S_t. Default assumptions come from Stats
  NZ's published projections, and its benchmark is reproducing them.
- **10.2 — GPT/Codex, then Claude Code. Economy as exogenous, sourced
  Assumptions with ranges:** GDP, productivity, employment, wages,
  inflation, interest rates and trade, from official publications.
  Poltika does not forecast them here.
- **10.3 — Claude Code. Crown baseline** as transparent accounting on the
  spine:
  - revenue from demography, participation and wages;
  - health, education and NZ Super;
  - transfers and debt servicing;
  - capital expenditure.
- **10.4 — Claude Code, GPT/Codex reviewing. Reproduce He Tirohanga
  Mokopuna 2025's unchanged-policy projection.** Swap Poltika's
  assumptions for Treasury's one at a time, and report each one's
  contribution and the unexplained residual: "Treasury produces X.
  Poltika produces Y. The difference comes from assumptions A, B and C."
- **10.5 — Claude Code. Uncertainty that grows with the horizon,** at
  least from Treasury's published alternative assumptions, carried in
  D_x. No long-horizon figure is shown as a point alone.

**Validation gate:** the baseline to 2065 is internally consistent (every
accounting invariant holds), and it reproduces He Tirohanga Mokopuna 2025
within a stated tolerance or attributes every difference to named
assumptions.

## Step 11: Uncertainty and Sensitivity Framework (M7-M10)

The data model has carried D_x since Step 2. This step propagates it,
before behavioural and domain complexity arrives:

- parameter distributions and confidence ranges;
- scenario uncertainty;
- model-form uncertainty: where two defensible model structures give
  different answers, both are run and the spread is reported;
- correlated uncertainties, stated as assumptions;
- one-way, multi-parameter and global sensitivity: which assumptions
  drive which results;
- seeded Monte Carlo on the batch engine (P10), with interval arithmetic
  where it is exact.

Model cards (Step 1.5) gain each model's uncertainty treatment.

**Validation gate:** every material result from the kernel, population,
spine and baseline has a propagated interval and a ranked list of the
assumptions that drive it, and stated intervals cover history at their
stated rates (Step 13).

## Step 12: Causal Evidence Library (M8-M12, then continuous)

Poltika's machine-readable library of behavioural relationships, each
explicitly classified:

| Class | Constitution class |
| --- | --- |
| `NZ_CAUSAL` | Estimate |
| `NZ_OBSERVATIONAL` | Estimate, flagged as not causal |
| `INTERNATIONAL_TRANSFERRED` | Transferred estimate |
| `EXPERT_ASSUMPTION` | Assumption, naming the expert judgement |
| `SCENARIO_ASSUMPTION` | Scenario |

- Each entry records the relationship (exposure to outcome) in
  registered variables, the estimate with its D_x, population and period,
  method, class, external validity, sources, and when it was last
  reviewed and by whom.
- A transfer protocol records what is needed to use another population's
  estimate.
- First entries are what Step 14's transition functions and the first
  domain need, from published studies, each reviewed. None comes from
  model memory.
- AI-proposed and discovered relationships enter only through `Discovery
  → Hypothesis → evidence → validation → human approval → model
  specification → tests → Simulator` (Step 30 is the AI intake).
- Behavioural scoring is always shown beside the static result.
- Poltika's own estimates (difference in differences, synthetic control,
  regression discontinuity, instrumental variables, matching, structural,
  Bayesian) are reviewed studies, with a design registered in the ledger
  before analysis.

**Validation gate:** every behavioural relationship in use is in the
library with its class, D_x and review, and results show static and
behavioural side by side.

## Step 13: Historical Validation Laboratory (M9-M13)

- **Backcasting:** start at a past date and run forward using only what
  was known then (as-of queries, Step 9).
- **Policy replay:** replay a past reform whose outcomes are published,
  and compare.
- **Shock replay:** reproduce a past period given the shocks that actually
  happened.
- **Benchmarks** against naive, statistical and government models,
  including past official projections.

Scored in the validation framework and never tuned: a tuned parameter is
a model change with its own record.

**Validation gate:** each covered model has published replay and backcast
errors against actuals and benchmarks, failures included. With Steps
10-12 this is the evidence for Phase 3's milestone and v1.0.

---

# Phase 4: First National System Model

**Milestone:** Poltika can simulate interacting long-term New Zealand
trajectories, rather than isolated policies.

## Step 14: National State Transition Engine (M11-M14)

S_t → S_t+1, with an explicit `NZState` containing population,
households, economy, the Crown, housing, health, infrastructure and more,
built from the state schema (Step 2.8). This is where Pete finds MIT's
Andorra architecture most relevant.

- Transition functions per subsystem, each simple and explicit, with
  relationships from the causal library or stated assumptions.
- A contract per transition function, so a domain model (Step 16) can
  replace it later without changing the rest.
- Multi-year trajectories from the latest observed S_t, keeping every
  accounting invariant.
- Validated by historical replay (Step 13), with forecasts registered in
  the ledger.

**Validation gate:** an integrated multi-year trajectory runs with every
invariant holding, and replays history at least as well as naive
benchmarks.

## Step 15: Canonical NZ Scenario Library (M12-M14, then grows)

Standard, versioned scenarios every analysis can compare against: a
reference scenario, low and high productivity, demographic pressure,
global shocks, infrastructure constraints, technology upside and others.
Each is a set of stated Scenario assumptions over registered variables,
with its sources and rationale. It changes only through a recorded,
versioned change.

**Validation gate:** each scenario runs through the transition engine
with every invariant holding, and is documented, versioned and
reproducible.

## Step 16: Priority Domain Models (M13-M22, sequentially)

Specialised models built one after another, never all at once. P13 orders
them by national importance × tractability × available evidence. The
likely early domains:

- NZ Super and ageing;
- health;
- housing and land;
- labour and migration;
- productivity and capital;
- infrastructure;
- energy;
- trade.

Each uses the method that fits it:

| Domain | Method |
| --- | --- |
| Health | Microsimulation |
| Housing | Spatial, econometric and agent-based hybrid |
| Electricity | Optimisation and network model |
| NZ Super | Overlapping generations and microsimulation |
| Transport | Network model |
| Macro | Structural, econometric and stock-flow consistent hybrid |

**Each domain earns integration through validation:** it replaces or
refines a transition function only when it does better in historical
replay than the function it replaces, has forecasts registered and has
classified relationships.

---

# Phase 5: Federated New Zealand

**Milestone:** an operational national digital twin. This is where Pete
would be comfortable calling Poltika one, and not before.

## Step 17: Federated Model Graph (M16-M24)

Validated domain models connected through the National State and the
accounting spine:

```text
                NZ STATE
                   │
      ┌────────────┼────────────┐
      ↓            ↓            ↓
   Fiscal      Households      Macro
      ↕            ↕            ↕
   Health ←→ Housing ←→ Labour
      ↕            ↕            ↕
   Ageing ←→ Infrastructure ←→ Energy
      │            │            │
      └────────────┼────────────┘
                   ↓
          ACCOUNTING SPINE
```

Each model keeps its contract. Invariants hold across models, conflicting
outputs are refused as contradictions, and coupled runs check
convergence.

**Validation gate:** the federated models run coupled, keep every
invariant, and reproduce history at least as well as separately.

## Step 18: Continuous State Estimation (M18-M24)

New observations are continuously reconciled with Poltika's estimate of
New Zealand's current state, using statistical and Bayesian methods
suited to each part of the state.

- Each resolved ledger miss gets a diagnosis: the prediction failed
  because X; the candidate explanations are A, B and C; the evidence
  supports B.
- Each parameter or model change is a reviewed change record ("parameter
  changed from X to Y").
- Historical predictions stay frozen.

**Validation gate:** the current-state estimate updates on each new
vintage with its uncertainty, and one full cycle of observe, forecast,
error, diagnosis and approved update is on record.

## Step 19: Synthetic Population Programme (M9-M28, paced by microdata access)

Increasingly realistic synthetic households and firms, ultimately
supported by strong enough microdata and governance, rather than
pretending public marginal distributions are adequate.

- Joint distributions calibrated to published cross-tabulations, then to
  IDI and Longitudinal Business Database outputs where access is granted
  and outputs pass their checks.
- Every population carries its grade, and moves up only when its criteria
  pass.
- Governed under Step 1.4 throughout.

**Validation gate:** each population's joint distributions reproduce the
microdata-derived checks they are held against, within stated tolerances,
under the governance agreed in Step 1.4.

## Step 20: Spatial and Physical Twin (M18-M28)

Land, housing, infrastructure capacity, transport, energy, water and
regional constraints, added to the state and the federation through the
geography registry (Step 2.5) and the domain models.

**Validation gate:** each physical subsystem reproduces its observed
history and capacity data, and its constraints bind correctly in coupled
runs. With Steps 17-19 and a sustained, published forecast record, this
is the evidence for Phase 5's milestone.

---

# Phase 6: Decision Intelligence

**Milestone:** Poltika can answer "Given these objectives and
constraints, what feasible trajectories exist?"

## Step 21: Cost-of-Delay Engine (M22-M24)

How delaying an intervention changes the size of the future adjustment
needed (P16): scenario families that vary only the start date, with D_x.

**Validation gate:** a cost-of-delay curve for a fiscal question, with its
interval and evidence chain, reproducible from ordinary scenarios.

## Step 22: Value-of-Information Engine (M23-M26)

Which uncertainties matter most, and what further research or data would
most improve a decision. Sometimes the right answer isn't another
simulation. It is "we need better evidence before deciding".

- The expected value of perfect information (EVPI) per uncertain
  parameter, under a stated objective.
- The expected value of sample information (EVSI) for a proposed study.
- A ranked list of the unknowns that most change the decision, linked to
  their causal-library entries.

**Validation gate:** where two options differ mainly through one
parameter, Poltika names it, estimates its EVPI, and gives the EVSI of a
named study design.

## Step 23: Policy-Space Search and Inverse Solver (M25-M29)

Instead of people testing one policy at a time, Poltika searches large
combinations subject to user-defined constraints, and solves inversely
for settings that reach a stated target.

- **Precondition, the causal credibility gate (P14):** every relationship
  the search relies on meets a stated minimum class and has been
  replayed.
- People state the objectives and constraints. Poltika holds no default
  objective.
- Results report the value of information (Step 22) for the parameters
  that separate the options.

**Validation gate:** every candidate the search returns reproduces as an
ordinary scenario.

## Step 24: Pareto Frontier Engine (M26-M30)

Feasible trade-offs, never a single "optimal" political answer: for
example across fiscal sustainability, incomes, distribution, housing and
emissions. Each point on the frontier shows its trade-offs, assumptions,
uncertainty and robustness across D_x.

**Validation gate:** the frontier is reproducible, every point on it runs
as an ordinary scenario, and its robustness across the stated uncertainty
is reported.

---

# Phase 7: National Decision Infrastructure

**Trust gate before any public or institutional use:**

- the milestones its claims rely on are reached;
- production hardening: threat model, penetration test, access control,
  encryption, backups, incident response, monitoring and performance;
- independent scrutiny by specialists in economics, econometrics,
  statistics, public finance, New Zealand policy, Māori data governance
  and security, with criticisms and responses published;
- a published ledger record, misses included.

## Step 25: Public NZ Futures Laboratory (M26-M30)

Interactive public scenario exploration. Every result exposes: why?
source? assumptions? uncertainty? who is affected? what would change the
result? It covers baseline, policy and alternative scenarios to 2030,
2040, 2050 and 2065, across GDP per person, wages, taxes, housing,
health, Crown debt, retirement, distribution, infrastructure and
environmental indicators. No scores and no winners.

**Validation gate:** a person who didn't build Poltika can answer all six
questions for any result.

## Step 26: Policy and Manifesto Analysis Interface (M28-M31)

Common assumptions applied to documented proposals, exposing their
modelled fiscal, economic and distributional consequences without
political scoring.

- A proposal enters only as documented, with its source, and every
  interpretation Poltika had to make is recorded and shown.
- Every proposal is run under the same assumptions and scenario library.
- No score, ranking or winner (the never-build list).

**Validation gate:** each analysed proposal reproduces as ordinary
scenarios, and every interpretation is shown and challengeable.

## Step 27: Constraint-Based Negotiation Sandbox (M29-M32)

Different stakeholders specify constraints, and Poltika identifies the
feasible intersection, using the search and frontier engines (Steps
23-24). It shows where no intersection exists, and which constraints
cause that.

**Validation gate:** every point in a reported intersection satisfies
every stated constraint when run as an ordinary scenario.

## Step 28: Research and Institutional APIs (M27-M34)

Treasury, councils, universities, consultancies and other authorised
users work programmatically with Poltika's models and evidence
infrastructure, under access control, audit logs, usage terms and the
governance constraints of Step 1.4.

**Validation gate:** every API result carries its quantity, evidence
chain and validation status, and access is controlled and audited.

---

# Phase 8: AI Scientific Layer

AI operates the instrument. It isn't the instrument. AI is used
throughout development from the start, but it never becomes the
epistemic foundation.

## Step 29: Natural-Language Policy Interface (M30-M32)

Human questions translated into structured model queries over registered
variables, constraints and scenarios. Every consequential interpretation
is shown and confirmed. `src/poltika/llm/` is built here, under
`doctrine/llm_boundaries.md`.

**Validation gate:** on a benchmark set of questions, every translation is
shown, confirmable, and runs as an ordinary query.

## Step 30: AI Hypothesis Discovery (M31-M34)

AI searches evidence and proposes mechanisms, relationships and research
questions. They enter the causal library's intake as AI hypotheses, and
are never promoted into a model without validation.

**Validation gate:** no AI-proposed relationship reaches a model except
through the promotion gate, and a test proves it.

## Step 31: AI Model Orchestration (M32-M35)

AI selects and coordinates validated models, scenarios, evidence and
simulations, and never an unregistered or unvalidated model.

**Validation gate:** every orchestrated run is reproducible without the
AI, from its recorded plan.

## Step 32: AI Explanation and Research Agent (M32-M35)

Results are explained through the executed model trace and the evidence
graph, never as plausible-sounding explanations written after the fact.
Every figure an explanation shows is checked against the engine output
before it is shown (the `verify()` pattern).

**Validation gate:** every figure and causal claim in an AI explanation
traces to the executed run and the evidence graph.

## Step 33: Autonomous Research Loop, with Human Gates (M34-M38, then continuous)

`Prediction → Observation → Error → Hypothesis → Evidence → Test → Human review → Model update`

Poltika progressively improves its representation of New Zealand. Each
turn is recorded in the ledger and the evidence graph, and no model
changes without a human gate.

**Validation gate:** every model update the loop proposes has a diagnosis,
evidence, a test and a recorded human approval.

---

## Releases

A release is tagged when its steps' gates pass. Milestones are claimed
separately, on validation evidence.

| Release | Steps | Target | Milestone evidence |
| --- | --- | --- | --- |
| v0.1, v0.1.5 | Done | | |
| v0.2 | Ready to tag (7.1) | M0 | |
| v0.1.6 | 3B | By M6 (1 April 2027) | |
| v0.3 | 1; 2; 3A; 5.1 for Tier 1 | M0-M3 | |
| v0.4 | 4; 5; 6; 3C | M2-M6 | Phase 1, for covered domains |
| v0.5 | 7; 8; 9; 3D | M4-M9 | Phase 2 |
| v0.6 | 10; 11; 3E | M6-M10 | |
| v0.7 | 12; 13 | M8-M13 | |
| v1.0 | Gates 1-13, plus the hardening an outside analyst needs | M13 | Phase 3 |
| v1.x | 14; 15; the first domain models | M11-M18 | |
| v2.0 | 16 | M22 | Phase 4 |
| v2.x | 17; 18; 19 | M16-M28 | |
| v3.0 | 20 | M28 | Phase 5 |
| v3.x | 21; 22 | M22-M26 | |
| v4.0 | 23; 24 | M25-M30 | Phase 6 |
| v5.0, v5.x | 25-28 | M26-M34 | Phase 7 |
| v6.0, v6.x | 29-33 | M30-M38 | Phase 8 |

**v1.0 definition (testable).** Phase 3's milestone: for a structured
package of changes inside its supported kernel domains, Poltika answers:

- **what happens:** static results, and behavioural ones where the
  causal library holds a classified relationship;
- **to whom:** by decile, household type, area and age, on a graded
  population;
- **when:** year by year, through the Crown accounts, against the
  national baseline;
- **through what mechanism:** the evidence-graph chain to law and
  evidence;
- **with what confidence:** evidence classes, propagated uncertainty, the
  population grade, validation status, replay errors and the ledger's
  record;
- **compared with what alternatives:** the baseline and other scenarios.

An independent analyst can reproduce and challenge the result without the
builders. A "supported domain" has an approved specification, a complete
conformance matrix, an independent review and current values.

## What changes in the current plans

| Current plan | Under this plan |
| --- | --- |
| `BUILD_PLAN_v0_3.md` | Kept. v0.3 also ships Phase 0 (Steps 1 and 2; its Phase 1 becomes 2.7) and Step 5.1 for Tier 1. The references in its "Not in v0.3" list point here. |
| `BUILD_PLAN_v0_1_6.md` | Kept as lane 3B. The 1 April 2027 deadline stands. |
| `BUILD_PLAN_v0_2.md` | Done. Tag it (7.1). Its population becomes the Development grade. |
| ROADMAP v0.4, scenario engine | Step 8.5, then the scenario library (Step 15) |
| ROADMAP v0.5, uncertainty, assurance and historical baseline | Connectors to Step 9; historical baseline to Steps 9-10; uncertainty to Step 11; backtesting to Step 13; model cards to Step 1.5 |
| ROADMAP v0.6, long-term fiscal model | Step 10, then Step 14. Its constrained search moves to Step 23. |
| ROADMAP v0.7, decision-intelligence product | Evidence APIs and lineage to Step 4; public interface to Step 25; institutional APIs to Step 28; the LLM to Steps 29-32 |
| ROADMAP v1.0 | Redefined as Phase 3's milestone (above) |
| Discovery and Hypothesis | The causal library's intake (Step 12), with AI hypothesis discovery at Step 30 |
| v2-v5 capability tracks | Phases 4-8 |
| The 22-step version's scenario discovery | Not a separate step. Its closest homes are the uncertainty framework (Step 11) and the scenario library (Step 15). |

## Carried workstreams (`ROADMAP_REALIGNMENT.md`)

| Workstream | Under this plan |
| --- | --- |
| W1 Review debt and cadence | The queue and gate rows stay. The cap is suspended (P17). |
| W2 Policy coverage throughput | Step 3. The `new-policy` skill gains registry entries, the conformance matrix, a model-registry entry and evidence classes. |
| W3 Real-data access | Steps 7 and 19, with governance from 1.4 |
| W4 Batch engine | Decided by M4 (P10), before Step 8's multi-year population runs |
| W5 Maintenance budget | Stays. The historical horizon (W5.3) is P11, due at M1. |
| W6 Shared household model | Step 2.7 |
| W7 Household dependency graph | Lane 3A, sharing node ids with Step 4 |
| W8 Multi-year parameters | Lane 3B |
| W9 Roadmap reorder | Superseded by ADR-0019 |
| W10 Coverage map | Extended by lanes 3C-3E, in the direction's order |

## What Poltika never builds

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins" (Step 26
  analyses proposals without scoring them).
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models: every change is a recorded change (Steps
  1.5, 18).
- No point estimate where the uncertainty is large (Steps 1.3, 2.6, 11).
- No synthetic population presented as reality (Steps 7.2, 19).
- No policy search before causal relationships are credible (Step 23's
  precondition).
- No "digital twin" branding before Phase 5's milestone.
- No AI claim promoted into a model without validation (Steps 1.2, 30).
- **Never optimise the model instead of the country.** Ledger and
  validation scores are monitored, never targeted. A change made to
  improve a score needs the same diagnosis record as any other change.

## Decisions

Pete approved the first version of this plan on 29 September 2026
("Approve and proceed all"), then set this master order the same day. The
decisions below carry over, with their step numbers updated.

**Decided 29 September 2026:**

- **P1:** the approach (reconciliation against what's built, month
  targets, releases tagged at gates, v1.0 defined around the question).
  The master order is Pete's own. Its month targets, tasks and release
  mapping are drafted here, and stand unless Pete changes them.
- **P2:** a caller-asserted household fact is a **Scenario** input.
- **P3:** the precision rule (Step 1.3).
- **P4, names:** Development, Public-data (MODERATE) and IDI-calibrated
  (HIGHER). The criteria come with Task 7.2.
- **P5, interim rule:** no output disaggregated by ethnicity or iwi until
  the governance process is agreed. Engaging people with standing in
  Māori data governance is Pete's, and still open.
- **P9:** the kernel follows the direction's order (lanes 3C-3E): NZ
  Super, childcare support and KiwiSaver interactions next, then the
  other major systems.
- **P12:** apply for IDI access. W3.1 documents the route first; lodging
  it is Pete's.
- **P16:** the cost-of-delay definition (Step 21).
- **P17:** the review-debt cap is suspended ("Ignore PR cap"). The review
  queue is still kept.
- **Carried:** ADR-0017, the shared household model, accepted with its
  three recommended answers (`BUILD_PLAN_v0_3.md` D6).

**Open:**

- **P6:** publishing the conformance suite as a standard (Step 5.5).
- **P7:** the timestamping service and the first genuinely predictive
  targets (Steps 6.4-6.5).
- **P8:** Evidence Intelligence as the first product.
- **P10:** the batch engine, by M4.
- **P11:** the historical horizon for the state store and replays, by
  M1.
- **P13:** the domain-model order (Step 16).
- **P14:** the causal credibility gate for policy search (Step 23).
- **P18:** the tolerances for each validation gate and milestone, set
  when each is first reached. Pete decides each milestone on the
  evidence.
- **P19:** state schema v0's scope (Step 2.8).
- **P20:** the scenario library's first set (Step 15).
- **v0.3 D1-D3:** each Tier 1 domain's slice, the disposable-income
  definition and the income-adequacy measures, from Phase 0's sourcing.

## Progress

| Step | State |
| --- | --- |
| Plan | Master order of 33 steps with Phase 0 foundations and eight delivery phases, 29 September 2026 (ADR-0019) |
| 1-33 | As in "Where Poltika stands". Each row is updated as its tasks land. |
