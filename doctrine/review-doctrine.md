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
  names the final head, and a P1 or P2 finding blocks the merge until it
  is fixed or answered in the PR.
- A PR touching `policy_specs/`, `engines/simulator/` or any calculated
  amount also needs the independent cross-model review, cleared
  in `review_packets/review_queue.md`, before it merges. GPT/Codex reviews Claude-authored work; Claude reviews
  GPT/Codex-authored work. A Claude reviewer pass can satisfy both gates for
  Codex-authored work if it meets the independent-review standard. A same-model
  pass cannot clear this gate. Any later commit requires a final-head re-review.

For GPT/Codex-authored PRs touching `policy_specs/`, `engines/simulator/` or a
calculated amount, the single Claude review must be a full `pr-review` pass with
primary-source re-derivation, recorded against the final head.
For mixed authorship, record review coverage by commit; a same-model pass
cannot clear that model's changes. Reconstruction authority: `review_packets/pr170_reconstruction_preflight.md`.

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review, except a
mechanical main update as ADR-0020 defines it. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

Interpretation, protected statutory values and anything without a cited
primary source are never accepted under the delegation. They go to Pete
through `PETE_QUEUE.md`.
