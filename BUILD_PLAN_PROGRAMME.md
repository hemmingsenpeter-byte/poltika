# Poltika programme build plan: the decision instrument

**Date:** 29 September 2026
**Status:** Approved by Pete on 29 September 2026 ("Approve and proceed
all"), with the recommended decisions (ADR-0018). Drafted by Claude Code.
The decisions still open are listed at the end.
**Supersedes:** ADR-0015's release sequence and `ROADMAP_REALIGNMENT.md`
W9. `BUILD_PLAN.md` stays the frozen record of v0.1. `BUILD_PLAN_v0_3.md`
stays the task list for v0.3, which now covers Step 1 and the first tier
of Step 2 ("What changes in the current plans").

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

A digital twin is what many defensible answers add up to. It is not the
starting point. Poltika is not called one until Step 12's gate is met.

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

**Why now:** Treasury's He Tirohanga Mokopuna 2025 projects net core
Crown debt at 200.0% of GDP by 2065 if fiscal policy is unchanged.
Treasury calls this a projection, not a prediction (treasury.govt.nz,
retrieved 29 September 2026). Step 7 reproduces that baseline or explains
where Poltika's differs.

## How to read this plan

- **Twenty steps, in Pete's build sequence.** The step number is the
  dependency order: a step's exit gate needs the earlier gates, except
  where a step says it starts early.
- **Months are targets**, counted from M0 = October 2026 (M3 = January
  2027, M6 = April 2027, M12 = October 2027, M18 = April 2028). Exit
  gates, not dates, decide when a step is done. Steps overlap. The code
  is rarely the constraint: v0.1 took seven calendar days
  (`docs/research/policy_onboarding_cost.md`). Sourcing, independent
  review and Pete's decisions set the pace.
- **Some things can't be compressed**, whatever the pace:
  - every rate year starts on 1 April; 2027-28 must be in by 1 April 2027
    (M6), and every domain adds a yearly update;
  - a forecast resolves no sooner than its horizon, so the ledger's track
    record grows with calendar time;
  - microdata (IDI) access is an external approval with its own lead
    time;
  - independent human scrutiny, Māori data governance engagement and
    Pete's decisions take the time they take.
- **Owners** follow the working roles: GPT/Codex for sources,
  interpretation and independent review; Claude Code for implementation;
  Pete for decisions and anything that needs a person.
- **Detail matches distance.** Steps 1-10 have tasks with a "done when".
  Steps 11-20 have scope and a gate, and each gets its own detailed plan
  when it starts, as every release has.

## Where Poltika stands (29 September 2026)

What is already built, against each step. "Partial" means a real part of
the step exists and is reused, not rebuilt.

| # | Step | What exists | State | What remains |
| --- | --- | --- | --- | --- |
| 1 | Epistemic constitution | CLAUDE.md's ground truth; doctrines (deterministic core, LLM boundaries, test, review, IP, scope); `calculated`/`unsupported`/`needs_review`, and a missing fact is never zero; `FactStatus`; source authority ranks (v0.1.5); `review_status` on every value, with `scenario_assumption` for reform values; the caller-asserted fact ledger (v0.1.5 4.5); `Observation` and `Lineage`; the 11-field snapshot manifest; `run_id`, `results_sha256` and code identity; the synthetic label; `verify()` on every explanation | Partial | One set of evidence classes on every output; unit, geography, population, uncertainty and dependencies on every number; a precision rule (v0.2 reports a synthetic population's cost to the cent); the AI-hypothesis gate written down; the never-build list; data governance constraints |
| 2 | Statutory kernel | WFF 2026-27 (in-work tax credit `needs_review`) and the Accommodation Supplement, each to v0.1's standard; fact catalogues, intake questions and conditional answers (v0.3 Phase 1b, mostly done); reforms as parameter overrides; the source-currency report | Partial: 2 of about 24 domains | v0.3 Phase 0 and Phases 1-5 (income tax, Jobseeker Support, Sole Parent Support, Supported Living Payment, household model, graph, disposable income); multi-year parameters; 2027-28; the other household domains; firms and government |
| 3 | Evidence Intelligence | `sources.yaml` with locators and ranks; rule ids; decision records; traces (`ParameterUse`, `InputUse`, `CalculationStep`); provenance reports; verified explanations; evidence coverage check; data lineage; stored run records | Partial: forward, per result | A queryable graph across all of these; reverse "what does this contaminate" queries; click-through across the chain; the behavioural, economic and fiscal layers |
| 4 | Conformance suite | Spec cases (WFF 23, AS 26, interaction 5), benchmarks, 9 golden households, golden traces, 100+ explanation fixtures, statutory-value guard, Hypothesis properties, shared-fact contradiction checks (Task 28.3) | Partial | A per-rule matrix with boundary and contradiction classes; an implementation-independent fixture format; a harness another calculator can run; publication |
| 5 | Household microsimulation | v0.2, ready to tag: synthetic development population from Stats NZ tables (independent marginals), reforms, deciles, winners and losers, areas, fiscal totals, withdrawal rates, sweeps, cross-validation with IRD and MSD, population ranges, `/microsim` | Partial: development grade | Confidence grades; joint calibration; secure-environment runner (v0.3 Phase 6); IDI access (W3.1-W3.2 not started); governance at export; every kernel domain in the population |
| 6 | Accounting and fiscal spine | Static annual cost per component with coverage (v0.2); stored scenarios (Task 32); the scaling model (W4.1) | Minimal | Sector accounts and stock-flow invariants; Crown accounts; classifications; multi-year scenarios (ADR-0015's v0.4); the batch-engine decision; static fiscal scoring |
| 7 | National baseline | Five Stats NZ snapshots used for calibration | None | Connectors; population engine; macro assumptions; Crown baseline; reproducing Treasury's projection |
| 8 | Causal evidence library | Discovery and Hypothesis placeholders, after v1.0; the promotion gate | None | Registry, transfer protocol, first entries, intake, behavioural scoring |
| 9 | Historical validation laboratory | v0.2's one-year cross-validation (untuned); stored-run code replay | Minimal | Backtest horizon; historical parameter years; as-of runs; scored backtests |
| 10 | Forward prediction ledger | Building blocks only: immutable snapshots under a CI guard, run ids, code identity | None | The ledger, timestamping, first entries, scoring |
| 11 | Domain models | None | None | All |
| 12 | Federated model and state graph | The module contract in ARCHITECTURE.md, with an empty `dependencies` field | None | All |
| 13 | Continuous state estimation | The currency report flags rule changes (a precursor for rules only) | None | All |
| 14 | Uncertainty and sensitivity | Conditional bounds for missing facts (ADR-0016), population ranges, deterministic sweeps | Minimal | Distributions, Monte Carlo, global sensitivity, model cards |
| 15 | Cost of delay | None | None | All |
| 16 | Policy-space optimisation | None (sweeps aren't optimisation) | None | All, behind the causal gate |
| 17 | Value of information | The intake planner ranks missing facts by impact: the household-scale version | None | EVPI and EVSI over model parameters |
| 18 | Public Futures Laboratory | Internal analyst pages; a password-protected hosted pilot | None | All, behind the trust gate |
| 19 | AI reasoning and search interface | `doctrine/llm_boundaries.md`; the intake page restricts any LLM to phrasing catalogue questions | None | All |
| 20 | Continuously improving twin | None | None | All |

## Schedule

| # | Step | Target months | Release |
| --- | --- | --- | --- |
| 1 | Epistemic constitution | M0-M1 | v0.3 |
| 2 | Statutory kernel | M0-M8, then yearly | v0.3 (Tier 1), then v0.4-v0.6 |
| 3 | Evidence Intelligence | M1-M4 | v0.4 |
| 4 | Conformance suite | M1-M4 | v0.3 (Tier 1 matrix), v0.4 (published) |
| 5 | Household microsimulation | M1-M6; IDI when granted | v0.5 |
| 6 | Accounting and fiscal spine | M3-M6 | v0.5 |
| 7 | National baseline | M4-M8 | v0.6 |
| 8 | Causal evidence library | M5-M9, then continuous | v0.7 |
| 9 | Historical validation laboratory | M6-M9 | v0.7 |
| 10 | Forward prediction ledger | Live by M2; grows with every step | v0.4 |
| 11 | Domain models | M8-M16, one at a time | v1.x |
| 12 | Federated model and state graph | M10-M14 | v2.0 |
| 13 | Continuous state estimation | M12-M15 | v2.0 |
| 14 | Uncertainty and sensitivity | M9-M13 (represented from Step 1) | v2.0 |
| 15 | Cost of delay | M13-M14 | v2.0 |
| 16 | Policy-space optimisation | M14-M16 | v3.0 |
| 17 | Value of information | M15-M17 | v3.0 |
| 18 | Public Futures Laboratory | M16-M18 | v4.0 |
| 19 | AI reasoning and search interface | M17-M19 | v4.0 |
| 20 | Continuously improving twin | M19 on | |

Two things start before their place in the order. The prediction ledger
(Step 10) starts early because the direction says to: its value accrues
with calendar time. Uncertainty representation starts early because the
constitution requires every number to carry its uncertainty from Step 1.
Step 14 itself is the full propagation and sensitivity machinery.

---

## Step 1: Epistemic constitution (M0-M1)

Rules no later step may break, written before any further modelling.
Most of their parts exist. This step makes them one system and applies
it to every output.

- **1.1 — Claude Code drafts, Pete approves. `doctrine/epistemic-constitution.md`.**
  - The eight evidence classes, in Pete's words:
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
  - The eleven fields every number carries: value, unit, reference
    period, geography, population, source, method, evidence class,
    uncertainty, model version, dependencies.
  - The four non-negotiables: no result without provenance; no false
    precision; no AI-generated claim enters a model without validation;
    no model expansion without tests.
  - People choose objectives. Poltika holds no default or hidden
    objective, and scores no party or plan.
  - The never-build list ("What Poltika never builds", below).
  - A mapping from today's concepts to the classes, so nothing is
    reinvented:

    | Today | Class |
    | --- | --- |
    | An approved statutory value, rule or rounding | Rule |
    | A `needs_review` value with recorded candidates (1b.2c) | Rule, with each candidate branch an Assumption |
    | A decided interpretation (`decisions/`) | Rule, citing the decision |
    | A caller-asserted household fact | P2 decides (recommended: Scenario) |
    | A reform override (`scenario_assumption`) | Scenario |
    | A Stats NZ or agency figure through `Lineage` | Fact |
    | A population generator rule (D1-D7, A1-A12) | Assumption |
    | A component result or run total | Model output |
    | Specification content drafted by a model, before review | AI hypothesis |

  *Done when:* Pete has approved it and CLAUDE.md's "Ground truth"
  points to it.
- **1.2 — Claude Code. `Quantity` and `EvidenceClass`** in `semantics/`
  (the exact location set in REPOSITORY_STRUCTURE.md by this task). A
  typed record of the eleven fields. Uncertainty is one of: exact (a Rule
  output), interval (with its kind, as `Bounds` has), distribution (Step
  14), or unquantified with a stated reason. `Observation` with `Lineage`
  and `ComponentResult` with its trace map onto it through adapters. The
  engines don't change.
  *Done when:* every existing output type has an adapter, a round-trip
  test passes, and every result and result id is byte-identical.
- **1.3 — Claude Code. Every shown or stored number is classed.** Every
  figure the API returns and every stored run carries or references a
  `Quantity`. A response with an unclassed number is refused, as a
  failing `verify()` is.
  *Done when:* a test walks every route's response and every golden
  household's result and finds no unclassed number.
- **1.4 — Claude Code, rule from P3. No false precision.** A display
  rule per evidence class. Stored values keep full precision, so runs
  still reproduce. v0.2's fiscal summaries and explanations adopt it.
  *Done when:* a test fails on any displayed population figure finer
  than the rule allows, and `run_id` and `results_sha256` are unchanged.
- **1.5 — Claude Code, GPT/Codex reviewing. The AI-hypothesis gate,
  written against today's process.** AI writes most of Poltika
  (Claude Code and GPT/Codex). Its sources, specifications, values,
  interactions and estimates are AI hypotheses until they have a cited
  primary source and an independent review, and, for protected values
  and interpretations, Pete's decision.
  *Done when:* the constitution names the gate for each kind of
  artifact, and each gate is enforced by an existing or new check.
- **1.6 — Pete, with the people Pete engages; GPT/Codex sources. Data
  governance as architecture.** From the Algorithm Charter for Aotearoa
  New Zealand, the Privacy Act 2020, Stats NZ's microdata and IDI rules
  and published Māori data governance frameworks, record the
  constraints Poltika's architecture must meet: who decides about Māori
  data and outputs about Māori, which disaggregations need that
  decision, confidentiality, and human oversight. This needs people with
  standing in Māori data governance, not only sources, and an interim
  rule holds until they are engaged (P5).
  *Done when:* `doctrine/data-governance.md` records each constraint
  with its source, and a test enforces the interim rule on population
  outputs.
- **1.7 — Claude Code. Check the never-build list mechanically where it
  can be checked.** A release-gate row checks that every population
  result carries its confidence grade, that no output schema scores or
  ranks a party or plan, and that no user-facing page calls Poltika a
  digital twin before Step 12's gate.
- **1.8 — Claude Code. An `evidence-classes` skill**, so every later
  task applies the constitution the same way.

**Exit gate:** the constitution is approved. Every output number is
classed, sourced and carries its uncertainty. The precision rule and
the interim governance rule are enforced, and the mechanical
never-build checks run in CI.

## Step 2: Statutory kernel (M0-M8, then yearly)

Given household state, a date and policy settings, Poltika returns the
legally correct result, explains exactly why, and names what is
uncertain or missing. Then it extends to firms and government. Every
domain follows the `new-policy` skill's five PRs, is born with its fact
catalogue and its conformance matrix (Step 4), and carries a yearly
update line (W5.4).

**Lanes:**

- **2A — Tier 1, M0-M3.** `BUILD_PLAN_v0_3.md` unchanged:
  - Phase 0 scoping;
  - Phase 1, the shared household model (ADR-0017, awaiting Pete);
  - the rest of Phase 1b (1b.2c candidate values, 1b.3e, and GPT/Codex's
    monotone declarations);
  - Phase 2, income tax;
  - Phase 3, Jobseeker Support, Sole Parent Support and Supported
    Living Payment;
  - Phase 4, the dependency graph;
  - Phase 5, disposable income and effective marginal tax rates.
- **2B — Dates.**
  - Multi-year parameters, M1 (W8, v0.1.6 Task 4.3), so "date" is a real
    input for every domain.
  - The 2027-28 year, M4-M6 (v0.1.6, calendar-bound).
  - Historical years for Step 9's backtests, sourced with each domain
    once P11 sets the horizon, so no domain is sourced twice.
- **2C — Next household domains, M2-M5,** in the order of Pete's
  direction:
  - student support (Student Allowance, student loan repayment);
  - ACC levies (new to the coverage map);
  - KiwiSaver interactions;
  - NZ Superannuation;
  - childcare support (Childcare and OSCAR Subsidies);
  - Paid Parental Leave, kept early because Best Start already reads it
    (WFF-06).
- **2D — Other major transfers, M4-M7:**
  - Temporary Additional Support;
  - Disability Allowance;
  - other MSD assistance;
  - Child Support;
  - ACC earnings compensation.
- **2E — Firms and government, M5-M8:**
  - GST: the statute is a Rule, but a household's spending is a Fact or
    an Estimate from survey data, and scoping says which;
  - company tax, which needs a firm state held the way household facts
    are, with the Longitudinal Business Database as its real-data
    target;
  - selected regulatory costs (P9 picks them);
  - other tax regimes (PIE, RWT and trust tax), from W10;
  - Crown revenue and expenditure classifications: every kernel output
    gets a payer and a payee, for Step 6.

2C and 2D reorder `ROADMAP_REALIGNMENT.md` W10's tiers to follow the
direction's list (P9 confirms). About 22 domains remain to add. At 5-8
PRs each (W2.6) that is roughly 110-180 PRs. Pipelining (W2.4) keeps sourcing one domain ahead
of implementation.

**Exit gate:** the kernel household (`BUILD_PLAN_v0_3.md`, "Exit gate")
runs to disposable income for every sourced year. Every domain in the
coverage table is reviewed and benchmarked to v0.1's standard. Every
kernel output maps to a payer and a payee.

## Step 3: Evidence Intelligence (M1-M4)

A machine-readable graph from law to fiscal effect, where every edge
carries its evidence. From any figure, a researcher follows the chain to
the law. For any assumption, Poltika names every result it contaminates.
Pete sees this as the first product Poltika could sell (P8).

- **3.1 — Claude Code. Graph schema.**
  - Node kinds:
    - LAW (source and provision);
    - DECISION;
    - RULE;
    - PARAMETER (value and interval);
    - FACT (catalogue entry);
    - CALCULATION (step template, component);
    - HOUSEHOLD (record);
    - RESULT (component result, run);
    - DATASET and OBSERVATION;
    - ASSUMPTION.
  - Reserved for later steps: BEHAVIOURAL RESPONSE (Step 8), ECONOMIC
    EFFECT (Steps 7 and 11), FISCAL EFFECT (Step 6).
  - Every edge carries source id, locator, evidence class and review
    status.
  - Location set in REPOSITORY_STRUCTURE.md by this task (proposed:
    `engines/assurance/`).
- **3.2 — Claude Code. Build it from what exists, never by hand:**
  - `sources.yaml` and the specification rule tables;
  - `policy.yaml`, `decisions/` and `facts.yaml`;
  - traces and run records;
  - data manifests.

  A test rebuilds the graph and compares.
  *Done when:* every node a golden household's result touches is in it.
- **3.3 — Claude Code. Queries in both directions.** "What does this
  figure rest on", down to the law. "What rests on this", for every
  result, stored run and ledger entry that depends on a source,
  parameter, decision, assumption or dataset. Stored runs are indexed by
  their dependencies.
  *Done when:* a property test shows both directions agree on every
  golden household and a population run.
- **3.4 — Claude Code. Change impact.** A currency-report finding, a
  `review_status` change or a new data vintage lists the results and
  ledger entries it affects.
- **3.5 — Claude Code. Click-through.** An API route and the analyst
  page go from any figure to its law and evidence, and from any
  assumption to what depends on it.
- **3.6 — GPT/Codex. Completeness review:** no rule, parameter or
  decision in a specification is missing from the graph.

**Exit gate:** a reader reaches the law and evidence behind any figure
Poltika shows, and Poltika lists every result a given assumption
contaminates. Both are tested.

## Step 4: Conformance suite (M1-M4)

Statute → machine-readable specification → golden cases → boundary cases
→ contradiction tests → regression suite, for every encoded rule. It is
published so other organisations can certify their calculations against
it.

- **4.1 — Claude Code. A coverage matrix per rule id:**
  - golden: hand-calculated;
  - boundary: each threshold and date boundary, one unit either side;
  - contradiction: inconsistent inputs refused or flagged, an asserted
    fact that contradicts a calculated one, and two rules that would give
    different answers;
  - regression: golden traces.

  CI fails on a rule with a missing class, unless the gap is named and
  Pete has accepted it.
- **4.2 — GPT/Codex. Backfill WFF and the Accommodation Supplement,**
  hand-calculating the missing cases through the test doctrine. The
  `new-policy` skill adds the matrix, so every later domain starts
  complete.
- **4.3 — Claude Code. Portable fixtures.** An implementation-independent
  format: inputs as fact-catalogue values, a date and policy settings;
  expected outcome, value, reason code and rule ids. It has a JSON Schema,
  is versioned with the specification and is generated from the YAML,
  and a test round-trips it.
- **4.4 — Claude Code. The harness.** It runs any calculator through a
  thin adapter (command line or HTTP) against the fixtures and writes a
  conformance report. Poltika's own engine is its first subject, reached
  only through the harness.
- **4.5 — Pete (P6), GPT/Codex checking the IP Doctrine.** What is
  published (specifications and fixtures, not necessarily the
  implementation), under which licence, where, and how it is versioned.

**Exit gate:** every kernel rule has all four classes or an accepted,
named gap, and the published package certifies Poltika through the
harness alone.

## Step 5: Household microsimulation (M1-M6; IDI when granted)

From "what happens to this household?" to "what happens across New
Zealand?", without presenting a synthetic population as reality.

- **5.1 — Pete. Tag `v0.2.0`.** It is ready (`BUILD_PLAN_v0_2.md` 10.3).
- **5.2 — Claude Code, criteria from P4. A confidence grade on every
  population and run:**
  - **Development:** today's independent-marginals population, not an
    estimate for New Zealand;
  - **Public-data (MODERATE);**
  - **IDI-calibrated (HIGHER).**

  A grade is assigned only when its criteria pass. It is never inferred.
- **5.3 — Claude Code, reviewed by GPT/Codex. Joint calibration** (W3.6)
  to published cross-tabulations, and to public survey microdata where
  its licence allows. It comes with a calibration report and extended
  cross-validation, and is graded Public-data only if P4's criteria pass.
- **5.4 — Claude Code.** Each kernel domain's facts join the population
  as the domain lands.
- **5.5 — Claude Code. Secure-environment runner, output checks and
  survey adapter** (`BUILD_PLAN_v0_3.md` Phase 6; W3.3-W3.5), with Step
  1.6's governance constraints enforced at export.
- **5.6 — GPT/Codex, then Pete. IDI and Longitudinal Business Database
  access.** W3.1 documents the route from Stats NZ's published guidance,
  then W3.2 lodges the application. D3 decided on 26 September 2026 to
  apply now, but neither has started. Start at M0, because the lead time
  is external.
- **5.7 — Claude Code.** Results by decile, household type, area and age
  across the whole available kernel, each with coverage and grade.

**Exit gate:** a Public-data population runs the whole available kernel.
Results by decile, household type, area and age carry their grade. The
secure runner passes its tests, and the access application is lodged.

## Step 6: Accounting and fiscal spine (M3-M6)

Connect households to government with stock-flow consistent accounts. A
dollar cannot disappear: if government pays $1b, some other sector
receives $1b, before behaviour. This is what makes static fiscal scoring
credible.

- **6.1 — GPT/Codex. Source the classifications** from Treasury's
  publications, with decision records where ambiguous:
  - Crown revenue and expense lines;
  - balance-sheet items;
  - the definition of net core Crown debt;
  - how the NZ Super Fund is treated.
- **6.2 — Claude Code. Sector accounts:** households, firms, government,
  financial sector and rest of world. Every flow has a payer and a payee.
  Stocks change only through flows and stated revaluations. The
  invariants are property tests: flows net to zero across sectors,
  balance sheets reconcile, and no unbalanced entry is accepted.
- **6.3 — Claude Code. Crown accounts on the spine:**
  - revenue and expenditure;
  - operating balance;
  - assets and liabilities;
  - debt and debt servicing;
  - the NZ Super Fund.
- **6.4 — Claude Code.** Map every kernel output to its Crown line and
  its household flow, from lane 2E.
- **6.5 — Claude Code. Multi-year scenarios** (ADR-0015's v0.4 scope):
  - identity, baseline, interventions and timing;
  - phasing, indexation and packages;
  - persistence and comparison;
  - deterministic run ids.
- **6.6 — Claude Code drafts, Pete decides (P10). The batch engine**
  (W4.2 prototype, W4.3 ADR) by M3, before multi-year population runs.
  The per-household engine stays the reference.
- **6.7 — Claude Code. Static fiscal scoring.** A reform flows through
  weighted household changes to Crown flows by year, then to the
  operating balance and debt. Results are labelled static (no
  behavioural response) and explained through the evidence graph.

**Exit gate:** a multi-year reform is scored statically: household,
distributional, Crown line and debt effects. Every invariant holds, and
every figure is classed and traceable.

## Step 7: National baseline (M4-M8)

What happens if nothing changes. Poltika needs this benchmark before it
predicts any policy effect.

- **7.1 — Claude Code, with GPT/Codex reviewing the mappings.** Stats NZ
  and Treasury connectors beneath the data layer (ADR-0015's v0.5
  connectors). Scheduled refreshes propose new vintages for review.
- **7.2 — Claude Code. Population engine:** age, sex, fertility,
  mortality and migration by cohort, and household formation. Default
  assumptions come from Stats NZ's published projections, and its
  benchmark is reproducing them.
- **7.3 — GPT/Codex, then Claude Code. Macro baseline as exogenous,
  sourced Assumptions with ranges.** GDP, productivity, employment,
  wages, inflation, interest rates and trade, taken from official
  publications. Poltika does not forecast them here.
- **7.4 — Claude Code. Crown baseline** as transparent accounting on the
  spine:
  - revenue from demography, participation and wages;
  - health, education and NZ Super;
  - transfers and debt servicing;
  - capital expenditure.
- **7.5 — Claude Code, GPT/Codex reviewing. Reproduce He Tirohanga
  Mokopuna 2025's unchanged-policy projection.** Swap Poltika's
  assumptions for Treasury's one at a time, and report each one's
  contribution and the unexplained residual: "Treasury produces X.
  Poltika produces Y. The difference comes from assumptions A, B and C."
- **7.6 — Claude Code. Uncertainty that grows with the horizon.** At
  least Treasury's published alternative assumptions become ranges, and
  no long-horizon figure is shown as a point alone.
- **7.7 — Claude Code.** Register the baseline's near-term values in the
  ledger (Step 10).

**Exit gate:** the baseline to 2065 reproduces He Tirohanga Mokopuna
2025 within a stated tolerance, or attributes every difference to named
assumptions. Every input is traced, and ranges grow with the horizon.

## Step 8: Causal evidence library (M5-M9, then continuous)

What causes what in New Zealand, and how sure we are. International
evidence is used where New Zealand evidence is missing, but always
explicitly transferred, never hidden.

- **8.1 — Claude Code, GPT/Codex reviewing. Registry schema,** held in
  files like `policy_specs/` (location set in REPOSITORY_STRUCTURE.md by
  this task). Each entry records:
  - the relationship (exposure to outcome);
  - estimate and range;
  - population and period;
  - method;
  - evidence grade: `NZ_CAUSAL`, `NZ_OBSERVATIONAL`,
    `INTERNATIONAL_TRANSFERRED` or `ASSUMED`;
  - external validity;
  - sources;
  - when it was last reviewed, and by whom.

  Grades map to constitution classes (Estimate, Transferred estimate,
  Assumption).
- **8.2 — GPT/Codex, Pete approving. Transfer protocol.** What must be
  recorded to use another population's estimate: the population,
  institutions, period and any adjustment.
- **8.3 — GPT/Codex. First entries:** the relationships Step 11's first
  domain and behavioural scoring need, from published studies, each
  reviewed. None comes from model memory.
- **8.4 — Claude Code. Intake and promotion.** AI-generated and
  discovered relationships enter as AI hypotheses or `NZ_OBSERVATIONAL`
  candidates. They are promoted only through `Discovery → Hypothesis →
  evidence → validation → human approval → model specification → tests
  → Simulator`. The Discovery and Hypothesis engines become this intake,
  built when there is data to run them on.
- **8.5 — Claude Code. Behavioural scoring:** static results plus
  library responses. The behavioural result is always shown beside the
  static one, with its grades and ranges.
- **8.6 — Pete and GPT/Codex. Poltika's own estimates** (difference in
  differences, synthetic control, regression discontinuity, instrumental
  variables, matching, structural, Bayesian) only as reviewed studies,
  with a design registered in the ledger before the data is analysed,
  and with data access. Methods code is built for the first study, not
  in advance.

**Exit gate:** every behavioural relationship Poltika uses is in the
library with a grade, range and review. A reform shows static and
behavioural results side by side, each chain in the evidence graph.

## Step 9: Historical validation laboratory (M6-M9)

Would Poltika have got the past right, using only what was known at the
time?

- **9.1 — Pete (P11). The backtest horizon,** due M1 so each domain's
  historical years are sourced once, with the domain.
- **9.2 — GPT/Codex. Historical parameter years** for each domain in the
  horizon (W5.3), through the test doctrine.
- **9.3 — Claude Code. As-of runs** that use only the data vintages and
  parameters available at the historical date.
- **9.4 — Claude Code. Backtests** against administrative outcomes and
  past official projections, for example WFF and benefit expenditure
  and recipients by year. They are scored with the ledger's metrics and
  never tuned. Tuning a parameter is a model change with its own record
  (Step 13).
- **9.5 — Claude Code. A published backtest report,** failures included.

**Exit gate:** each covered domain and the baseline report backtest
errors by year against actuals, untuned, with failures published.

## Step 10: Forward prediction ledger (live by M2; grows with every step)

Every material forecast is frozen before reality happens, then scored,
and misses are published. Anyone can build a good historical backtest;
years of timestamped predictions are much harder to fake.

- **10.1 — Claude Code. Entry schema:**
  - id and registration timestamp;
  - target: variable, definition, unit, geography, population and
    period;
  - the resolution source, named in advance;
  - the forecast as an interval or distribution, never a point alone;
  - naive baseline forecasts;
  - model version (commit), data cutoff and run id;
  - the evidence classes it relies on.
- **10.2 — Claude Code. Append-only.** A CI guard, like the
  data-snapshot guard, refuses any edit to a registered entry.
  Resolutions and diagnoses are appended records.
- **10.3 — Pete (P7). External timestamps.** Entries are registered
  publicly, with a third-party hash timestamp, so none can be backdated.
- **10.4 — Pete picks, Claude Code registers. First entries by M2:**
  targets Poltika can honestly forecast now (P7), each with a naive
  baseline and its population grade. Skill on a Development population
  will be low. What matters is the record.
- **10.5 — Claude Code. Scoring:** calibration, bias, mean absolute
  error, Brier scores and interval coverage, by model, by horizon and
  against baselines. The report is generated and published, misses
  included.
- **10.6 — All.** Every later step registers its material forecasts
  before their outcomes are known.

**Exit gate (live):** entries are registered with external timestamps
and named resolution sources, and scoring runs on the first resolutions
and publishes the misses. Resolution takes calendar time.

## Step 11: Domain models (M8-M16, one at a time)

Attack New Zealand's structural problems one at a time, never "the
whole economy" at once. P13 orders them by national importance ×
tractability × available evidence.

- **Proposed first:** fiscal sustainability and ageing (NZ Super,
  health and demography on the spine).
- **Then, in P13's order:**
  - productivity and capital formation;
  - housing, land and infrastructure;
  - health expenditure and healthy ageing;
  - labour supply, skills and migration;
  - energy and infrastructure productivity;
  - trade and economic resilience.

Each domain has its own plan and the method that fits it:

| Domain | Method |
| --- | --- |
| Health | Microsimulation |
| Housing | Spatial, econometric and agent-based hybrid |
| Electricity | Optimisation and network model |
| NZ Super | Overlapping generations and microsimulation |
| Transport | Network model |
| Macro | Structural, econometric and stock-flow consistent hybrid |

Each draws its relationships from Step 8, backtests in Step 9, registers
forecasts in Step 10, and puts its nodes in the evidence graph.

**Gate, per domain:** validated against history, forecasts registered,
relationships graded, and every figure traceable. The next domain starts
once the previous domain's specification is decided (pipelined, as
W2.4).

## Step 12: Federated model and state graph (M10-M14)

Specialised engines, not a monolith, reconciled through a shared state
and the accounting spine.

- An engine contract: canonical inputs and outputs, units, periods and
  sectors. It extends ARCHITECTURE.md's module contract and gives its
  `dependencies` field content.
- A state graph of the national state, and the couplings between
  engines.
- Reconciliation through the spine: the stock-flow invariants hold
  across engines, and conflicting outputs are refused as contradictions.
- Coupled runs, with convergence checks.

**Gate:** two or more domain engines run coupled through the spine, with
every invariant holding, validated and explained. Whether Poltika may
now be called a digital twin is decided here (P15), not before.

## Step 13: Continuous state estimation (M12-M15)

Poltika corrects itself, but never silently.

- Connector refreshes (Step 7) update the state.
- Each resolved ledger miss gets a diagnosis record: the prediction
  failed because X; the candidate explanations are A, B and C; the
  evidence supports B.
- Each parameter or model change is a reviewed PR that cites its
  diagnosis ("parameter changed from X to Y").
- Historical predictions stay frozen.

**Gate:** one full cycle of observe, forecast, error, diagnosis and
approved update is recorded for a domain.

## Step 14: Uncertainty and sensitivity (M9-M13)

The full machinery, beyond Step 1's per-number representation:

- an assumption register with distributions (ADR-0015's v0.5);
- seeded Monte Carlo on the batch engine (P10);
- one-way, multi-parameter and global sensitivity;
- correlated uncertainties;
- uncertainty that grows with the horizon;
- model cards: methods, validation, limitations and failure modes.

**Gate:** every material result has a propagated interval and a ranked
list of the assumptions that drive it.

## Step 15: Cost of delay (M13-M14)

Proposed definition (P16): for an intervention, how outcomes and the
adjustment needed to meet a stated target change as its start date
moves. It is computed from scenario families that vary only the start
date, with uncertainty.

**Gate:** a cost-of-delay curve for one fiscal intervention, with its
interval and evidence chain.

## Step 16: Policy-space optimisation (M14-M16)

**Precondition, the causal credibility gate (P14):** every relationship
the search relies on meets a stated minimum grade and has been
backtested.

- People state the objectives and constraints. For example:
  - debt to GDP in 2065 below 60%;
  - real GDP per capita in 2065 above the baseline;
  - poverty in 2065 no higher than the baseline;
  - plus environmental, distributional, fiscal and implementation
    constraints.
- Poltika searches packages across the supported levers (tax,
  retirement, health, migration, planning, infrastructure, education,
  capital investment, regulation, transfers). It returns the
  Pareto-efficient feasible set, with trade-offs, uncertainties,
  assumptions and robustness across the uncertainty.
- It never returns a single recommendation, and it holds no default
  objective. The answer is "these packages satisfy the constraints you
  supplied", not "do this".
- v0.2's deterministic sweeps stay. They are not optimisation.

**Gate:** every member of a returned set reproduces as an ordinary
scenario, with its trade-offs and assumptions shown.

## Step 17: Value of information (M15-M17)

Which unanswered questions cost New Zealand the most.

- Under a stated objective, the expected value of perfect information
  (EVPI) per uncertain parameter.
- The expected value of sample information (EVSI) for a proposed study.
- A ranked list of the unknowns that most change the decision.

The intake planner's "most useful next question" (ADR-0016) is the same
idea at household scale.

**Gate:** where two packages differ mainly through one parameter,
Poltika names it and estimates its EVPI, and the EVSI of a named study
design.

## Step 18: Public Futures Laboratory (M16-M18)

**Trust gate first:**

- Steps 1-14 have passed.
- Production hardening (ADR-0015's v1.0 list): threat model,
  penetration test, access control, encryption, backups, incident
  response, monitoring and performance.
- Independent scrutiny by specialists in economics, econometrics,
  statistics, public finance, New Zealand policy, Māori data governance
  and security, with criticisms and responses published.
- A published ledger record, misses included.

**Scope:**

- Baseline, policy and alternative scenarios at 2030, 2040, 2050 and
  2065.
- GDP per person, wages, taxes, housing, health, Crown debt, retirement,
  distributional effects, infrastructure and environmental indicators.
- Every chart answers: why? source? assumptions? uncertainty? who is
  affected? what would change this result? The answers come from the
  evidence graph, sensitivity and value of information.
- No scores and no winners.

**Gate:** a person who didn't build Poltika can compare scenarios and
answer all six questions for any chart.

## Step 19: AI reasoning and search interface (M17-M19)

AI operates the instrument. It isn't the instrument.

- An LLM translates a request into Poltika constraints and scenarios,
  and confirms any consequential interpretation.
- The deterministic and statistical engines execute, and the optimisers
  search.
- The LLM explains the verified results. It supplies no number and no
  relationship. Every figure in its explanation is checked against the
  engine output before it is shown (the `verify()` pattern).
- Hypotheses it generates go to Step 8's intake as AI hypotheses.
- `src/poltika/llm/` is built here, under `doctrine/llm_boundaries.md`.

**Gate:** on a benchmark set of requests, every figure the AI shows
matches the engine, and every interpretation it made is shown and can be
confirmed.

## Step 20: Continuously improving national digital twin (M19 on)

The long-run loop, with each turn recorded in the ledger and the
evidence graph:

`OBSERVE → DISCOVER → HYPOTHESISE → TEST → SIMULATE → ASSURE → COMPARE → DECIDE → OBSERVE REAL OUTCOME → RECALIBRATE`

---

## Releases

A release is tagged when its steps' exit gates pass. Each one answers a
harder version of the question.

| Release | Steps | Target | Adds to the question |
| --- | --- | --- | --- |
| v0.1, v0.1.5 | Done | | What does this household get, and why? |
| v0.2 | Ready to tag (5.1) | M0 | What happens across a development population? |
| v0.1.6 | 2B | By M6 (1 April 2027) | Under next year's law |
| v0.3 | 1; 2A; 4.1 for Tier 1; 5.5 | M0-M3 | Whole disposable income, through which chain of rules, with every number classed |
| v0.4 | 3; 4; 10 live; 2C | M2-M5 | Through what mechanism, checkable by anyone, with forecasts on record |
| v0.5 | 5; 6; 2D | M4-M7 | To whom across New Zealand, and what it costs the Crown each year |
| v0.6 | 7; 2E | M6-M8 | Compared with what happens if nothing changes |
| v0.7 | 8; 9 | M7-M9 | How people respond, how sure we are, and whether we got the past right |
| v1.0 | Gates 1-10, plus the hardening an outside analyst needs | M10 | The whole question, for changes inside the kernel |
| v1.x | 11, one domain per release | M9-M16 | One structural problem at a time |
| v2.0 | 12-15 | M12-M15 | Across connected systems, self-correcting, with full uncertainty and the cost of waiting |
| v3.0 | 16-17 | M16-M17 | Which options meet our constraints, and what to learn first |
| v4.0 | 18-19 | M18-M19 | Anyone can ask |

**v1.0 definition (testable).** For a structured package of changes
inside its supported kernel domains, Poltika answers:

- **what happens:** static results, and behavioural ones where the
  causal library holds a graded relationship;
- **to whom:** by decile, household type, area and age, on a graded
  population;
- **when:** year by year, through the Crown accounts;
- **through what mechanism:** the evidence-graph chain to law and
  evidence;
- **with what confidence:** evidence classes, ranges, the population
  grade, backtest errors and the ledger's record;
- **compared with what alternatives:** the unchanged-policy baseline and
  other scenarios.

An independent analyst can reproduce and challenge the result without
the builders. A "supported domain" has an approved specification, a
complete conformance matrix (Step 4), an independent review and current
values (P1, decided).

## What changes in the current plans

| Current plan | Under this plan |
| --- | --- |
| `BUILD_PLAN_v0_3.md` | Kept. v0.3 also ships Step 1, Step 4.1 for Tier 1 domains, and the Step 1.7 release-gate rows. The references in its "Not in v0.3" list now point here: multi-year scenarios to Step 6, uncertainty to Step 14, the historical baseline to Step 7, GST and company tax to lane 2E, behaviour to Step 8, and Tier 2 and 3 to lanes 2C-2D. |
| `BUILD_PLAN_v0_1_6.md` | Kept as lane 2B. The 1 April 2027 deadline stands. |
| `BUILD_PLAN_v0_2.md` | Done. Tag it (5.1). Its population becomes the Development grade (5.2). |
| ROADMAP v0.4, scenario engine | Step 6.5, inside the fiscal spine |
| ROADMAP v0.5, uncertainty, assurance and historical baseline | Split: assumption register and Monte Carlo to Step 14; connectors and the historical baseline to Step 7; backtesting to Step 9; provenance, staleness and validation checks to Steps 1 and 3; model cards to Step 14 |
| ROADMAP v0.6, long-term fiscal model | Step 7 (Crown baseline, comparison with Treasury) and Step 11's first domain. Its "constrained scenario search" moves to Step 16, behind the causal gate. |
| ROADMAP v0.7, decision-intelligence product | APIs and click-through lineage to Step 3; the public interface to Step 18; the LLM to Step 19; users, organisations, permissions and audit logs to v1.0 hardening and Step 18 |
| ROADMAP v1.0, production | Redefined around the question (above); security hardening stays before any public use (Step 18) |
| Discovery and Hypothesis, after v1.0 | The intake of the causal library (Step 8), under the same promotion gate |
| v2 Economic Digital Twin | Steps 11-12 |
| v3 Physical NZ | Step 11's energy, infrastructure, housing, land and transport domains, as federation members |
| v4 Adaptive Digital Twin | Step 13 |
| v5 National Decision Intelligence | Steps 16-20 |

## Carried workstreams (`ROADMAP_REALIGNMENT.md`)

| Workstream | Under this plan |
| --- | --- |
| W1 Review debt and cadence | The queue and gate rows stay. The cap doesn't sequence this plan (Pete, 29 September 2026). Whether it stays in the working agreement is P17. |
| W2 Policy coverage throughput | Step 2. The `new-policy` skill, five PRs per domain, pipelining and throughput tracking all stay. The skill gains the Step 4 matrix and Step 1's evidence classes. |
| W3 Real-data access | Step 5 (5.3, 5.5, 5.6), with governance from 1.6 |
| W4 Batch engine | Decided by M3 (P10), before Step 6's multi-year population runs |
| W5 Maintenance budget | Stays. The backtest horizon (W5.3) is due at M1 (P11). |
| W6-W8 | Stay in v0.3 and v0.1.6 |
| W9 Roadmap reorder | Superseded by ADR-0018 |
| W10 Coverage map | Extended by lanes 2C-2E: ACC levies, GST, company tax, selected regulatory costs and Crown classifications join, and the tiers follow the direction's order (P9) |

## What Poltika never builds

This becomes doctrine in Step 1.1. Where it can be checked mechanically,
Step 1.7 checks it.

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models: every change is a reviewed record (Step
  13).
- No point estimate where the uncertainty is large (Steps 1.4 and 14).
- No synthetic population presented as reality (Step 5.2).
- No policy optimisation before causal relationships are credible (Step
  16's gate).
- No "digital twin" branding before the model deserves it (Step 12's
  gate).
- **Never optimise the model instead of the country.** Ledger and
  backtest scores are monitored, never targeted. A change made to
  improve a score needs the same diagnosis record as any other change.

## Decisions

Pete approved this plan on 29 September 2026 ("Approve and proceed all").
That decided every item below that had a recommendation or a proposal.
Items with no recommendation stay open, and each is brought back with one
when its task starts.

**Decided 29 September 2026:**

- **P1:** the reconciliation, month targets, release mapping, v1.0
  definition and "supported domain" definition, as written.
- **P2:** a caller-asserted household fact is a **Scenario** input,
  because Poltika never observes it. A later verified real-household use
  could make it a Fact with a verification source.
- **P3:** the precision rule. A single household's Rule output keeps the
  precision the law sets. Population, baseline and Estimate-dependent
  figures are shown to three significant figures with their range.
  Stored values keep full precision.
- **P4, names:** Development, Public-data (MODERATE) and IDI-calibrated
  (HIGHER). The criteria for each come with Task 5.2.
- **P5, interim rule:** no output is disaggregated by ethnicity or iwi
  until the governance process is agreed. Engaging people with standing
  in Māori data governance is Pete's, and still open.
- **P9:** the kernel follows the direction's order (lanes 2C-2E). Which
  regulatory costs to model comes with lane 2E's scoping.
- **P12:** apply for IDI access. W3.1 (GPT/Codex) documents the route
  first; lodging it is Pete's.
- **P16:** the cost-of-delay definition in Step 15.
- **P17:** the review-debt cap is suspended (Pete: "Ignore PR cap"). The
  review queue is still kept, and release gates still name unreviewed
  PRs.
- **Carried:** ADR-0017, the shared household model, accepted with its
  three recommended answers (dated spells; one family per household in
  v0.3; today's request formats kept as adapters). This is
  `BUILD_PLAN_v0_3.md` D6.

**Open (no recommendation yet):**

- **P6:** conformance publication: what, licence, where, versioning (with
  Task 4.5).
- **P7:** the timestamping service and the first forecast targets (with
  Task 10.3-10.4). Public registration with a third-party hash timestamp
  is part of the approved plan.
- **P8:** Evidence Intelligence as the first product: scope, users and
  terms.
- **P10:** the batch engine (was `ROADMAP_REALIGNMENT.md` D5), by M3.
- **P11:** the backtest horizon (was D6), by M1.
- **P13:** the domain-model order, from a scored rubric.
- **P14:** the causal credibility gate for policy search: the minimum
  grade and the backtest requirement.
- **P15:** the criteria for calling Poltika a digital twin.
- **v0.3 D1-D3:** each Tier 1 domain's slice, the disposable-income
  definition and the income-adequacy measures, from Phase 0's sourcing.

## Progress

| Step | State |
| --- | --- |
| Plan | Approved 29 September 2026 with ADR-0018 |
| 1-20 | As in "Where Poltika stands". Each row is updated as its tasks land. |
