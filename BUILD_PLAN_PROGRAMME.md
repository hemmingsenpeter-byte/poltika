# Poltika master build programme

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

**Date:** 3 October 2026 (adoption date; live status is in `PROGRAMME_STATUS.md`). **Direction:** approved by Pete's repository
reconciliation and migration instruction; recorded in [ADR-0021](adr/0021-economist-first-pilot-programme.md).
**Authority:** this is the single active master build order. It supersedes
ADR-0019's execution sequence, while preserving its enduring architectural
principles, completed work and decision provenance.

Build complete analytical vertical slices, validate them, put them in front
of real users, and generalise infrastructure when multiple real models
require it. The objective is the shortest technically rigorous path from
the current repository to economist-grade output and credible external
pilots, with cumulative progress towards the national economic/policy
digital twin. This migration authorises documentation and governance
changes; model implementation follows in separately reviewed, bounded PRs.

## Authority and how to work

The governing hierarchy is:

1. `doctrine/` and accepted `adr/` decisions: permanent evidence,
   determinism, testing, review, IP, epistemic and decision constraints.
   [ADR-0020](adr/0020-delegated-acceptance.md) retains delegated acceptance
   and Tier C boundaries; superseded decisions remain permanent history.
2. [ARCHITECTURE.md](ARCHITECTURE.md) and
   [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md): design and placement.
3. This file: the single current implementation sequence/capability gates.
4. Active detailed lanes: [BUILD_PLAN_v0_3.md](BUILD_PLAN_v0_3.md) for B/C's
   household/tax-benefit graph/measures, with population work in E;
   [BUILD_PLAN_v0_1_6.md](BUILD_PLAN_v0_1_6.md) for parallel source currency,
   effective-dated years and enacted changes; [BUILD_PLAN_v0_2.md](BUILD_PLAN_v0_2.md)
   for release closeout until v0.2.0 is tagged; [BUILD_PLAN_B0_1_WEB.md](BUILD_PLAN_B0_1_WEB.md)
   for Task B0.1's web frontend.
5. [PROGRAMME_STATUS.md](PROGRAMME_STATUS.md): live owners, status, PRs,
   evidence and blockers; a merged asset is not a completed capability gate.
6. [PETE_QUEUE.md](PETE_QUEUE.md): retained Tier C decisions/actions.
7. `docs/archive/`: historical planning only, never current task selection.

[ROADMAP.md](ROADMAP.md) explains direction; it is not another backlog.
[docs/decision_log.md](docs/decision_log.md) permanently records delegated
A/B decisions. `BUILD_PLAN.md` remains the historical v0.1 record at its
existing path, including frozen doctrine anchors still referenced by
living/protected artifacts. Completed/superseded plans remain evidence,
not competing current build instructions.

Every policy rule, rate, threshold, eligibility condition, effective date
and interaction must come from cited primary NZ sources. Missing sources
or interpretation ambiguity stop the affected slice and go to Pete;
unrelated work continues. Maintain Spec, Benchmark and Regression tests,
protected statutory-value procedures, the discrepancy taxonomy and the
clean-room boundary. No model memory or external engine is policy authority.

Owners remain GPT/Codex for independent sourcing/specification and review,
Claude Code for implementation and its delegated project-management role,
and Pete for retained decisions. ADR-0020 delegates acceptance to Claude
Code; it does not assign that power to every agent. Its author preflight,
fresh-context reviewer, independent review requirements and merge rules
remain unchanged. Tagging, publication, access applications and external
resources stay with Pete unless explicitly authorised in the session.

Phases define capability dependencies, not a calendar promise. Source
research, approved access preparation and statutory maintenance may proceed
in parallel. Conformance and validation accompany B's slices and complete
in C. Deferred infrastructure must not become a prerequisite for an earlier
capability. A gate is claimed on recorded evidence with Pete's retained
milestone decision (P18), and can be lost if the evidence stops supporting it.

## Critical path: 34 capability milestones

| Order | Capability | Phase / programme tasks |
| --- | --- | --- |
| 1 | Repository stabilisation | A, 1–2 and 4 |
| 2 | Release baseline | A, 3 |
| 3 | Minimum household semantics | B, 5 |
| 4 | Shared household model | B, 6 |
| 5 | Income tax | B, 7 |
| 6 | Core benefits | B, 8 |
| 7 | Household dependency graph | B, 9 |
| 8 | Disposable income | B, 10 |
| 9 | EMTR / incentive measures | B, 11 |
| 10 | Conformance | C, 12, alongside B |
| 11 | Validation | C, 13, alongside B |
| 12 | Analyst Workbench | C, 15; surface from B, B0.1 |
| 13 | Scenario contract | C, 14; delivered with the workflow |
| 14 | Pilot 1 | D, 16 |
| 15 | PopulationDataset | E, 17 |
| 16 | Batch microsimulation | E, 18 |
| 17 | Population calibration | E, 19 |
| 18 | External aggregate validation | E, 20 |
| 19 | Distributional outputs | E, 21 |
| 20 | Direct fiscal accounting | F, 22–23 |
| 21 | Economist-grade report | F, 24 |
| 22 | Pilot 2 | G, 25 |
| 23 | Historical validation | I, 27–30 |
| 24 | Causal / behavioural models | J, 31–33 |
| 25 | Uncertainty propagation | J, 34 |
| 26 | Dynamic state | K, 35–36 |
| 27 | National baseline | K, 37–38 |
| 28 | Domain models | L, 39 |
| 29 | Federation | M, 40–41 |
| 30 | State estimation | M, 42 |
| 31 | Spatial / synthetic population | M, 43–45, where justified |
| 32 | Validated digital twin | M's gate |
| 33 | Decision intelligence | N, 46–49 |
| 34 | AI layer | P, 54–58, after validated models |

Statutory expansion H is driven by real analytical demand; public/research
infrastructure O depends on trust and permission. Both retain explicit
phases without making speculative coverage or public deployment a
prerequisite for the first useful analyst workflow.

### Recurring policy-analysis use cases (overlays, not new critical-path gates)

| Overlay | Earliest delivery | Dependence and truthful output |
| --- | --- | --- |
| C14a — Proposed-policy claim intake | C 14–15 | Source-preserved, manually verified proposal-to-scenario mapping for supported household instruments; not a full manifesto model |
| D16a — Campaign-policy pilot | D 16, optional | One or two sourced supported proposals tested on example households; no representative national costing or party ranking |
| F24a — New Zealand Budget analysis runner | After E 17–21 and F 22–24 | Repeatable Budget source register, measure coverage, supported fiscal/distributional analysis and reconciliation to *comparable* official figures; unmodelled initiatives explicit |
| I29a — Historical Budget as-of replay | I 27–29 (30 for predictive tracking) | Preserve announcement, policy, data and information vintages; compare modelled and subsequently observed outcomes without hindsight leakage |
| O 51 — Public policy/Budget explorer | O trust/publication gate | Public presentation of validated analyses only, not a requirement for analyst pilots |

These IDs are subordinate additions to the existing A–P tasks, not a 35th
critical-path milestone, release promise, parallel app or authorisation to
implement unsupported models. Limited provenance/source preparation may be
researched earlier; implementation follows normal bounded PRs and the active
B/C/D/E/F sequence. Detail and acceptance criteria: [docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).
A published party assertion is a *claim to be examined*, not statutory
authority or model input until its proposed parameters are independently
reviewed; a Budget announcement is not itself enacted law.

## What is retained and what is deferred

Reuse WFF and Accommodation Supplement calculations, sources, traces,
provenance, deterministic explanations, scenario identity/replay,
PostgreSQL persistence, data manifests/registry, canonical population
schemas, synthetic tooling, weighting, static microsimulation,
cross-validation, FastAPI routes, analyst pages, workbench backend and
CSV/Excel blocks, hosted-pilot hardening and assurance tests. Their
concrete evidence and incomplete gates are recorded in PROGRAMME_STATUS.

The workbench backend is implemented; a completed workbench UI and real
external pilot are not evidenced. Existing synthetic population results
are development results, not representative New Zealand estimates.
Preserve the synthetic label, unresolved coverage and per-component units.
Current WFF/AS fiscal figures cannot silently become combined annual totals.

Grow the National Variable Registry from actual model contracts: WFF
requires variables; AS reuses/adds; tax and benefits reuse/add; population,
fiscal and later domains extend it. Preserve built registries and approved
epistemic obligations. Implement only the contract and metadata needed by
the current slice; complete universal vocabulary and every-number schema
migration are not household-kernel prerequisites. Uncertainty, evidence
class and provenance must stay visible even before any universal type exists.

Use current `sources.yaml`, rule/source links, parameter IDs, traces,
evidence coverage and reports now. A richer evidence/causal graph belongs
in J when relationships need intervention, outcome, estimate, source,
population, jurisdiction, identification, uncertainty and external validity.
General graph infrastructure belongs later if multiple models require it.

This migration builds no Neo4j/general knowledge graph, universal ontology,
broad NZState schema, microservices, Kubernetes, Kafka, Spark, distributed
orchestration, agent framework, ABM, Monte Carlo infrastructure, policy
optimisation or natural-language model orchestration. Existing sound
architecture stays; adding a dependency or changing it needs a real slice
and its normal decision/review process.

## Phase A — Stabilise

This is bounded closeout, not a new foundations programme. Preserve other
sessions' worktrees, uncommitted files and parked drafts. Reconcile their
actual scope with their owners; resume only the small amount of baseline
or governance work already substantially underway. Do not duplicate it.

1. **Finish bounded governance/professional-baseline work in flight.**
   Claude Code owns implementation; GPT/Codex reviews.
   Done when required existing PRs are reviewed/CI-green and merged, with
   unfinished general infrastructure explicitly deferred rather than expanded.
2. **Reconcile open PRs and independent-review debt.** Claude Code coordinates;
   GPT/Codex independently reviews its assigned work.
   Done when current PRs/branches have dispositions and the live queue is
   accurate, including #128; affected gates remain blocked until review clears.
3. **Establish the release baseline.** Claude Code assembles evidence; Pete
   chooses and tags releases.
   Done when the current reproducible baseline, tags and outstanding release
   obligations agree. v0.1.5's external pilot is retained; no premature tag.
4. **Stop expanding abstract Phase 0 infrastructure.** Claude Code coordinates.
   Done when this migration is merged and all active instructions use one
   master, with existing workers re-scoped or parked by explicit disposition.

**Gate A:** the repository is safe enough to focus on economic models:
required checks/reviews are recorded, ownership is clear and releases are
truthfully described. v0.1.5's historical external-user obligation maps to
D where applicable; it must not block source scoping/minimum household work
or be waived by relabelling the baseline. Pending release tags do not block
B work once its own source/review gates are met. The Q1 ruleset is applied (5 October 2026) but its enforcement is not yet verified with a red check;
ADR-0020's merge rules apply regardless.

## Phase B — Household economic kernel

Use the detailed v0.3 lane and the five-PR policy onboarding process.
Sourcing and supported-slice decisions precede implementation. Complete
household semantics only to the extent required by these models.

**B0.1. Web frontend: the single product surface.** Claude Code implements;
GPT/Codex reviews which amounts are shown; Pete owns hosting, access and
ADR-0018 acceptance. Detailed lane: [BUILD_PLAN_B0_1_WEB.md](BUILD_PLAN_B0_1_WEB.md)
([ADR-0023](adr/0023-web-frontend-product-surface.md)).
Done when a password-protected user at `poltika.onrender.com` can start
or open a scenario and move from its headline result through fiscal,
distributional, evidence, assumption, technical and audit views, and
browse models and datasets, with every number traced to an API value and
no calculation in the frontend. It blocks none of Tasks 5–11.

5. **Minimum household semantic contracts.** Claude Code implements;
   GPT/Codex reviews source-derived mappings.
   Done when units, periods, people/families, income facts, identifiers and
   required geography support current policies without hidden conversions.
6. **Shared household model.** Claude Code implements ADR-0017;
   GPT/Codex reviews the mappings.
   Done when facts are held once, dated spells and policy-specific meanings
   remain explicit, adapters preserve callers and existing results/IDs match.
7. **Personal income tax.** GPT/Codex sources/specifies; Claude Code implements;
   Pete decides any interpretation and supported-slice ambiguity.
   Done when the sourced slice passes independent cases, benchmarks,
   regression/provenance checks and review, ready for graph integration.
8. **Jobseeker Support, Sole Parent Support and Supported Living Payment.**
   GPT/Codex sources/specifies; Claude Code implements; Pete decides ambiguity.
   Done when all three agreed slices meet the same source, test, trace,
   benchmark and independent-review standard as existing policies.
9. **Household computational dependency graph.** Claude Code implements;
   GPT/Codex reviews source-derived interaction edges.
   Done when real policy dependencies execute in their reviewed order,
   unresolved inputs remain gated and the chain is inspectable/reproducible.
10. **Canonical household disposable income.** Claude Code implements after
    GPT/Codex's source-linked definition and Pete's D2 decision.
    Done when the agreed component/period/income definitions reconcile,
    coverage is explicit and missing/unsupported amounts are never zero.
11. **EMTRs, withdrawal profiles and supported replacement/participation measures.**
    GPT/Codex sources definitions; Claude Code implements; Pete decides D3.
    Done when supported income paths, denominators, steps and periods are
    explicit, independently checked and shown with their coverage/limitations.

**Gate B:** Poltika calculates the connected supported household tax-transfer
position, with disposable income and incentive measures. WFF/AS results
remain protected, all three new benefits are covered within agreed slices,
and a reviewed household example demonstrates an output feeding another
input. D8 annualisation and D9 combined-income mappings remain unresolved
until explicitly sourced/reviewed and decided through the applicable tier.

## Phase C — Assurance and analyst product

Conformance and benchmark review run alongside B. The first analyst product
surface is the existing Analyst Workbench; complete its workflow over its
current contracts inside the B0.1 web app (ADR-0023) rather than creating a
parallel product stack.

12. **Legislation conformance.** Claude Code assembles the matrix/harness;
    GPT/Codex independently derives missing cases through the test doctrine.
    Done when supported rules have golden, boundary, contradiction and
    regression coverage, with source/rule links and visible exclusions.
13. **Model/benchmark validation.** Claude Code implements the bounded validation
    contract; GPT/Codex independently checks comparators and cases.
    Done when supported results can be challenged against independent
    expectations, coverage/mismatches are reported and review findings resolved.
14. **Counterfactual scenario contract.** Claude Code implements; GPT/Codex reviews.
    Done when baseline, reform, household/population, assumptions, dates,
    policy/data/code artifacts and comparisons are explicit, retained and replayable.
**C14a. Proposed-policy claim intake (bounded use-case overlay).**
GPT/Codex prepares independent source/parameter checks; Claude Code
implements only after C 14's scenario identity and B's supported policy
contracts are available. Preserve the exact primary announcement and
retrieval/version metadata; record speaker/publisher, dates, proposed-versus-
enacted status, effective period, extracted measure and manual review.
Map only verified and supported parameters into a proposed reform through
the existing scenario contract. Expose unsupported/ambiguous components,
the difference between quoted claims and calculated consequences, and the
review trail. No LLM or UI generates policy rates or numerical conclusions.
Done when a documented proposal can be traced from original evidence to
an independently checked, replayable supported household scenario (or a
refusal with reasons), with no party/plan ranking. [docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).

15. **Complete the Analyst Workbench workflow.** Claude Code implements;
    GPT/Codex reviews; Pete retains ADR-0018's design-acceptance question.
    Done when an analyst can define/check a reform, run supported cases,
    inspect comparisons/evidence/traces and export matching screen/CSV/Excel/report blocks.

**Gate C:** an external analyst can define a reform, run cases, inspect
evidence, understand calculations and export results through a usable
end-to-end workflow. Unknowns, assumptions and partial results remain
visible. P3 keeps household Rule outputs at legally required precision;
population, baseline and estimate-dependent figures display three significant
figures with their range, while stored values retain full precision. This
display obligation does not wait for a universal quantity type. Existing in-memory population/workbench runs are not described as
durably persisted merely because household scenarios already use PostgreSQL.

## Phase D — Pilot 1

16. **Run a real external analyst pilot.** Pete selects/engages the user;
    Claude Code prepares/facilitates; GPT/Codex checks evidence and limitations.
    Done when at least one external analyst completes a real supported
    household-reform question and the evidence below is recorded.

Record the user/background and consented identification, session date,
real analytical question, supported scope, baseline/reform/assumptions,
release/commit and run IDs, completed workflow/export/reproduction steps,
feedback, missing features and usefulness assessment. Test speed,
comprehension, reproducibility, auditability and workflow friction. Classify
findings under the review doctrine, with owners/dispositions and follow-up
PRs. Reuse `docs/pilot/` scripts/findings and retain their historical entries.

**D16a. Campaign-policy pilot extension (optional, non-blocking).**
Pete selects a public proposed household measure and consenting analyst;
Claude Code facilitates and GPT/Codex independently inspects the source
mapping. Reuse Task 16's workflow and evidence record to compare supported
household examples with the dated status quo. Record unsupported provisions,
uncertainty and mismatched assumptions. A separate campaign session may
serve as an additional product test but is not a condition of Gate D; it
cannot claim population costs before E/F or produce a party score.
Done when the proposal-to-result trail is reproducible and feedback and
limitations are recorded. [docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).

**Gate D:** an external user demonstrates that the workflow solves a real
analytical problem. Author smoke tests and populated templates do not meet
this gate. National estimates, IDI access and a completed universal registry
are not required. Resolve any misleading/wrong-result finding before
claiming readiness. A future session may also satisfy the retained v0.1.5
pilot obligation if it explicitly evidences that release's existing gates;
this migration does not declare either pilot complete.

## Phase E — Representative population microsimulation

Harden the substantial existing v0.2 capabilities after Pilot 1. Use the
canonical data boundary and acquire only datasets needed by this vertical.
Access preparation may start earlier without promising approval.

17. **Harden PopulationDataset.** Claude Code implements; GPT/Codex reviews.
    Done when population identity, provenance, representativeness, household
    facts, weights, missingness and policy coverage have validated contracts.
18. **Harden batch microsimulation.** Claude Code profiles/implements;
    GPT/Codex reviews parity.
    Done when household/batch results agree, failure/coverage is explicit,
    reproducibility holds and measured scale requirements are met.
19. **Robust weighting/calibration.** GPT/Codex sources targets/methodology;
    Claude Code implements and records diagnostics.
    Done when weights and relevant joint distributions have an independently
    reviewed method, fit/limitations and a justified population confidence grade.
20. **Validate against authoritative external aggregates.** GPT/Codex checks
    comparators/periods; Claude Code produces versioned diagnostics.
    Done when unmatched scope, dates, take-up and population assumptions are
    reconciled/explained, with agreed tolerances; no tuning merely to improve scores.
21. **National distributional outputs.** Claude Code implements;
    GPT/Codex checks interpretation and coverage.
    Done when winners/losers, income groups and household types are supported
    by representative data/validation and reproducible, coverage-aware tables.

**Gate E:** direct population-level effects can be estimated with transparent
representativeness and external validation. A synthetic label or confidence
name cannot establish national validity. Household surveys/IDI require
approved access and, where applicable, secure execution/output checks.
Ethnicity/iwi outputs remain prohibited under P5 pending agreed governance.
No microdata is committed or exported outside its approved constraints.

## Phase F — Fiscal and economist-grade output

22. **Direct fiscal accounting spine.** GPT/Codex sources definitions and
    mappings; Claude Code implements.
    Done when direct policy costs/revenue, periods, payer/payee and baseline
    versus reform reconcile under a reviewed method, without double counting.
23. **Combine distributional and fiscal analysis.** Claude Code implements;
    GPT/Codex reviews reconciliation.
    Done when the same scenario/population/run underlies both outputs,
    changes reconcile and incomplete coverage is reflected in all claims.
24. **Deterministic economist-style report package.** Claude Code implements;
    GPT/Codex checks the independent challenge/reproduction workflow.
    Done when every reported figure is verified against retained results,
    exports agree and an independent analyst can reproduce/challenge the package.

The report must contain policy specification; baseline; reform; fiscal
effect; affected population; winners/losers; income-group results;
household-type results; incentive effects; data; assumptions; validation;
provenance; and limitations. Keep assumptions and exclusions explicit, with
policy/data/code versions, run identities and reproducibility instructions.
Static mechanical entitlement effects are not automatically forecasts of
cash expenditure, take-up or behavioural effects. Resolve D8/D9 where needed;
otherwise preserve separate units and clearly restrict the claims.

**F24a. Recurring NZ Budget analysis runner (bounded overlay after F).**
Claude Code implements a reusable Budget-release workflow over C's scenario
contract and F's independently reviewed fiscal/report outputs; GPT/Codex
separately verifies official Budget source/measure mapping and comparators.
Ingest or register immutable official release documents and tables, identify
initiatives and classify each as supported, partially supported, unsupported
or not a microsimulation question; preserve announcement, financial year,
legislation/effective dates and data vintages. For supported slices produce
baseline/reform results, explicitly period-and-basis-aligned comparisons
against relevant published estimates, differences, uncertainty and a
coverage ledger; never sum appropriations, fiscal forecasts and modelled
entitlements as if interchangeable. The runner must work for later releases
without a new one-off engine. Early source-preservation/rehearsal work may
proceed without implying complete Budget costing.
Done when a selected published Budget is analysed and independently
reproduced for its declared coverage, with mismatches and exclusions visible.
This does not block G/Pilot 2 and does not promise whole-of-Budget modelling.
[docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).

**Gate F:** Poltika produces independently challengeable economist-grade
static policy analysis for its supported scope. It does not require full
national accounts, long-run debt trajectories or a universal state engine.

## Phase G — Pilot 2

25. **External population-level policy-analysis pilot.** Pete engages the user;
    Claude Code facilitates; GPT/Codex reviews evidence/limitations.
    Done when an external analyst completes a real national static analysis
    using the F package and the professional-use evidence is recorded.

Record D's workflow/reproduction evidence plus whether the user trusts the
estimates, understands representativeness/limitations, would use them
professionally, and finds the workflow faster/better than their existing
Excel/R/Python practice. Record issues, dispositions and the capabilities
they request. Do not equate favourable interface feedback with statistical
validation or professional trust.

**Gate G:** external validation justifies broader investment. Subsequent
expansion is increasingly earned by real analytical demand and validation.

## Phase H — Expand statutory coverage

26. **Add policy domains by demonstrated demand.** Pete sets priorities from
    pilot/use-case evidence; GPT/Codex sources; Claude Code implements.
    Done per slice when it passes source/specification, protected-value,
    implementation, interaction and release reviews under normal onboarding.

Possible domains include NZ Superannuation, childcare, KiwiSaver
interactions, Paid Parental Leave, student support, ACC, supplementary
assistance and Child Support. This is a candidate set, not a fixed backlog.
Each proposal states its consumer, supported slice, interaction needs,
maintenance cost and expected analytical value. A material pilot need may
justify a bounded coverage slice earlier; record its priority decision.
**Gate H per slice:** usable validated coverage answering the named question.

## Phase I — Historical validation

27. **Historical policy/data states.** GPT/Codex sources; Claude Code implements.
    Done when chosen historical periods have retained source/policy/data
    versions, explicit gaps and provenance within Pete's agreed horizon (P11).
28. **As-of execution.** Claude Code implements; GPT/Codex reviews mappings.
    Done when policy validity, observation period and information vintage are
    selected independently and unavailable information is not substituted.
29. **Historical replay.** Claude Code implements; GPT/Codex validates.
    Done when retained historical builds/artifacts replay and observed/modelled
    discrepancies are classified, reproducible and explained.
**I29a. Historical Budget as-of replay (use-case overlay).**
Reuse I 27–29 for a selected prior Budget, distinguishing what was known
when published from retrospectively observed information. Preserve
document/data/policy/code vintages and historical gaps, rerun supported
measures and attribute discrepancies where evidence allows. Only genuine
prospective forecasts registered before their resolution enter I 30's
prediction/model-error ledger; retrospective reproductions do not become
prediction-track-record evidence. Done when an analyst can independently
inspect and reproduce an as-of comparison. [docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md).

30. **Prediction/model-error ledger.** Claude Code implements; Pete chooses
    genuine predictive targets and timestamping/publication boundaries (P7).
    Done when predictions are registered before resolution, compared when
    outcomes arrive and error/diagnosis records remain inspectable.

**Gate I:** Poltika demonstrates where its models reproduce reality and
where they fail. Existing scenario/code replay is reused, while historical
policy validity and predictive track record remain separate claims.

## Phase J — Behaviour and causality

31. **Structured Causal Evidence Library.** GPT/Codex sources and independently
    assesses evidence; Claude Code implements its bounded representation.
    Done when relationships declare jurisdiction/population, identification,
    external validity, estimate/assumption class, uncertainty and source.
32. **Behavioural models, one mechanism at a time.** GPT/Codex specifies evidence;
    Claude Code implements; Pete decides unresolved assumptions/interpretations.
    Done per mechanism when its scope, empirical basis and validation are reviewable.
33. **Separate mechanical and behaviour-adjusted results.** Claude Code implements;
    GPT/Codex checks the comparison and claim labels.
    Done when both outputs are retained and the behavioural contribution is traceable.
34. **Formal uncertainty propagation.** Claude Code implements from reviewed
    empirical/model requirements; GPT/Codex validates treatment/interpretation.
    Done when parameter, data, transfer and model-form uncertainty and sensitivity
    are explicit, tested and propagated without hiding mechanical results.

**Gate J:** behavioural results are empirically sourced, separable from
statutory results and uncertainty-aware. Discovery/AI hypotheses still pass
`evidence → validation → human approval → specification → tests → Simulator`.

## Phase K — Dynamic national model

35. **NZState(t), when real requirements exist.** Claude Code proposes the
    contract under delegated P19; GPT/Codex reviews model/data mappings.
    Done when actual validated models require a shared state and its stocks,
    flows, periods and accounting identities have an explicit contract.
36. **State transitions.** Claude Code implements; GPT/Codex reviews.
    Done when validated transitions declare inputs/outputs/time step and preserve
    accounting, provenance, uncertainty and reproducibility.
37. **National Baseline Engine.** GPT/Codex sources exogenous assumptions;
    Claude Code implements a transparent conditional baseline.
    Done when policy/population/economy/fiscal assumptions and transitions reconcile.
38. **Validate historical/official trajectories.** Claude Code produces comparisons;
    GPT/Codex checks definitions/periods; Pete decides tolerances.
    Done when historical replay and official projections are reproduced or
    differences are diagnosed, without presenting conditional projections as predictions.

**Gate K:** defensible multi-year conditional trajectories, with model
error and growing uncertainty visible. Historical validation precedes claims
of sophisticated forecasting; direct static scoring does not wait for K.

## Phase L — Domain models

39. **High-value domain models, vertically.** Pete prioritises from demand;
    GPT/Codex sources/specifies; Claude Code implements.
    Done per model when requires, provides, parameters, time step, evidence,
    uncertainty and validation are declared and independently reviewed.

Potential domains: labour, housing, health, education, infrastructure,
firms/productivity, environment, transport and energy. Choose method from
actual mechanism/data requirements rather than a universal modelling style.
**Gate L per model:** a useful independently validated slice with tested
composition contracts; no speculative package/federation work.

## Phase M — Digital twin infrastructure

40. **Generalise the model dependency graph when necessary.** Claude Code implements;
    GPT/Codex reviews; done when multiple real models demonstrate reusable needs.
41. **Federate where independent execution is required.** Claude Code proposes the
    architecture decision; done when measured requirements justify it and parity holds.
42. **Continuous state estimation.** GPT/Codex sources observations/estimation methods;
    Claude Code implements; done when observed/modelled state reconciles with diagnosed updates.
43. **Spatial state.** GPT/Codex sources geography/concordances; Claude Code implements;
    done when required spatial resolution and aggregation have validated mappings.
44. **Production synthetic populations where justified.** GPT/Codex sources methods;
    Claude Code implements; done when a real use requires them and fit/privacy are validated.
45. **Agent-based models where interactions require them.** GPT/Codex specifies evidence;
    Claude Code implements; done when interactions justify the method and validation is credible.

**Gate M:** a validated, periodically reconciled computational
representation of New Zealand. Only then use “digital twin” operationally.
Federation, spatialisation and ABM are conditional tools, not branding goals.

## Phase N — Decision intelligence

46. **Cost-of-delay.** Claude Code implements P16: how delaying an intervention
    changes the size of the future adjustment needed, using scenario families
    varying only the start date, with uncertainty. Done when the curve, interval
    and evidence chain reproduce from ordinary scenarios.
47. **Value-of-information.** Claude Code implements from validated uncertainty;
    done when information value is conditional on named human objectives/decisions.
48. **Policy-space search.** Claude Code implements after Pete's P14 credibility
    gate; done when feasible constraints, assumptions and model limits remain inspectable.
49. **Pareto-frontier analysis.** Claude Code implements; GPT/Codex checks interpretation;
    done when trade-offs are reproducible for objectives people specify.

**Gate N:** people choose objectives/constraints; Poltika calculates
consequences and trade-offs. No secret objective, party score or claim that
a plan “wins”; validation scores are monitored, never optimisation targets.

## Phase O — Public / research infrastructure

50. **Research APIs.** Claude Code implements; done when authorised users can
    reproduce supported analyses with appropriate provenance and access boundaries.
51. **Policy-analysis interfaces.** Claude Code implements; done when validated
    policy proposals, campaign-claim provenance and supported Budget analyses
    can be explored with coverage, evidence, assumptions and comparisons,
    without normative scoring. This public/research surface builds on
    C14a/D16a/F24a/I29a and remains gated by O's trust/access decisions; it
    must not be mistaken for their first analyst implementation.
52. **Futures laboratory.** Claude Code implements; done when supported trajectories
    are exposed with assumptions, uncertainty and validation status.
53. **Scenario/negotiation tools.** Claude Code implements; done when user-stated
    constraints and trade-offs remain explicit and results are reproducible.

**Gate O:** validation/trust and Pete's publication, licensing/IP, security
and access decisions permit the intended audience. Existing internal APIs
and password-protected pilot capability do not establish public readiness.

## Phase P — AI layer

54. **Natural-language scenario interface.** Claude Code implements;
    done when verified structured requests, supported scope and human confirmation
    prevent an LLM from calculating or inventing policy/data values.
55. **AI explanation over verified results.** Claude Code implements;
    done when claims trace to recorded results/evidence and unsupported claims are refused.
56. **AI orchestration over validated models.** Claude Code implements;
    done when model selection/execution obeys contracts, scope and human controls.
57. **AI hypothesis generation.** Claude Code implements; GPT/Codex reviews evidence;
    done when hypotheses stay explicitly classed until the approved promotion gate passes.
58. **Human-gated autonomous research loop.** Claude Code implements under Pete's
    retained research approvals; done when proposals, evidence, experiments and
    model changes have explicit human gates and auditable outcomes.

**Gate P:** AI remains above the validated modelling system. It is never
the numerical source of truth or a substitute for primary statutory sources.

## Old-to-new migration and retained detail

The [exact ADR-0019 programme snapshot](docs/archive/programmes/2026-09-29-adr0019-master-programme.md)
retains every old task, done-when statement and rationale. The links below
are historical detail lookup, not an alternative execution order. Later
bounded plans recover relevant detail from this record and reconcile it
against current sources/code before implementation. The
[roadmap snapshot](docs/archive/roadmaps/2026-09-29-roadmap-adr0019.md),
[status snapshot](docs/archive/status/2026-10-03-programme-status-adr0019.md)
and [W1–W10 realignment record](docs/archive/programmes/2026-09-26-roadmap-realignment.md)
retain release mappings, ownership and earlier cross-release reasoning.

| Old ADR-0019 step / retained detailed scope | New phase/tasks | Treatment |
| --- | --- | --- |
| 1. [Epistemic Constitution and Model Governance](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-1-epistemic-constitution-and-model-governance-m0-m1) | A 1; permanent doctrine | Retained; bounded closeout, then permanent constraint. |
| 2. [National Variable Registry and Common Schemas](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-2-national-variable-registry-and-common-schemas-m0-m2-then-grows) | B 5–6; E 17; K 35; M 40–43 | Split; registry grows from real contracts; universal completion deferred. |
| 3. [Deterministic Statutory Kernel](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-3-deterministic-statutory-kernel-m0-m9-then-yearly) | B 7–11; H 26; maintenance | Moved to immediate critical path; existing WFF/AS retained. |
| 4. [Evidence Intelligence and Evidence Graph](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-4-evidence-intelligence-and-evidence-graph-m1-m4-then-grows) | C 15; J 31; M 40 | Current provenance retained; richer/general graph deferred. |
| 5. [Legislation Conformance Suite](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-5-legislation-conformance-suite-m1-m4) | B alongside slices; C 12 | Moved earlier; publication remains P6. |
| 6. [Validation Framework and Forward Prediction Ledger v0](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-6-validation-framework-and-forward-prediction-ledger-v0-m2-m4) | C 13; E 20; I 30 | Split; validation earlier, predictive ledger later. |
| 7. [Household Microsimulation Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-7-household-microsimulation-engine-m3-m7-idi-when-granted) | A 3; E 17–21 | Retained v0.2; release closeout and later hardening, not greenfield. |
| 8. [Fiscal and Shared Accounting Spine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-8-fiscal-and-shared-accounting-spine-m4-m8) | C 14; F 22–23; K 35–37 | Split; direct fiscal scoring first, shared national accounts later. |
| 9. [Historical NZ State Store](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-9-historical-nz-state-store-m5-m9) | I 27–29; K 35 | Moved later; retained snapshots/data contracts reused. |
| 10. [National Baseline Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-10-national-baseline-engine-m6-m10) | K 37–38 | Moved later; national baseline does not block static analysis. |
| 11. [Uncertainty and Sensitivity Framework](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-11-uncertainty-and-sensitivity-framework-m7-m10) | B/C metadata; E limits; J 34; K 38 | Split; visible uncertainty now, formal propagation later. |
| 12. [Causal Evidence Library](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-12-causal-evidence-library-m8-m12-then-continuous) | J 31 | Retained/deferred; empirical/causal evidence drives representation. |
| 13. [Historical Validation Laboratory](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-13-historical-validation-laboratory-m9-m13) | I 27–30 | Retained; precedes sophisticated forecasting claims. |
| 14. [National State Transition Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-14-national-state-transition-engine-m11-m14) | K 35–36 | Retained/deferred until validated models require shared state. |
| 15. [Canonical NZ Scenario Library](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-15-canonical-nz-scenario-library-m12-m14-then-grows) | C 14; K 37 | Split; counterfactual contract earlier, national scenario library later. |
| 16. [Priority Domain Models](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-16-priority-domain-models-m13-m22-sequentially) | H 26; L 39 | Split; statutory and other domains are demand-driven. |
| 17. [Federated Model Graph](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-17-federated-model-graph-m16-m24) | B 9 seed; M 40–41 | Retained/deferred generalisation and federation. |
| 18. [Continuous State Estimation](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-18-continuous-state-estimation-m18-m24) | M 42 | Retained/deferred; source currency continues in maintenance. |
| 19. [Synthetic Population Programme](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-19-synthetic-population-programme-m9-m28-paced-by-microdata-access) | E 17–19 reuse; M 44 | Split; development tooling now, production synthetic programme when justified. |
| 20. [Spatial and Physical Twin](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-20-spatial-and-physical-twin-m18-m28) | L 39 needs; M 43 | Retained/deferred; spatial resolution follows real use cases. |
| 21. [Cost-of-Delay Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-21-cost-of-delay-engine-m22-m24) | N 46 | Retained/deferred; P16 definition preserved. |
| 22. [Value-of-Information Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-22-value-of-information-engine-m23-m26) | N 47 | Retained/deferred; household intake ranking reused now. |
| 23. [Policy-Space Search and Inverse Solver](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-23-policy-space-search-and-inverse-solver-m25-m29) | N 48 | Retained/deferred; P14 credibility gate still required. |
| 24. [Pareto Frontier Engine](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-24-pareto-frontier-engine-m26-m30) | N 49 | Retained/deferred; user-specified objectives. |
| 25. [Public NZ Futures Laboratory](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-25-public-nz-futures-laboratory-m26-m30) | O 52 | Retained/deferred; pilots are separately bounded D/G. |
| 26. [Policy and Manifesto Analysis Interface](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-26-policy-and-manifesto-analysis-interface-m28-m31) | O 51 | Retained/deferred; no party/manifesto scoring. |
| 27. [Constraint-Based Negotiation Sandbox](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-27-constraint-based-negotiation-sandbox-m29-m32) | O 53 | Retained/deferred; human constraints and trade-offs. |
| 28. [Research and Institutional APIs](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-28-research-and-institutional-apis-m27-m34) | C 15 existing APIs; O 50 | Split; internal analyst integration now, research/public APIs later. |
| 29. [Natural-Language Policy Interface](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-29-natural-language-policy-interface-m30-m32) | P 54 | Retained/deferred; deterministic intake reused. |
| 30. [AI Hypothesis Discovery](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-30-ai-hypothesis-discovery-m31-m34) | P 57 | Retained/deferred; promotion gate retained. |
| 31. [AI Model Orchestration](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-31-ai-model-orchestration-m32-m35) | P 56 | Retained/deferred; validated models only. |
| 32. [AI Explanation and Research Agent](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-32-ai-explanation-and-research-agent-m32-m35) | C 15 deterministic explanation; P 55 | Split; verified templates now, AI explanation later. |
| 33. [Autonomous Research Loop, with Human Gates](docs/archive/programmes/2026-09-29-adr0019-master-programme.md#step-33-autonomous-research-loop-with-human-gates-m34-m38-then-continuous) | P 58 | Retained/deferred; human gates remain. |

W1 review debt remains in A; W2 onboarding/throughput in B/H; W3 access
preparation and secure data work in E; W4 profiling/batch choice in E;
W5 maintenance stays parallel; W6 household model and W7 real household
graph in B; W8 multi-year statutory parameters in maintenance; W9's old
sequence is historical; W10 is retained as demand-informed coverage history.

## Decision continuity and unresolved questions

The following are inherited decisions, not new approvals. Their detailed
original wording remains in the archived programme. Changed timing does
not silently resolve interpretation, access, publication or methodological
questions. ADR-0020's tiers continue to override general engineering delegation.

| Decision | Current treatment |
| --- | --- |
| P1 | New A–P sequencing replaces the old order; reconciliation, reuse, reviewable gates and tagged releases remain. |
| P2 | Caller-asserted household facts remain Scenario inputs under approved doctrine. |
| P3 | Household Rule outputs retain legal precision; population/baseline/estimate-dependent figures display three significant figures with their range; stored values retain full precision. Implementation follows actual outputs, independent of a universal quantity type. |
| P4 | Development, Public-data (MODERATE), IDI-calibrated (HIGHER) names retained; criteria and evidence belong to E, not labels alone. |
| P5 | Interim no ethnicity/iwi-disaggregated output remains; Pete agrees Māori data governance before affected claims/data use. |
| P6 | Publication of an independent conformance standard remains Pete's, C 12; does not block internal conformance. |
| P7 | Genuine predictive targets/timestamping remain Pete's, I 30; no longer block C's benchmark validation. |
| P8 | Strategic first-product choice resolved by this instruction: Analyst Workbench, C 15. ADR-0018 design acceptance remains separate. |
| P9 | Fixed future statutory order superseded by demonstrated analytical demand in H; original choice preserved historically. |
| P10 | Technical batch-engine decision remains delegated by ADR-0020; profile existing implementation in E 18 before choosing. |
| P11 | Historical horizon still unresolved, Pete's decision for I 27 and historical maintenance; old M1 urgency removed. |
| P12 | IDI application direction retained; source the route first, Pete lodges; E/M access-dependent work only. |
| P13 | Domain-model priorities remain Pete's; raise use-case-based options in H/L. |
| P14 | Causal credibility gate for policy-space search remains Pete's, N 48. |
| P16 | Delay changes the future adjustment needed; scenario families vary only start date, with uncertainty, N 46. |
| P17 | Review-debt cap remains suspended; queue and required independent review remain. |
| P18 | Pete sets gate tolerances/claims on evidence at each milestone; no implied gate approval from plan acceptance. |
| P19 | State-schema technical scope remains delegated; postponed to actual validated requirements in K 35. |
| P20 | First national scenario set remains Pete's; broad library deferred to K. |
| v0.3 D1–D3 | Supported tax/benefit slices, disposable-income definition and household measures remain source-dependent Pete decisions in B. |
| v0.2 D8 | AS annualisation/combined fiscal-period method remains unresolved; preserve separate units until an explicit reviewed decision. |
| v0.2 D9 | Combined withdrawal/income path mapping remains unresolved; source/review definitions before B 11/F claims. |

Keep ADR-0014's static microsimulation decision and its produced code;
ADR-0015 stays historical context; ADR-0017 remains operative. ADR-0018
is still proposed despite implemented/reviewed backend: PETE_QUEUE records
the minimum acceptance decision. ADR-0019's architectural principles remain
except where explicitly superseded; its historical body is not rewritten.

## Releases, maintenance and next work

Only v0.1.0 is evidenced as tagged at reconciliation. v0.1.5's code and
reviews do not prove its external pilot/tag; v0.2 is implementation/review
complete according to its retained evidence but still awaits Pete's tag.
Tags are verified against the remote and stay Pete's action. Later version
labels are assigned to completed capability gates, not used to resurrect
ADR-0019's old release schedule. The statutory-maintenance lane retains the
1 April 2027 deadline and sourced-year requirements independently of pilots.

The next bounded coding task is ADR-0017's shared household model and
named WFF/AS mappings (v0.3 1.1–1.3): hold underlying facts once, preserve
policy-specific definitions/periods and demonstrate byte-identical existing
results and IDs through the adapters. Coordinate minimum semantics with
current owners and obtain the required independent mapping review before
acceptance. Do not build a general registry/state/evidence graph to unblock it.

In parallel, GPT/Codex performs primary-source scoping for personal income
tax/core benefits and source-derived interaction/definition proposals for
Pete's v0.3 D1–D3 decisions. This is research/specification, not a second
coding task. Use the relevant source-check/spec-draft/clean-room skills and
normal independent review; introduce no policy values in this migration.
The A governance/CI PRs (#138-#143) and the #128 review closeout (#152) are merged; dev tooling (no PR) remains with its owner.
