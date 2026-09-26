# Session orientation: findings and plan

- **Date:** 26 September 2026
- **Author:** Claude Code, at Pete's request, after running the v0.1
  question set Q71-Q140 in a fresh session.
- **Checkout:** `main` at `27aa811` when the session started. `main` moved
  to `5a73539` (PR #74) during the session.
- **Status (26 September 2026):** S1-S7, S9 and S10 are done (PR #77). S8 is
  not being built (see below).

## Goal

A fresh Claude Code or GPT/Codex session can explain what v0.1 is, and run
a correct WFF, AS and combined scenario, after reading about 300 lines. This
session read about 5,000 lines to get there.

Done when:

1. `docs/ORIENTATION.md` exists, fits on one page (about 200 lines at most)
   and describes current behaviour only, with no task or PR history.
2. CLAUDE.md has a "v0.1 at a glance" block (15 lines at most) and a
   reading list for each type of task.
3. The orientation doc's example runs unchanged on `main`, and CI runs it.
4. A fresh-context check passes (S10): a new session given only CLAUDE.md
   and the orientation doc answers the check questions and runs the
   example, without opening BUILD_PLAN.md, a specification or a calculator.

## Findings

### F-1: the only reading list is about 3,700 lines

CLAUDE.md's "Before making changes" list sends every session to
BUILD_PLAN.md (1,995 lines), ARCHITECTURE.md (321), REPOSITORY_STRUCTURE.md
(263), the WFF specification (854) and the AS specification (633). That is
right before changing policy logic. It is far too much for running a
scenario, answering a question about v0.1 or checking results, and there is
no shorter path for those tasks.

### F-2: code and YAML comments record history, not current behaviour

`wff.py` is 1,121 lines, `accommodation_supplement.py` 939 and the AS
`policy.yaml` 401. Much of the comment text is review history ("PR #21
review finding", "Task 26a repair", superseded wording kept on record). The
current rules are there, but they have to be dug out. This note does not
propose removing that history, which is the audit trail. It proposes a
separate summary of current behaviour.

### F-3: the facts that matter most are scattered

Each of these took a separate discovery:

- **No WFF total.** The in-work tax credit is always `needs_review` for
  2026-27, because `in_work_base` is gated (Task 10.2). So
  `total_annual_entitlement()` never returns a value.
- **Inputs are caller-asserted statuses, not raw facts.** Facts are
  `verified`, `excluded` or `unknown`. There is no date of birth, age, child
  ID, hours worked, address or rent breakdown. The API rejects unknown
  fields with a 422.
- **WFF covers whole years only.** A child who qualifies for part of the
  year, a relationship change or shared care makes every component
  `unsupported` for the whole household.
- **MFTC needs an attested after-tax (ME 3) income.** Poltika has no income
  tax module.
- **AS is weekly.** Each assessment week takes one area, one cost and one
  income. It uses MSD's published entry thresholds, and rounds up only at
  the end (r 19).
- **Outcomes.** `unsupported` outranks `needs_review`. A value is returned
  only when the outcome is `calculated`, and a missing fact never becomes
  zero.
- **Combined runs.** Results stay in their own periods and are never added
  together. Conflicting shared facts turn results into `needs_review`.
- **Run settings.** WFF uses policy `0.1.0` and a lookup date inside
  2026-04-01 to 2027-04-01. AS uses policy `0.1.1` and an explicit 7-day
  assessment week starting on or after 2026-04-01.

### F-4: the fastest sources exist but aren't signposted

- `docs/demo/v0_1/request.json` and `response_summary.json` show the whole
  input and output contract in about 100 lines.
- The "Read this first" section of
  `review_packets/v0_1_question_set/calculations.md` is the best summary of
  v0.1, but it sits inside a review packet.
- The `WffScenario` and `AsScenario` dataclasses are the real input
  contract.

### F-5: each session rewrites the same scenario builders

`run_questions.py`, `run_current_70.py` and this session's `run_q71_140.py`
each rebuild WFF, AS and combined scenario constructors with the same
"every fact verified" defaults.

### F-6: the checkout changes under a running session

During this one session:

- `main` moved (PR #74);
- the shared checkout switched to `fix/q71-140-review`, with another
  session's uncommitted changes;
- a third session announced a change to every `ComponentResult`
  (ADR-0014 outcome reason codes, `feat/outcome-reason-codes`).

An API check (`extra="forbid"`) contradicted code read minutes earlier.
Nothing tells a session to check git state first or to work in its own
worktree.

## Subtasks

Claude Code drafts; Pete accepts.

- [x] **S1: Pete decides timing and location.**
  - Timing: land before the `v0.1.0` tag (documentation only, with no
    policy or code change), or as the first v0.1.5 task alongside the
    deferred taxonomy rework (Task 35.4).
  - Location: confirm `docs/ORIENTATION.md`, and choose where the shared
    helper in S8 lives (`scripts/` is in the target tree but not
    instantiated).
  - **Decided 26 September 2026 (Pete, "proceed"):** S2 starts now, before
    the `v0.1.0` tag, at `docs/ORIENTATION.md`. The S8 helper's location is
    still open.
- [x] **S2: write `docs/ORIENTATION.md`.** (PR #77) Sections:
  - what v0.1 models and what it doesn't;
  - outcome states and which one wins;
  - the facts that always hold (F-3);
  - the input contract, one line per group of scenario fields;
  - where things live, in one table;
  - how to run it: an example of about 15 lines that runs one WFF, one AS
    and one combined scenario, plus the API equivalent;
  - what to read next, by task.

  Current behaviour only, linking to the specifications as the authority.
  Write it against `main` after the in-flight branches land, or update it
  when they do. `fix/q71-140-review` changes the r 15 asset test and adds an
  s 65AAA gate. `feat/outcome-reason-codes` changes `ComponentResult`.
- [x] **S3: add the new file to REPOSITORY_STRUCTURE.md** (PR #77) in the same PR as
  S2.
- [x] **S4: add a "v0.1 at a glance" block to CLAUDE.md.** (PR #77) 15 lines at most:
  one line per F-3 fact, plus a link to the orientation doc.
- [x] **S5: key CLAUDE.md's reading list by task.** (PR #77)
  - Running scenarios or answering questions: the orientation doc and the
    demo.
  - Checking results: add the relevant specification's calculation
    sequence.
  - Changing policy logic: the current full list, unchanged.

  The ground-truth, implementation and review rules stay as they are.
- [x] **S6: add a "check state first" rule to CLAUDE.md.** (PR #77) At the start,
  run `git status -sb`, `git log --oneline -5 origin/main` and
  `git worktree list`. Make edits in a `/private/tmp/poltika-*` worktree off
  `origin/main`, not in the shared checkout, because several sessions run at
  once.
- [x] **S7: make CI run the orientation example** (PR #77:
  `tests/acceptance/test_orientation_examples.py`), so the doc fails the
  build when the contract changes. For example, keep the example in a
  module that a test imports and runs.
- [x] **S8 (closed, not built): extract one shared scenario-builder helper**
  from the three question-set scripts, and point the orientation example at
  it. Its location is decided in S1.
  - **Closed 26 September 2026: not built.** The orientation page's example now shows how to build each scenario. A helper that defaults every fact to
    `verified` must not live in production code: it would make it easy for a
    missing fact to count as verified, which SCHEMA.md forbids. If built, it
    belongs with test or script code and must be named as a test
    convenience.
- [x] **S9: add a check to prevent staleness.** (PR #77) Add a step to
  `.claude/skills/pr-review-preflight/SKILL.md`: "Does this PR change a fact
  in `docs/ORIENTATION.md`? If so, update it in the same PR."
- [x] **S10: run the fresh-context check.** Start a new session with only
  CLAUDE.md and the orientation doc. It answers the questions below and runs
  the example. Record the result in `reviews/`.
  - **Done 26 September 2026**, twice, by a subagent given only CLAUDE.md and
    `docs/ORIENTATION.md` (questions without answers). First run: 6/6
    correct, question 2 hedged; it listed 11 gaps (IWTC reason in the
    example, "gated", decimals, `None` for unknowns, the age rule, the
    shared-fact list, the week end, Act names, named `ChildFacts`
    arguments), all fixed in #77. Second run, on the v0.1.5-updated page:
    6/6 correct; two remaining gaps (part-year input value, unknown-assets
    effect) fixed in #77's last commit. The page is about 240 lines, over
    the 200-line target, because v0.1.5 content and these fixes were added.

### Check questions for S10

| # | Question | Expected answer |
| --- | --- | --- |
| 1 | Why does v0.1 never give a WFF total? | The in-work tax credit is always `needs_review` (`in_work_base` is gated). |
| 2 | A child turns 18 in October 2026. What does Poltika return? | Every WFF component is `unsupported`: part-year qualification is outside the whole-year domain. |
| 3 | Can Poltika tell whether two child records are the same child? | No. There is no child ID or date of birth, and the API rejects those fields. |
| 4 | In a combined run, the household's assets are unknown. What happens? | WFF is unaffected. AS is `needs_review`. |
| 5 | What period is an AS result for, and can it be added to a WFF result? | One assessment week. No: results stay in their own periods and are never added. |
| 6 | Run the example on the demo household. What are FTC and AS? | FTC $7,472.50 a year; AS $220 a week. |
