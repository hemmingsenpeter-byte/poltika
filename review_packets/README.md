# GPT and Claude Code handoffs

GitHub pull requests carry task artifacts between the two models. Pete remains
the v0.1 message bus, acceptance judge, and owner of genuine interpretation
decisions, as specified in `BUILD_PLAN.md`. This process replaces copy-pasting
artifacts, not Pete's approval or the fresh-context review gate.

1. The author makes one task-sized change on a branch or isolated worktree,
   commits it, and opens a PR against `main`. The PR template gives only
   mechanical review inputs: source paths, spec paths, diff, and test output.
   Do not put the author's interpretation or a proposed expected result in
   the reviewer-facing description.
2. Pete asks the other model to review that PR by number or URL. For a policy
   review, the reviewer first derives expected behaviour from primary sources
   and the specification, then compares the diff and tests. The reviewer
   records findings with `review_packets/TEMPLATE.md` or in PR comments before
   reading any implementer explanation.
3. The author responds after the independent pass. Pete classifies and decides
   genuine ambiguities, records any required decision artifact, and accepts
   or rejects the handoff. Only then does the next gated task begin.

Do not have both models edit the same checkout concurrently. A branch/worktree
per active task keeps changes separate. A local unpublished diff can be read
from the same checkout, but a separate worktree or cloud session cannot see it
until the work is committed and shared. Neither `@codex review` nor `@claude`
automation is required for this workflow.
