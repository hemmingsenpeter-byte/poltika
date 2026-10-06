# Codex recheck — PR #176 review refresh rule

## Findings

**Verdict: no actionable findings.** The Claude-authored amendment is eligible
for independent cross-model clearance, subject to the coordinating review's
required verification. No P1, P2, P3, nit or escalation remains open.

This retrospective pass covers the two Claude commits below and their unchanged
operational text on inspected main. It does not clear the Codex-authored
reconstruction in this mixed-authorship PR. Acceptance and clearance recording
remain with the coordinating lane and delegated acceptance authority.

## Review inputs

- Reviewer: GPT/Codex, 7 October 2026; independent cross-model review of Claude work.
- PR: [#176](https://github.com/hemmingsenpeter-byte/poltika/pull/176).
- Inspected main: `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`.
- Claude amendment: `be7ca4ec1d5bc63ef94c14f71904b4acb1e6256e`; parent
  `5329d4df42b0f07767471999649db3d56fa4968e`.
- Claude follow-up: `0df6008504bb4a920463c64bb18956d5c952a249`; parent
  `ee0c007b24cb796ec1320759184a07965fd2019a`.
- Squash: `7c0f67e7e847e5e57f66269bf007c9fe88d1e5e7`; parent
  `0d115b4e2c63b5d6f2d6517d92f74d9d9ffdc934`.
- Depth: complete diffs of both Claude commits and all ten changed operational
  entry points. The complete merged PR diff was also read for surrounding
  context (17 files, 319 additions, 83 deletions); clearance remains scoped by authorship.
- Contracts: Pete's 6 October decision supplied in the review brief; ADR-0020,
  BUILD_PLAN's retained review doctrine, architecture and repository-placement
  guidance, review/development/test doctrine, reviewer agent, both review skills
  and `writing-findings.md`.
- Blind derivation: expected behaviour was derived and communicated before either
  commit diff or author rationale was read. Commit messages and reconstruction
  packet were read afterwards. Live PR body and threads were not fetched here.
- CI: not independently queried. The coordinating reviewer owns global checks.
- No statutory claim, protected expected value, calculation or external-engine
  comparison is introduced by the two Claude commits.

## Independent review

### Independently derived expected behaviour

A merge from main qualifies only when it has no conflict and the PR's own diff
matches the reviewed own diff under `git patch-id --stable`. It needs green
required CI on the new head and a PR delta record naming reviewed head, new head
and main SHA. It renews neither author preflight nor either reviewer gate.
Conflict resolution or a changed own diff renews every gate. A qualifying merge
adds no semantic authorship; a same-model pass cannot clear that model's
substantive changes.

### Entry-point audit

| Entry point | Result |
| --- | --- |
| `adr/0020-delegated-acceptance.md:69` | Gates 2/3 allow the reviewed head only for a mechanical update. Lines 89–97 require no conflict, matching own patch IDs, new-head CI and the three-SHA record; conflict resolution or own-diff change renews every gate. |
| `AGENTS.md:99`, `CLAUDE.md:156`, `BUILD_PLAN.md:44` | Each explicitly limits its general invalidation rule to ADR-0020's mechanical exception. |
| `CONTRIBUTING.md:74` | Update/review flow includes the specific exception at line 78 and shared exception at lines 96–98. Merging authority is explicitly ADR-0020. |
| `doctrine/review-doctrine.md:42`, `doctrine/development-doctrine.md:106` | The former links the same exception; the latter substitutes green CI plus delta record for renewed author preflight and review. |
| `.claude/agents/poltika-reviewer.md:9` | First instruction preserves prior clearance only for ADR-0020's mechanical update; shared rule repeats it. |
| `.claude/skills/pr-review-preflight/SKILL.md:43` | Shared invalidation rule includes the narrow exception. Follow-up fixes continue to require renewed checks and final-head review. |
| `.claude/skills/pr-review/SKILL.md:287` | Step 8 compares own diffs against their respective main bases. Matching IDs waive renewal only after a conflict-free merge. Mismatch **or** conflict routes to full re-review. |
| Acceptance checks | `test_programme_authority.py` checks programme authority; `test_review_queue.py` checks queue parsing. Neither claims to validate this exception. No dedicated mechanical-update acceptance test exists; that is a limitation, not a defect without a requirement for such a test. |

No entry point permits patch-ID equality to waive review of conflict resolution.
Green CI and matching IDs also do not independently prove a conflict-free merge;
that prerequisite remains explicit.

A preliminary suspicion treated unconditional summaries (`AGENTS.md:87`,
`CLAUDE.md:144`, `doctrine/review-doctrine.md:31`, `CONTRIBUTING.md:115`) as a
blocking contradiction. That proposed P2 characterization was withdrawn:
each document supplies the specific ADR-0020 exception, and no contrary gate
decision was reproduced. The withdrawn characterization is `REVIEWER_ERROR`;
no defect finding is retained.

## Author response

Read after contract derivation. `be7ca4e` explains that only a conflict-free,
unchanged-own-patch update avoids renewal. `0df6008` explains why comparing own
diffs replaces old-head/new-head changes, which include unrelated main changes.
Both explanations agree with the independently derived contract.

## Resolution and verification

- Complete Claude-commit and merged diffs inspected in bounded parts.
- `git diff --check be7ca4e^ be7ca4e`, `git diff --check 0df6008^ 0df6008`,
  `git diff --check 7c0f67e^ 7c0f67e`: exit 0, no whitespace errors.
- `git diff 7c0f67e a8b214f --` the ten operational paths and `tests/acceptance`:
  empty; the reviewed text and checks are unchanged on inspected main.
- `git merge-base be7ca4e ee0c007^2` returned
  `b176ddc72eefd1811a0b8317d812dd389e6f3ae7`.

Actual branch history reproduces positive and negative own-diff comparisons:

```sh
git diff b176ddc72eefd1811a0b8317d812dd389e6f3ae7...be7ca4e | git patch-id --stable
git diff 0d115b4e2c63b5d6f2d6517d92f74d9d9ffdc934...ee0c007 | git patch-id --stable
git diff 0d115b4e2c63b5d6f2d6517d92f74d9d9ffdc934...0df6008 | git patch-id --stable
```

| Own diff | Stable patch ID | Expected / actual |
| --- | --- | --- |
| Before main integration | `b952b3da92b7c2fdedd2e28b48a14e6d05d8a432` | Reviewed reference |
| After `ee0c007` main integration | `b952b3da92b7c2fdedd2e28b48a14e6d05d8a432` | Matches reference |
| After `0df6008` follow-up | `92ada1c57b0d90ca3118fecbd405b61d24895961` | Differs; full gate renewal required |

Control: `git diff be7ca4e...ee0c007 | git patch-id --stable` returned
`33536f3824acb8f0583ad86e6ee1b2b109fa8573`, showing why old-head/new-head
changes are not the own-diff comparison. These probes establish comparison
behaviour, not historical CI or absence of a merge conflict.

### Not verified

- After interpreter startup recovered, the following command passed on the
  exact source checkout:
  `env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -p no:cacheprovider -q tests/acceptance/test_programme_authority.py tests/acceptance/test_review_queue.py`:
  **12 passed in 0.69s**. These verify existing authority/queue behaviour,
  not a dedicated mechanical-update acceptance contract.
- Coordinating broad checks and remote CI are recorded in the PR handoff.
  No dedicated refresh acceptance or mutation test was run; the direct
  Git history probes above test the actual documented delta procedure.
- Live PR threads, original supplied attachment and retrospective proof of
  conflict-free status were not independently verified. The governing decision
  was supplied as an explicit review input.

No target fix is requested. Only this record was written by this reviewer;
no commit, remote post, merge or shared Git mutation was performed.
