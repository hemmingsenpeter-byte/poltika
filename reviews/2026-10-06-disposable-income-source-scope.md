# Disposable-income source scope — independent review closeout

- Record date: 6 October 2026, Pacific/Auckland.
- Author: GPT/Codex. This record transcribes existing independent Claude
  review evidence and documents the author's response; it is not a new
  independent review by its recorder.
- PR: [#172](https://github.com/hemmingsenpeter-byte/poltika/pull/172).
- Reviewed head: `933a4162694a4f0b1a7c909b0b3ef878a48b8695`.
- Independent review: [Claude comment, 5 October 2026 at 07:44:57 UTC](https://github.com/hemmingsenpeter-byte/poltika/pull/172#issuecomment-5990259914).
- Inputs: [source note](../docs/research/task_0_4a_disposable_income_source_scope.md),
  its five official sources, local 0.4a and the Q5 commission, review/IP
  doctrine. Claude derived expectations first, was not blind to the PR body,
  re-read official sources, and recorded a separate fresh `poltika-reviewer`
  consistency check without web access.
- Verdict on that head: no P1/P2; four non-blocking P3s. No definition,
  statutory value, numerical comparator or coverage contract was selected.

## Expected contract and original findings

Source-scoping must distinguish complete candidate definitions, household
and policy units, survey/assessment periods, publication vintages and
unverified content. Unmodelled components and missing formula sources stay
visible. D2 definition selection and D3 adequacy remain separate decisions.

| Finding | Proposed classification | Author response, 6 October |
| --- | --- | --- |
| P3-1: DI-4 omitted its tax-estimation method and recurring-receipt convention | `SPEC_ERROR` — incomplete source scope | Added the report's Taxwell method for individual/benefit-unit tax liabilities and footnote 3's general recurring-receipt convention; footnote 4 identifies predecessor Taxmod. This is a report-method observation, with no engine implementation inspected |
| P3-2: DI-4's historical reference period could be confused with DI-5 | `SPEC_ERROR` — provenance precision | DI-4 explicitly covers 1982–2016, with latest HES 2015–16; the PDF records publication on 25 July 2017, distinguished from the URL's 19 July filename |
| P3-3: “All are primary official sources” overstated the unextracted DI-5 body | `MISSING_SOURCE` — scope limit | DI-5 is explicitly metadata only; its 2019 report-body extraction gap stays open |
| P3-4: proposed tax/benefit period references lacked traceable dependencies | `SPEC_ERROR` — traceability | Linked #148, #151 and Q5 decision draft #167; explicitly says income tax is not yet modelled in the foundation/current engine |

## Verification and remaining gates

The author re-read [MSD's 2017 PDF](https://www.msd.govt.nz/documents/about-msd-and-our-work/publications-resources/monitoring/household-income-report/2017/2017-incomes-report-wed-19-july-2017.pdf)
on 6 October: cover and PDF page 2 for publication/version; “About this
report”, PDF page 5 / printed page 1, for 1982–2016 and HES 2015–16; Section A,
PDF page 7 / printed page 3 and footnotes 3–4, for tax estimation and income
scope. These support the author response; they do not independently select
or harmonise Stats NZ and MSD definitions.

Author preflight on the prepared delta: `git diff --check` and targeted
changed-document relative-file/anchor checks exited 0. The author knows the
source rationale. No production code, protected expectation or numerical
benchmark changed, so runtime tests were not rerun for this note-only delta.

The old independent review does not cover the response commits or later
main integration. A new exact-final-head reviewer pass must be recorded in
the PR before merge, with author preflight and green current CI. No review
queue clearance is claimed by this record. The 2019 MSD report extraction,
D2 choice/coverage and income/period specifications remain outstanding.


## Independent Claude source-delta review — 6 October 2026

Reviewer: Claude Code `poltika-reviewer`, Sonnet alias (reported model
`claude-sonnet-5`), separate read-only context. The reviewer first derived
the source-only contract, then checked the fixed staged delta and historical
evidence. Source snapshot base: `933a4162694a4f0b1a7c909b0b3ef878a48b8695`.
Reviewed source-delta SHA256:
`b39467265939c490608b1cd540cc1e87e733285e6c4c7b68048fac6bcbcc0846`.

Preserved reviewer verdict: **approve (no blocking P1/P2) — snapshot-scoped only**.

The initial re-review could not render the official MSD PDF and recorded
a P2 source-access gap. The second pass read exact pages 1, 2, 5 and 7
extracted independently with pypdf and confirmed all DI-4 additions,
resolving that P2. The author-record placement and reachable Q5 provenance
were non-blocking P3s; the linked Q5 PR remains the decision record.

This pass covers that source delta, not later review-record/queue additions
or main integration. It provides independent evidence for the substantive
source increment; final-head preflight, reviewer evidence in the PR,
up-to-date main and green CI remain required before merge. It approves no
statutory value, executable specification or complete disposable income.

Public MSD PDF SHA256:
`28b0106959e0b26b2e8cd8b854bbab11be842b5b274df7e7cae47f840f8b1630`.
Selected-page text SHA256:
`6c84673b5da0b01e323d54653bfaf6d9c8acd33af1bd8f559ee38d1fcdf000b6`.
The official URL above was retrieved on 6 October 2026. An isolated
temporary environment used `pypdf.PdfReader` and
`pages[num - 1].extract_text()` for PDF pages 1, 2, 5 and 7; no repository
dependency or external policy-engine implementation was added.

Current author follow-up, 6 October 2026: merged `origin/main` at
`f9c69d8e3384f0753be482c5ee4a6564cfa5d8ea`; whitespace and two relative
file links checked (exit 0). The source note and this labelled transcription
change no executable result. Historical reviews cover their stated heads
and fixed deltas only. No review-queue row changed before #170 merged;
final-head Claude review and current CI remain outstanding.
