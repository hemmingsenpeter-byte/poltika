# Poltika Roadmap

This is the release-level direction, not an implementation backlog. The
twenty-step build plan, what already exists against each step, the tasks
and the open decisions are in `BUILD_PLAN_PROGRAMME.md`. Detailed tasks
for each release are in its own plan:

- `BUILD_PLAN.md` remains the frozen authority for v0.1;
- `BUILD_PLAN_v0_1_5.md`, `BUILD_PLAN_v0_1_6.md` and `BUILD_PLAN_v0_2.md`
  hold theirs;
- `BUILD_PLAN_v0_3.md` holds v0.3's, which now also covers Step 1;
- later releases get a detailed plan when they start.

## Planning status

Operative from 29 September 2026. ADR-0018 records Pete's direction: build
Poltika as a decision instrument, in twenty steps, with targets in months.
It supersedes ADR-0015's sequence (and through it ADR-0008's and
ADR-0014's). Nothing here changes v0.1's scope, approvals or acceptance
criteria, or anything already built.

## The question

Poltika is built to answer increasingly difficult versions of one
question:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

Each release answers a harder version of it. A digital twin is what many
defensible answers add up to, so Poltika starts small: represent one
piece of New Zealand correctly, then two, then ten; connect them; show
that the connections reproduce reality; make predictions; let reality
prove them wrong; improve.

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

## The build sequence

Months are targets from M0 = October 2026. Exit gates decide when a step
is done.

| # | Step | Target | Release |
| --- | --- | --- | --- |
| 1 | Epistemic constitution | M0-M1 | v0.3 |
| 2 | Statutory kernel | M0-M8, then yearly | v0.3-v0.6 |
| 3 | Evidence Intelligence | M1-M4 | v0.4 |
| 4 | Conformance suite | M1-M4 | v0.3-v0.4 |
| 5 | Household microsimulation | M1-M6; IDI when granted | v0.5 |
| 6 | Accounting and fiscal spine | M3-M6 | v0.5 |
| 7 | National baseline | M4-M8 | v0.6 |
| 8 | Causal evidence library | M5-M9 | v0.7 |
| 9 | Historical validation laboratory | M6-M9 | v0.7 |
| 10 | Forward prediction ledger | Live by M2 | v0.4 |
| 11 | Domain models | M8-M16 | v1.x |
| 12 | Federated model and state graph | M10-M14 | v2.0 |
| 13 | Continuous state estimation | M12-M15 | v2.0 |
| 14 | Uncertainty and sensitivity | M9-M13 | v2.0 |
| 15 | Cost of delay | M13-M14 | v2.0 |
| 16 | Policy-space optimisation | M14-M16 | v3.0 |
| 17 | Value of information | M15-M17 | v3.0 |
| 18 | Public Futures Laboratory | M16-M18 | v4.0 |
| 19 | AI reasoning and search interface | M17-M19 | v4.0 |
| 20 | Continuously improving national digital twin | M19 on | |

Some things can't be compressed: the 1 April rate year, forecast
resolution, microdata access, independent human scrutiny, Māori data
governance engagement and Pete's decisions.

## Releases

### Done: v0.1, v0.1.5 and v0.2

- **v0.1, deterministic foundation.** Working for Families and the
  Accommodation Supplement, specified from primary sources, implemented,
  benchmarked and independently reviewed.
- **v0.1.5, evidence and explainability.** Every result shows its
  calculation steps, rules, evidence, assumptions and missing facts.
- **v0.2, static population microsimulation.** The same engines across a
  synthetic development population. It is ready to tag, and every result
  is labelled as not an estimate for New Zealand.

### v0.1.6 - Keep v0.1 current (Step 2)

Source and implement 2027-28 by 1 April 2027, settle the 2026-27 in-work
tax credit, and keep source currency a scheduled check.

**Exit gate:** every golden household calculates for 2026-27 and 2027-28
from approved, sourced values, with 2026-27 unchanged.

### v0.3 - Constitution and the kernel's first tier (Steps 1, 2 Tier 1, 4 for Tier 1)

The epistemic constitution becomes doctrine and every output conforms to
it: eight evidence classes, eleven fields on every number, four
non-negotiables, the never-build list, and data governance as
architecture. Personal income tax, Jobseeker Support, Sole Parent Support
and Supported Living Payment join the kernel on a shared household model
and a source-derived dependency graph, producing disposable income and
effective marginal tax rates.

**Exit gate:** `BUILD_PLAN_v0_3.md`'s exit gate, plus every output number
classed, sourced and carrying its uncertainty, and the Tier 1 conformance
matrix complete.

### v0.4 - Mechanism, conformance and the ledger (Steps 3, 4, 10)

An evidence graph from law to result, queryable both ways: what a figure
rests on, and what an assumption contaminates. A published conformance
suite (specifications and fixtures, with a harness) that others can
certify against. The prediction ledger goes live with externally
timestamped forecasts. The next household domains join the kernel.

**Exit gate:** any figure traces to its law and evidence, any assumption
lists its dependents, the published fixtures certify Poltika through the
harness alone, and the ledger holds timestamped entries with named
resolution sources.

### v0.5 - To whom, and at what cost to the Crown (Steps 5, 6)

A graded public-data population (MODERATE) runs the kernel, with a secure
runner ready for IDI data. Stock-flow consistent sector accounts and
Crown accounts give multi-year static fiscal scoring: nothing
disappears between payer and payee.

**Exit gate:** a multi-year reform is scored statically with household,
distributional, Crown line and debt effects, every invariant holds, and
every population result carries its grade.

### v0.6 - Compared with doing nothing (Step 7)

Population, macro and Crown baselines to 2065. Macro values are sourced
assumptions with ranges, not Poltika forecasts. Firms and government
(GST, company tax, Crown classifications) join the kernel.

**Exit gate:** the baseline reproduces He Tirohanga Mokopuna 2025 within
a stated tolerance, or attributes every difference to named assumptions.

### v0.7 - Behaviour and the past (Steps 8, 9)

A library of graded causal evidence (NZ causal, NZ observational,
international transferred, assumed), with Discovery and Hypothesis as its
intake. Backtests using only what was known at each date, never tuned.

**Exit gate:** every behavioural relationship in use is graded and
reviewed, results show static and behavioural side by side, and
backtest errors are published with their failures.

### v1.0 - The whole question, inside the kernel

For a package of changes inside the supported kernel domains, Poltika
answers what happens, to whom, when, through what mechanism, with what
confidence and compared with what alternatives. An independent analyst
can reproduce and challenge it without the builders
(`BUILD_PLAN_PROGRAMME.md`, "Releases").

**Exit gate:** the gates of Steps 1-10, and the hardening an outside
analyst needs.

### v1.x - Structural problems, one at a time (Step 11)

Domain models chosen by national importance × tractability × available
evidence, starting with fiscal sustainability and ageing. Each uses the
method that fits it.

**Exit gate, per domain:** validated against history, forecasts
registered, relationships graded.

### v2.0 - The federated model (Steps 12-15)

Specialised engines reconciled through a shared state and the accounting
spine; continuous state estimation that never learns silently; full
uncertainty propagation and sensitivity; the cost of delay. Poltika may
be called a digital twin only when Step 12's gate is met.

**Exit gate:** two or more domain engines run coupled with invariants
holding, one observe-forecast-diagnose-update cycle is on record, and
every material result has a propagated interval.

### v3.0 - Options and what to learn (Steps 16, 17)

Behind a causal credibility gate: people state objectives and
constraints, and Poltika returns the Pareto-efficient feasible set with
trade-offs, never a recommendation. Value of information names the
unknowns that cost New Zealand the most.

**Exit gate:** every member of a returned set reproduces as an ordinary
scenario, and Poltika estimates the value of resolving its most
decision-relevant unknown.

### v4.0 - Anyone can ask (Steps 18, 19)

After a trust gate (hardening, independent scrutiny, a published
ledger record): a public Futures Laboratory where every chart answers
why, source, assumptions, uncertainty, who is affected and what would
change it. Then an AI interface that translates questions into
constraints and explains verified results, and never supplies a number.

**Exit gate:** a person who didn't build Poltika can answer all six
questions for any chart, and every figure the AI shows matches the
engine.

### Continuous (Step 20)

`OBSERVE → DISCOVER → HYPOTHESISE → TEST → SIMULATE → ASSURE → COMPARE → DECIDE → OBSERVE REAL OUTCOME → RECALIBRATE`

## Policy kernel coverage

The kernel covers New Zealand's household tax-and-transfer system, then
firms and government, one reviewed domain at a time
(`BUILD_PLAN_PROGRAMME.md` Step 2):

- **Tier 1, v0.3:** personal income tax, Jobseeker Support, Sole Parent
  Support, Supported Living Payment.
- **Next households (lane 2C):** student support, ACC levies, KiwiSaver
  interactions, NZ Superannuation, Childcare and OSCAR Subsidies, Paid
  Parental Leave.
- **Other major transfers (lane 2D):** Temporary Additional Support,
  Disability Allowance, other MSD assistance, Child Support, ACC
  earnings compensation.
- **Firms and government (lane 2E):** GST, company tax, selected
  regulatory costs, other tax regimes, Crown revenue and expenditure
  classifications.

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
- No policy optimisation before causal relationships are credible.
- No "digital twin" branding before the model deserves it.
- Never optimise the model instead of the country.

AI is used throughout development. It operates the instrument; it is
never the instrument.
