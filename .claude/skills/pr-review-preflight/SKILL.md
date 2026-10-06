---
name: pr-review-preflight
description: Use before opening, self-reviewing, updating, or recommending acceptance of your own Poltika implementation PR, especially while GPT/Codex is unavailable. Run an adversarial code and evidence preflight, record reproducible findings, and prepare a deferred independent-review handoff. Self-review never substitutes for the rotating reviewer or acceptance under ADR-0020. To review a PR someone else wrote, use pr-review.
---

# PR review preflight

This skill improves Claude Code's own work. It does **not** make the author an
independent reviewer. To review a PR you did not write, use `pr-review`. Follow `BUILD_PLAN.md`'s Roles and Review Doctrine,
`doctrine/review-doctrine.md`, `doctrine/test-doctrine.md`, and
`review_packets/README.md` if they impose a stricter gate.

Acceptance follows ADR-0020: Claude Code accepts Tier A and B work; Pete
decides Tier C. An author's preflight never substitutes for independent
review. Current sequencing follows BUILD_PLAN_PROGRAMME.md (ADR-0021).

## 1. Separate the review from implementation

- Finish the proposed change, then review the exact PR head SHA in a separate
  worktree. Do not edit a checkout another agent is using, and do not review a
  moving or unpublished diff as though it were a fixed artifact.
- If you authored the change, label this pass **author preflight**, not
  independent/fresh-context review. For a stronger check, give a new session or subagent of the
  author's model only `review_packets/TEMPLATE.md`'s mechanical inputs
  (sources, approved spec, base/head diff, tests). Have it record expected
  behavior and findings before showing it your PR explanation. That remains a
  same-model check, not the required cross-model rotation.
  GPT/Codex reviews Claude-authored work; Claude reviews GPT/Codex-authored
  work, as ADR-0020 specifies.
- Do not read an external policy engine's code, tests, or values to derive
  expected behavior. Apply `doctrine/ip-doctrine.md` and the clean-room skill
  before any specifically authorized comparison.

For GPT/Codex-authored PRs touching `policy_specs/`, `engines/simulator/` or a
calculated amount, the single Claude review must be a full `pr-review` pass with
primary-source re-derivation, recorded against the final head.
For mixed authorship, record review coverage by commit; a same-model pass
cannot clear that model's changes. Reconstruction authority: `review_packets/pr170_reconstruction_preflight.md`.

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

## 2. Derive the contract before judging the diff

Read the relevant accepted spec, `policy.yaml`, source map, architecture and
dependency boundaries, and the task's acceptance criteria. For a statutory
claim or protected expected value, check the dated primary NZ source and
official guidance independently; record the URL, version/effective date,
locator, and what it actually supports. Do not promote an assumption into a
verified fact merely because it makes a benchmark pass.

Write a short expected-behavior checklist **before** reading the PR author's
rationale. Include supported inputs, `unsupported`/`needs_review` outcomes,
period and version gates, precision, provenance, and errors. If you already
know the rationale because you authored it, say so in the packet.

## 3. Inspect and probe

Review `git diff --check` and the full base-to-head diff, not just the summary.
Trace every changed input through validation, calculation, response, and
tests. `.claude/skills/pr-review/scripts/pr_triage.sh <PR>` sorts a pushed
PR's files by risk tier, and `pr-review`'s `references/checklist.md` is the
full line-by-line list. At minimum ask:

- Can a missing, contradictory, or unverified fact become `calculated` or
  numeric zero? Can one component's unresolved state contaminate another?
- Are policy ID/version, assessment period, effective intervals, and live
  rate-status checks enforced at the correct boundary? Test both date edges,
  missing parameter IDs, and mismatched policy/version.
- Are fixture values actually supported by their cited source, including
  adjustments stated elsewhere on the same page? Are conditional assumptions
  named and kept distinct from source-stated facts?
- Do tests use the real approved policy where the production gate matters,
  while keeping synthetic fixtures clearly conditional? Would the test fail
  if the alleged bug were reintroduced? Exercise a negative case directly.
- For API changes, test malformed input, exact Decimal transport, status/error
  mapping, internal-detail leakage, and whether packaged/deployed code can
  locate its server-owned policy assets. Never accept a caller-supplied
  policy directory or call a user assertion independently verified evidence.
- For shared helpers, check callers outside the changed module and run
  broader tests proportional to the blast radius.
- Does the change make any statement in `docs/ORIENTATION.md` or CLAUDE.md's
  "v0.1 at a glance" untrue? Update them in the same PR. CI runs the
  orientation examples (`tests/acceptance/test_orientation_examples.py`), but
  nothing checks the prose.

Run and record the actual exit status and output of the relevant commands
(normally `uv run pytest -q`, `uv run ruff check src tests`, and
`uv run mypy --strict src`). A green suite is supporting evidence, not a
substitute for the probes above. Do not claim a check ran if it did not.

## 4. Record findings before fixing

Put findings first, ordered by severity, with file/line, the smallest
reproduction, expected versus actual behavior, and a **proposed** Review
Doctrine classification (`CODE_ERROR`, `TEST_ERROR`, `SPEC_ERROR`,
`SOURCE_CONFLICT`, `INTERPRETATION_AMBIGUITY`, `MISSING_SOURCE`,
`ARCHITECTURE_ISSUE`, or `REVIEWER_ERROR`). Note what was *not* verified.
Use `review_packets/TEMPLATE.md` for the durable record and link it from
the PR. Keep author response below the independently derived section.

Fix confirmed code/test errors in a follow-up commit, add a regression test,
and rerun checks. Re-review the final SHA; do not let a prior green result
stand for a later commit. Escalate source conflicts and genuine policy
ambiguities to Pete with competing readings and evidence; never resolve them
silently or change a protected expected value just to make tests pass.

## 5. Handoff while Codex is unavailable

Keep one compact, auditable PR packet with:

- Base/head SHAs, changed paths, approved spec/source URLs and dated versions.
- Expected behavior, exact commands/results, adversarial probes, findings,
  fix commits, remaining uncertainty, and any Pete decision artifact.
- An explicit label: `author preflight`, `fresh same-model check`, or
  `independent GPT/Codex review`. Never use the last label without that
  actual review; never invent a Codex approval.
- A short **Deferred Codex audit** section listing the exact commits and
  unresolved questions to inspect when Codex returns.

Claude Code accepts Tier A/B under ADR-0020; Pete decides Tier C. If a
build-plan gate requires the other model and that reviewer is unavailable,
leave it pending unless Pete
explicitly authorizes a temporary exception and records its scope. A
same-author or same-model pass may support a *provisional* decision, but it
does not silently close the independent-review gate. Do not change a
policy spec's `status` or protected fixture approval to imply that gate
passed. On Codex's return, present the packet and final SHA before claiming
the PR or task is fully reviewed.
