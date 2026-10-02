# Writing findings, comments and the summary

A finding is only useful if the author can act on it without asking you
what you meant, and if Pete can see from the summary alone what blocks the
merge. Write for both readers.

## Severity

| Severity | Meaning | Blocks merge | Poltika examples |
| --- | --- | --- | --- |
| **P1** | Wrong result or status, or a trust-breaking defect | Yes | A missing fact becomes `calculated` or `0`; an amount off by a rule; a protected value changed outside the test-doctrine process; a raw snapshot edited; a caller-supplied path reaches the filesystem; CI red because of this PR |
| **P2** | A real defect on a narrower path, or the change's main behaviour untested | Yes, unless Pete waives it | A crash on an edge input; the wrong HTTP status; a cache key missing a selector; tests that pass with the change reverted; `ORIENTATION.md` now untrue |
| **P3** | Minor defect or fragility | No. Fix in this PR if cheap | A misleading error message; a missing regression test for a fixed edge |
| **Nit** | Style, naming or readability | No | A name that says less than it could. Group nits into one comment |
| **Question** | You can't tell whether it's a defect | No, until answered | "Is `x` ever unknown here? If so, …" |
| **Escalation** | The law, sources or spec don't settle it | The affected part waits for Pete | Two MSD pages round differently; a rule the spec doesn't cover |

The IDs `R1`, `R2`… stay fixed across review rounds, so a thread and the
summary always mean the same finding.

## Review Doctrine class

Defects and escalations carry a *proposed* class. Pete confirms it.

| Class | Use when | Goes to |
| --- | --- | --- |
| `CODE_ERROR` | The code doesn't do what the accepted spec says | The author |
| `TEST_ERROR` | A test or expected value is wrong, or doesn't test what it claims | The author |
| `SPEC_ERROR` | The accepted spec itself is wrong against its sources | The spec's owner (GPT/Codex) and Pete |
| `SOURCE_CONFLICT` | Primary sources disagree | Pete, with both citations |
| `INTERPRETATION_AMBIGUITY` | The sources allow more than one reading | Pete, with the competing readings and their effect |
| `MISSING_SOURCE` | A claim has no primary source | Pete, and the spec's owner |
| `ARCHITECTURE_ISSUE` | Wrong layer or boundary, or a design that won't hold | Pete and the author |
| `REVIEWER_ERROR` | A reviewer's finding (yours or an earlier one) was wrong | Withdraw it on the record; don't delete it |

## An inline comment

One finding per comment, on the line it concerns. Lead with the severity
and class so the author can triage at a glance. Then what happens, why it
matters, the proof, and a fix if you have one. This example is
illustrative, not a real finding:

````markdown
**R2 · P1 · CODE_ERROR.** Unknown family income is abated as zero.

`_abate()` falls back to `income or Decimal(0)`, so a household with no
attested income gets the full family tax credit and a `calculated` status.
Spec step 2 needs `needs_review` with `family_scheme_income` in
`missing_facts`: a missing fact is never zero.

Reproduction on `03b6729`:

```text
uv run pytest -q <scratchpad>/test_r2.py
AssertionError: status 'calculated' != 'needs_review' (amount 7921)
```

Suggested fix:

```suggestion
    if income is None:
        return ComponentResult(
            outcome="needs_review", code="WFF_FAMILY_INCOME_UNVERIFIED",
            missing_facts=("family_scheme_income",), reason="family_scheme_income unverified",
        )
```
````

Use a GitHub `suggestion` block only when the replacement is exact and
complete for the lines the comment is anchored to. Otherwise describe the
fix in prose.

### How it reads

| Instead of | Write |
| --- | --- |
| "This is wrong." | "`x` returns 0 when `y` is unknown; the spec needs `needs_review`." |
| "Why did you do it this way?" | "What's the reason for a set here? If order doesn't matter, a comment saying so would help; if it does, the hash changes with input order." |
| "Consider refactoring this." | "`_band()` and `_rate()` repeat the interval lookup. One helper would keep them from drifting. Non-blocking." |
| "I think this might break X." (unverified) | Reproduce it and report it, or ask it as a question. |
| Twelve separate nit comments | One comment: "Nits, all non-blocking: …" |

Write about the code, not the person. Assume the author had a reason and
ask when you can't see it. Say what is good only when it is specific and
useful to know ("the period-edge tests are exactly the ones that caught
#75"), never as padding. Match the repo's plain style: short declarative
sentences, no hedging stacks, no emphasis for its own sake.

## The summary review body

Submit it with the pending review's inline comments, event `COMMENT`.
Blockers come first. Link inline findings rather than repeating them.

```markdown
## <Label> of PR #<N> at `<short head SHA>`

**Verdict: <Ready to merge | Changes requested | Needs Pete's decision | Not reviewable yet>.**
<One or two sentences: what blocks, or why it's ready.>

Label: <independent cross-model review (Claude Code) | fresh same-model check>.
<Blind, or: the author's notes were read before expectations were derived.>
Depth: <full | light>. Diff `<fork point>...<head>`, <n> files, <n> commits.

### Blocking
- **R1 · P1 · CODE_ERROR** `<path>:<line>`: <one line>. (inline)

### Escalations for Pete
- **R3 · INTERPRETATION_AMBIGUITY**: <the question; reading A → effect; reading B → effect; citations>.

### Non-blocking
- **R4 · P3** …
- Nits: see the grouped comment.

### Checks on `<short head SHA>`
- `ruff check src tests`: <result>. `mypy --strict src`: <result>.
- Evidence coverage: <result>. `pytest -q`: <n passed, n skipped (reasons)>.
- Tests bite: <reverted which source files; which new tests failed>.
- CI on this SHA: <each check and its result>. Statutory Value Guard: <files listed, or none>.
- Sources checked: <URL, version or date, locator>, or "no statutory claims in this diff".

### Not verified
- <What you didn't check and why: e.g. PostgreSQL tests skipped locally, deploy image not built, a source unreachable.>

### Not code findings
- <Review-debt cap, merge conflict, draft state. Omit if none.>

---
_Generated by [Claude Code](https://claude.ai/code)_
```

Omit empty sections, except **Not verified**: say "Nothing material" if
that's true, so the reader knows you considered it.

## Replies in a re-review

- Fixed: "Fixed in `abc1234`. The reproduction now returns `needs_review`,
  and `test_unknown_income_is_needs_review` fails on the old head." Then
  resolve the thread.
- Not fixed: say what still happens, with the rerun output. Leave it open.
- Author disagrees convincingly: "Withdrawn: <reason>." If the original
  finding was wrong, class it `REVIEWER_ERROR` in the summary.
- Author disagrees and you still think it's a defect: restate the
  evidence once, then leave it for Pete in the summary. Don't argue in
  circles on the thread.

## The durable record

Write `reviews/<YYYY-MM-DD>-pr<N>.md` when SKILL.md step 7 calls for one.
Follow `review_packets/TEMPLATE.md`, shaped like
`reviews/2026-09-27-pr117.md` and `reviews/2026-09-27-queued-pr-audit.md`:

1. **Findings**: the verdict and what this review does and doesn't close.
2. **Review inputs**: reviewer and date, PR link, base or fork point and
   head SHAs, diff scope, CI state, the contracts reviewed against, the
   label, and whether the review was blind.
3. **Independent review**: the expected behaviour you derived, then a
   discrepancies table (ID, severity and class, trigger, impact and
   resolution).
4. **Author response**: added after the independent section, never
   merged into it.
5. **Resolution and verification**: each finding's outcome (fixed in
   which commit, escalated, withdrawn), the exact commands with their
   results, and what remains open.
