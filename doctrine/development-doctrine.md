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
  (`ROADMAP_REALIGNMENT.md` W1.4, decided 26 September 2026) was suspended
  by Pete on 29 September 2026 ("Ignore PR cap"; `BUILD_PLAN_PROGRAMME.md`
  P17). Every merged implementation PR without an independent review is
  still listed in `review_packets/review_queue.md`, and release gates
  still skip, naming those PRs, until they are reviewed.
- Branch protection is not enforced on this plan (ADR-0007), so this is
  kept by agreement (v0.1.5 decision D3).
