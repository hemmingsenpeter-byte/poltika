# ADR-0020: Delegated acceptance

**Date:** 2 October 2026
**Status:** accepted. Pete granted this authority on 2 October 2026, in the
goal that set Claude Code (Opus) as the programme's software project
manager. Drafted by Claude Code under that authority.

## Context

Pete has been the acceptance judge for every PR (`BUILD_PLAN.md`, Roles)
and the merge step for most of them. `BUILD_PLAN_PROGRAMME.md` ("How to
read this plan") names his review and decision time as what sets the
programme's pace. Most of what waits on him is engineering: tooling, CI,
schemas, tests, refactors and docs. Those are reversible, and the
repository's doctrine and checks constrain them already.

The rules that protect what Poltika claims are a different kind of thing:
cited primary sources, protected statutory values, escalated
interpretation, Māori data governance, and anything public. They stay
with Pete.

## Decision

Claude Code, acting as the programme's software project manager (an Opus
orchestrator), may accept and merge work in three tiers. Sonnet subagents
implement (`poltika-worker`) and review (`poltika-reviewer`), each in its
own worktree off `origin/main`.

### Tier A: decide and merge

- Engineering, tooling, CI, repository structure and test infrastructure.
- Schemas and contracts within the target architecture (`ARCHITECTURE.md`,
  `REPOSITORY_STRUCTURE.md`).
- Documentation, and refactors that change no calculated amount.
- The technical programme decisions P10 (the batch engine) and P19 (the
  scope of state schema v0).

### Tier B: decide, record and keep moving

Any reversible choice the plans leave open where no doctrine names Pete,
including the detailed plans for Steps 3 onward. Each is logged in
`docs/decision_log.md` with the options, the rationale and how to reverse
it.

### Tier C: never decided by Claude Code

Each is parked in `PETE_QUEUE.md` with the smallest action Pete needs to
take, and the work routes around it:

- any statutory rate, threshold, eligibility or abatement rule, effective
  date or interpretation without a cited NZ primary source;
- changes to protected statutory expected values (`doctrine/test-doctrine.md`);
- programme decisions P6, P7, P8, P13, P14, P18 and P20;
- Māori data governance (Task 1.4), and IDI or microdata access;
- making anything public, licensing or IP;
- creating or paying for Render or other external resources;
- tagging releases;
- deleting data or history.

Tier C overrides A and B. The ground-truth rule in `CLAUDE.md` is not
delegated: no tier lets a model's memory stand as a source.

### Merge rules

A PR merges, with `gh pr merge --squash --auto`, when all of these hold:

1. CI is green on its latest commit, and the branch is up to date with
   `origin/main`.
2. The author's `pr-review-preflight` has run on the final head.
3. A fresh-context `poltika-reviewer` pass on the final head has left no
   unresolved P1 or P2 finding. A later fix or merge of main requires a new
   pass; the review records its exact commit.
4. If it touches `policy_specs/`, `engines/simulator/` or any calculated
   amount, its independent cross-model review row in
   `review_packets/review_queue.md` is cleared. GPT/Codex reviews Claude-authored
   work; Claude reviews GPT/Codex-authored work. The PR is queued and waits;
   other work continues.

`--admin`, bypassed checks and rewriting `main` are never used. If `main`
regresses, a revert PR is opened at once.

### The ruleset on `main` (the target)

- Required status checks: every existing CI workflow (tests, the
  statutory-value guard, the data-snapshot guard, source currency) and
  every CI job added later.
- Branches up to date before merging.
- Squash merges only; auto-merge on; branches deleted on merge.
- Zero required approvals; no force pushes and no deletions.

Changing repository settings was outside what this session could do, so
the ruleset is in `PETE_QUEUE.md` as a one-command action. Until it is
active, the merge rules above are kept by agreement, as the working
agreement already is (`doctrine/development-doctrine.md`).

ADR-0007 found that required checks needed GitHub Pro on this private
repository, and made the statutory-value guard visibility only. On 2
October 2026 the API returned a branch-protection object for `main`, so
the plan now appears to allow it. If GitHub still refuses the ruleset,
ADR-0007 stands, Q1 closes as not possible, and the merge rules stay by
agreement. Once the ruleset is active, it supersedes ADR-0007's
"visibility only" for the checks it requires: the guard still warns rather
than fails, but it must run.

Source currency runs weekly, not on pull requests, so it cannot yet be a
required check. It becomes one when a pull-request trigger is added (a
report only; its issue step stays on the schedule).

### What changes elsewhere

- `CLAUDE.md` and `AGENTS.md`: the tiers, the merge rules and the three
  tracking files.
- `doctrine/review-doctrine.md`: delegated acceptance and the reviewer
  rotation.
- `doctrine/development-doctrine.md`: squash merges, and acceptance under
  this ADR.
- `BUILD_PLAN.md`: a note on the frozen Roles section that acceptance is
  delegated under this ADR.

### Tracking

- `PROGRAMME_STATUS.md` (added in the PR after this one): every step and
  task, with status, owner, PR and blocker.
- `docs/decision_log.md`: every Tier A and B decision.
- `PETE_QUEUE.md`: the open Tier C items.

Pete receives one short digest at the end of each session: the PRs
merged, the decisions made, the open Tier C items and what comes next.

## Consequences

- Engineering work no longer waits on Pete's review. His time goes to Tier
  C: sources, interpretation, governance and anything public.
- A reviewer of the author's model is a same-model check and cannot clear
  a cross-model review row. Claude's fresh-context `poltika-reviewer` can
  supply both the reviewer pass and the independent cross-model review
  for GPT/Codex-authored work, when its packet independently derives the
  contract and records the final head. Claude-authored high-risk work
  still waits for independent GPT/Codex review.
- Every Tier B choice is reversible and logged, so Pete can overturn one
  without archaeology.
- Pete can narrow or withdraw this delegation at any time, by editing this
  ADR or telling a session. A session that finds this ADR superseded falls
  back to `BUILD_PLAN.md`'s Roles.

## Amendment approved by Pete, 5 October 2026

Pete instructed this closeout session to accept the best options in the
supplied decisions. Item 4 explicitly chooses BUILD_PLAN's reviewer rotation:
use whichever model did not author the PR. Rule 4's original GPT/Codex naming
assumed Claude authorship; it never authorised same-model clearance. The
amendment changes the reviewer identity, not review depth or protected gates.

For this bounded closeout, Pete also explicitly authorised Codex to accept,
commit, push and merge the prepared work in order once the gates pass. This
is session authority, not a permanent transfer of all Tier C decisions. It
includes the named v0.2 tag correction and the supplied scope/governance choices;
new unsourced interpretations, protected statutory values, public release,
microdata/governance access and paid resources retain their existing gates.

The project-permission settings are prepared separately for Pete's explicit
approval of their command and branch scope. Existing per-command permissions
remain in use meanwhile. Tool capabilities do not waive the merge rules or
authorise private-repository export to another model provider. Such export
needs explicit destination and scope authorization from Pete.
