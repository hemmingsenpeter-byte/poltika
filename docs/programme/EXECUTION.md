# Programme execution

**Started:** 3 October 2026, Pacific/Auckland. Pete's active goal appoints
GPT/Codex to coordinate Poltika with separate writing, security, testing and
simplification roles. This file records that operating practice and the
current handoff; [PROGRAMME_STATUS.md](../../PROGRAMME_STATUS.md) remains the
task tracker and [BUILD_PLAN_PROGRAMME.md](../../BUILD_PLAN_PROGRAMME.md)
remains the single build order. It does not add a second roadmap. This
execution record is proposed in draft [PR #149](https://github.com/hemmingsenpeter-byte/poltika/pull/149).

## Roles and capacity

There are four concurrent slots including the coordinating agent, so at
most three subagents run at once. Rotate specialist checks after a writer
finishes; use another fresh agent when independence from the author matters.

| Role | Responsibility | Required output |
| --- | --- | --- |
| Project manager | Read live state, choose the next unblocked increment, preserve other sessions, assign isolated worktrees, resolve routine engineering findings, track dependencies and handoffs | Accurate task/PR/owner/blocker rows and a short session digest |
| Writer | Implement one authorised increment or source the policy slice from primary NZ evidence | Bounded commit, relevant documentation and author preflight |
| Security reviewer | Independently inspect actual threat boundaries, token/data handling, dependencies and changed execution paths | Reproducible findings with discrepancy class, severity and pinned SHA |
| Testing lead | Exercise acceptance criteria, meaningful regressions and failure cases on the pinned revision | Commands/results, explicit skips and environment limitations |
| Simplification reviewer | Check contracts and remove concrete process contradictions or complexity with practical costs | Minimal corrections and final diff check; no speculative redesign |
| Source/evidence checker | Independently retrieve dated primary evidence and compare the proposed scope/rules | Source locators, discrepancies, coverage limits and review label |

These are development roles, not a new runtime agent framework. A fresh
GPT/Codex check of GPT/Codex-authored work is a same-model check. It does not
clear the GPT/Claude reviewer rotation. The author never approves its own work.

## Working cycle

1. Read the master, live tracker, applicable detailed lane, doctrine/ADRs,
   repository map and Pete queue. Inspect actual PRs and worktrees; preserve
   uncommitted work owned by other sessions.
2. Take the highest-priority startable increment. Research may run beside
   coding where the master allows it. Keep sources, parameters/cases,
   implementation, interactions and release in their normal review units.
3. Assign one writer to an isolated branch/worktree. Give reviewers mechanical
   inputs and the acceptance contract before the author's rationale.
4. Commit the change, run author preflight, and check exact revisions with
   separate security, testing, maintainability and source roles as relevant.
   Record findings before fixes, using the review taxonomy.
5. Fix confirmed errors in the existing PR. Recheck remote heads and push
   without force; validate final changed behavior and inspect latest-head CI.
6. Update the same PR's tracker row. An open PR is not Done. Preserve source,
   protected-value, interpretation, release and independent-review gates.
7. Route around blocked choices and start useful independent work. Give Pete
   a concrete source-linked decision when its dependent action is ready.

Acceptance follows [ADR-0020](../../adr/0020-delegated-acceptance.md): Claude
Code holds delegated Tier A/B acceptance; Pete holds Tier C. This coordination
request does not silently transfer merge or reserved decision authority.
Publication, resources, release tags and protected values keep their gates.

## First work-cycle handoff — historical snapshot, 3 October 2026

This snapshot precedes #150's merge. CI/review statements apply to the
recorded heads and the then-current `e52f5d3` baseline; the second-cycle
handoff below supersedes its next-action status without rewriting the evidence.

The live GitHub list showed migration #144–147 prepared as drafts, not merged.
Preserve that stack; new programme/source documents are stacked on its final
branch `docs/economist-programme` at `422b055`. Do not repeat the migration.

| Work | Actual result | Remaining gate |
| --- | --- | --- |
| #142 security CI | Fixed PR issue-token exposure, unverified private-CodeQL use and failing permissions. Bandit/zizmor, immutable action pins and isolated issue publisher tested at `941cbc18`; final record `f483fb90`. All applicable latest-head CI jobs pass, including database/artifact/code replay in the test job and image smoke. | Claude acceptance; Q1 check-list update after merge. Bandit retains four medium XML findings and 35 low findings for engineering triage. |
| #143 governance | Fixed private reporting route, incomplete release-gate allowance, absent Make target instructions, CI-tier comments and false scanner claim. Fresh check of `82990da` has no actionable findings; all latest-head CI jobs pass. | Delegated acceptance; confidential external contact before publication. |
| #138 evidence classes | Corrected the unconditional AI-draft stop to preserve approved promotion gates. Fresh check of `d868564` has no actionable findings; all latest-head CI jobs pass. | Delegated acceptance; migration references remain separate. |
| #140 hosting guide | Exact `ffa0516` installed-wheel probe passes; no actionable defect in its added policy-path guidance. | Draft/main CI and author/acceptance handoff. Local database sub-probe was unavailable. |
| #148 income-tax source scope | 12 primary-source entries and reviewable D1 options; fresh source check at `cd2f116` has no actionable discrepancy. Source files unchanged in tracking commits. | Migration integration, Claude independent review, Pete D1, enacted-period coverage, rounding/benchmarks and later onboarding gates. |

See [the verification record](../../reviews/2026-10-03-programme-verification.md)
for the local test-run distinction and environment limits. No model amount,
protected expected value, data snapshot or production code changed in this cycle.
No PR or migration was marked merged in this first-cycle snapshot.

Next startable work is the outstanding #128 independent review and primary
source scoping for the three core main benefits. The next coding slice remains
ADR-0017's shared household model with named WFF/AS mappings and golden parity,
coordinated with existing minimum-semantics owners. Neither income-tax scoping
nor release tags justify building deferred universal registries or AI layers.

## Second work-cycle handoff — 3 October 2026, after 01:38:42 UTC

The recorded main advanced through actual delegated acceptance of #150;
the migration #144–147 remains unmerged and preserved. This is an update to
draft #149, not programme adoption or acceptance of this revised PM record.

| Work | Recorded result | Remaining gate |
| --- | --- | --- |
| #150 conditional-summary fixes | Actual fresh Sonnet review approved the submitted fixes; Opus accepted Tier A and squash-merged head `ea872403acdd3e3a37a15040161d4fb847332f12` at `3bea73fba44f9173ecc4ee3d00be3aa22328b993`. Latest-head PR checks and up-to-date branch were checked by Opus before merge. | #128 queue closure remains a separate docs change; this merge does not complete a new economic-model capability. |
| #128 review closure / #152 | Draft #152 targets main at `2404ab47fc17b5c685382155cf616e5b014e92ee`. All four latest-head CI checks SUCCESS; test finished 02:01:40 UTC. Separate same-model doc check has no findings; local checks record 7 passed/7 unbuilt-capability skips. | Still OPEN/DRAFT. Actual Sonnet review has not run; Claude review/Opus acceptance await destination consent. No closure landed on main or source/release approval inferred. |
| #151 core-benefit source scope | Draft final head `50f13f44533cdab2939dd80e37538c8313ecb774`: three source-only inventories and proposed slices/interactions. Separate source check found a JS category discrepancy; narrow correction `b238820` was rechecked and resolved. | Separate same-model checking does not replace Claude source review or Pete D1. Payment/rounding, assessment basis, population breadth and later onboarding gates remain; no values/spec/engine approved. |
| #148 income-tax source scope | Draft final head `0db2bfaf787280a6cda252f6fa7e9287ba107ef7`; retained dated source check has no actionable discrepancy in its bounded draft. | Claude source review, Pete D1, enacted-period coverage and rounding/benchmark gates remain. |
| #138/#142/#143 baseline closeout | Actual read-only Sonnet review reports no blocking findings on the submitted artifacts, distinct from the earlier GPT/Codex checks. | All remain behind main after #150 at this handoff. Refresh bases, inspect changed diffs, obtain latest-head CI and Opus acceptance. Review of earlier artifacts does not automatically cover later updates. |

The actual Claude results are retained in the verification record with their
local evidence-file identities and limits. Sonnet did not execute broad
test/lint runs; the baseline Sonnet pass could not independently verify live
CI or action-pin authenticity. These limits do not become new test evidence.

Automatic approval review rejected the attempted new #152 Sonnet invocation
because transmitting the private review payload to Anthropic lacked explicit
destination consent. The bounded permission request is pending. This blocks
the affected external reviewer/acceptance steps; authorised local writing,
verification, conflict preparation and source work continue. It does not
mark the whole programme blocked.

Next coding handoff is to reconcile and review the existing ADR-0017 writer's
increment in `/Users/peterhemmingsen/poltika-p1-household`, branch
`build/p1-household`, before assigning another household/model/mapping writer.
Its uncommitted `semantics/household.py`, `scenarios/household_mappings.py`,
roundtrip/semantics tests and pass1/pass2 documents must be preserved.
Source-derived WFF/AS mapping review and byte-identical golden results/IDs
remain acceptance requirements, coordinated with minimum-semantics owners.
The planning review found no genuinely unowned household implementation task:
take a pinned review intake of that writer's committed handoff first. A later
additive snapshot/trace parity harness may be unoccupied after that handoff;
it is not startable while owner files move. Branch-local construction-mode
claims are unaccepted ownership evidence, not capability acceptance.

### Existing draft ownership — second-cycle inventory

The coordinator's planning inventory records the following uncommitted
branch-local work. This note is ownership evidence only: no code audit,
test result or approval is inferred, and no capability becomes Done.

| Existing worktree | Branch | Handoff constraint |
| --- | --- | --- |
| `/Users/peterhemmingsen/poltika-p1-household` | `build/p1-household` | Preserve household/mapping files, tests and pass1/pass2 docs; pinned review intake comes first. |
| `/Users/peterhemmingsen/poltika-p1-income-tax` | `build/p1-income-tax` | Preserve the implementation draft; reconcile with source draft #148 and source/slice gates before assigning a tax writer. |
| `/Users/peterhemmingsen/poltika-p1-benefits` | `build/p1-benefits` | Preserve the implementation draft; reconcile with source draft #151 and source/slice gates before assigning a benefit writer. |
| `/Users/peterhemmingsen/poltika-p1-reporting` | `build/p1-reporting` | Preserve the reporting draft and obtain its owner's pinned handoff before assigning overlapping reporting work. |
| `/Users/peterhemmingsen/poltika-p1-sim-analysis` | `build/p1-sim-analysis` | Preserve simulation-analysis work, including both existing snapshot test files; obtain a pinned owner handoff before overlapping changes. |

Do not assign new tax/benefit/reporting/simulation writers from older
Not started rows alone. Future additive household snapshot/trace parity
must use an unoccupied path after the pinned owner handoff; the existing
snapshot test files are already owned. #148/#151 retain their separate
source-only draft state; these implementation observations do not approve
their policy content, values or construction-mode claims.

The next engineering handoffs are #152 closure,
baseline PR refresh/acceptance, migration integration and the new PM/source
review packets. Previous review does not cover this second-cycle PM update.
