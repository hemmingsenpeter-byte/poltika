# PR #193 — GPT/Codex clearance and Task 7 handoff

**Date:** 13 October 2026, Pacific/Auckland.
**Reviewer:** GPT/Codex, with separate fresh-context source and gate readers.
**Disposition:** #193's merged, gated source/specification draft is reviewed.
No actionable P1/P2 defect was found within that scope. The owed GPT/Codex
clearance is complete; Task 7, its executable specification and Gate B are
still incomplete.

## Fixed target and review ownership

| Input | Evidence |
| --- | --- |
| PR | [#193](https://github.com/hemmingsenpeter-byte/poltika/pull/193), merged 11 October 2026 |
| Actual final base | `f78eb26278b21df13a6a60c61b088348e7f233e1` |
| Actual final head | `b108c40fa464af4dfd0a29f77c5c3aebe27c3fb0` |
| Squash on main | `aa0c9c6e4336bacdbe3f451978853bcf09b5e454` |
| Current review baseline | `de76f26`, isolated worktree `/private/tmp/poltika-task7-clearance-20261013` |
| Scope | Eleven source/specification, decision, research, preflight and tracking paths; no executable policy, engine or protected expected-value fixture |
| Claude-authored follow-ups | `34225bd` (source-check wording, DEC-003 arithmetic and queue placement), `709118e` (adjacent IR3G rows), and main integrations |

The original specification was GPT/Codex-authored. Its independent Claude
source review is recorded in the [10 October PR comment](https://github.com/hemmingsenpeter-byte/poltika/pull/193#issuecomment-6093912718)
and [11 October source review](2026-10-11-pr193-independent-source-review.md)
at `2cc00c89b3abbeee80df2d9257eaa799dee65b71`. This Codex pass independently
checks the Claude-authored additions and final integration; its supporting
review of the original GPT content does not replace that Claude review.
The 11 October Claude record's clause-level limits remain part of that
evidence; it did not fully read BC 2–5, BC 8, DA 2/3, YD 1, CF 1 or CE 1BA.
This closeout does not relabel that pass as a complete executable-specification
approval.
The root reader had the PR description and earlier reviews available; the
separate source reader derived claims before reading author rationale.

The income-tax directory, scope note, preflight and 9 October source-recheck
record are byte-identical from `2cc00c8` to the final head, squash and current
baseline. Later main integrations changed unrelated scopes. Their correctness
is outside this income-tax clearance. Pete's [D30 waiver](../docs/decision_log.md)
allowed the earlier merge; this record now closes the separately retained
Task 7 review obligation.

## Expected behavior and findings

The source/specification contract requires classified individual annual
taxable income in the commissioned salary/wage slice, explicit exclusions
and missing facts, the exact requested period/version, and visible authority
and precision gates. The documentary rate table is source transcription,
not executable parameters. Unsupported facts outrank unresolved facts;
unresolved authority prevents every numeric result, including known zero.
Basic tax is separate from PAYE, ACC, credits and disposable income.

| Review item | Classification and disposition |
| --- | --- |
| Claude's documentary date correction | Consistent with `sources.yaml`: retrieved 3 October, rechecked 8 October; no rate, threshold or effective date changed |
| CE 1 / CE 1BA wording | Explicitly limits the amendment audit rather than asserting unreviewed provisions are out of scope; full-period coverage remains required |
| DEC-003 arithmetic and adjacent worksheet rows | Reviewed source evidence; the discrepancy is retained, with no silently corrected official cell or adopted benchmark |
| Annual authority | Existing gated limitation, not an introduced draft defect. D36 retains `needs_review` until Royal assent and a dated source check |
| Precision | D36 chooses whole-dollar taxable income only as an Assumption. It supplies no official intermediate/final rounding or tie convention |
| Stale tracking and DEC/spec statuses after D36 | P3 documentation discrepancy. This closeout reconciles the queue and programme row; applying the decisions to the existing DEC/spec/source records is the next bounded specification change |

The [IRD bill status page](https://www.taxpolicy.ird.govt.nz/bills/2026-fbt-simplification-tax-bill),
retrieved 13 October, is labelled **as at 12 October 2026**, **Select committee**.
It does not establish Royal assent. This is bill-status guidance, not enacted
authority; the D11/Q16 gate remains `needs_review`. The [IRD annual-calculator
page](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income)
separately confirms the component exclusions, but supplies no retained
numerical benchmark here.

The separate source reader fetched the official [ITA version dated
4 September 2026](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
and read BB 1, BC 1–6/8, BD 1/3, CE 1, CF 1, DA 2/3, YD 1, YE 1 and
Schedule 1 Part A cl 1/Table 1. The [2024 Budget Measures Act](https://www.legislation.govt.nz/act/public/2024/19/en/2024-06-04/)
ss 2(5), 37(1)/(4), and [TAA version dated 4 September 2026](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/)
ss 22I/92A were checked separately. Direct official retrieval was used
where the web reader returned 403; each dated source was checked as fetched.

The separately retrieved [IR3G PDF](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1---ir99/ir3g/ir3g-2026.pdf?modified=20260331185539)
matches SHA-256 `4b0f2ffbc831c0aa88235d2c0ce986fa80b234be8f3fb6ac17ee1ab377f71b99`.
Printed p 43 independently reproduces the three adjacent A/B/C rows
`53,500 / .30 / 8,270.50`, `78,101 / .33 / 15,650.50` and
`180,000 / .39 / 49,277.50`. The band sum through 78,100 is 15,650.50;
subtracting 78,101 omits one dollar at .33. This verifies Claude's
documentary arithmetic, without promoting a corrected official cell or
an expected statutory fixture. The guide's period is 2025–26.

## Recorded Pete decisions and next Task 7 work

The controlling decision is [D36 / 12 October approval record](../docs/programme/2026-10-12-pete-approvals.md),
not the earlier AI recommendations:

1. **Q16 / DEC-001:** retain D11. No authoritative 2026–27 annual result
   before Royal assent, dated source checking and the reviewed follow-up.
   TAA s 92A's Commissioner route does not override this project decision.
2. **Q17 / DEC-002:** admit whole-dollar taxable income only; fractional
   inputs are `unsupported`. Label this as an Assumption and revisit if an
   official method is found. Do not truncate or round an input into scope.
3. **Q18 / DEC-003:** statute prevails; exclude IR3G as a benchmark, retain
   `SOURCE_CONFLICT`, and do not contact IRD under this instruction.

Next, the Task 7 specification owner applies those decisions to the existing
DEC-001–003, specification and source-review metadata, preserving documentary
history and the enactment gate. Prepare the numeric specification and the
onboarding values/expected-results packet under [the existing five-PR
process](../.claude/skills/new-policy/SKILL.md): source-linked dated parameters,
fact questions, independently derived boundary cases, period-matched official
benchmarks and explicit provenance/outcome checks. Candidates remain gated;
this clearance approves no protected expected value.

The numeric specification must state the arithmetic and output precision
explicitly. Whole-dollar inputs can still yield sub-cent band products;
Q17 is not authority to invent output quantisation. Any unrounded mathematical
value must be described accurately, and any legally rounded amount needs its
own applicable source/review. The excluded IR3G cannot fill the benchmark gap.

GPT/Codex retains the source/value review role; Claude Code implements the
engine after the applicable specification/value gates, using Tasks 5/6's
reviewed household mapping. Missing facts never become zero, the unsupported
input restriction remains visible, and annual authority remains live at the
result boundary. No tax engine or downstream income/EMTR headline is cleared
by this documentary review. Task 7's done-when still requires independent
cases, official benchmarks, regression/provenance checks and engine review.

## Verification and limits

The final #193 GitHub check rollup was inspected on 13 October: `test`,
`web`, `links`, source currency, snapshot/statutory guards, security checks
and `pilot-image` completed successfully. Only the scheduled external-link
report and source-currency issue publisher were skipped. This is historical
CI at the actual final head, not CI for this new documentation follow-up.

Author preflight follows [pr-review-preflight](../.claude/skills/pr-review-preflight/SKILL.md)
for this new documentation follow-up, not independent review of the
original author. The actual focused command was:

```sh
PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q \
  tests/unit/policy/test_decision_records.py \
  tests/unit/engines/assurance/test_evidence.py \
  tests/acceptance/test_review_queue.py
```

Result: **18 passed**, exit 0. `git diff --check` passed. A separate direct
probe validates 14 source-catalogue entries, eight rule rows and four rank-1
source references; verifies the preserved annual-authority gate and absence
of an executable income-tax policy; and checks 38 relative file links in
the three clearance documents and refreshed lane ledger. The #193 `programme`
row was checked directly:
the existing automated queue reader only parses `v...` release rows, so its
green tests alone cannot establish this clearance. The evidence tests check
existing WFF/AS mechanics, not an income-tax executable policy report.

No full suite, external policy engine, full-year amendment assurance, new
statutory fixture, tax engine or retained interactive IRD benchmark is
claimed by this clearance. Fresh-context checking of the new documentation
is supporting same-model evidence; its independent Claude acceptance and
new CI remain with the follow-up PR's normal review process.
