# Jobseeker Support — single established-grant weekly slice

**Programme:** Phase B Task 8; `BUILD_PLAN_v0_3.md` 0.2 / 3.1.1.
**Author/source check:** GPT/Codex, 13 October 2026, Pacific/Auckland.
**Status:** `specification_approved` (Pete, 16 October 2026, D47: rules, coverage, outcome precedence and gates for this first slice; no values, policy version, cases or engine, and no gross amount until DEC-001/002 have a sourced method). **Policy version:** `null`.
**Scope authority:** Pete D11, 5 October 2026; D36 preserves the first-slice
household coverage limit. This document adds no executable policy or values.

The proposed component is `jobseeker_support_gross_weekly_entitlement` for
one identified single beneficiary aged **25 or older**, without dependent
children, on an existing ordinary grant. The chosen assessment week is
**[2026-10-05, 2026-10-12)**. Those endpoints are a project choice under D11,
not a statutory definition of every benefit week. Income must already be
resolved for that exact policy week; this draft does not allocate receipts,
annualise wages, divide by spell length or prorate a partial grant.

All AI-authored interpretations below remain **AI hypotheses** pending the
Epistemic Constitution's source, independent-review and Pete decision gates.
D11 approves the slice and gross output meaning, not any rate, precision
method, expected result or implementation. The gross conversion and precision
gaps in [DEC-001](decisions/DEC-001-gross-entitlement-conversion.md) and
[DEC-002](decisions/DEC-002-income-and-payment-precision.md) block promotion
of the monetary procedure. A source-linked draft is not an approved Rule.

## Dated evidence and output meaning

The current official Act index checked on 13 October identifies the
**26 September 2026** consolidation. It supersedes the catalogue's preserved
4 September source observation for this assessment. The full extracted-text
comparison found one substantive change: Schedule 2's `CYPFA order or
agreement` definition adds the Oranga Tamariki Act s 283(na) reference. The
scoped Jobseeker provisions are unchanged. A **15 October 2026 recheck** corrects
the Regulations authority to **1 October 2026**, recorded as
`jobseeker-support-social-security-regulations-20261001`; the earlier
4 September observation is retained as history. The amendment changes
Schedule 1 cl 33(2)'s transitional review deadline; comparison finds rr 8–11,
205, Schedule 6 and the JS income transition unchanged. Legislation was retrieved directly from
official HTML with a browser user agent after the web tool failed; MSD MAP
pages were retrieved separately. New checks are author observations, not an
extension of [PR #151's independent source review](../../reviews/2026-10-06-pr151.md).

The proposed legal review interval is **[2026-09-26, 2026-11-02)**, containing
the selected week. Its end is a conservative coverage boundary: Amendment
Act 2026/54 s 2(1) commences Part 1 on 2 November. It does not establish that
this adult's rate expires then. No week outside the selected week is supported
by this draft, and no cross-November or full-year assurance is claimed. The
completed week precedes the 13 October source check; whole-week amendment
coverage still requires independent review before approving a monetary rule.
([Act](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/),
[Regulations](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-10-01/),
[Amendment Act s 2](https://www.legislation.govt.nz/act/public/2026/54/en/2026-09-03/))

Gross entitlement is distinct from the Schedule 4 rate, net M payment,
actual bank receipt and household disposable income. Schedule 4 Part 1
cl 1(d) prints **$372.55 a week**. The 2026 Order amends that same amount;
MSD's table labels $372.55 as net after M tax and **$426.12** as gross.
MSD's income-assessment examples subtract abatement from a **net** maximum.
Sections 349–351 provide a tax-on-benefit mechanism, including a gross-up
relationship and treating tax paid under s 350(2) as benefit income. These
sources do not establish a complete arbitrary-income gross conversion here.
In particular, `426.12 − 0.70 × excess_income` is not a supported gross formula.
([Act ss 349–351; Schedule 4 Part 1](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/),
[MSD rates](https://map.workandincome.govt.nz/map/deskfile/main-benefits-rates/jobseeker-support-current.html),
[MSD assessment examples](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/examples-of-income-assessment-01.html))

The 15 October recheck located **IRD DET 24/03**, issued 10 July 2024,
under RD 11(3). For payments from 2 August 2024 its operative determination
selects the M rate in the weekly PAYE tables applying from 31 July 2024.
This supplies previously unlocated authority, not a reviewed inverse gross-up
or precision procedure. Exact table edition/application, payment-date linkage,
levy treatment and rounding still need review; DEC-001 remains open.
([determination, printed p 1](https://www.taxtechnical.ird.govt.nz/-/media/project/ir/tt/pdfs/determinations/miscellaneous/2024/det-24-03.pdf?modified=20240715225311),
[15 October evidence and options](../../review_packets/task8_benefit_specifications.md#15-october-2026-source-recheck-and-decision-options))

## Input and outcome contract

These are proposed meanings for the later fact catalogue and household
mapping, not new runtime fields. A caller's verified assertion is a **Scenario**;
it does not become an administrative Fact because Poltika accepts it.

| Required input | Meaning and boundary | Grounding |
| --- | --- | --- |
| Person and policy identity | One identified beneficiary, requested component and exact week; future approved policy revision required | JS-01/02; repository identity contract |
| Age and category | At least 25 throughout the week; single under the Act's relationship rules; no policy-specific dependent children; not the cl 1(c) 2013 transfer category | JS-03; s 8, Schedule 2, Schedule 4 Part 1 cls 1, 7 |
| Existing grant and route | Ordinary s 20 grant established and covering the whole week; residential and other grant requirements asserted as resolved | JS-04; ss 16, 19–28 |
| Payment state | Ordinary rate throughout; no suspension, cancellation, sanction, stand-down, special rate, hospital/absence or discretionary modification | JS-04/05; s 17(3) and stated coverage exclusions |
| Income classification | Non-negative exact NZD chargeable income independently established under Schedule 3 and relevant exemptions; ordinary earnings only in this slice | JS-06; Schedule 3 cls 2–10, 13–14 |
| Income period and charging basis | Amount represents the selected policy week; weekly basis and any relevant grant transition resolved; receipt date alone insufficient | JS-07; r 205, Schedule 6, Schedule 1 cl 25 |
| Other benefits/status | No concurrent own-right main benefit, NZ Super or veteran's pension for this person; household first-slice limit separately known | JS-10; s 18; D11/D36 |
| Source, precision and gross-conversion states | Approved rules/values for this exact component and period before an authoritative number | JS-05/08/09; DEC-001/002 |

The exact input is chargeable income **before income tax**, with its period
and provenance. It is not net wages, gross household income, annual taxable
income, WFF family-scheme income or AS chargeable income. The caller must
establish classification and allocation; this component cannot infer them
from the amount. Known zero requires an affirmative resolved-income assertion.
Income or grant spans that merely overlap the week do not suffice.

Known cases outside the slice give `unsupported` / `not_modelled`, before
`needs_review`; a directly established statutory exclusion is labelled
`evidenced_exclusion`. Unknown required facts give `needs_review` with named
missing facts. Conflicting assertions give a named contradiction or the
existing household validation refusal; they are never reconciled silently.
Unapproved gross conversion, precision or whole-week source currency gives `needs_review` /
`MISSING_SOURCE`, with **no amount**, including known-zero-income cases.
Malformed numeric transport is validation failure, not missing income or zero.
These outcome conventions come from repository doctrine and the onboarding
contract, not from the statute's eligibility language.

## Source-linked rule map

IDs resolve in [sources.yaml](sources.yaml). Each proposed legal row identifies
primary legislation; separate operational material corroborates or exposes
a gap. Documentary candidates below are not adopted parameters.

| Rule | Proposed interpretation / boundary | Primary source and locator | State |
| --- | --- | --- | --- |
| JS-01 | Calculate one person's existing-grant entitlement; do not determine a new application, work capacity, exemption or medical eligibility | `jobseeker-support-social-security-act-20260926`: ss 8, 16, 19–28 | Draft; administrative route/status asserted |
| JS-02 | Exact selected week inside the pre-2 November review window only; no inferred historical/future coverage | `jobseeker-support-social-security-act-20260926`; `jobseeker-support-future-jobseeker-as-amendment-2026`: s 2(1), ss 4–12 | Draft; endpoints are project design; whole-week source review pending |
| JS-03 | Apply Part 1 cl 1(d) only after excluding the younger and legacy-transfer categories and dependent-child/relationship branches | `jobseeker-support-social-security-act-20260926`: Schedule 2; Schedule 4 Part 1 cl 1(a)–(d), cl 7; s 8 | Draft; single 25+ alone does not exclude cl 1(c) |
| JS-04 | Grant, appropriate rate and amount paid are different; temporary income reducing payment to zero need not end an otherwise qualifying grant | `jobseeker-support-social-security-act-20260926`: s 17(1),(3); s 24(1),(2); ss 20–28 | Draft; temporary-period eligibility remains asserted |
| JS-05 | Statutory cl 1(d) maximum is $372.55 weekly, subject to Test 3; Order adjustments apply to benefits payable from 1 April 2026 | `jobseeker-support-social-security-act-20260926`: Schedule 4 Part 1 cl 1(d); `jobseeker-support-rates-order-2026`: cls 2–5, Schedule 1 Part 1 cl 1(d) row | Documentary candidate; net/gross relationship JS-09 |
| JS-06 | Income is policy-specific and before income tax; exclusions/overrides matter, including statutory benefits and WFF credits | `jobseeker-support-social-security-act-20260926`: Schedule 3 cls 2–10, especially 3, 8(1)(a),(l); cls 13–14 | Draft; caller resolves ordinary chargeable earnings |
| JS-07 | Weekly income uses the prescribed number of weeks; ordinary JS is Schedule 6 item 2, one week. Grant transition is checked separately | `jobseeker-support-social-security-act-20260926`: Schedule 3 cls 11, 13(1)–(3), s 338(1)–(5); `jobseeker-support-social-security-regulations-20261001`: r 205(1), Schedule 6 items 1–2, Schedule 1 cl 25(1)–(4) | Draft; seven-day payable week is separate from MSD instalment timing and income attribution; no allocation or transition algorithm |
| JS-08 | Test 3 reduces the applicable rate by $0.70 per $1 above $160 weekly; the Act's text alone does not settle fractional-income treatment | `jobseeker-support-social-security-act-20260926`: Schedule 2 Income Test 3(b); Schedule 4 Part 1 cl 1(d) | `needs_review` for precision; DEC-002 |
| JS-09 | Gross benefit and net statutory payment differ; s 350(3) defines a tax-dependent gross-up relationship. DET 24/03 selects a weekly M tax basis; its full computational application remains unreviewed | `jobseeker-support-social-security-act-20260926`: ss 349–351; `jobseeker-support-ird-det-24-03`: operative determination, printed p 1 | `needs_review` / `MISSING_SOURCE` for complete method; DEC-001 |
| JS-10 | Section 18 limits concurrent own-right receipt per person. Two partners' own-right main benefits are recognised rate categories; one-benefit-per-household is this slice's coverage limit | `jobseeker-support-social-security-act-20260926`: s 18, Schedule 4 Part 1 cl 1(g); D11/D36; PR #151 | Draft; mixed-benefit couples `unsupported` / `not_modelled` |
| JS-11 | Income-related entitlement is not a new PAYE, net-payment, tax-year or AS/WFF result; graph edges require separate reviewed mappings | `jobseeker-support-social-security-act-20260926`: ss 17, 24, 349–351, Schedule 3 cl 8; existing interaction locators in `jobseeker-support-income-tax-act-interactions` | Interaction inventory only; Task 9 / 3.1.4 pending |

## Documentary candidates and calculation sequence

| Candidate | Exact source meaning | Source/version/period |
| --- | --- | --- |
| NZD 372.55 weekly | Part 1 cl 1(d) statutory maximum, matching MSD net M column | Act 26 September; Order as made 2 March 2026, applies from 1 April; checked 13 October |
| NZD 426.12 weekly | MSD's published gross maximum for single 25+ | MAP rates dated 1 April 2026, checked 13 October; no arbitrary-income conversion or end date established |
| NZD 160 weekly; reduction fraction 0.70 | Test 3(b) threshold and reduction of applicable rate | Act Schedule 2; selected week only in proposed review scope |

The statute does not print $426.12 in this rate row. No derived cut-out is
adopted, and no current rates page proves an unbounded future parameter
interval. The later values PR must bind independently reviewed values to
their source/locator and approved coverage interval.

The proposed sequence, conditional on approval, is:

1. Validate person/component/week and supported category. Preserve explicit
   exclusions and unresolved assertions (JS-01/02/03/10).
2. Verify the covering grant and ordinary payment state. Keep grant status
   separate from payment; never cancel it solely because an abated amount
   would be zero (JS-04).
3. Verify that the input is already-classified, exact **policy-week** income
   and that the weekly charging basis applies (JS-06/07). Schedule 3 cl 13
   prioritises earning/entitlement periods; allocation is not implemented here.
4. Select the dated cl 1(d) statutory maximum and Test 3. Subject to the
   precision decision, let `I*` be the approved income-test amount and
   `D = 0.70 × max(I* − 160, 0)`. The leading hypothesis is to reduce the
   statutory-side amount before gross-up, not subtract from the published
   gross maximum (JS-05/08). DEC-001 must resolve that computational
   application. This algebra expresses a proposed reduction substep, not
   an approved sequence or complete executable monetary rule.
5. Resolve lawful nil-payment treatment, precision and the tax-dependent
   conversion of the reduced statutory rate to the requested gross amount
   (JS-04/09; DEC-001/002). No negative benefit, unsourced clamp, rounding
   order or gross zero is emitted while this step remains unresolved.
6. Only after those gates close, emit the approved gross weekly component
   with retained trace and provenance. Actual tax deductions, net cash,
   arrears and household disposable income are separate components.

MSD's calculating-rate page instructs downward whole-dollar income rounding
for its DREW estimate, and its examples exclude cents. That is affirmative
guidance evidence, not a missing-source claim about **all** income rounding.
Whether that rule governs this statutory component, and its position relative
to aggregation/classification, requires review. Final benefit rounding, ties,
intermediate gross-up precision and nil-payment boundaries remain unverified.
([MSD calculating the rate](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/calculating-the-benefit-rate-01.html),
[DEC-002](decisions/DEC-002-income-and-payment-precision.md))

## Charging, exclusions and interactions

Regulation 205 and Schedule 6 do not grant a caller discretion to choose an
annual JS basis. Schedule 1 cl 25 distinguishes grants commencing/last
commencing from 1 July 2025 from specified earlier annually charged grants;
the latter transition is per grant at the end of its specified 52 weeks.
MSD's live summary says the transition ended by 30 June 2026. The legal
source supplies the per-grant boundary; the summary is not substituted for
grant-history evidence. The ordinary cl 1(d) weekly slice excludes unresolved
legacy/transitional charging. ([Regulations r 205; Schedules 1 and 6](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-10-01/),
[MSD income test](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/income-test-01.html))

Known outside-slice cases are `unsupported` / `not_modelled`: under-25 or
legacy 2013-transfer rates; couples or dependent-child categories; partial
weeks, grant/regrant or category changes; first applications; s 25 hardship
routes and exceptional residential routes; housekeeper additions (Part 1
cl 2), sanctions/stand-downs, suspension/cancellation, hospital/custody/absence,
overseas pensions, arrears/debts/direct deductions; discretionary exclusions,
childcare disregards, self-employment, asset/business/insurance income,
child support, deprivation and holiday/termination lump sums. These exclusions
describe coverage, not legal ineligibility. Unknown applicability requires
review. Anchors: ss 16–28; Part 4; Parts 5–6; Schedule 3; Schedule 4 Part 1.

Other household members are not folded into this person's income test.
Multiple own-right main-benefit recipients in the household remain a known
first-slice exclusion under D36, even where s 18 permits their separate grants.
Neither a zero payment nor an asserted grant supplies AS's “being paid” fact
or every WFF main-benefit test. Separate policy child and income definitions
remain separate. D38's existing income-period/no-apportionment and benefit-spell
contradiction decisions are preserved; no new adapter or graph edge is added.

## Identity, precision, provenance and validation handoff

A future calculated amount must identify person, component, NZD per selected
week, exact `[from,to)` period, geography/population, source/locator/version,
method, evidence class, uncertainty, model version and dependencies. Store
full approved precision; display only sourced household precision. Decimal
transport and reproducible arithmetic do not supply a legal rounding rule.
Trace the assertions, selected category/basis, income-test preparation,
parameters/intervals/review states, deductions, gross conversion and rounding,
rule/decision IDs and retained input/source/policy/code artifacts. Preserve
existing scenario/result hashes; a non-calculated outcome has no numeric value.

The next values/facts PR must close DEC-001/002, bind approved intervals and
questions, and hand-calculate independent **spec** cases: category/legacy
exclusions, exact week, whole-week grant coverage, known zero versus missing
income, $160 and $1 either side, fractional income, nil-payment boundary,
temporary zero status, and unsupported changes. Do not create fixtures from
this draft or change existing protected values to fit code.

For **benchmarks**, the MSD rate row is a dated documentary cross-check;
MAP's current income examples cover couple/sole-parent net amounts, not
this single gross output. A matching dated official worked result and gross
conversion/precision evidence remain missing; no calculator was run and no
expected gross value was adopted. **Regression** coverage must pin outcome
precedence, no unknown-to-zero conversion, net/gross distinction, period/version
gates, grant-versus-payment status, legacy exclusion, per-person s 18 versus
household coverage, and provenance. Independent Claude source/spec review,
Pete's decisions and the protected-value process precede implementation.
