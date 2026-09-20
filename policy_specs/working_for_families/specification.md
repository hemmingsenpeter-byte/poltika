# Working for Families specification

**Status:** Task 2 independent source map complete on 21 September 2026; not an
approved implementation specification. **Reference period:** 2026-27 tax year.
Source IDs below refer to [sources.yaml](sources.yaml). Task 10 must turn this
map into a scoped, reviewed calculation specification before values or examples
become protected tests. No external implementation was consulted.

## Statutory structure

The Income Tax Act 2007, Part M is the governing source (`wff-income-tax-act`).
Subpart MA defines terms, MB adjusts net income to family scheme income, MC sets
family-scheme entitlement, MD covers family tax credit and in-work tax credit,
ME covers minimum family tax credit, MF covers instalments, and MG covers Best
Start. IRD's `wff-ird-interpretation-2026` is an agency interpretation of the
law currently in force, not a substitute for those provisions.

| ID | Source-grounded policy meaning | Authority and check |
| --- | --- | --- |
| WFF-01 | The claimant must meet the family-scheme criteria for the relevant entitlement period: age, principal care of a dependent child, residence (or applicable emergency-benefit route), and continuing requirements. Relationships and shared care affect entitlement periods. | Income Tax Act ss MC 2-11; `wff-ird-shared-care`. Check the Act's definitions of dependent child and principal caregiver for each case. |
| WFF-02 | Family scheme income begins with net income and requires the adjustments in subpart MB. It cannot be represented safely as wages alone; relationship periods, partner income, and child support paid or received matter. | Income Tax Act ss MB 1-14; `wff-ird-interpretation-2026`, `wff-ird-family-income`. The adjustment inventory below is a required input-domain checklist. |
| WFF-03 | Family tax credit uses the eldest-child and additional-child annual amounts, prorated by eligible days. Abatement is based on family scheme income; any excess over family tax credit can reduce in-work tax credit. | Income Tax Act ss MD 1, MD 3, MD 13-15; `wff-ird-family-tax-credit`. Confirm ordering and protected-credit cases in the Act. |
| WFF-04 | In-work tax credit has additional age, care, residence, benefit-status, and earner conditions. The calculation varies with qualifying children and eligible weeks. | Income Tax Act ss MD 4-10 and MA 7; `wff-ird-in-work-tax-credit`. Distinguish the earner test from the full-time-earner test used for minimum family tax credit. |
| WFF-05 | Minimum family tax credit tops up qualifying after-tax family income for eligible full-time-earner weeks; it is separate from the abating family and in-work credits. | Income Tax Act ss ME 1-3 and MA 7; `wff-ird-minimum-family-tax-credit`. Check the Act's net-family-scheme-income definition before implementing a tax calculation. |
| WFF-06 | Best Start is a per-child credit during the first three years. Paid parental leave defers payment. For children born before 1 April 2026, the first year is exempt from income abatement; later birth cohorts can be abated from their first year. | Income Tax Act ss MG 1-4; `wff-ird-best-start`, `wff-budget-measures-2025`. Confirm partial-year, birth-date, and protected-credit cases. |
| WFF-07 | Shared care is component-specific. IRD describes a principal-care threshold of 122 days per year or a third of a four-month period and different apportionment for family tax credit/Best Start, in-work tax credit, and minimum family tax credit. | Income Tax Act ss MC 9-11 and component provisions; `wff-ird-shared-care`. Its examples use older rates, so do not promote their amounts to 2026 benchmarks. |
| WFF-08 | A main benefit may coexist with family tax credit and Best Start but normally prevents in-work and minimum family tax credit. Payment source can be IRD or MSD. | Income Tax Act ss MD 8, MD 14, MG 4; `wff-ird-government-payments`. Verify exceptions and the protected-credit monthly calculation. |
| WFF-09 | Instalment payments and annual entitlement are distinct. IRD describes weekly/fortnightly instalments as annual entitlement divided by 52/26 and rounded down to whole dollars. | Income Tax Act subpart MF; `wff-ird-family-tax-credit`, `wff-ird-best-start`. Check exact statutory instalment treatment and mid-year changes. |

## Family scheme income adjustment inventory

The applicable subpart MB has more than the main wage/partner pathway. Task 10
must either represent each category below or mark its input as unsupported;
otherwise a supplied `family_income` cannot be treated as derived by Poltika.

| Provision | Adjustment or classification to preserve |
| --- | --- |
| MB 1-2 | Start from net income, allocate income across relationship/employment periods, and annualise income for a non-year period. |
| MB 3-4 | Business/investment activities and major shareholding in close companies require adjusted income rather than merely taxable wages. |
| MB 5-6 | Superannuation and retirement-savings distributions have separate inclusion rules. |
| MB 7, 7B-8 | Settlor-attributable trust income and employment/fringe benefits (including controlling-shareholder cases) are distinct adjustments. |
| MB 9-10 | MB 9 is repealed; specified exempt pensions and annuities have a half-inclusion rule under MB 10. |
| MB 11-12B | Dependent-child passive income above the $500 threshold, non-resident foreign-sourced income, and non-beneficiary trust distributions each have their own tests. |
| MB 13-14 | Other family-support payments can be included when the statutory threshold is met; remission income of a discharged bankrupt is excluded. |

IRD also requires the claimant and partner's income, child support received and
paid, and relevant worldwide income of a non-resident partner to be handled as
separate facts (`wff-ird-family-income`, `wff-ird-interpretation-2026`). IRD
excludes a non-taxable Accommodation Supplement from other family-support
income (`wff-ird-other-income`); this is not a reason to exclude taxable main
benefits or other payments.

## Entitlement branches to retain

| Branch | Mapping consequence |
| --- | --- |
| Care and relationships | Apply MC 3-11 by entitlement period; a child can have more than one principal caregiver. Use the component-specific shared-care treatment, not one household-wide fraction. |
| Earner and benefits | MD 4-10 and MA 7 distinguish an earner from the full-time earner required by ME 1-3. Main-benefit and Student Allowance periods can change in-work/minimum-credit eligibility without automatically removing family tax credit or Best Start. |
| Abatement and protection | MD 13-15 govern abatement across family and in-work credits; MD 14's protected family-tax-credit case must be checked before applying the ordinary reduction. |
| Child age and leave | MG 1-4 require birth-cohort, third-birthday, eligible-day, paid-parental-leave, and income-abatement branches. A first year is not universally exempt after the 2026 change. |
| Payment timing | MF instalments, income estimates and annual square-up are different from annual entitlement. Do not use a weekly chart cell as a statutory annual amount. |

## Dated parameter and amendment map

These are source observations for the 2026-27 tax year, not accepted test values.
Annual statutory amounts and displayed weekly instalments must remain distinct.

| Effective period | Observation | Source |
| --- | --- | --- |
| From 1 April 2026 | The 2025 Tax Credit Order changes annual family tax credit rates to $7,921 for the eldest child and $6,454 for each additional child; minimum family tax credit's prescribed amount to $36,604; and Best Start's annual rate to $4,041. | `wff-tax-credit-order-2025`, clauses 4-6; Income Tax Act ss MD 3, ME 1, MG 2. |
| From 1 April 2026 | The family tax credit abatement threshold is $44,900 and the rate is 27.5 cents per complete dollar above it. | `wff-budget-measures-2025`; Income Tax Act s MD 13(3)(a); `wff-ird-family-tax-credit`. |
| From 1 April 2026, subject to earlier reversal | The temporary in-work tax credit base is $7,670 annually rather than $5,070; a later Order in Council can set the reversal date. A petrol-price condition is described by IRD, but the operative legal event is the Order. | `wff-iwtc-increase-act-2026`, ss 105-106; `wff-ird-temporary-increase`. Verify the Order status for each modelled date. |
| From 1 April 2026 | Best Start abatement is 21 cents per complete dollar of family scheme income above $79,000 for periods subject to abatement. The pre-1-April-2026 birth exception remains relevant. | Income Tax Act s MG 3; `wff-ird-best-start`; `wff-budget-measures-2025`. |
| From 1 April 2027 | Enacted changes to family scheme income adjustments and residence are future law on this reference date. | `wff-budget-measures-2026`; `wff-ird-interpretation-2026`. Do not apply them to 2026-27 cases. |

## Benchmark candidates

`wff-ird-family-tax-credit`, `wff-ird-in-work-tax-credit`,
`wff-ird-minimum-family-tax-credit`, and `wff-ird-best-start` each contain
published worked examples. `wff-ird-rates-2026` is an estimate chart, useful as
a cross-check but not a replacement for independently calculated statutory
expectations. A prior revision of that chart omitted the temporary in-work
increase; use the revision recorded in `sources.yaml` and preserve its date.

## Task 10 and review gates

- Set the v0.1 input domain explicitly. Unsupported adjustment or exception
  paths must return an unsupported/needs-review outcome, not zero entitlement.
- Verify whether an Order in Council has ended the temporary in-work rate for
  each modelled date. The 2026 Act permits an early legal change; the petrol
  condition described by IRD does not change the rate without that instrument.
- Specify exact component ordering, part-period day/week treatment, tax and
  rounding rules, and protected-credit treatment from the operative provisions.
- Recalculate fully specified official examples independently before making
  benchmark fixtures. IRD's shared-care examples contain older rates.
- Have an independent reviewer verify the dated law and the supported-domain
  decisions. Pete decides genuine interpretation ambiguities; this map does not.

## Task 10 calculation draft (not approved)

**Draft date:** 21 September 2026. **Period:** 1 April 2026 to 31 March 2027.
This section is a proposed implementation contract, separate from the Task 2
source map above. The companion `policy.yaml` is `draft_pending_review` with
`policy_version: null`; neither file authorises executable policy content yet.
The official legislation site exposed indexed provision text but returned 403
to full-page retrieval during this pass. The pinpoint checks below therefore
remain independent-review gates, not claims of complete legal verification.

### Proposed v0.1 supported domain

One claimant and a stable partner status, dependent-child set, residence and
principal-care arrangement for the **whole** 2026-27 tax year. Children are
fully in the claimant's care and meet the statutory dependent-child tests;
there is no shared-care fraction, change of caregiver, or relationship change.
The scenario supplies a documented family-scheme-income amount for the whole
relationship period, including all applicable subpart MB adjustments. A wages
sum or unlabelled `family_income` is not accepted as that amount (WFF-01/02;
Income Tax Act ss MB 1-14, MC 3-11; `wff-ird-family-income`). This is a
deliberately narrow input contract, not a claim that other households receive
no WFF entitlement.

For the in-work component, the initial calculable branch requires a qualifying
salary/wage earner throughout the year, with no main benefit or Student
Allowance period and no unpaid work break. Self-employment can legally
qualify, but is outside this first branch until its facts and MD 9 pathway are
reviewed (`wff-ird-in-work-tax-credit`; Income Tax Act ss MD 4-10). For the
minimum family component, require documented full-time-earner weeks and a
separately verified **net** family-scheme-income amount under s ME 3; gross
family-scheme income must not be substituted. For Best Start, the first
calculable branch is one qualifying child born from 1 April 2024 through
31 March 2025, eligible for the entire tax year, with no paid parental leave
or shared care. This keeps the birth-cohort and part-period cases explicit
without guessing their apportionment (WFF-05/06; Income Tax Act ss ME 1-3,
MG 1-4; `wff-ird-minimum-family-tax-credit`, `wff-ird-best-start`). These
component branches are **proposals for review**, not an approved reduction of
WFF's eventual scope.

The calculator must return per-component `calculated`, `unsupported`, or
`needs_review`, with a reason. Missing eligibility evidence, an unverified
income derivation, or unknown operative rate produces `needs_review`;
structurally outside-domain facts produce `unsupported`. Neither becomes a
numeric zero. A genuine, evidenced failure of an eligibility test may yield
zero for that component. Do not sum a partial result and present it as total
WFF entitlement (`policy_specs/SCHEMA.md`; WFF-01/02/07/08).

### Proposed full-year calculation sequence

1. Select the law and parameter interval for the assessment date; verify the
   temporary in-work base has not been reversed by an Order in Council. The
   2026 Act changed MD 10(3)(a) to $7,670 with a possible earlier reversal;
   the `policy.yaml` end date is the statutory outer bound, not confirmation
   that the increased rate applies throughout 2026-27. On 21 September 2026,
   the official Act page reported no secondary legislation made under s 2(43)
   on that site; this does not establish the position on a later assessment date.
   An early reversal needs a separately specified split-period calculation
   before a full-year result can be claimed. Petrol-price guidance is not
   itself the operative legal instrument
   (`wff-iwtc-increase-act-2026`, ss 2, 105-106; `wff-ird-temporary-increase`).
2. Validate family membership, qualifying children, residence, care, and
   family-scheme income. Calculate the full-year family tax credit as $7,921
   for the eldest qualifying child plus $6,454 for each additional qualifying
   child. For the ordinary full-year case, abatement is $0.275 times the
   number of **complete dollars** by which family-scheme income exceeds
   $44,900: `0.275 * floor(max(0, income - 44900))`. Subtract up to the
   family-credit amount, and carry any remaining abatement to in-work tax
   credit, following IRD's component allocation guidance. Do **not** apply
   this ordinary formula to MD 14 protected-credit or per-child
   government-payment cases
   until independently specified (WFF-03/08; Income Tax Act ss MD 3, 13-15;
   `wff-tax-credit-order-2025`, cl 4;
   `wff-budget-measures-2025`, s 7;
   `wff-ird-family-tax-credit`).
3. If in-work eligibility is established, the full-year maximum for one to
   three children is $7,670, plus $780 for each child beyond three. Reduce it
   by the unused family-credit abatement, with a zero floor. If the claimant
   cannot receive family tax credit for a child due to a different payment,
   the separate direct-abatement pathway requires review and is unsupported
   in this draft (WFF-04/08; Income Tax Act ss MD 4-10, 13-15;
   `wff-ird-in-work-tax-credit`).
4. If minimum-family eligibility and s ME 3 net family-scheme income are
   independently established, the all-52-week draft amount is the positive
   difference between $36,604 and that net income. It does not abate with the
   family/in-work credits and must not be calculated from gross income alone.
   Tax and part-week derivations remain unsupported (WFF-05; Income Tax Act
   ss ME 1-3; `wff-ird-minimum-family-tax-credit`).
5. For the single full-year Best Start branch above, the draft maximum is
   $4,041. For an abatable year, reduce it by 21 cents per **complete dollar**
   of family-scheme income over $79,000, with a zero floor. First-year
   pre-1-April-2026 births, later birth cohorts, births/third birthdays within
   the year, paid parental leave, and multiple eligible children require
   separate review; do not apply this branch to them (WFF-06; Income Tax Act
   ss MG 1-4; `wff-tax-credit-order-2025`, cl 6;
   `wff-ird-best-start`).

All amounts above are **annual entitlement candidates**, not weekly payment
figures. IRD's weekly/fortnightly guidance divides by 52/26 and rounds each
instalment down to a whole dollar; instalments and annual square-up are not
in the initial calculation output (WFF-09; Income Tax Act subpart MF;
`wff-ird-family-tax-credit`). Use decimal arithmetic and preserve cents in
annual results; independently verify any statutory intermediate rounding
before implementation. No official example is promoted to `benchmarks.yaml`
or `spec_cases.yaml` by this draft.

### Review gates and source checks

- Re-read the operative Income Tax Act Part M version as at the chosen
  assessment date, particularly MB 1-14, MC 3-11, MD 3-15, ME 1-3, MG 1-4,
  and MF. Confirm each formula, rounding point, protected-credit exception,
  and commencement/application clause against full text, not only IRD pages.
- Verify the 2025 Tax Credit Order clauses 4-6, the 2025 Budget Measures Act
  s 7, and 2026 annual-rates Act ss 2/105-106. Search secondary legislation
  for an actual early in-work reversal Order for each modelled date. An
  unconfirmed order status keeps `in_work_base` at `needs_review`.
- Independently test the proposed supported-domain boundary, especially
  whether verified family-scheme income and net family-scheme income are
  acceptable v0.1 canonical inputs. Resolve any genuine scope/interpretation
  dispute with Pete before setting `status: approved` or `policy_version`.
- Recalculate the dated IRD worked examples independently during Tasks 13-14;
  the shared-care page uses older rates and is not a 2026-27 benchmark.

**Handoff to Claude Code:** critique the schema shape, missing/unsupported
conditions, component ordering, source locators, date handling, and whether
this static-year branch can be implemented without accidentally representing
out-of-domain households as zero entitlement. Do not implement the policy
calculator or statutory-value fixtures before the review outcome is resolved.
