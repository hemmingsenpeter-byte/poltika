# ADR-0019: The master build order: 33 steps with Phase 0 foundations and eight delivery phases, with validation gates

**Date:** 29 September 2026
**Status:** accepted as direction. Pete set it on 29 September 2026 in
three steps the same day:

1. A 20-step sequence, which Pete approved with its plan ("Approve and
   proceed all").
2. A revised 22-step sequence, after reviewing MIT's work in Andorra and
   the dependency order.
3. The master build order below, consolidating the whole thread ("Update
   roadmap again with this order and detail").

Drafted by Claude Code. The reconciliation, month targets, tasks and
release mapping are in `BUILD_PLAN_PROGRAMME.md`. It supersedes ADR-0015's
sequence and, through it, ADR-0008's and ADR-0014's.

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
epistemic constitution, a permanent layer of capabilities, and a list of
things Poltika never builds. People choose objectives and trade-offs;
Poltika measures consequences.

The motivating baseline is Treasury's [He Tirohanga Mokopuna 2025](https://www.treasury.govt.nz/publications/ltfp/he-tirohanga-mokopuna-2025).
Table 2 (p. 38) projects net core Crown debt, excluding NZSF and
advances, at 200.0% of GDP by 2065 in its unchanged-policy LTFM baseline.
The executive summary (p. 2) distinguishes the projection from a
prediction. Published 24 September 2025; retrieved 29 September 2026
and rechecked 2 October 2026.

Across the day's three versions, Pete's reasoning was:

- **Several things are architectural properties, not late features:**
  uncertainty, validation, the prediction ledger, the national variable
  registry and state schema, and model governance.
- **A common language first.** Pete's lesson from the Andorra work: define
  what population, income, Crown revenue, household and year mean before
  several models invent incompatible definitions (Step 2).
- **Proof before impressive models.** The validation framework and the
  forward prediction ledger come in Phase 1, so the external track record
  starts early (Step 6).
- **Uncertainty in the data model from the start.** Every quantity is
  X = (x̂, D_x, E_x), its value, uncertainty and evidence. The
  architecture accommodates distributions before anything propagates
  them (Steps 2 and 11).
- **An integrated system before sophisticated parts.** An explicit
  `NZState` and a state transition engine (S_t → S_t+1) with simple,
  explicit relationships come before domain models replace its parts
  (Step 14).
- **A digital twin is earned, then used.** Poltika is called an
  operational national digital twin only once the federated,
  continuously estimated, spatially grounded model has been validated
  (Phase 5). Decision intelligence follows it.
- **Value of information before search.** Poltika should be able to say
  that an answer hinges on a poorly evidenced parameter, and that the
  right next step is better evidence, before it searches large policy
  spaces (Steps 22-24).
- **AI last as a product layer, never as the epistemic foundation**
  (Phase 8).
- **Not a waterfall.** A permanent layer runs through every step and is
  never finished: evidence and provenance, validation and benchmarking,
  forward prediction scoring, uncertainty and model risk, versioning and
  reproducibility, Māori data governance, privacy and security, human
  oversight, and model governance.
- **Every stage has a validation gate.** Poltika doesn't move from
  "built" to "trusted" because the code works.

Pete was explicit that the current work doesn't change: WFF and the
Accommodation Supplement, then evidence and explainability, sit at the
start of Phase 1. What changes now is that the early architecture
anticipates the variable registry, evidence classes, uncertainty
metadata, data and model versioning, the dependency graph and the
validation framework.

Comparing this with what is built (`BUILD_PLAN_PROGRAMME.md`, "Where
Poltika stands") found most of Steps 1-7 partly built, and v0.2's
canonical variables as the registry's seed. There is not yet a model
registry, a validation framework, a ledger, a state store or a
transition engine.

## Decision

1. **The build order is Pete's master order: 33 steps with Phase 0 foundations and eight delivery phases.**
   - **Phase 0, foundations:**
     1. epistemic constitution and model governance;
     2. National Variable Registry and common schemas.
   - **Phase 1, executable New Zealand:**
     3. deterministic statutory kernel;
     4. Evidence Intelligence and evidence graph;
     5. legislation conformance suite;
     6. validation framework and forward prediction ledger v0.
   - **Phase 2, population and fiscal effects:**
     7. household microsimulation engine;
     8. fiscal and shared accounting spine;
     9. Historical NZ State Store.
   - **Phase 3, baseline New Zealand:**
     10. National Baseline Engine;
     11. uncertainty and sensitivity framework;
     12. Causal Evidence Library;
     13. Historical Validation Laboratory.
   - **Phase 4, first national system model:**
     14. National State Transition Engine;
     15. Canonical NZ Scenario Library;
     16. priority domain models.
   - **Phase 5, federated New Zealand:**
     17. Federated Model Graph;
     18. continuous state estimation;
     19. Synthetic Population Programme;
     20. spatial and physical twin.
   - **Phase 6, decision intelligence:**
     21. cost-of-delay engine;
     22. value-of-information engine;
     23. policy-space search and inverse solver;
     24. Pareto frontier engine.
   - **Phase 7, national decision infrastructure:**
     25. Public NZ Futures Laboratory;
     26. policy and manifesto analysis interface;
     27. constraint-based negotiation sandbox;
     28. research and institutional APIs.
   - **Phase 8, AI scientific layer:**
     29. natural-language policy interface;
     30. AI hypothesis discovery;
     31. AI model orchestration;
     32. AI explanation and research agent;
     33. autonomous research loop, with human gates.
2. **Each phase ends in a milestone question**, claimed only on validation
   evidence and recorded by Pete. Every step has a validation gate. A
   milestone can be lost when the evidence stops supporting it.
3. **The permanent layer starts in the step named and never finishes**
   (`BUILD_PLAN_PROGRAMME.md`, "The permanent layer").
4. **Months, not years.** Targets are months from M0 (October 2026).
   Gates and milestones decide when something is done. What can't be
   compressed is named: the 1 April rate year, forecast resolution,
   microdata access, human review and Pete's decisions.
5. **Releases are tags at gates.** v0.3 keeps its tasks and adds Phase 0.
   v1.0 is Phase 3's milestone: "What happens if policy X changes, and how
   confident should we be?", reproducible and challengeable without the
   builders.
6. **Kept unchanged:** everything built; every doctrine; the v0.3 tasks;
   the `new-policy` skill's five-PR onboarding; the promotion gate
   `Discovery → Hypothesis → evidence → validation → human approval →
   model specification → tests → Simulator`; `ROADMAP_REALIGNMENT.md`
   W2-W8 and W10, carried into the programme plan.
7. **The review-debt cap is suspended** (Pete: "Ignore PR cap"). The
   review queue is still kept.

## Consequences

- `ROADMAP.md` is rewritten on Phase 0 and the eight delivery phases. `BUILD_PLAN.md`'s Roadmap
  Doctrine, v1.0 definition and north star are updated. `BUILD_PLAN_v0_3.md`
  and `ROADMAP_REALIGNMENT.md` carry notes saying how they are re-homed.
- Nothing already built is discarded. v0.2's canonical variables become
  the registry's seed, `Bounds` becomes one kind of D_x, and existing
  tests and comparisons become validation cases.
- v0.3 grows: it now includes the constitution, model governance, the
  variable registry and the quantity type, alongside income tax and the
  core benefits.
- The 22-step version's seven-level ladder is replaced by phase
  milestones with validation gates. The difference that matters: an
  operational digital twin (Phase 5) now comes before decision
  intelligence (Phase 6).
- New scope arrives that no earlier plan had: a scenario library, a
  synthetic population programme, a spatial and physical twin, manifesto
  analysis without scoring, a negotiation sandbox, institutional APIs,
  and a human-gated autonomous research loop.
- Claims are bounded by validation status, so some outputs will be
  labelled more cautiously than they would otherwise be.
- This decision holds only while its reasoning does. A later reorder is
  a new ADR against this one.
