# Claude Code Instructions — Poltika

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
| Planning, sequencing or starting new work | `BUILD_PLAN_PROGRAMME.md` (ADR-0018: the master build order of 33 steps in eight phases, and what exists against each step), then the step's own plan |
| Checking or explaining a result | Also the policy's `specification.md` calculation sequence and `decisions/` |
| Changing policy logic, statutory values, code or repository structure | Everything under "Before making changes" below |
| Opening or reviewing a PR | The "Review" section below |

## Before making changes

Read:

- BUILD_PLAN.md
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

`doctrine/epistemic-constitution.md` is a proposed classification framework,
awaiting Pete's approval and the decisions it marks "For Pete". Read it as
a draft; it does not change the ground-truth rules above or require caller
Scenarios, explicit Assumptions or calculated Model outputs to be treated
as independently verified Facts or Rules.

## Implementation

Follow the vertical-slice approach defined in BUILD_PLAN.md.

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
independent reviewer rotation required by BUILD_PLAN.md.

To review a PR you did not write (a Codex PR, a review-queue row, a
re-review after new commits), use `.claude/skills/pr-review/SKILL.md`.

Interpretation ambiguity must be escalated rather than silently resolved.

## External prior art

Follow doctrine/ip-doctrine.md.

OpenFisca or other external implementations must not be used as the source for Poltika policy logic.
