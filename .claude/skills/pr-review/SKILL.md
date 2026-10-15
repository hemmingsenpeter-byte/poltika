---
name: pr-review
description: Use whenever asked to review, check, look over, give feedback on, re-review or clear a Poltika pull request you did not write in this session. That includes a PR number or URL, a Codex/GPT-authored PR, a row in review_packets/review_queue.md, new commits pushed after an earlier review, and whether a PR is ready to merge. Runs a professional reviewer's pass. It pins the exact head SHA and triages CI, scope and risk. It derives expected behaviour before reading the author's rationale, reads the whole diff and reproduces every suspected defect before reporting it. Findings are graded (P1-P3, nit, question, escalation) and classified under the Review Doctrine. The output is inline comments and one summary with a clear verdict, posted as a comment and never as an approval or merge; acceptance follows ADR-0020. To check your own change before opening or updating it, use pr-review-preflight instead.
---

# PR review

You are the reviewer in `BUILD_PLAN.md`'s rotation. A review finds the
defects that matter before they merge, proves each one, and gives the
accepting party what's needed to decide without redoing your work. Review
is distinct from acceptance: Claude Code accepts Tier A/B under ADR-0020;
Pete decides Tier C, including interpretation ambiguity.

Review the way a careful senior engineer reviews a colleague's PR.
Understand what the change is for before judging how it does it. Read all
of it, run it and try to break it. Then say plainly what must change,
what could, and what you didn't check.

The order below matters. The contract comes before the diff so the
author's framing can't anchor you. Reproduction comes before writing so
you never post a guess as a fact.

Acceptance follows ADR-0020: Claude Code accepts Tier A and B work; Pete
decides Tier C. An author's preflight never substitutes for independent
review. Current sequencing follows BUILD_PLAN_PROGRAMME.md (ADR-0021).

## 1. Pin the target and label the pass

From the repo root, run:

```sh
.claude/skills/pr-review/scripts/pr_triage.sh <PR number> [base branch, default main]
```

It fetches the head and prints the SHAs and the fork point (for a merged
PR, the base it merged into). It also shows the commits with their
authorship trailers, the changed files by risk tier, what the statutory
value and snapshot guards will say, the diff size and the review-queue
count. Then read the PR with `mcp__github__pull_request_read`: `get` for
its state, `base.sha` and the template's Handoff and Reviewer inputs
(leave any explanation below them until step 6), then `get_check_runs`,
`get_reviews`, `get_review_comments` and `get_comments`. A local session
with `gh` can use `gh pr view`, `gh pr checks` and `gh api` instead.

Check the head out in its own worktree so you never disturb a checkout
another session is using. Use CLAUDE.md's `/private/tmp/poltika-<name>`
convention, or your scratchpad in a cloud session:
`git worktree add --detach <dir>/pr-<N> <head SHA>`.

Your verdict covers one SHA. If the head moves mid-review, either finish
and say which SHA you reviewed, or restart on the new one.

Decide the label now and use it in everything you write. Pete relies on
it to know which gate a review can close.

| Who wrote the PR | Your pass is | Closes the independent-review gate |
| --- | --- | --- |
| GPT/Codex | Independent cross-model review (Claude Code) | Yes for that author's work, on the final head. For `policy_specs/`, `engines/simulator/` or a calculated amount, only as a full `pr-review` with primary-source re-derivation. Acceptance then follows ADR-0020's merge rules |
| Claude Code, another session | Fresh same-model check | No. Say so, as `reviews/2026-09-27-v0-2-fresh-same-model-check.md` does |
| Claude Code, this session | Author preflight: stop and use `pr-review-preflight` | No |
| Mixed (e.g. Codex fixes on a Claude PR) | Split by commit: cross-model for the other model's commits, same-model for the rest | Only for the other model's commits |

Work out authorship from the PR body's Handoff section and the commit
trailers the triage script shows. Claude Code commits carry
`Co-Authored-By: Claude`. Every PR is opened from Pete's GitHub account
and both models' commits can carry the same git author name, so neither
tells you who wrote it.

Record whether you saw the author's rationale (PR body, commit messages)
before deriving expectations. If you did, the review is "not blind"; say
so, as `reviews/2026-09-27-pr117.md` does. Being honest about it is worth
more than looking blind.

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review, except a
mechanical main update as ADR-0020 defines it. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

## 2. Triage before reading code

Take a few minutes to decide how deep the review goes and whether it can
go ahead at all.

- **Depth follows risk** (`doctrine/development-doctrine.md`). Interpretation
  files, protected statutory values and code under `src/poltika/` get a
  full review, deepest for engine, loader, data-boundary and graph code.
  Tests-only, documentation-only and generated-file changes get a light
  check: confirm the scope matches the label. A "tests-only" PR that adds
  statutory expected values still gets the value check in step 3.
- **CI on the head SHA.** If this PR turned it red, that is a P1 and the
  verdict can't be "ready". Keep reviewing so the author gets everything
  in one round. If it's red for a reason outside the PR, note it and
  don't blame the author. The Statutory Value Guard never goes red, so
  read its summary or the triage script's list.
- **Scope.** A PR should be one bounded task (for policy work, the
  `new-policy` skill's five-PR structure). If unrelated changes are
  bundled in, say so and ask for a split rather than silently reviewing
  around them. If the non-generated diff is too big to read properly in
  one sitting (roughly 1,000 lines), say so and review commit by commit.
- **Earlier threads.** Read the existing reviews and comments so you
  don't repeat them. Check whether earlier findings were dealt with.
- **Blockers that aren't code.** A merge conflict, a draft state, or any
  active gate in `doctrine/development-doctrine.md`. The review-debt cap
  is suspended by programme plan P17: open rows still block their release
  gates, but do not stop implementation merges. Put blockers in the
  verdict, not in the findings; they aren't the author's defects.

## 3. Derive the contract before reading the rationale

Before you read the PR's explanation or any long commit message, write
down in your scratchpad what the change should do:

- the BUILD_PLAN task named in the Handoff, and its done-when criteria;
- the accepted spec rows, `policy.yaml` entries, `decisions/`, ADRs and
  `REPOSITORY_STRUCTURE.md` dependency-boundary rows the diff touches;
- supported inputs, the `unsupported` and `needs_review` outcomes, period
  and version gates, rounding and precision, provenance and errors.

For every statutory value or rule the PR adds or relies on, check the
dated primary NZ source yourself. That means the legislation.govt.nz
version in force for the period, plus the IRD or MSD guidance checked
separately. Record the URL, version or date, the locator and what it
supports. Memory is never the authority. If a source can't be reached,
record the claim as not verified instead of assuming it. Never consult
OpenFisca or another engine for expected behaviour
(`doctrine/ip-doctrine.md`). Use the `provenance` skill for `sources.yaml`
and dataset manifests.

Once you have read "this is right because…", you tend to check the code
against the author's story rather than against the law. That is why this
step comes first.

## 4. Read the whole diff, twice

Review `git diff <fork point>...<head>`. That is the diff GitHub and the
guard workflows use. Open each changed file and read around its hunks,
not only the hunks.

**Pass 1: design.** Does it do what the task asks, at the right layer and
in the file `REPOSITORY_STRUCTURE.md` names, with no more abstraction than
two real policies need? Does it respect the dependency boundary? Does it
change a shape that others rely on: an API response, the stored-run
schema, the `policy.yaml` schema? Search for callers of anything changed
or removed outside the diff (`rg`). Raise design problems first, before
the author polishes code that has to move.

**Pass 2: line by line**, with `references/checklist.md`. It covers:

- correctness;
- the Poltika invariants (a missing fact is never zero, `unsupported`
  outranks `needs_review`, WFF and AS are never added, Decimal exactness,
  `[from, to)` periods, version gates);
- sources and protected values;
- tests, and API and data boundaries;
- security, performance, readability and docs.

The invariants always apply when the diff touches calculation, outcomes
or the API.

Keep a running list of *suspicions*. They are not findings yet.

## 5. Run it and try to break it

In the worktree, run what CI runs and record the exact results:

```sh
uv sync --locked --extra dev
uv run --extra dev ruff check src tests
uv run --extra dev mypy --strict src
uv run --extra dev python -m poltika.engines.assurance.evidence policy_specs/working_for_families policy_specs/accommodation_supplement
uv run --extra dev pytest -q
```

Add any new `policy_specs/<policy>` directory to the evidence command.
Note every skip and its reason. PostgreSQL skips are expected where the
server binaries are missing; any other skip needs a named reason. A green
suite supports a verdict. It doesn't replace the probes below.

- **Reproduce every suspicion.** Write the smallest test or `python -c`
  in your scratchpad that shows the defect on this SHA. If it reproduces,
  it's a finding and the reproduction goes in it. If it doesn't, drop it
  or ask it as a question. An unproven defect report wastes the author's
  time and costs the review its credibility.
- **Check that the tests bite.** Restore the modified source files to
  the fork point while keeping the new tests
  (`git checkout <fork point> -- <modified src files>`), run the new
  tests, and confirm they fail. Then `git checkout <head> -- .`. If the
  tests import a module or name the PR adds, the revert only gives a
  collection error, which proves nothing. Break each line that
  implements a rule instead (flip a comparison, drop a guard, skip a
  conversion) and confirm a test fails for each. A change no test
  notices is untested, and so is a behaviour the PR claims but no test
  pins. That's a `TEST_ERROR`, or dead code if nothing reads the result.
- **Probe the edges the author may have missed.** Both edges of every
  period and threshold. Unknown against zero. `unsupported` and
  `needs_review` in the same household. A malformed or extra API field.
  A mismatched policy version.
- For changes to `api/`, `deploy/` or input handling, also run the
  built-in `/security-review`. The built-in `/code-review` is a useful
  second bug-hunting pass. Whatever either reports goes through the same
  reproduce-first rule.

Don't push fixes to the PR you're reviewing. The author fixes their PR,
and a reviewer's fix would need a review of its own. If Pete asks you to
implement the fixes, make them separate commits, label them
reviewer-authored, and say they need the other model's review (the
queued-PR audit did this).

## 6. Write the findings

Read `references/writing-findings.md` first. In short, each finding has:

- an ID (`R1`, `R2`…) that stays fixed across rounds;
- a severity. **P1**: a wrong result or status, a missing fact turned
  into a number, a protected value changed outside the process, data
  integrity, security, or CI red because of this PR. **P2**: a real
  defect on a narrower path, the main behaviour untested, or a doc now
  untrue. **P3**: minor and non-blocking. Then **nit**, **question**, and
  **escalation** (for Pete);
- for defects and escalations, a proposed Review Doctrine class:
  `CODE_ERROR`, `TEST_ERROR`, `SPEC_ERROR`, `SOURCE_CONFLICT`,
  `INTERPRETATION_AMBIGUITY`, `MISSING_SOURCE` or `ARCHITECTURE_ISSUE`.
  Use `REVIEWER_ERROR` when withdrawing a finding that was wrong. Pete
  confirms classes;
- the location, expected against actual, the reproduction and its output
  on the head SHA, and a suggested fix if you have one.

Genuine interpretation ambiguity and conflicting sources are
escalations, not something for the author to "fix". Give the competing
readings with citations and what each would change, and leave the choice
to Pete. Never choose the reading that makes the tests pass.

Now read the author's rationale: the PR body, commit messages and any
replies. If it answers a finding, withdraw or downgrade it and say so. If
it shows a misunderstanding, the finding stands. In any written record,
keep your derived expectations above the author's response.

## 7. Verdict, posting and the record

Choose one verdict for the SHA:

- **Ready to merge**: no open P1, P2 or escalation, and CI green on this
  SHA. List any blockers that aren't code separately. The verdict is
  review evidence, not the merge: under ADR-0020's merge rules Claude Code
  merges Tier A/B work only when the branch is up to date, the author
  preflight and a final-head `poltika-reviewer` pass have run, and, for
  `policy_specs/`, `engines/simulator/` or a calculated amount, the
  cross-model row in `review_packets/review_queue.md` is cleared. Tier C
  stays with Pete.
- **Changes requested**: at least one P1 or P2 is open.
- **Needs Pete's decision**: an escalation blocks part of the change.
- **Not reviewable yet**: the head is still moving, the scope is
  unbounded, it's a draft, or it doesn't build.

**Posting.** Post one GitHub review:

1. `pull_request_review_write`, method `create`, with `commitID` set to
   the reviewed SHA and no `event`. That creates a pending review.
2. `add_comment_to_pending_review` for each finding on a changed line
   (`subjectType: LINE`, `side: RIGHT`). A finding on a line outside the
   diff goes in the summary instead.
3. `pull_request_review_write`, method `submit_pending`, with event
   `COMMENT` and the summary body from `references/writing-findings.md`.

Always use `COMMENT`, never `APPROVE` or `REQUEST_CHANGES`. The tools act
as Pete's account, which opened the PR, so GitHub refuses the other two
events. An approval from that account would also read as Pete's
acceptance. Review comments remain distinct from acceptance under
ADR-0020. End every post with the Claude Code attribution footer.

Posting is outward-facing. Post straight away if the user asked you to
review *and post*, or if the review was triggered by a PR event.
Otherwise show the summary and inline comments in chat and ask first.

**Durable record.** Write `reviews/<YYYY-MM-DD>-pr<N>.md` for a full
review of a queue row, an independent cross-model review, or any review
with an escalation. The record's shape is in
`references/writing-findings.md`, and it goes in its own documentation
PR. For a queue row, set its status to `reviewed (reviews/<file>)` and
update the open count in the header. A light check or a re-review round
can live in the PR comment alone, as #108's and #112's did.

Findings on an open PR are fixed in that PR. Findings on merged work are
fixed in a new PR (`doctrine/development-doctrine.md`).

Remove the worktree when you're done: `git worktree remove <dir>/pr-<N>`.

## 8. Re-review after new commits

- **Mechanical main update (ADR-0020).** If the only new commit integrates
  `main`, apply ADR-0020's whitespace-sensitive comparison to the PR's own
  changes against the old base and new `main`. Preserve change bytes, paths,
  modes and binary contents; matching `git patch-id --stable` alone is not
  proof. A conflict is allowed only in ADR-0020's listed records and only
  after a base-relative check proves an exact combination of existing,
  independent entries, with no new text, duplicate authoritative IDs or
  contradictory statuses or decisions. No-deletion diffs alone are not
  proof either. Record the old base, reviewed head, new head, new `main`,
  record paths and both checks; require green CI on the new head. If any
  condition fails or cannot be proved, review the fix under the bullets below.
- Diff from the SHA you last reviewed to the new head. If the old SHA is
  no longer an ancestor (a force-push or rebase), review the whole PR
  again.
- Rerun the checks on the new head. A green run on the old SHA says
  nothing about the new one.
- Rerun each earlier finding's reproduction. Reply on its thread with
  the fixing commit and the evidence, and resolve the threads you opened
  once they're fixed (`pull_request_review_write`, method
  `resolve_thread`). Say which findings remain open, using the same IDs.
- Review the new code properly. Don't raise new nits on lines this round
  didn't change; that turns the review into a moving target. A real
  defect anywhere is still fair game.
- Post a short round summary with the new SHA and verdict.

## Mistakes that cost the most

- Approving because CI is green, or reviewing the description instead of
  the code.
- Posting a suspicion as a fact. Reproduce it or ask.
- Burying a P1 under nits. Put blockers first and group the nits in one
  comment.
- Reporting a style preference that ruff doesn't enforce and the code
  base doesn't follow as a defect.
- Settling an interpretation question yourself, or accepting a protected
  expected value changed to match the code.
- Calling a same-model check independent, or wording a review so it
  implies acceptance by Claude Code or Pete.
