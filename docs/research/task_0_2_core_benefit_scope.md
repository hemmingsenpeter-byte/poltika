# Core main benefits — dated primary-source scope proposal

Author source draft, 3 October 2026 (Pacific/Auckland). Programme Task 8;
`BUILD_PLAN_v0_3.md` local 0.2, with source-only inputs to 0.3. This is a
proposal for review and Pete's D1, not an approved specification or a decision.
No amount, parameter, statutory expected value or runtime capability is added.

The three inventories use the existing `SourceCatalog` model:

- [Jobseeker Support](../../policy_specs/jobseeker_support/sources.yaml).
- [Sole Parent Support](../../policy_specs/sole_parent_support/sources.yaml).
- [Supported Living Payment](../../policy_specs/supported_living_payment/sources.yaml).

## Source date and legal period

The [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/),
[Social Security Regulations 2018](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-09-04/)
and [Income Tax Act 2007](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
were retrieved and their identified provisions read on 3 October 2026.
The official current indexes showed these same 4 September consolidations.
The consolidation date is a source version, not the commencement of every rule.
The claims below concern law in force on 3 October, not a complete historical
or full-year audit.

The [Rates of Benefits and Allowances Order 2026](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/2026-03-02B/)
is the official as-made 2 March version. Clauses 2–4 establish commencement
and payment applicability from 1 April 2026; cl 5 and Schedule 1 Part 1
amend these three benefit tables. The amounts were located, not adopted.
MSD's published rate categories are dated 1 April 2026 and distinguish net M
from gross. Neither a displayed cut-out nor a net M column determines a new
parameter or a universal tax conversion. No legal end date is invented.

The [Jobseeker Support and Accommodation Supplement Amendment Act 2026](https://www.legislation.govt.nz/act/public/2026/54/en/latest/)
was retrieved as enacted on 3 September 2026; its page says it is not yet in
force. Section 2 commences the Act on 2 November 2026, with Part 2 commencing
on 1 April 2027. These are enacted future changes, not current rules or an
unpassed proposal. Any assessment spanning those dates needs a new source
and version review. This pack does not map the future amendment's detailed
eligibility or interaction logic.

Legislation was read from official HTML using a browser user agent when the
web tool could not retrieve it. MSD/IRD pages were retrieved separately.
The inventories distinguish published page dates, rate dates, source versions
and legal commencement. MAP pages without a displayed version date are live
corroboration only; they do not prove historical applicability.

## Shared gates and facts to retain

The Act's ss 16–19 and Schedule 2 require separate applicant, partner, child,
residence and other-benefit facts. Section 16 includes ordinary residence,
citizenship/residence status and qualifying residence, with refugee,
reciprocity and regulatory exceptions. A simple citizenship checkbox cannot
establish the whole gate. Sections 8 and 19 also matter for relationship and
immigration status. The first slice below proposes excluding exceptional
routes explicitly while retaining verified ordinary-route facts.

Section 17 directs payment to the appropriate Schedule 4 rate, subject to
reductions, suspension and cancellation. A grant, a maximum rate, an abated
entitlement and a cash payment are different facts. For example, JS s 24(2)
can preserve entitlement during a temporary period of income that reduces
payment to zero. A zero payment must not silently establish no main-benefit
status for WFF or AS.

**Scope discrepancy for review — proposed `SPEC_ERROR`:** local 3.4 says a
household cannot receive two main benefits unless a specification says
otherwise. Act s 18 limits simultaneous receipt by a person **in their own
right**. Schedule 4 Parts 1 and 3 expressly include a partner receiving a
main benefit in their own right. A household-wide prohibition would reject
recognised categories, including mixed-benefit couples. The detailed plan is
left unchanged; reviewer/Pete should clarify the intended contract before
implementation. This proposal creates no household-wide prohibition.

Schedule 2's general dependent-child definition and each Schedule 4 part's
specific exclusion need separate facts: JS Part 1 cl 7, SPS Part 2 cl 4 and
SLP Part 3 cl 8 exclude children receiving an orphan's or unsupported child's
benefit for those rate parts. This does not establish WFF child eligibility.

## Eligibility gate inventory

| Benefit and source locators | Gate classes that need evidence | Cases requiring a separate route or review |
|---|---|---|
| JS: Act ss 20–28; Regulations rr 8–9 | Work gap; availability or statutory exemption/limited capacity; applicant age band and dependent-child status; ordinary residential gate; no/minimum income; exclusions; clinical certificate where applicable | Employed but losing earnings through health/injury; discretionary hardship/student routes; strikes, training and full-time students; clinical assessment and MSD exemptions |
| SPS: Act ss 29–33 | Sole-parent route; care of qualifying child; youngest-child age; applicant age; ordinary residential gate; relevant income/category facts | Section 30 includes bereavement, dissolved relationship, living apart with insufficient support, and imprisoned-partner routes. Section 31 may treat a non-natural child as the claimant's own; s 32 has split-care selection and a court-order exception |
| SLP restricted capacity/blindness: Act ss 34–39; Regulations rr 10–11 | Restricted capacity or total blindness; statutory duration/severity or terminal route; applicant age and residence; clinical evidence and MSD determination | Do not infer capacity from a diagnosis. Section 36 intentional qualification exclusion, s 38 residential-care treatment and s 39 approved trial employment require distinct handling |
| SLP carer: Act ss 40–42; Regulations r 11 | Full-time care at home of a person other than the claimant's partner; institutional-care counterfactual; age/dependent-child and residential gates; required clinical evidence | The cared-for person and claimant's partner are different entities; temporary absence and partnered-carer rate rules require separate handling |

[MSD's JS overview](https://www.workandincome.govt.nz/products/a-z-benefits/jobseeker-support.html)
(updated 24 July 2026) corroborates separate work and health routes, partner
income and weekly payment. [Its SPS overview](https://www.workandincome.govt.nz/products/a-z-benefits/sole-parent-support.html)
(17 July 2026) gives simplified relationship wording; the broader
[MAP qualifications](https://map.workandincome.govt.nz/map/income-support/main-benefits/sole-parent-support/qualifications.html)
and s 30 prevent promoting that wording into a universal no-partner gate.
[The SLP overview](https://www.workandincome.govt.nz/products/a-z-benefits/supported-living-payment.html)
(24 July 2026) distinguishes restricted-capacity/blindness from full-time care.
These pages corroborate the route inventory; they do not verify a person's
eligibility or replace an MSD determination.

## Rate categories and abatement locators

Category labels and Income Test numbers below identify legal provisions,
not adopted monetary values. Schedule 2 defines the tests using combined
claimant and partner income. Tests 1 and 2 have tiered withdrawal; Tests 3 and
4 have a single withdrawal band. The beneficiary category selects the test,
so one universal curve per benefit would lose statutory distinctions.

| Benefit | Schedule 4 category inventory | Abatement and special locators |
|---|---|---|
| JS, Part 1 cl 1 | Young single at/away from parental home (a); other young single (b); grandparented woman alone (c); ordinary older single without children (d); sole-parent child-age categories (e), (f); partner own-right main benefit (g); partner NZ Super/veteran pension (h); partner without such own-right entitlement (j) | (a), (b), (d), (j): Test 3; (c), (e), (f): Test 1; (g), (h): Test 4. Clauses 2–8 cover housekeeper, partner sanction/non-entitlement, sole-parent history, childcare disregard, imprisonment, child exclusion and living-with-parent meaning |
| SPS, Part 2 cl 1 | Beneficiary with qualifying dependent children | Test 1. Clause 2 discretionary childcare earnings disregard; cl 3 discretionary spouse-income attribution for specified s 30 routes; cl 4 policy-specific child exclusion |
| SLP, Part 3 cl 1 | Single age bands without children (a), (b); single with children (c); partner own-right main benefit (d); partner NZ Super/veteran pension (e); restricted-capacity/blindness claimant with partner without such own-right entitlement (g); carer claimant in that partner category (h) | (a)–(c), (g), (h): Test 1; (d), (e): Test 2. Clause 1's trailing paragraph separately disregards own-effort earnings for s 34 and totally blind claimants; cls 2–4 cover blind earnings subsidy; cls 5–6 residential care; cl 7 carer floor/cap; cl 8 child exclusion |

The [JS rate-category table](https://map.workandincome.govt.nz/map/deskfile/main-benefits-rates/jobseeker-support-current.html)
and [MSD April 2026 rate page](https://www.workandincome.govt.nz/products/benefit-rates/benefit-rates-april-2026.html)
corroborate current category distinctions. The statutes retain authority.
An excluded special rate is not replaced by the closest ordinary rate.

The [MAP partnered-carer guidance](https://map.workandincome.govt.nz/map/income-support/main-benefits/supported-living-payment/supported-living-payment-caring-for-a-person-charg-01.html)
specifically separates claimant/partner income from the cared-for person's
income and describes the capped calculation. It must be read with Part 3
cl 7; the restricted-capacity dependent-partner rate is not a shortcut for it.

## Income definitions and assessment basis

Schedule 3 cl 2 orders the income provisions. Clauses 3–7 concern gross
money value, periodical and insurance receipts, employment-ending receipts,
parental-leave payments and goods/services; cl 7A and Part 3A distinguish
child-support classes and charging periods. Clauses 8–9 provide exclusions
and regulation overrides. Clauses 11–14 cover periods and changes, cl 15
business/trade rules, and cls 16–17 deprivation. An annual wage total alone
cannot prove chargeable benefit income or its weekly attribution.

The current cl 13(1A) attributes ordinary income by earning/entitlement
period; cl 13(2) provides the fallback when MSD cannot determine that period.
Clauses 13(3A)–(3E) separately handle holiday-pay timing. Receipt date is not
a general replacement for these rules. Information-share child support is
expressly outside cl 13 and has its own Part 3A timing.

| Benefit | Statutory basis to preserve | Current operational corroboration |
|---|---|---|
| JS | Regulation 205/Schedule 6 current ordinary weekly basis; Schedule 1 cl 25 contains the prior grant transition. Historical grant dates require a separate audit | [JS income-test page](https://map.workandincome.govt.nz/map/income-support/main-benefits/jobseeker-support/changes-and-reviews-jobseeker-support/income-test-01.html) says the annual-charging transition ended before the as-of date and distinguishes family categories |
| SPS | Regulation 205(1)/Schedule 6 prescribes the annual assessment basis. Regulation 205(2) permits a weekly agreement; (3) allows termination by either party | [SPS charging page](https://map.workandincome.govt.nz/map/income-support/main-benefits/sole-parent-support/charging-income-01.html) describes both bases, childcare exemptions and separate overseas-pension deductions |
| SLP | Same regulation 205 annual basis/weekly-agreement distinction; route-specific earnings disregards in Schedule 4 Part 3 remain separate | [SLP charging page](https://map.workandincome.govt.nz/map/income-support/main-benefits/supported-living-payment/charging-income-01.html) corroborates bases and exemptions; carer-couple guidance adds the special cap |

**Proposed fact boundary:** store the assessment basis, evidence of any weekly
agreement, period to which earnings relate, benefit route, personal earnings
class, partner income class and policy-specific child facts. This does not
approve a new schema. Missing or contradictory basis/evidence should require
review; a known excluded income type should be explicitly unsupported in the
first slice. Neither becomes a guessed wage total or a numeric zero.

## Source-only interaction candidates for local 0.3

These are dependency locators for a later specification, not accepted graph
edges or a disposable-income definition. Existing WFF/AS decisions and their
supported periods remain binding; this draft does not extend their domain.

| Candidate | Dated primary locator and implication | Integration gate |
|---|---|---|
| Taxable main-benefit income → personal income tax | Income Tax Act CF 1(1)(c), YA 1 main benefit; Social Security Act Schedule 2 main benefit includes the three routes scoped here | Preserve gross benefit income separately from withheld tax and actual net payment; basic tax does not supply PAYE or every tax credit |
| Paid-for main-benefit period → WFF family scheme income | MB 1(1)(b), MB 2 distinguish main-benefit allocation and non-year periods | Need paid-for dates and the appropriate relationship period; avoid projecting one week across a full year |
| Main-benefit receipt → component-specific WFF status | MC 6(b)(i) excludes specified credits for claimant receipt; MD 8 also covers partner receipt for IWTC. MD 14 and MG 4 create protected-month conditions | Recheck WFF-08 and existing Earner and benefits mapping. FTC/Best Start may coexist; main-benefit income is not itself qualifying earned employment. ME 2 remains a distinct MFTC employment test |
| Benefit/category status → AS base-rate route | Social Security Regulations r 17 defines beneficiary by payment and specifies appropriate maximum pre-abatement rates; r 18 applies its reduction to non-beneficiaries | Retain actual payment/status, claimant and partner category, and policy-specific child facts. Do not substitute the abated benefit amount for the statutory AS base rate |
| WFF tax credits → benefit/AS chargeable-income exclusions | Social Security Act Schedule 3 cl 8(1)(l) excludes credits under the named WFF subparts without naming the paying agency; Schedule 2 income cross-reference applies | This confirms the source locator behind AS-10/WFF DEC-003, already decided by Pete. No new payer decision or blanket exclusion for other income types is proposed |
| Youngest-child transition SPS → JS | Social Security Act s 33 deemed replacement is conditional on MSD not believing JS qualifications fail | Requires dated transition and eligibility review; a birthday alone must not silently produce a new entitlement |
| Own-right benefit status ↔ partner's category | Section 18; Schedule 4 Parts 1 and 3 partner categories | Resolve local 3.4 household wording and identify persons before composing benefit totals |

[IRD's government-payments guidance](https://www.ird.govt.nz/working-for-families/types/government-payments)
(updated 9 April 2026) corroborates the FTC/Best Start versus IWTC/MFTC
distinction and family-income inclusion. Its broad table does not implement
relationship periods or protected months. Main-benefit receipt and amount
must remain separate from a whole-year WFF eligibility assertion.

## Proposed first supported slices and implementation order

The source evidence supports retaining the detailed plan's proposed order,
**JS → SPS → SLP**, subject to Pete D1. Start with JS ordinary older single,
without dependent children (Schedule 4 Part 1 cl 1(d)), an established ordinary
grant, verified availability/residence and ordinary earnings attributable to
the assessment week. This proves the present weekly basis with the fewest
partner/care branches. Adding JS children or couples introduces a different
test or rate and should be a separately approved increment.

Next propose SPS ordinary single principal caregiver, own qualifying child,
no disputed/split/non-natural-child care, ordinary established grant and
ordinary earnings. Select either the statutory annual basis or a verified
weekly agreement explicitly; do not inherit JS's weekly default. This adds
the tiered test and child/care gates before partner attribution complexity.

Then propose SLP restricted-work-capacity ordinary adult single without
children (Part 3 cl 1(b)), with existing MSD/clinical eligibility evidence and
an explicit assessment basis. Even this small route requires its own-effort
earnings disregard; omitting that would understate the supported contract.
Total blindness, carer and partnered SLP are later slices because their
exemptions, evidence, rates and caps differ. No automated medical determination
or new personal-data collection is authorised by this proposal.

Across the initial slices propose excluding new-grant commencement and
stand-down calculations, sanctions/non-entitlement periods, arrears/debt or
direct deductions, hospital/residential-care rates, overseas absence/pensions,
reciprocity/refugee exceptions, discretionary hardship/childcare/income
attribution, self-employment, termination/holiday lump sums, child support,
deprivation, variable-period transitions, trial employment and competing grants.
These are proposed coverage exclusions, not statements that the cases cannot
qualify legally. Preserve unsupported reasons. Case histories with missing
eligibility/payment/basis evidence require review instead of assumed approval.

## Unresolved coverage and Pete D1 choices

| Gate | Choice or evidence needed before a specification/implementation |
|---|---|
| D1 period | Approve an as-of established-grant assessment or a broader historical interval. This pack alone cannot support the full 2026–27 year, especially across the enacted November change |
| D1 population breadth | Accept the three ordinary single slices, or prioritise couples/children/carers. Broader populations need their complete rate, partner, care and income branches, not just the locators here |
| D1 income and assessment basis | Choose ordinary earnings only versus broader receipts; for SPS/SLP decide how to represent the default annual basis and evidenced weekly agreements |
| D1 result meaning | Decide whether the first result is pre-tax statutory entitlement, net payment with specified tax treatment, or a clearly limited entitlement conditional on an established grant. Do not label it complete household disposable income |
| Payment precision and boundary source gap | Benefit-specific rounding, gross/net M reconciliation, tax-code and direct-deduction ordering were not established in this scoped pass. No monetary calculation, cut-out parameter or boundary benchmark is authorised until those sources are mapped and reviewed |
| Clinical/discretionary facts | Determine acceptable evidence/provenance for an existing MSD finding; do not have the model infer medical capacity, exemption, childcare disregard or discretionary grant |
| Entity contract | Clarify the local 3.4 per-household prohibition against s 18 and the partner tables; preserve different partner/care/child definitions across benefits, WFF and AS |
| Integration/version coverage | Tax scope, shared household semantics and existing WFF/AS period limits remain dependencies. Protected-month WFF, mixed-benefit couples and zero-payment entitlement status remain explicitly gated |
| Future maintenance | Review the detailed enacted JS amendments before 2 November and AS amendments before 1 April 2027. This pack identifies commencement only; it cannot approve future graph edges or rates |

The rounding/payment gap is proposed `MISSING_SOURCE` for the dependent
monetary claim, not evidence that no rule exists. Competing or insufficient
interpretations should be routed to Pete under the review doctrine. This
draft does not create DEC records, clear an independent review queue, mark
Task 8 Done or authorise implementation. A fresh source checker must verify
the dated locators and scope proposals before they are presented for D1.
