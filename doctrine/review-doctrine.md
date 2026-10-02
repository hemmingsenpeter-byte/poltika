# Review doctrine

All interpretation decisions must be reviewable.

## Required evidence

- cited source references
- rationale for the interpretation
- owner of the decision
- date of decision
- any unresolved ambiguity

## Review standard

Ambiguity is escalated, not silently resolved.

## Acceptance (ADR-0020)

Pete delegated acceptance of engineering work to Claude Code on 2 October
2026 (`adr/0020-delegated-acceptance.md`). The rotation still holds:

- The author runs `pr-review-preflight`.
- A `poltika-reviewer` subagent reviews the diff with a fresh context. It
  is a same-model check, and a P1 or P2 finding blocks the merge until it
  is fixed or answered in the PR.
- A PR touching `policy_specs/`, `engines/simulator/` or any calculated
  amount also needs the independent cross-model (GPT/Codex) review, cleared
  in `review_packets/review_queue.md`, before it merges.

Interpretation, protected statutory values and anything without a cited
primary source are never accepted under the delegation. They go to Pete
through `PETE_QUEUE.md`.
