# Programme status

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

**As of:** 5 October 2026. **Repository baseline:** `origin/main` after #146
(`a782693`); reconciled against live GitHub state on this date. This migration
branch is documentation work, not evidence that any new economic model is built.
[BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md), under
[ADR-0021](adr/0021-economist-first-pilot-programme.md), is the single active
master build order. [ADR-0020](adr/0020-delegated-acceptance.md) remains the
acceptance authority; [PETE_QUEUE.md](PETE_QUEUE.md) tracks Tier C items and
[docs/decision_log.md](docs/decision_log.md) records delegated decisions.

Every PR changing a task's state updates its row in the same PR. **Done**
requires a merged PR and the task's done-when evidence; reusable merged code
alone does not complete a larger new capability. PRs labelled “reuse” prove
existing assets, not a new task's completion. No A–P capability gate is claimed
by this migration. Later owners are provisional until their bounded plan starts.

Pete appointed GPT/Codex as coordinating project manager on 3 October 2026 (the handoff text below is dated 3 October; live PR state is in the tables and `gh`).
[Execution practice](docs/programme/EXECUTION.md) records separate writing,
security, testing and simplification roles within the four concurrent slots.
The task tables remain the live backlog; ADR-0020 acceptance and Tier C
boundaries remain unchanged. The economist-first migration #144–#147 has since merged; new work follows the live task tables.

The second-cycle ownership inventory preserves unmerged drafts on
`build/p1-household`, `build/p1-income-tax`, `build/p1-benefits`,
`build/p1-reporting` and `build/p1-sim-analysis` in the corresponding
`/Users/peterhemmingsen/poltika-p1-*` worktrees. Older Not started rows do
not establish unowned implementation paths. Reporting is clean and committed
at `8a541368cc2dda4a0ef18df3288d28b1934bc701`; the other four listed worktrees
remain uncommitted at the coordinator's 02:14 UTC check on 3 October 2026.
Obtain pinned owner handoffs
before assigning overlapping writers. This is unaccepted ownership evidence,
not a code audit or test/approval result. #148/#151 remain separate source
drafts. The simulation-analysis owner also owns both existing snapshot tests;
later additive parity work needs an unoccupied path after the owner handoff.

Third-cycle note: the original reporting owner draft at `8a541368` remains
preserved. [Draft #154](https://github.com/hemmingsenpeter-byte/poltika/pull/154)
contains the isolated reporting review/fixes, code pin `3a10771`, docs head
`9b6413c`. The earlier `8235506` passed 1,380 default-suite tests with 22 skips
and two opt-in exclusions, but security found R12's Decimal expansion defect.
The corrected pin passed 136 focused tests/no skips, whole Ruff, strict mypy
(85 source files) and installed-library smoke; targeted same-model security
and contract rechecks have no remaining blocker. All four CI checks pass at
final documentation head `9b6413c`; its default suite passed 1,409 tests with
nine skips, and both installed-artifact and replay checks passed separately.
Required Claude review/acceptance remains pending.
Task 24 remains gated by 21–23;
prototype review changes no task state. The [execution handoff](docs/programme/EXECUTION.md)
and [dated evidence](reviews/2026-10-03-programme-verification.md) record the
reporting limits and the 3 October refresh order (#153 and #152, since merged, as are #144-#147); none of it displaces Pete's authorised working sequence.

| Status | Meaning |
| --- | --- |
| Done | Merged and the task's done-when is met. |
| In flight (other session) | Existing worktree/PR owned elsewhere; coordinate, do not duplicate. |
| In progress | Actual work underway; named incomplete parts remain. |
| Planned | Previously taken but not started; dependencies are explicit. |
| Blocked | Named dependency outside the session prevents progress. |
| Pete | Waiting on a retained Pete decision/action. |
| Not started | New scope has not begun; existing reusable assets are recorded separately. |

## Professional baseline and current PRs

These are engineering closeout, not economic-model progress. Open/draft PRs
are not Done merely because their checks pass. Inspect latest head checks
and review again before merge; this is the reconciliation snapshot.

| Item | Status / owner | PR / checked head | Blocker or evidence |
| --- | --- | --- | --- |
| Delegated acceptance | Done; Claude Code, Pete's recorded delegation | #139 merged, `dd2650b` | ADR-0020 accepted; #141 added live tracking. |
| Main ruleset / squash auto-merge | Done (applied 2026-10-05 by Claude Code under Pete's delegation); red-check blocking observed in #168 | Ruleset id 24478578 | Squash only, strict up-to-date, nine required checks, no bypass, delete_branch_on_merge. ADR-0007 recorded that the plan could not enforce required checks on a private repo; The #168 probe at fb92c17 observed required test FAILURE, eight other required checks SUCCESS and GitHub BLOCKED. |
| Evidence-classes skill | Done; Claude Code | #138 merged, `38a3f17` | Legacy 1.7. |
| Dev tooling | In flight (other session); Claude Code | No PR | Existing uncommitted worker includes tooling and calculation-adjacent `conditional.py`; preserve files and apply relevant independent review. |
| Security CI | Done; Claude Code, GPT/Codex review and fixes | #142 merged, `b292666` | Its checks are among the nine required by the applied Q1 ruleset. |
| Governance files | Done; Claude Code | #143 merged, `6a7da14` | |
| Hosting policy-path documentation | Done; Claude Code | #140 merged, `96900a4` | Documents `POLTIKA_POLICY_SPECS_DIR`. This is not the dev-tooling PR. |
| Independent review debt | Done; GPT/Codex, Claude Code coordinates | #128, #150, #152 merged (`fe67875`) | `review_packets/review_queue.md` is current: no open implementation assurance rows. |

## Release and maintenance state

| Lane / release | Status / owner | Evidence and outstanding gate |
| --- | --- | --- |
| v0.1.0 | Done; Pete tagged | Remote tag exists; v0.1 accepted and retained release/demo/review evidence. |
| v0.1.5 | Pete; Claude Code prepares | Code/reviews retained; external-user field remains blank in `docs/pilot/V0_1_5_PILOT_FINDINGS.md`; external-user gate skips; no remote tag. Historical plan is archived with compatibility pointer. |
| v0.2.0 | Done; Pete authorised tag correction | Annotated remote tag 63f5f0d points to adf4058 (v0.2 gate and GPT/Codex clearance recorded); approved and verified on 5 October 2026. D10 records the correction. Retain BUILD_PLAN_v0_2.md as release evidence pending deliberate archive cleanup. |
| Statutory maintenance / v0.1.6 | In progress; GPT/Codex sources, Claude Code implements | Source-currency task 2.1 done (#92); other sourced-year work not started. `BUILD_PLAN_v0_1_6.md` remains active; 2027-28 deadline 1 April 2027. |
| Household model / v0.3 | In progress, existing intake only; GPT/Codex and Claude Code | Phase 1b assets retained; tax, benefits, shared household graph/income work not built. D1–D3 wait for primary-source packs. `BUILD_PLAN_v0_3.md` supports B/C; secure population work maps to E. |
| Later version labels | Not started | Assigned to evidenced capability gates; old v0.4–v6 schedule is historical, not a second build order. |

## Completed reusable assets

These merged capabilities remain available. Their limits explain why the
new task tables do not mark whole phases complete. Review evidence remains
in the live queue and retained `reviews/`/`review_packets/`; older plans/audit
packets can still say “open” historically and do not override current records.

| Asset | Merged PR / evidence | Scope and limitation |
| --- | --- | --- |
| WFF and Accommodation Supplement | v0.1 task/review records; policy_specs; golden cases | Existing supported 2026-27 slices; in-work tax credit remains `needs_review`; no income-tax/main-benefit engine. |
| Calculation traces / provenance | #40, #45, #60 and combined report records | Parameter/source/rule/input/rounding traces and hash-bound artifacts; no general evidence graph needed to reuse. |
| Deterministic explanations / evidence coverage | #82–#84, #86, #88 | Verified templates and source coverage; not an AI explanation layer. |
| Scenario identity and replay | #60, #63, #64, #65, #68 | Household artifact identities, replay/code checks and append-only PostgreSQL store; population/workbench runs remain in memory. |
| Data manifests, registry and canonical variables | #93, #111, #114, #120 | Frozen source snapshots/transforms and lineage; no complete national ontology. |
| Canonical population schema / adapter | #93, #117 | Weighted household/person forms; synthetic mapping assumptions are explicit; shared household model still pending. |
| Validation, weighting, reform contract | #94, #108 | Existing checks, weighted summaries and parameter overrides; no robust representative-population calibration yet. |
| Batch runner / parse cache | #95, #108 | Same statutory runner, reproducible hashes and measured caching; scale/representative hardening remains. |
| Static distribution/fiscal/withdrawal tables | #96 | Coverage-aware, named component/unit sets; separate WFF-year/AS-week results; combined income path not approved. |
| Synthetic tooling / development calibration | #98, #100, #111, #113, #117, #118 | Seeded records and explicit assumptions/fit diagnostics; synthetic development population is not a national estimate. |
| External aggregate cross-validation | #114, #118, #120; V0_2_CROSS_VALIDATION | Existing untuned IRD/MSD comparisons and explained gaps; not new representative validation. |
| Population explanations / analyst population API and page | #97, #99 | Existing verified population explanations and `/analyst/microsim`; population operator-set, run store in memory. |
| Household analyst page / pilot scripts | #85, #87, #89 | Existing `/analyst`, case pack and findings template; external user/session not recorded. |
| Fact catalogues, conditional branches and intake | #109, #112, #121, #125–#128 | Reviewed questions, finite/ranged branches, intake API/page, population ranges; #128 independently reviewed, fixes merged (#150, #152); source-based monotone/candidate declarations pending. |
| Hosted pilot protection/hardening | #124, #132 | Password-required image, security headers, body/concurrency limits; deployment/resource actions not completed by this migration. |
| Workbench backend / export | #133; ADR-0018 proposed | Registry, checks, generic blocks, worked examples, CSV/Excel export reviewed; completed workbench UI and ADR acceptance not evidenced. |
| Epistemic constitution | #136, #137, Pete approval 2 October | Eight classes and seven decisions are approved; preserve them while re-scoping implementation. |
| Source currency | #92 | Existing report/workflow; statutory new-year parameters still require dated primary sources. |

## Phase A — Stabilise

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bounded governance/baseline closeout | In progress | Claude Code; GPT/Codex reviews | #138, #139, #140, #142, #143 merged | Dev tooling (no PR) remains; coordinate existing workers | Professional-baseline rows above; constitution already approved | Step 1; baseline B1–B5 |
| 2 | PR/review-debt reconciliation | Done | Claude Code coordinates; GPT/Codex reviews | #128 closed by #152 | Keep queue truthful; retain open/draft PR ownership | Live review_queue; most earlier rows cleared | W1; P17 |
| 3 | Release baseline | Pete | Pete; Claude Code prepares | No new release PR | v0.2 tag; v0.1.5 external pilot/tag; verify baseline/gates | v0.1.0 tagged; retained release evidence | 7.1; v0.1.5 8.2–8.6; v0.2 10.3 |
| 4 | End abstract Phase 0 expansion | In progress | Claude Code coordinates | #144, #145, #146 merged; #147 (household lane) completes the migration | Merge #147; agree scoped/parked worker dispositions | ADR-0021 direction; snapshots preserve old tasks | Steps 1–2 sequencing |

## Phase B — Household economic kernel

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | Minimum household semantics | In progress | Claude Code; GPT/Codex mapping review | #161 merged (units, old 2.2, `9e67009`); periods (2.3) and entities (2.4) not yet PRs | Commit 2.3, then 2.4 on main (shared `errors.py`, CHANGELOG, REPOSITORY_STRUCTURE); then reconcile with the registry (2.1). `units.convert` is a stub: no sourced deflator rule exists, so any conversion is refused | CanonicalVariable and population contracts; recovered worktree drafts committed with Pete's approval of 2026-10-05 | 2.1–2.6, 2.10 scoped |
| 6 | Shared household model | In flight (other session) | Existing `build/p1-household` writer; GPT/Codex mapping review | None yet; existing increment recorded at the 3 Oct handoff (verify before use) | Reconcile/review the existing writer's scope before assigning another household/model/mapping writer; 5 and independent source-derived mapping review | ADR-0017 accepted; existing household/mapping files, roundtrip/semantics tests and pass1/pass2 docs preserved; adapters/golden parity not yet accepted | 2.7; v0.3 Phase 1; W6 |
| 7 | Personal income tax | In progress (source scope only) | GPT/Codex source writer; separate evidence checker; Claude Code implementation; Pete D1 | #148 draft `0db2bfaf`, base `main` after #147 merged | Open: Codex-authored source scopes need full final-head independent Claude pr-review with primary-source re-derivation (ADR-0020 rule 4). Earlier passes do not cover a later head. Pete D1; Bill 344-1 enactment and 2026–27 annual rates unverified; 5–6 for integration | Source draft and separate same-model check retained; no approved specification, parameters, benchmarks or engine | 3A; v0.3 0.1 / Phase 2 |
| 8 | Three core main benefits | In progress (source scope only) | GPT/Codex source writer; separate evidence checker; Claude Code implementation; Pete D1 | #151 draft `50f13f44`, base `main` after #147 merged | Open: Codex-authored source scopes need full final-head independent Claude pr-review with primary-source re-derivation (ADR-0020 rule 4). Earlier passes do not cover a later head. Pete D1; payment/rounding and supported-slice gaps; 5–6 for integration | Three sources-only catalogues; JS category corrected at `b238820` and rechecked by separate same-model checker; no approved values/spec/engine | 3A; v0.3 0.2 / Phase 3 |
| 9 | Household dependency graph | Not started | Claude Code; GPT/Codex interaction review | None | Sourced interactions; 6–8 for integrated paths | Existing combined WFF/AS runner reused | 3A; v0.3 Phase 4; W7 |
| 10 | Disposable income | In progress (source scoping commissioned) | GPT/Codex sources; Claude review; Pete definition acceptance | None | Local 0.4a: dated official-definition source pack and independent review; connected 7–9 outputs; uncovered components stay explicit | Existing per-policy results remain separate | v0.3 0.4 / 5.1 |
| 11 | EMTR/withdrawal/participation measures | Blocked (EMTR first approved) | GPT/Codex definitions; Claude Code | None | Reviewed income/period paths and Q10; adequacy follows D2 source review; v0.2 D9 unresolved | #96 per-policy withdrawal profiles/sweeps reuse | v0.3 Phase 5; v0.2 8.6–8.7 |

## Phase C — Assurance and analyst product

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | Legislation conformance | Not started | Claude Code matrix; GPT/Codex independent cases | Existing tests reuse | Build per-rule matrix alongside B; P6 only for publication | Existing Spec/Benchmark/Regression, goldens, value guard | Step 5; v0.3 Tier 1 matrix |
| 13 | Model/benchmark validation | Not started | Claude Code; GPT/Codex independent checks | #117, #114 reuse | B models and bounded validation contract; P18 tolerances | Existing cases and cross-validation reused | 6.1–6.3; Step 5 |
| 14 | Counterfactual scenario contract | Not started | Claude Code; GPT/Codex reviews | #60, #63, #64, #65, #68, #94–#95 reuse | Complete retained baseline/reform/comparison contract with 15 | Household persistence/replay and population reform identities exist separately | 8.5; Step 15 core split |
| 15 | End-to-end Analyst Workbench | Not started | Claude Code; GPT/Codex review; Pete ADR-0018 | #133 backend reuse | Usable UI/workflow, 12–14; separate ADR-0018 acceptance | Backend/CSV/Excel reviewed; no completed workbench UI evidence | P8; ADR-0018; Steps 4/28/32 reuse |

## Phase D — Pilot 1

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | Real household analyst pilot | Pete | Pete user; Claude Code facilitates; GPT/Codex evidence | #85, #89, #124, #132 reuse | Name external user/question; B/C workflow; record session/feedback | Existing scripts/template/hardening; external-user field blank | v0.1.5 8.2–8.5; new pilot gate |

## Phase E — Representative population microsimulation

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Harden PopulationDataset | Not started | Claude Code; GPT/Codex review | #93, #117 reuse | D workflow evidence; representative contract/data requirements | Existing weighted household/person schema and adapter | 7.2, 7.5–7.6; v0.2 Phase 2 |
| 18 | Harden batch runner | Not started | Claude Code; GPT/Codex parity review | #95, #108 reuse | 17; profile actual requirements before P10 engine decision | Existing runner/cache/reproducibility/scaling report | 7; 8.6; W4 |
| 19 | Robust weighting/calibration | Not started | GPT/Codex methodology; Claude Code | #94, #111, #113 reuse | Reviewed representativeness/targets/fit; approved access if needed | Existing equal-weight synthetic development calibration only | 7.2–7.3; Step 19 seed |
| 20 | External aggregate validation | Not started | GPT/Codex comparators; Claude Code diagnostics | #114, #118, #120 reuse | 19; comparable periods/scope and P18 tolerances | Existing IRD/MSD untuned comparisons and explained gaps | 7.4; 6.3; v0.2 9.4 |
| 21 | National distributional outputs | Not started | Claude Code; GPT/Codex review | #96, #99 reuse | 17–20 validated representativeness; P5 output restrictions | Existing synthetic distribution/coverage tables | 7.8; v0.2 Phase 8 |

## Phase F — Fiscal and economist-grade output

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 22 | Direct fiscal accounting | Not started | GPT/Codex mappings; Claude Code | #96 reuse | Sourced classifications/period methods; D8 annualisation unresolved | Separate-unit/component static entitlement totals exist | Step 8 narrow; 8.1, 8.4, 8.7 |
| 23 | Fiscal/distributional reconciliation | Not started | Claude Code; GPT/Codex review | #96, #133 reuse | 21–22; same scenario/run and explicit coverage | Existing generic table blocks and component totals | Step 8; v0.2 8.1–8.5 |
| 24 | Economist-grade report package | Not started | Claude Code; GPT/Codex independent challenge | #97, #133 reuse | 21–23; verified minimum-content report and reproduction | Existing explanations/CSV/Excel blocks; no full national report | New gate; Steps 4/8 output reuse |

## Phase G — Pilot 2

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | External population-analysis pilot | Not started | Pete user; Claude Code facilitates; GPT/Codex evidence | None | E/F gates; real professional question/user; trust/limitations feedback | No recorded national-estimate pilot | New pilot gate |

## Phase H — Demand-driven statutory coverage

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | Add domains by real analytical demand | Not started | Pete priority; GPT/Codex sources; Claude Code | None | Pilot/use-case pull, supported-slice decisions and maintenance budget | Existing five-PR onboarding; old coverage candidate map retained | 3C–3E; P9 changed; W2/W10 |

## Phase I — Historical validation

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | Historical policy/data states | Not started | GPT/Codex sources; Claude Code; Pete P11 | Existing snapshots reuse | P11 historical horizon at start; sourced retained periods | DataContext/vintages and immutable datasets already exist | Step 9; maintenance historical years |
| 28 | As-of execution | Not started | Claude Code; GPT/Codex review | None | 27; distinct policy validity/data observation/information vintage | Existing DataContext vintage lookup | 9.3; Step 13 |
| 29 | Historical replay | Not started | Claude Code; GPT/Codex validation | #63, #64, #65, #68 code replay reuse | 27–28; historical comparator/diagnosis contract | Household stored-run/code replay exists | Step 13; Step 9 |
| 30 | Prediction/model-error ledger | Not started | Claude Code; Pete targets/timestamps; GPT/Codex review | None | P7 genuine predictions/timestamping; forecast-resolution calendar | No predictive ledger evidenced | 6.4–6.5; Step 13 |

## Phase J — Behaviour and causality

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | Causal Evidence Library | Not started | GPT/Codex evidence; Claude Code | None | Reviewed empirical relationships and bounded representation | Existing statutory provenance retained; no causal library | Step 12; Step 4 richer graph |
| 32 | One behavioural mechanism at a time | Not started | GPT/Codex specifies; Claude Code; Pete ambiguity | None | 31; historical/model validation and mechanism-specific evidence | No behavioural model evidenced | Steps 12/16 behavioural split |
| 33 | Mechanical/behavioural result separation | Not started | Claude Code; GPT/Codex checks | None | 32 and explicit comparison contract | Existing deterministic statutory results reused | New explicit contract |
| 34 | Formal uncertainty propagation | Not started | Claude Code; GPT/Codex validates | None | Reviewed empirical/model uncertainties; profile batch requirements | Conditional/population bounds and sweeps reused, not formal propagation | Step 11 |

## Phase K — Dynamic national model

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | NZState(t) when required | Not started | Claude Code P19; GPT/Codex mappings | None | Deferred until validated models require shared national state | Old planned scope retained in archive; no implemented national state schema | 2.8; Step 14 |
| 36 | State transitions | Not started | Claude Code; GPT/Codex review | None | 35 and historical/empirical validation | No national transition engine | Step 14 |
| 37 | National Baseline Engine | Not started | GPT/Codex assumptions; Claude Code | None | 35–36; accounting; Pete P20 for broad scenario set | No national baseline; static status quo already exists | Step 10; Step 15 broad library |
| 38 | Historical/official trajectory validation | Not started | Claude Code; GPT/Codex checks; Pete tolerances | None | 37; I evidence; comparable official trajectories | Existing one-period cross-validation is a different claim | Steps 10/13 |

## Phase L — Domain models

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | High-value domains vertically | Not started | Pete P13; GPT/Codex sources; Claude Code | None | Actual use-case priority and independently validated composition contract | Architecture's requires/provides/module contract retained | Step 16 |

## Phase M — Digital twin infrastructure

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | General model dependency graph | Not started | Claude Code; GPT/Codex review | None | Multiple real models prove need; reuse B graph first | No general graph | Step 17 |
| 41 | Justified federation | Not started | Claude Code architecture decision | None | Measured independent-execution requirement and validated parity | Existing modular architecture preserved | Step 17 |
| 42 | Continuous state estimation | Not started | GPT/Codex methods; Claude Code | None | Validated state, observations and diagnosed update contract | Source currency is not state estimation | Step 18 |
| 43 | Spatial state | Not started | GPT/Codex concordances; Claude Code | None | Real spatial model requirement; source/validate resolution | Existing AS area fact/geography only | Step 20 |
| 44 | Production synthetic populations | Not started | GPT/Codex methods; Claude Code; Pete data access | #98, #113 development reuse | Justified use, fit, privacy and P5/access constraints | Development generator is not production synthetic state | Step 19 |
| 45 | Agent-based models where justified | Not started | GPT/Codex specifies; Claude Code | None | Mechanism requires interactions; empirical validation | No ABM | Steps 16/19 domain-method scope |

## Phase N — Decision intelligence

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 46 | Cost-of-delay | Not started | Claude Code; GPT/Codex review | None | Validated trajectories; P16 start-date-only scenario families with uncertainty | No cost-of-delay engine | Step 21; P16 |
| 47 | Value-of-information | Not started | Claude Code; GPT/Codex review | None | Validated uncertainty and human-specified objectives | Existing missing-fact intake ranking is household-scale reuse | Step 22 |
| 48 | Policy-space search | Not started | Claude Code; Pete P14; GPT/Codex review | None | P14 credibility, validated models and explicit user constraints | Deterministic sweeps are not policy optimisation | Step 23 |
| 49 | Pareto-frontier analysis | Not started | Claude Code; GPT/Codex checks | None | 48; human-specified objectives | No frontier engine | Step 24 |

## Phase O — Public / research infrastructure

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | Research APIs | Not started | Claude Code; Pete public/access decisions | Existing FastAPI reuse | Trust/security/licensing/access gate; validated supported scope | Internal/password-protected routes exist | Step 28 public/institutional split |
| 51 | Policy-analysis interfaces | Not started | Claude Code; Pete publication | None | Validated models, trust/permission, no normative scoring | Existing analyst interfaces reused | Step 26 |
| 52 | Futures laboratory | Not started | Claude Code; Pete publication | None | Validated trajectories and trust/permission | No public futures laboratory | Step 25 |
| 53 | Scenario/negotiation tools | Not started | Claude Code; Pete constraints/publication | None | Validated scenarios and user objectives/access | Current reforms are not a negotiation sandbox | Step 27 |

## Phase P — AI layer

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 54 | Natural-language scenario interface | Not started | Claude Code; GPT/Codex review | None | Validated structured scenario/model contract; AI gate | No LLM layer; deterministic intake exists | Step 29 |
| 55 | AI explanation over verified results | Not started | Claude Code; GPT/Codex checks | None | Verified results/evidence; refuse unsupported claims | Deterministic explanation templates retained | Step 32 AI split |
| 56 | AI model orchestration | Not started | Claude Code; GPT/Codex review | None | Validated models and explicit execution/human controls | No AI orchestration | Step 31 |
| 57 | AI hypothesis generation | Not started | Claude Code; GPT/Codex evidence review | None | Approved promotion gate; never auto-promote hypotheses | Discovery/Hypothesis placeholders only | Step 30 |
| 58 | Human-gated research loop | Not started | Claude Code; Pete approvals; GPT/Codex review | None | Validated models, auditable experiments and human gates | No autonomous research capability | Step 33 |

## Existing workers, follow-ups and parked scope

Preserve existing work; this migration neither commits their uncommitted
files nor reopens parked designs. “In flight” below is inherited ownership,
not proof of a live PR or approval of broader scope.

| Legacy work | Disposition / current home |
| --- | --- |
| AI gate, `prog/ai-gate` | Old 1.2: parked draft [#163](https://github.com/hemmingsenpeter-byte/poltika/pull/163), recovered from the local worktree. It amends the approved constitution, so it awaits GPT/Codex review and Pete's acceptance. |
| Model governance, `prog/model-governance` | Old 1.5: parked draft [#164](https://github.com/hemmingsenpeter-byte/poltika/pull/164), recovered from the local worktree. New doctrine awaits Pete's approval; retain doctrine constraints. |
| Never-build checks, `prog/never-build-checks` | Merged in #162 at `5a8c17e` (old 1.6); the validation-grade row skips until grades exist (old 7.2). |
| Units/periods/entities, old 2.2–2.4 | Units merged in #161 at `9e67009` (its `convert` is a stub: no sourced deflator rule exists). Periods (old 2.3) and entities (old 2.4) remain uncommitted in `/private/tmp/poltika-periods` and `/private/tmp/poltika-entities` (modified 2026-10-02); Pete approved committing them on 2026-10-05, so they are next, on the merged #161. Reconcile with minimum B 5 requirements. |
| Quantity draft, `claude/step2-quantity` | Parked draft, not for review; no universal schema prerequisite. P3 display obligation remains. |
| State schema, old 2.8 | Not started; old planned scope retained in archive. K 35 deferred pending real model requirements. |
| Dataset evidence classes / existing DEC classes | Approved constitution follow-ups retained; immutable manifests and hash-bound DEC files are not silently rewritten. Pete confirms interpretations/classes where required. |
| Monotone declarations and candidates, v0.3 1b.2b/2c/3e | Source-derived declarations not started; structured candidate evidence still required. Do not substitute author test fixtures for reviewed policy content. |

Māori governance blocks affected claims/outputs and microdata work where
applicable, not unrelated deterministic household sourcing. IDI access
belongs to later E/M work. P11 historical horizon, P7 prediction targets,
P13 domain priority, P14 search credibility, P18 tolerances and P20 national
scenarios remain unresolved at their new phases; P8's strategic workbench
choice is resolved, while ADR-0018's acceptance remains open. D8/D9 remain
explicit unresolved period/income-method dependencies for B/F.

The [pre-migration status snapshot](docs/archive/status/2026-10-03-programme-status-adr0019.md)
retains every old row; the master's 33-row migration table links all
[old detailed programme steps](docs/archive/programmes/2026-09-29-adr0019-master-programme.md).
Choose next work from the current master/status, not from those historical rows.
Next coding handoff: reconcile and review the existing ADR-0017 writer's
increment in `/Users/peterhemmingsen/poltika-p1-household` on
`build/p1-household` before assigning another household/model/mapping writer.
Preserve its uncommitted household/mapping files, tests and pass1/pass2 docs;
source-derived WFF/AS mapping review and byte-identical golden results/IDs
(v0.3 1.1–1.3) remain acceptance requirements, coordinated with minimum
semantics owners. The next intake needs a pinned committed handoff; no unowned
household implementation is assigned while those files move. Branch-local
construction-mode claims remain unaccepted ownership evidence.
Primary-source tax/benefit scoping and D1–D3 proposals
are parallel research (#148/#151 drafts); existing A closeout continues with
its current owners. (3 October handoff; #150 and #152 have since merged and the #128 queue row is closed.)

## Open PRs outside the closeout (live state, 5 October 2026)

[#154](https://github.com/hemmingsenpeter-byte/poltika/pull/154) (draft, reporting evidence) and [#155](https://github.com/hemmingsenpeter-byte/poltika/pull/155) (draft, closeout plan) are open. Dependabot [#156](https://github.com/hemmingsenpeter-byte/poltika/pull/156)-[#160](https://github.com/hemmingsenpeter-byte/poltika/pull/160) are open. None is part of this closeout's merges.
