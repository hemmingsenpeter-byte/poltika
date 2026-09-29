# ADR-0018: Build Poltika as a decision instrument, climbing a validity ladder

**Date:** 29 September 2026
**Status:** accepted as direction. Pete set it on 29 September 2026 in two
steps the same day. First came a 20-step sequence, which Pete approved
with its plan ("Approve and proceed all"). Then, after reviewing MIT's
work in Andorra and the dependency order, Pete revised it to the 22 steps
below ("Modify the build plan again to this"). Drafted by Claude Code. The
reconciliation, month targets and release mapping are in
`BUILD_PLAN_PROGRAMME.md`. It supersedes ADR-0015's sequence and, through
it, ADR-0008's and ADR-0014's.

## Context

ADR-0015 ordered the work towards a production v1.0:

`v0.3 kernel → v0.4 scenario engine → v0.5 uncertainty, assurance and
historical baseline → v0.6 long-term fiscal model → v0.7 product (with
an LLM layer) → v1.0 hardening → Discovery and Hypothesis → v2-v5
capability tracks`

Pete's direction starts from a question Poltika should answer in
increasingly difficult versions:

> If New Zealand changes X, what happens, to whom, when, through what
> mechanism, with what confidence, and compared with what alternatives?

It sets a mandate ("help New Zealand maximise sustainable prosperity and
quality of life for current and future generations"), a north star, an
epistemic constitution, and a list of things Poltika never builds. People
choose objectives and trade-offs; Poltika measures consequences.

The motivating baseline is Treasury's. He Tirohanga Mokopuna 2025
projects net core Crown debt at 200.0% of GDP by 2065 if fiscal policy is
unchanged, and Treasury calls it a projection, not a prediction
(treasury.govt.nz, retrieved 29 September 2026).

The revision's reasoning, in Pete's words: the first sequence treated
several things as late features when they need to be architectural
properties from the beginning, namely uncertainty, validation, the
prediction ledger, the national variable registry and state schema, and
model governance. It made five changes:

1. **A National Variable Registry at Step 2.** Pete's lesson from the
   Andorra work: define what population, income, Crown revenue,
   household and year mean before several models invent incompatible
   definitions. The common schema exists early and grows with Poltika.
2. **The prediction ledger moves forward, to Step 6.** It holds small,
   testable predictions as soon as Poltika produces genuinely predictive
   outputs, which starts the clock on an external track record.
3. **Uncertainty moves forward, to Step 11, and into the data model from
   Step 2.** Every quantity is X = (x̂, D_x, E_x): its value, its
   uncertainty and its evidence. The architecture accommodates
   distributions before anything propagates them, so later models aren't
   built on an implicit assumption of point values.
4. **A National State Transition Engine (S_t → S_t+1) before
   federation.** Simple, explicit relationships give an integrated
   working system early. Individual transition functions are later
   replaced by domain engines.
5. **Value of information before optimisation.** Before searching large
   policy spaces, Poltika should be able to say that the answer hinges
   on a poorly evidenced parameter, and that the right next step is
   better evidence.

Two principles govern the whole sequence:

- **The steps are not a waterfall.** Evidence and provenance, validation,
  uncertainty, versioning, prediction scoring, security and privacy,
  Māori data governance, model governance and reproducibility run across
  every step, start early and never have a "finished" version.
- **Poltika graduates on validity, not on completion.** It climbs:

  `executable rules → observable state → explanatory model → predictive model → integrated model → decision instrument → digital twin`

  Each transition has its own burden of proof. Poltika moves up a level
  only when the current level has shown sufficient validity.

Pete was explicit that what is being done now doesn't materially change:
the statutory kernel and the evidence and explainability work remain
where Poltika starts. What changes now is that the early architecture
anticipates the variable registry, evidence classes, uncertainty
metadata, data and model versioning, the dependency graph and the
validation framework.

Comparing this with what is built (`BUILD_PLAN_PROGRAMME.md`, "Where
Poltika stands") found most of Steps 1-7 partly built, the canonical
variables of v0.2 as the seed of the registry, and nothing yet for a
model registry, a validation framework, a ledger, a state store or a
transition engine.

## Decision

1. **The build order is Pete's 22 steps:**
   1. epistemic constitution and model governance;
   2. National Variable Registry and common schemas;
   3. statutory kernel;
   4. Evidence Intelligence and the evidence graph;
   5. conformance and regression suite;
   6. validation framework and Prediction Ledger v0;
   7. household microsimulation;
   8. fiscal and accounting spine;
   9. Historical NZ State Store;
   10. National Baseline Engine;
   11. uncertainty and sensitivity framework;
   12. Causal Evidence Library;
   13. Historical Validation Laboratory;
   14. National State Transition Engine;
   15. priority domain models;
   16. Federated Model Graph;
   17. continuous state estimation;
   18. cost of delay and scenario discovery;
   19. value of information;
   20. policy-space optimisation;
   21. Public Futures Laboratory;
   22. AI reasoning and search layer.

   The continuously improving national digital twin is what they produce,
   not a release.
2. **The maturity ladder is doctrine** (Step 1.6). Every model has a
   level. Graduation and demotion are recorded decisions on validation
   evidence. Outputs carry the level of the least mature model they rely
   on, and language follows level.
3. **Horizontal capabilities start in the step named and keep growing**
   (`BUILD_PLAN_PROGRAMME.md`, "Two directions of growth").
4. **Months, not years.** Targets are months from M0 (October 2026).
   Gates and graduations decide when something is done. What can't be
   compressed is named: the 1 April rate year, forecast resolution,
   microdata access, human review and Pete's decisions.
5. **Releases become tags at step gates.** v0.3 keeps its tasks and adds
   Steps 1 and 2. v1.0 is the whole question answered inside the kernel
   by models at Level 3, reproducible and challengeable without the
   builders.
6. **Kept unchanged:** everything built; every doctrine; the v0.3 tasks;
   the `new-policy` skill's five-PR onboarding; the promotion gate
   `Discovery → Hypothesis → evidence → validation → human approval →
   model specification → tests → Simulator`; `ROADMAP_REALIGNMENT.md`
   W2-W8 and W10, carried into the programme plan.
7. **The review-debt cap is suspended** (Pete: "Ignore PR cap"). The
   review queue is still kept.

## Consequences

- `ROADMAP.md` is rewritten on the 22 steps and the ladder.
  `BUILD_PLAN.md`'s Roadmap Doctrine, v1.0 definition and north star are
  updated. `BUILD_PLAN_v0_3.md` and `ROADMAP_REALIGNMENT.md` carry notes
  saying how they are re-homed.
- Nothing already built is discarded. v0.2's canonical variables become
  the registry's seed, `Bounds` becomes one kind of D_x, and existing
  tests and comparisons become validation cases.
- v0.3 grows: it now includes the constitution, model governance, the
  variable registry and the quantity type, alongside income tax and the
  core benefits.
- Work arrives earlier than ADR-0015 planned: the registry, model
  governance, validation, the ledger, uncertainty and the causal library.
  The LLM layer and optimisation arrive later, and optimisation follows
  value of information.
- Claims are bounded by level, so some later outputs will be labelled
  more cautiously than they would otherwise be.
- This decision holds only while its reasoning does. A later reorder is
  a new ADR against this one.
