# Poltika roadmap

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

**Direction approved:** 3 October 2026, [ADR-0021](adr/0021-economist-first-pilot-programme.md).
[BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md) is the single active
master build order. This roadmap explains the direction; detailed tasks,
dependencies and gates belong in that programme. Live evidence, owners and
blockers are in [PROGRAMME_STATUS.md](PROGRAMME_STATUS.md).

Poltika aims to answer: if New Zealand changes X, what happens, to whom,
when, through what mechanism, with what confidence, and compared with what
alternatives? People choose objectives and trade-offs. Poltika measures
consequences. The eventual destination remains a validated computational
representation of New Zealand and its economic/policy systems.

Build complete analytical vertical slices, validate them with independent
evidence, put them in front of real users, and grow common infrastructure
from multiple real model requirements. Reuse working capabilities; the new
programme changes execution order while preserving sound architecture.

## Near term

`Stabilise → household tax-transfer system → assurance and Analyst Workbench
→ Pilot 1 → representative population microsimulation → fiscal/distributional
analysis and economist-grade report → Pilot 2`

The household system connects sourced personal income tax, Jobseeker
Support, Sole Parent Support and Supported Living Payment to existing WFF
and Accommodation Supplement through a shared household model and an
explicit computational graph. It produces supported disposable-income and
incentive measures with verified calculations, provenance and coverage.
[BUILD_PLAN_v0_3.md](BUILD_PLAN_v0_3.md) is this detailed active lane.
Minimum semantics support those real models; a completed universal registry,
national state schema or general evidence graph is not its prerequisite.

The Analyst Workbench is the first analyst product surface. Its existing
registry, scenario checks, results blocks and CSV/Excel backend are reused
and completed into a usable end-to-end workflow. Backend implementation is
not evidence that its UI or an external pilot is complete. ADR-0018's design
acceptance remains a separate recorded question under ADR-0020.

Pilot 1 asks whether an external analyst can productively answer a real
supported household-reform question, inspect evidence and reproduce/export
results. It tests usefulness, speed, comprehension, auditability and workflow
friction. National population estimates are not required for this pilot.

An early **policy-claim intake** use case (C14a) maps source-preserved,
independently checked public policy proposals into *supported* household
scenarios through the same Analyst Workbench. An optional campaign-policy
pilot (D16a) can demonstrate example-household consequences without treating
party announcements as enacted rules or claiming national costs, full
manifesto coverage or comparative party scores. These overlays do not delay
Pilot 1 or create a separate product.

Next, harden the existing PopulationDataset, batch runner, weighting and
calibration against representative inputs and authoritative aggregates.
Existing synthetic development results remain labelled synthetic and are
not national estimates. Direct fiscal accounting and distributional output
then support a deterministic report containing specification, baseline,
reform, fiscal effect, affected population, winners/losers, income groups,
household types, incentives, data, assumptions, validation, provenance and
limitations. Unresolved annualisation/income definitions require explicit
reviewed decisions rather than implicit combined totals.

Pilot 2 asks whether an external analyst trusts and would professionally use
those population estimates, understands their limitations and finds the
workflow useful alongside existing Excel/R/Python practice. Record workflow,
reproduction and feedback evidence; expansion follows real analytical demand.

After validated national distributional and direct fiscal reporting (E/F),
the **Budget analysis runner** (F24a) should accept each newly published NZ
Budget as a versioned set of official sources and initiatives, reuse
validated models to analyse supported measures, compare methodologically
compatible estimates and publish explicit coverage and gaps. It is a
repeatable analyst workflow, not a promise to simulate an entire Budget on
release day or a prerequisite for Pilot 2.

## Medium term

`Demand-driven statutory coverage → historical validation → causal/behavioural
models → formal uncertainty → dynamic state and national baseline → domain models`

Add statutory domains according to pilot/use-case pull and their maintenance
cost. Build retained historical policy/data states, as-of execution, replay
and a prediction/model-error ledger before sophisticated forecasting claims.
Historical Budget as-of replay (I29a) uses these capabilities to keep the
information available at announcement separate from later outcomes.
Budget claims about multi-year GDP, employment, inflation or debt wait
for separately validated behavioural, fiscal and macroeconomic models.
Add empirically sourced behavioural mechanisms individually, keeping
mechanical and behaviour-adjusted results separate and propagating uncertainty.

Introduce NZState(t), state transitions and a national baseline when actual
validated models require them. Multi-year trajectories remain conditional on
stated assumptions and are checked against historical/official trajectories.
Domain models declare inputs, outputs, parameters, time step, evidence,
uncertainty and validation. Labour, housing, health, education, infrastructure,
firms/productivity, environment, transport and energy are candidates whose
priority must be earned by analytical demand.

## Long term

`Model composition/federation → state estimation → spatial/production synthetic
state where justified → validated digital twin → decision intelligence
→ trusted public/research infrastructure → AI`

Generalise the graph and federate only when real models need independent
execution. Continuous estimation and reconciliation against observations,
spatial state, production synthetic populations and agent-based methods are
introduced only where validated requirements justify them. “Digital twin”
is an operational claim only after the programme's M validation gate.

Decision intelligence calculates cost-of-delay, value-of-information,
feasible policy search and Pareto trade-offs for objectives/constraints
people specify. Public/research interfaces need sufficient trust, permission
and governance. The public campaign-policy and Budget explorer is Phase O
(Task 51), while its bounded, non-public analytical workflows arrive earlier
in C/D/F/I. No political party/manifesto ranking or policy endorsement. AI comes above verified results and validated models:
translation, explanation, orchestration, hypothesis generation and a
human-gated research loop. It never supplies statutory/numerical ground truth.

## Permanent constraints, releases and planning history

Primary NZ sources, epistemic classification, provenance, visible unknowns,
Spec/Benchmark/Regression tests, protected statutory values, clean-room
boundaries and independent review remain permanent governing constraints.
ADR-0020's delegated acceptance and Pete's retained decisions remain active.
Statutory source currency and new policy years proceed in parallel through
[BUILD_PLAN_v0_1_6.md](BUILD_PLAN_v0_1_6.md), including the 1 April 2027 deadline.

Releases are tags supported by their actual gates, not substitutes for
capability evidence. At reconciliation v0.1.0 is tagged; v0.1.5 still lacks
a recorded external pilot/tag, and v0.2 awaits Pete's tag. Its
[release-closeout plan](BUILD_PLAN_v0_2.md) remains available until that action.
Later version labels do not reinstate the old release sequence.

ADR-0019's sequencing is superseded; its enduring common semantics,
model governance, validation, uncertainty, human control and long-term
national-system principles remain. Exact historical planning snapshots
live in [docs/archive/](docs/archive/README.md); ADRs, release evidence and
reviews retain their permanent locations. Historical references explain
past decisions and never choose the next implementation task.
