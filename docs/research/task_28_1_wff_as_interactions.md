# Task 28.1: WFF and Accommodation Supplement interactions

Author: GPT/Codex. Checked: 24 September 2026 (NZST).
Base revision: `18e1ca5`.
Status: source-research handoff for independent Claude review and Pete's
acceptance. Not the Task 28.3 interaction contract or a calculator change.

## Scope and evidence

This addresses the four parts of Task 28.1 for the existing WFF full-year
2026-27 domain and AS's scoped rent/board domain. It does not choose the
28.2 lookup dates, assessment week or reporting mode; verify the operative
versions again for the selected dates before accepting a combined run.
An as-of source check is not approval of an unfinished future interval.

Primary legislation read directly, versions as at 4 September 2026:

- Income Tax Act 2007: CW 33(1)(a), MB 13(2)(l), MC 1(2), MC 6(b)(i),
  MD 8, MD 14-15, ME 1-3, and MG 4.
- Social Security Act 2018: Schedule 2 main-benefit definition,
  Schedule 3 clause 8(1)(a), (l), and Schedule 4 Part 7 clause 7.
- Social Security Regulations 2018: regulations 16-18, Schedule 8
  Part 1 item 15 and Part 21 clauses 36-37.
- Tax Administration Act 1994: sections 80KK, 80KN-80KS and 80KU.

URLs, versions, locators and bounded claims are recorded in the two
`sources.yaml` catalogues under `task_28_1_check`. Official HTML was read
using the documented browser-user-agent retrieval method. Agency guidance
was checked separately; undated live MAP pages are not historical
snapshots. No external policy-engine code or values were consulted.

## 28.1(a): AS in WFF family-scheme income

The sourced chain is:

1. CW 33(1)(a) exempts Social Security monetary benefits other than its
   specified main-benefit/equivalent-assistance categories.
2. AS is not in Schedule 2's main-benefit list. Jobseeker Support, Sole
   Parent Support and Supported Living Payment are in that list.
3. MB 13(2)(l) prevents an exempt Social Security monetary benefit from
   being added back under the other-payments rule.
4. IRD's `wff-ird-other-income` guidance explicitly corroborates the AS
   exclusion; `wff-ird-government-payments` separately confirms that
   taxable main benefits remain in family income.

Conclusion, as an inference from those provisions corroborated by IRD:
the AS output must not be added to the verified WFF family-scheme-income
input. It must not be subtracted again if the caller already supplied a
correctly derived income amount. This is not a blanket exclusion for
everything paid by MSD, nor authority to derive WFF income from wages alone.

Task 28.3 should require evidence that the supplied income already follows
its policy definition. If an amount is an unexplained total of wages,
benefits and credits, the derivation is unverified: keep `needs_review`
rather than silently normalising it.

## 28.1(b): WFF in AS chargeable income, with the routes kept distinct

### IRD-paid route

Schedule 3 clause 8(1)(l) excludes amounts or tax credits received under
Income Tax Act subparts MA-MG and MZ. MC 1(2) identifies the WFF components,
including FTC, IWTC, MFTC and Best Start. MSD's
`as-msd-chargeable-income` page explicitly lists IRD-paid WFF among the
non-beneficiary income exclusions. These are corroborating sources, not
alternative authorities.

### MSD-paid route

The full clause 8(1)(l) text does **not** contain an IRD-only payer
qualification. TAA section 80KN calls the amount paid by the chief
executive a WFF tax credit, and section 80KO determines its amount by
reference to the Income Tax Act. MSD's `as-msd-ftc-administration` says
that MSD pays FTC on behalf of IRD.

Conclusion, inferred from the linked statutes: an identified statutory
WFF tax credit does not lose the clause 8(1)(l) income exclusion merely
because MSD pays it. An agency page naming the IRD route is not evidence
that the MSD route is chargeable. This supports resolving the source
question left open by AS-10, subject to Pete's recorded acceptance of the
cross-Act interpretation; it does not silently amend
the approved specifications or assert that every MSD payment is WFF.

The research distinguishes two propositions:

- **Nature of payment:** verified WFF has the sourced income exclusion
  on either route. Unknown payer alone is not evidence that WFF is income.
- **Payment administration:** the actual payer, period, component and
  payment history cannot be inferred from a broad claimant category.
  They remain relevant evidence for a combined scenario and WFF's own
  protected-credit/extra-instalment checks.

The ordinary AS main-beneficiary branch has no separate regulation 18
income reduction; that regulation applies to non-beneficiaries as defined
in regulation 17. Do not invent a beneficiary income reduction merely to
feed a WFF output into AS. Conversely, an AS non-beneficiary's verified
income must use the proper exclusions, not contain WFF by default.

## 28.1(c): which payer can apply to supported households?

| Household circumstances | Source-supported route observation | What remains to verify |
| --- | --- | --- |
| Ordinary non-beneficiary, not transitioning off a main benefit | MSD guidance assigns ordinary FTC administration to IRD | Actual payment identity, period and schedule; do not infer all annual facts from one AS week |
| Jobseeker, Sole Parent Support or Supported Living recipient with qualifying children | TAA 80KN provides for MSD payment subject to its conditions; MAP says ordinary main-benefit clients may choose IRD instead | Actual choice/agreement, component eligibility and protected-credit facts |
| Main benefit has recently ended | TAA 80KP permits continued MSD payments; 80KK and 80KU address IRD takeover/arrears | Transition dates and payments; non-beneficiary status does not prove the payer is already IRD |
| No qualifying dependent child | Payer choice cannot create WFF entitlement | Each policy's own household and eligibility checks |

Sources: `as-taa-wff-payment-routes`, `as-msd-wff-payer-choice`,
`as-msd-ftc-administration`, and `wff-tax-administration-act`.

MAP says FTC and Best Start are paid together by the same agency in the
ordinary choice case. It also identifies foster-parent and Young Parent
Payment exceptions. Do not turn the ordinary rule into a universal one:
Young Parent Payment is not an AS supported claimant category, and the
other exclusions/facts still need their existing checks.

This source work does not verify the section 225A instruments authorising
particular abated payments, reconstruct a claimant's payer agreement, or
derive actual instalments from annual WFF outputs. Those cases cannot be
declared verified by this note. Known out-of-domain schedules remain
`unsupported`; missing payment evidence remains `needs_review` where the
approved calculation requires it.

## 28.1(d): other interactions found in the scoped domains

### AS's base rate references an FTC rate, with interpretation gates

Regulation 17(2)(b), (d) and (h) expressly reference a maximum annual FTC
rate divided by 52 in relevant parent cases. Paragraph (f), for a single
non-beneficiary with children, instead says the annual rate payable. The
initial note incorrectly described all four as expressly maximum rates.
Whether (f) also selects the un-abated statutory eldest-child rate must
be decided from the sources, not assumed from its neighbouring paragraphs.
All four refer to an eldest dependent child under 16; the age condition
also needs interpretation before a count-only household key can be accepted.

This establishes a rate-construction link distinct from the income
exclusion, but does not settle the (f) term's treatment. Do not feed an
annual household WFF total or IWTC into the AS base. Nor should a household
FTC output be wired in for (f) without a reviewed interpretation and
contract. No new output dependency is approved here.

Consequences for 26a/28.3: base-rate provenance must include this statutory
source where applicable; an expressly maximum-rate term must not be
replaced by a possibly abated or unresolved household output. Paragraph
(f) remains a decision gate, not a proven maximum-rate case. This research
does not require a
v0.3 dependency graph or approval of WFF's temporary IWTC base. The separate
26a audit identifies household-selector, subtype and threshold-precision blockers;
this note does not resolve them.

Claude's independent review also recommends an explicit decision record
for the MSD-paid income exclusion. The linked statutory text supports it
at high confidence, but accepting that inference closes AS-10's reserved
gate and belongs to Pete. Within ordinary main-beneficiary AS cases there
is no regulation 18 income reduction; do not introduce a generic payer
gate there. The MSD income-exclusion question is particularly relevant
to a non-beneficiary still receiving transitional MSD-paid WFF.

### Main-benefit facts constrain WFF component branches

MC 6(b)(i) and MD 8 give the main-benefit restrictions for the relevant
WFF components; MD 14-15 and MG 4 require calendar-month protected-credit
checks. The current scoped calculator returns `unsupported` for known
protected-credit cases and `needs_review` when applicability is unknown.
Receiving AS alone is not receiving a main benefit.

Thus an AS input asserting payment of Jobseeker/Sole Parent/Supported
Living during a week inside the WFF year cannot coexist with an assertion
that no main benefit was received throughout that year. A combined runner
must not silently select one assertion. The plan's shared-fact conflict
gate applies; correcting a verified main-benefit fact must preserve each
component's existing outcome, not substitute zero or an ordinary formula.

Likewise, a beneficiary example cannot be made into an ordinary calculated
FTC demo simply by declaring protected-credit applicability absent. This
is a fixture-design constraint for Task 29, not a change to WFF's domain.

### Income exclusions do not establish cash-assets exemptions

Regulation 16 and Schedule 8 govern AS cash-assets exemptions separately.
Part 1 item 15 references Best Start arrears defined by Part 21 clauses
36-37, with a specific pre-July-2018 entitlement/birth boundary and time
limit. It is not a blanket exemption for all saved WFF receipts or current
Best Start. The current WFF Best Start birth cohort is different.

Do not calculate assets by subtracting all WFF from a bank balance or by
adding the annual WFF output to it. Use the separately verified asset
stock at the appropriate AS date and retain the existing exempt-asset
scope gate. No new asset exemption or treatment of a particular balance
is approved here.

### Shared people are not interchangeable policy definitions

Schedule 4 Part 7 clause 7 expressly excludes children with an orphan's
or unsupported child's benefit from its AS dependent-child definition.
WFF has its own dependent-child/care tests and payment exclusions. An
unexplained equal child count is not enough to establish that the same
people satisfy both definitions. In the narrow supported intersection,
verify identities and qualification facts under each policy before
checking agreement; a mismatch must not be silently repaired.

Period reconciliation remains 28.2. Annual WFF income and weekly AS income
are distinct quantities; there is no verified rule here for converting
one into the other or summing the outputs into a mixed-period total.

## Gates for the subsequent contract

These are research handoff requirements, not new runtime implementation:

| Unresolved evidence or conflicting fact | Required disposition |
| --- | --- |
| Exact assessment dates/reporting mode not accepted | Leave 28.2, 28.3 and dependent work pending |
| Individual payer/history or income derivation needed but unverified | `needs_review`; do not invent a payer, schedule or income adjustment |
| Two inputs contradict a shared main-benefit/household fact | Plan's combined `needs_review` gate; preserve the conflicting evidence |
| Known protected-credit, extra-instalment, exemption or other outside-domain case | Preserve existing component/domain `unsupported` outcome, not a false zero |
| AS rate selection or precision unresolved | Retain 26a's rate gate; this income research does not approve a base rate |
| Future IWTC rate interval unverified | Preserve the Task 10.2/26b whole-year gate |

No additional actual-output feedback loop was established in this bounded
pass. That is not a claim that all tax and benefit interactions have been
exhaustively verified. The parameter, eligibility, asset and definition
interactions above are substantive and must not be omitted just because
both ordinary output payments are excluded from the other's income.

## Handoff

Claude independently derives these claims from the primary sources before
reading the author's conclusions. Pete confirms any discrepancy and
accepts the research. After 28.2, Codex writes the 28.3 contract in both
specifications, preserving separately sourced payment routes and existing
component boundaries; Claude then implements the combined runner.

No `policy.yaml`, `specification.md`, expected value, calculator or
BUILD_PLAN.md status is changed by this research slice.
