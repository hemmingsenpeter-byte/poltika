# Three core main benefits — separate source check

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex source writer. Checker: a separate GPT/Codex agent,
  including an independently retrieving SLP subchecker.
- Base: `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Reviewed head: `59d5e4aaadf28b26c644f2da0e16b2acc6f0e38f`;
  substantive source/scope commit `cf83e16`.
- Mechanical inputs: three `policy_specs/*/sources.yaml` catalogues;
  `docs/research/task_0_2_core_benefit_scope.md`; Task 8/local 0.2–0.3;
  existing SourceCatalog and primary-source/evidence/review/IP doctrine.
- Label: separate same-model source check. This is not Claude source review,
  Pete D1, statutory-value approval or implementation acceptance.

## Expected contract before the author narrative

Each eligibility, rate-category, partner/family, income-test and interaction
claim must match a dated retrieved NZ primary pinpoint. Separate source
version from commencement, future enacted changes from current law, and
guidance/rate tables from their legislative authority. Scope proposals cannot
become approved rules, parameters or graph edges. Unknown period, rounding,
assessment and partner/carer coverage must remain explicit.

## Finding before correction

**P2 / SPEC_ERROR**, scope note line 108: the JS category inventory attributes
“at/away from parental home” to Schedule 4 Part 1 clause 1(a).

The independently retrieved [Social Security Act, version as at 4 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/)
places a single beneficiary under 20, living with a parent and whose benefit
commenced on/after 1 July 1998 in clause 1(a). Clause 1(b) covers other single
beneficiaries under 25 without dependent children. The official MSD current
category table corroborates the distinction. Correct the category labels;
adopt no monetary value. Root also retrieved and confirmed the dated Act.

## Other checks and limits

The three catalogues validate (9/10/10 entries, 29 globally unique IDs).
Ranks, dates and diff whitespace pass. Material eligibility/partner/category,
income and assessment-period, commencement and AS/WFF interaction locators
were retrieved and checked independently. The SLP checker retrieved its ten
sources separately and found no actionable discrepancy. No other actionable
finding in the examined draft material.

No statutory values, complete historical coverage, numerical rounding/net
conversion, clinical determination or administrative discretion is approved.
Primary-source gaps and D1 choices remain as recorded. No external engine was
inspected. Full runtime tests are outside this source/document-only change.

## Author response

The project manager made the narrow category correction at `b238820`. The
checker inspected `59d5e4a..b238820` and confirmed the source-backed fix,
unchanged catalogues and no new actionable finding; whitespace passes.
The historical P2 is resolved. Later changes only record checks and draft
tracking. No policy parameter,
protected case or approved interpretation is created. Task 8 stays In progress.

## Author transcription of Claude review and 6 October closeout

Compiled by GPT/Codex from the linked Claude comments. This is author
transcription, pending reviewer confirmation, not new independent reviewer
output or a claim of review-queue clearance. The historical same-model
review above remains separate.

Claude's [independent final-source-head review](https://github.com/hemmingsenpeter-byte/poltika/pull/151#issuecomment-5990307455)
on 5 October 2026 at 07:48:26 UTC reviewed
`7418c99e780bfa06f577c31e5bfcf27261eef249` with no P1/P2 and recorded a
separate fresh-context `poltika-reviewer` pass on that head. It confirmed the
future-amendment inventory, gender-neutral transfer category, per-grant
transition wording and source-linked per-person correction to local 3.4.
The earlier same-model check above is historical; it does not cover those
later corrections. The primary Claude comment is the reviewer's output;
this section preserves its identity and disposition without relabelling
the earlier GPT/Codex check as independent cross-model review.

The independent comment left two non-blocking P3s:

- R1: local 3.4's Pete-authorisation statement lacked a decision-record
  link. The 6 October closeout links the [verbatim approval record](../docs/programme/2026-10-06-pete-approvals.md#1-petes-approvals-to-record).
- R2: mixed-benefit couples remain explicitly `unsupported` pending a
  reviewed specification. The source catalogues carry that coverage limit
  as structured, regression-checked metadata, with `unsupported` ahead of
  `needs_review`; this source-only PR adds no executable gate.

Limits recorded by Claude: SPS/SLP rows were not compared field by field
in that re-review; JS rows and future-law claims were checked. The earlier
[source review](https://github.com/hemmingsenpeter-byte/poltika/pull/151#issuecomment-5986426524)
records its broader dated-primary-source checks. Rates were located, not
adopted; rounding/payment and cross-policy gaps remain open.

This records actual reviewed heads. Later main integration and the
decision-link/review-record delta require a new final-head reviewer pass
recorded in the PR, author preflight and current CI before merge.


## Independent Claude source-delta review — 6 October 2026

Reviewer: Claude Code `poltika-reviewer`, Sonnet alias (reported model
`claude-sonnet-5`), separate read-only context. The reviewer first derived
the source-only contract, then checked the fixed staged delta and historical
evidence. Source snapshot base: `7418c99e780bfa06f577c31e5bfcf27261eef249`.
Reviewed source-delta SHA256:
`b7d43ba0e9f515432536289343d4579758dcf7584c7e050ef3080f1d76074dee`.

Preserved reviewer verdict: **Approve (R1 non-blocking, for the record)**.

The reviewer compared both historical Claude comments to the labelled
author transcription, including the SPS/SLP limit, and confirmed the
decision anchor and unchanged unsupported/categorical source scope. The
record-placement convention was noted as a non-blocking P3.

This pass covers that source delta, not later review-record/queue additions
or main integration. It provides independent evidence for the substantive
source increment; final-head preflight, reviewer evidence in the PR,
up-to-date main and green CI remain required before merge. It approves no
statutory value, executable specification or complete disposable income.
