# Claude Code Instructions — Poltika

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

## Start here

1. Check the repository state before relying on anything you read. Several
   sessions often work in this repository at once, and `main` can move
   during a session:

   ```sh
   git status -sb && git log --oneline -5 origin/main && git worktree list
   ```

   Make changes in your own worktree off `origin/main`, never in the shared
   checkout another session may be using:
   `git worktree add -b <branch> /private/tmp/poltika-<name> origin/main`.
2. Read [docs/ORIENTATION.md](docs/ORIENTATION.md): what Poltika does now, on
   one page, with runnable examples.

## v0.1 at a glance

- WFF 2026-27 (FTC, IWTC, MFTC, Best Start; annual) and the Accommodation
  Supplement (weekly), separately or for one household.
- Every component is `calculated`, `unsupported` or `needs_review`.
  `unsupported` outranks `needs_review`. A missing fact is never zero.
- IWTC is always `needs_review` (`in_work_base` is gated), so there is never a WFF total.
- Inputs are caller-asserted statuses (`verified`/`excluded`/`unknown`). There is no
  date of birth, age, child ID, hours or address, and the API rejects unknown fields.
- WFF covers whole years only: part-year children, relationship changes and
  shared care are `unsupported`.
- MFTC needs an attested after-tax income. There is no income tax module.
- AS is per assessment week: one area, cost and income, rounded up once at the end.
- WFF and AS results are never added together.
- Results also carry a reason code, missing facts and calculation steps, and the
  API adds explanations (v0.1.5). No amount changed.
- WFF runs on policy `0.1.0`; AS on `0.1.1` with an explicit 7-day week.

## What to read, by task

| Task | Read |
| --- | --- |
| Running scenarios or answering questions about v0.1 | `docs/ORIENTATION.md` and `docs/demo/v0_1/` |
| Planning, sequencing or starting new work | `BUILD_PLAN_PROGRAMME.md` (ADR-0021: the single current master build order, capability gates A–P), then `PROGRAMME_STATUS.md` and the relevant active detailed lane |
| Checking or explaining a result | Also the policy's `specification.md` calculation sequence and `decisions/` |
| Changing policy logic, statutory values, code or repository structure | Everything under "Before making changes" below |
| Opening or reviewing a PR | The "Review" section below |

## Before making changes

Read:

- BUILD_PLAN_PROGRAMME.md and the relevant active detailed lane
- BUILD_PLAN.md — historical v0.1 record; retained substantive doctrine and anchors
- ARCHITECTURE.md
- REPOSITORY_STRUCTURE.md — before creating any new production file, module, or directory; a proposed component with no obvious location means updating that file deliberately, not creating an ad-hoc directory
- doctrine/epistemic-constitution.md
- relevant files under doctrine/
- relevant policy specification under policy_specs/

## Ground truth

Policy rules must be derived from cited primary NZ sources.

Never use model memory as authority for:
- statutory rates
- thresholds
- eligibility rules
- abatement rules
- effective dates
- policy interactions

If the source is missing or ambiguous, stop and flag it.

Every claim carries one of the eight evidence classes in
`doctrine/epistemic-constitution.md` (approved 2 October 2026). Validation
expectations retain Decision 1's temporary exception: their classification
is deferred to Phase C validation (old Step 6; the accepted exception is unchanged). An AI-authored claim is an AI hypothesis until its
promotion gate passes. The constitution adds to the ground-truth rules above
and replaces none of them.
A caller's assertion stays a Scenario, an explicit Assumption stays an
Assumption, and a calculated result stays a Model output. None of them is
treated as an independently verified Fact or Rule.

## Implementation

Follow the vertical-slice approach in doctrine/development-doctrine.md and
the single current BUILD_PLAN_PROGRAMME.md. Preserve the frozen constraints
in BUILD_PLAN.md until they are deliberately extracted.

Active lanes are BUILD_PLAN_v0_3.md (household economic kernel) and
BUILD_PLAN_v0_1_6.md (statutory maintenance). BUILD_PLAN_v0_2.md is release
closeout support. Archived plans never determine new work.

Do not:
- introduce speculative abstractions
- redesign the architecture without explicit approval
- change statutory expected test values simply to make tests pass
- silently resolve policy interpretation ambiguity

## Tests

Maintain the three test classes:

1. Spec
2. Benchmark
3. Regression

Protected statutory expected values require the process defined in doctrine/test-doctrine.md.

## Review

Use the discrepancy taxonomy in doctrine/review-doctrine.md.

Before publishing or recommending acceptance of an implementation PR, use
`.claude/skills/pr-review-preflight/SKILL.md`. An author preflight is not the
independent reviewer rotation in doctrine/review-doctrine.md and the
historical BUILD_PLAN.md Roles. Acceptance follows ADR-0020.

To review a PR you did not write (a Codex PR, a review-queue row, a
re-review after new commits), use `.claude/skills/pr-review/SKILL.md`.

Interpretation ambiguity must be escalated rather than silently resolved.

## Delegated acceptance (ADR-0020)

Pete delegated acceptance on 2 October 2026 (`adr/0020-delegated-acceptance.md`).
Claude Code may merge Tier A work (engineering, tooling, CI, structure,
schemas within the target architecture, tests, docs, refactors that change no
calculated amount, P10 and P19) and decide Tier B choices (reversible, left
open by the plans, no doctrine naming Pete), logging each in
`docs/decision_log.md`. Tier C never is decided here: unsourced statutory
values or interpretations, protected expected values, P6, P7, P8, P13, P14,
P18, P20, Māori data governance, IDI access, anything public, licensing, IP,
paid or external resources, release tags, and deleting data or history.
Park each in `PETE_QUEUE.md` and route around it.

A PR merges (`gh pr merge --squash --auto`) only when CI is green, the branch
is up to date, `pr-review-preflight` has run and a `poltika-reviewer` pass
has no unresolved P1 or P2 finding. A PR touching `policy_specs/`,
`engines/simulator/` or any calculated amount also waits for its independent review
row in `review_packets/review_queue.md` to clear: GPT/Codex reviews Claude
authorship, and Claude reviews GPT/Codex authorship. Every
preflight and reviewer pass names the final head; new commits require re-review. Never use `--admin` or
bypass a check. `PROGRAMME_STATUS.md` tracks every current capability task and its evidence.

For GPT/Codex-authored PRs touching `policy_specs/`, `engines/simulator/` or a
calculated amount, the single Claude review must be a full `pr-review` pass with
primary-source re-derivation, recorded against the final head.
For mixed authorship, record review coverage by commit; a same-model pass
cannot clear that model's changes. Reconstruction authority: [6 October reconstruction authority](review_packets/pr170_reconstruction_preflight.md).

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review, except a
mechanical main update as ADR-0020 defines it. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

## External prior art

Follow doctrine/ip-doctrine.md.

OpenFisca or other external implementations must not be used as the source for Poltika policy logic.

## GitHub and Render

The repository remote is `https://github.com/hemmingsenpeter-byte/poltika.git` on branch `main`.

Use the Render MCP server for Render workspace, service, deploy, log, metric, and database operations. Confirm the target Render workspace before creating or changing resources.
