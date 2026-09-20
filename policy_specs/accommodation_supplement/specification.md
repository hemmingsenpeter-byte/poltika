# Accommodation Supplement specification

**Status:** Task 2 independent source map complete on 21 September 2026; not an
approved implementation specification. **Reference period:** September 2026.
Source IDs below refer to [sources.yaml](sources.yaml). Task 22 must turn this
map into a scoped, reviewed calculation specification before values or examples
become protected tests. No external implementation was consulted.

## Statutory structure

The Social Security Act 2018, ss 65AAA-69 and Schedule 4 Part 7 (`as-social-security-act`),
and Social Security Regulations 2018, rr 15-19 (`as-social-security-regulations`),
govern entitlement, costs, assets, base rate, income reductions, and rounding. MSD's Map
pages describe current administration but do not override the legislation.

| ID | Source-grounded policy meaning | Authority and check |
| --- | --- | --- |
| AS-01 | Entitlement requires accommodation costs, satisfaction of the asset requirement, and no social-housing or other-funding exclusion. General residence and age rules, student-allowance alternatives, and actual occupancy also matter. | Act ss 16, 19, 65AAA-67 and Schedule 2 definitions; `as-msd-qualifications`, `as-msd-residence`, `as-msd-students`. Apply the exceptions by claimant, not a single student or residence flag. |
| AS-02 | Rent, board, and home-ownership costs are distinct inputs. Service costs and arrears can be excluded; homeowners have defined eligible outgoings. A client generally claims one cost type at a time. | Act s 65AAA; `as-msd-rate-method`, `as-msd-qualifications`. Check mixed-tenure and joint-tenant cases separately. |
| AS-03 | Weekly qualifying accommodation costs deduct the cost of any part of a property not lived in by the claimant, then accommodation income. For a boarder paying board, MSD treats 62% of their board as accommodation costs. A claimant receiving board normally deducts 62% of those receipts as accommodation income. | Act Schedule 4 Part 7 cl 7; `as-msd-qualifying-costs`, `as-msd-rent-board-examples`. These are different roles; do not apply both 62% treatments to one payment. |
| AS-04 | The rate starts from 70% of positive weekly qualifying costs above the applicable entry threshold, then is limited by household category and one of four geographic-area maxima. Rent/board and homeowner thresholds differ. | Act Schedule 4 Part 7 cls 1-6; Regulations r 17; `as-msd-rate-method`, `as-msd-rates-2026`. Select the base-rate category and threshold before calculating. |
| AS-05 | The area lookup uses Statistical Area Units, not a postal suburb or city name. | `as-msd-areas`; Act Schedule 4 Part 7. A location input without a verified area must not silently default to Area 4. |
| AS-06 | Cash assets above the statutory ceiling prevent entitlement. For non-beneficiaries, $1 weekly income is imputed per $100 of assets above a lower threshold. Partner assets can be included, subject to statutory exceptions. | Act ss 68-69, 423(3); Regulations rr 15-16 and Schedule 8 Part 1; `as-msd-assets`. Exempt assets and exceptional asset-limit increases require separate facts. |
| AS-07 | A non-beneficiary's weekly chargeable income above the relevant threshold reduces the assessed rate by 25 cents per dollar. The base rate is capped before income reduction, and the final positive amount is rounded up to a whole dollar. | Regulations rr 17-19; `as-msd-income-method`, `as-msd-income-2026`, `as-msd-income-example`. Fractional income handling has a conflicting agency example, recorded below. |
| AS-08 | MSD says a claimant on a main benefit generally has no separate Accommodation Supplement income test; NZ Superannuation and Veteran's Pension recipients do. | `as-msd-beneficiaries`; Regulations rr 17-18. Do not use non-beneficiary income thresholds for every claimant. |
| AS-09 | Couples in a joint tenancy are treated as one joint tenant for their qualifying costs, income, and assets; community partners have special rate treatment. | Act s 68 and Schedule 4 Part 7 cl 6A. Check shared-property facts before combining households. |
| AS-10 | WFF tax credits paid by Inland Revenue are listed by MSD as excluded from non-beneficiary Accommodation Supplement chargeable income. Conversely, IRD excludes non-taxable Accommodation Supplement from WFF family income. | Act Schedule 2 income definition, Schedule 3 cl 8; `as-msd-chargeable-income`, `as-ird-other-income`. The MSD-paid WFF route is not established by that IRD-paid wording. |
| AS-11 | Assets, income, housing costs, family status, and location can all change an award; the Act allows refusal, reduction, or cancellation in specified circumstances. | Act s 69; `as-msd-overview`. Change-date and reassessment rules still need mapping. |

## Qualification and claimant branches

| Branch | Source-grounded consequence |
| --- | --- |
| Residence and age | General Act ss 16 and 19 govern residence/presence; MSD requires citizenship or a residence-class visa and ordinary residence, but no minimum residence duration for this payment. Financially independent 16-17 year olds are a separate branch under the Schedule 2 definition. |
| Home and housing funding | Section 65AAA bases costs on the premises where the claimant resides. Section 66 excludes specified social-housing/concessionary mortgage costs; a boarder in social housing may still be eligible because the claimant's own board is a different cost. |
| Student funding | Section 67 excludes a recipient of, or a person who could receive, the specified Student Allowance grant. MSD says an income-only Student Allowance decline does not bypass that exclusion; a decline for another reason or exhausted entitlement may. A non-student partner may claim, with any student Accommodation Benefit deducted (`as-msd-students`, `as-msd-student-partner`). |
| Other support | Section 67 also covers a partner already receiving Accommodation Supplement, subject to s 68, and specified residential-care funding. Section 69 contains separate refusal, reduction, and cancellation grounds; these are not ordinary zero-rate branches. |
| Claimant rate class | Regulations rr 17-18 distinguish beneficiary and non-beneficiary treatment. Main-benefit recipients generally have no separate AS income test; NZ Superannuation and Veteran's Pension recipients instead face the s 67/Schedule 5 income limit (`as-msd-beneficiaries`, `as-msd-pensioners`). Use separate Jobseeker, Sole Parent, Supported Living, non-beneficiary, pension, and mixed-benefit-couple thresholds, then area/household caps. |
| Assets | Apply the r 15 cash-asset ceiling after r 16/Schedule 8 exemptions; s 423(3) supplies the lower-threshold non-beneficiary imputation. Impairment/independence lump sums and community-spouse cases need their statutory exceptions, not a universal cap. |

## Calculation order and cross-policy boundary

For an ordinary assessed case: determine qualifying weekly costs under Schedule
4 Part 7 cl 7, subtract the applicable entry threshold, take 70% of any
positive excess, cap by household and area, then apply any r 18 non-beneficiary
income reduction. A non-positive result pays zero; r 19 rounds the final
positive amount **up** to the complete dollar. At the exact entry threshold,
the cost-based amount is zero. MSD's general worksheet rounds excess weekly
income down to a whole dollar before multiplying by 25%, but its student-partner
example multiplies a fractional $54.14 directly. This is a source discrepancy,
not a licence to choose silently (`as-msd-income-method`,
`as-msd-student-partner-example`).

The policies have different income definitions. IRD explicitly says a
non-taxable Accommodation Supplement is not WFF family income
(`as-ird-other-income`). MSD explicitly excludes **IRD-paid** WFF credits from
non-beneficiary AS income (`as-msd-chargeable-income`). Whether every MSD-paid
WFF component is treated identically remains a distinct verification gate;
do not collapse payment channel into entitlement type.

## Dated parameter and amendment map

These observations are not accepted test values. `sources.yaml` links to the
complete agency tables; no single household table covers all benefit statuses.

| Effective period | Observation | Source |
| --- | --- | --- |
| From 2 March 2026 | The 2025 Amendment Act revised the accommodation-cost and weekly-qualifying-cost provisions. MSD explicitly separates calculations before and after this date. | `as-2025-amendment`; `as-msd-qualifying-costs`. |
| From 1 April 2026 | MSD publishes separate entry-threshold tables for non-beneficiaries, Jobseeker Support, Sole Parent Support, Supported Living Payment, pension recipients, and mixed-benefit couples. Maximum weekly rates are grouped by household category and Area 1-4. | `as-msd-rates-2026`, `as-msd-jobseeker-rates-2026`, `as-msd-sole-parent-rates-2026`, `as-msd-supported-living-rates-2026`, `as-msd-pension-rates-2026`, `as-msd-mixed-benefit-rates-2026`. |
| Current asset settings | Regulation 15 gives a $8,100 ceiling for a single person without dependent children and $16,200 for a couple or sole parent. MSD describes lower $2,700/$5,400 thresholds for non-beneficiary asset-income imputation. | Regulations r 15; `as-msd-assets`. Check exemptions and rounding. |
| From 1 April 2027 | The 2026 Amendment Act changes homeowner entry-threshold percentages for specified claimant groups. Its transitional provision applies the accommodation changes on and after this date, including some existing grants. | `as-2026-amendment`, Part 2 and Schedule 2. Exclude from September 2026 calculations. |

## Benchmark candidates

`as-msd-rent-board-examples` provides a 2026 rent example and a separate board
example; `as-msd-income-example` shows the non-beneficiary income reduction
and final rounding. `as-msd-qualifying-costs` gives a business-use and boarder
example. Each candidate needs the matching dated rate table and an independent
recalculation before it becomes a protected benchmark.

## Task 22 and review gates

- Resolve the fractional-income discrepancy above against operative law and
  agency practice before setting a rounding fixture. Also verify whether
  s 423(3)'s $100 asset steps mean complete or partial hundreds in practice.
- Confirm the statutory basis and treatment of MSD-paid WFF components before
  any combined-policy scenario relies on that route.
- Select a supported household/tenure/benefit domain. Unsupported student,
  pension, mixed-benefit, care, joint-tenancy, asset-exemption, or geographic
  cases must return needs-review, not a false zero or default Area 4.
- Independently recalculate selected dated MSD examples with their correct
  threshold table and location before promoting them to protected benchmarks.
- Independently review effective dates, discretionary s 69 paths, reassessment
  timing, and the supported-domain decisions. Pete decides genuine ambiguity.
