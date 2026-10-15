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
2. The author's `pr-review-preflight` has run on the final head, or on the
   reviewed head when the only later change is a mechanical main update.
3. A fresh-context `poltika-reviewer` pass on the final head (or on the
   reviewed head, under a mechanical main update) has left no unresolved P1
   or P2 finding.
4. If it touches `policy_specs/`, `engines/simulator/` or any calculated
   amount, its independent cross-model review row in
   `review_packets/review_queue.md` is cleared. GPT/Codex reviews Claude-authored
   changes; Claude reviews GPT/Codex-authored changes. The PR is queued and
   waits; other work continues.

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review, except a
mechanical main update as defined below. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

**Mechanical main update (Pete, 6 October 2026).** Updating a PR from `main`
is mechanical when the merge has no conflict and the PR's own diff
(`git diff <new main>...HEAD`) is identical to the reviewed diff (the same
`git patch-id --stable`). It needs green required CI on the new head and a
delta check recorded in the PR naming the reviewed head, the new head and the
`main` SHA (`pr-review` step 8). It does not renew the author preflight or the
independent review, and the merge commit is not a semantic change by whoever
made it. A conflict resolution, or any change to the PR's own diff, is a fix
and renews every gate.

**Append-only record conflicts (Pete, 16 October 2026; decision log D43).**
A main update whose only conflicts are in append-only records
(`CHANGELOG.md`, `changelog.d/`, `docs/decision_log.md`,
`review_packets/review_queue.md`, `PROGRAMME_STATUS.md`, `PETE_QUEUE.md`)
is also mechanical when the resolution keeps every line of both sides and
changes nothing else. Two checks show it: `git diff <reviewed head> <new head>
-- <record>` and `git diff <new main> <new head> -- <record>` remove no line,
and the PR's diff over every other path has the same `git patch-id --stable`
as the reviewed diff. The delta check records both, with the reviewed head,
the new head and the `main` SHA. A resolution that drops, merges or rewrites
a line, such as two edits to one queue row, is a fix and renews review.

For GPT/Codex-authored policy/calculation work, a Claude `poltika-reviewer`
pass may meet both reviewer gates only as a full `pr-review` with independent
primary-source re-derivation. Mixed authorship retains commit-specific
coverage; a same-model pass does not clear that model's semantic changes.

`--admin`, bypassed checks and rewriting `main` are never used. If `main`
regresses, a revert PR is opened at once.

### The ruleset on `main` (active since 5 October 2026)

Ruleset id 24478578 requires up-to-date branches, squash PR merges and nine
checks: `test`, `pilot-image`, `check-protected-paths`,
`check-immutable-snapshots`, `source-currency`, `pip-audit`, `links`,
`Bandit (python)` and `zizmor (actions)`. There are no bypass actors,
required GitHub approvals, force pushes or deletions on main.

The [negative probe #168](https://github.com/hemmingsenpeter-byte/poltika/pull/168)
observed GitHub's BLOCKED state with the required test failing and the other
eight required checks passing. This was no merge or bypass attempt.
ADR-0007's earlier platform limitation is historical. The statutory-value
guard reports changed protected files and must complete successfully;
it does not approve values. Source currency now runs on PRs; its issue
publication remains scheduled only.

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
- Same-model review supports assurance but cannot clear cross-model review.
  Reviewer identity follows semantic authorship, and clearance covers only
  the recorded final head. Author preflight never substitutes for it.
- Every Tier B choice is reversible and logged, so Pete can overturn one
  without archaeology.
- Pete can narrow or withdraw this delegation at any time, by editing this
  ADR or telling a session. A session that finds this ADR superseded falls
  back to `BUILD_PLAN.md`'s Roles.

## Review amendment reconstructed, 6 October 2026

Pete's Codex-lane instruction commissions a clean reconstruction of #170's
remaining semantic delta on current main. It requires other-model review,
separate author preflight and final-head clearance after any later change.
This amendment leaves all Tier A/B/C authorities, primary-source rules,
protected statutory-value and interpretation gates unchanged. Claude Code
owns final independent review and integration of this reconstruction.
The [author packet](../review_packets/pr170_reconstruction_preflight.md)
enumerates the old changes and their dispositions.

On 6 October 2026 Pete chose the mechanical-main-update exemption above, after
the independent review of this reconstruction found that renewing preflight
and cross-model review on every conflict-free update would stop the merge
train it governs. Claude Code added that exemption as a labelled commit.
