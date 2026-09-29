# Poltika programme build plan: from executable rules to a decision instrument

**Date:** 29 September 2026
**Status:** Pete's direction, 29 September 2026 (ADR-0018), revised the
same day to a 22-step sequence. The revision followed Pete's review of
MIT's work in Andorra and of the dependency order. It replaces the first,
20-step version of this plan, which Pete had approved ("Approve and
proceed all"). The decisions taken then carry over unless marked
otherwise ("Decisions"). The reconciliation, month targets and release
mapping are Claude Code's drafting to Pete's order.
**Supersedes:** ADR-0015's release sequence and `ROADMAP_REALIGNMENT.md`
W9. `BUILD_PLAN.md` stays the frozen record of v0.1. `BUILD_PLAN_v0_3.md`
stays the task list for v0.3, which now covers Steps 1 and 2 and the first
tier of Step 3 ("What changes in the current plans").

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

**Why now:** Treasury's He Tirohanga Mokopuna 2025 projects net core
Crown debt at 200.0% of GDP by 2065 if fiscal policy is unchanged.
Treasury calls this a projection, not a prediction (treasury.govt.nz,
retrieved 29 September 2026). Step 10 reproduces that baseline or explains
where Poltika's differs.

## What Poltika becomes, and how it earns each stage

The progression is not calculator → simulator → digital twin. It is:

`executable rules → observable state → explanatory model → predictive model → integrated model → decision instrument → digital twin`

Each transition has a different burden of proof. **Poltika doesn't
graduate to the next level because the code is finished. It graduates
when the current level has shown sufficient validity.**

| Level | Burden of proof to reach it | Mainly built by |
| --- | --- | --- |
| 1. Executable rules | Legally correct. Every rule's golden, boundary, contradiction and regression cases pass, benchmarks match official worked examples, and the specification is independently reviewed. | Steps 1-5 |
| 2. Observable state | Poltika's picture of New Zealand matches what is observed. The population reproduces published aggregates within stated tolerances, the state store reproduces its sources, and the accounts reconcile with the Crown's published statements. | Steps 6-9 |
| 3. Explanatory model | Poltika explains observed history. The baseline reproduces Treasury's projection or attributes every difference. Historical replays reproduce past outcomes, given the shocks that actually happened, better than naive baselines. Stated intervals cover history at their stated rates. | Steps 10-13 |
| 4. Predictive model | Out of sample: registered forecasts resolve inside their intervals at their stated rates and beat naive and statistical baselines, over a record long enough to judge. This takes calendar time. | Steps 6 and 14 |
| 5. Integrated model | The coupled system keeps every invariant and reproduces history at least as well as its parts do separately. | Steps 14-17 |
| 6. Decision instrument | Decision outputs (cost of delay, value of information, feasible sets) are robust across the stated uncertainty, reproducible, and have survived independent scrutiny. | Steps 18-21 |
| 7. Digital twin | The state estimate updates continuously from observations, with a sustained, published forecast record. | Step 17 onward |

Rules that follow from the ladder (Step 1.6 makes them doctrine):

- Every model in the model registry (Step 1.5) has a level. An output
  carries the level of the least mature model it relies on.
- Graduation is a recorded decision by Pete on validation evidence (Step
  6). The tolerances for each level are set when that level is first
  reached (P18).
- Language follows level. Nothing is described as predictive before
  Level 4, and Poltika is not called a digital twin before Level 7.
- A level can be lost. If validation evidence stops supporting it, the
  model is demoted and its outputs relabelled.

## Two directions of growth

The 22 steps are not a waterfall. They build a vertical stack, from the
statutory kernel up to the AI layer:

`statutory kernel → microsimulation → fiscal and accounting spine → national state engine → domain models → decision intelligence → AI layer`

Horizontal capabilities run across every level, from the start, and never
have a "finished" version:

| Capability | Exists now | Early steps add | Grows into |
| --- | --- | --- | --- |
| Evidence and provenance | Per-result traces, source locators and ranks, data lineage, verified explanations (v0.1.5) | The evidence graph (Step 4) | Behavioural, economic and fiscal edges (Steps 8, 12); public click-through (Step 21) |
| Validation | Spec cases, benchmarks, golden households, v0.2 cross-validation, stored-run code replay | One validation framework (Step 6); the conformance matrix (Step 5) | Published aggregates (Step 7); historical replay (Step 13); forecast scoring (Step 6 onward) |
| Uncertainty | Conditional bounds and population ranges (ADR-0016) | D_x in every quantity (Step 2) | Propagation and sensitivity (Step 11); horizon uncertainty (Steps 10, 14) |
| Versioning | Code identity, policy file hashes, run ids, data vintages | Model and variable registry versions (Steps 1.5, 2) | State-store vintages (Step 9); diagnosed model changes (Step 17) |
| Prediction scoring | None | Ledger v0 (Step 6) | Every model registers forecasts; Level 4 |
| Security and privacy | Password-protected pilot; operator-set population; no unit records committed | Secure-environment runner and output checks (Step 7) | Production hardening before public use (Step 21) |
| Māori data governance | None | Interim rule and sourcing (Step 1.4) | An agreed process covering microdata outputs (Step 7) and public outputs (Step 21) |
| Model governance | Doctrines, independent review, the review queue | Model registry, change control, graduation gates (Steps 1.5-1.6) | Diagnosed updates under continuous estimation (Step 17) |
| Reproducibility | Run ids, result hashes, code replay, immutable snapshots | Model versions on every quantity (Step 2) | As-of runs (Steps 9, 13); transition runs (Step 14) |

For example, validation starts with "does WFF case #147 produce the
legally correct answer?", then "can the household microsimulation
reproduce published aggregates?", then "starting in 2015, can the fiscal
model reproduce 2016-2025, given the shocks that actually happened?", and
finally "did the forecast registered in 2029 land inside its interval?".
It is the same doctrine, scaling upward.

## What changes now, and what doesn't

The statutory kernel and the evidence and explainability work stay
exactly where they are: they are where Poltika starts. What changes now
is that the early architecture anticipates what the later steps need, so
v0.x isn't torn apart later. v0.3 adds:

- **Evidence classes and model governance** (Step 1): what kind of claim
  every number is, and a registry of models with versions, levels and
  change control.
- **The National Variable Registry** (Step 2): one definition for every
  unit, period, population, geography, stock or flow, and identifier,
  before several models each invent their own. The shared household
  model (ADR-0017) is its first instance.
- **Uncertainty metadata in the data model** (Step 2): every quantity is
  X = (x̂, D_x, E_x), where x̂ is the value, D_x its uncertainty and E_x
  the evidence for it. The types accept intervals and distributions now,
  even though propagation comes in Step 11.
- **Data and model versioning** (Steps 1.5 and 2): every quantity names
  the model version and data vintage it came from.
- **One dependency graph** (Steps 3A and 4): the household policy graph
  and the evidence graph share node ids.
- **The validation framework's shape** (Step 6): today's tests and
  comparisons become validation cases, so later validation extends them
  rather than replacing them.

## How to read this plan

- **22 steps, in Pete's order.** A step's exit gate needs the earlier
  gates, except where a step says it starts early. Horizontal capabilities
  start in the step named, then grow.
- **Months are targets**, counted from M0 = October 2026 (M3 = January
  2027, M6 = April 2027, M12 = October 2027, M24 = October 2028). Steps
  overlap. Exit gates and level graduations, not dates, decide when
  something is done. The code is rarely the constraint: v0.1 took seven
  calendar days (`docs/research/policy_onboarding_cost.md`). Sourcing,
  independent review and Pete's decisions set the pace.
- **Some things can't be compressed**, whatever the pace:
  - every rate year starts on 1 April; 2027-28 must be in by 1 April 2027
    (M6), and every domain adds a yearly update;
  - a forecast resolves no sooner than its horizon, so Level 4 waits on
    calendar time;
  - microdata (IDI) access is an external approval with its own lead
    time;
  - independent human scrutiny, Māori data governance engagement and
    Pete's decisions take the time they take.
- **Owners** follow the working roles: GPT/Codex for sources,
  interpretation and independent review; Claude Code for implementation;
  Pete for decisions and anything that needs a person.
- **Detail matches distance.** Steps 1-10 have tasks with a "done when".
  Steps 11-22 have scope and a gate, and each gets its own detailed plan
  when it starts.

## Where Poltika stands (29 September 2026)

What is already built, against each step. "Partial" means a real part of
the step exists and is reused, not rebuilt.

| # | Step | What exists | State | What remains |
| --- | --- | --- | --- | --- |
| 1 | Epistemic constitution and model governance | CLAUDE.md's ground truth; doctrines (deterministic core, LLM boundaries, test, review, IP, scope, development); `calculated`/`unsupported`/`needs_review`, and a missing fact is never zero; source authority ranks; `review_status`, with `scenario_assumption` for reform values; the caller-asserted fact ledger; independent review and the review queue | Partial | The evidence classes on every output; a precision rule; the AI-hypothesis gate written down; the never-build list; data governance; a model registry, change control and the graduation ladder |
| 2 | National Variable Registry and common schemas | `CanonicalVariable` (unit, frequency, price basis, stock or flow, geography and population, validity) and a dictionary of 54 variables (v0.2 Task 3.1); `Observation` and `Lineage`; the population schema; `DataContext` with vintages; ADR-0017 accepted | Partial: external data only | Engine inputs and outputs in the registry; unit, period, entity and geography registries with explicit conversions; identifiers; the quantity type X = (x̂, D_x, E_x); the shared household model; the state schema S_t |
| 3 | Statutory kernel | WFF 2026-27 (in-work tax credit `needs_review`) and the Accommodation Supplement, each to v0.1's standard; fact catalogues, intake questions and conditional answers (v0.3 Phase 1b, mostly done); reforms as parameter overrides; the source-currency report | Partial: 2 of about 24 domains | v0.3 Phase 0 and Phases 2-5; multi-year parameters; 2027-28; the other household domains; firms and government |
| 4 | Evidence Intelligence and the evidence graph | Sources with locators and ranks; rule ids; decision records; traces; provenance reports; verified explanations; the evidence coverage check; data lineage; stored runs | Partial: forward, per result | A queryable graph; reverse "what does this contaminate" queries; click-through; later layers |
| 5 | Conformance and regression suite | Spec cases (WFF 23, AS 26, interaction 5), benchmarks, 9 golden households, golden traces, 100+ explanation fixtures, the statutory-value guard, Hypothesis properties, shared-fact contradiction checks | Partial | A per-rule matrix with boundary and contradiction classes; portable fixtures; a harness; publication |
| 6 | Validation framework and Prediction Ledger v0 | The three test classes; v0.2's cross-validation against IRD and MSD figures (untuned); stored-run code replay; immutable snapshots under a CI guard | Partial: no common framework; no ledger | Validation cases and reports; standard naive baselines; the ledger |
| 7 | Household microsimulation | v0.2, ready to tag: a synthetic development population, reforms, distributional and fiscal tables, withdrawal rates, sweeps, cross-validation, population ranges, `/microsim` | Partial: development grade | Confidence grades; joint calibration; secure runner; IDI access; governance at export; every kernel domain in the population |
| 8 | Fiscal and accounting spine | Static annual cost per component with coverage (v0.2); stored scenarios; the scaling model | Minimal | Sector accounts and invariants; Crown accounts; classifications; multi-year scenarios; the batch-engine decision; static fiscal scoring |
| 9 | Historical NZ State Store | Five Stats NZ snapshots; `DataContext.get(variable, on, vintage)` | Minimal | Connectors; state snapshots per period and vintage; as-of queries |
| 10 | National Baseline Engine | None | None | Population engine; macro assumptions; Crown baseline; Treasury comparison |
| 11 | Uncertainty and sensitivity framework | Conditional bounds, population ranges, deterministic sweeps | Minimal | Propagation, sensitivity, correlated uncertainty |
| 12 | Causal Evidence Library | Discovery and Hypothesis placeholders; the promotion gate | None | All |
| 13 | Historical Validation Laboratory | v0.2's one-year cross-validation | Minimal | Backcasts, policy and shock replay, benchmarks |
| 14 | National State Transition Engine | None | None | All |
| 15 | Priority domain models | None | None | All |
| 16 | Federated Model Graph | ARCHITECTURE.md's module contract, with an empty `dependencies` field | None | All |
| 17 | Continuous State Estimation | The currency report flags rule changes (for rules only) | None | All |
| 18 | Cost of delay and scenario discovery | Deterministic sweeps | None | All |
| 19 | Value of information | The intake planner ranks missing facts by impact: the household-scale version | None | EVPI and EVSI over model parameters |
| 20 | Policy-space optimisation | None | None | All, behind its gates |
| 21 | Public Futures Laboratory | Internal analyst pages; a password-protected hosted pilot | None | All, behind the trust gate |
| 22 | AI reasoning and search layer | `doctrine/llm_boundaries.md`; the intake page limits any LLM to phrasing catalogue questions | None | All |

## Schedule

| # | Step | Target months | Release |
| --- | --- | --- | --- |
| 1 | Epistemic constitution and model governance | M0-M1 | v0.3 |
| 2 | National Variable Registry and common schemas | M0-M2, then grows | v0.3 |
| 3 | Statutory kernel | M0-M9, then yearly | v0.3 (Tier 1), then v0.4-v0.6 |
| 4 | Evidence Intelligence and the evidence graph | M1-M4, then grows | v0.4 |
| 5 | Conformance and regression suite | M1-M4 | v0.3 (Tier 1 matrix), v0.4 |
| 6 | Validation framework and Prediction Ledger v0 | M2-M4; ledger live by M3 | v0.4 |
| 7 | Household microsimulation | M3-M7; IDI when granted | v0.5 |
| 8 | Fiscal and accounting spine | M4-M8 | v0.5 |
| 9 | Historical NZ State Store | M5-M8 | v0.6 |
| 10 | National Baseline Engine | M6-M10 | v0.6 |
| 11 | Uncertainty and sensitivity framework | M7-M10 | v0.7 |
| 12 | Causal Evidence Library | M8-M12, then continuous | v0.7 |
| 13 | Historical Validation Laboratory | M9-M13 | v0.7 |
| 14 | National State Transition Engine | M11-M14 | v1.x |
| 15 | Priority domain models | M13-M21, one at a time | v2.x |
| 16 | Federated Model Graph | M15-M21 | v2.0 |
| 17 | Continuous State Estimation | M17-M22 | v2.x |
| 18 | Cost of delay and scenario discovery | M19-M21 | v3.0 |
| 19 | Value of information | M20-M22 | v3.0 |
| 20 | Policy-space optimisation | M21-M24 | v3.x |
| 21 | Public Futures Laboratory | M23-M25 | v4.0 |
| 22 | AI reasoning and search layer | M24-M26 | v4.x |
| ∞ | Continuously improving national digital twin | Emerges; not a release | |

---

## Step 1: Epistemic constitution and model governance (M0-M1)

What counts as fact, rule, estimate, assumption, scenario and model
output, and what provenance and reproducibility every model owes.

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
- **1.2 — Claude Code, GPT/Codex reviewing. The AI-hypothesis gate.**
  Everything Claude Code or GPT/Codex drafts (sources, specifications,
  values, interactions, estimates) is an AI hypothesis until it has a
  cited primary source and an independent review, and, for protected
  values and interpretations, Pete's decision.
  *Done when:* the constitution names the gate for each kind of
  artifact, and each gate is enforced by an existing or new check.
- **1.3 — Claude Code. The precision rule (P3).** A single household's
  Rule output keeps the precision the law sets. Population, baseline and
  estimate-dependent figures are shown to three significant figures with
  their range. Stored values keep full precision. It is implemented with
  the quantity type (2.6).
- **1.4 — Pete, with the people Pete engages; GPT/Codex sources. Data
  governance as architecture.**
  - From the Algorithm Charter for Aotearoa New Zealand, the Privacy Act
    2020, Stats NZ's microdata and IDI rules and published Māori data
    governance frameworks, record the constraints Poltika must meet.
  - Record who decides about Māori data and outputs about Māori, which
    disaggregations need that decision, confidentiality, and human
    oversight.
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
    - its level on the ladder;
    - its validation status, linked to its validation cases (Step 6);
    - the evidence classes it consumes;
    - known limitations;
    - a change log.
  - Change control: every material change to a rule, parameter,
    relationship or engine has a change record (what changed, why, the
    evidence, the validation re-run, the approval). Nothing changes
    silently.
  - Model cards: methods, validation, limitations and known failure
    modes, generated from the registry and validation reports.

  *Done when:* every existing engine has an entry and a card, and CI
  fails on an engine without one.
- **1.6 — Claude Code drafts, Pete approves. The maturity ladder as
  doctrine:** the seven levels, each level's burden of proof, graduation
  and demotion by recorded decision on validation evidence, outputs
  labelled with the least mature model they rely on, and language that
  follows level.
  *Done when:* every registered model has a level, and every output
  carries the level of the least mature model it relies on.
- **1.7 — Claude Code. Mechanical never-build checks.** A release-gate
  row checks that every population result carries its grade, that no
  output schema scores or ranks a party or plan, and that no
  user-facing page claims a level Poltika hasn't reached (for example,
  "digital twin" before Level 7).
- **1.8 — Claude Code. An `evidence-classes` skill**, so every later
  task applies the constitution the same way.

**Exit gate:** the constitution, model governance and ladder are
approved; every existing engine is registered with a level and a card;
the interim governance rule and the mechanical checks run in CI.

## Step 2: National Variable Registry and common schemas (M0-M2, then grows)

Canonical units, periods, populations, geographies, stocks and flows and
identifiers, defined before several models invent incompatible ones. The
registry grows with Poltika. It is never finished.

- **2.1 — Claude Code, GPT/Codex reviewing. The registry covers every
  variable a model reads or writes,** not only external data. This
  extends `semantics/variables.py`'s `CanonicalVariable` and dictionary
  with:
  - the entity it describes (person, family, household, firm, sector,
    the Crown, New Zealand);
  - stock or flow (`Measure` exists);
  - its unit, period type and geography type, each from 2.2-2.5;
  - its identifier scheme.

  Engine inputs (fact-catalogue entries) and outputs (components) are
  registered alongside the Stats NZ variables.
- **2.2 — Claude Code. Units.** Each unit has a dimension (money, persons,
  households, ratio, percent) and a price basis. A conversion (for
  example nominal to real) exists only as a named, sourced rule with its
  deflator variable, and is never implicit.
- **2.3 — Claude Code. Periods.** Tax year, assessment week, quarter,
  calendar year and point in time. A conversion between period types is
  a named rule citing its source. For example, the AS week sits inside
  the WFF year (Task 28.3), and a WFF income can't become an AS weekly
  income without a stated rule (v0.2 D9).
- **2.4 — Claude Code. Populations, entities and identifiers:** person,
  family, household, firm, sector and the Crown, each with an identifier
  scheme. v0.3 keeps one family per household (ADR-0017).
- **2.5 — Claude Code, GPT/Codex sourcing concordances. Geographies:**
  New Zealand, regions, statistical areas and AS areas, with dated
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

  `Observation` with `Lineage`, and `ComponentResult` with its trace,
  map onto it through adapters. The engines don't change.
  *Done when:* every existing output type has an adapter, round-trip
  tests pass, and every result and result id is byte-identical.
- **2.7 — Claude Code. The shared household model** (ADR-0017;
  `BUILD_PLAN_v0_3.md` Phase 1) as the registry's first full instance.
  Each household fact is a registered variable.
- **2.8 — Claude Code drafts, GPT/Codex reviewing. State schema v0.** The
  set of registered stocks that define New Zealand's state S_t, and the
  flows between S_t and S_t+1. Version 0 covers what the kernel,
  microsimulation and spine use, and it grows with each step. Steps 9,
  10 and 14 use it.
- **2.9 — Claude Code. Every shown or stored number is a quantity.**
  Every figure the API returns carries its quantity, and every stored run
  can produce its quantities, without changing stored results. A
  response with an unclassed number is refused, as a failing `verify()`
  is. The precision rule (1.3) applies to what is shown.
- **2.10 — Claude Code. Registry checks.** CI fails on a variable used in
  code but not registered, or on a unit or period mismatch in a mapping.

**Exit gate:** every number any engine reads or writes is a registered
variable with its unit, period, entity and geography; every output is a
quantity with D_x and E_x; state schema v0 is defined.

## Step 3: Statutory kernel (M0-M9, then yearly)

Given household state, a date and policy settings, Poltika returns the
legally correct result, explains exactly why, and names what is
uncertain or missing. Then it extends to firms and government. Every
domain follows the `new-policy` skill's five PRs, is born with its fact
catalogue, its registry entries (Step 2), its conformance matrix (Step 5)
and its model-registry entry (Step 1.5), and carries a yearly update line
(W5.4).

**Lanes:**

- **3A — Tier 1, M0-M3.** `BUILD_PLAN_v0_3.md` unchanged:
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
  - Historical years for backtests and replays (Step 13), sourced with
    each domain once P11 sets the horizon.
- **3C — Next household domains, M2-M5,** in the direction's order:
  - student support (Student Allowance, student loan repayment);
  - ACC levies;
  - KiwiSaver interactions;
  - NZ Superannuation;
  - childcare support (Childcare and OSCAR Subsidies);
  - Paid Parental Leave, early because Best Start already reads it
    (WFF-06).
- **3D — Other major transfers, M4-M7:**
  - Temporary Additional Support;
  - Disability Allowance;
  - other MSD assistance;
  - Child Support;
  - ACC earnings compensation.
- **3E — Firms and government, M5-M9:**
  - GST: the statute is a Rule, but a household's spending is a Fact or
    an Estimate from survey data, and scoping says which;
  - company tax, which needs a firm state in the registry, with the
    Longitudinal Business Database as its real-data target;
  - selected regulatory costs (chosen at scoping);
  - other tax regimes (PIE, RWT and trust tax);
  - Crown revenue and expenditure classifications: every kernel output
    gets a payer and a payee, for Step 8.

About 22 domains remain to add. At 5-8 PRs each (W2.6) that is roughly
110-180 PRs, with sourcing kept one domain ahead of implementation
(W2.4).

**Exit gate:** the kernel household (`BUILD_PLAN_v0_3.md`, "Exit gate")
runs to disposable income for every sourced year. Every domain in the
coverage table reaches Level 1. Every kernel output maps to a payer and
a payee.

## Step 4: Evidence Intelligence and the evidence graph (M1-M4, then grows)

A machine-readable graph from law to fiscal effect, where every edge
carries its evidence. It started with v0.1.5's evidence work and grows
for the life of Poltika. Pete sees it as the first product Poltika could
sell (P8).

- **4.1 — Claude Code. Graph schema.**
  - Node kinds:
    - LAW (source and provision);
    - DECISION;
    - RULE;
    - PARAMETER (value and interval);
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
    EFFECT (Steps 10, 15), FISCAL EFFECT (Step 8).
  - Every edge carries source id, locator, evidence class and review
    status. Node ids are shared with the household dependency graph
    (3A).
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
  `review_status` change, a new data vintage or a model change lists
  what it affects, and which validation cases must re-run.
- **4.5 — Claude Code. Click-through** from any figure to its law and
  evidence, and from any assumption to what depends on it, in the API and
  the analyst page.
- **4.6 — GPT/Codex. Completeness review:** no rule, parameter or
  decision in a specification is missing from the graph.

**Exit gate:** a reader reaches the law and evidence behind any figure
Poltika shows, and Poltika lists everything a given assumption or model
version affects. Both are tested.

## Step 5: Conformance and regression suite (M1-M4)

Statute → machine-readable specification → golden cases → boundary cases
→ contradiction tests → regression suite, for every encoded rule. The
specifications and fixtures are published so other organisations can
certify their calculations against them.

- **5.1 — Claude Code. A coverage matrix per rule id:**
  - golden: hand-calculated;
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
- **5.5 — Pete (P6), GPT/Codex checking the IP Doctrine.** What is
  published (specifications and fixtures, not necessarily the
  implementation), under which licence, where, and how it is versioned.

**Exit gate:** every kernel rule has all four classes or an accepted,
named gap, and the published package certifies Poltika through the
harness alone. A domain that passes reaches Level 1.

## Step 6: Validation framework and Prediction Ledger v0 (M2-M4)

How Poltika will prove itself, established before it builds impressive
models. The ledger starts early so the clock on an external track record
starts early.

- **6.1 — Claude Code. The validation case.** One schema for every
  validity claim:
  - the claim;
  - its level (rules, aggregates, history, forecast);
  - the target, as a registered variable and period;
  - the reference: a Fact, a hand calculation or an official figure,
    with its source;
  - the tolerance, and why it is that;
  - the model id and version;
  - the result and its date.

  Existing checks become validation cases without changing: spec cases
  and benchmarks (rules), v0.2's cross-validation (aggregates) and
  stored-run replay (reproducibility).
- **6.2 — Claude Code. Validation reports per model**, which set its
  validation status in the model registry and are the evidence for
  graduation (Step 1.6).
- **6.3 — Claude Code. Standard comparators.** Naive baselines (last
  value, trend, seasonal naive) are computed beside every validation
  against history and every forecast, so skill is always measured
  against something simple.
- **6.4 — Claude Code. Ledger v0.**
  - Each entry records:
    - id and registration timestamp;
    - target: a registered variable, with its definition, unit,
      geography, population and period;
    - the resolution source, named in advance;
    - the forecast as an interval or distribution (D_x), never a point
      alone;
    - naive baselines;
    - model id, version and level;
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
  won't be 40-year macro forecasts. They will be small, testable
  predictions, such as a published administrative figure predicted
  before its release (P7).

**Exit gate:** every existing test and comparison is a validation case in
one framework, each model's validation report sets its status, and the
ledger accepts, freezes, timestamps and scores entries. The first
genuinely predictive output is registered before its outcome is
published.

## Step 7: Household microsimulation (M3-M7; IDI when granted)

From individual calculations to population and distributional
consequences, without presenting a synthetic population as reality.

- **7.1 — Pete. Tag `v0.2.0`.** It is ready (`BUILD_PLAN_v0_2.md` 10.3).
- **7.2 — Claude Code, criteria from P4. A confidence grade on every
  population and run:**
  - **Development:** today's independent-marginals population, not an
    estimate for New Zealand;
  - **Public-data (MODERATE);**
  - **IDI-calibrated (HIGHER).**

  A grade is assigned only when its criteria pass. It is never inferred.
- **7.3 — Claude Code, reviewed by GPT/Codex. Joint calibration** (W3.6)
  to published cross-tabulations, and to public survey microdata where
  its licence allows, graded Public-data only if P4's criteria pass.
- **7.4 — Claude Code. Validation against published aggregates** as
  validation cases (Step 6): the Level 2 evidence for the population.
- **7.5 — Claude Code.** Each kernel domain's facts join the population
  as the domain lands.
- **7.6 — Claude Code. Secure-environment runner, output checks and
  survey adapter** (`BUILD_PLAN_v0_3.md` Phase 6; W3.3-W3.5), with Step
  1.4's governance constraints enforced at export.
- **7.7 — GPT/Codex, then Pete. IDI and Longitudinal Business Database
  access** (W3.1-W3.2, P12). Start at M0, because the lead time is
  external.
- **7.8 — Claude Code.** Results by decile, household type, area and age,
  each with coverage and grade.

**Exit gate:** a Public-data population runs the whole available kernel,
reproduces the published aggregates it is checked against within stated
tolerances, and carries its grade. The secure runner passes its tests,
and the access application is lodged.

## Step 8: Fiscal and accounting spine (M4-M8)

Connect households, the Crown and firms, and later the financial and
external sectors, through consistent stocks and flows. A dollar cannot
disappear: if government pays $1b, some other sector receives $1b, before
behaviour.

- **8.1 — GPT/Codex. Source the classifications** from Treasury's
  publications, with decision records where ambiguous:
  - Crown revenue and expense lines;
  - balance-sheet items;
  - net core Crown debt;
  - the NZ Super Fund.
- **8.2 — Claude Code. Sector accounts,** defined in the state schema
  (2.8): households, firms, government, the financial sector and the rest
  of the world. The last two are defined now and populated later. Every
  flow has a payer and a payee. Stocks change only through flows and
  stated revaluations. The invariants are property tests: flows net to
  zero across sectors, balance sheets reconcile, and no unbalanced entry
  is accepted.
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
  statements** as validation cases (Level 2 evidence).

**Exit gate:** a multi-year reform is scored statically, with household,
distributional, Crown line and debt effects, and every invariant holds.
The accounts reconcile with published Crown figures within stated
tolerances.

## Step 9: Historical NZ State Store (M5-M8)

Versioned historical snapshots of New Zealand, built on the variable
registry and the state schema.

- **9.1 — Claude Code, GPT/Codex reviewing the mappings. Connectors**
  for Stats NZ, Treasury and agency publications beneath the data layer
  (ADR-0015's v0.5 connectors). Scheduled refreshes propose new vintages
  for review.
- **9.2 — Claude Code. State snapshots:** for each past period, S_t under
  state schema v0 and later versions, per vintage. Snapshots are
  immutable, and each value is a quantity with its lineage.
- **9.3 — Claude Code. As-of queries:** S_t as it was known on a given
  date, for backtests (Step 13) and ledger scoring (Step 6).
- **9.4 — Claude Code. Gaps are explicit.** A missing state variable is
  labelled missing, never filled silently. An imputed one is an
  assumption, with its method.
- **9.5 — Claude Code. Validation:** the store reproduces its sources
  exactly, as validation cases (Level 2 evidence).

**Exit gate:** for every year in the horizon (P11), the store returns S_t
with lineage, as known at any vintage date, and reproduces its sources.

## Step 10: National Baseline Engine (M6-M10)

The reference trajectory that interventions are measured against: what
happens if nothing changes.

- **10.1 — Claude Code. Population engine:** age, sex, fertility,
  mortality and migration by cohort, and household formation, starting
  from the state store's S_now. Default assumptions come from Stats NZ's
  published projections, and its benchmark is reproducing them.
- **10.2 — GPT/Codex, then Claude Code. Macro baseline as exogenous,
  sourced Assumptions with ranges.** GDP, productivity, employment,
  wages, inflation, interest rates and trade, taken from official
  publications. Poltika does not forecast them here.
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
- **10.6 — Claude Code.** Register the baseline's near-term values in the
  ledger.

**Exit gate:** the baseline to 2065 reproduces He Tirohanga Mokopuna 2025
within a stated tolerance, or attributes every difference to named
assumptions. Every input is traced, and ranges grow with the horizon.

## Step 11: Uncertainty and sensitivity framework (M7-M10)

Uncertainty made native before behavioural and domain complexity arrives.
The data model has carried D_x since Step 2. This step propagates it.

- Propagation of D_x through the kernel, population, spine and baseline:
  interval arithmetic where it is exact, and seeded Monte Carlo on the
  batch engine (P10) otherwise.
- Correlated uncertainties, stated as assumptions.
- One-way, multi-parameter and global sensitivity: which assumptions
  drive which results.
- Uncertainty that grows with the horizon.
- Model cards (Step 1.5) gain each model's uncertainty treatment.

**Gate:** every material result from the kernel, population, spine and
baseline has a propagated interval and a ranked list of the assumptions
that drive it.

## Step 12: Causal Evidence Library (M8-M12, then continuous)

Behavioural relationships from New Zealand estimates, transferred
evidence and explicitly identified assumptions.

- Each entry records:
  - the relationship (exposure to outcome), in registry variables;
  - the estimate, with its D_x;
  - population and period;
  - method;
  - grade: `NZ_CAUSAL`, `NZ_OBSERVATIONAL`,
    `INTERNATIONAL_TRANSFERRED` or `ASSUMED`;
  - external validity;
  - sources;
  - when it was last reviewed, and by whom.
- A transfer protocol records what is needed to use another population's
  estimate.
- First entries are what the state transition engine (Step 14) and the
  first domain need, from published studies, each reviewed. None comes
  from model memory.
- AI-generated and discovered relationships enter as AI hypotheses and
  are promoted only through `Discovery → Hypothesis → evidence →
  validation → human approval → model specification → tests →
  Simulator`. The Discovery and Hypothesis engines are this intake.
- Behavioural scoring is always shown beside the static result.
- Poltika's own estimates (difference in differences, synthetic control,
  regression discontinuity, instrumental variables, matching, structural,
  Bayesian) are reviewed studies with a design registered in the ledger
  before analysis.

**Gate:** every behavioural relationship in use is in the library with a
grade, D_x and review, and results show static and behavioural side by
side.

## Step 13: Historical Validation Laboratory (M9-M13)

- **Backcasts:** start at a past date and run forward using only what was
  known then (as-of queries, Step 9).
- **Policy replay:** replay a past reform whose outcomes are published,
  and compare.
- **Shock replay:** reproduce a past period given the shocks that actually
  happened.
- **Benchmarks** against naive and statistical baselines, and against
  past official projections.

Scored in the validation framework and never tuned: a tuned parameter is
a model change with its own record.

**Gate:** each covered model has published replay and backcast errors
against actuals and baselines, failures included. This is the Level 3
evidence.

## Step 14: National State Transition Engine (M11-M14)

The integrated stage between the national baseline and a large collection
of domain models: S_t → S_t+1 (for example 2029 → 2030 → 2031), using
simple, explicit relationships.

- Transition functions per subsystem (demography, household incomes
  through the kernel and population, labour, Crown accounts through the
  spine, and so on), each simple and stated. Their relationships come
  from the causal library or are stated assumptions.
- A contract per transition function, so a domain engine can replace it
  later without changing the rest.
- Multi-year trajectories from S_now, keeping every accounting invariant.
- Validated by historical replay (Step 13), with forecasts registered in
  the ledger.

**Gate:** an integrated multi-year trajectory runs from S_now with every
invariant holding, and replays history at least as well as naive
baselines. This is the first Level 5 evidence, and the start of Level 4's
forecast record.

## Step 15: Priority domain models (M13-M21, one at a time)

Health, NZ Super and ageing, housing, labour, productivity,
infrastructure, energy and others. P13 orders them by national importance
× tractability × available evidence. The proposed first is fiscal
sustainability and ageing. Each domain replaces or refines a transition
function, and uses the method that fits it:

| Domain | Method |
| --- | --- |
| Health | Microsimulation |
| Housing | Spatial, econometric and agent-based hybrid |
| Electricity | Optimisation and network model |
| NZ Super | Overlapping generations and microsimulation |
| Transport | Network model |
| Macro | Structural, econometric and stock-flow consistent hybrid |

**Gate, per domain:** it does better in historical replay than the
transition function it replaces, has forecasts registered, has graded
relationships, and has every figure traceable.

## Step 16: Federated Model Graph (M15-M21)

Validated domain models connected through the common state and the
accounting spine. Each keeps its contract. Invariants hold across
engines, conflicting outputs are refused as contradictions, and coupled
runs check convergence.

**Gate:** two or more domain models run coupled, keep every invariant,
and reproduce history at least as well as separately (Level 5).

## Step 17: Continuous State Estimation (M17-M22)

Poltika's estimate of New Zealand updates as observations arrive. Each
resolved ledger miss gets a diagnosis: the prediction failed because X;
the candidate explanations are A, B and C; the evidence supports B. Each
parameter or model change is a reviewed change record ("parameter
changed from X to Y"). Historical predictions stay frozen.

**Gate:** one full cycle of observe, forecast, error, diagnosis and
approved update is on record for a model.

## Step 18: Cost of delay and scenario discovery (M19-M21)

The first high-value decision-intelligence uses of the integrated engine.

- **Cost of delay** (P16): how outcomes, and the adjustment needed to
  meet a stated target, change as an intervention's start date moves,
  from scenario families that vary only the start date, with D_x.
- **Scenario discovery:** which combinations of uncertain assumptions and
  policy settings lead to outcomes of concern, searched over the
  uncertainty framework.

**Gate:** a cost-of-delay curve and a scenario-discovery result for one
fiscal question, each with its interval and evidence chain.

## Step 19: Value of information (M20-M22)

Before searching large policy spaces, Poltika should be able to say: "the
answer depends heavily on parameter X, and our evidence for X is poor."
Sometimes the right result isn't another simulation. It is "we need
better evidence before making this decision."

- The expected value of perfect information (EVPI) per uncertain
  parameter, under a stated objective.
- The expected value of sample information (EVSI) for a proposed study.
- A ranked list of the unknowns that most change the decision, linked to
  their causal-library entries.

**Gate:** where two options differ mainly through one parameter, Poltika
names it, estimates its EVPI, and gives the EVSI of a named study design.

## Step 20: Policy-space optimisation (M21-M24)

Only once the model is credible enough.

- **Preconditions:**
  - the causal credibility gate (P14): every relationship the search
    relies on meets a stated minimum grade and has been replayed;
  - the relevant models have reached Level 3 at least.
- People state the objectives and constraints. For example:
  - debt to GDP in 2065 below 60%;
  - real GDP per capita in 2065 above the baseline;
  - poverty in 2065 no higher than the baseline;
  - plus environmental, distributional, fiscal and implementation
    constraints.
- Poltika returns the Pareto-efficient feasible set, with trade-offs,
  uncertainties, assumptions, robustness across D_x, and the value of
  information (Step 19) for the parameters that separate the options.
- It never returns a single recommendation, and it holds no default
  objective.

**Gate:** every member of a returned set reproduces as an ordinary
scenario, with its trade-offs, assumptions and decision-relevant unknowns
shown.

## Step 21: Public Futures Laboratory (M23-M25)

**Trust gate first:**

- the models behind it have reached the levels its claims need;
- production hardening: threat model, penetration test, access control,
  encryption, backups, incident response, monitoring and performance;
- independent scrutiny by specialists in economics, econometrics,
  statistics, public finance, New Zealand policy, Māori data governance
  and security, with criticisms and responses published;
- a published ledger record, misses included.

**Scope:**

- Baseline, policy and alternative scenarios at 2030, 2040, 2050 and
  2065.
- GDP per person, wages, taxes, housing, health, Crown debt, retirement,
  distributional effects, infrastructure and environmental indicators.
- Every chart answers: why? source? assumptions? uncertainty? who is
  affected? what would change this result? It also shows its level.
- No scores and no winners.

**Gate:** a person who didn't build Poltika can answer all six questions
for any chart.

## Step 22: AI reasoning and search layer (M24-M26)

Natural-language interaction, hypothesis generation, research and
explanation, over validated machinery. AI operates the instrument; it
isn't the instrument.

- An LLM translates a request into registered variables, constraints and
  scenarios, and confirms any consequential interpretation.
- The engines execute and the optimisers search.
- The LLM explains the verified results. Every figure it shows is checked
  against the engine output before it is shown. It supplies no number and
  no relationship.
- Hypotheses it generates go to the causal library's intake as AI
  hypotheses.
- `src/poltika/llm/` is built here, under `doctrine/llm_boundaries.md`.

**Gate:** on a benchmark set of requests, every figure the AI shows
matches the engine, and every interpretation it made is shown and can be
confirmed.

## ∞: Continuously improving national digital twin

Not a release. It is what everything above produces:

`OBSERVE → DISCOVER → HYPOTHESISE → TEST → SIMULATE → ASSURE → COMPARE → DECIDE → OBSERVE REAL OUTCOME → RECALIBRATE`

Poltika is called a digital twin only at Level 7.

---

## Releases

A release is tagged when its steps' exit gates pass. Levels are
graduated separately, on validation evidence.

| Release | Steps | Target | Level evidence |
| --- | --- | --- | --- |
| v0.1, v0.1.5 | Done | | |
| v0.2 | Ready to tag (7.1) | M0 | |
| v0.1.6 | 3B | By M6 (1 April 2027) | |
| v0.3 | 1; 2; 3A; 5.1 for Tier 1 | M0-M3 | |
| v0.4 | 4; 5; 6; 3C | M2-M5 | Level 1 for kernel domains |
| v0.5 | 7; 8; 3D | M4-M8 | |
| v0.6 | 9; 10; 3E | M6-M10 | Level 2 |
| v0.7 | 11; 12; 13 | M8-M13 | Level 3 |
| v1.0 | Gates 1-13, plus the hardening an outside analyst needs | M13 | Level 3 |
| v1.x | 14 | M11-M14 | Level 4 when the ledger supports it; Level 5 begins |
| v2.0, v2.x | 15-17 | M13-M22 | Level 5 |
| v3.0, v3.x | 18-20 | M19-M24 | Level 6 |
| v4.0, v4.x | 21-22 | M23-M26 | |
| ∞ | | | Level 7 |

**v1.0 definition (testable).** For a structured package of changes
inside its supported kernel domains, Poltika answers:

- **what happens:** static results, and behavioural ones where the
  causal library holds a graded relationship;
- **to whom:** by decile, household type, area and age, on a graded
  population;
- **when:** year by year, through the Crown accounts, against the
  national baseline;
- **through what mechanism:** the evidence-graph chain to law and
  evidence;
- **with what confidence:** evidence classes, propagated uncertainty, the
  population grade, the models' levels, replay errors and the ledger's
  record;
- **compared with what alternatives:** the baseline and other scenarios.

The models it relies on have reached Level 3, and an independent analyst
can reproduce and challenge the result without the builders. A
"supported domain" has an approved specification, a complete conformance
matrix, an independent review and current values.

## What changes in the current plans

| Current plan | Under this plan |
| --- | --- |
| `BUILD_PLAN_v0_3.md` | Kept. v0.3 also ships Step 1, Step 2 (Phase 1 becomes 2.7) and Step 5.1 for Tier 1. The references in its "Not in v0.3" list point here. |
| `BUILD_PLAN_v0_1_6.md` | Kept as lane 3B. The 1 April 2027 deadline stands. |
| `BUILD_PLAN_v0_2.md` | Done. Tag it (7.1). Its population becomes the Development grade. |
| ROADMAP v0.4, scenario engine | Step 8.5 |
| ROADMAP v0.5, uncertainty, assurance and historical baseline | Connectors to Step 9; historical baseline to Steps 9-10; assumption register and Monte Carlo to Step 11; backtesting to Step 13; model cards to Step 1.5 |
| ROADMAP v0.6, long-term fiscal model | Step 10, then Step 14. Its constrained search moves to Step 20. |
| ROADMAP v0.7, decision-intelligence product | APIs and lineage to Step 4; the public interface to Step 21; the LLM to Step 22; users, permissions and audit to v1.0 hardening and Step 21 |
| ROADMAP v1.0 | Redefined around the question and Level 3 (above) |
| Discovery and Hypothesis | The causal library's intake (Step 12) |
| v2-v5 capability tracks | Steps 14-22 and ∞, climbing the ladder |

## Carried workstreams (`ROADMAP_REALIGNMENT.md`)

| Workstream | Under this plan |
| --- | --- |
| W1 Review debt and cadence | The queue and gate rows stay. The cap is suspended (P17). |
| W2 Policy coverage throughput | Step 3. The `new-policy` skill gains registry entries, the conformance matrix, a model-registry entry and evidence classes. |
| W3 Real-data access | Step 7, with governance from 1.4 |
| W4 Batch engine | Decided by M4 (P10), before Step 8's multi-year population runs |
| W5 Maintenance budget | Stays. The historical horizon (W5.3) is P11, due at M1. |
| W6 Shared household model | Step 2.7 |
| W7 Household dependency graph | Lane 3A, sharing node ids with Step 4 |
| W8 Multi-year parameters | Lane 3B |
| W9 Roadmap reorder | Superseded by ADR-0018 |
| W10 Coverage map | Extended by lanes 3C-3E |

## What Poltika never builds

- No LLM pretending to be five million New Zealanders.
- No score for a party's policy, and no "this plan wins".
- No secret normative objective function.
- No black-box AI forecast of GDP, or of anything else.
- No silently changing models: every change is a recorded change (Steps
  1.5, 17).
- No point estimate where the uncertainty is large (Steps 1.3, 2.6, 11).
- No synthetic population presented as reality (Step 7.2).
- No policy optimisation before causal relationships are credible (Step
  20's preconditions).
- No "digital twin" branding before Level 7.
- **Never optimise the model instead of the country.** Ledger and
  validation scores are monitored, never targeted. A change made to
  improve a score needs the same diagnosis record as any other change.

## Decisions

Pete approved the first version of this plan on 29 September 2026
("Approve and proceed all"), then revised the sequence the same day. The
decisions below carry over, with their step numbers updated.

**Decided 29 September 2026:**

- **P1:** the approach (reconciliation against what's built, month
  targets, releases tagged at step gates, v1.0 defined around the
  question). The revised sequence is Pete's own. Its month targets and
  release mapping are redrafted here, and stand unless Pete changes them.
- **P2:** a caller-asserted household fact is a **Scenario** input.
- **P3:** the precision rule (Step 1.3).
- **P4, names:** Development, Public-data (MODERATE) and IDI-calibrated
  (HIGHER). The criteria come with Task 7.2.
- **P5, interim rule:** no output disaggregated by ethnicity or iwi until
  the governance process is agreed. Engaging people with standing in
  Māori data governance is Pete's, and still open.
- **P9:** the kernel follows the direction's order (lanes 3C-3E).
- **P12:** apply for IDI access. W3.1 documents the route first; lodging
  it is Pete's.
- **P16:** the cost-of-delay definition (Step 18).
- **P17:** the review-debt cap is suspended ("Ignore PR cap"). The review
  queue is still kept.
- **Carried:** ADR-0017, the shared household model, accepted with its
  three recommended answers (`BUILD_PLAN_v0_3.md` D6).

**Open:**

- **P6:** conformance publication (Step 5.5).
- **P7:** the timestamping service and the first genuinely predictive
  targets (Steps 6.4-6.5).
- **P8:** Evidence Intelligence as the first product.
- **P10:** the batch engine, by M4.
- **P11:** the historical horizon for the state store, backtests and
  replays, by M1.
- **P13:** the domain-model order.
- **P14:** the causal credibility gate for policy search.
- **P18:** the tolerances for each level's graduation, set when each
  level is first reached. Pete decides each graduation on the validation
  evidence.
- **P19:** state schema v0's scope (Step 2.8).
- **v0.3 D1-D3:** each Tier 1 domain's slice, the disposable-income
  definition and the income-adequacy measures, from Phase 0's sourcing.

(P15, the digital-twin criteria, is replaced by Level 7.)

## Progress

| Step | State |
| --- | --- |
| Plan | Revised to 22 steps, 29 September 2026 (ADR-0018) |
| 1-22 | As in "Where Poltika stands". Each row is updated as its tasks land. |
