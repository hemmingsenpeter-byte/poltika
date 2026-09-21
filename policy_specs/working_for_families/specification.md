# Working for Families specification

**Status:** Task 2 source map complete; Task 10 scoped specification approved
by Pete on 21 September 2026 (`policy_version: "0.1.0"`). **Reference period:**
2026-27 tax year. Source IDs below refer to [sources.yaml](sources.yaml).
Approval covers only the supported domain and explicit status outcomes below;
it does not promote examples to protected tests or clear a parameter marked
`needs_review`. No external implementation was consulted.

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
| WFF-03 | Family tax credit uses the eldest-child and additional-child annual amounts, prorated by eligible days. MD 2 applies family credit abatement first to family tax credit, then to in-work tax credit; protected-credit months are a separate path. | Income Tax Act ss MD 1-3, MD 13-15; `wff-ird-family-tax-credit`. |
| WFF-04 | In-work tax credit has additional age, care, residence, benefit-status, and earner conditions. The calculation varies with qualifying children and eligible weeks. | Income Tax Act ss MD 4-10 and MA 7; `wff-ird-in-work-tax-credit`. Distinguish the earner test from the full-time-earner test used for minimum family tax credit. |
| WFF-05 | Minimum family tax credit tops up qualifying after-tax family income for eligible full-time-earner weeks; it is separate from the abating family and in-work credits. | Income Tax Act ss MA 7 and ME 1-3; `wff-ird-minimum-family-tax-credit`. Full-time-earner hours and ME 2 employment exclusions must be checked separately from the in-work earner test. |
| WFF-06 | Best Start is a per-child credit during the first three years. Same-child parental leave or preterm baby payments, parental tax credit, and specified veterans' payments can exclude entitlement for a period under MC 6(c). For children born before 1 April 2026, the first year is exempt from income abatement; later birth cohorts can be abated from their first year. | Income Tax Act ss MC 6(c), MG 1-4; `wff-ird-best-start`, `wff-budget-measures-2025`. Confirm partial-year, birth-date, and protected-credit cases. |
| WFF-07 | Shared care is component-specific. IRD describes a principal-care threshold of 122 days per year or a third of a four-month period and different apportionment for family tax credit/Best Start, in-work tax credit, and minimum family tax credit. | Income Tax Act ss MC 9-11 and component provisions; `wff-ird-shared-care`. Its examples use older rates, so do not promote their amounts to 2026 benchmarks. |
| WFF-08 | A main benefit may coexist with family tax credit and Best Start but normally prevents in-work and minimum family tax credit. Payment source can be IRD or MSD. | Income Tax Act ss MD 8, MD 14, MG 4; `wff-ird-government-payments`. Verify exceptions and the protected-credit monthly calculation. |
| WFF-09 | Instalment payments and annual entitlement are generally distinct. IRD describes weekly/fortnightly instalments as annual entitlement divided by 52/26 and rounded down to whole dollars, but an extra-instalment year can also alter annual entitlement. | Income Tax Act subpart MF; Tax Administration Act s 80KW (`wff-tax-administration-act`); `wff-ird-family-tax-credit`, `wff-ird-best-start`. Check payment schedule and mid-year changes. |

## Family scheme income adjustment inventory

The applicable subpart MB has more than the main wage/partner pathway. Task 10
must either represent each category below or mark its input as unsupported;
otherwise a supplied `family_income` cannot be treated as derived by Poltika.

| Provision | Adjustment or classification to preserve |
| --- | --- |
| MB 1-2 | Start from net income, allocate employment, main-benefit, and other income across the applicable periods, and annualise income for a non-year period. MB 1 also distinguishes PIE income/distributions, maintenance deductions, and main income-equalisation deposits/refunds. |
| MB 3-4 | Net-loss business/investment activities are disregarded for this purpose, subject to MB 3's associated-activity and deduction-apportionment rules; major shareholding in close companies requires a separate attributed-income calculation rather than merely taxable wages. |
| MB 5-6 | Specified superannuation distributions linked to recent employer contributions and specified RSCT-withheld retirement-savings distributions have separate inclusion and timing tests; ordinary distributions must not be treated as automatically included. |
| MB 7, 7B-8 | Settlor-attributable trust income, specified employment benefits for non-controlling employees, and attributed fringe benefits for controlling shareholders are distinct adjustments with their own exclusions and thresholds. |
| MB 9-10 | MB 9 is repealed; specified exempt pensions and annuities have a half-inclusion rule under MB 10. |
| MB 11-12B | If the listed dependent-child income types total more than $500, only the excess is allocated across the child's principal caregivers; non-resident partner foreign-sourced income and non-beneficiary, non-settlor trust distributions have separate tests. |
| MB 13-14 | MB 13 includes qualifying income-replacement/living-expense payments after its specific exclusions. Its $5,000 exception tests the combined otherwise-includable total for the person and their spouse or partner, not each payment or person separately. MB 14's former remission-income exclusion is repealed; do not apply it as a current adjustment. |

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
| From 1 April 2026, subject to earlier reversal | The temporary in-work tax credit base is $7,670 annually rather than $5,070. Section 105(2) reverses the amendment on the date set by an Order in Council, or on 1 April 2027 if no earlier Order takes effect. The 2026-27 full-year rate remains conditional while that year is open. | `wff-iwtc-increase-act-2026`, ss 2(40), 2(43)-(45), 105-106; `wff-ird-temporary-increase`. Apply the rate-status contract below. |
| From 1 April 2026 | Best Start abatement is 21 cents per complete dollar of family scheme income above $79,000 for periods subject to abatement. The pre-1-April-2026 birth exception remains relevant. | Income Tax Act s MG 3; `wff-ird-best-start`; `wff-budget-measures-2025`. |
| From 1 April 2027 | Enacted changes to family scheme income adjustments and residence are future law on this reference date. | `wff-budget-measures-2026`; `wff-ird-interpretation-2026`. Do not apply them to 2026-27 cases. |

## Benchmark candidates

`wff-ird-family-tax-credit`, `wff-ird-in-work-tax-credit`,
`wff-ird-minimum-family-tax-credit`, and `wff-ird-best-start` each contain
published worked examples. `wff-ird-rates-2026` is an estimate chart, useful as
a cross-check but not a replacement for independently calculated statutory
expectations. A prior revision of that chart omitted the temporary in-work
increase; use the revision recorded in `sources.yaml` and preserve its date.

## Task 10 scope and follow-on gates

The source and independent-review gates for this scope are complete. The
following constraints still govern implementation and benchmark promotion.

- Set the v0.1 input domain explicitly. Unsupported adjustment or exception
  paths must return an unsupported/needs-review outcome, not zero entitlement.
- Verify the official reversal-Order record for the complete modelled interval,
  including its end date, before using the temporary in-work base. The 2026
  Act permits an early legal change; the petrol condition described by IRD
  does not change the rate without that instrument.
- Specify exact component ordering, part-period day/week treatment, tax and
  rounding rules, and protected-credit treatment from the operative provisions.
- Recalculate fully specified official examples independently before making
  benchmark fixtures. IRD's shared-care examples contain older rates.
- Have an independent reviewer verify the dated law and the supported-domain
  decisions. Pete decides genuine interpretation ambiguities; this map does not.

## Approved Task 10 scoped calculation contract

**Reviewed and accepted:** 21 September 2026. **Period:** 1 April 2026 to
31 March 2027. This section is the scoped implementation contract, separate
from the Task 2 source map above. The companion `policy.yaml` is `approved`
at `policy_version: "0.1.0"`; calculators must still enforce every
`unsupported`/`needs_review` branch and the live in-work rate-status gate.
The official legislation site returned 403 to the initial full-page fetch;
later browser-user-agent retrieval enabled direct checks of the relevant
provisions recorded in `sources.yaml`. Unchecked provisions and exceptions
remain outside the approved branch, not claims of complete legal verification.

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

For a partnered claimant, the verification must also show each person's
family-scheme income and their combined amount. The ordinary combined-income
abatement branch below is used only when both individual amounts are
non-negative, so the sum cannot be less than either individual amount.
Otherwise the statutory individual-or-sum tests in MD 13(3)(a)(ii) and
MG 3(2)(a)(ii) need separate interpretation and the component is
`needs_review`; an unexplained household total is never enough.

For this branch, the claimant must meet MC 5(2)'s own residence pathway for
the whole entitlement period: the prior continuous 12-month New Zealand
residence-and-presence test, daily YD 1 residence, and the transitional-resident
exclusion must each be verified. The emergency-benefit and child-residence
alternatives in MC 5(1)/(3) are outside this first branch, not grounds for a
zero entitlement. All children in this branch are under 18 throughout the tax
year; MC 9's Commissioner-determined extension for some 18-year-olds is outside
it. A competing caregiver or an MC 7 case where partners qualify for different
children also needs a separate determination and is unsupported here. Known
MC 6(a)-(c) payments must be checked by component and period; absence cannot
be inferred from a missing payment field. The claimant must also satisfy
MC 10(1)'s principal-care definition, including its exclusions for certain
institutional caregivers (WFF-01/06/07; Income Tax Act ss MC 3-10).

For the in-work component, the initial calculable branch requires a qualifying
salary/wage earner throughout the year, with no main benefit or Student
Allowance period and no unpaid work break. Self-employment can legally
qualify, but is outside this first branch until its facts and MD 9 pathway are
reviewed (`wff-ird-in-work-tax-credit`; Income Tax Act ss MD 4-10). For the
minimum family component, require documented full-time-earner weeks under
MA 7 (at least 20 hours for a single person or 30 combined hours for partners
per week, subject to ME 2's employment exclusions) and a separately verified
**net** family-scheme-income amount under s ME 3; gross
family-scheme income must not be substituted. For Best Start, the first
calculable branch is one qualifying child born from 1 April 2024 through
31 March 2025, eligible for the entire tax year, with no MC 6(c)
disqualifying payment for that child and no shared care. This keeps the
birth-cohort and part-period cases explicit
without guessing their apportionment (WFF-05/06; Income Tax Act ss ME 1-3,
MG 1-4; `wff-ird-minimum-family-tax-credit`, `wff-ird-best-start`). These
component branches define a limited v0.1 scope, not the entitlement of
households outside that scope.

Pete accepted this narrow v0.1 input boundary on 21 September 2026: stable
full-year household/care facts, a separately verified family-scheme-income
input, and a separately verified net family-scheme-income input for MFTC.
This is a scope decision, not a determination that all calculations below
are approved. Cases meeting Tax Administration Act s 80KW's 27-fortnight or
53-week extra-instalment conditions are outside the ordinary full-year branch;
the payment schedule must be checked, not inferred from the tax-year length.

The calculator must return per-component `calculated`, `unsupported`, or
`needs_review`, with a reason. Missing eligibility evidence, an unverified
income derivation, or unknown operative rate produces `needs_review`;
structurally outside-domain facts produce `unsupported`. Neither becomes a
numeric zero. A genuine, evidenced failure of an eligibility test may yield
zero for that component. Do not sum a partial result and present it as total
WFF entitlement (`policy_specs/SCHEMA.md`; WFF-01/02/07/08).

### Temporary in-work base: Task 10.2 rate-status contract

Section 105(1) substituted $7,670 for $5,070 in MD 10(3)(a) from
1 April 2026 (commencement s 2(40)). Section 105(2) reverses that substitution
on a single date set by Order in Council under s 2(43); if it has not begun by
1 April 2027, s 2(44) commences it that day. The Order is secondary legislation
under s 2(45). On 21 September 2026 the official s 2 page showed no secondary
legislation made under that section on the website, and a targeted official-site
search found no reversal Order (`wff-iwtc-increase-act-2026`). This check fixes
only the observed as-of position. It does not establish the rate for dates
after the check or certify the whole 2026-27 tax year.

| Evidence for modelled interval | Outcome for the in-work component |
| --- | --- |
| Official version and Order record establish no reversal throughout the entire completed, supported full tax year | Use $7,670 as the MD 10(3)(a) annual base, subject to all other eligibility, abatement, and approval gates. This row does not authorise a part-year annual formula. |
| Interval extends beyond the last Order check, including a full 2026-27 calculation requested on 21 September 2026 | `needs_review` for an unconditional annual in-work amount. A no-future-Order projection is a separately labelled scenario assumption, not verified law or a benchmark. |
| An Order is found with a commencement date within the modelled interval | Record the instrument and effective date; do not present an ordinary full-year $7,670 amount. The split-period annual entitlement path is `unsupported` until its statutory calculation and treatment are independently specified and reviewed. |
| Order status cannot be verified for the modelled interval | `needs_review`, not $7,670, $5,070, or zero. |
| Modelled period starts on or after 1 April 2027 | Recheck the operative MD 10 version and any later amendments; s 2(44) guarantees the s 105(2) reversal no later than this date, but does not establish all future policy values. |

MF 4L, inserted by s 106, expressly calculates **instalments** for 2026-27
if an early Order takes effect. Its pre-/post-change-date amounts do not by
themselves specify a full-year annual-entitlement apportionment. Do not infer
that annual formula from the instalment rule. The petrol-price description in
IRD guidance is context for a possible Order, not an operative rate switch
(`wff-income-tax-act`, s MF 4L; `wff-ird-temporary-increase`).

The `in_work_base` YAML row remains `needs_review`: its 2027-04-01 end is the
latest statutory reversal date, **not** an independently verified uninterrupted
rate interval. An implementation must source and record an as-of Order check
covering each modelled date before selecting a rate. It must not treat the YAML
row alone as permission to calculate an unconditional full-year amount.

### Scoped full-year calculation sequence

1. Select the law and parameter interval for the complete assessment period;
   apply the Task 10.2 rate-status contract above to the in-work component.
   A point-in-time Order check cannot verify a future full-year rate, and an
   unresolved in-work component cannot be silently included in total WFF.
   Check the official Order record again at implementation and for each
   modelled date (`wff-iwtc-increase-act-2026`, ss 2, 105-106).
2. Validate family membership, qualifying children, residence, care,
   component-specific MC 6 exclusions, the absence of an MC 7 claimant
   allocation, and family-scheme income. An MC 6(a) veterans' payment can
   disqualify abating WFF and Best Start for a relationship period, while
   MC 6(b) and (c) affect different components or children; do not collapse
   these into one household-wide test. The ordinary branch also excludes
   any applicable parental or child tax credit; MD 2 has a third abatement
   step for parental tax credit that is not modelled here. Calculate the
   full-year family tax credit as $7,921
   for the eldest qualifying child plus $6,454 for each additional qualifying
   child. For the ordinary full-year case, abatement is $0.275 times the
   number of **complete dollars** by which family-scheme income exceeds
   $44,900: `0.275 * floor(max(0, income - 44900))`. Under MD 2(2)(c),
   apply the abatement first to family tax credit, then any remainder to
   in-work tax credit. The component allocation is
   `family_credit = max(0, family_credit_base - abatement)` and
   `remaining_abatement = max(0, abatement - family_credit_base)`; no
   component is reported as a negative credit. Do **not** apply
   this ordinary formula to MD 14 protected-credit or per-child
   government-payment cases. An established MD 14/15 protected month is
   `unsupported` for this component; unknown applicability is `needs_review`.
   Those monthly income and payment pathways need their own specification
   (WFF-03/08; Income Tax Act ss MD 2-3, 13-15;
   `wff-tax-credit-order-2025`, cl 4;
   `wff-budget-measures-2025`, s 7;
   `wff-ird-family-tax-credit`).
3. If in-work eligibility is established, the full-year maximum for one to
   three children is $7,670, plus $780 for each child beyond three. Reduce it
   by `remaining_abatement`, with a zero floor (MD 2(2)(c)(ii)). If the claimant
   cannot receive family tax credit for a child due to a different payment,
   the separate direct-abatement pathway requires review and is unsupported
   in this scope (WFF-04/08; Income Tax Act ss MD 4-10, 13-15;
   `wff-ird-in-work-tax-credit`).
4. If minimum-family eligibility, MA 7/ME 2 full-time-earner weeks, and
   s ME 3 net family-scheme income are independently established, the
   all-52-week scoped amount is the positive
   difference between $36,604 and that net income. It does not abate with the
   family/in-work credits and must not be calculated from gross income alone.
   ME 3 defines the supplied net amount as adjusted income minus adjusted
   income-tax liability plus the specified MB 1(2) amount received minus
   the MB 1(3) amount paid; the input must attest to this derivation, not
   merely carry an after-tax label. ME 1(2)-(3) uses `weekly periods / 52`;
   this branch requires 52 verified full-time-earner weeks. A ME 2(2)-(4)
   Commissioner-determined employment period or part-week case is
   `unsupported`; an unverified tax derivation is `needs_review`. A verified
   net income at
   or above $36,604 yields no positive top-up, consistent with IRD's stated
   income limit; the zero-credit treatment is included in the reviewed
   scoped contract (WFF-05; Income Tax Act ss ME 1-3;
   `wff-ird-minimum-family-tax-credit`).
5. For the single full-year Best Start branch above, the scoped maximum is
   $4,041. For an abatable year, reduce it by 21 cents per **complete dollar**
   of family-scheme income over $79,000, with a zero floor. First-year
   pre-1-April-2026 births, later birth cohorts, births/third birthdays within
   the year, MC 6(c) disqualifying payments, and multiple eligible children require
   separate review; do not apply this branch to them or to months receiving
   protected Best Start credit under MG 4. An established MG 4 protected
   month is `unsupported` for this component; unknown applicability is
   `needs_review` (WFF-06/08; Income Tax Act
   ss MG 1-4; `wff-tax-credit-order-2025`, cl 6;
   `wff-ird-best-start`).

All amounts above are **annual entitlement candidates**, not weekly payment
figures. MD 3(2), MD 13(2), MG 2(1), and MG 3(1) use `days / 365`; ME 1(2)
and MD 10(2) use `weekly periods / 52`. The ordinary supported full-year
branch must verify 365 eligible days for day-based components and, when an
in-work or minimum-family credit is calculated, 52 qualifying whole weeks;
neither follows solely from a tax-year label. The Act's `complete dollar` rule applies
to income **excess** in MD 13(3)(a) and MG 3(2)(a), not to the credit amount.
MF 3-4 concern interim instalments: MF 4(4) requires the notice to show a
complete-dollar instalment, while IRD describes rounding each weekly or
fortnightly instalment down. Neither is an instruction to truncate an annual
component or an intermediate annual abatement. Instalments and annual
square-up are not in the initial calculation output (WFF-09; Income Tax Act
ss MD 3/10/13, ME 1, MG 2-3, MF 3-4; `wff-ird-family-tax-credit`). Preserve
the exact decimal annual result, including a possible half-cent from
MD 13's 27.5-cent rate; do not introduce cent or whole-dollar rounding in
the calculation core. Any later payment or presentation rounding needs its
own sourced rule. Section 80KW of the Tax Administration Act can alter
annual entitlement if the person receives 27 fortnightly or may have received
53 weekly instalments under the section's all-year payment conditions. If
that exception applies, return
`unsupported` in this first branch rather than the ordinary annual amount;
if its applicability is unknown, return `needs_review` (`wff-tax-administration-act`,
s 80KW(1)-(7)). No official example is promoted to `benchmarks.yaml`
or `spec_cases.yaml` by this approval.

### Source checks and implementation obligations

- Task 10.1 checked MD 1-3/10/13-15, ME 1-3, MG 1-4, and MF 1-4/4L against
  the official 4 September 2026 Act version on 21 September 2026. The
  ordinary 365-day/52-week formulas and MD 2 abatement order are linked
  to those provisions. Task 10.3 reviewed the assembled scoped contract;
  implementation and tests must preserve the partnered-income boundary,
  exact-decimal/half-cent handling, non-negative component handling, and
  MFTC zero-credit treatment.
- The relevant MB 1-13 and MC 2-11 provisions were checked against the
  official 4 September 2026 Act version on 21 September 2026; MB 9 and MB 14
  are repealed. Recheck the operative version for each later modelled date.
  Any branch not covered by this reviewed contract requires a new sourced
  specification and review, not an extrapolation from this one.
- The 2025 Tax Credit Order clauses 2/4-6, 2025 Budget Measures Act ss 2/7-8,
  and 2026 annual-rates Act ss 2/105-106 were checked in the earlier Task 10
  passes. The 21 September 2026 official s 2 check found no linked reversal
  Order. Search secondary legislation again for every later modelled interval;
  an unverified interval keeps the in-work outcome at `needs_review`.
- Pete accepted the narrow supported-domain boundary, including separately
  verified family-scheme income and net family-scheme income. New scope or
  interpretation decisions require a reviewed policy revision.
- Recalculate the dated IRD worked examples independently during Tasks 13-14;
  the shared-care page uses older rates and is not a 2026-27 benchmark.

The independent whole-spec review is recorded below. Tasks 11-15 must
implement and test this accepted scope without representing out-of-domain
households as zero entitlement. Component-level `validation_checks` remain
a Task 12 obligation, not a new eligibility rule.

## Task 10 follow-up: MD 4-9/14, MG 1-4 verification (Claude Code, 2026-09-21) — resolved

Both findings below are resolved as of PR #8/#9/#10 and superseded by the
Task 10.3 whole-spec review further down. Left here, marked resolved, for
the provenance trail rather than deleted. MD 5-9 matched the draft exactly
and needed no follow-up.

1. ~~MG 1(4)'s Tax Administration Act s 80KW citation missing from
   `sources.yaml`~~ — resolved: `wff-tax-administration-act` added to
   `sources.yaml` (PR #8) and the `extra_instalment_status` input, plus the
   s 80KW paragraph in the calculation sequence below, added (PR #9/#10).
2. ~~Best Start's calculation step didn't exclude protected-Best-Start
   (MG 4) cases~~ — resolved: step 5 now excludes "months receiving
   protected Best Start credit under MG 4" symmetrically with step 2's
   MD 14 exclusion (PR #8).

The reversal-Order check recorded here (2026-09-21) is superseded by the
Task 10.2 rate-status contract above, which is stricter: an as-of check
confirms no Order on that date, not the whole 2026-27 tax year.

## Task 10.3 whole-spec independent review (Claude Code, 2026-09-21)

Reviewed the complete source map, policy draft, calculation sequence, and
status outcomes as one document — not incrementally per PR — after
independently deriving expected behaviour from primary sources across the
PR #6/#8/#9/#10/#11 review passes (each already recorded its own
comparison; this pass checks the whole assembled result for internal
consistency, not individual claims again).

**No CODE_ERROR, SPEC_ERROR, or SOURCE_CONFLICT found.** The
`unsupported`/`needs_review` discipline is now applied consistently across
every component (FTC's MD 14/15, IWTC's direct-abatement pathway, MFTC's
ME 2(2)-(4), Best Start's MG 4, and the s 80KW extra-instalment case) —
known-and-excluded conditions consistently return `unsupported`, unverified
applicability consistently returns `needs_review`, and nothing collapses
either into a silent zero. Every `parameters[].source_id` resolves to a
`sources.yaml` entry. `policy.yaml`'s `assessment.unsupported` list matches
the household/eligibility exclusions described in prose exactly (six items,
checked one-for-one).

**One finding worth acting on before Task 12, not a correctness bug:**
`assessment.unsupported` consolidates the six household-level exclusions
into one machine-readable list, but the five component-level exclusions
(MD 14/15, the IWTC direct-abatement pathway, ME 2(2)-(4), MG 4, s 80KW) are
each stated only in prose, scattered across four different steps and one
table. Nothing is missing — every one of them is present and correctly
handled — but an implementer working from `policy.yaml` alone (the
executable contract) rather than reading every paragraph of this file
could plausibly miss one. This is exactly what the `validation_checks`
field in `ARCHITECTURE.md`'s simulation module contract is for — recommend
each `components[]` entry in `policy.yaml` gain a `validation_checks` list
naming its known exclusion triggers when Task 12 starts, rather than
leaving them prose-only. Not blocking Task 10's closure; a Task 12
implementation note.

**Reviewed revision:** this file and `policy.yaml`/`sources.yaml` as of PR
#11 (`docs/task10-temp-iwtc-rate`, commits `b937e2d` and `bf70d1b`).

## Task 10.4 acceptance (Pete, 2026-09-21)

Pete accepted the reviewed PR #11 revision after Task 10.3, including the
narrow full-year input domain, the component-specific `unsupported` and
`needs_review` outcomes, and the temporary in-work rate-status contract.
This acceptance assigns `policy_version: "0.1.0"` and `status: approved` to
the scoped WFF specification. It is not approval of a future, unverified
Order status or an unconditional full-year $7,670 in-work result. The
`in_work_base` value retains `review_status: needs_review`; Tasks 11-12 must
enforce the dated Order check through sourced policy state, with no live
network request inside the deterministic calculator. The component-level
`validation_checks` consolidation is carried to Task 12.
