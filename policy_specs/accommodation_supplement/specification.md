# Accommodation Supplement specification

**Status:** Task 2 independent source map complete on 21 September 2026; Task
22's scoped calculation contract drafted 22 September 2026 (see below); not
yet an approved implementation specification -- Pete's acceptance decision is
still pending, including one escalated ambiguity. **Reference period:**
proposed 2026-03-02 to 2027-04-01 (see the Task 22 contract below; supersedes
the earlier "September 2026" placeholder). Source IDs below refer to
[sources.yaml](sources.yaml). No external implementation was consulted.

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

## Proposed Task 22 scoped calculation contract (draft, not yet accepted)

**Drafted:** 22 September 2026, working from the Task 2 source map above plus
direct re-checks of the Social Security Act 2018 (`as-social-security-act`)
and Social Security Regulations 2018 (`as-social-security-regulations`)
official text (legislation.govt.nz, browser user-agent, since a bare fetch
403s -- the same access pattern this project already established for WFF).
**Not approved.** Mirrors WFF's Task 10 pattern: a narrow, explicit v0.1
input domain plus a scoped calculation sequence, presented for Pete's
acceptance decision, not self-accepted here. One question below is left as a
genuine, unresolved ambiguity for Pete to decide, not silently picked.

### Two review-gate questions, resolved or escalated

**s 423(3) asset-to-income imputation -- resolved directly from the Act
text, no escalation needed.** Checked s 423(3) itself (2026-09-22): "the
following must be treated as $1 a week of income: (a) every $100 of cash
assets over $5,400 held by [a person in a relationship, or a single person
with a dependent child or children]; and (b) every $100 of cash assets over
$2,700 held by any other person." "Every $100" only has a coherent reading
as counting complete $100 increments of the excess -- there is no partial-
hundred treatment stated or implied, unlike the genuine gap below. This
matches the same complete-unit floor discipline WFF's MD 13(3)(a)/MG 3(2)(a)
already established for this project (`_complete_dollar_excess()` in
`wff.py`), not a new invention.

**Regulation 18(2)'s income-excess rounding -- genuine, unresolved
ambiguity. Escalating to Pete, not deciding it here.** Checked r 18(2)
directly: "That amount must be reduced by 25 cents for every $1 of the
relevant weekly income... in excess of the income level specified in
subclause (3)." Unlike WFF's MD 13(3)(a) ("0.275 times the number of
**complete dollars** by which family-scheme income exceeds..."), r 18(2)
contains no "complete dollar" instruction for the income *excess* itself --
it is genuinely silent on whether that excess is rounded/floored to a whole
dollar before the 25% reduction is applied. Regulation 19 ("Rounding")
only governs the *final* accommodation supplement amount ("must be rounded
up to the complete dollar"), not this intermediate step; s 423(1)(f)'s
enabling power is likewise only about rounding "assessed amounts of
accommodation supplement" (the final figure), not the income excess. Two
MSD pages read this two different ways: `as-msd-income-method`'s general
worksheet rounds the excess weekly income down to a whole dollar before
multiplying by 25%; `as-msd-student-partner-example`
(`as-msd-student-partner-example`) applies the reduction directly to a
fractional $54.14. Neither the Act nor the Regulations resolve which
reading is correct -- this is either SOURCE_CONFLICT (MSD's own two pages
disagree) or INTERPRETATION_AMBIGUITY (the Regulations are simply silent
and either reading is defensible), and per Review Doctrine and this
policy's own `decisions/README.md`, that decision belongs to Pete, not to
an implementer picking whichever makes an example match. The scoped
contract below marks the income-reduction step's rounding treatment as an
open decision gate, not a chosen convention, until Pete records it as a
`DEC-NNN` decision artifact.

**AS-10 (MSD-paid WFF exclusion) -- statutory basis confirmed to exist,
full AS/WFF interaction not resolved (out of this task's scope).** The
Act's own definitions section cross-references "WFF tax credit" (defined
via Income Tax Act 2007 s YA 1, through ss 98/428) directly against
"clause 8(l) of Schedule 3" as the income-exclusions schedule. This
confirms Schedule 3 cl 8 is a real, existing statutory income-exclusion
list that specifically names WFF tax credit, corroborating (not
independently re-deriving the full text of) `specification.md`'s existing
AS-10 citation. The deeper question -- whether every *MSD-paid* WFF
component receives the same treatment as the *IRD-paid* route Schedule 3
cl 8 and the IRD source both describe -- remains open, exactly as AS-10
already says, and is Task 28's problem (WFF + AS interaction), not this
task's.

### Proposed v0.1 supported domain

One claimant, optionally with a partner in an ordinary (non-joint-tenancy,
non-community-spouse) relationship. Rent, contributions, or board payments
only (Schedule 4 Part 7 cl 1-3, 25%-of-base-rate entry threshold) --
homeowner accommodation costs (cl 4-6, 30%-of-base-rate entry threshold,
mortgage-security "reasonably required" MSD judgment) are a deliberately
separate, unsupported branch for v0.1, the same kind of narrowing WFF used
for self-employment income under the in-work tax credit. Claimant category
limited to Jobseeker Support, Sole Parent Support, Supported Living
Payment, or non-beneficiary (r 18's ordinary income-reduction route) --
NZ Superannuation/Veteran's Pension recipients (a structurally different
s 67(e)/Schedule 5 income-*limit* exclusion, not an r 18 reduction) and
mixed-benefit couples (a separate half-married rate table) are unsupported
for this first branch. This is a deliberately narrow input contract, not a
claim that other households or claimant categories receive no entitlement
(the same framing WFF's Task 10 contract used).

Unsupported (must resolve to `unsupported` or `needs_review`, never a
false zero or a silent default):

- Social housing exclusion (s 66) or other-funding exclusion (s 67) applying
  -- including the disability/care-funding branch of s 67(d), which the
  existing Task 2 table did not separately name as its own trigger.
- Student Allowance exclusion or exception (s 67(b), the student-partner
  branch) -- not calculated in this branch even though it is exactly the
  branch containing the unresolved rounding question above.
- Joint tenancy (s 68) or community spouse/partner (Schedule 4 Part 7
  cl 6A) treatment.
- NZ Superannuation/Veteran's Pension claimant category, or a mixed-benefit
  couple.
- Any s 69 discretionary refusal, reduction, or cancellation ground.
- Homeowner accommodation costs (cl 4-6).
- An unverified Statistical Area Unit -- a location input without a
  verified Area 1-4 classification must not silently default to Area 4
  (`as-msd-areas`; already stated in the Task 2 map, restated here as a
  binding contract term).
- Cash assets at or above the r 15 ceiling (a genuine, evidenced zero via
  the assets requirement, not a scope limitation -- distinct from the
  s 423(3) imputation above, which applies *below* that ceiling).
- Any exempt cash asset requiring Part 1 of Schedule 8's own
  determination (r 16) -- not modelled in this branch; exemptions must be
  verified, not assumed absent.
- A weekly qualifying accommodation costs calculation involving
  accommodation income from boarders or sub-letting, or business use of
  part of the premises (Schedule 4 Part 7 cl 7's `b`/`c`/`d`/`f` terms) --
  the first calculable branch is the plain case (`b = c = d = f = 0`,
  i.e. the claimant's own accommodation costs, no sub-letting, boarding,
  or business use), matching WFF's own "narrow, add complexity later"
  precedent; the fuller formula is documented above for when this is
  extended, not implemented in v0.1.

### Scoped calculation sequence (v0.1 domain only)

1. Verify household eligibility: accommodation costs exist (s 65AAA), no
   social-housing exclusion (s 66), no other-funding exclusion applicable
   (s 67, including the disability/care branch), no s 69 refusal/
   reduction/cancellation ground applicable, cash assets below the r 15
   ceiling for the claimant's relationship/dependent-child category
   ($16,200 or $8,100, checked directly against the regulation text,
   2026-09-22), Statistical Area Unit verified to an Area 1-4
   classification. Any unverified or excluded condition returns
   `unsupported`/`needs_review` for the whole calculation, before any
   component-specific step -- the same household-gate-first pattern
   `_household_gate_failure()` already established for WFF.
2. Calculate weekly qualifying accommodation costs under the plain-case
   formula (Schedule 4 Part 7 cl 7, `b = c = d = f = 0`): the claimant's
   verified weekly accommodation costs, unreduced.
3. Select the entry threshold: 25% of the claimant's base rate (rent/board
   tenure, cl 1-3). The base rate itself is set per claimant category
   (Jobseeker/Sole Parent/Supported Living/non-beneficiary) by the
   relevant dated MSD table (`as-msd-jobseeker-rates-2026`,
   `as-msd-sole-parent-rates-2026`, `as-msd-supported-living-rates-2026`,
   `as-msd-rates-2026`) -- Task 22 does not independently recalculate or
   promote these dated tables to protected values; that is Tasks 23-24's
   job. The parameter carries `review_status: needs_review` until then.
4. The cost-based amount is 70% of the positive excess of qualifying costs
   over the entry threshold, capped at the applicable Area 1-4 maximum for
   the claimant's household category. These caps are **statutory, not
   agency guidance** -- confirmed directly in Schedule 4 Part 7 cl 1-3
   itself (checked 2026-09-22, current since the 2 March 2026 amendment,
   with no further 1 April 2026 Order amendment found for this clause):
   household with 1+ dependent children in a relationship, or a sole
   parent with 2+ dependent children -- $305/$220/$160/$120 (Areas 1-4);
   no dependent children in a relationship, or a sole parent with 1
   dependent child -- $235/$155/$105/$80; any other person (a single
   claimant with no dependent children) -- $165/$105/$80/$70. A
   non-positive excess pays a genuine calculated zero for this component
   (at the exact entry threshold, the cost-based amount is zero), not
   `unsupported`.
5. If the claimant is a non-beneficiary (r 18's route, not the s 67(e)
   pension-income-limit route), reduce the capped amount by 25 cents per
   $1 of relevant weekly income (combined with any partner's, unless the
   claimant is a community spouse/partner, which is unsupported in this
   branch) in excess of the applicable jobseeker-support-equivalent income
   level (r 18(3)(a)-(c)). Add $1 of imputed weekly income per complete
   $100 of cash assets over the s 423(3) threshold ($5,400 or $2,700,
   confirmed directly against the Act text) before applying this
   reduction. **The rounding treatment of the income excess itself is the
   open decision gate above -- do not implement either MSD convention as
   the accepted rule until Pete decides.** A result at or below zero after
   this step pays zero, not `unsupported`.
6. Round the final positive amount up to the complete dollar (r 19) --
   confirmed this governs only the final figure, not any intermediate
   step.

### Note for Task 25 (schema stress test)

AS is assessed on an ongoing weekly basis, reassessed on a change of
circumstance, not against a fixed annual membership period the way WFF's
`assessment.membership_period: tax_year` is -- `SCHEMA.md`'s "allowing
relationships and care to change within a tax year or **benefit week**"
already anticipated this. `reference_period` (below, tracking which
*statutory version* applies) and `assessment.membership_period` (the
*assessment's own* periodicity) are two different things for AS in a way
they weren't clearly distinguished for WFF -- flagging this now as
specification.md's own contribution to Task 25, not solving the schema
question here.

### Source checks and implementation obligations

- Task 2's source map (`sources.yaml`, dated 2026-09-21) remains the
  primary-source inventory; this section adds direct 2026-09-22 re-checks
  of ss 65AAA-69, 423, Schedule 4 Part 7 (cl 1-8), and Regulations rr
  15-19 against the official "latest" consolidated text
  (legislation.govt.nz, browser user-agent). Schedule 3 cl 8's exact text
  was not independently re-fetched this session -- only its existence and
  WFF-tax-credit cross-reference were confirmed (AS-10 above); recheck
  before relying on its exact wording.
- Recheck the operative version of every cited provision at
  implementation and for each later modelled date, per this project's
  established discipline -- particularly Schedule 4 Part 7's cl 1-6 caps,
  which are Act-level dollar figures rather than annually-indexed Order
  amounts, and the 2027-04-01 homeowner threshold change (`as-2026-
  amendment`), which is out of scope for a September 2026 reference
  period but must be rechecked before modelling any later date.
- Dated MSD rate/threshold tables (entry thresholds by claimant category,
  jobseeker-equivalent income levels) are not independently recalculated
  or promoted to protected values by this task -- they carry
  `review_status: needs_review` in `policy.yaml` until Tasks 23-24's
  benchmark process, matching WFF's `in_work_base` precedent for a
  parameter whose contract shape is settled before its exact dated value
  is.
- Pete accepts or declines this scoped contract, and decides the r 18(2)
  rounding ambiguity, recording that decision under
  `decisions/DEC-NNN-<topic>.md` per `decisions/README.md` -- not
  self-accepted or silently resolved here.
