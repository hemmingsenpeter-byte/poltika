# ADR-0004: Acknowledged sequencing deviation for the comparative external-project review

**Date:** 2026-09-21
**Status:** accepted

## Context

BUILD_PLAN.md's IP Doctrine permits exactly two external-inspection
touchpoints: a narrow, structural-only glance during Week 0 schema design
(Task 3, after Task 2's independent mapping), and a coverage-gap check
strictly after each vertical slice's own test suite is complete (Task 16).

Two research documents were produced on 2026-09-21:

- `docs/research/task_3_structural_glance.md` — the Task 3 exercise itself,
  within its narrow pre-suite exception (schema shape only, no values).
- `docs/research/nz_policy_engines_review.md` — a broader clean-room
  comparative review of OpenFisca Aotearoa **and** PolicyEngine New Zealand
  (`PolicyEngine/policyengine-nz`, a second external project not previously
  named in Poltika's doctrine), assessing licensing, architectural lessons,
  and potential gaps against Poltika's own documented architecture.

The second document does not fit either doctrine window: it ran before the
WFF test suite exists, so it is not Task 16, and it goes well beyond schema
shape, so it is not Task 3. It was performed at Pete's explicit request,
using the same two-stage clean-room method (structural/conceptual
observation only, no code/value/test copying, independent synthesis against
Poltika's own architecture) described in `.claude/skills/clean-room-research/SKILL.md`.

## Decision

This is an acknowledged, deliberate, one-off deviation from the IP
Doctrine's default Task-16 timing — not a doctrine change, and not a
precedent that external-project research may happen whenever convenient.
The review is accepted as valid evidence on the basis that:

- it was explicitly requested by Pete (scope owner), not initiated
  unprompted;
- it followed the same clean-room discipline the doctrine already requires
  (structural/conceptual only; no external values, formulas, code, or test
  content recorded as Poltika fact; independent synthesis against Poltika's
  own architecture, not the external projects' structure);
- its own findings do not propose any change to the frozen Development,
  Architecture, Scope, Test, Review, or Data Acquisition doctrines, and
  explicitly defer schema-affecting observations (the person/assessment-unit
  entity distinction, G1) to Task 4 as an existing task, not a new one;
- it corrects and logs its own methodology error in place (an initial,
  incorrect "no NZ PolicyEngine package exists" conclusion, later verified
  and corrected against a URL Pete supplied directly), rather than silently
  fixing it.

Task 16, when it is actually performed for WFF and then AS, must still
independently include both OpenFisca Aotearoa and PolicyEngine NZ as
comparators — this review does not substitute for that later, narrower,
post-suite check.

## Consequences

- Pete/GPT retain the authority to request bounded external research outside
  the doctrine's default windows; each instance should be logged this way
  (a dated ADR, not a silent action) rather than assumed to need no record.
- `PolicyEngine/policyengine-nz` is now a named comparator alongside
  OpenFisca Aotearoa for Task 16's coverage-gap check, and both are
  confirmed AGPL-3.0 (network copyleft) — reference/pattern-review only,
  never a code or value dependency, per ADR-0001 and doctrine/ip-doctrine.md.
- No BUILD_PLAN.md task list change is required by this ADR; the review's
  own "Proposed build-plan notes" are left for Pete/GPT to decide on
  separately and are not applied here.
