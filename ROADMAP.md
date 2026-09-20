# Roadmap

`BUILD_PLAN.md` is authoritative for frozen scope, task order, and release
gates. This document names later capabilities without adding v0.1 work.

## v0.1

- Source-grounded, independently benchmarked WFF and Accommodation
  Supplement vertical slices; deterministic cross-policy scenarios,
  provenance, scenario/version persistence, and API integration per
  `BUILD_PLAN.md`.
- Acquire only the external statistical datasets those vertical slices need
  as immutable, provenance-tagged snapshots; no live statistical API.
- Represent scenario parameter changes as validated, machine-readable data
  distinct from the reviewed policy baseline. This preserves later automated
  generation without building Policy Search now.

## Fixed Next Steps

- v0.1.5: evidence intelligence and pilotability.
- v0.2: more policies, uncertainty, and narrow on-demand Discovery.

## Later Capabilities

The post-v0.2 sequence remains capability-driven: Hypothesis, deeper
Assurance, cross-domain Discovery, fiscal and behavioural modelling, and
system-wide integration toward v1.0. Policy Search is a later capability
on the path to a progressively improving New Zealand Digital Twin, when
the relevant domains and uncertainty models can support meaningful searches.
It is not a v0.1 feature or a new fixed release gate.

- Automate external data ingestion (Stats NZ API connector, scheduled
  refreshes, additional government-source connectors, schema-change
  detection, broader dataset coverage) beneath the same canonical-variable
  contract established in v0.1, when a later capability needs it.

### Policy Search (future)

Humans define objectives, hard constraints, and acceptable trade-offs.
Policy Search explores parameter combinations and effective-dated policy
pathways by submitting validated scenarios to the same deterministic
Simulator, then uses Assurance and uncertainty analysis to identify
feasible sets and trade-offs. It must not select a preferred political
outcome or encode one through hidden weights.

Methods may include exhaustive and grid search for small spaces;
random/Monte Carlo sampling, Latin hypercube sampling, and Bayesian
optimisation for larger or expensive spaces. Multi-objective searches may
produce Pareto frontiers instead of one optimum. Constraint satisfaction,
robust decision-making across plausible futures, and sensitivity analysis
would show which candidates remain feasible and why others fail.

Scenario ensembles may vary productivity, fertility, migration, interest
rates, inflation, technology, climate, international trade, commodity
prices, and behavioural responses. Searches may combine interventions
across policies and vary their timing (for example, infrastructure in 2028,
tax in 2030, migration in 2032, retirement settings in 2035). These are
future modelling capabilities, not v0.1 parameter or dataset requirements.

The conceptual progression is deterministic simulation, interconnected
domains, scenario comparison, uncertainty and sensitivity analysis, Policy
Search, robust pathway exploration, and an increasingly current Digital
Twin. Poltika exposes the policy possibility space; humans judge its
desirability.
