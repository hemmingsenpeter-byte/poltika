# Sole Parent Support — existing-grant first slice

| Metadata | Draft contract |
| --- | --- |
| `policy_id` | `sole_parent_support` |
| `status` | `draft_pending_review` |
| `policy_version` | `null` |
| Author / source check | GPT/Codex, 13 October 2026, Pacific/Auckland |
| Reference candidate | One completed week `[2026-10-05, 2026-10-12)`; lookup date `2026-10-05` |
| Programme / lane | Task 8; v0.3 local 0.2 and commissioned preparation for 3.2.1 |
| Source catalogue | [sources.yaml](sources.yaml); earlier 3–5 October observations retained |

Pete accepted D11's single principal-caregiver, established-grant, **gross
weekly entitlement** slice on 5 October; the [dated record](../../docs/programme/2026-10-06-pete-approvals.md)
records its boundary before 2 November 2026. D36's [Q10 decision](../../docs/programme/2026-10-12-pete-approvals.md)
requires caller amounts for each policy period, without apportioning spells.
This commissioned draft prepares that slice. The detailed lane still places
the SPS 3.2.1 decision after Jobseeker 3.1.1; drafting does not clear that gate.
No values file, fact catalogue, protected expected case or engine is approved.

The proposed output is one person's ordinary gross SPS entitlement for this
week, conditional on asserted grant and policy facts. It is neither a general
eligibility determination nor a net payment, PAYE liability, bank deposit,
annual income, disposable income or combined tax-transfer total. The gross
method and precision gates below prevent any numeric output from this draft.

## Dated authority and coverage

The active statutory authority is the [Social Security Act 2018, 26 September
2026 consolidation](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/)
(`sole-parent-support-social-security-act-2026-09-26`, **SSA** below).
The previous 4 September catalogue entry remains historical evidence.
Author comparison found the scoped SPS ss 29–33, Schedule 4 Part 2,
Schedule 3 cl 13, Income Test 1 and ss 18, 349–351 unchanged. The later
Schedule 2 CYPFA order-definition amendment remains outside this ordinary slice.

[Regulations, 4 September version](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-09-04/)
(`sole-parent-support-social-security-regulations`, **SSR**) supply r 205 and
Schedule 6. The [2026 Rates Order](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/2026-03-02B/)
(`sole-parent-support-rates-order-2026`, **Order**) is the as-made 2 March
instrument; commencement/payment applicability starts on 1 April under cls 2–4.
[Income Tax Act, 4 September version](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
(`sole-parent-support-income-tax-act-interactions`, **ITA**) supplies RD 11(3).
Consolidation, legal commencement, table reference date and check date differ.

The [enacted 2026 amendment](https://www.legislation.govt.nz/act/public/2026/54/en/2026-09-03/)
commences Part 1 on 2 November 2026 and Part 2 on 1 April 2027 (s 2).
Its shared-definition/income changes require a new review; SPS implications
are not assumed absent. Nothing here claims coverage from 2 November onward.
The completed reference week lies after the 26 September consolidation and
before the November commencement. Its bounded source/independent-review gates
remain; the dates are a labelled Scenario/coverage proposal, not a legal rate
expiry or payment-cycle rule.

The first slice requires an existing ordinary s 29 grant throughout the week,
the single route in s 30(a), ordinary parent/care/dependency facts, no shared
or split care and no in-week status/rate/basis change. It accepts an independently
classified ordinary weekly income amount under an active r 205(2) agreement.
The legally prescribed 52-week basis remains real but outside this proposed
weekly-agreement sub-slice; a weekly payment does not establish weekly assessment.
Initial applications, s 31 child-attribution decisions, other s 30 routes,
child-order exceptions, transfer/reapplication decisions, sanctions,
hospitalisation, imprisonment, absence, overseas pensions/direct deductions,
arrears, business/trade, special income charging and exceptional rates remain
`unsupported / not_modelled`. These are deliberate coverage limits, not claims
that their recipients are legally ineligible for SPS.

## Primary-source rule map

IDs below are stable draft rule IDs. Every statutory row resolves through
the source IDs above to the exact provision. Operational pages corroborate
the law; scope and outcome choices are separately identified as model design.

| Rule | Sourced requirement and proposed first-slice treatment | Primary locator |
| --- | --- | --- |
| SPS-01 | Bind the exact week, lookup date, source versions and complete-period currency. No other period or post-commencement default. | `sole-parent-support-social-security-act-2026-09-26` s 17; `sole-parent-support-rates-order-2026` cls 2–5; future amendment s 2; D11/Q10 coverage design |
| SPS-02 | Receive an established ordinary SPS grant covering the week and verified ordinary residential/age conditions; never decide the application from proxies. | `sole-parent-support-social-security-act-2026-09-26` ss 16, 19, 29(c)–(d) |
| SPS-03 | This slice requires s 30(a)'s single route. Other relationship routes are recognised and excluded from coverage, not relabelled as no entitlement. | `sole-parent-support-social-security-act-2026-09-26` ss 8, 30(a)–(e); Schedule 4 Part 2 cl 3 |
| SPS-04 | Receive the claimant's parent/care status and an eligible dependent child under 14, plus youngest-dependent-child status throughout the week. A birthday/transfer is a distinct excluded path. | `sole-parent-support-social-security-act-2026-09-26` ss 29(a), 30, 31, 33(2)–(3) |
| SPS-05 | Receive separate child, primary care, family maintenance, financial dependence and relevant excluded-payment facts. OB/UCB payment excludes that child for the rate part. | `sole-parent-support-social-security-act-2026-09-26` Schedule 2 `child`, `dependent child`, `principal caregiver`; Schedule 4 Part 2 cl 4 |
| SPS-06 | Refuse this slice for shared/split care or a required court-order/caregiver selection. A principal-caregiver assertion alone cannot resolve split care. | `sole-parent-support-social-security-act-2026-09-26` ss 29(b), 32(1)–(4); bounded care-coverage design |
| SPS-07 | Preserve the per-person restriction on simultaneous own-right main benefits/NZ Super/veteran's pension. Check identity and period explicitly. | `sole-parent-support-social-security-act-2026-09-26` s 18 |
| SPS-08 | A couple with both partners on own-right main benefits is outside this first slice, before missing-fact gates. No household-wide statutory prohibition is asserted. | `sole-parent-support-social-security-act-2026-09-26` s 18; Schedule 4 Part 1 cl 1(g), Part 3 cl 1(d); Pete's 5 October coverage decision |
| SPS-09 | Select the ordinary SPS Schedule 4 rate and Income Test 1; respect separately asserted reductions/suspension/cancellation. An agency gross column cannot replace the statutory rate. | `sole-parent-support-social-security-act-2026-09-26` s 17(1), (3); Schedule 4 Part 2 cl 1; `sole-parent-support-rates-order-2026` cl 5 / Schedule 1 Part 1 |
| SPS-10 | Benefit-test income is its own before-tax statutory concept. The source order, inclusions and exclusions must already be resolved for this person/week. | `sole-parent-support-social-security-act-2026-09-26` Schedule 3 cls 2–9, 15 and Part 4; Part 3A for separately excluded child-support charging |
| SPS-11 | SPS normally uses 52 weeks. Require an MSD/person agreement for one-week determination that neither party has ended during the week. | `sole-parent-support-social-security-regulations` r 205(1)–(3); Schedule 6 item 1; `sole-parent-support-social-security-act-2026-09-26` Schedule 3 cls 11, 13(1) |
| SPS-12 | Receive income already attributed to the exact week under the earning/entitlement-period rule, with any MSD fallback identified. Do not use receipt date or annual division automatically. | `sole-parent-support-social-security-act-2026-09-26` Schedule 3 cl 13(1), (1A)–(2), (3A)–(4); Q10/D32 |
| SPS-13 | A childcare earnings disregard is discretionary and limited by statute. Require its non-applicability or an already resolved amount/decision; never infer it from child age or subtract it twice. | `sole-parent-support-social-security-act-2026-09-26` Schedule 4 Part 2 cl 2 |
| SPS-14 | Income Test 1 reduces the applicable rate using its two bands. The official deduction page places this reduction against the after-tax benefit payment; it does not establish gross reduction at the same rate. | `sole-parent-support-social-security-act-2026-09-26` Schedule 2 `Income Test 1`; Schedule 4 Part 2 cl 1; ss 349–351 |
| SPS-15 | Gross SPS entitlement requires the separately authorised benefit-tax/gross-up method and its applicability. Missing method gives no amount. | `sole-parent-support-social-security-act-2026-09-26` ss 349–351; `sole-parent-support-income-tax-act-interactions` RD 11(3)(a); DEC-001 |
| SPS-16 | Input, intermediate, final and tie precision must be source-backed and reviewed before a numeric amount. No tax, payroll, JS or AS convention is inherited. | `sole-parent-support-social-security-act-2026-09-26` Schedule 2 Income Test 1 / Schedule 4 Part 2; `sole-parent-support-social-security-regulations` r 205; `sole-parent-support-income-tax-act-interactions` RD 11(3); DEC-002 |
| SPS-17 | Known excluded coverage outranks missing facts; missing/contradictory required facts or unreviewed source gates give `needs_review`, never zero. | Repository outcome contract; source-linked exclusions SPS-01–16; new-policy skill ; statutory input/exclusion context: `sole-parent-support-social-security-act-2026-09-26` s 17 |
| SPS-18 | Keep SPS, WFF and AS inputs/statuses distinct; graph edges and common-period totals require their own reviewed specifications. | `sole-parent-support-social-security-act-2026-09-26` Schedule 3 cl 8(1)(a), (l); `sole-parent-support-income-tax-act-interactions` CF 1(1)(c), MB 1–2; `sole-parent-support-social-security-regulations` rr 17–18; source-scope interaction inventory |

## Proposed input and outcome contract

These are semantic questions for the later `facts.yaml`, not runtime fields
or newly registered variables. Caller assertions remain Scenarios unless
independently evidenced; a `verified` scenario status does not make an MSD
determination. Each fact carries person/child identity, exact validity period,
status, source or attestation, rule ID and any relevant determination reference.
No date of birth, diagnosis, benefit amount, household address or other policy's
child count substitutes for the required SPS fact.

| Proposed fact / owner | Required meaning; outcome when absent or excluded |
| --- | --- |
| `assessment_week`, `lookup_date` / request | Exact reference candidate and seven-day interval. Other dates `unsupported`; unknown date `needs_review` (SPS-01). |
| `existing_sps_grant` / claimant | s 29 grant effective for the entire week. Unknown `needs_review`; initial application or another grant route `unsupported` (SPS-02). |
| `ordinary_residential_requirement`, `sps_age_requirement` / claimant | Independently classified s 16 ordinary route and age at least 20 under s 29(d). Unknown `needs_review`; exceptional route or excluded condition `unsupported` (SPS-02). |
| `s30_single_route` / claimant | Single under the Act for the exact week; no partner-income route chosen by this module. Unknown `needs_review`; other s 30 route `unsupported` (SPS-03). |
| `sps_parent_and_care_requirement` / claimant/child | Mother/father and caring status under s 30, with no s 31 discretion required. Unknown `needs_review`; unmodelled attribution `unsupported` (SPS-04). |
| `principal_caregiver_status` / claimant/child | Separate Schedule 2 primary day-to-day care classification, not a guess from residence. Unknown `needs_review` (SPS-05). |
| `sps_child_dependency_status` / each relevant child | Full Schedule 2 classification, maintenance/dependence and excluded-payment meanings. Unknown `needs_review`; exceptional child route `unsupported` (SPS-05). |
| `sps_rate_qualifying_child_present` / claimant | At least one child qualifies for Part 2 after its OB/UCB exclusion. Unknown `needs_review`; no qualifying child `unsupported / evidenced_exclusion` (SPS-05). |
| `youngest_dependent_child_under_14_whole_week` / claimant/child | Separate s 30/s 33 classification for the whole week. Unknown `needs_review`; birthday or transfer in the week `unsupported` (SPS-04). |
| `ordinary_care_arrangement_whole_week` / claimant/children | No shared/split care, court-order exception or care change needing selection. Unknown `needs_review`; any such path `unsupported` (SPS-06). |
| `own_right_other_main_benefit_or_pension` / claimant | No conflicting simultaneous own-right receipt under s 18. Unknown `needs_review`; verified conflict `unsupported / evidenced_exclusion` (SPS-07). |
| `both_partners_own_right_main_benefits` / household | Verified occurrence `unsupported / not_modelled` under approved coverage precedence; do not invent a legal household ban (SPS-08). |
| `ordinary_unmodified_rate_status` / claimant | No sanction, special rate, suspension/cancellation, hospital/prison/absence or direct-deduction path. Unknown `needs_review`; known path `unsupported` (SPS-09). |
| `income_assessment_basis`, `weekly_agreement_active_whole_week` / claimant | Exact-week agreement under r 205(2), with its start/end evidence. Annual basis or termination/change `unsupported`; missing agreement `needs_review` (SPS-11). |
| `sps_weekly_chargeable_income` / claimant | Nonnegative NZD for this exact week, before income tax, independently classified/attributed and after any authorised resolved disregard. Unknown or wrong/unverified meaning `needs_review`; unsupported composition/period `unsupported` (SPS-10–13). |
| `income_classification_complete`, `income_exception_status` / claimant | Evidence for relevant inclusions/exclusions and no unresolved holiday, business/trade, child-support, insurance/compensation, overseas-pension or deprivation path. Unknown `needs_review`; a path requiring this module to derive them `unsupported` (SPS-10/12). |
| `childcare_disregard_status`, `resolved_disregard_provenance` / claimant | Not applicable, or separately resolved under Part 2 cl 2 and reflected exactly once in charged income. Unknown/disputed MSD discretion `needs_review`; request to determine it `unsupported` (SPS-13). |
| `period_currency`, `gross_method_status`, `precision_status` / governed sources | Complete-period confirmation and approved sourced methods; a missing/unreviewed gate `needs_review` regardless of all caller facts (SPS-01/15/16). |

The module never constructs chargeable income from raw wages, tax returns or
generic household income. If an earning-cost exemption or legitimate expense
adjustment is relevant, the caller must establish its exact statutory exemption,
MSD decision where required, amount and week before supplying classified income.
No general employment-expense deduction has been established by this bounded
check. An unresolved adjustment gates the input; a request for Poltika to decide
it is outside coverage. Childcare costs alone do not establish a $20 disregard.
Self-employment and new Schedule 8 exemption derivation require a later slice.

For contradictory grant, relationship, care or income/basis assertions, preserve
the conflict and return `needs_review` with the affected fact IDs. Apply a
verified coverage exclusion first. Missing income, source, rate or status has
no amount. A later reviewed calculation can yield an evidenced zero, but zero
cannot infer cancellation, no grant, no receipt or WFF/AS eligibility status.

## Documentary numeric candidates and calculation sequence

The following are sourced observations pending the values-stage review.
They are not executable parameters, protected test values or gross benchmarks.

| Candidate | Meaning and source |
| --- | --- |
| NZD `521.52` per week | Statutory ordinary rate: SSA Schedule 4 Part 2 cl 1; Order Schedule 1 Part 1 replaces `505.80` with `521.52`. |
| NZD `606.69` per week | Official April 2026 before-tax maximum-rate observation; `sole-parent-support-msd-rates-2026`, SPS section. Its paired after-tax M amount is `521.52`. |
| NZD `160`, `250` per week; fractions `0.30`, `0.70` | SSA Schedule 2 Income Test 1 thresholds and tier rates; weekly-basis gate applies. |
| Up to NZD `20` per week | Discretionary personal-earnings childcare disregard, SSA Schedule 4 Part 2 cl 2; never an automatic parameter deduction. |
| `52` weeks / `1` week | SSR Schedule 6 item 1 default / r 205(2) agreement; not an undocumented conversion. |

1. Bind person, reference week, lookup date and exact source versions (SPS-01).
   Resolve verified excluded scope before collecting missing facts (SPS-17).
2. Validate established ordinary grant, relationship, child/dependency/care and
   per-person other-benefit facts independently (SPS-02–08); do not adjudicate them.
3. Confirm ordinary-rate status and whole-period authority (SPS-09). Receive
   the active weekly agreement and charged income for this exact week, with
   classification, attribution and resolved-disregard provenance (SPS-10–13).
4. After values/precision approval, the statutory deduction candidate is
   `D = 0.30 × min(max(I − 160, 0), 90) + 0.70 × max(I − 250, 0)`.
   This transcription of Income Test 1 describes the deduction substep only.
   It does not authorise a gross-entitlement formula, fractional-income
   procedure or repayment. Preserve all intermediate quantities (SPS-14/16).
5. **Stop while DEC-001/DEC-002 or period currency is unresolved.** To produce
   the requested gross component, the reviewed method must connect the
   statutory-side reduced amount to the applicable ss 350–351/RD 11 method,
   including a sourced zero floor and precision. Subtracting `D` directly from
   `606.69` or equating `521.52` with gross entitlement would be `SPEC_ERROR`.
6. After those gates and independent expected-case review, emit only the
   gross SPS component, NZD per exact week, person ID, outcome and Model-output
   class. This draft produces no accepted numeric result (SPS-15–17).

Every retained trace must name the input assertion/evidence classes, grant
period, child/care facts, assessment agreement, income classification and
disregards, source ID/version/locator/check date, rate interval and review
state, rule/decision IDs, deduction bands, gross-up and rounding stages,
policy version and retained input/result identities. A citation or period gap
stops calculation. Full stored precision does not invent a statutory display rule.

## Decisions, values and independent validation handoff

[DEC-001](decisions/DEC-001-gross-entitlement-authority.md) records the missing
operative gross-up determination and scope/meaning question for Pete.
[DEC-002](decisions/DEC-002-weekly-precision.md) records the unverified complete
SPS precision procedure. Neither selects a modelling convention. Tax Q17's
whole-dollar Assumption and AS r 19's round-up do not decide SPS precision.

The next values pack needs sourced dated intervals with no invented expiry,
complete fact questions and independently calculated boundary cases at both
thresholds, including $1 either side, fractional dollars/ties, resolved/no
disregard, basis termination, care changes and the sourced zero boundary.
Cases for missing/contradictory facts, unsupported routes and both-partner
coverage precedence are required separately. Protected expected values follow
[test doctrine](../../doctrine/test-doctrine.md); none is added here.

`sole-parent-support-msd-weekly-example` supplies an official candidate:
gross weekly income `350`, lower-band deduction `27`, upper-band deduction
`70`, total `97`. Its threshold note is dated 1 April 2022; the live page has
no version date. The [current deduction table](https://www.workandincome.govt.nz/on-a-benefit/tell-us/income/deduction-tables/sole-parent-support)
(updated 23 June 2026) corroborates that deduction, explicitly as an estimate
against after-tax payment. These can validate the deduction substep after scope
review. They do not benchmark a 2026 gross entitlement or fractional precision.
An independently published full gross example remains `MISSING_SOURCE`.

Maintain separate Spec, Benchmark and Regression classes, including currency,
income meaning, no pro-rating, no inferred child status and no implicit gross
conversion. Benchmark absence and the open decisions block numeric acceptance;
author drafting is not independent review.

Taxable SPS income, WFF main-benefit effects/allocation and AS claimant categories
remain source-located **future interaction candidates** under SPS-18. Their
amount/status/period mapping requires the later graph review. Do not add a graph
edge, mix WFF child eligibility with SPS dependency, convert this week to a year,
or treat a gross SPS component as disposable income in this first slice.
