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
`review_packets/review_queue.md` must be cleared first (GPT/Codex for Claude
authorship, Claude for GPT/Codex authorship). Every PR also needs
the author's preflight (`.claude/skills/pr-review-preflight/SKILL.md`) and a
fresh-context `poltika-reviewer` pass on the final head with no unresolved P1 or
P2 finding. A new commit requires a new pass.
Merges are squash merges, on green CI and an up-to-date branch.

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
## Efficient execution

- Keep [the Codex lane ledger](docs/programme/codex_lane_state.md) compact:
  objective, ownership, observed main and relevant heads, completed checks,
  evidence links, remaining gates and next action. Replace stale state instead
  of appending a transcript. The ledger is session memory; GitHub and committed
  review evidence remain authoritative.
- After required initial reads, reuse guidance already read in the session
  while its revision is unchanged. Read changed guidance and newly relevant
  sections when scope changes.
- Use targeted `rg` searches, selected GitHub fields and bounded file excerpts.
  Batch independent reads. Cover the complete review diff in manageable parts;
  keep dependent actions and mutations sequential.
- Bundle nonblocking wording corrections into the existing scoped handoff.
  Create another branch or packet only when it adds review or integration value.
  Before branch modifications, fetch main and check live PR heads and new merges.
  Preserve concurrent ownership and never overwrite another agent's work.
- Run focused verification and every required preflight/CI check. Repeat or
  broaden checks for new changes, failures or unresolved concerns. Simple
  wording fixes need whitespace and relevant link checks, not new tests.
- Delegate bounded independent tasks with explicit scope and file ownership.
  Request concise findings, evidence, exact SHAs and remaining gates; retain
  author versus independent-review provenance.
- Keep progress updates and final handoffs concise: decisions, meaningful
  evidence, blockers and next action. Link durable evidence instead of
  repeating it.

These rules preserve primary-source derivation, protected statutory values,
ambiguity escalation, acceptance authority and required final-head review.
