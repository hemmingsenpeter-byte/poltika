# Poltika Roadmap

This is the release-level direction, not an implementation backlog. The
22-step build plan, what already exists against each step, the tasks and
the decisions are in `BUILD_PLAN_PROGRAMME.md`. Detailed tasks for each
release are in its own plan:

- `BUILD_PLAN.md` remains the frozen authority for v0.1;
- `BUILD_PLAN_v0_1_5.md`, `BUILD_PLAN_v0_1_6.md` and `BUILD_PLAN_v0_2.md`
  hold theirs;
- `BUILD_PLAN_v0_3.md` holds v0.3's, which now also covers Steps 1 and 2;
- later releases get a detailed plan when they start.

## Planning status

Operative from 29 September 2026. ADR-0018 records Pete's direction: build
Poltika as a decision instrument in 22 steps, climbing a validity ladder,
with targets in months. It supersedes ADR-0015's sequence (and through it
ADR-0008's and ADR-0014's). Nothing here changes v0.1's scope, approvals
or acceptance criteria, or anything already built.

## The question

Poltika is built to answer increasingly difficult versions of one
question:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

Poltika starts small: represent one piece of New Zealand correctly, then
two, then ten; connect them; show that the connections reproduce reality;
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

## The validity ladder

`executable rules → observable state → explanatory model → predictive model → integrated model → decision instrument → digital twin`

Each transition has its own burden of proof. **Poltika doesn't graduate
to the next level because the code is finished. It graduates when the
current level has shown sufficient validity.**

| Level | Shown by |
| --- | --- |
| 1. Executable rules | Every rule's golden, boundary, contradiction and regression cases pass; independent review |
| 2. Observable state | Reproducing published aggregates, sources and Crown accounts within stated tolerances |
| 3. Explanatory model | Reproducing Treasury's baseline or explaining the difference; replaying history better than naive baselines |
| 4. Predictive model | Registered forecasts landing inside their intervals and beating baselines, over enough calendar time |
| 5. Integrated model | The coupled system keeping every invariant and replaying history at least as well as its parts |
| 6. Decision instrument | Decision outputs robust across uncertainty, reproducible, and independently scrutinised |
| 7. Digital twin | A continuously updated state estimate with a sustained, published forecast record |

A model can be demoted as well as promoted. Outputs carry the level of
the least mature model they rely on.

## Two directions of growth

The steps build a vertical stack:

`statutory kernel → microsimulation → fiscal and accounting spine → national state engine → domain models → decision intelligence → AI layer`

Horizontal capabilities run across all of it, from the start, and are
never finished: evidence and provenance, validation, uncertainty,
versioning, prediction scoring, security and privacy, Māori data
governance, model governance and reproducibility.

## The build sequence

Months are targets from M0 = October 2026. Gates and graduations decide
when something is done.

| # | Step | Target | Release |
| --- | --- | --- | --- |
| 1 | Epistemic constitution and model governance | M0-M1 | v0.3 |
| 2 | National Variable Registry and common schemas | M0-M2, then grows | v0.3 |
| 3 | Statutory kernel | M0-M9, then yearly | v0.3-v0.6 |
| 4 | Evidence Intelligence and the evidence graph | M1-M4, then grows | v0.4 |
| 5 | Conformance and regression suite | M1-M4 | v0.3-v0.4 |
| 6 | Validation framework and Prediction Ledger v0 | M2-M4 | v0.4 |
| 7 | Household microsimulation | M3-M7; IDI when granted | v0.5 |
| 8 | Fiscal and accounting spine | M4-M8 | v0.5 |
| 9 | Historical NZ State Store | M5-M8 | v0.6 |
| 10 | National Baseline Engine | M6-M10 | v0.6 |
| 11 | Uncertainty and sensitivity framework | M7-M10 | v0.7 |
| 12 | Causal Evidence Library | M8-M12 | v0.7 |
| 13 | Historical Validation Laboratory | M9-M13 | v0.7 |
| 14 | National State Transition Engine | M11-M14 | v1.x |
| 15 | Priority domain models | M13-M21 | v2.x |
| 16 | Federated Model Graph | M15-M21 | v2.0 |
| 17 | Continuous State Estimation | M17-M22 | v2.x |
| 18 | Cost of delay and scenario discovery | M19-M21 | v3.0 |
| 19 | Value of information | M20-M22 | v3.0 |
| 20 | Policy-space optimisation | M21-M24 | v3.x |
| 21 | Public Futures Laboratory | M23-M25 | v4.0 |
| 22 | AI reasoning and search layer | M24-M26 | v4.x |
| ∞ | Continuously improving national digital twin | Emerges | |

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

### v0.1.6 - Keep v0.1 current (Step 3)

Source and implement 2027-28 by 1 April 2027, settle the 2026-27 in-work
tax credit, and keep source currency a scheduled check.

**Exit gate:** every golden household calculates for 2026-27 and 2027-28
from approved, sourced values, with 2026-27 unchanged.

### v0.3 - Foundations and the kernel's first tier (Steps 1, 2, 3A, 5 for Tier 1)

The architecture the later steps need:

- the epistemic constitution, the never-build list and data governance;
- model governance: a model registry, change control and the ladder;
- the National Variable Registry, with the shared household model as its
  first instance and state schema v0;
- every quantity as X = (x̂, D_x, E_x): value, uncertainty and evidence.

Personal income tax, Jobseeker Support, Sole Parent Support and Supported
Living Payment join the kernel, producing disposable income and effective
marginal tax rates.

**Exit gate:** `BUILD_PLAN_v0_3.md`'s exit gate. Every engine is
registered with a level. Every number it reads or writes is a registered
variable. Every output is a quantity with D_x and E_x. The Tier 1
conformance matrix is complete.

### v0.4 - Mechanism, conformance and proof (Steps 4, 5, 6)

- An evidence graph, queryable both ways: what a figure rests on, and
  what an assumption contaminates.
- A published conformance suite that others can certify against.
- One validation framework for every validity claim.
- The prediction ledger, live, with its first genuinely predictive entry
  registered before its outcome.

**Exit gate:** kernel domains reach Level 1, any figure traces to its law,
and the ledger freezes, timestamps and scores entries.

### v0.5 - To whom, and at what cost to the Crown (Steps 7, 8)

A graded public-data population runs the kernel, with a secure runner
ready for IDI data. Stock-flow consistent accounts give multi-year static
fiscal scoring.

**Exit gate:** a multi-year reform is scored statically with every
invariant holding, and population and accounts reproduce published
figures within stated tolerances.

### v0.6 - What New Zealand looked like, and where it is heading (Steps 9, 10)

A versioned historical state store, queryable as known at any date, and a
national baseline to 2065. Firms and government join the kernel.

**Exit gate:** Level 2. The baseline reproduces He Tirohanga Mokopuna
2025 within a stated tolerance, or attributes every difference to named
assumptions.

### v0.7 - Uncertainty, behaviour and the past (Steps 11, 12, 13)

Uncertainty propagated and its drivers ranked. A graded library of causal
evidence. Backcasts, policy replays and shock replays against baselines,
never tuned.

**Exit gate:** Level 3 for the kernel, population, spine and baseline.

### v1.0 - The whole question, inside the kernel

For a package of changes inside the supported kernel domains, Poltika
answers what happens, to whom, when, through what mechanism, with what
confidence and compared with what alternatives, on models at Level 3. An
independent analyst can reproduce and challenge it without the builders.

### v1.x - An integrated national system (Step 14)

S_t → S_t+1: simple, explicit transition functions running New Zealand
forward year by year, each replaceable later by a domain engine.

**Exit gate:** an integrated trajectory with every invariant holding that
replays history at least as well as naive baselines. Level 4 follows
when the ledger's record supports it.

### v2 - Domain models, federation and continuous estimation (Steps 15-17)

Priority domains, one at a time, each beating the transition function it
replaces. They are federated through the common state and the spine, and
the state estimate updates as observations arrive, never silently.

**Exit gate:** Level 5.

### v3 - Decision intelligence (Steps 18-20)

Cost of delay and scenario discovery. Value of information, before
optimisation: sometimes the answer is "get better evidence first". Then a
search for the Pareto-efficient options that satisfy the constraints a
person states, never a recommendation.

**Exit gate:** Level 6.

### v4 - Anyone can ask (Steps 21, 22)

After a trust gate, a public Futures Laboratory where every chart answers
why, source, assumptions, uncertainty, who is affected and what would
change it. Then an AI layer that translates questions and explains
verified results, and never supplies a number.

### ∞ - The digital twin

`OBSERVE → DISCOVER → HYPOTHESISE → TEST → SIMULATE → ASSURE → COMPARE → DECIDE → OBSERVE REAL OUTCOME → RECALIBRATE`

Called a digital twin only at Level 7.

## Policy kernel coverage

The kernel covers New Zealand's household tax-and-transfer system, then
firms and government, one reviewed domain at a time
(`BUILD_PLAN_PROGRAMME.md` Step 3):

- **Tier 1, v0.3:** personal income tax, Jobseeker Support, Sole Parent
  Support, Supported Living Payment.
- **Next households (lane 3C):** student support, ACC levies, KiwiSaver
  interactions, NZ Superannuation, Childcare and OSCAR Subsidies, Paid
  Parental Leave.
- **Other major transfers (lane 3D):** Temporary Additional Support,
  Disability Allowance, other MSD assistance, Child Support, ACC
  earnings compensation.
- **Firms and government (lane 3E):** GST, company tax, selected
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
- No "digital twin" branding before Level 7.
- Never optimise the model instead of the country.

AI is used throughout development. It operates the instrument; it is
never the instrument.
