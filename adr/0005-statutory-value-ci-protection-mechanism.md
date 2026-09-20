# ADR-0005: Statutory-value CI protection mechanism

**Date:** 2026-09-21
**Status:** accepted

## Context

Test Doctrine requires statutory expected values to be CI-protected before
implementation starts, protecting *the intent* — statutory expected values
specifically — not every numeric literal in a test file. CLAUDE.md forbids
changing a statutory expected test value simply to make a test pass.
BUILD_PLAN.md's Task 7/9 split assigns Claude Code the job of determining the
concrete mechanism (Task 7, this ADR) and installing it (Task 9, not done
here).

Two mechanisms were on the table (Test Doctrine's own parenthetical): protected
benchmark/spec fixture files, or explicitly tagged statutory assertions inside
test code (e.g. a custom pytest marker plus a committed value-hash baseline
and a bespoke CI script to check it).

## Decision

**Path-based protection over three specific files per policy, enforced by
required human review, not a bespoke hashing tool.**

Protected files, per policy (`working_for_families`, `accommodation_supplement`):

- `policy_specs/<policy>/benchmarks.yaml` — official published worked-example
  values (already established, Task 5).
- `policy_specs/<policy>/spec_cases.yaml` — hand-calculated spec-test expected
  values (**new**, small addition to Task 5's file list, symmetric with
  `benchmarks.yaml`). Spec tests (Task 13) must load expected values from
  this file, not hardcode them as Python literals.
- `policy_specs/<policy>/policy.yaml` — the whole file is the gate's actual
  enforcement boundary, since GitHub CODEOWNERS cannot target a sub-section
  of a YAML file. The `parameters` block (the statutory rates/thresholds
  themselves, per `SCHEMA.md`'s Task 4 draft) is *why* the file is
  protected, not the enforced scope — see Consequences for the accepted
  coarseness this implies for non-statutory edits.

Mechanism (to be installed in Task 9):

1. A `CODEOWNERS` entry assigning Pete as required reviewer for those three
   path patterns, per policy.
2. Branch protection on `main` requiring that review before merge (a GitHub
   repository setting, not a file — configured separately from this ADR).
3. A lightweight CI check that diffs the protected paths against the PR base
   and surfaces which protected files changed, so a reviewer can't miss it in
   a larger diff — informational/visibility, not a replacement for (1)/(2).
4. Spec and benchmark test *code* (Task 13/14) reads expected values from
   these files at test-collection time; it never duplicates a statutory value
   as an inline Python literal. This is what makes path-based protection
   actually work — the only way to change a protected value is to touch a
   protected file.

Regression-test fixtures (Task 15, frozen dataset snapshots) are a related
but separate case, already covered by the Data Acquisition Doctrine's
immutable-snapshot rule and `data/fixtures/` — not re-litigated by this ADR.

## Rationale

- No bespoke Python/pytest tooling to build and maintain in v0.1 — uses
  native GitHub features only, matching Architecture Doctrine's "minimum
  abstraction" rule.
- Path-based, not literal-based, matches Test Doctrine's own framing:
  protects specific files carrying statutory intent, leaves ordinary
  implementation/test code free to change.
- Human sign-off (Pete, via required review) is the actual enforcement,
  consistent with Review Doctrine's existing pattern of routing
  interpretation/statutory questions to Pete rather than automating a
  judgment call.
- Tagged-assertion hashing was rejected for v0.1: it requires a custom pytest
  plugin and baseline-file tooling before any implementation code exists,
  which is more upfront engineering than the problem currently needs. It
  remains available to reconsider post-v0.1 if path-based protection proves
  too coarse (e.g. if `policy.yaml` grows fields that aren't statutory
  values and the file-level gate starts blocking unrelated changes).

## Consequences

- Task 5's file list gains `spec_cases.yaml` per policy.
- Task 9 becomes concrete: add `CODEOWNERS`, enable branch protection, add
  the CI visibility check — no design work left at that point.
- Task 13 (spec tests) and Task 14 (benchmark tests) must load expected
  values from these files rather than hardcoding them.
- If `policy.yaml`'s schema changes non-statutory fields, that still
  triggers the review gate on the whole file — accepted as a minor coarse-
  ness cost for v0.1, revisit only if it becomes a real friction point.
