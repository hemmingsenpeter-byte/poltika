# Income-tax source scope — fresh same-model check

- Date: 3 October 2026, Pacific/Auckland.
- Reviewed head: `cd2f1162be5aaa9ca43fe7505e0f7410791b09db`.
- Base: prepared migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Author: GPT/Codex source-writer agent.
- Reviewer: separate GPT/Codex source/evidence checker with a fresh context.
- Result: no actionable discrepancy or P1/P2 finding in this bounded draft.
  This is not independent Claude rotation, statutory approval or Pete D1.

The reviewer derived Task 7/local 0.1 requirements before reading the draft:
source-linked income types, period, annual/withholding basis and exclusions;
dated catalogue metadata; no executable parameters or approved amounts;
unverified enactment and unknown income/rounding/interaction facts gated.

## Independently checked sources

The dated official locators in the catalogue were read independently:

- Income Tax Act 2007, 4 September 2026: BB 1; BC 1–8; CE 1; CF 1; CW 33;
  DA 2; LC 13; MA 3; RD 3; YA 1; YD 1; YE 1; Schedule 1 Part A clause 1/Table 1.
  The official latest header also identifies 4 September 2026.
- Taxation (Budget Measures) Act 2024: ss 2(5), 37(1), 37(4).
- Annual Rates Act 2026 No 8: s 3 establishes the 2025–26 annual rates.
- Social Security Act 2018, 4 September 2026: Schedule 2, paragraph (a)(i)–(iv).
- Bill 344-1, IRD status and Parliament progress: retrieved proposal/select
  committee status and the recorded introduction-date difference agree.
- IRD annual calculator scope, individual rates, taxable income, IETC and
  IR340 April 2026 cover/printed p3: stated scope and update dates agree.

The [catalogue](../policy_specs/income_tax/sources.yaml) retains the exact
primary URLs, versions and pinpoints. No numerical calculator result or
future-year enactment is inferred. The population/WFF artifacts confirm that
grouping income and family-scheme income are not individual annual taxable income.

## Verification and limits

- `git diff --check 422b055..cd2f116`: passed.
- Current `SourceCatalog.model_validate(yaml.safe_load(...))`: passed, 12
  unique sources, required stated metadata present; bill/status entries rank 4.
- Source/note hashes match the committed head; note link resolves; worktree clean.
- No full-Act/future-year audit, statutory rounding, benchmark expectation,
  approved slice, annualisation or income mapping is claimed.

Claude's independent review and Pete D1 remained pending at this historical
head. The source pack is preparation for onboarding, not evidence that the
income-tax capability is done.

## Historical scope supersession (author note, 6 October 2026)

The 3 October check above applies only to `cd2f116`, including its source/note
hash statement and Schedule 2 (a)(i)–(iv) inventory. The latter was expanded
to (a)(i)–(vii) and ITA YA 1 (a)–(b) in the 5 October source refresh; the old
inventory is not the current catalogue's coverage.

## Author transcription of Claude review (6 October 2026)

Compiled by GPT/Codex from the linked Claude comment. This is the author's
transcription, pending reviewer confirmation; it is not new independent
reviewer output or a claim of review-queue clearance. The earlier same-model
review above remains the historical reviewer's record.

Claude's [independent final-source-head review](https://github.com/hemmingsenpeter-byte/poltika/pull/148#issuecomment-5990307031)
on 5 October 2026 at 07:48:25 UTC reviewed
`4e73947593ddd48fc5900f95016eeae4ee1d3d42` with no P1/P2 and recorded a
separate fresh-context `poltika-reviewer` pass on that head. Its remaining
P3s concern this historical inventory, the Parliament metadata kind and
unreproduced progress-page content. The catalogue retains those source
limitations; no numerical value, executable slice or rounding rule is adopted.

This records actual review evidence, not a review of later commits. The
final integrated head still requires author preflight, a fresh reviewer pass
recorded in the PR and current CI before merge.


## Independent Claude source-delta review — 6 October 2026

Reviewer: Claude Code `poltika-reviewer`, Sonnet alias (reported model
`claude-sonnet-5`), separate read-only context. The reviewer first derived
the source-only contract, then checked the fixed staged delta and historical
evidence. Source snapshot base: `4e73947593ddd48fc5900f95016eeae4ee1d3d42`.
Reviewed source-delta SHA256:
`1a610ced12ffe39f89e1743086c5e5248abe695b066d8a0ddffae70dbc20e47b`.

Preserved reviewer verdict: **Approve (no blocking finding)**.

The reviewer compared the author transcription to the actual historical
Claude comment, confirmed the Q5 commission evidence and heading link, and
resolved the attribution P2. The minor historical-note attribution P3 is
labelled as an author note above.

This pass covers that source delta, not later review-record/queue additions
or main integration. It provides independent evidence for the substantive
source increment; final-head preflight, reviewer evidence in the PR,
up-to-date main and green CI remain required before merge. It approves no
statutory value, executable specification or complete disposable income.
