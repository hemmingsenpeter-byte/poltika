# PR #193 source/specification closeout and Q16–Q18 decision handoff

Date: 9 October 2026, Pacific/Auckland. Prepared by a fresh GPT/Codex source-review agent in the single independent source/review lane.

**Disposition:** the source/specification draft accurately preserves its legal and precision gates. The IR3G discrepancy is reproduced. No new actionable P1/P2 defect was found in the bounded gated draft. This is independently performed source checking but **same-model supporting review** of Codex-authored work; it does not clear ADR-0020's required full Claude primary-source/specification review, Pete's Tier C decisions or CI. Do not approve a tax policy, begin a tax engine or mark Task 7 complete from this record.

## Fixed target and authorship

| Field | Observed evidence |
| --- | --- |
| PR | [#193](https://github.com/hemmingsenpeter-byte/poltika/pull/193), OPEN, MERGEABLE, merge state BLOCKED |
| Main/base | `26cd8a6dde236f5c3df93602979f5f85de283643` |
| Reviewed head | `e50bf86d4a0f0dd2dddc17249eb4253911b0dbba` |
| Branch | `codex/income-tax-spec-20261008` |
| Semantic author | GPT/Codex, from PR attribution and all eight commits' GPT/Codex coauthor trailers; Pete's GitHub account does not establish model authorship |
| Review checkout | Detached `/private/tmp/poltika-source-review-193-20261009`; no edits to its tracked files or existing PR branch |
| Scope | Ten documentation/specification paths; no engine, API, policy parameters, facts, benchmark cases or existing protected expected values |
| Stack | Standalone source/spec delta against current main; #148 source scoping already merged |
| Live review evidence | `gh pr view`, `gh api .../pulls/193/reviews`, `gh api .../pulls/193/comments`: no GitHub reviews or inline review comments; one GPT-6 recommendation issue comment |
| GPT-6 recommendation | [8 October UTC comment](https://github.com/hemmingsenpeter-byte/poltika/pull/193#issuecomment-6069451116), explicitly proposed dispositions, not Tier C approvals |

This review is **not blind**: the assigned task, PR body and recommendation comment were available before the complete source re-derivation. The source calculations were performed separately from author fixtures; no external policy engine was consulted.

Required guidance examined includes current AGENTS/CLAUDE instructions; programme and household-lane Task 7 contracts; retained BUILD_PLAN doctrine; architecture and repository policy locations; review/test/epistemic/IP doctrine; ADR-0020/0021/0023; PETE_QUEUE, decision log, review queue; existing income-tax research/source review; PR #193's full ten-file delta and author packet; `pr-review`, `pr-review-preflight`, `new-policy`, and the primary-NZ-source-check workflow. No implementation acceptance is recommended by this source review.

## Independently checked source evidence

All following retrievals are new observations on 9 October 2026. Current agency pages are not immutable historical snapshots. Only named provisions and source questions were checked; no complete future-year amendment audit is claimed.

| Primary source/version | Locator and supporting observation |
| --- | --- |
| [Income Tax Act 2007](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/), headers explicitly as at 4 September 2026 | BB 1 uses annual taxing legislation; BC 1–6 distinguish filing status and taxable income; BC 8 separates credits and terminal tax; BD 1/3 require classification and year allocation; CE 1(1)(a) includes ordinary wages; DA 2/3 preserve express deduction overrides; YA 1's non-filing definition differs from simply not completing a manual IR3; YD 1/YE 1 support residence and April–March boundaries. |
| Same Act, Schedule 1 Part A cl 1/Table 1 | Five documentary bands/rates match the draft. Its general basic rate excludes special cl 2–14 categories, and the table computes per-dollar tax; it is not the top marginal rate applied to all income. |
| [Taxation (Budget Measures) Act 2024 as enacted](https://www.legislation.govt.nz/act/public/2024/19/en/2024-06-04/) | Sections 2(5), 37(1), 37(4): Part 4 commencement 1 April 2025; replacement table applies to 2025–26 and later income years. Application is distinct from year-specific annual authority. |
| [Tax Administration Act 1994, 4 September 2026](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/) | Sections 22D/H/I and 92 support annual-account/assessment distinctions. Section 92A(1) permits Commissioner assessments before annual enactment; s 92A(2) adjusts assessments if annual rates differ. It does not name Poltika as an assessing authority. No complete annual rounding procedure was established from these provisions. |
| [Annual Rates Act 2026 No 8 as enacted](https://www.legislation.govt.nz/act/public/2026/8/en/2026-03-30C/) | Section 3 sets rates for **2025–26**, not 2026–27. |
| [Bill 344-1](https://www.legislation.govt.nz/bill/government/2026/344/en/latest/), as introduced | Clause 3 proposes 2026–27 annual rates. The official page remains a Bill; no enactment is inferred. |
| [IRD Bill status](https://www.taxpolicy.ird.govt.nz/bills/2026-fbt-simplification-tax-bill) and [Parliament progress](https://bills.parliament.nz/v/6/ae9d3517-66d6-4a30-c155-08df0eed0d02?Tab=history&lang=en) | IRD still labels its observation 15 September 2026/first reading. Parliament's retrieved page identifies 344-1, select committee as current and no dated Royal Assent. The introduction-date difference (9 versus 10 September) remains recorded; neither supplies enacted law. |
| [IRD individual rates](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals) | Five bands match; heading applies from 1 April 2025; update label 3 June 2025. Guidance cross-checks rates, not annual enactment or all-period amendment coverage. |
| [IRD yearly calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income) | Basic yearly tax needs taxable income and excludes credits, previously paid tax and ACC. Page update 1 April 2025. No interactive numeric result was run or retained. |
| [IRD IR3G 2026 PDF](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1---ir99/ir3g/ir3g-2026.pdf?modified=20260331185539) | Cover revision August 2026; printed p7 identifies 2025–26; printed pp43–44 contain the disputed table and arithmetic instructions. PDFKit rendering and visual inspection confirm the cells. |

Retrieval caveat: the Income Tax Act root redirected to a part under `latest`; its header explicitly remains 4 September 2026. Dated parts B/D/Y/schedules returned HTTP 500, so their official `latest/parts/...` pages were fetched and each header independently checked as 4 September 2026. Dated Part C was directly reachable. This is a recorded fallback, not an assumption that `latest` permanently means that date. The TAA, 2024 Act, annual-rates Act and Bill were retrieved directly at the URLs above. The web reader failed for several legislation URLs; direct official HTTPS retrieval worked.

The prior catalogue limitation that Parliament's client-rendered progress could not be independently reproduced can be supplemented by this newly successful web retrieval. Do not overwrite the historical limitation as if the earlier reviewer had accessed it.

Temporary source evidence is under `/private/tmp/poltika-source-evidence-20261009`, with `evidence-manifest.json`, direct HTML/PDF, extracted text and page renders. These are review scratch artifacts, not repository datasets or promoted Source Archive inputs.

## Q18 exact reproduction

Observed PDF SHA-256: `4b0f2ffbc831c0aa88235d2c0ce986fa80b234be8f3fb6ac17ee1ab377f71b99`, exactly matching the author packet. Printed p43, the fourth ordinary-tax row, shows A=`78,101`, B=`.33`, C=`15,650.50`; p44 computes `(taxable income − A) × B + C` before separate PIE/credit adjustments. The neighbouring A values are `0`, `15,600`, `53,500`, `180,000`. The other cumulative C values match independently summed bands.

The enacted table gives these accumulated **unrounded arithmetic** values:

```text
15,600 × .105                                      = 1,638.000
1,638.000 + (53,500 − 15,600) × .175                = 8,270.500
8,270.500 + (78,100 − 53,500) × .300                = 15,650.500
15,650.500 + (180,000 − 78,100) × .330              = 49,277.500
```

Thus the disputed row subtracts one additional whole dollar while retaining tax only through $78,100. Independent Python Decimal arithmetic, with no quantisation, reproduces:

| Whole-dollar taxable income | Statutory band sum, unrounded | IR3G worksheet arithmetic | Worksheet minus band sum |
| --- | --- | --- | --- |
| 78,100 | 15,650.500 | 15,650.500 | 0.000 |
| 78,101 | 15,650.830 | 15,650.500 | -0.330 |
| 100,000 | 22,877.500 | 22,877.170 | -0.330 |
| 180,000 | 49,277.500 | 49,277.170 | -0.330 |
| 180,001 | 49,277.890 | 49,277.890 | 0.000 |

The worksheet therefore produces a $0.72 increase from $180,000 to $180,001 rather than the next row's $0.39 marginal increment. This localises the arithmetic discrepancy to the fourth subtraction threshold; it does **not** establish an official correction or legally rounded liability. No fractional taxable-income interpretation is needed for these whole-dollar probes. Q17 remains unresolved, and this guide cannot benchmark the commissioned 2026–27 component merely because some rates coincide.

The reproduction is review evidence, not an approved `spec_cases.yaml` or `benchmarks.yaml`, and changes no protected expectation.

## Decision-ready dispositions (all proposed)

| Question / existing record | Evidence and proposed disposition | Implementation effect | Remaining authority |
| --- | --- | --- | --- |
| **Q16 / DEC-001** | Recommend allowing an explicitly conditional **internal** 2026–27 mathematical basic-rate lane using independently reviewed applicable **enacted** Schedule 1 legislation. Retain annual legal finality as `needs_review`. Section 92A explains the Commissioner route; it does not make Poltika's output an official assessment. Bill 344-1 stays proposed-law context. | Later internal arithmetic/testing may advance only after Pete expressly revises D11 and the required source review. If current outcome contracts cannot express the conditional status without suggesting authoritative `calculated`, keep the value internal and all public numeric annual-tax results gated. No PAYE, ACC, credit, refund, terminal-tax or full disposable-income claim. | Pete decides the D11/component authority revision; Claude independently re-derives BB1/Schedule1/s92A and enactment state at the final head. Enactment/finality and full-period amendment coverage remain open. |
| **Q17 / DEC-002** | Recommend exact Python `Decimal` arithmetic from exact transport, explicit bands and reproducible unrounded traces. Decimal context must be sufficient for the admitted input range; using Decimal alone is not proof of exactness. Keep fractional-dollar legal treatment, intermediate/final rounding and ties unresolved. | A later approved internal mathematical contract can preserve cents and exact traces. Do not select floor-to-dollar, half-up, half-even, truncation or borrowed PAYE/FBT rules. Legally rounded/public statutory output, including nominal zero, remains gated under current D11/spec. Conditional values cannot enter disposable-income, EMTR or fiscal headlines. | Pete commissions or identifies a dated authoritative annual basic-tax method; Claude reviews it independently; Pete accepts legal precision only once supported. Bounded search remains `MISSING_SOURCE`, not a proof no source exists. |
| **Q18 / DEC-003** | Confirm the observed arithmetic mismatch as a proposed `SOURCE_CONFLICT`. Recommend excluding the disputed fourth row and any results derived from it from authoritative benchmarks; retain original source/version/hash. Seek IRD clarification or a separately retained period-matched official comparator. | Independently derive later statutory expectations from reviewed enacted sources, subject to Q17. No quiet repair of the IRD cell and no earlier-year guide promoted into a 2026–27 benchmark. Unaffected neighbouring rows may support diagnosis but are not newly approved benchmarks here. | Pete confirms the conflict disposition/benchmark policy; Claude repeats source and arithmetic checks on the final source head. Official clarification/comparator and precision acceptance remain pending. |

The dedicated precision search checked the listed legislative provisions and guidance plus primary-domain searches for annual taxable-income cents/rounding. It found historical worksheet formatting and payroll-specific conventions but no complete applicable annual basic-tax procedure. An input box displaying `.00` or an output box with cents does not independently settle truncation, rounding or ties. No broader negative legal conclusion is made.

## Decision PR C duplicate check

At verified main `26cd8a6`, D11 is the existing approved scope commission; Q16–Q18 and DEC-001/002/003 are not yet present on main. They are already correctly recorded **as open** in #193. All three records say Pete owns the decision, decision date is none, and status is open/`needs_review`. The GPT-6 comment makes recommendations without recording approval. The live recent PR inventory contains no separate approved tax-decision PR, and no later approved D11 revision was found in the decision log.

Therefore do not create duplicate DEC identifiers, label these recommendations approved, or replace their open status. Decision C can be a bounded **supplementary evidence/recommendation record** referring to the existing #193 records. Once Pete decides, update those same DEC/Q records and record the dated authority, instead of creating competing interpretations. If a separate C PR is needed before #193 merges, use GitHub links to #193's documents so current-main relative links do not claim files already exist. A source-evidence record can preserve pending dispositions; it does not clear #193's independent reviewer row.

Proposed short decision text ready for Pete:

> Q16: permit a separately labelled internal conditional basic-rate calculation from reviewed enacted sources, while annual legal authority remains `needs_review`; expressly revise D11 only for that internal boundary. Q17: permit exact internal Decimal traces, while fractional-dollar legal treatment and statutory rounding/ties remain pending source-backed acceptance. Q18: quarantine the reproduced disputed IR3G row and its derived results as benchmarks; commission clarification or a reviewed period-matched comparator. These decisions do not approve an executable tax specification, legal finality, protected expected values or Task 7 completion.

This paragraph is AI-authored proposed project disposition, not quoted law or recorded Pete approval.

## Verification on the reviewed head

```sh
# cwd: /private/tmp/poltika-source-review-193-20261009
PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q \
  tests/unit/policy/test_decision_records.py \
  tests/unit/engines/assurance/test_evidence.py \
  tests/acceptance/test_review_queue.py
# 18 passed in 10.44s; exit 0

git diff --check 26cd8a6dde236f5c3df93602979f5f85de283643...HEAD
# clean; exit 0
```

The committed source catalogue validates with the current `SourceCatalog`: 14 unique entries; all four source IDs used in IT-01–IT-08 resolve; annual authority, precision and full-period amendment coverage remain `needs_review`. The policy directory contains only `sources.yaml`, `specification.md` and three open DEC records. Tracked checkout remains clean. Existing local dependencies were reused; nothing installed.

At live CI observation, `test`, `pip-audit`, `Bandit (python)` and `zizmor (actions)` were QUEUED; snapshot guard, links, source currency, statutory-path guard and pilot-image were SUCCESS. `image-inputs` succeeded; scheduled-only publisher/external-report jobs were skipped. This is not final green CI. The security/maintenance lane owns runner diagnosis; no identical job was rerun by this source lane.

No full pytest, Ruff/mypy rerun, engine policy evidence-coverage pass, new statutory fixture, interactive IRD calculator benchmark, external-engine comparison or tax implementation was performed. For this docs/spec-only change the focused checks substantiate documentary mechanics; mandatory final-head CI and full independent Claude source review still apply.

## Gates and smallest next action

1. **Independent reviewer: Claude Code.** A fresh-context full `pr-review`, with primary-source re-derivation, must cover final head `e50bf86...` or the actual later reviewed head. It may satisfy both reviewer gates for this Codex-authored policy-spec work. This Codex report cannot clear that gate. Update `review_packets/review_queue.md` only from actual Claude evidence.
2. **Author owner: existing Codex source branch owner.** The existing packet records author preflight at corrected source head `86f48e1`, while actual PR head `e50bf86` includes later packet metadata. Those checks are supporting source-head evidence, not a record that the author preflight covered the actual final head. This report reruns the focused checks at `e50bf86`, but is not the author’s recorded preflight. The owner must record the final-head author pass before acceptance. Supplement rather than duplicate the source/DEC evidence, preserve all gates, and renew preflight/review after any semantic edit. A conflict-free identical-diff mechanical main update uses ADR-0020's documented exception only when its conditions are proved.
3. **Pete: Tier C.** Decide Q16's limited D11 revision, Q17's source commission/precision acceptance and Q18's conflict disposition through dated existing records. Until then they remain proposed/pending. Accepting a gated draft does not promote its interpretations into approved Rules.
4. **Merger: authorised Claude coordinator, after current CI and required review.** Codex does not approve or merge its source work. A gated documentation merge, if accepted within existing authority, is separate from approved-specification exit criteria; every unresolved interpretation stays visible. Do not claim #193 ready for merge while its reviewer row or CI remains open.
5. **Programme:** Task 7 and Gate B remain incomplete. Next implementation stays Task 5's bounded unit/period mapping patch, then reviewed Task 6. No tax engine starts in this closeout.

_Generated by GPT/Codex; same-model supporting evidence only._
