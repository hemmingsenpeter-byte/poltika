# Phase B disposable-income and incentive-method decision pack

Checked 15 October 2026, Pacific/Auckland. Author: GPT/Codex.
Base: `63359fecfe3b6659476528da021ea0ade0023537`.
**Candidate / needs_review.** This develops the retained [#172 comparison](task_0_4a_disposable_income_source_scope.md);
it selects no D2 definition, approves no statutory amount and authorises no
implementation. D2/D3 and protected-value acceptance remain Pete's. New
method choices are AI hypotheses pending independent Claude review; example
inputs are Scenarios. Existing Q16–Q18 and Q10 decisions are retained.

## Dated primary inputs

All except DI-4 were retrieved on 15 October. HTML publication dates below were read
from Stats NZ's `pageViewData` payload, since its browser shell omits the body.

| ID | Official version / locator | Bounded use |
| --- | --- | --- |
| DI-1 | [HILS concepts](https://www.stats.govt.nz/methods/measuring-child-poverty-in-the-household-income-and-living-survey-concepts-and-definitions/), 12 February 2026; “Income definitions”, “Household”, “Disposable household income” | Whole candidate accounting definition and membership; statistical method, not tax law |
| DI-2 | [June 2025 technical appendix](https://www.stats.govt.nz/methods/child-poverty-statistics-year-ended-june-2025-technical-appendix/), 26 February 2026, including 11 August and 29 September notices; “Reference and collection period”, “Steps to create household equivalised disposable income”, “Note on determining income-sharing unit”, “Working for Families data” | Collection/reference periods and methodological limits; no new conversion permission |
| DI-3 | [HILS correction notice](https://www.stats.govt.nz/reports/error-notification-for-household-income-and-living-survey-hils-data-for-year-ended-june-2025/), 29 September 2026; “Next steps”, “Important information for data users” | Original and corrected releases must be distinguished; qualification-broken-down data remains unusable pending correction |
| DI-4 | [MSD 2017 report](https://www.msd.govt.nz/documents/about-msd-and-our-work/publications-resources/monitoring/household-income-report/2017/2017-incomes-report-wed-19-july-2017.pdf), published 25 July 2017; PDF pp 5, 7 / printed pp 1, 3, footnotes 3–4 | Retained #172 historical comparison and independent [Claude review](../../reviews/2026-10-06-pr172.md); **not freshly reverified in this pass** |
| DI-5 | [MSD 2019 report](https://www.msd.govt.nz/documents/about-msd-and-our-work/publications-resources/monitoring/household-income-report/2019/household-incomes-report-2019.doc), linked by the [1982–2018 index](https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/monitoring/household-incomes/household-incomes-1982-to-2018.html) | Index reconfirmed; Word download retrieved, but body conversion still fails. **MISSING_SOURCE** for its detailed method |
| IM-1 | [Treasury AN 25/01](https://www.treasury.govt.nz/sites/default/files/2025-01/an25-01.pdf), 23 January 2025; PDF pp 3–4, 18–19 | Officially published research, authors' views; EMTR concept, weekly perturbation/annual response, family unit, illustrative PTR/RR definitions. Not current statutory parameters or a period-matched policy benchmark |

No external policy-engine code, tests or values were inspected. The Treasury
paper is used for its published measure definitions and method examples only.

## D2: proposed complete candidate, for selection

Candidate **HILS disposable household income before housing costs**, without
equivalisation. For a common reference interval P:

`D(H,P) = sum over source-compatible members aged 15+ of
  [personal income received(P) + tax credits(P) - ACC levy(P) - tax payable(P)]`.

This is a transcription of DI-1/DI-2's accounting structure, not an approved
Poltika formula. DI-1 includes employment, self-employment, investments,
pensions, government assistance, regular transfers and listed irregular
receipts. Its credits include WFF/IETC. Broader receipts cannot be omitted
from a total merely because the first policy slices do not model them.

| Contract field | Candidate and consequence |
| --- | --- |
| Gross/net | Count each receipt once. A gross taxable benefit plus its attributable tax differs from a net benefit; subtracting tax again from a net payment double counts the deduction. An entitlement is not automatically income received |
| Included support | Main benefits and AS fall within DI-1's listed government-assistance categories; add a WFF credit once, independently of its payer. An inclusion in disposable resources does not establish another policy's income-test edge |
| Tax | Basic salary/wage tax alone is incomplete tax payable for broader income. ACC and IETC are not implemented. Keep these coverage gaps visible |
| Household/person | Aggregate source-compatible members, including unrelated residents who share facilities. A WFF family or AS claimant unit does not prove statistical membership; the existing record has no age field establishing the 15+ set |
| Period | DI-2 collects interviews July–June and asks about each respondent's preceding twelve months. The collection year is not one shared tax year. A fixed April–March scenario would be an explicit modelling adaptation requiring approval |
| Excluded operations | Housing-cost subtraction, equivalisation, inflation adjustment and poverty thresholds are separate measures. Capital/receipt classifications must follow the selected whole definition, not a convenient recurring-income subset |
| Missing/unsupported | Unknown necessary income/tax/membership/period facts prevent a complete total. Known required components outside model scope remain uncovered/unsupported. A proved zero must have its own scope/period evidence; absence is not zero |

DI-2's allocation of annual WFF records across tax years is a statistical
estimation method for received income, not authority to prorate a statutory
entitlement. Its administrative-data imputation of absent WFF returns is
also not Poltika's missing-input rule. Q10/D32 still prohibit hidden
apportionment. No `weekly × 52`, `annual ÷ 52` or calendar-day conversion is
approved here. A conversion explicitly prescribed for one policy parameter
does not authorise a general cashflow conversion.

**Pete's decision options after Claude source review:**

| Option | Consequence / remaining gate |
| --- | --- |
| Adopt DI-1/DI-2 whole as the target definition | Current official definition, with an explicit component/coverage register. Execution remains blocked until membership, received-versus-entitled amounts and common-period mappings are reviewed. Incomplete results cannot be labelled complete HILS disposable income |
| Adopt the retained DI-4 historical recurring-cash concept | Requires completing its component map and explaining historical-purpose limits and differences from current HILS; #172 did not establish a complete executable contract |
| Prefer the later DI-5 MSD definition | First obtain a reliable readable report body and independent method review. Metadata cannot choose its component/period rules |
| Defer selection | Continue source/specification work and component reconciliation only; no canonical disposable-income total |

These alternatives do not choose D2 for Pete. Whichever is selected, record
the exact publication, membership, period convention and full component list.

## Independent accounting examples

All inputs below are hypothetical same-period annual NZD amounts supplied
as Scenario values, **including tax and levy**. They are not claims about
what any New Zealand household owes or receives, and are not statutory
spec/benchmark fixtures. They test an accounting identity only.

| Case | Independent derivation | Candidate result |
| --- | --- | --- |
| One source-compatible adult | wages 40,000 + gross benefit 5,000 + non-taxable receipts 2,000 + credits 3,000 − tax 8,000 − levy 600 | 41,400 |
| Two eligible household members | prior result 41,400 + (second person's income 25,000 − tax 3,500 − levy 400) | 62,500 |
| Missing levy or unresolved IWTC | A required deduction/credit has no amount | No complete total; retain the independently available components |
| Annual wages with only one AS week | Periods differ; no approved conversion covers the remainder | No common-period total |

## D3: reproducible EMTR proposal

IM-1 measures changes in one non-dependent earner's wages while accounting
for effects on the family. It uses a one-dollar **weekly** wage/salary
increase and the change in **annual** family take-home income (p 4). Its
family is the WFF economic unit; student-loan repayments are excluded
(p 3). This is a methodological precedent, not approval to infer missing
annual/weekly mappings in Poltika.

Proposed finite-difference definition:

`EMTR(g,h;P) = 100 × [1 − (D(g+h;P) − D(g;P)) / h]`, with `h > 0`.

Here **h is the increase in that earner's gross earnings over P**, not the
change in total household gross income after benefits respond. Both runs
must share a reviewed P. The numerator includes every dependent change in
tax, levy, credits and transfers in the agreed resource definition. In a
component decomposition it is equivalently
`100 × (Δtax + Δlevy − Δtax_credits − Δother_transfers) / h`, where tax
credits and other transfers are disjoint same-period resource components,
only where coverage and the accounting identity are complete.

Proposed fixed facts: other adults' income, household membership,
relationships, housing costs/area, assets, child and medical assertions,
policy/version/source dates and other eligibility facts. Recalculate all
sourced dependent amounts. An earnings-only path must not infer changed
hours, work eligibility or medical capacity. A separate hours path requires
an explicit wage and reviewed hours-dependent eligibility rules.

**Step/period options for Pete after source review:**

| Option | Meaning and limit |
| --- | --- |
| Annual h = NZD 1 | Compatible with Q17 whole-dollar input precision for the tax-only slice. It remains a partial tax change, not a complete household EMTR while transfers/ACC/periods are unresolved |
| Weekly h = NZD 1 with a reviewed annual income path, following IM-1 | Appropriate methodological candidate for a connected family response. The actual annual earnings increment must come from explicit dated earnings/path inputs or an approved conversion, not an assumed multiplier |
| Additional larger whole-dollar steps | Sensitivity/interval results must name both endpoints and h; never relabel their interval average as a local derivative |

Boundary requirements: evaluate `(b−1,b)`, `(b,b+1)` and `(b−1,b+1)` in the
policy's own units at every approved tax or abatement boundary; use exact
candidate h in the denominator. Q17 refuses fractional taxable inputs.
For a cliff report the endpoint change and one-sided intervals separately;
do not smooth, clip to 0–100%, interpolate or silently change eligibility.
Negative or above-100% results can be mathematically valid. Unknown at one
endpoint prevents a complete rate; unsupported outranks needs_review.

Method examples (not current-policy benchmarks): IM-1 p 18's extra dollar
with 0.30 tax and 0.40 withdrawn support gives `1−0.30−0.40=0.30` retained,
so **70%**. A hypothetical tax-only 0.30 deduction gives **30% partial
change**, not a claim of zero transfer change. A hypothetical cliff losing
9.20 net income for one extra gross dollar gives **1,020%**; preserve the
cliff and interval label. The [independent Decimal script](../../review_packets/phaseb_income_methods_20261015.py)
reproduces these examples without importing or executing the simulator.

## Other measures and explicit limits

| Measure | Supported definition / consequence |
| --- | --- |
| Statutory marginal tax rate | Rate on the next dollar of taxable income; not the combined EMTR |
| Component withdrawal rate | `−Δcomponent / Δspecified earnings`, explicitly naming component, input definition and units; an AS-only or WFF-only profile does not become a household EMTR |
| Participation tax rate | IM-1 p 18 compares entering work: `100 × [1 − (D_work − D_out) / gross earnings from work]`. Its illustrative 800 versus 600 disposable resources and 1,000 earnings gives 80%; endpoint/grant transitions are outside today's established-grant slices |
| Replacement rate | IM-1 p 18 illustrates out-of-work resources relative to in-work take-home resources: 600/1,000 = 60%. Exact resource basis, household scope and valid transition still need review; no automated loss-of-work/grant decision |
| Effective wage | IM-1 p 19 relates gross hourly wage and retained share. Requires a reviewed hours path and costs convention; not proposed for this first implementation |

Do not select adequacy lines, behavioural responses, poverty rankings,
student-loan treatment beyond the cited method or wider population measures
from this pack. D3 approves order (EMTR first), not these unreviewed details.

## Reproduction and handoff

Run `python3 review_packets/phaseb_income_methods_20261015.py` for offline
Decimal workings. Optional `--sources-dir /private/tmp/<chosen-directory>`
downloads the five fixed official URLs and preserves raw bytes/Stats payloads;
record the actual retrieval date and hashes on each rerun. It never reads a
Poltika engine. Raw source hashes observed in this pass:

| File | SHA256 |
| --- | --- |
| HILS concepts HTML | `3e313568fdeb24c629fbfdfaa96700ee97be8621ec16cdbf9fc4980cb27b876f` |
| HILS appendix HTML | `2f0b4681a9edd08127fb430670e43e9dd0f381379a2c5984c5ff6708057d9018` |
| HILS correction HTML | `99041e5ff1c7d3adbac71a910414a21abf2e53489b8bcb291313112af35e4843` |
| Treasury AN 25/01 PDF | `3cc2f5a9adf2901ea27fc0d1c546c330c103ed09285b34174f7e853f7627d45b` |
| MSD 2019 Word | `85c438042f95acbc3fe7e24cbcf8aa6161bb4bb19be46d1a2af653d3aa1e34b1` |

MSD conversion was explicitly checked: automatic `textutil -convert txt`
emitted binary-like data, while `textutil -convert txt -format doc` reported
the input was not in the correct format. Neither output verifies the body.
Do not close DI-5's MISSING_SOURCE from a successful download or exit code.

Next: independent Claude source/method review, then Pete's recorded D2 and
D3 choices and a reviewed period/coverage contract. Only then derive
protected reconciliation/threshold cases and review Claude's implementation.
This packet cannot clear Gate B; that requires a supported calculated output
feeding a dependent policy, trace/replay evidence and complete named gates.
