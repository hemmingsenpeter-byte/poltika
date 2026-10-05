# Agent Instructions - Poltika

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

## Start here

Read `docs/ORIENTATION.md`, then `BUILD_PLAN_PROGRAMME.md` for planning,
sequencing and new implementation work (ADR-0021). It is the single active
master build order. Read `PROGRAMME_STATUS.md` and the relevant active detailed
lane: `BUILD_PLAN_v0_3.md` for household economic modelling or
`BUILD_PLAN_v0_1_6.md` for statutory maintenance. `BUILD_PLAN_v0_2.md` supports
release completion only. Historical plans and `docs/archive/` never determine
the next task.

## Before making changes

Read:

- BUILD_PLAN_PROGRAMME.md and the relevant active detailed lane
- BUILD_PLAN.md — historical v0.1 record; retained substantive doctrine and anchors
- ARCHITECTURE.md
- REPOSITORY_STRUCTURE.md - before creating any new production file, module, or directory; a proposed component with no obvious location means updating that file deliberately, not creating an ad-hoc directory
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

## Implementation

Follow the vertical-slice approach in doctrine/development-doctrine.md and
the single current BUILD_PLAN_PROGRAMME.md. Preserve the frozen constraints
in BUILD_PLAN.md until they are deliberately extracted.

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

Interpretation ambiguity must be escalated rather than silently resolved.

## Delegated acceptance (ADR-0020)

Since 2 October 2026 Claude Code accepts and merges engineering work under
three tiers (`adr/0020-delegated-acceptance.md`). Sources, interpretation,
protected statutory values, Māori data governance and anything public stay
with Pete (Tier C, listed in `PETE_QUEUE.md`). An independent cross-model
review is still required before a PR touching `policy_specs/`,
`engines/simulator/` or any calculated amount merges: its row in
`review_packets/review_queue.md` must be cleared first (GPT/Codex for Claude authorship, Claude for GPT/Codex
authorship). Every PR also needs
the author's preflight (`.claude/skills/pr-review-preflight/SKILL.md`) and a
fresh-context `poltika-reviewer` pass on the final head with no unresolved P1 or
P2 finding. A new commit requires a new pass.
Merges are squash merges, on green CI and an up-to-date branch.

## External prior art

Follow doctrine/ip-doctrine.md.

OpenFisca or other external implementations must not be used as the source for Poltika policy logic.

## GitHub and Render

The repository remote is `https://github.com/hemmingsenpeter-byte/poltika.git` on branch `main`.

Use the Render MCP server for Render workspace, service, deploy, log, metric, and database operations. Confirm the target Render workspace before creating or changing resources.
