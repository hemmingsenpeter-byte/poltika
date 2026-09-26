# Development doctrine

Poltika follows a source-first, review-driven workflow.

## Principles

- Evidence before implementation
- Vertical slices over broad speculative designs
- Explicit ambiguity handling
- Benchmark and regression protection

## Working agreement (v0.1.5 Task H.2, 25 September 2026)

- Every change reaches `main` through a pull request from a short-lived
  branch. Nobody pushes to `main` directly.
- A pull request merges only when CI is green on its latest commit and its
  review is recorded in the PR (an independent review, or Pete's recorded
  delegation and the author's preflight when the other model is unavailable).
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
- Merge with a merge commit, and tag releases on the merge commit on `main`.
- Review debt is capped (`ROADMAP_REALIGNMENT.md` W1.4, decided 26 September
  2026). When five or more merged implementation PRs await independent
  review (`review_packets/review_queue.md`), no further implementation PR
  merges until the queue is below five. Plan, documentation and
  review-fix PRs are exempt.
- Branch protection is not enforced on this plan (ADR-0007), so this is
  kept by agreement (v0.1.5 decision D3).
