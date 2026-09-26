# Poltika Roadmap

This is a release-level direction, not an implementation backlog. Each release
has a technical purpose and an exit gate. Detailed tasks belong in the active
release's build plan:

- `BUILD_PLAN.md` remains the frozen authority for v0.1;
- `BUILD_PLAN_v0_1_5.md`, `BUILD_PLAN_v0_1_6.md` and `BUILD_PLAN_v0_2.md`
  hold theirs;
- `BUILD_PLAN_v0_3.md` holds v0.3's, approved with ADR-0015, with its Phase 0
  scoping the policies;
- `ROADMAP_REALIGNMENT.md` holds the cross-release workstreams.

## Planning status

Operative. The sequence below superseded the Roadmap Doctrine's original
capability-sequence framing per ADR-0008 (2026-09-21), amended by ADR-0014
(static microsimulation in v0.2) and ADR-0015 (the v0.3-v0.7 realignment and
Discovery and Hypothesis after v1.0). They record the dependency reasoning
for this order — see BUILD_PLAN.md's Roadmap
Doctrine section for the summary. Nothing here changes v0.1 scope,
approvals, or acceptance criteria.

## v0.1 - Deterministic foundation

Deliver independently reviewed Working for Families and Accommodation
Supplement specifications and calculation slices, benchmark and regression
tests, a cross-policy household scenario, and provenance-tagged frozen data
acquired manually. No live statistical API is required. `BUILD_PLAN.md` owns
the detailed scope and acceptance criteria.

**Exit gate:** A supported household scenario runs end to end with
deterministic, source-traceable results for both policies and passes the frozen
v0.1 review and test gates.

## v0.1.5 - Evidence and explainability bridge

Turn the v0.1 calculator into a system that shows its work, without
broadening its scope. Every result carries ordered calculation steps with
intermediate values, stable rule ids, ranked and period-checked evidence,
a deterministic plain-language explanation, an assumption ledger and
structured review reasons. A thin analyst interface and one external pilot
test it. No new policies, data or simulation. `BUILD_PLAN_v0_1_5.md` holds
the tasks (approved 25 September 2026).

**Exit gate:** An external pilot user can take any supported WFF and
Accommodation Supplement result and find where the number came from, which
rule and source govern it, what was assumed and what is missing, with every
explanation tested against the calculation and no open P0 or P1 findings.

## v0.1.6 - Keep v0.1 current

Every v0.1 parameter value and reference period ends on 1 April 2027. Source
and implement the 2027-28 year, settle the 2026-27 in-work tax credit once
the year is complete, and make source currency a scheduled check. No new
policy or capability. `BUILD_PLAN_v0_1_6.md` holds the tasks.

**Exit gate:** Every golden household calculates for both 2026-27 and
2027-28 from approved, sourced values, with the 2026-27 results unchanged.

## v0.2 - Static population microsimulation

Run the unchanged v0.1 engines across a weighted population, under current
law and a reform, and aggregate the differences. Results cover
winners and losers, income deciles, household types, Accommodation
Supplement areas, static entitlement cost by component, WFF and AS
withdrawal rates, and deterministic parameter sweeps. Every figure carries
its coverage, explanation, evidence and reproducibility record.

It is built on a data layer (manifested immutable snapshots, a dataset
registry, canonical variables, validation) and a synthetic development
population calibrated to published tables. No output is a New Zealand
estimate until real microdata is available. `BUILD_PLAN_v0_2.md` holds the
tasks (ADR-0014, accepted 26 September 2026).

**Exit gate:** In one reproducible run, with no code edited, a WFF reform
produces household, distributional, area and fiscal results with weighted
coverage, a driver explanation, evidence and a rerunnable record.

## v0.3 - Income tax, main benefits and the household graph

Specify and implement income tax and the main benefits needed for
disposable income to v0.1's standard, each scoped from primary sources
before anything is built. Replace per-policy inputs with one shared
household model that holds each fact once. Order policy calculations per
household in a dependency graph whose every edge comes from a
specification, refuse unresolved cycles, and explain dependency chains.
Produce disposable income, effective marginal tax rates and sourced
income-adequacy measures for supported households. Make Poltika runnable
inside a secure data environment that exports only checked aggregates.
`BUILD_PLAN_v0_3.md` holds the tasks (ADR-0015).

**Exit gate:** One policy's output feeds another's input for a real
household, calculated in source-derived order and explained, with income
tax and at least the first main benefit independently reviewed and
benchmarked, and WFF and AS results unchanged from v0.2.

## v0.4 - Scenario engine

Define scenarios with identity, baseline, interventions, timing, assumptions,
overrides, model version, data vintage, ownership, and timestamps. Support
parameter changes, new/removed policies, phased or temporary policies,
indexation, and multi-policy packages. Compare against explicit baselines and
other scenarios over annual trajectories.

Add deterministic run IDs, standard fiscal, household, distributional, and
macro result schemas, and persistence for saving, cloning, rerunning,
archiving, and comparing versions. Preserve the model commit, data and
parameter versions, assumptions, and configuration.

v0.2 already delivers single-year static reforms of WFF and the
Accommodation Supplement (ADR-0014). v0.4 extends them to the above.

Decide by the start of v0.4 whether population runs need a batch engine,
with the per-household engine kept as the reference it is tested against
(`ROADMAP_REALIGNMENT.md` W4).

**Exit gate:** An analyst can create, save, reproduce, and compare multi-policy
NZ scenarios over time.

## v0.5 - Uncertainty, assurance and the historical baseline

Register material assumptions with rationale, evidence, uncertainty, owner,
review date, and applicable models. Support ranges/distributions, one-way and
multi-parameter sensitivity, seeded Monte Carlo, and outcome ranges. Backtest
using information available at historical dates and calibrate against recorded
targets without silent tuning.

Check missing provenance, stale data, unsupported assumptions, extreme
extrapolation, unit mismatches, untested changes, failed validation, and
incompatible versions. Attach structured reliability metadata rather than
arbitrary AI confidence scores. Publish model cards covering methods,
validation, limitations, and known failure modes.

Add Stats NZ and Treasury connectors beneath the v0.2 data layer, with
scheduled refreshes that propose new vintages for review. Reconstruct
historical revenue, expenditure, operating balance, debt, interest, nominal
GDP and debt/GDP, with inflation and population scaling. Every material
input keeps its chain:

`value -> transformation -> dataset -> source -> publication -> vintage -> retrieval date`

(Moved from v0.2 by ADR-0014, then to v0.5 by ADR-0015, where backtesting
is its first consumer.)

**Exit gate:** For a historical date, Poltika reconstructs the major fiscal
and economic baseline from authoritative NZ data and traces every material
input. Every material result can be traced, stress-tested, challenged,
and reproduced.

## v0.6 - Long-term NZ fiscal model

Connect demographics, labour-force participation, wages, tax revenue,
major spending categories (health, education, NZ Super, welfare,
infrastructure), interest and debt as a transparent accounting model.
Behavioural relationships and macro aggregates such as nominal GDP enter
as exogenous, stated, sourced assumptions, registered through v0.5's
assumption register, not as forecasts Poltika generates. Support long-run
trajectories with uncertainty that grows with the horizon.

Compare a documented Poltika baseline with Treasury's published long-term
projections and explain differences. Constrained scenario search over
specified parameters may follow; optimisation results are not policy
recommendations. Behavioural and GDP modelling belong to the v2 track
(ADR-0015).

**Exit gate:** Poltika generates internally coherent long-run NZ fiscal
scenarios across connected systems, with every assumption stated and
every difference from Treasury's projections explained.

## v0.7 - Decision-intelligence product

Expose stable APIs for datasets, variables, policies, scenarios, simulations,
results, provenance, and assurance. Build an analyst workflow to explore,
build, simulate, compare, investigate, and report. Provide structured scenario
editing, fiscal and household visualisations, assumptions, sensitivity, and
click-through result lineage.

An LLM may retrieve evidence, translate questions into candidate scenarios,
call models, and explain results; it cannot fabricate calculated figures.
Confirm consequential interpretations when ambiguous. Add reproducible
reports, users, organisations, permissions, scenario ownership, and audit
logs. Begin formal security and privacy work for institutional use.

**Exit gate:** An analyst who did not build Poltika can complete a scenario
analysis and understand how its results were produced.

## v1.0 - Production Poltika

Harden architecture, interfaces, schemas, data/model governance, licensing,
revision handling, and historical reproducibility. Complete threat modelling,
penetration testing, access control, encryption, dependency management,
backups, incident response, performance benchmarks, monitoring, and failure
handling. Publish architecture, API, methodology, model, data, developer,
analyst, and governance documentation.

Obtain independent scrutiny from economics, econometrics, statistics, public
finance, NZ policy, architecture, and security specialists; document
criticisms and responses. Maintain benchmarks against historical outcomes,
official tax and transfer calculations, comparable government estimates, and
pathological cases. Validate reference scenarios for tax reform, NZ Super,
infrastructure, demographic shocks, and productivity. Prepare accessibility,
operational, security, AI-governance, and model-risk materials for adoption.

**Exit gate:** An independent analyst can construct a supported NZ policy
scenario, reproduce its results, trace material outputs to authoritative
evidence, inspect uncertainty and assumptions, and challenge the methodology
without the original builders.

## Beyond v1.0 - Capability tracks

- **Discovery and Hypothesis (moved from v0.6-v0.7 by ADR-0015).** They
  extend a hardened system rather than being part of hardening it, and
  the v1.0 definition doesn't need them. Their scope is kept below.
- **v2, Economic Digital Twin:** Deeper households, firms, industries, trade,
  capital, housing, labour, regional economies, and behavioural microsimulation.
- **v3, Physical NZ:** Infrastructure networks, transport, electricity, water,
  land, housing stock, geospatial models, and physical constraints.
- **v4, Adaptive Digital Twin:** Better causal models, justified agent-based
  simulation, continuous calibration, near-real-time signals, and feedback
  between observed and modelled outcomes.
- **v5, National Decision Intelligence:** Connect economic, fiscal,
  demographic, social, environmental, and physical systems across decades.

The long-run loop is:

`OBSERVE -> DISCOVER -> HYPOTHESISE -> TEST -> SIMULATE -> ASSURE -> COMPARE -> DECIDE -> OBSERVE REAL OUTCOME -> RECALIBRATE`

After v0.1 ships, freeze its build plan and create a detailed plan for the
next approved release. Keep later implementation tickets out of this roadmap.

### Discovery engine (post-v1.0)

Offer on-demand research questions specifying outcome, population, geography,
period, candidate variables, and exclusions. Find compatible datasets using
semantic metadata. Explore trends, lags, cohorts, regions, anomalies, breaks,
and associations with sample-size, multiple-testing, robustness, and holdout
controls where possible. Store questions, data, transformations, tests,
results, robustness, and limitations; rank by methodological quality, not
political desirability.

Present evidence, charts, methods, and alternative interpretations.
Association must never be represented as established causality.

**Exit gate:** Poltika produces reproducible candidate relationships for
human investigation without asserting causality.

### Hypothesis engine (post-v1.0)

Turn discoveries and human questions into competing causal hypotheses with
mechanisms, exposures, outcomes, confounders, mediators, moderators,
predictions, falsifiers, and evidence requirements. Include null and
measurement explanations. Use proposed causal graphs, evidence retrieval,
adversarial review, and causal methods only where their assumptions can be
examined and approved. Grade plausible mechanisms, observed associations,
and credible causal evidence separately.

The Simulator promotion gate is:

`Discovery -> Hypothesis -> evidence -> validation -> human approval -> model specification -> tests -> Simulator`

**Exit gate:** Competing explanations can be tested without promoting
speculative relationships into deterministic models.
