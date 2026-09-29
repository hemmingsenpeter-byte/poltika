# ADR-0018: Build Poltika as a decision instrument, in twenty steps

**Date:** 29 September 2026
**Status:** accepted as direction. Pete set it on 29 September 2026
("Redirect the build plan to accommodate this new order", then "reconcile
what we have in the build already, and rewrite build plan for this ...
assume it can be done in months"), then approved the programme plan
with its recommended decisions ("Approve and proceed all"). Drafted by
Claude Code. The reconciliation, month targets and release mapping are in
`BUILD_PLAN_PROGRAMME.md` (P1, decided).
It supersedes ADR-0015's sequence and, through it, ADR-0008's and
ADR-0014's.

## Context

ADR-0015 ordered the work towards a production v1.0:

`v0.3 kernel → v0.4 scenario engine → v0.5 uncertainty, assurance and
historical baseline → v0.6 long-term fiscal model → v0.7 product (with
an LLM layer) → v1.0 hardening → Discovery and Hypothesis → v2-v5
capability tracks`

Pete's direction starts from a different question. Poltika should
answer increasingly difficult versions of:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

The digital twin is what repeated answers add up to, not the starting
point. The direction sets a mandate ("help New Zealand maximise
sustainable prosperity and quality of life for current and future
generations"), a north star, an epistemic constitution, fourteen
phases, a twenty-step build sequence, and a list of things Poltika never
builds. People choose objectives and trade-offs; Poltika measures
consequences.

The motivating baseline is Treasury's. He Tirohanga Mokopuna 2025, the
Long-term Fiscal Statement, projects net core Crown debt at 200.0% of GDP
by 2065 if fiscal policy is unchanged, and Treasury calls it a
projection, not a prediction (treasury.govt.nz, "He Tirohanga Mokopuna
2025", retrieved 29 September 2026). Poltika's national baseline (Step 7)
must reproduce or explain it before relying on it.

Comparing the direction with ADR-0015's sequence and with what is built
(`BUILD_PLAN_PROGRAMME.md`, "Where Poltika stands") found eleven
differences:

1. **The epistemic rules exist in pieces, not as one system.** Outcome
   states, `review_status`, `scenario_assumption`, `Lineage`, source
   ranks, the synthetic label and `verify()` all exist. No output number
   carries an evidence class, uncertainty or its dependencies, and v0.2
   reports a synthetic population's cost to the cent. The direction puts
   the constitution before any further modelling.
2. **Evidence is per result, not a graph.** A result can be traced to
   its law. Nothing can answer the reverse: which results a changed
   assumption contaminates.
3. **Tests are not organised as a conformance suite.** Spec cases,
   benchmarks, golden households, guards and properties exist, but not
   per rule, not with boundary and contradiction classes, and not in a
   form another calculator could certify against.
4. **The accounting spine comes before the baseline.** ADR-0015 had
   scenarios, then uncertainty, then a long-term model. The direction
   builds sector accounts with stock-flow invariants and static fiscal
   scoring first, then the national baseline on them.
5. **There is no prediction ledger.** Its value accrues with calendar
   time and cannot be compressed, so it starts early.
6. **Causal knowledge was after v1.0.** Discovery, Hypothesis and
   behaviour sat after v1.0 or in v2. The direction puts a graded library
   of causal evidence before policy search and before v1.0. Discovery and
   Hypothesis become its intake.
7. **Optimisation was too early.** ADR-0015's v0.6 allowed constrained
   scenario search. The direction allows no policy optimisation before
   causal relationships are credible (Step 16, behind a gate).
8. **AI comes last in the product.** ADR-0015's v0.7 added an LLM layer.
   The direction uses AI throughout development, as now, but the AI
   reasoning interface is Step 19.
9. **Data governance was an adoption task.** Māori data governance,
   privacy, confidentiality and Te Tiriti considerations become
   architectural constraints from Step 1. The Algorithm Charter for
   Aotearoa New Zealand's Partnership commitment asks for a te ao Māori
   perspective, and the Charter says Māori data sovereignty needs
   separate consideration (data.govt.nz, retrieved 29 September 2026).
10. **The kernel reaches firms and government.** GST, company tax,
    selected regulatory costs and Crown revenue and expenditure
    classifications join the household domains.
11. **Uncertainty is represented from the start.** Every number carries
    its uncertainty from Step 1. The full propagation and sensitivity
    machinery is Step 14.

## Decision

1. **The build order is Pete's twenty steps:** epistemic constitution;
   statutory kernel; Evidence Intelligence; conformance suite; household
   microsimulation; accounting and fiscal spine; national baseline;
   causal evidence library; historical validation laboratory; forward
   prediction ledger; domain models; federated model and state graph;
   continuous state estimation; uncertainty and sensitivity; cost of
   delay; policy-space optimisation; value of information; public Futures
   Laboratory; AI reasoning and search interface; continuously improving
   national digital twin.
2. **Months, not years.** Targets are months from M0 (October 2026).
   Exit gates, not dates, decide when a step is done. Things that cannot
   be compressed are named: the 1 April rate year, forecast resolution,
   microdata access, human review and Pete's decisions.
3. **Releases become tags at step gates** (`BUILD_PLAN_PROGRAMME.md`,
   "Releases"). v0.3 keeps its tasks and adds Step 1. v1.0 is redefined
   around the question: the whole question answered for a package of
   changes inside the kernel, reproducible and challengeable without the
   builders.
4. **The constitution and the never-build list become doctrine** (Step
   1.1), binding every later step.
5. **Kept unchanged:** everything built; every doctrine; the v0.3 tasks;
   the `new-policy` skill's five-PR onboarding; the promotion gate
   `Discovery → Hypothesis → evidence → validation → human approval →
   model specification → tests → Simulator`; `ROADMAP_REALIGNMENT.md`
   W2-W8 and W10, carried into the programme plan.
6. **The review-debt cap is suspended** (P17). Pete said to ignore it on
   29 September 2026. The review queue is still kept.

## Consequences

- `ROADMAP.md` is rewritten on the twenty steps. `BUILD_PLAN.md`'s
  Roadmap Doctrine, its v1.0 definition and its north star are updated.
  `BUILD_PLAN_v0_3.md` and `ROADMAP_REALIGNMENT.md` carry notes saying
  how the redirect re-homes them.
- Nothing already built is discarded. Most of it is part of Steps 1-5,
  and the reconciliation table says what remains for each step.
- Work arrives earlier than ADR-0015 planned: the constitution, the
  evidence graph, the conformance suite, the ledger and the causal
  library. The LLM layer and optimisation arrive later.
- The kernel's scope grows by the firm and government domains, and each
  domain adds a yearly update (W5). The maintenance cost grows with it.
- Several decisions are needed early: evidence classes for asserted
  facts, the precision rule, population confidence grades, governance,
  ledger timestamping, conformance publication and the backtest horizon
  (`BUILD_PLAN_PROGRAMME.md`, "Open decisions").
- This decision holds only while its reasoning does. A later reorder is
  a new ADR against this one.
