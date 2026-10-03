# Programme execution

**Started:** 3 October 2026, Pacific/Auckland. Pete's active goal appoints
GPT/Codex to coordinate Poltika with separate writing, security, testing and
simplification roles. This file records that operating practice and the
current handoff; [PROGRAMME_STATUS.md](../../PROGRAMME_STATUS.md) remains the
task tracker and [BUILD_PLAN_PROGRAMME.md](../../BUILD_PLAN_PROGRAMME.md)
remains the single build order. It does not add a second roadmap.

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

## First work-cycle handoff

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
No PR or migration is marked merged here.

Next startable work is the outstanding #128 independent review and primary
source scoping for the three core main benefits. The next coding slice remains
ADR-0017's shared household model with named WFF/AS mappings and golden parity,
coordinated with existing minimum-semantics owners. Neither income-tax scoping
nor release tags justify building deferred universal registries or AI layers.
