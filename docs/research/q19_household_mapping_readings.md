# Q19 (1), (2) and (5): household mapping readings

Checked 12 October 2026 by GPT/Codex, after the
[Task 5–6 mapping review](../../reviews/2026-10-12-task5-6-mapping-codex.md).
Status: research for Pete's review; no mapping, refusal or protected value
has changed. The review records one P2 in AS category handling (`MAP-01`).

## Evidence and scope

Every source reading, comparison and design option in this document has
evidence class **AI hypothesis**. Source readings identify their prospective
class as **candidate Rule** (law) or **candidate Fact** (what official
guidance says). This notation does not promote AI-authored text before the
constitution's independent-review and, for interpretation, Pete-decision
gates. Probe/hypothetical inputs are **Scenario**; any observed calculation
is **Model output**, with its dependencies named. The project decisions
below are cited project authority, not statutory sources.

**Recorded standing decisions:** [Pete's 12 October decisions](../programme/2026-10-12-pete-approvals.md),
Q10/D36, and [D32](../decision_log.md): no apportionment across periods;
the caller supplies an amount for each policy period. The source passages
below that provide statutory annualisation or period formulae do not
authorise a change to that modelling contract. No application, outreach,
external policy-engine inspection or implementation occurred.

The review baseline is `1c19f64`; #207's final head is
`77ffc71f964060ee9c9a0fb5b8400ca0f53d539d`, merged as `cbc4f380`.
Line references below are to the baseline. The three mapping/household/unit
files are unchanged from #207's final head.

## Source register

All retrieved 12 October 2026. Legislation was obtained directly from the
official site with a browser user agent after the browser interface returned
403; returned version metadata/text was checked. Live guidance with no
displayed revision date is evidence as at the retrieval date only.

| ID | Primary source URL and version/as-at date | Locator | Actual support; prospective evidence class |
| --- | --- | --- | --- |
| S1 | [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/), version as at 26 September 2026 | ss 65, 68(2), 69(2), 423(3); Schedule 2, `cash assets` | Candidate Rule: AS tests the person's cash assets, including partner assets; lower asset thresholds impute income expressed per week from assets held. No universal stock snapshot weekday is specified in these provisions. |
| S2 | [Social Security Regulations 2018](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-09-04/), version as at 4 September 2026 | rr 15–18; Schedule 8 Part 1 | Candidate Rule: asset ceiling, asset exemptions, category/income rules. Exemptions can have their own time limits; the assessment week does not erase those limits. |
| S3 | [MSD, Change in assets](https://map.workandincome.govt.nz/map/income-support/extra-help/accommodation-supplement/changes-and-reviews-accommodation-supplement/change-in-assets-01.html), live as at 12 October 2026; no revision date displayed | introduction; Increase; Reduce, suspend or cancel; False or misleading information | Candidate Fact about guidance: asset changes require review; increasing AS generally uses the actual change date, reduction/suspension/cancellation generally the first available date with a late-notification exception, and false/misleading information the actual change date. |
| S4 | [MSD, Accommodation Supplement income rules](https://www.workandincome.govt.nz/on-a-benefit/tell-us/income/need-to-declare/accommodation-supplement.html), live as at 12 October 2026 | opening paragraph | Candidate Fact about guidance: income, one-off payments and assets received by the claimant or partner must be reported. It supplies no default weekly stock averaging rule. |
| S5 | [Income Tax Act 2007, Part Y](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1520573/), version as at 4 September 2026 | YA 1, `child`, `dependent child`, `financially independent`, `tax year` | Candidate Rule: WFF child/dependency conditions and exclusions, financial independence, and the 1 April–31 March tax year. |
| S6 | [Income Tax Act 2007, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/), version as at 4 September 2026 | MC 9–10; MD 6(1)–(3) | Candidate Rule: 18-year-old continuation is determined by the Commissioner, principal care has component-specific treatment, and IWTC expressly treats specified children as financially dependent despite the ordinary exclusion. |
| S7 | [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/), version as at 26 September 2026 | Schedule 2, `child`, `dependent child`, `financially independent`; Schedule 4 Part 7 cl 7 | Candidate Rule: governing AS dependency definition, special care routes and exclusions. The orphan's/unsupported-child's-benefit exclusion applies to Schedule 4 Part 7, which contains AS. |
| S8 | [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/), version as at 26 September 2026 | ss 103A, 103B(1)–(3), 103F(1)–(3),(7)–(8); amendment notes | Candidate Rule: from 4 September 2026, general exclusion after an 18th birthday follows the defined benefit entitlement period; MSD can continue/allow inclusion for a determined educational-continuation period. This is not an automatic under-18-only rule. |
| S9 | [IRD, Dependent child](https://www.ird.govt.nz/working-for-families/can-you-get-it/dependent-child), last updated 24 October 2025 | Dependent child – definition; Independent child | Candidate Fact about guidance: short explanation of age, care, relationship and financial dependence. It does not list every statutory component exception or replace MC 9's determination. |
| S10 | [MSD, Map changes in 2026](https://map.workandincome.govt.nz/map/changes/map-changes-in-2026.html), live as at 12 October 2026 | 4 September 2026, Changes when a child turns 18 | Candidate Fact about guidance: corroborates the commencement of changed turning-18 handling and possible continuation while studying and not financially independent. The Act's determination and period wording governs precision. |
| S11 | [Income Tax Act 2007, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/), version as at 4 September 2026 | MC 6(b), MC 8, MC 11; MD 4, MD 8, MD 10(3)(d); ME 1 | Candidate Rule: receipt exclusions, continuing requirements, relationship/entitlement periods, IWTC whole weekly periods and MFTC full-time-earner weekly periods. It does not equate one AS week with the entire WFF year. |
| S12 | [Income Tax Act 2007, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/), version as at 4 September 2026 | MB 2; MD 3; MD 13(3)(b), MD 14–15; MG 1–4 | Candidate Rule: FTC/Best Start entitlement-period formulae and calendar-month protection; protected-month income has its own definitions/adjustment. |
| S13 | [IRD, Government payments that affect your Working for Families](https://www.ird.govt.nz/working-for-families/types/government-payments), last updated 9 April 2026 | main-benefit row; payments added to family income | Candidate Fact about guidance: FTC and Best Start can coexist with a main benefit, IWTC and MFTC are excluded in relevant circumstances, and taxable benefits enter family income. The table is not a part-year entitlement formula. |
| S14 | [IRD, In-work tax credit](https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit), last updated 24 March 2026 | How the in-work tax credit works; note that figures are full-year entitlements | Candidate Fact about guidance: weeks worked and changing family circumstances affect entitlement; a full-year figure requires full-year requirements. No rate in this page is promoted by this research. |

The source/version dates are evidence about the retrieved texts. This
reading does not certify all historical dates in 2026–27: in particular,
S8's rules commence on 4 September 2026. Earlier turning-18 cases require the
applicable earlier version. No conclusion for an unexamined earlier version
is asserted.

## Q19 (1): the period and observation date of AS stocks

**Reading — AI hypothesis, candidate Rule/inference:** the asset ceiling,
lower imputation threshold, monetary imputation step and `cash_assets` are
amounts in currency. They are not amounts of income received during a week.
S1 distinguishes assets *held* from the weekly income imputed from them;
S2 r 15 applies the asset ceiling to the person's cash assets. The conversion
in S1 s 423(3) is a specific statutory relation between a stock and an
imputed weekly flow, not authority to divide a cash-asset balance by the
number of days in a period.

Three different dates/periods need to be kept distinct:

| Quantity | Reading and source | What remains unresolved |
| --- | --- | --- |
| Ceiling, imputation threshold and monetary step | Candidate Rule/inference: parameter amount with a legal applicability interval (S1–S2); the interval is not an observation interval for household assets. | How the registry will represent parameter applicability separately from its unit. |
| Household `cash_assets` | Candidate Rule/inference: balance of qualifying assets, after the applicable exclusions, at the circumstances being assessed (S1–S2). A dated observation is a plausible representation of that stock. | The retrieved provisions do not select the start, end, maximum or average of Poltika's arbitrary seven-day week. |
| Imputed income | Candidate Rule: explicitly a weekly income figure from the stock under s 423(3), feeding the non-beneficiary reduction (S1–S2 r 18). | The effect of an intra-week asset change and the operational date from which the revised payment applies. |

**Candidate Fact about guidance:** S3 requires review when assets change and
describes different effective-date rules by review action. S4 requires
reporting assets received. Together they weigh against treating a single
week-long balance as automatically constant. They still do not establish
one universal stock measurement instant for a calculator. S3 is operational
guidance with qualifications; this reading does not reconstruct every
review/backdating exception in the Act.

**Competing representations — AI hypotheses, not a selected interpretation:**

- A point-in-time balance with an explicit observation date and a separate
  assertion about its suitability for the requested assessment. This fits
  a stock's meaning but still needs an approved relation to the weekly view.
- A caller-supplied assessment-week asset fact, meaning the caller already
  resolved the relevant assessment/review circumstances. It must not imply
  that the stock was earned over the week or silently use an average.
- Keep timing unresolved and refuse calculations requiring a timing choice.

**Current mapping:** `semantics/unit_binding.py:96–98` labels `NZD`
`UNRESOLVED`, bundling stocks, thresholds and step size. This correctly
avoids a selected period, but cannot be described as verification of one.
`semantics/household.py:254–263` stores `Housing.cash_assets` with no date;
`scenarios/household_mappings.py:329–331` copies it for any requested week.
The model therefore lacks an observation/applicability relation. A legal
change mid-week cannot be represented by this field. The standing narrow
slice and refusal policy should remain until Pete settles the contract.

**Possible implication:** a later mapping change may separate unit dimension,
parameter validity and household stock observation, or retain a deliberately
attested assessment-week fact. No general amount conversion, averaging or
apportionment follows from this research. **Unverified:** a universal AS
stock snapshot date or intra-week asset-change amount rule.

## Q19 (2): WFF and AS dependent children

**Reading — AI hypothesis, candidate Rule:** the definitions share care,
family membership and financial dependence, but their age rules, assistance
exclusions, exceptions and effective periods differ. The governing AS source
is **Social Security Act 2018 Schedule 2**, applied to **Schedule 4 Part 7**,
with relevant turning-18 provisions in **ss 103A–103F**. AS r 17 uses
dependent children in its categories; it does not substitute an IRD child
definition for the Act's definition.

| Point | WFF (S5–S6) | AS (S7–S8) |
| --- | --- | --- |
| Basic dependency | Care primarily the person's responsibility; maintained as a family member; financially dependent. | Same broad three conditions, with the Act's explicit alternative care route. |
| Child's relationship and age | YA 1 excludes marriage/civil union/de facto relationship; ordinary under-16 children, 16/17 not financially independent, and an 18-year-old through the specified credit route. MC 9 permits Commissioner-determined continuation for study and financial dependence. | Schedule 2 `child` is a single person under 18, excluding financially independent 16/17-year-olds. From 4 September, ss 103A–103F address continuation at 18 where the applicable criteria/determination exist. |
| Financial independence | YA 1 includes full employment, specified student grants, analogous government assistance, receipt of a Social Security Act **benefit**, and specified superannuation/pension-equivalent assistance. | Schedule 2 includes full employment, specified student grants, analogous assistance and receipt of a **main benefit**. These terms differ; do not substitute one test. |
| Orphan's/unsupported child's benefit | Ordinary YA 1 exclusion for WFF other than Best Start; Best Start has an express inclusion. MD 6(2)–(3) separately treats these children as financially dependent for IWTC and overrides MC 8. | Schedule 2 excludes these children for the listed Schedule 4 Parts, including Part 7 (AS); Part 7 cl 7's formula definition confirms the exclusion. |
| Oranga Tamariki care | YA 1 excludes specified s 363 payments for WFF other than Best Start, with an express parental s 361/362 return-to-care inclusion; Best Start expressly includes specified care payments. | Schedule 2 has a s 363 payment exclusion and the s 361/362 parental placement route. |
| Young-parent payment circumstance | No matching blanket exception is stated in the YA 1 dependent-child definition; all other WFF tests still apply. | Schedule 2 expressly excludes a child in respect of whom a young parent payment is paid in relation to someone who is not the child's parent/step-parent. |
| Period and institutional determination | MC 9 period is determined by the Commissioner; its endpoint is linked to the first tax-credit instalment date in the following calendar year. Principal caregiver/shared care is component-specific under MC 10. | Section 103A defines benefit entitlement periods; s 103B exclusion uses the first such period wholly after the birthday. Section 103F continuation is determined by MSD and capped by its specified period after 31 December. |

S9 and S10 are useful summaries, not replacements for the exceptions in the
table. An 18-year-old is not automatically included under either policy,
and “AS always stops on the 18th birthday” is not supported by the current
Act. The current source evidence supports differences between the two
definitions; it does not prove that all AS children form a subset of all
WFF children or that different counts are contradictory.

**Current mapping:** `semantics/household.py:186–198` keeps
`qualifies_whole_year` and `as_dependent_child`; `Family:235–241` separates
list completeness. This is supported for transporting two caller-resolved
facts in the narrow full-year WFF slice. A single shared dependency flag
would lose the demonstrated differences. For broader WFF coverage, one WFF
flag also cannot express the component exceptions; the ordinary WFF child
list is not automatically an IWTC/Best Start membership set.

`to_wff` at `household_mappings.py:157–170` passes **every** family child
to the WFF list, whereas `to_as:303–310` counts AS-verified statuses.
Consequently a household holding an AS-only or component-only child cannot
be made a fully supported WFF input simply by adding that child to the
shared list. The current code is a limited representation, not authority
to resolve those memberships.

The adapter at `household_mappings.py:445–491` treats an AS count no greater
than the WFF count as first-N synthetic AS membership and refuses a greater
count. The inputs contain no child identities, so neither the subset
relationship nor those individual statuses is established by the counts.
This is an engineering reconstruction for an unchanged aggregate round
trip; it must not be promoted to verified real-person membership. Equal
counts also do not identify the same children. The retained check at
`scenarios/combined.py:163–166` is a conservative count check, not a legal
equivalence rule.

**Possible implication:** keep separately asserted statuses for the
supported slice, with scope and periods explicit; or commission
component-specific WFF membership and a count-only adapter contract before
expansion. **Unverified:** identity matching from the current count-only
inputs. Neither dropping the AS fact nor treating the first-N reconstruction
as statutory truth is supported by these sources.

## Q19 (5): weekly main-benefit receipt inside a WFF tax year

**Reading — AI hypothesis, candidate Rule:** a weekly spell is evidence for
the interval it asserts, not for receipt/non-receipt in the rest of the tax
year. The WFF tax year contains relationship and entitlement periods; MC 11
expressly permits some or all days of a year. MC 8 defines continuing
requirements, including changes in credit composition and protected FTC
status. MC 6(b) excludes the named credits where main-benefit receipt occurs
in the relevant relationship period; MD 8 also tests the spouse/partner for
IWTC. The statute supplies component-specific consequences, not one common
annual “on benefit” switch (S11–S12).

| Component | Retrieved governing provisions | What the source actually supports |
| --- | --- | --- |
| FTC | MC 2–11; MD 3(2),(5); MD 13(3)(b); MD 14–15 (S11–S12) | Main-benefit receipt alone does not exclude FTC. Entitlement uses days in its entitlement period. Protected FTC depends on benefit receipt **and** the specified family-income condition in a calendar month, with MD 15's income adjustments and MB 2's annualised equivalent. A benefit week alone does not establish protection. |
| IWTC | MC 6(b); MD 4, MD 8, MD 10(3)(d) (S11) | Relevant receipt by claimant or partner prevents the not-receiving-benefit requirement. Calculation counts whole weekly periods of qualifying continuous entitlement/work as specified; annual income and one positive benefit week do not prove all other weeks qualify or fail. |
| MFTC | MC 6(b); ME 1(1)–(3); ME 3 (S11–S12) | Receipt exclusion and a calculation using qualifying full-time-earner weekly periods, with ME 3 net family scheme income for the relevant relationship period. A weekly receipt flag cannot supply that income or eligible-week count. |
| Best Start | MC 6(c); MG 1–2; MG 3(2)(b)(ii), MG 4 (S12) | A main benefit alone does not exclude Best Start. Its specific disqualifying payments/child conditions remain separate. Protection is assessed by calendar month with a benefit/income test; the abatement excludes days of protected months. |

S13 corroborates coexistence/exclusion distinctions. S14 describes varying
entitlement with weeks worked and changing circumstances. Neither agency
page settles the precise part-year boundaries by itself.

**Distinguish a check from a calculation:** a positive, asserted main-benefit
spell overlapping the tax year contradicts a claim that no main benefit was
received anywhere in that year. Checking overlap uses dates and does not
apportion an amount. Conversely, absence of a listed spell is not verified
absence of benefits; a partner's receipt also matters for MD 8. A spell
straddling the tax-year boundary cannot be scaled to produce an amount under
Q10/D32. This distinction does not authorise deriving statutory eligible
weeks, relationship periods or protected months from an incomplete record.

**Competing uses — AI hypotheses requiring Pete's scope decision:**

- Retain the current whole-year caller assertions and conservatively flag
  any overlap that conflicts with an explicit whole-year “no benefit”
  assertion; preserve partial-year/protected-period refusal as applicable.
- Commission an explicit relationship/entitlement-period contract for each
  component, with relevant receipt, partner and calendar-month income facts.
  The caller still supplies each required amount for its policy period;
  no new amount apportionment follows automatically.
- Keep the unresolved part-year relation as a `needs_review` gate while
  continuing supported standalone calculations.

Choosing a blanket “one week means the entire year's statutory entitlement
is zero” is not justified by the retrieved formulae. Choosing “one benefit
week has no consequence because it does not cover the year” is likewise not
justified. This reading selects neither an interpretation of particular
receipt/relationship-period boundaries nor an amount for a part-year case.

**Current mapping/conflicts:** `to_wff` at
`household_mappings.py:233–239` copies bundle assertions and does not inspect
benefit spells. `to_as:278–285` inspects the claimant's week, with the P2
partial-overlap defect in the preceding review; that defect does not require
a WFF policy interpretation to fix. `to_combined:341–357` retains the pair.
`combined.py:135–161` flags a main-benefit week against asserted annual
IWTC/MC 6(b)/protected-credit gates. Its whole-year non-receipt check is a
conservative supported-slice check; its protected-credit checks are explicitly
conservative because the scenario lacks monthly income. A main-benefit week
alone cannot establish a protected month under MD 14 or MG 4. Any replacement
must preserve that distinction instead of turning the current conservative
flag into a derived legal status.

**Possible implication:** retain the reviewed amounts and refusal contract
until the period relation is decided. A later household check can establish
date overlap as evidence while leaving component entitlement/protection
unknown. It needs both claimant and partner where the relevant provision
requires them. The generic AS category `NZ_SUPER_OR_VETERANS_PENSION` is not
by itself a WFF main-benefit spell; nor does a claimant-only AS category
establish partner non-receipt. **Unverified:** a precise automated rule for
turning these current, incomplete spells and annual assertions into statutory
relationship periods, eligible weeks, monthly protection or part-year amounts.

## What Pete decides

- Q19 (1): retain unresolved stock timing, approve dated observation plus an
  explicit assessment relation, or retain a caller-resolved weekly assessment
  assertion. A universal snapshot/average must not be assumed from these sources.
- Q19 (2): retain separate caller-resolved WFF/AS facts in the existing slice,
  or commission component-specific child membership/periods; decide how
  count-only synthetic child alignment is labelled or refused before reuse.
- Q19 (5): retain whole-year assertions and conservative refusals, retain a
  review gate for partial-year relations, or commission a sourced component
  period design. The caller continues supplying policy-period amounts under
  Q10/D32. The authorised retirement of household pairwise checks still waits
  for this reading's review and the resulting approved relation.
