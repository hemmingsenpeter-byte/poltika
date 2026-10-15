# Programme status

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

**As of:** 13 October 2026. **Baseline:** `origin/main` after #216
(`7342e52`), reconciled against live GitHub state; rows owned by open
PRs (#217 for Task 7, #218 for Task 6) are left for those PRs. This
refresh records existing work and claims no new
capability acceptance. Campaign-policy and NZ Budget overlay planning rows
(C14a, D16a, F24a, I29a) were added by #196 and are planning only.
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

The 3 October construction-mode drafts in the
`/Users/peterhemmingsen/poltika-p1-*` worktrees were never committed, pushed or
reviewed. On 7 October 2026 the household, income-tax, benefits and
simulation-analysis worktrees still held uncommitted files last modified on
3 October. Their dispositions are in "Existing workers" below (decision log D22):
all are parked, none is an active writer, and none is policy authority. Deleting
any of them is a Pete decision. #148/#151 are the merged source-first lanes for
income tax and benefits.

Reporting: the original `build/p1-reporting` draft (`8a541368`, committed,
local only) and [#154](https://github.com/hemmingsenpeter-byte/poltika/pull/154)
(isolated review fixes, head `5a45719`) are parked for Phase F Task 24 (D22).
#154 was closed unmerged on 7 October 2026 with its branch
`codex/reporting-review-fixes` and review records retained. Nothing on `main`
supersedes it. Task 24 remains gated by 21–23, and the prototype changes no task state.

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
| Main ruleset / squash auto-merge | Done (applied 2026-10-05 by Claude Code under Pete's delegation); red-check blocking observed in #168 | Ruleset id 24478578 | Squash only, strict up-to-date, eleven required checks, no bypass, delete_branch_on_merge. ADR-0007 recorded that the plan could not enforce required checks on a private repo; The #168 probe at fb92c17 observed required test FAILURE, eight other required checks SUCCESS and GitHub BLOCKED. The obsolete Gate A red-check caveat in `BUILD_PLAN_PROGRAMME.md` is corrected by this refresh; the #168 evidence does not itself accept Gate A. |
| Evidence-classes skill | Done; Claude Code | #138 merged, `38a3f17` | Legacy 1.7. |
| Dev tooling | Lapsed, no surviving work (D22) | No PR | On 7 October 2026 the worker's worktree no longer exists (`git worktree list` marks it prunable), and its branch `infra/dev-tooling` (`ab56f4c`) is an ancestor of `main`, so nothing is left to finish. `conditional.py` is on `main` through #128/#150. New tooling needs its own bounded task. |
| Self-hosted CI runner | Retired 16 October 2026; Claude Code (D41, superseding D21) | D21 was #182, `dd2c485` | Every job runs on GitHub-hosted `ubuntu-latest` again and the repository is public, so hosted minutes are not charged. Fork pull requests run every check; `fork-pr-gate` and `image-inputs` are removed and `pilot-image` runs on every PR and push to `main`. Check names are unchanged and still match ruleset 24478578. `pete-mac-1` was stopped and its LaunchAgent uninstalled; its GitHub registration was deleted on 16 October once a stranded job cleared. `~/actions-runner` remains on disk. |
| Integration-train closeout | Done; Claude Code merges (D18), GPT/Codex rechecks | #161–#182 merged (#170 closed, superseded by #176; #168 closed, retained probe evidence) | Final-head reviews are in `reviews/2026-10-06-integration-train.md`. #181 closed the follow-ups: review-rule wording and test, household id `\Z`, model-card policy versions, FastAPI telemetry, and the #162 and #177 recheck findings. |
| Security CI | Done; Claude Code, GPT/Codex review and fixes | #142 merged, `b292666` | Its checks are among the eleven required by the applied Q1 ruleset. |
| Governance files | Done; Claude Code | #143 merged, `6a7da14` | |
| Hosting policy-path documentation | Done; Claude Code | #140 merged, `96900a4` | Documents `POLTIKA_POLICY_SPECS_DIR`. This is not the dev-tooling PR. |
| Independent review debt | Recorded, 13 October 2026: 8 open rows on `main` (`7342e52`); GPT/Codex rechecks, Claude Code coordinates | `review_packets/review_queue.md` | Open: #174 (R1 P2 fixed in #179), #162 (R1 P2 fixed in #181), #179, #181 and #182 (Claude-authored), each awaiting a Codex recheck of the fix's exact final head; #189 (merged with review waived, D30); #193 (Codex clearance in #217, not yet merged); and #211's boundary-proposal row. #207 and #216 cleared on 13 October. Apart from #193's documentary specification, none touches `policy_specs/`, `engines/simulator/` or a calculated amount, and none blocks Phase B work. #154's Claude test commits, which had `poltika-reviewer` passes but await a Codex recheck, are recorded as a deferral, not debt (#184). #128 stays closed (#150, #152). |

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
| Scenario identity and replay | #60, #63, #64, #65, #68; #187 | Household artifact identities, replay/code checks and append-only PostgreSQL store. #187 adds durable `/api/v1` reform scenarios/runs and retained Workbench results; legacy `/microsim` and `/workbench` run lookups remain in memory. B0.1 frontend acceptance and deployed persistence are separate gates. |
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
| Workbench backend / export | #133; ADR-0018 accepted (Pete, 12 October 2026) | Registry, checks, generic blocks, worked examples, CSV/Excel export reviewed; completed workbench UI not evidenced. |
| Epistemic constitution | #136, #137, Pete approval 2 October | Eight classes and seven decisions are approved; preserve them while re-scoping implementation. |
| Source currency | #92 | Existing report/workflow; statutory new-year parameters still require dated primary sources. |

## Phase A — Stabilise

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bounded governance/baseline closeout | Done | Claude Code; GPT/Codex reviews | #138–#143, #161–#167, #169, #171–#182 merged | The five open Codex rechecks are review debt (Task 2), not unfinished work. Dev tooling lapsed with no surviving work. | Professional-baseline rows above; constitution approved; ruleset red check observed (#168) | Step 1; baseline B1–B5 |
| 2 | PR/review-debt reconciliation | Done (#184 merged at `88107a2`) | Claude Code coordinates; GPT/Codex reviews | #181 queue refresh; this refresh (#183); #184 closeout record (`88107a2`) | Every open PR, every named stale branch and every draft worktree has a disposition here. The per-branch classification of all remote branches (87 delete candidates, 16 kept) is #184's `reviews/2026-10-07-closeout.md`; deleting them is Pete's (PETE_QUEUE Q12). Open Codex recheck scopes block only their own rows. | `review_packets/review_queue.md`; #128 closed by #152 | W1; P17 |
| 3 | Release baseline | Done (records agree); tags stay Pete's | Pete; Claude Code prepares | No new release PR | v0.1.0 and v0.2.0 (annotated, `63f5f0d` → `adf4058`) are on the remote. v0.1.5 is untagged and its external pilot is not recorded: it stays outstanding under Q11 and maps to D. It does not block B. | Release table below; D10 | 7.1; v0.1.5 8.2–8.6; v0.2 10.3 |
| 4 | End abstract Phase 0 expansion | Done | Claude Code coordinates | #144–#147 merged | All active instructions point to this master. Old workers are parked by explicit disposition (D22, "Existing workers" below). | ADR-0021; snapshots preserve old tasks | Steps 1–2 sequencing |

## Phase B — Household economic kernel

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B0.1 | Web frontend (single product surface) | In progress | Claude Code; GPT/Codex reviews shown amounts; Pete hosting/access | #185 plan, #186 B0.1.1 (`57e4ddb`), #187 B0.1.2 (`26cd8a6`), #188 B0.1.3 (`9a79a2e`) and #189 B0.1.4 scenario experience (`8380f4b`, merged 11 Oct with review waived by Pete, D30) merged. #206: B0.1.5 Models/Data complete and tested; B0.1.6 accessibility (jsx-a11y, axe) and SVG charts (D31); B0.1.7 deploy prep (FRONTEND.md, HOSTING database step, restart-persistence test). Independent fresh-context reviews: B0.1.5 and B0.1.6 ready (P3s fixed); #189 delta `5be777c..2fc06ed` no P1/P2 #209: B0.1.6 axe over Home and the empty, loading, error and unavailable states (one landmark violation fixed), a responsive pass pinned in jsdom, consistent empty-state copy, and a scrollable chart region (D34). | B0.1.6's real-browser check is done in headless Chromium and WebKit at 360px (12 October, #209/#212; third pass on `7342e52` on 13 October fixed four sub-24px summaries; [record](reviews/2026-10-12-b016-360px-browser-check.md)). Open: Pete's human check on a real phone (Q23; iOS Safari, Android Chrome). The RSC prefetch P3 is fixed: nested routes get their export payload, and soft navigation is shown in headless Chromium (15 October). B0.1.7: Pete's Render actions (Q15). The live service was found **open without a password** on 15 October; Q15 lists the exact steps: set `POLTIKA_ACCESS_PASSWORD`, remove the override of the image's fail-closed default, set `POLTIKA_DATABASE_URL`, set the health-check path, confirm backups; and `web` and `fork-pr-blocked` as required checks (Q20). Then the live smoke (401 without password; Home, Scenarios, a created run, Models, Data; deep link after restart). The `except ValidationError` P3 was narrowed in #211 | [BUILD_PLAN_B0_1_WEB.md](BUILD_PLAN_B0_1_WEB.md); ADR-0023; [deploy readiness](reviews/2026-10-11-b017-deploy-readiness.md); [FRONTEND.md](docs/web/FRONTEND.md). No B0.1 deployment or formal Pilot 1 acceptance is evidenced | New (7 Oct 2026); surface for C 15 |
| 5 | Minimum household semantics | Done (GPT/Codex mapping review cleared with MAP-01's fix, #216) | Claude Code; GPT/Codex mapping review | #161 (units, `9e67009`), #169 (exact rescale), #166 (periods, `c72c409`), #171 (entities, `b176ddc`), #181 (household id `\Z`); unit binding (`semantics/unit_binding.py`) in #207 | Every `ParameterUnit` and every input unit and period a `policy.yaml` declares binds to a registered unit, a `PeriodType` and a per-entity qualifier. A test over every policy fails on an unregistered unit or period, a parameter or input whose period differs from the policy's, a unit-bearing input with no period, and a spec directory silently skipped. The AS stock unit `NZD` (asset ceilings, thresholds, `cash_assets`) is a stock with no period; `cash_assets` is the caller's balance for the assessment week (Q19 (1), decided 13 October, D38). Next: GPT/Codex mapping review ([packet](review_packets/task5_6_unit_binding_household_mapping.md)) | Gap analysis in `docs/programme/2026-10-07-task5-gap-analysis.md`; `units.convert`, `units.rescale` and `periods.convert_amount` still refuse every period, dimension or price-basis change; independent fresh-context review cleared the P2 fix (planted annual parameter in AS now fails) | 2.1–2.6, 2.10 scoped |
| 6 | Shared household model | In progress (ADR-0017 1.1–1.3 merged; 1.4 in its PR) | Claude Code; GPT/Codex mapping review | `semantics/household.py`, `scenarios/household_mappings.py` in #207 (from the parked draft, reviewed; date of birth and age dropped) | One `Household` holds facts once with dated spells; `to_wff`, `to_as` and `to_combined` map it to the existing scenarios, and adapters build it from the existing request formats. A spell is never scaled across periods: a spell not tiling the policy period gives `needs_review` `HOUSEHOLD_SPELL_PERIOD_MISMATCH` citing Q10 (independent review P2, fixed). WFF needs a child list asserted complete (`HOUSEHOLD_CHILD_LIST_INCOMPLETE` otherwise; reviewer P2, fixed). Codex mapping review done 12 October: MAP-01 (P2, overlapping benefit spells) fixed with the Q19 decisions of 13 October (D38) in #216, verified by GPT/Codex at `19128cb`. 1.4: `run_household()` keeps the restated checks (partner status narrowed), retires the claimant-link check and reports a supplied per-child count difference as definitional for household inputs ([#218](https://github.com/hemmingsenpeter-byte/poltika/pull/218); Codex R1/R2 P2 fixed, awaiting recheck), with Q19 (7)'s relationship-change fact (D39); awaits Codex's final-head recheck. Q19 (6) waits until the household is canonical | ADR-0017 accepted; round trip over the golden households, interaction cases and WFF/AS spec cases and benchmarks gives identical scenarios, result payloads and result ids (one listed refusal: WFF lists 1 child, AS asserts 2) | 2.7; v0.3 Phase 1; W6 |
| 7 | Personal income tax | In progress (#193 draft review cleared; numeric specification next) | GPT/Codex sources/values and independent review; Claude Code implementation; Pete retained decisions | #148 source scope merged at `164fdbd`; #193 gated specification merged at `aa0c9c6`, final head `b108c40`; [13 October clearance/handoff](reviews/2026-10-13-pr193-codex-clearance.md) and [independent Claude source review](reviews/2026-10-11-pr193-independent-source-review.md) | Pete decided Q16–Q18 on 12 October (D36). Next: apply those decisions to existing DEC/spec/source metadata and prepare the numeric specification, source-linked values, facts, independent cases and official benchmarks. Whole-dollar taxable income only is an Assumption; other precision is `unsupported`, with no invented output rounding. Annual authority stays `needs_review` until Royal assent and dated reviewed source checks; full-period amendment coverage remains required. Engine follows specification/value review and Tasks 5–6 mapping | IT-01–IT-08 source draft reviewed; Codex clearance of Claude follow-ups and final integration recorded. IR3G excluded as benchmark (`SOURCE_CONFLICT`). No approved executable specification, parameters, benchmarks or engine; Task 7 and Gate B remain incomplete | 3A; v0.3 0.1 / Phase 2 |
| 8 | Three core main benefits | In progress (source scope only) | GPT/Codex source writer; separate evidence checker; Claude Code implementation; Pete D1 | #151 source scope merged at `38e5629` after final-head Claude cross-model review (`reviews/2026-10-06-pr151.md`) | Next: source-approved specifications. Pete approved bounded single existing-grant slices (decision-log D11; SLP is the s 34 restricted-capacity route, confirmed 6 October); payment/rounding, assessment and source/specification gaps remain; 5–6 for integration | Three sources-only catalogues; JS category corrected at `b238820` and rechecked by separate same-model checker; no approved values/spec/engine | 3A; v0.3 0.2 / Phase 3 |
| 9 | Household dependency graph | Not started | Claude Code; GPT/Codex interaction review | None | Sourced interactions; 6–8 for integrated paths | Existing combined WFF/AS runner reused | 3A; v0.3 Phase 4; W7 |
| 10 | Disposable income | In progress (source scoping commissioned) | GPT/Codex sources; Claude review; Pete definition acceptance | #172 source comparison merged at `30935de` after final-head Claude cross-model review (`reviews/2026-10-06-pr172.md`) | Pete's D2 definition choice from the reviewed candidates; connected 7–9 outputs; uncovered components stay explicit | Existing per-policy results remain separate | v0.3 0.4 / 5.1 |
| 11 | EMTR/withdrawal/participation measures | Blocked (EMTR first approved) | GPT/Codex definitions; Claude Code | None | Reviewed income/period paths and Q10; adequacy follows D2 source review; v0.2 D9 unresolved | #96 per-policy withdrawal profiles/sweeps reuse | v0.3 Phase 5; v0.2 8.6–8.7 |

## Phase C — Assurance and analyst product

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | Legislation conformance | In progress (WFF/AS matrix) | Claude Code matrix; GPT/Codex independent cases | [WFF/AS conformance matrix](reviews/2026-10-11-wff-as-conformance-matrix.md) and `tests/unit/api/test_wff_as_conformance_api.py` (27 non-numeric API tests) in #207 | 57 rules mapped: 55 covered, 2 partial (W-16 relationship change is not an input; A-08 cash-asset imputation step edges are numeric). Six numeric boundary cases are listed for the test-doctrine process, not written. Next: those cases through the doctrine, and matrices for each new policy as it lands; P6 only for publication | Existing Spec/Benchmark/Regression, goldens, value guard | Step 5; v0.3 Tier 1 matrix |
| 13 | Model/benchmark validation | Not started | Claude Code; GPT/Codex independent checks | #117, #114 reuse | B models and bounded validation contract; P18 tolerances | Existing cases and cross-validation reused | 6.1–6.3; Step 5 |
| 14 | Counterfactual scenario contract | In progress (first increment: reform run manifest, migration 0003, `verify_reform_run`, audit-tab block; PR pending) | Claude Code; GPT/Codex reviews | #60, #63, #64, #65, #68, #94–#95 reuse | Complete retained baseline/reform/comparison contract with 15 | Household persistence/replay and population reform identities exist separately | 8.5; Step 15 core split |
| C14a | Proposed-policy claim intake (bounded overlay) | Not started (plan only) | GPT/Codex sources/mapping checks; Claude Code implements | None (documentation plan only) | B approved supported slice and C 14; original claim, dates/status and reviewer-gated mapping; [use-case spec](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md) | Existing source/provenance/scenario IDs can be reused; no campaign claim ingestion or analysis implemented | New overlay (9 Oct 2026) |
| 15 | End-to-end Analyst Workbench | Not started | Claude Code; GPT/Codex review | #133 backend reuse | Usable UI/workflow, 12–14 (ADR-0018 accepted 12 October 2026) | Backend/CSV/Excel reviewed; no completed workbench UI evidence | P8; ADR-0018; Steps 4/28/32 reuse |

## Phase D — Pilot 1

| Task | Capability | Status | Owner | PR | Blocker / next action | Evidence / reuse | Old mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | Real household analyst pilot | Pete | Pete user; Claude Code facilitates; GPT/Codex evidence | #85, #89, #124, #132 reuse | Name external user/question; B/C workflow; record session/feedback | Existing scripts/template/hardening; external-user field blank | v0.1.5 8.2–8.5; new pilot gate |
| D16a | Campaign-policy example-household pilot (optional) | Not started (plan only) | Pete chooses user/question; Claude Code facilitates; GPT/Codex sources review | None (documentation plan only) | C14a; actual supported proposal; Task 16 evidence; optional and does not block Gate D | Pilot templates and Workbench can be reused; no political-policy pilot evidenced | New overlay (9 Oct 2026) |

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
| F24a | Recurring NZ Budget release analysis (bounded overlay) | Not started (plan only) | GPT/Codex checks official sources/comparators; Claude Code implements; Pete scope/publication | None (documentation plan only) | E 17–21 and F 22–24 for supported measures; release/initiative inventory, coverage ledger, comparable fiscal reporting; not a Gate G blocker | Existing source preservation, model and report contracts can be reused; no whole-Budget runner or estimate validated | New overlay (9 Oct 2026) |

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
| I29a | Historical Budget as-of replay (bounded overlay) | Not started (plan only) | GPT/Codex historical sources; Claude Code replay; Pete P11 horizon | None (documentation plan only) | I 27–29; dated information vintages and comparable historical sources; I 30 required only for real prediction tracking | Existing code replay and archived snapshots reuse; no past-Budget as-of test accepted | New overlay (9 Oct 2026) |
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
| 51 | Policy-analysis interfaces | Not started | Claude Code; Pete publication | None | Gate O, trust/permission and validated proposals/Budget results from C14a, F24a and I29a; no normative scoring | Existing analyst Workbench reused; not the first campaign/Budget analytical implementation | Step 26; late public surface |
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
| AI gate, `prog/ai-gate` | Old 1.2: [#163](https://github.com/hemmingsenpeter-byte/poltika/pull/163) merged at f9c69d8 on 6 October after final-head Claude review and green CI; Pete's accepted constitution remains intact. Artifact gates and known gaps are explicit; future enforcement and Gate C precision implementation remain open. |
| Model governance, `prog/model-governance` | Old 1.5: [#164](https://github.com/hemmingsenpeter-byte/poltika/pull/164) merged at `94df1a0` on 6 October after final-head Claude review and green CI; Pete accepted the bounded governance choices. Registry/card checks cover the four existing models; arithmetic validation is not national-population validation, and output labels remain pending. |
| Never-build checks, `prog/never-build-checks` | Merged in #162 at `5a8c17e` (old 1.6); the validation-grade row skips until grades exist (old 7.2). |
| Units/periods/entities, old 2.2–2.4 | Units merged in #161 at `9e67009` (its `convert` is a stub: no sourced deflator rule exists). Periods (old 2.3) merged in #166 at c72c409; Entities (old 2.4) merged in #171 at `b176ddc`. Both recovered drafts were committed with Pete's approval of 2026-10-05. The AS-week-in-WFF-year containment is registered; annual/weekly value conversion is refused (v0.2 D8). Follow-up: period and relation source strings are checked by a line-range test, not resolved to the cited text. Reconcile with minimum B 5 requirements. |
| Quantity draft, `claude/step2-quantity` | Parked draft, not for review; no universal schema prerequisite. P3 display obligation remains. |
| Household draft, `poltika-p1-household` (uncommitted) | Parked input to Task 6 (D22). Unreviewed and not accepted; the Task 6 implementer reviews it before reusing any of it. |
| Income-tax and benefits drafts, `poltika-p1-income-tax`, `poltika-p1-benefits` (uncommitted) | Parked (D22). They were written before the source-first lanes (#148, #151) merged. Their `policy_specs/` and engines are not policy authority, and Tasks 7–8 restart from source-approved specifications. |
| Simulation-analysis draft, `poltika-p1-sim-analysis` (98 uncommitted changes) | Parked (D22). No programme task expects it; Phase E reuse needs a fresh bounded plan. |
| Reporting, `build/p1-reporting` (`8a54136`) and #154 (`codex/reporting-review-fixes`, `5a45719`) | Parked for Phase F Task 24 (D22). #154 was closed unmerged; its branch and review records are retained. Its open P3s (control characters in the SVG, unlabelled standalone population tables) and the Codex recheck of its Claude test commits carry over if it is revived. |
| Closed PR branches `close/reviewer-rotation-20261005` (#170), `close/ruleset-red-probe-20261005` (#168), `docs/claude-code-repo-closeout` (#155) | Retained historical evidence. #170 was superseded by #176 and #167; #168 is the ruleset probe ADR-0020 cites; #155's plan was superseded by the executed closeout. |
| Unmerged no-PR branches `codex/review-debt-end-train-20261006`, `codex/slp-packet-locator-20261006`, `copilot/fix-bug-in-model-method` | Superseded: their content reached `main` through #177/#180, #177 (`354079e`) and #155's closed plan respectively. Deletion is a Pete decision. |
| Merged-PR head branches still on the remote | Safe to delete, since their squash commits are on `main`, but deletion is a Pete decision (Tier C: deleting history). Nothing is lost by keeping them. |
| State schema, old 2.8 | Not started; old planned scope retained in archive. K 35 deferred pending real model requirements. |
| Dataset evidence classes / existing DEC classes | Approved constitution follow-ups retained; immutable manifests and hash-bound DEC files are not silently rewritten. Pete confirms interpretations/classes where required. |
| Monotone declarations and candidates, v0.3 1b.2b/2c/3e | Source-derived declarations not started; structured candidate evidence still required. Do not substitute author test fixtures for reviewed policy content. |

Māori governance blocks affected claims/outputs and microdata work where
applicable, not unrelated deterministic household sourcing. IDI access
belongs to later E/M work. P11 historical horizon, P7 prediction targets,
P13 domain priority, P14 search credibility, P18 tolerances and P20 national
scenarios remain unresolved at their new phases; P8's strategic workbench
choice is resolved, and Pete accepted ADR-0018 on 12 October 2026. D8/D9 remain
explicit unresolved period/income-method dependencies for B/F.

The [pre-migration status snapshot](docs/archive/status/2026-10-03-programme-status-adr0019.md)
retains every old row; the master's 33-row migration table links all
[old detailed programme steps](docs/archive/programmes/2026-09-29-adr0019-master-programme.md).
Choose next work from the current master/status, not from those historical rows.
Next coding handoff: close Task 5 with the one bounded patch in its row, binding
the policy-spec units to the semantics registries. That patch changes no
calculated amount. Then start Task 6 from ADR-0017 and v0.3 1.1–1.3, reviewing the parked
`poltika-p1-household` draft as input. Primary-source specifications for income tax
(Task 7) and the three benefits (Task 8) proceed in parallel from #148/#151 as
GPT/Codex source work.

## Closeout PRs (7 October 2026)

#184 (closeout record: `reviews/2026-10-07-closeout.md`, PETE_QUEUE Q12–Q14, and the #182 and #154
queue rows) merged at `88107a2`. #182 and #181 merged, and #154 was closed unmerged (parked, above).
#155 is closed, and Dependabot #156–#160 merged on 6 October. Work opened after that historical closeout is tracked separately. As checked on 10 October, #183, #189, #191 (draft audit), #192, #193 (gated income-tax specification), #194/#195 (draft decision proposals), #196 (roadmap overlays) and Dependabot #197–#202 are open. #186, #187, #188 and #190 are merged. #191's
findings need individual dispositions/remediation; merging its documentation
would not resolve them. #193 does not complete Task 7 and cannot clear pending
annual-authority, precision or source-conflict decisions by itself. Neither
frontend deployment nor a formal external Pilot 1 is accepted by this refresh.
