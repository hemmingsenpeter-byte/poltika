# Poltika Roadmap

This is a release-level direction, not an implementation backlog. Each release
has a technical purpose and an exit gate. Detailed tasks belong in the active
release's build plan; `BUILD_PLAN.md` remains the frozen authority for v0.1,
and `BUILD_PLAN_v0_1_5.md` holds v0.1.5's.

## Planning status

Operative. The sequence below superseded the Roadmap Doctrine's original
capability-sequence framing per ADR-0008 (2026-09-21), which records the
dependency reasoning for this specific order — see BUILD_PLAN.md's Roadmap
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

## v0.1.5 - Evidence intelligence and pilotability

Make v0.1 usable by someone who did not build it, and keep the evidence
behind every number visibly current. No new policies or data. Report
pending, open-ended, expiring and stale rates and sources with each result;
close the in-work tax credit gap when the evidence allows; ship a
reproducible deployment and a pilot-user guide; tidy the repository's review
records. `BUILD_PLAN_v0_1_5.md` holds the tasks (draft, pending Pete's
approval).

**Exit gate:** A pilot user who did not build Poltika deploys it, answers a
supported WFF and Accommodation Supplement household question, and sees for
every number its sources and whether any rate is pending or expiring.

## v0.2 - Authoritative data foundation

Replace proof-of-concept inputs with reproducible, versioned NZ data. Add Stats
NZ and Treasury connectors, historical fiscal and tax/transfer series, CPI,
GDP, population, labour, wages/incomes, household demographics, and government
revenue/expenditure. Keep a governed manual path for authoritative sources
without APIs.

Define canonical variables, units, frequency, nominal/real and stock/flow
semantics, geographic/population dimensions, source vintages, mappings, schema
versions, a data dictionary, and a transformation registry. Validate schemas,
types, units, missing/duplicate records, ranges, continuity, revisions, and
checksums. Separate raw, processed, and curated data; add a dataset registry,
caching, migrations, scheduled refreshes, logging, ingestion tests, and CI.

Reconstruct historical revenue, expenditure, operating balance, debt,
interest, nominal GDP, and debt/GDP with inflation and population scaling.
Every material input retains its chain:

`value -> transformation -> dataset -> source -> publication -> vintage -> retrieval date`

**Exit gate:** For a historical date, Poltika reconstructs the major fiscal
and economic baseline from authoritative NZ data and traces every material
input.

## v0.3 - Policy interaction graph

Define variables, parameters, rules, nodes, dependencies, feedback, and
calculation order. Execute acyclic dependencies as a DAG; resolve dependencies,
detect cycles, and handle genuine feedback loops explicitly. Give modules a
common contract for inputs, parameters, outputs, units, assumptions,
provenance, version, and valid time range.

Build interaction slices across PAYE/disposable income, transfers, wages,
population, and fiscal balance/debt. Test multi-step changes, such as a
minimum-wage increase, and add dependency-chain explanations and frozen
regression scenarios.

**Exit gate:** One parameter change recalculates all declared downstream
variables in the correct order, with an explainable dependency chain.

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

**Exit gate:** An analyst can create, save, reproduce, and compare multi-policy
NZ scenarios over time.

## v0.5 - Uncertainty and assurance

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

**Exit gate:** Every material result can be traced, stress-tested, challenged,
and reproduced.

## v0.6 - Discovery engine

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

## v0.7 - Hypothesis engine

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

## v0.8 - Long-term NZ system model

Connect demographics, labour, productivity, tax revenue, major spending
categories, and debt dynamics. Model population, participation, wages, GDP,
income tax, GST, corporate tax, health, education, NZ Super, welfare,
infrastructure, interest, borrowing, and debt/GDP at justified detail. Support
long-run trajectories with uncertainty that grows with the horizon.

Compare a documented Poltika baseline with Treasury publications and explain
differences. Add constrained scenario search over specified parameters;
optimisation results are not policy recommendations.

**Exit gate:** Poltika generates internally coherent long-run NZ fiscal and
economic scenarios across connected systems.

## v0.9 - Decision-intelligence product

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
