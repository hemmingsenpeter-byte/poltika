# Repository reconciliation: economist-first programme

**Date:** 3 October 2026. **Author:** GPT/Codex. **Purpose:** the pre-migration reconciliation required by Pete's supplied programme-migration instruction. This is governance evidence, not a second build order or an implementation review.

**Evidence baseline:** live GitHub `main` was `e52f5d35913fbb4b81c7b64c6caf6d446c158759` ([commit](https://github.com/hemmingsenpeter-byte/poltika/commit/e52f5d35913fbb4b81c7b64c6caf6d446c158759)), committed 2 October 2026 at 16:23:26 NZDT through [#141](https://github.com/hemmingsenpeter-byte/poltika/pull/141). GitHub checks, branches, PRs and release refs were read on 3 October at approximately 12:44 NZDT. The original shared checkout was `342909b5a2183656f164bfbedef7db35005efb4b`, eight commits behind; its `origin/main` matched live GitHub. Reconciliation used the authoritative main tree rather than that older working tree.

The reconnaissance changed no files, branches, PRs, settings, deployments or releases. It did not inspect external policy-engine implementations. The migration worktree is `/private/tmp/poltika-programme-migration`, branch `docs/economist-programme`, based on the verified main SHA above. In-flight worktrees remain untouched. This report records pre-migration state; later migration edits do not retroactively change these findings.

## 1. Planning map and final authority

Classes: **A** active authority; **B** active supporting plan; **C** historical planning/archive; **D** decision record; **E** permanent release/review evidence. Classification distinguishes a file's historical content from its proposed live role.

| Artifact | Current role and authority | Class and final location | Supersession and reference action |
| --- | --- | --- | --- |
| `BUILD_PLAN_PROGRAMME.md` | Accepted ADR-0019 master sequence, 33 steps | A, root live file | Archive exact old text; replace sequence under ADR-0021. Update every operational old-step reference. |
| `ROADMAP.md` | High-level destination but also repeats the old master sequence | B, root live file | Preserve snapshot; rewrite concise direction under the new master, without a second backlog. |
| `PROGRAMME_STATUS.md` | Live execution tracker with a 2 October snapshot | A, root live file | Preserve snapshot; rebuild against merged evidence and new capability gates. It records state, not sequence. |
| `BUILD_PLAN_v0_3.md` | Accepted detailed household lane; currently also gates on universal Phase 0 | B, root live file | Re-home under Phases B-C; retain source scoping, policy tasks and mappings; move population work to E and remove obsolete universal blockers. |
| `BUILD_PLAN_v0_1_6.md` | Accepted source-currency and effective-dated maintenance lane | B, root live file | Retain maintenance responsibilities and calendar dates; remove competing roadmap/old-lane mappings. |
| `BUILD_PLAN_v0_2.md` | Implemented static microsimulation and release closeout | B, root until tag | `v0.2.0` is absent. Keep closeout live; archive only after the release action and evidence are recorded. New E-F work hardens existing assets. |
| `BUILD_PLAN_v0_1_5.md` | Historical explainability/pilot plan, substantial implementation, unfinished external pilot gate | C, `docs/archive/build-plans/2026-09-25-v0-1-5-build-plan.md` | Move exact text; retain root historical redirect. Carry unresolved pilot/release facts into live status, never declare it tagged. |
| `BUILD_PLAN.md` | Frozen v0.1 tasks and embedded doctrine/role anchors | C, root preserved | Header identifies historical scope; new master governs work. Do not move while doctrine/protected artifacts depend on its anchors. |
| `ROADMAP_REALIGNMENT.md` | Historical W1-W10 rationale; sequence already superseded by ADR-0019 | C, `docs/archive/programmes/2026-09-26-roadmap-realignment.md` | Move exact text; retain root historical compatibility redirect. Preserve workstream decisions; route current work to master/detailed lanes. |
| `ARCHITECTURE.md` | Architecture authority, mixed release/current/future prose | A, root | Preserve valid layers and target; correct current-state claims and sequence references. New programme changes execution, not production layout. |
| `REPOSITORY_STRUCTURE.md` | Canonical locations and dependency boundaries | A, root | Add archive/programme-evidence locations and replace old planning hierarchy; preserve production package boundaries. |
| `CLAUDE.md`, `AGENTS.md` | Operational agent instructions | A, root | Both start planning with the new master, then active lane/status. Retain source, test, review and ADR-0020 constraints. |
| `README.md`, `docs/ORIENTATION.md` | Contributor/analyst orientation | B, existing paths | Identify current master and status; distinguish release history, current capability and next work. |
| `PETE_QUEUE.md` | Open Tier C decisions/actions | A, root | Reconcile release/ruleset state and remap surviving decisions by capability. Do not erase retained authority boundaries. |
| `doctrine/*` | Governing constraints, including approved epistemic constitution | A, existing paths | Preserve substance. Update operational sequencing references only; remap the constitution's validation exception to Phase C. |
| `adr/0014-v0-2-static-microsimulation.md` | Accepted static microsimulation decision | D, unchanged path | Retain decision and historical release rationale; implemented capability supports E-F. |
| `adr/0015-roadmap-realignment.md` | Accepted historical roadmap decision, already redirected by ADR-0019 | D, unchanged path | Preserve history; new ADR identifies later sequencing supersession. |
| `adr/0017-shared-household-model.md` | Accepted shared household contract | D, operative at existing path | Retain period, mapping, compatibility and proof requirements; immediate Phase B work. |
| `adr/0018-analyst-workbench-registry.md` | Proposed design; backend implemented and reviewed | D, unchanged path | Implementation does not itself prove acceptance. Keep proposed; record minimum acceptance question in Pete's queue. |
| `adr/0019-decision-instrument-programme.md` | Accepted old execution sequence and enduring principles | D, unchanged path | Add only sequencing-supersession status referencing ADR-0021; preserve historical body and surviving principles. |
| `adr/0020-delegated-acceptance.md` | Accepted delegated engineering acceptance, Tier A/B/C and review rules | D, operative at existing path | Remains in force. Old P-decision labels keep their history while current queue entries explain the new capability location. |
| Other `adr/*`, `docs/decision_log.md` | Permanent decision provenance | D, unchanged paths | Preserve; retain delegated entries unchanged; ADR-0021 records the Pete-authorised migration and reversal rule. |
| `CHANGELOG.md`, `docs/releases/*`, `reviews/*`, `review_packets/*` | Historical results, releases and reviews | E, unchanged paths | Preserve accessible evidence and historical references. Current `review_packets/review_queue.md` is additionally B as the active audit tracker. |

Final reading hierarchy: doctrine/accepted ADRs; architecture/repository map; **one** root master programme; active detailed lanes; live status; Pete-only queue; historical archive. Archive documents never select the next implementation task. `ROADMAP.md` expresses direction, and `PROGRAMME_STATUS.md` records execution state.

## 2. Exact archival actions

All snapshots capture the exact files at the evidence baseline, including updates made after their title dates. The archive README carries historical/non-authoritative metadata; snapshot bodies are not rewritten.

| Action | Existing path | Archive destination | Root handling |
| --- | --- | --- | --- |
| Copy before replacement | `BUILD_PLAN_PROGRAMME.md` | `docs/archive/programmes/2026-09-29-adr0019-master-programme.md` | Root becomes current master. |
| Copy before replacement | `ROADMAP.md` | `docs/archive/roadmaps/2026-09-29-roadmap-adr0019.md` | Root becomes concise current direction. |
| Copy before replacement | `PROGRAMME_STATUS.md` | `docs/archive/status/2026-10-03-programme-status-adr0019.md` | Root becomes reconciled live status. |
| Move with Git provenance | `ROADMAP_REALIGNMENT.md` | `docs/archive/programmes/2026-09-26-roadmap-realignment.md` | Keep root historical redirect; original headings remain in the exact archive. |
| Move with Git provenance | `BUILD_PLAN_v0_1_5.md` | `docs/archive/build-plans/2026-09-25-v0-1-5-build-plan.md` | Keep root historical redirect; original headings remain in the exact archive. |

Create `docs/archive/README.md` stating that these are historical planning records and that the root `BUILD_PLAN_PROGRAMME.md` is current authority. Leave ADRs, protected policy/source artifacts, reviews, packets, releases and `BUILD_PLAN.md` where they are. Preserve root redirects for old paths. No tracked local links to anchors in the moved plans were found; their historical headings remain in the archive and original commit. Repair relative links operationally without changing the byte-identical archive snapshots.

## 3. ADR and decision changes

- Create `adr/0021-economist-first-pilot-programme.md`: Pete's supplied instruction approves the new strategy. Record what supersedes ADR-0019's execution order, the critical path, pilots and the smallest-real-model decision rule. Preserve long-run national-system goals and doctrine.
- ADR-0019: status becomes **superseded for programme sequencing by ADR-0021; architectural principles remain unless explicitly superseded**. Preserve its historical content.
- ADR-0014 stays accepted; ADR-0015 stays historical decision context; ADR-0017 stays accepted and operative; ADR-0020 stays accepted and operative.
- ADR-0018 stays **proposed** pending its stated Pete acceptance. Add a queue item explaining that #133 implemented/reviewed the backend and asking only for the outstanding design acceptance. Promoting Workbench as the first product surface follows the new directive; it does not silently amend that ADR's status.
- The new directive selects the first product surface previously left open as P8. Record that strategic choice while preserving ADR-0020's Tier C boundaries for other retained decisions, public exposure and resources.
- Record the migration in ADR-0021; retain `docs/decision_log.md` entries without implying a new delegated acceptance by Claude Code. Remap P6/P7/P13/P14/P18/P20 to their actual capability, retain P11 for later historical scope, and retain P12 for IDI access. No new policy interpretation is decided here.

## 4. All 33 old steps mapped to the new programme

Phase keys: A stabilise; B household economic kernel; C assurance/analyst product; D Pilot 1; E representative population microsimulation; F fiscal/report outputs; G Pilot 2; H statutory expansion; I historical validation; J behaviour/causality/uncertainty; K dynamic national model; L domain models; M digital twin infrastructure; N decision intelligence; O public/research infrastructure; P AI.

| Old step and exact title | New phase(s) | Treatment and retained scope |
| --- | --- | --- |
| 1 Epistemic Constitution and Model Governance | A, permanent constraints | Retain approved constitution; finish bounded in-flight governance. No universal foundation phase blocks household work. |
| 2 National Variable Registry and Common Schemas | B, E, K, M | Split; grow units, periods, entities and variables from real household/population/state contracts. Retain existing schemas; defer universal completion. |
| 3 Deterministic Statutory Kernel | B, H, maintenance | Move to immediate critical path; current tax/benefits first, later domains by demand, effective-dated maintenance throughout. |
| 4 Evidence Intelligence and Evidence Graph | C, J, M | Absorb existing statutory provenance in C; richer empirical/causal evidence graph later, general infrastructure only when useful. |
| 5 Legislation Conformance Suite | B-C | Move earlier; golden, boundary, contradiction and regression coverage alongside every supported household rule. |
| 6 Validation Framework and Forward Prediction Ledger v0 | C, E, I | Split current model/benchmark validation, later population validation, historical/prediction error ledger. |
| 7 Household Microsimulation Engine | A, E | Recognise v0.2 assets during stabilisation; harden representativeness/batch execution after Pilot 1. |
| 8 Fiscal and Shared Accounting Spine | C, F, K | Counterfactual accounting contract now; direct fiscal scoring/report spine in F; broader shared/dynamic accounts later. |
| 9 Historical NZ State Store | I, K | Move later; historical policy/data and `as_of` first, national state only with dynamic requirements. |
| 10 National Baseline Engine | K | Defer national trajectories; household baseline/reform runs already exist and are not this national engine. |
| 11 Uncertainty and Sensitivity Framework | B-C, E, J, K | Retain current conditional bounds/points and coverage labels; formal propagation later with empirical/dynamic models. |
| 12 Causal Evidence Library | J | Retain, deferred until sourced behavioural mechanisms require it. |
| 13 Historical Validation Laboratory | I | Retain historical replay, errors and validation; does not block first pilots. |
| 14 National State Transition Engine | K | Retain, deferred until state and trajectory requirements are demonstrated. |
| 15 Canonical NZ Scenario Library | C, K | Split immediate counterfactual scenario contract from later national/multi-year scenario library. |
| 16 Priority Domain Models | H, L | Split statutory-domain expansion from high-value economic domains; demand selects order. |
| 17 Federated Model Graph | M | Defer general graph/federation until independent model execution requires it. |
| 18 Continuous State Estimation | M | Retain long-run state reconciliation; defer national estimation infrastructure. |
| 19 Synthetic Population Programme | E, M | Retain current development population; improve representative data in E; advanced production populations later when justified. |
| 20 Spatial and Physical Twin | L, M | Retain spatial/domain needs; defer broad spatial twin infrastructure. |
| 21 Cost-of-Delay Engine | N | Retain after validated models; people set objectives. |
| 22 Value-of-Information Engine | N | Retain after validation/uncertainty evidence. |
| 23 Policy-Space Search and Inverse Solver | N | Retain later search, bounded by human objectives and constraints. |
| 24 Pareto Frontier Engine | N | Retain later trade-off analysis, never automatic objective selection. |
| 25 Public NZ Futures Laboratory | O | Retain after trust/validation and public-release authority. |
| 26 Policy and Manifesto Analysis Interface | O | Retain later public/institutional analysis; current analyst workbench remains C. |
| 27 Constraint-Based Negotiation Sandbox | O | Retain later scenario/negotiation tooling under human authority. |
| 28 Research and Institutional APIs | C, O | Reuse current APIs immediately; broad institutional/research product later. |
| 29 Natural-Language Policy Interface | P | Defer AI interface over typed, validated model requests. |
| 30 AI Hypothesis Discovery | P | Defer; hypotheses remain human-gated and separate from numerical authority. |
| 31 AI Model Orchestration | P | Defer AI orchestration until validated models exist. |
| 32 AI Explanation and Research Agent | C, P | Reuse deterministic verified explanations now; AI explanation/research later. |
| 33 Autonomous Research Loop, with Human Gates | P | Retain late research loop with explicit human gates. |

Nothing mapped later is declared abandoned. The current numerical/statutory boundaries remain in force until independently sourced bounded implementation changes them.

## 5. Existing code reuse and evidence

| Capability asset on main | New phase | Evidence and remaining work |
| --- | --- | --- |
| WFF and AS deterministic modules, parameter loader and scoped specifications | B | `engines/simulator/{wff,accommodation_supplement}.py`, `policy/loader.py`, existing `policy_specs/`. Reuse supported calculations; tax/core benefit source packs are absent. |
| Combined household runner and shared-fact checks | B | `scenarios/combined.py`, Tasks 28.3-28.5 recorded in the frozen plan; ADR-0017 replaces duplicate facts only with proof. No connected disposable-income calculation exists. |
| Canonical scenario/result IDs, artifacts, PostgreSQL store, replay | C, I | `scenarios/{record,store}.py`, ADR-0013, installed-artifact/code-replay checks. Reuse scenario contracts; historical policy-year execution remains later work. |
| Trace, provenance, evidence coverage and deterministic explanation verification | B-C | `engines/assurance/`, `engines/simulator/trace.py`; #82/#84/#86 and reviewed queue. Keep statutory evidence structures; no general graph needed. |
| Fact catalogues, conditional answers/ranges, intake and verified summaries | B-C | #109/#112/#121/#125-128; #128 still has independent review debt. Parameter-candidate branching and the full household kernel remain incomplete. |
| `PopulationDataset`, dataset manifests, variable dictionary, versioned transforms | E | `semantics/{population,variables}.py`, `data/`, #93/#111/#120. Extend contracts from real needs; do not rebuild the pipeline. |
| Batch baseline/reform runner, weighted groups, withdrawal paths, fiscal component sums | E-F | `scenarios/microsim/`, #94-100. Existing static calculations are valuable assets, not proof of national representativeness or complete fiscal accounts. |
| Seeded/calibrated synthetic development population and cross-validation reports | E | #98/#111/#113/#114/#117/#118/#120/#122. Preserve development label, data vintage, assumptions and known aggregate mismatch limitations. |
| Analyst APIs/pages, pilot container and hosted hardening | C-D | #85/#99/#124/#132; #132 reviewed. Operator-controlled access and deployment contracts stay in place. No external pilot completion is evidenced. |
| Workbench registry, check, generic result blocks and CSV/Excel export | C, F | #133 merged and reviewed; `api/workbench*.py`. Reuse backend/contracts; ADR-0018 acceptance and end-to-end workflow validation remain explicit. |
| Spec, benchmark, regression, golden results/traces, orientation and release checks | B-C, A | `tests/`, protected fixtures and review queue. Preserve all statutory expected values and historical hashes. |

The immediate source/model gap is income tax and Jobseeker Support, Sole Parent Support and Supported Living Payment, their interactions, sourced disposable income and measures. Representative national inference, a full economist report, external pilots, historical states and dynamic/causal capabilities are not established by existing microsimulation machinery alone.

## 6. In-flight work, releases and enforcement

Live GitHub has four open PRs. No submitted reviews or issue comments were returned for any of them at the evidence snapshot. Their bodies describe reviewer roles; do not equate those descriptions or green CI with completed acceptance.

| PR/branch | Exact live head | Verified state and recommendation |
| --- | --- | --- |
| [#138](https://github.com/hemmingsenpeter-byte/poltika/pull/138), `prog/evidence-classes-skill` | `e34e681c380683ff6444a1c42367937e301199f3` | Ready, main base, checks green. Finish bounded work before migration after exact-head review; body still says stacked on already merged #137. Local worktree head `461ee95` is older. |
| [#142](https://github.com/hemmingsenpeter-byte/poltika/pull/142), `infra/security-ci` | `f11f692f930e2e79ead0188bd4664d7288cd9948` | Open; CodeQL actions fails. Fix and review before merge; coordinate overlapping workflow edits with tooling. Migration need not absorb CI fixes. |
| [#143](https://github.com/hemmingsenpeter-byte/poltika/pull/143), `docs/governance-files` | `75eb7a9561c00d3dc87e33fd381e24fe824a0c9f` | Checks green. Finish bounded baseline; CONTRIBUTING's Make targets depend on in-flight tooling. Reconcile new programme references. |
| [#140](https://github.com/hemmingsenpeter-byte/poltika/pull/140), `copilot/finish-installed-artifact-test` | `ffa05168a34b29192ba1bff08622bd1328fe4c59` | Draft, no check runs. Actual delta is hosting documentation for `POLTIKA_POLICY_SPECS_DIR`; scaffold/test requests were already satisfied. Continue as a small independent docs task. |

Recent merges establish #139 delegated acceptance and #141 status tracking, #136/#137 approved constitution, #135 ADR-0017 acceptance, #134 old master, #132 hardening and #133 workbench. #131 records/fixes the #124-127 audit; #123 reviewer tooling is merged. The live tracker still says B1/#139 is in progress, although it merged on 2 October at 16:13:23 NZDT.

Active uncommitted local work must be preserved:

| Branch/worktree | Observed work and disposition |
| --- | --- |
| `infra/dev-tooling`, `/private/tmp/poltika-tooling` | Makefile, pre-commit, lint/workflow changes, dependency/lock edits, plus `conditional.py` and several tests/docs. Finish bounded baseline only; inspect scope before merge and coordinate #142. |
| `prog/units`, `/private/tmp/poltika-units` | Unit module, variable/error changes and tests/docs. Retarget to minimum household/population requirements; no universal vocabulary gate. |
| `prog/periods`, `/private/tmp/poltika-periods` | Period module, errors and tests/docs. Retain dated-spell/native-period requirements for ADR-0017. |
| `prog/entities`, `/private/tmp/poltika-entities` | Entity module, errors and tests/docs. Retain required persons/families/households; no premature national ontology. |
| `prog/ai-gate`, `/private/tmp/poltika-p12` | Constitution and decision-record tests. Finish bounded existing safeguards; do not start AI orchestration. |
| `prog/model-governance`, `/private/tmp/poltika-p15` | Doctrine, model registry/cards and tests. Retain substantially built work; minimise current requirements and preserve stated acceptance gates. |
| `prog/never-build-checks`, `/private/tmp/poltika-p16` | v0.3 release-gate changes. Retarget bounded checks to the new programme. |

Clean open-PR worktrees exist for security/governance and an older evidence-class head. Worktrees for `adr/delegated-acceptance`, `docs/programme-status`, `docs/constitution-decisions` and `fix/hosted-hardening` retain already merged work; no duplicate task is needed. Three registered review worktrees are marked prunable. Do not prune, delete, reset or rebase other sessions' work during this migration.

The GitHub branch inventory returned **92 live branches**, including retained historical/review refs. `claude/architecture-target-state` has no PR and its changes are already contained in main; `fix/q71-140-review` merged as #75. `copilot/clean-up-spaghetti-code` and `copilot/run-simulations-wff-as-calculators` point to current main with no open PR. A retained branch name is not evidence of an active task. Local-only foundation branches above have uncommitted work even though they are absent from the live remote list.

### Quantity branch

`claude/step2-quantity` remains parked at `a9b9168bea02f628be7b2325f10a170fef1a6d36`, explicitly labelled WIP/not for review. Its head adds a 342-line `semantics/quantity.py`; its full main-to-branch merge-base diff includes nine files, 742 additions and three deletions, including older constitution/governance/skill/planning edits.

The draft defines evidence/method enums, uncertainty intervals/quantiles, population grades, its own period, flattened dependencies, a quantity, observation adapter and precision formatting. It has no tests, production callers or implemented assurance adapters. Main's engines/population/workbench already use Decimal values, explicit periods, traces and outcome states. No tax/benefit source pack yet establishes a requirement for this entire wrapper.

Keep the draft intact and deferred; salvage only parts required by the household contract after units/periods/entities are reconciled. Do not merge its stale bundled doctrine, duplicate period types or make universal quantities a tax/benefit prerequisite. ADR-0017's immediate requirements are dated verified facts, relationships and policy mappings, not an eleven-field wrapper around every existing number.

### Release and CI evidence

- Live Git ref enumeration contains only `v0.1.0`: annotated tag object `d2f5b9ab9336207f5ab5ed762504837505fd3b53`, target commit `e41871d3bef43456e68b9590ed23638931e27991`. The [published release](https://github.com/hemmingsenpeter-byte/poltika/releases/tag/v0.1.0) dates to 26 September 2026 at 18:02:13 NZST; a duplicate v0.1.0 draft exists.
- Exact `v0.2.0` ref returned 404; `v0.1.5` also does not appear in live tag refs. Keep Q8. Do not conflate accepted/implemented work with tagged releases.
- v0.1.5's external-user gate skips while `docs/pilot/V0_1_5_PILOT_FINDINGS.md` has blank pilot user/date. Preserve that unfinished gate in live status even after archiving its plan.
- `review_packets/review_queue.md` has one open merged implementation row, #128. Historical v0.2 rows are reviewed; v0.3's gate still skips seven unbuilt capability rows plus its pending review row.
- Main `test` and `pilot-image` succeeded. Tests workflow runs Ruff, strict mypy, evidence coverage, main suite/PostgreSQL, installed artifact and code replay. A green run containing release-gate skips is not release completion.
- #142's [failed CodeQL job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/36960015968/job/110691421610) reports missing explicit token permissions at `data-snapshot-guard.yml:14`, `statutory-value-guard.yml:15`, `tests.yml:17` and `tests.yml:62`. Other substantive checks passed; scheduled external links skipped normally.
- GitHub reports main `protected: true`; rulesets returns `[]`. Classic branch-protection inspection returned 403, inaccessible to the integration. Enforcement details remain unverified; keep Q1 and do not claim protection is absent or the target ruleset is active.

## 7. Stale or conflicting operational documentation

These findings are proposed discrepancy classifications under the frozen review taxonomy, not changes to statutory interpretation.

| Operational contradiction at baseline | Proposed classification and remedy |
| --- | --- |
| `CLAUDE.md` tells agents to follow ADR-0019's 33-step order; `AGENTS.md` begins with frozen BUILD_PLAN and omits the master/status hierarchy | `ARCHITECTURE_ISSUE`: after activation both must direct work to ADR-0021's single master and relevant lane. |
| README calls BUILD_PLAN what is being built now and ROADMAP the master; repository-map hierarchy repeats this | `ARCHITECTURE_ISSUE`: distinguish historical tasks, current sequence and high-level direction. |
| ARCHITECTURE says no frontend, data pipeline or container while main has analyst pages, workbench, data modules and Docker/Compose | `SPEC_ERROR`: separate release/current/target architecture and document actual current assets. |
| ARCHITECTURE uses old numbered state/federation/causal slots and says WFF is the only module | `SPEC_ERROR`: retain historical context where labelled, update operational current claims and use capability names. |
| PROGRAMME_STATUS says v0.1/v0.1.5 Done together and B1 in progress | `SPEC_ERROR`: v0.1.0 tagged; v0.1.5 pilot/tag unresolved; #139 merged. Track assets, releases and gates separately. |
| v0.3 header requires old Steps 1-2/universal Phase 0; roadmap repeats that sequence | `ARCHITECTURE_ISSUE`: household requirements first; governance permanent and population work after Pilot 1. |
| ORIENTATION says current work is the latest collection of release plans | `ARCHITECTURE_ISSUE`: use master/status/lane hierarchy; historical releases are not next-task authority. |
| ADR-0018 proposed despite merged/reviewed backend | `SPEC_ERROR` in any claim that implementation establishes acceptance: keep proposed and ask only for stated acceptance; no inferred approval. |
| Pete queue Q4 uses opaque obsolete step labels; Q7 gives historical horizon artificial near-term urgency | `SPEC_ERROR`: map every retained decision to capability/actual blocker; historical horizon moves to I/K. |
| Review skills still say Pete accepts every PR although ADR-0020 delegates A/B | `SPEC_ERROR`: operational skill language follows ADR-0020; a same-author pass still does not become independent review. |
| New archived destinations affect historical links, test docstrings and skill helper path assumptions | `ARCHITECTURE_ISSUE`: keep root historical compatibility shims and audit active tooling separately; no blanket replacement of history. |

Global matches for ADR-0019, 33 steps, Phase 0, master path and old release mappings must be classified as current operational, historical decision/review, protected reference, or deliberate compatibility. Only operational matches change authority. Phase 0 source-scoping inside a detailed policy lane remains valid; the superseded universal Phase 0 sequencing gate does not.

Pete queue keeps repository enforcement, Māori governance, IDI access, sourced domain/disposable-income/measure decisions, deferred historical horizon and v0.2 tagging. Māori-specific claims and relevant microdata remain gated; unrelated deterministic household work routes around those items where existing doctrine permits. Do not weaken the approved interim governance rule to accelerate the programme.

## 8. Migration PR sequence and activation

Four logical PR scopes keep the change reviewable:

1. **ADR and exact snapshots:** ADR-0021, minimal ADR-0019 status, archive README and exact snapshots/moves. Preserve root compatibility; no production changes.
2. **Master programme replacement:** root master, concise roadmap and reconciled status, all old-step mappings, evidence gates and actual reuse.
3. **Operational reference migration:** agents, README/ORIENTATION, repository map, Pete queue, current architecture/reference language and active lane redirects.
4. **Detailed household lane:** v0.3 source/model tasks under B-C, population work in E, retained maintenance, conformance/validation/pilot dependencies and source decisions.

The scopes should be independently reviewable, but a partially activated chain is unsafe: accepting a superseding ADR while operational agents still read the old sequence produces competing authority. Stage all dependent scopes before activation, review the integrated final tree, and merge the ordered stack in one coordinated activation window. A temporary branch/combined draft is a review staging artifact, not permission to leave main in a mixed-authority state.

Run the author's required preflight and obtain the required reviewer rotation for the final published scope/head. Independent review must inspect the authority change and historical preservation; this author's reconciliation is not independent acceptance of their own migration. No merge, release tag, deployment, external-user contact or resource change follows merely from this report.

Verify archive snapshots against baseline blob bytes, doc links/anchors, policy/protected fixture hashes, the operational-reference audit, and applicable lint/tests. Run existing gates without changing statutory expectations or replacing skipped human-evidence rows with artificial passes. Add a mechanical hierarchy check only if it prevents the actual competing-authority failure; avoid brittle wording tests.

## 9. Risks and controls

| Risk | Control |
| --- | --- |
| Losing bounded task detail while replacing 33 steps | Exact archive plus all-step migration table; preserve active v0.3/maintenance tasks and provenance links. |
| Breaking historical/protected links or helper scripts | Root historical redirects and archive/original-commit headings; inspect skill/helper assumptions and links; preserve protected files/hashes. |
| Accidentally changing doctrine or acceptance authority | Minimal sequencing edits; approved constitution, source/test/IP/LLM rules and ADR-0020 remain controlling. |
| Agents continue implementing the old programme | Migrate both instruction files, orientation and skills' current references; audit integrated final authority before activation. |
| Archive reads as abandoned scope | Explicit retained/deferred mapping and non-authoritative archive README; preserve long-term architecture. |
| Completed code reported as validated national product or tagged release | Separate assets, review state, validation, pilot evidence and tags; retain #128, pilot and Q8 blockers. |
| Active worker changes overwritten or duplicated | Isolated migration worktree; no edits/rebases/pruning in existing worktrees; coordinate CI/tooling overlap. |
| Four PRs temporarily establish incompatible authority | Stage/review all scopes, then coordinated ordered activation; no mixed-authority acceptance recommendation. |
| Public/pilot/resource actions inferred from strategy | Pete's retained Tier C authority applies; create reviewable programme artifacts without external publication or contact. |

## 10. Exactly one next coding task

After the programme migration is complete, implement **the ADR-0017 canonical household record and named WFF/AS mappings**, with byte-identical golden results and result IDs and existing request formats retained as adapters. Build only the dated facts, person/family relationships, verification states and native-period views those mappings need; reuse the existing engines and reviewed specifications. Retire a pairwise contradiction check only where proof makes it impossible, and retain meaningful period/definition checks.

This accepted, bounded task connects existing value on the new critical path without waiting for universal registries or the generic quantity draft. The policy mappings require the prescribed independent review. Income-tax/benefit sourcing remains necessary parallel preparation, not permission to invent rules or begin those calculators. No implementation starts as part of the documentation migration.

The [reference audit](2026-10-03-reference-audit.md) classifies every matching
pre-migration tracked text line (142 matches across 31 files), including retained
historical references and operational files reconciled by the migration.
