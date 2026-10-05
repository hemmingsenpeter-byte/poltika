# Development doctrine

Poltika follows a source-first, review-driven workflow.

## Principles

- Evidence before implementation
- Vertical slices over broad speculative designs
- Explicit ambiguity handling
- Benchmark and regression protection

## High-throughput build mode ("monkey with a hammer")

Poltika deliberately optimises for useful functional coverage before internal
polish while the system is still being built out. The aim is to exploit AI
coding capacity to get the major executable skeleton in place quickly, learn
from integration, and refine what proves important rather than perfecting
modules in isolation.

This mode relaxes build order and internal polish only. It does not relax the
protected expected values and `doctrine/test-doctrine.md`, the ADR-0020 Tier C
items, or the independent cross-model review rotation and the review queue.

The operating rules are:

- **Breadth before elegance.** Where dependencies allow, build working vertical
  slices across the active programme instead of polishing one subsystem to its
  theoretical endpoint before the next begins.
- **Front-load implementation, defer non-blocking polish.** Refactors,
  micro-optimisation, documentation polish, UI polish and speculative
  abstractions may wait when they do not affect correctness, integration or an
  acceptance gate.
- **Ugly internals are acceptable; bad contracts are not.** Provisional code may
  sit behind stable typed interfaces. Shared schemas, identifiers, quantity
  semantics and public contracts are treated as architecture, not disposable
  implementation detail.
- **Tests before polish.** Every bounded increment needs enough deterministic,
  regression and integration protection to make rapid AI-generated iteration
  safe. Test debt that could permit silent numerical or semantic regression is
  blocking debt, not deferred polish.
- **No shortcuts on truth.** Statutory values, legal interpretation, source
  provenance, evidence classes, reproducibility, uncertainty semantics and
  protected expected values remain subject to their existing gates. Speed never
  promotes an Assumption to a Fact or lets an LLM substitute for calculation.
- **Parallelise by default.** Independent bounded modules should be assigned to
  separate workers/worktrees when their contracts are sufficiently clear.
  Serial execution is reserved for genuine dependency chains and shared-state
  integration.
- **Make technical debt explicit.** Provisional implementations, known
  limitations and deferred cleanup must be machine-visible in code, a tracked
  task, review record or decision log. Silent debt is not acceptable.
- **Refactor at real integration boundaries.** Prefer abstractions justified by
  two or more actual consumers over abstractions invented for hypothetical
  future needs.
- **Prefer bounded replacement over prolonged repair.** If an AI-built module is
  locally poor but well-contained, rewriting the module can be cheaper and safer
  than preserving a bad internal design. Its external contract and tests remain
  the continuity boundary.
- **Ship runnable vertical slices regularly.** A working end-to-end capability
  that can be exercised and criticised is more valuable than a pristine but
  isolated subsystem.
- **Architecture is the guardrail.** High-throughput mode operates inside the
  epistemic constitution, source-first policy workflow, deterministic statutory
  kernel, common schemas and review doctrine. It accelerates construction; it
  does not waive those constraints.
- **Escalate genuine ambiguity instead of guessing.** If speed encounters an
  unresolved legal, evidential or policy-definition question, preserve the
  unknown explicitly and route the decision through the existing authority
  process.

This mode should be used most aggressively while building broad system
capability (especially the executable foundations and deterministic/model
infrastructure). Refinement becomes stricter as a component becomes shared,
externally relied upon, release-critical or evidentially consequential.

## Working agreement (v0.1.5 Task H.2, 25 September 2026)

- Every change reaches `main` through a pull request from a short-lived
  branch. Nobody pushes to `main` directly.
- A pull request merges only when CI is green on its latest commit and its
  review is recorded in the PR (an independent review, or Pete's recorded
  delegation and the author's preflight when the other model is unavailable).
  Since 2 October 2026 acceptance follows ADR-0020's tiers and merge rules.
- One bounded task per pull request, one commit per logical change. For a
  policy domain, "bounded" means the five-PR structure in
  `.claude/skills/new-policy/SKILL.md`: one PR per kind of review
  (sources and specification, values and expected results,
  implementation, interactions, release), not one PR per plan task.
- Review findings on an open pull request are fixed in that pull request
  before it merges. A new pull request is only for a finding against
  merged work.
- Review depth follows risk. Interpretation, protected statutory values
  and engine, loader or graph code get a full independent review.
  Tests-only, documentation-only and generated-file changes get a light
  independent check that the scope matches its label.
- Squash merge (ADR-0020; a merge commit until 2 October 2026), and tag
  releases on the resulting commit on `main`. Tagging stays Pete's.
- Review debt is recorded but not capped. The cap of five
  (historical `ROADMAP_REALIGNMENT.md` W1.4, decided 26 September 2026) was suspended
  by Pete on 29 September 2026 ("Ignore PR cap"; `BUILD_PLAN_PROGRAMME.md`
  retained decision P17). Every merged implementation PR without an independent review is
  still listed in `review_packets/review_queue.md`, and release gates
  still skip, naming those PRs, until they are reviewed.
- Main now has the active ADR-0020 ruleset: nine required checks, strict
  up-to-date branches, squash-only PR merges and no bypass actors. The
  deliberate failing-check probe #168 was blocked (see the dated evidence
  in `docs/programme/2026-10-05-main-ruleset-probe.md`). ADR-0007 records the
  earlier platform limitation; independent review remains a substantive gate.

## Current sequencing (ADR-0021)

`BUILD_PLAN_PROGRAMME.md` is the single current build order. The household
and statutory-maintenance lanes supply detail. The frozen BUILD_PLAN.md
retains substantive source/IP/data/test/review constraints and historical
anchors; archived planning never determines the next implementation task.
ADR-0021 changes execution order, not the five-PR onboarding workflow, review
rotation, protected-value process, independent-review debt or acceptance tiers.
