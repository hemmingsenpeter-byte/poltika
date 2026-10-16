# Task 8 benefit specifications — draft handoff

**Author/source writers:** GPT/Codex, 13 October 2026.
**Base:** `7342e528ad67b58984de5711ba2d195bdef97c67`.
**Review state:** author preflight plus supporting fresh-context GPT check;
independent Claude full primary-source final-head review remains pending.
Exact published head and actual checks are recorded in the draft PR.
No acceptance, protected-value approval or implementation clearance is given.

## Commission and expected behaviour

Task 8 / v0.3 sources-and-specification steps 3.1.1, 3.2.1 and 3.3.1, under
Pete's D11 and the 6 October restricted-capacity clarification. Pete asked
for all three drafts now. They share a completed proposed reference week,
`[2026-10-05, 2026-10-12)`, checked 13 October. The dates are a project scope
choice. No benefit week-to-year conversion or receipt apportionment is made.
The author knows the drafting rationale; this is **author preflight**, not
the independent reviewer rotation.

| Draft | Commissioned slice | Rules / unresolved monetary method |
| --- | --- | --- |
| [Jobseeker](../policy_specs/jobseeker_support/specification.md) | Single existing ordinary grant, 25+, no dependent children; excludes legacy transfer rate | JS-01–11; gross conversion and income/payment precision DEC-001/002 |
| [Sole Parent](../policy_specs/sole_parent_support/specification.md) | Single existing ordinary principal-caregiver grant; ordinary child/care route, active weekly assessment agreement | SPS-01–18; gross authority and weekly precision DEC-001/002 |
| [Supported Living](../policy_specs/supported_living_payment/specification.md) | Single adult existing restricted-work-capacity s 34 grant, no children; active weekly assessment agreement | SLP-01–13; gross entitlement and precision DEC-001 |

- Unknown grant, income, relationship, child, basis or source facts cannot
  become zero, an exclusion or an administrative determination.
- Known coverage exclusions precede `needs_review`; per-person s 18 and the
  deliberately narrower household coverage limit remain distinct.
- Ordinary payable state and a covering grant are separate asserted facts.
- Gross entitlement, scheduled rate, withheld tax and actual cash payment
  remain distinct; no result while monetary/source/approval gates are open.
- All interpretation text is draft. No `policy.yaml`, `facts.yaml`, protected
  expected cases, engine, household adapter or graph edge is added.

## Primary evidence and material gaps

SSA's current consolidation is 26 September 2026. The earlier 4 September
catalogue entries and original check dates remain for history. Author
comparisons found the scoped benefit provisions unchanged; the updated
CYPFA definition is recorded separately. The 15 October recheck below corrects
SSR to 1 October 2026 and retains the 4 September inventory as history. The 2026
Order commenced/applies to benefits payable from 1 April under cls 2–4.
Amendment Act 2026/54 commences Part 1 on 2 November and Part 2 on 1 April
2027; no post-commencement coverage is claimed.

Schedule 4 prints $372.55 (JS), $521.52 (SPS) and $424.60 (SLP adult), matching
MSD's net-M observations. The published gross maxima are respectively
$426.12, $606.69 and $489.21. Income-test deductions apply on the statutory
side. SSA ss 349–351 and ITA RD 11(3) establish the tax-dependent gross-up
authority. The original pass had not located the operative determination;
the 15 October pass below locates DET 24/03, while its complete computational
application and precision remain unreviewed. Reducing the statutory-side
amount before gross-up is the leading hypothesis subject to DEC-001, not a
settled computational sequence. Direct subtraction from the gross maxima
is not an approved alternative. The drafts explicitly stop there.

SPS/SLP normally use a **52-week income basis**, despite weekly payments;
r 205(2) permits an MSD/person weekly agreement, terminable under (3).
Their proposed weekly sub-slices require that active agreement. SLP's s 34
own-effort disregard is mandatory up to its sourced limit; SPS childcare
disregard is discretionary. Inputs must carry resolved provenance and apply
the relevant adjustment exactly once. No generic disregard is invented.

Official MSD deduction examples can corroborate a deduction substep, but do
not independently benchmark these requested gross outputs. Full gross
benchmark and precision evidence remain `MISSING_SOURCE`, named in each
decision. Pete owns any residual interpretation choice; an evidence-backed
source update can resolve a missing-source item if no choice remains.

## Review and next steps

Review the full source catalogues, statutory rule rows, period/slice refusal
contracts and decision records against dated primary legislation. The
supporting GPT check cannot approve GPT-authored policy content. Claude must
perform the full source re-derivation at the final head.

The detailed lane's decision order remains Jobseeker → Sole Parent →
Supported Living. Concurrent commissioned drafting does not approve the
later slice or clear those stage gates. Resolve gross-up/precision sources
and interpretations before the separate values/facts/cases/benchmarks PR;
only then may Claude implement an independently accepted slice. Task 8 and
Gate B remain incomplete; Tasks 9–11 still need the connected reviewed work.

## 15 October 2026 source recheck and decision options

**Scope/provenance:** GPT/Codex source-author follow-up on draft
[PR #220](https://github.com/hemmingsenpeter-byte/poltika/pull/220), observed
head `0994a0cda950d8ef2d712e35aff3a2bc573110f9`, against observed main
`63359fecfe3b6659476528da021ea0ade0023537`. Amendments were prepared in a
new detached worktree. This is not independent cross-model clearance.
GitHub's live review and inline-comment lists were empty; its only comment
was CodeRabbit's draft-review skip. No Claude finding is invented or marked
resolved. Reconcile the final branch and rerun final-head review before any
publication or acceptance claim.

### Findings and corrections

1. **P2 / proposed `SPEC_ERROR`: stale Regulations currency.** The draft
   said 4 September remained current. The official latest index retrieved
   on 15 October identifies **1 October 2026, version 219_0**. New dated
   catalogue entries and specification citations correct this. Direct
   full-text comparison finds one substantive body change: Schedule 1
   cl 33(2)'s first-review transition. [SL 2026/255](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/255/en/latest/),
   made 31 August, rr 2 and 4, commences/replaces that clause on 1 October.
   The transition concerns independent review benefits under cl 32,
   including SLP overseas; it does not alter rr 8–11, 205, Schedule 6,
   JS transitional cl 25 or Schedule 8 cl 44. No ordinary domestic amount
   is changed. A newer index date alone does not establish complete
   reference-week currency, grant continuity or approval.
2. **`MISSING_SOURCE` narrowed: RD 11(3) authority located.**
   [IRD DET 24/03](https://www.taxtechnical.ird.govt.nz/-/media/project/ir/tt/pdfs/determinations/miscellaneous/2024/det-24-03.pdf?modified=20240715225311),
   issued **10 July 2024**, cover effective **2024–25 onwards**, operative
   printed p 1 (PDF p 2), specifies the weekly M PAYE-table basis for
   payments from **2 August 2024**. The earlier statement that no operative
   determination had been located is superseded. Application to the exact
   payment/entitlement dates, table edition/components, inverse gross-up
   and all precision stages remain unreviewed. Background paras 3 and 6
   expressly distinguish payment tax from final annual tax; that background
   is outside the operative determination. Store this as conservative
   `agency_interpretation` in the existing source schema, with its actual
   legal character stated. No authority-rank/schema change or promotion is
   hidden in this source-only correction.

### Dated source and amount check, in the required order

The [Act latest index](https://www.legislation.govt.nz/act/public/2018/32/en/latest/)
still identifies **26 September 2026**. Direct official HTML retrieval was
needed after browser-tool failure; the dated Act, both Regulations versions
and the Order were read from official text. The [current Regulations](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-10-01/)
and [rates Order](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/2026-03-02B/)
were checked separately. Order cls 2–5 establish the 1 April 2026
commencement/payment applicability and replacements; the three relevant
Schedule 4 rows do not contain the published gross maxima.

| Slice / statutory locator | Scheduled amount / weekly net M observation | Published weekly gross observation | Independent source check, 15 October |
| --- | --- | --- | --- |
| JS single 25+, no children; Schedule 4 Part 1 cl 1(d) | `372.55` | `426.12` | [MSD MAP JS rates](https://map.workandincome.govt.nz/map/deskfile/main-benefits-rates/jobseeker-support-current.html), row Single 25+; table date 1 April 2026; Test 3(b) |
| SPS ordinary; Schedule 4 Part 2 cl 1 | `521.52` | `606.69` | [MSD MAP SPS rates](https://map.workandincome.govt.nz/map/deskfile/main-benefits-rates/sole-parent-support-current.html), Sole parent row; table date 1 April 2026; Test 1 |
| SLP single adult, no children; Schedule 4 Part 3 cl 1(b) | `424.60` | `489.21` | [MSD MAP SLP rates](https://map.workandincome.govt.nz/map/deskfile/main-benefits-rates/supported-living-payment-current.html), Single 18+ row; table date 1 April 2026; Test 1 |

All six observations remain **candidate documentary amounts**, with no
`policy.yaml`, statutory expected fixture or approved gross result. The
existing specs already distinguished gross/net meanings; this check confirms
them and does not derive an abated gross curve from maximum-rate pairs.
Live MAP rates state a reference date, without proving immutable historical
page content or an unbounded parameter end date.

SSA **s 338(1)–(5)** separates the seven-day payable main-benefit week from
MSD-determined instalment length and payment dates. Schedule 3 **cl 13(1),
(1A)–(3)** governs income's assessment and earning/entitlement attribution;
SSR **r 205(1)–(3), Schedule 6 items 1–2** selects one week for ordinary JS
and normally 52 weeks for SPS/SLP, with an agreement required for their
one-week determination. A project week, weekly bank payment, or stable
income does not establish an agreement. Existing specs correctly require
the agreement and distinguish unknown from known annual-basis exclusion.
No payment-date-to-entitlement-week conversion is added.

SSA **s 18** remains a restriction on the same person's own-right receipt.
The distinct partners' categories in Schedule 4 Part 1 cl 1(g) and Part 3
cl 1(d) disprove a general one-main-benefit-per-household reading. The
specs' narrower household scope is preserved. SSA **ss 34–37**, SSR
**rr 10–11**, and SLP-03 continue to require asserted MSD capacity/grant
determinations. No diagnosis, hours or clinician assertion becomes an
automated Poltika eligibility decision.

### Independent deduction workings, not gross expectations

The following transcribe only the statutory deduction bands at exact
whole-dollar chargeable income `I`, before any remaining payment, tax or
gross conversion. They are **AI-hypothesis candidate workings**, not protected
values, accepted precision rules or outputs from the simulator.

`JS: D = 0.70 × max(I − 160, 0)`.
`SPS/SLP: D = 0.30 × min(max(I − 160, 0), 90) + 0.70 × max(I − 250, 0)`.

| Chargeable `I`, NZD per assessed week | JS deduction candidate | SPS/SLP deduction candidate |
| --- | --- | --- |
| 0 | 0.00 | 0.00 |
| 159 | 0.00 | 0.00 |
| 160 | 0.00 | 0.00 |
| 161 | 0.70 | 0.30 |
| 249 | 62.30 | 26.70 |
| 250 | 63.00 | 27.00 |
| 251 | 63.70 | 27.70 |

Independent corroboration: [SPS weekly Example 1](https://map.workandincome.govt.nz/map/income-support/main-benefits/sole-parent-support/weekly-income-example-01.html)
at earnings 350 gives `0.30 × 90 + 0.70 × 100 = 97`.
[SLP personal-earnings Example 1](https://map.workandincome.govt.nz/map/income-support/main-benefits/supported-living-payment/personal-earnings-exemptions-01.html)
at earnings 400 first disregards 20, so `I = 380` and
`0.30 × 90 + 0.70 × 130 = 118`. The SLP disregard applies once; SPS's
childcare discretion is separate. These undated live examples corroborate
deductions, not 2026 gross outputs or final rounding. A matching complete
gross-entitlement benchmark remains unestablished.

Precision matters before gross-up: JS `I = 160.99` would give `0.6930`
under exact arithmetic and `0` if income is first floored. Test 1
`I = 250.99` would give `27.6930` or `27` respectively. These are **competing
calculation illustrations**, not a selected method. [JS DREW guidance](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/calculating-the-benefit-rate-01.html)
provides positive whole-dollar-flooring evidence in its estimate workflow;
its scope/aggregation stage and SPS/SLP applicability remain review questions.

### Pete's decision options and remaining gate

| Decision | Options and consequence | Current state |
| --- | --- | --- |
| Gross scope, each benefit in JS → SPS → SLP order | **A:** retain D11's full abated gross slice and complete the DET 24/03/table/rounding pack before values. **B:** explicitly narrow to ordinary zero-chargeable-income maxima; the published gross rows can support candidate cases after independent currency, category and protected-value review, but no abatement curve. **C:** expressly revise D11 to a scheduled/net-M component, separately labelled; this changes output meaning and does not satisfy the existing gross commission. | No option chosen. A preserves the existing scope; B/C require a recorded scope change. No numeric output is approved now, including at zero income. |
| Precision | **A:** require complete benefit-specific source authority for income preparation, aggregation, deduction, gross-up, final rounding and ties. **B:** if evidence remains incomplete, approve an expressly bounded whole-dollar input restriction plus any separately identified necessary assumptions; this restriction alone does not settle gross-up/final rounding. | No convention chosen. Q17 tax and AS rounding are not benefit authority. |
| SPS/SLP assessment sub-slice | **A:** retain the proposed active r 205(2) weekly-agreement contract with dated start/end evidence. **B:** commission a separate 52-week basis specification with its own caller periods and sourced rules. Neither option permits assuming an agreement from weekly payment frequency. | Pete chose A on 16 October 2026 (Q25/D44), with the separate 52-week slice later. Scope only; independent source/specification review and monetary gates remain open. The shared SPS DEC-003 below records this choice. |

DET 24/03's 31 July 2024 table reference needs a precise application review:
the linked [August 2024 IR340](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-aug-2024.pdf?modified=20250314001644)
cover ends March 2025, while [April 2026 IR340](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-apr-2026.pdf?modified=20260323203256),
printed p 3, covers 2026–27 and includes ACC earners levy in employee PAYE.
The remaining task is to verify the exact benefit-tax components and
inverse/rounding use under the determination; copying the wage deduction
or substituting annual basic income tax would introduce an unsourced method.
This is a bounded applicability question, not a declared `SOURCE_CONFLICT`
or a Pete-approved legal convention. No agency contact is authorised here.

### Validation and next handoff

Reproduced the deduction workings with Python `decimal.Decimal` directly
from the statutory bands; no Poltika engine or outside implementation was
executed to derive an expectation. For source comparison, retrieved official
HTML with `curl -L --fail -A 'Mozilla/5.0'`, extracted visible text with Python's
`html.parser.HTMLParser`, compared full body text with `difflib.unified_diff`,
and inspected each changed substantive block against SL 2026/255 rr 2, 4.
DET 24/03 downloaded PDF SHA-256 is
`987e25163d4ba227792e7900798c26082b6733dc0723b4b0d23af98fddd92028`.
Temporary retrieval files are audit working material, not a new retained
dataset or source-publication claim. Focused validation on this detached
amendment: `git diff --check` passed; all three catalogues validated against
`SourceCatalog` (16 / 17 / 20 unique IDs), preserving draft/null state and
explicit unsupported-coverage precedence; 27 relative document links resolved.
`PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q
tests/unit/policy/test_core_benefit_source_scope.py` passed **3 tests**.
The initial invocation without `PYTHONPATH=src` failed to import `poltika`;
the explicit source-path rerun above is the passing check. No new tests or
engine files were written. Independent Claude final-head review, applicable
Pete decisions, full gross benchmarks and protected-value review stay open.
Next work: complete the bounded **JS** determination/table/precision pack,
then prepare reviewed values only after its scope/source gates clear; the
later SPS/SLP implementation stage gates remain unchanged.

### JS-only gross-up follow-up, 15 October 2026

Author source check after published head
`c5ef0085827e39cbf41372d70e28e8a2d25ad929`; supporting GPT/Codex evidence,
not independent Claude clearance. The candidate week remains
`[2026-10-05, 2026-10-12)`. No amount, expected value or approval changes.

The levy question is now narrower. [ACC Act 2001, 10 July 2026](https://www.legislation.govt.nz/act/public/2001/49/en/2026-07-10/),
**ss 9(1)–(2), 11(1)(a),(2), 219(1),(3), 220(1), 221(1)(a)**, excludes
main benefits from employee earnings and establishes the earnings-based
levy/deduction context. The latest index also identifies that version.
Direct official HTML was read after web-reader failures. This is positive
statutory evidence for excluding the main benefit from employee-earnings
levy treatment; levy authority must no longer be described as wholly
missing. It does not tell us how to remove levy from an already rounded
employee-table amount.
The dated retrieved HTML SHA-256 is
`5586132230814b404d600eebadb95a0e0af12512a6722dc01b2c4fec4dfdf527`;
this identifies the observed working copy, not immutable website content.

[SSA, 26 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/),
**ss 349–351**, already supplies the inverse relationship: s 350(3) requires
the increased payment, after its determined tax deduction, to equal the
source payment; s 351 treats MSD's tax payment as benefit/income. Thus
`gross − determined tax(gross) = source payment` is source-linked. The
remaining gap is the **complete applicable tax calculation and precision**,
not absence of an inverse relationship.

[DET 24/03](https://www.taxtechnical.ird.govt.nz/-/media/project/ir/tt/pdfs/determinations/miscellaneous/2024/det-24-03.pdf?modified=20240715225311),
issued **10 July 2024**, operative printed p 1 / PDF p 2, selects the M
weekly-table rate applying from 31 July 2024 for payments from 2 August
2024. Background **5.2**, printed p 3 / PDF p 4, refers to the applicable
IR340; background **3 and 6** distinguishes payment tax from final annual
tax. Background is expressly outside the determination. These texts do not
clearly establish permanently freezing the August 2024 booklet; neither
that freeze nor substitution of a current employee deduction is adopted.
The determination follows payment date; a payment date is not inferred
from the entitlement week's endpoints.

The [August 2024 IR340](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-aug-2024.pdf?modified=20250314001644),
cover/printed p 2, limits employee pay periods to 31 July 2024–31 March
2025. Printed **pp 3–4** include ACC in employee PAYE; **p 9**, “Main job
income”, instructs use of the nearest lower earnings row and warns that
online-calculator results may differ. [April 2026 IR340](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-apr-2026.pdf?modified=20260323203256),
printed **p 3**, identifies the 2026–27 year and includes ACC in salary/wage
PAYE. Those employee-table instructions are not established as the
benefit-specific inverse/rounding procedure. [JS MAP](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/calculating-the-benefit-rate-01.html)
only gives its income-flooring instruction in the DREW estimate workflow.

Unresolved: exact benefit-tax table/formula edition and continuing currency;
fractional preparation/aggregation; inverse-solution precision; intermediate
and final cent/tie treatment; payment-date mapping; and a matching official
gross calculation. The next source request is a benefit-specific complete
calculation method plus a fractional-income worked result. Preserve the
existing gross/precision/benchmark gates. A narrower net-payment component
would require Pete's explicit change of scope; it is not a gross result.

Working-diff checks: `SourceCatalog` validates **17 unique JS entries**, the
new entry ranks as legislation, draft/null policy state is preserved, and
all **3 relative packet links** resolve. `git diff --check` passes.
`PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q
tests/unit/policy/test_core_benefit_source_scope.py` passes **3 tests**.
Only the JS catalogue and this packet were edited; final-head preflight and
independent Claude review remain required after the next source commit.

## 16 October 2026 — Q25 scope decisions and review follow-up

**Authorship:** GPT/Codex author follow-up, not independent specification
approval. Exact starting head: `712402da10682d481f14381533049008a8092fc9`;
original review base: `7342e528ad67b58984de5711ba2d195bdef97c67`. The final
published head and exact-head preflight are recorded in the PR handoff.
Main was observed at `ed39fe700532b1d22b5a7ae2a3daa44963ce9cf6`; no main
integration or conflict resolution is included in this author change.

Pete chose Q25 option (a) in D44 on 16 October, conditional on separate
records for each narrowing. This follow-up adds exactly those three:

- [SPS DEC-003](../policy_specs/sole_parent_support/decisions/DEC-003-weekly-agreement-first-slice.md)
  is the canonical shared SPS/SLP assessment-basis record: active weekly
  agreement now, a separately reviewed 52-week slice later.
- [SPS DEC-004](../policy_specs/sole_parent_support/decisions/DEC-004-s30a-care-first-slice.md)
  records s 30(a) and ordinary care without shared/split-care selection.
- [SLP DEC-002](../policy_specs/supported_living_payment/decisions/DEC-002-adult-only-first-slice.md)
  records the adult category and deliberate exclusion of under-18s.

They name Pete, his decision date, options, consequences, sources, reversal
and retained gates. Each is classed as an Assumption about model coverage;
none says an excluded recipient is legally ineligible. Existing monetary
DECs remain open. Q25 decides no rate, gross method, precision or benchmark,
including for zero income, and does not approve these draft specifications.

### Response to the existing Claude review

The [review at `0994a0c`](https://github.com/hemmingsenpeter-byte/poltika/pull/220#pullrequestreview-5529214514)
and [delta review at `712402d`](https://github.com/hemmingsenpeter-byte/poltika/pull/220#issuecomment-6186793830)
remain the independent record; the following are author changes awaiting
Claude verification, not a reviewer gate clearance:

| Finding | Author response |
| --- | --- |
| R1, scope escalation | Three separate Q25/D44 records and specification crosslinks now record Pete's choices. No new interpretation is selected by Codex. |
| R2, P2 SPEC_ERROR | SPS's governed-source input row now applies `needs_review` after known coverage exclusions, consistent with SPS-17 and calculation step 1. |
| R3, P3 | All three calculation sequences identify reduction-before-gross-up as the leading hypothesis subject to DEC-001. The premature SPS `SPEC_ERROR` label is removed; no alternative method is approved. |
| R4, P3 | JS DEC-002 explicitly labels exact-input retention as provisional evidence-preservation handling, not a decided monetary procedure. |
| R5, P3 | SPS/SLP now state D36's one-own-right-recipient-per-household limit. All three catalogues retain the couples subset and add the general household coverage row; s 18 remains a per-person legal rule. |
| R6, metadata | JS separates the latest recorded source pass from `initial_as_of` and original entry dates; SLP uses `draft_pending_review` while retaining its old specification-status string as history. |

### Bounded primary-source and author checks

A separate source reader rechecked the official dated SSA **26 September
2026**, s 30(a)–(e), ss 31–32, s 34(c), Schedule 4 Part 3 cl 1(a)–(b),
and SSR **1 October 2026**, r 205(1)–(3), Schedule 6 items 1–2, on
**16 October 2026**. Direct official HTML retrieval was needed after web-reader
failure. The review confirms the legal categories and both assessment bases;
it does not verify a monetary value or extend whole-policy currency. D44,
not those statutes, supplies authority for the narrower model coverage.

Working-tree checks passed: `git diff --check`; 17/17/20 unique source IDs
validate against `SourceCatalog`; draft status and null versions remain;
the couples and broader household rows preserve `unsupported/not_modelled`
before `needs_review`; all 36 then-existing local document links resolve.
The new links in this section are rechecked in final-head preflight.

```sh
PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q \
  tests/unit/policy/test_decision_records.py \
  tests/unit/policy/test_core_benefit_source_scope.py \
  tests/unit/semantics/test_unit_binding.py \
  tests/acceptance/test_programme_authority.py \
  tests/acceptance/test_review_queue.py
```

Result: **46 passed in 1.06 seconds**, exit 0. No new test, executable policy,
protected expected value, engine, adapter or graph edge is introduced.

The integration owner still resolves #220's conflicts and updates from main.
After integration, obtain full independent Claude primary-source review,
exact-base/final-head author preflight and the required fresh-context pass.
No cross-model approval or merge is performed by this author follow-up.
