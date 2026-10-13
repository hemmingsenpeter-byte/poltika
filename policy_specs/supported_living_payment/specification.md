# Supported Living Payment — restricted-work-capacity existing-grant draft

**Status:** `draft_pending_review`. **Policy:** `supported_living_payment`.
**Policy version:** `null`. **Draft date / source check:** 13 October 2026.
**Programme:** Task 8; v0.3 local 0.2 / 3.3.1, sources and specification only.
**Proposed reference week:** `[2026-10-05, 2026-10-12)`; lookup date `2026-10-05`.
The week is a bounded project choice, not a statutory commencement or end date.

Pete's [D11](../../docs/decision_log.md) approves a single existing-grant,
no-children SLP slice before 2 November 2026, with gross weekly entitlement.
Its 6 October clarification restricts that slice to s 34 restricted work
capacity; the carer and total-blindness routes remain unsupported.
This draft proposes the ordinary adult category in Schedule 4 Part 3 cl 1(b)
and an evidenced weekly income agreement. The adult-category and assessment
contract require review; D11 did not approve a rate, precision convention,
income-test implementation, or gross-up method.

Local 3.3.1 starts when SPS 3.2.1 is decided. Parallel documentary preparation
does not claim that sequencing gate has passed. No `policy.yaml`, facts
catalogue, protected cases, engine, graph edge or executable policy version
is created here. [DEC-001](decisions/DEC-001-gross-entitlement-and-precision.md)
blocks the affected monetary claim; Task 8 and the sources/specification
exit gate remain incomplete.

## Source identities and legal period

Each source key below resolves to the full ID, URL, date and locator in
[sources.yaml](sources.yaml). The key is shorthand within this document.

| Key | Source ID and checked locator |
| --- | --- |
| Act | `supported-living-payment-social-security-act-20260926`: ss 16–18, 34–42, 349–351; Schedule 2 Income Test 1; Schedule 3 cls 2–14; Schedule 4 Part 3 cl 1 |
| Regulations | `supported-living-payment-social-security-regulations`: rr 10–11, 205; Schedule 6 item 1; Schedule 8 cl 44 |
| Order | `supported-living-payment-rates-order-2026`: cls 2, 4–5; Schedule 1 Part 1, Schedule 4 Part 3 cl 1(a)–(b) entries |
| Overview | `supported-living-payment-msd-overview`: health-condition route, evidence and review sections |
| Charging | `supported-living-payment-msd-income`: annual/weekly charging and exemptions |
| Earnings | `supported-living-payment-msd-personal-earnings`: disregard and Example 1 |
| Examples | `supported-living-payment-msd-weekly-income-examples`: Examples 1–2 |
| Rates | `supported-living-payment-msd-rates-2026`: SLP without-children rows, net M and gross columns |
| Deductions | `supported-living-payment-msd-single-adult-deductions`: calculation instructions and after-tax deduction heading |
| Cut-outs | `supported-living-payment-msd-cutouts-2026`: single 18+ row and weekly-rounding warning |
| Tax | `supported-living-payment-msd-taxation`: taxable benefit, net payment and tax on benefits |
| Benefit tax authority | `supported-living-payment-income-tax-act-rd11`: RD 11(3)(a), overriding ordinary RD 10(1) tax determination |

Act version: **26 September 2026**. Regulations version: **4 September 2026**.
Order: as made **2 March 2026**, commencing **1 April 2026**. All current
checks are dated **13 October 2026**. The earlier 4 September Act inventory
and its October checks remain historical evidence in the catalogue.
The 26 September amendment changes the Schedule 2 CYPFA-order definition;
comparison with 4 September found the scoped SLP provisions unchanged.

The enacted 2026/54 Amendment Act, s 2, commences Part 1 on 2 November 2026
and Part 2 on 1 April 2027. Its shared-definition/income amendments require
fresh assessment before extending coverage. This draft covers one week
only; neither a live MSD page nor the April rate date proves a full year.
Source retrieval, law version, legal commencement and review state remain
separate provenance fields.

## Supported domain and outcome rules

The proposed unit is one identified beneficiary, single throughout the
week, with no SLP-dependent children, an established ordinary s 34 grant
on restricted-work-capacity grounds, ordinary personal-effort earnings
only, and an active r 205(2) agreement covering the entire week.
This is a conditional amount model. It neither grants a benefit nor
replaces MSD's medical, residence, discretion or payment-state decisions.

The outcome contract follows the existing three outcomes. A known fact
outside this slice gives `unsupported` with no amount and a reason/category.
Unknown or contradictory required facts, unreviewed parameters, precision
or gross-up authority give `needs_review` with no amount and named gaps.
`unsupported` precedes `needs_review`. A missing amount never becomes zero.
`calculated` is available only after source/specification/value approval
and all monetary gates are closed; this draft supplies no such authority.

| Rule | Required behaviour | Evidence |
| --- | --- | --- |
| SLP-01 | Refuse a different week, lookup date outside the week, partial week or a within-week category/basis/grant change. Unknown dates require review. | Project boundary under D11; `supported-living-payment-social-security-regulations` r 205; Act Schedule 3 cl 13 |
| SLP-02 | Require an existing MSD grant on the restricted-work-capacity limb of s 34 throughout the week. Carer s 40, total blindness, commencement/regrant calculations or competing-grant cases are unsupported. Unknown route/grant state requires review. | `supported-living-payment-social-security-act-20260926` ss 34–42; D11 clarification |
| SLP-03 | Take MSD's work-capacity determination and its continuing applicability as asserted facts. Do not infer entitlement from diagnosis, hours, a clinician's opinion alone, or a benefit label. | `supported-living-payment-social-security-act-20260926` ss 35–37; `supported-living-payment-social-security-regulations` rr 10–11; Overview |
| SLP-04 | Require verified ordinary residence/eligibility and ordinary payable state. A grant assertion without week-specific payment evidence is insufficient. Known exceptional states below are unsupported. | `supported-living-payment-social-security-act-20260926` ss 16, 34(b), 36–39; Overview review sections; bounded existing-grant contract |
| SLP-05 | Require single status, no dependent children and the ordinary adult cl 1(b) category. Under-18 cl 1(a), child and partner categories are separate unsupported categories, never the nearest rate. Unknown category requires review. | `supported-living-payment-social-security-act-20260926` s 34(c), Schedule 4 Part 3 cl 1(a)–(h); Rates |
| SLP-06 | Apply the s 18 restriction per person in their own right. The household first-slice limit is separate: partnered and mixed-benefit-couple cases are unsupported coverage. | `supported-living-payment-social-security-act-20260926` s 18, Schedule 4 Part 3 cl 1(d); approved local 3.4 correction |
| SLP-07 | Require a current MSD/person weekly agreement under r 205(2), with no termination notice affecting this week. Annual-basis cases are unsupported here; unknown agreement/basis requires review. | `supported-living-payment-social-security-regulations` r 205(1)–(3), Schedule 6 item 1; Charging |
| SLP-08 | Use caller-resolved SLP chargeable income for this exact week. Require evidence of income classification, earning/entitlement attribution and applicable exclusions. No calendar-day or spell apportionment. | `supported-living-payment-social-security-act-20260926` Schedule 2 income, Schedule 3 cls 2–14; interim Task 6 period contract D32/D36 |
| SLP-09 | Require the s 34 own-effort disregard to be resolved exactly once before the chargeable-income assertion enters the test. It is mandatory up to the statutory limit; it is not the general income-test allowance. | `supported-living-payment-social-security-act-20260926` Schedule 4 Part 3 cl 1 trailing paragraph (a); `supported-living-payment-msd-personal-earnings` |
| SLP-10 | The adult scheduled rate is the cl 1(b) amount subject to Income Test 1. Keep the scheduled/net-M amount distinct from MSD's published gross amount. | `supported-living-payment-social-security-act-20260926` s 17, Schedule 4 Part 3 cl 1(b); `supported-living-payment-rates-order-2026`; `supported-living-payment-msd-rates-2026` |
| SLP-11 | Income Test 1 has two marginal bands, selected from chargeable income after SLP-09. Do not use Test 2 or a universal main-benefit curve. | `supported-living-payment-social-security-act-20260926` Schedule 2 Income Test 1; `supported-living-payment-msd-weekly-income-examples`; Charging |
| SLP-12 | Keep the deduction and remaining scheduled amount distinct from gross entitlement, withheld tax and bank payment. Gross-up and precision remain gated by DEC-001. | `supported-living-payment-social-security-act-20260926` ss 349–351; `supported-living-payment-income-tax-act-rd11` RD 11(3); Tax; Deductions; Cut-outs |
| SLP-13 | Record the exact week, facts, evidence, rule IDs, law version and candidate values used, including any refused step. Do not publish a numeric result with unresolved monetary gates. | Project trace contract under POLICY_SPECS/review doctrine; `supported-living-payment-social-security-act-20260926` Schedule 2 Income Test 1 and Schedule 4 Part 3 cl 1 identify the legal amounts to trace |

For SLP-03, s 35 distinguishes permanence from severity. Regulation 10
prescribes two years; s 35(2)(b) separately addresses a terminal condition.
Section 35(3) requires MSD satisfaction about inability regularly to work
at least 15 hours weekly in open employment. These locators explain the
assertion; Poltika must not calculate a medical finding from those figures.

For SLP-05, s 34 permits age 16+, but cl 1(a) covers single beneficiaries
under 18 without children and cl 1(b) covers other single beneficiaries
without children. The proposed adult category is therefore **18+**, not
25+ and not every legally eligible single claimant. Require an attested
category for the whole week; do not collect date of birth or infer it from
another policy's age fact. The under-18 category needs its own later rate
and reviewed scope before support is extended.

## Proposed input contract

Names below are a reviewable semantic contract, not a new production type.
Status facts use verified / excluded / unknown with evidence references;
finite choices require an explicit unknown rather than an inferred default.
All period-bearing facts identify the same beneficiary and exact week.

| Input | Owner / meaning / failure behaviour | Rule |
| --- | --- | --- |
| `claimant_person_id`, `assessment_week`, `lookup_date` | Caller: stable identity and `[start,end)` dates; missing requires review, known different period unsupported. | SLP-01/13 |
| `established_grant_status`, `grant_route` | Caller: continuing established restricted-work-capacity s 34 grant; route unknown requires review, s 40/blindness/new grant unsupported. | SLP-02 |
| `msd_capacity_determination_current` | Caller: MSD determination applicable throughout the week, including any review status; unknown or contradictory evidence requires review. | SLP-03 |
| `ordinary_eligibility_status`, `ordinary_payment_state` | Caller: applicable residence/grant eligibility and continuous ordinary payable state; unknown requires review, exceptional known state unsupported. | SLP-04 |
| `relationship_category`, `slp_child_status`, `slp_age_rate_category` | Caller: single, no SLP-dependent children, adult cl 1(b), all week; unknown requires review, other known category unsupported. | SLP-05 |
| `no_simultaneous_own_right_payment` | Caller: no other main benefit/NZ Super/veteran's pension concurrently in this person's own right; contradiction or unknown requires review, evidenced competing case unsupported. | SLP-06 |
| `income_assessment_basis`, `weekly_agreement_current` | Caller: r 205(2) weekly agreement covers the week and has not ended; annual or terminated basis unsupported, unknown requires review. | SLP-07 |
| `income_scope_status`, `income_attribution_resolved` | Caller: ordinary personal-effort earnings only, all chargeable income identified and attributed under Schedule 3; missing evidence requires review, known excluded class unsupported. | SLP-08 |
| `personal_earnings_disregard_resolved` | Caller: records original personal earnings, applicable disregard and its one-time application in the supplied amount; missing/contradictory reconciliation requires review. | SLP-09 |
| `weekly_chargeable_income` | Caller: finite non-negative exact decimal, NZD per this week, before income tax but after applicable benefit-income exclusions/disregard; missing or unverified requires review. | SLP-08/09/11 |
| `no_severe_disablement_exemption` | Caller: no discretionary Schedule 8 cl 44 exemption affects the week. Unknown requires review, known applicable exemption unsupported in this ordinary slice. | SLP-08/09 |

The claimant's restricted-capacity finding does not establish whether a
severe-disablement income exemption applies. They are distinct determinations.
Explicitly verified zero chargeable income may be supplied; omission, an
annual wage total, an unallocated receipt or an empty earnings list is not
evidence of zero. The adapter must not subtract the personal disregard
again or promote gross wages to chargeable income without reconciliation.
Future `facts.yaml` must supply a question and finite admissible states for
every gate, with rule IDs, using ADR-0016 rather than collecting medical data.

## Documentary value observations — unapproved

These observations are checked against primary material; they are neither
parameters nor protected expected values. The Order alters the scheduled
amounts, not the two distinct MSD table columns by a guessed tax formula.

| Candidate observation | Value / unit | Primary pinpoint |
| --- | --- | --- |
| Adult single no children scheduled amount | `424.60` NZD/week | Act Schedule 4 Part 3 cl 1(b); Order Schedule 1 Part 1 same entry |
| Under-18 scheduled amount, outside proposed slice | `355.87` NZD/week | Act Schedule 4 Part 3 cl 1(a); Order same entry |
| Published adult gross maximum | `489.21` NZD/week | Rates, SLP single 18+ without children, before-tax column |
| Published adult net M maximum | `424.60` NZD/week | Rates, same row, after-tax-M column |
| Personal-effort disregard limit | `20` NZD/week | Act Schedule 4 Part 3 cl 1 trailing paragraph (a) |
| Income Test 1 lower / upper breakpoint | `160` / `250` NZD/week | Act Schedule 2 definition, paragraphs (a)–(b) |
| Income Test 1 lower / upper marginal reduction | `0.30` / `0.70` NZD per NZD | Act Schedule 2 definition, paragraphs (a)–(b) |

MSD's adult weekly income cut-out is explicitly rounded to a whole dollar;
its guidance directs comparison with annual figures near the boundary.
It is not an exact weekly zero threshold, a rounding rule for entitlement,
or an approved gross-entitlement benchmark for this weekly contract.

## Reproducible calculation sequence and stop points

1. Verify the week, identity and every known coverage exclusion first.
   Record `unsupported` before examining missing facts when a known
   outside-slice fact is present; identify `not_modelled` versus an
   evidenced legal exclusion without treating either as a numeric zero.
2. Verify all remaining grant, capacity, category, income and agreement
   evidence. Contradictory facts give `needs_review`; the latest assertion
   must not silently replace a source-derived or dated fact.
3. Confirm approved policy/version/parameters and their coverage of the
   whole week. This draft has no approved version; halt numerical output.
4. Read the caller's resolved chargeable weekly income `I`. Record the
   prior own-effort disregard reconciliation. For ordinary personal-effort
   income, the statutory disregard is the qualifying earnings up to the
   candidate limit, not a flat subtraction from income of every kind.
5. Once values and precision are approved, transcribe Income Test 1 as
   `D = 0.30 × min(max(I − 160, 0), 90) + 0.70 × max(I − 250, 0)`.
   This algebra records the sourced band structure. It does not adopt
   fractional-income processing, a complete-dollar floor or cent rounding.
6. For a positive remaining scheduled amount, record `B − D`, where `B`
   is the approved cl 1(b) scheduled amount. This intermediate is not gross
   entitlement. Do not produce a negative benefit or infer a zero/payment
   status at cut-out from the rounded MSD weekly cut-out observation.
7. Resolve DEC-001: gross up the correct remaining scheduled amount under
   the applicable benefit tax authority and approved precision contract.
   RD 11(3) requires a Commissioner determination in consultation with MSD.
   Do not compute gross entitlement as `489.21 − D`, apply a fixed net/gross
   ratio, borrow salary PAYE, or use annual basic income tax as withholding.
8. Only after that gate closes return the approved gross-weekly component
   with its provenance. Keep net payment, deductions and downstream policy
   facts separate; do not multiply this week by 52 or apportion a spell.

The formula's documentary `0`, `90` and min/max structure express the
two bands (`250 − 160 = 90`), not additional statutory parameters. Exact
decimal representation is an engineering requirement; it does not select
the legal/operational treatment of fractional money. No caller assertion
can close a policy-owned source, approval or precision gate.

## Output, exclusions and later handoff

Proposed output: `gross_weekly_entitlement`, NZD per the exact assessment
week, identified claimant, before income tax and direct deductions. It
requires the gross-up gate above. A scheduled/net-M intermediate, bank
payment, PAYE withheld, arrears, debt deductions, Winter Energy Payment or
supplementary assistance must not be relabelled as that output.
Every result needs outcome, optional exact amount, period, reason/code,
missing facts, unsupported category and trace. Trace records source IDs,
law versions, review state, rule IDs, parameter/input values and each
intermediate or refusal. Expected monetary output is absent while gated.

Known out-of-slice facts remain explicit `unsupported`: under-18 category;
partners or children; carer/blindness; new grants, stand-downs or changing
grants; trial employment; sanctions, suspended/non-entitlement periods;
hospital/residential care; overseas absence/pensions or exceptional
residence routes; direct deductions/arrears/debt as a requested result;
annual income basis; self-employment, child support, termination/holiday
or other lump sums; discretionary exemptions, deprivation or income
attribution. These are coverage choices, not blanket legal ineligibility.
Unknown corresponding states remain named review gaps.

Next values-stage work must source and review gross-up, fractional-income
precision, cut-out/payment status and final rounding, then create dated
`policy.yaml`, facts and independent spec cases. Cover both Test 1 boundaries,
the personal-disregard boundary, unknown/contradictory facts and every
coverage refusal; protect adopted statutory values under test doctrine.
Earnings Example 1 and weekly Examples 1–2 are **reduction** benchmark
candidates, not gross-entitlement examples. Their published whole-dollar
workings cannot settle fractional precision. Keep Spec, Benchmark and
Regression separate, and preserve WFF/AS results and household IDs.

Tax, WFF and AS interactions remain later reviewed graph work. Retain
actual payment/receipt facts separately from calculated entitlement,
including a reduced-to-zero case. This draft approves no annual taxable
benefit total, full-year WFF status, AS base-rate mapping or disposable
income. Independent final-head Claude primary-source review, author's
preflight, Pete's source/interpretation decisions and the preceding SPS
gate remain required before recommending acceptance or implementation.
