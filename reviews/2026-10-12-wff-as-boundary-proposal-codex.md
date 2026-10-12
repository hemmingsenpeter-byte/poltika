# Independent GPT/Codex review: WFF/AS boundary proposal

Date: 12 October 2026. This reviews **only** the six-case proposal in #211,
not its implementation changes. No value here is approved for a test.

## Review inputs and evidence labels

**AI hypothesis — Fact candidate (repository observation):** #211's head was
`f7313bedb52c747433b86daf2b5d72b6a7e44f5e`, merged as
`ac08ecc1d65342884b4b82d3cd0a688799959c77`. The proposal is unchanged between
that merge and the reviewed `origin/main` snapshot
`1c19f645f08823d2089ef4850afa5e640cdbfbd4`. Input:
[proposal](../review_packets/wff_as_boundary_cases_proposal.md).
Contracts: [WFF specification](../policy_specs/working_for_families/specification.md)
and [AS specification](../policy_specs/accommodation_supplement/specification.md),
including AS DEC-001 and the policy 0.1.1 selector repair.

**AI hypothesis — Fact candidate (method record):** this root pass was not fully blind. A headings scan
unexpectedly displayed several proposed values, and input extraction included
source/spec summaries. Primary-source derivations were recorded before reading
the full rationale. A separate input-only derivation is recorded below; it
must not be described as a blind root review.

**Evidence convention:** chosen household inputs are **Scenario**. Python
`Decimal` arithmetic reported below is **Model output**, depending on those
Scenarios and the cited rule candidates. New legal readings and review findings
are **AI hypothesis**, with intended promotion class **Rule** where they state
law, pending independent review/Pete's interpretation gate. Bibliographic and
git observations are **AI hypothesis**, with intended promotion class **Fact**. Labels do not turn an attestation into an
independently verified household fact. Test-expectation classification remains
deferred under constitution Decision 1; nothing is promoted here.

## Primary sources independently retrieved

All were retrieved on 12 October 2026. Official legislation HTML was downloaded
directly with a browser user agent after browser retrieval failed. S1–S4 are
rule candidates (current evidence class **AI hypothesis**, intended **Rule**);
the titles, displayed version dates and passage locations are **AI hypothesis**, intended **Fact**.

| ID / URL | Version / locator | What the retrieved passage supports |
| --- | --- | --- |
| S1 [Income Tax Act 2007, Part M](https://www.legislation.govt.nz/act/public/2007/97/en/2026-04-01/parts/DLM1518405/) | As at 1 April 2026; also checked as at 4 September 2026. MD 3(2), (4)–(5); MD 13(2)–(3); ME 1(2)–(3), ME 3(2)–(3); MG 2(1)–(2), MG 3(1)–(2); MF 4(4) | Annual/day and weekly-period formulas; complete-dollar income **excess** for FTC and Best Start; the ME 3 definition of net income. Annual formulas and an instalment-notice provision are distinct. |
| S2 [Income Tax (Tax Credit) Order 2025](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2025/260/en/2025-11-17/) | As made 17 November 2025, in force; cls 2, 4–6 | Commencement on 1 April 2026; eldest-child $7,921, MFTC $36,604, Best Start $4,041, applying for 2026–27 and later tax years. |
| S3 [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-04-01/) | As at 1 April 2026, operative for the June scenarios; also checked 4 September 2026. S 423(3); Schedule 4 Part 7 cls 1, 3, 7 | Asset imputation thresholds and $1 per $100 wording; 70% rent/contribution/board calculation, Area 1 caps, qualifying-cost definition. S 423 does not expressly specify incomplete-$100 treatment. |
| S4 [Social Security Regulations 2018](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-03-02/) | As at 2 March 2026, operative for the June scenarios; also checked 4 September 2026. Rr 15(1), 17(1), 18(1)–(3), 19 | Inclusive asset ceilings; beneficiary/non-beneficiary distinction; separate non-beneficiary income reduction; rounding the assessed supplement upwards to a complete dollar. |
| S5 [MSD non-beneficiary thresholds](https://map.workandincome.govt.nz/map/deskfile/extra-help-information/accommodation-supplement-tables/non-beneficiaries-current-01.html) | Table explicitly at 1 April 2026; single and couple-with-children rent/board rows | Weekly entry thresholds $93 and $205; Area 1 caps $165 and $305. Candidate **Rule** from agency rates, currently **AI hypothesis** pending this document's review. |
| S6 [MSD non-beneficiary income cut-outs](https://map.workandincome.govt.nz/map/deskfile/extra-help-information/accommodation-supplement-tables/income-cut-out-points-for-non-beneficiaries-curren.html) | Table explicitly at 1 April 2026; Area 1 income-threshold column | Weekly thresholds $693 for single and $1,117 for couple with children. Candidate **Rule**, currently **AI hypothesis**. No inversion from a rounded cut-out is used. |
| S7 [MSD Jobseeker AS thresholds](https://map.workandincome.govt.nz/map/deskfile/extra-help-information/accommodation-supplement-tables/jobseeker-support-current-01.html) | Table explicitly at 1 April 2026; ordinary single and couple-with-children rent/board rows | $93 and $205 entry thresholds; the protected woman-alone row differs. Candidate **Rule**, currently **AI hypothesis**. |
| S8 [MSD non-beneficiary assets](https://map.workandincome.govt.nz/map/income-support/extra-help/accommodation-supplement/assets-non-beneficiaries-01.html), [asset example](https://map.workandincome.govt.nz/map/income-support/extra-help/accommodation-supplement/example-calculating-income-from-assets-non-benefic-01.html) | Live guidance as retrieved 12 October 2026; no revision date shown. Opening asset paragraphs, SWIFTT process; example calculation | **AI hypothesis — Fact candidate:** MSD repeats the $100 wording and illustrates an exact $400 excess producing $4 weekly income. It supplies no fractional-block example. It cannot settle the disputed rows. |

**AI hypothesis — Fact candidate:** IRD guidance was checked separately: [FTC](https://www.ird.govt.nz/working-for-families/types/family-tax-credit),
[MFTC](https://www.ird.govt.nz/working-for-families/types/minimum-family-tax-credit),
[Best Start](https://www.ird.govt.nz/best-start), live pages labelled last updated
25 February 2026. Locators: FTC calculation/weekly or fortnightly payments;
MFTC income limit/full-year calculation; Best Start summary/abatement.
They corroborate the annual amounts and distinguish rounding instalments from
annual calculations. Their simplified prose does not replace the Act's
complete-dollar-excess wording.

## Independently derived behaviour

**Scenario:** use the proposal's ordinary supported June 2026 branch: 365
eligible days for day-based WFF components, 52 qualifying weeks for MFTC,
single relationship period, no protected-credit or extra-instalment exception;
AS costs are qualifying rent/contribution costs for one week. All other
required facts must be expressly asserted with the appropriate scoped status.
These are calculator scenarios, not verified benefit determinations.

The following are **Model outputs** of exact `Decimal` arithmetic using S1–S7;
they are review calculations, not a run of the production engines.

| Case | Derivation before comparison | Comparison / classification |
| --- | --- | --- |
| 1 FTC | $44,900.99 has zero complete dollars of excess: $7,921. $44,901.99 has one: $7,921 − $0.275 = $7,920.725. S1 MD 3/13 and S2 cl 4. | **Supported conditionally.** Formula matches. The decimal inputs remain caller Scenarios; input precision is not independently certified by the word `verified`. |
| 2 Best Start | $79,001: $4,041 − $0.21 = $4,040.79. $79,000.99: zero complete dollars of excess, $4,041. S1 MG 2/3 and S2 cl 6. | **Supported conditionally.** Requires the specified fully abatable supported cohort and no protected month; no result is inferred for other birth cohorts. |
| 3 MFTC | At 52 qualifying weeks, $36,604 − $36,603 = $1; subtracting $36,603.99 gives $0.01. S1 ME 1/3 and S2 cl 5. | **Supported as formula scenarios; statutory input construction unverified.** `ME 3 attestation = true` does not demonstrate that $30,000 family income and the larger supplied net amount describe a coherent real claimant. No ME 3 derivation is supplied. |
| 4 AS imputation | Single cost basis: 0.7 × (300 − 93) = 144.90. At assets 2,700 / 2,800 / 8,100: imputation 0 / 1 / 54, raw result 143.15 / 142.90 / 129.65, final 144 / 143 / 130. Couple variant uses **cost 401**, basis 137.20: assets 5,400 / 5,500 give raw 136.20 / 135.95 and final 137 / 136. S3–S6. | **Supported at exact blocks; ambiguous at incomplete blocks.** At 2,799.99 complete-block reading gives 144; proportional reading gives raw 142.900025, final 143. At 5,499.99 those readings give 137 and 136 respectively. A started-block reading also gives 143/136 here. No reading is selected. |
| 5 AS ceiling | $16,200 satisfies r 15; 0.7 × (400 − 205) = 136.50, rounded to 137. $16,200.01 fails that asset requirement. R 18's non-beneficiary reduction is not applied to Jobseeker. S3, S4, S7. | **Supported.** Failed asset eligibility is represented by the project's `unsupported` status with no value, as the proposal states; it is not a calculated zero. |
| 6 AS final rounding | 0.7 × (103 − 93) = 7, retained as 7; 0.7 × (103.01 − 93) = 7.007, rounded to 8. S3, S4, S7. | **Supported conditionally.** This is final assessment rounding. The ordinary rate and other eligibility/exempt-asset facts must be supplied before a calculator can report either amount. |

**AI hypothesis (interpretation escalation, candidate Rule):** s 423(3)'s
counting reading treats only completed blocks as weekly income; a proportional
reading applies the ratio to a fractional block. An alternative reading starts
a new block on any excess. The retrieved text does not expressly settle this,
and the exact-block MSD example cannot distinguish them. WFF expressly says
complete dollars; that wording is absent here. The proposal correctly flags
the incomplete-block question; an independent reread does not close it.
DEC-001 remains the recorded project treatment of income-excess rounding,
not a decision on asset-block counting. Its proportional-reading consequences
above are conditional illustrations, not an extension of DEC-001.

## Findings and disposition

No P1 or P2 numerical defect was established in this proposal. Proposed
classifications below are **AI hypothesis** for review; Pete confirms them.

| ID | Severity | Location | Classification | Evidence / consequence | Suggested fix |
| --- | --- | --- | --- | --- | --- |
| B1 | P3 | Proposal lines 104–110, especially 105–106 | SPEC_ERROR | The text says the 8,100 ceiling row depends on a complete-block interpretation. Its excess is exactly 5,400: 54 blocks under all three readings, producing 130 in the single scenario. S3 s 423(3), S4 rr 18–19 and exact arithmetic above. | List 8,100 among the exact-block rows. Keep 2,799.99 and 5,499.99 unresolved. This correction selects no interpretation. |
| B2 | P3 | Proposal lines 65–66, 74, 152–153 | MISSING_SOURCE | The MFTC arithmetic is supported, but the stated $30,000 gross/family input and $36,603/36,603.99 net input have no displayed ME 3 construction. S1 ME 3(2)–(3) requires more than an after-tax label. | Label this explicitly an isolated caller-asserted formula scenario, or supply a source-derived coherent ME 3 construction before treating it as an entitlement benchmark. Do not alter protected values. |
| B3 | P3 | Proposal lines 130–138 | SPEC_ERROR | The AS rounding inputs omit the ordinary-rate, exempt-asset and household statuses required by the existing scoped input contract. S7 contains a different protected single rate row. The amount is conditional, rather than assured by the short input list. | Name the ordinary row and all scoped status assumptions, or explicitly inherit a named ordinary fixture's input facts. This asks for documentation, not a new test. |
| B4 | P2 (interpretation escalation) | Proposal lines 76–111, 147–148 | INTERPRETATION_AMBIGUITY | S3 s 423(3) and S8 leave incomplete $100 blocks unresolved. Complete-block and proportional readings differ by $1 in the selected final weekly amounts. The proposal already flags the question; this is not a newly established numerical defect. | Keep the two fractional rows unpromoted; Pete may request distinguishing primary evidence or record an interpretation decision. Do not treat a reread alone as resolution. |

**AI hypothesis (B4, P2 interpretation escalation; INTERPRETATION_AMBIGUITY):**
the part-$100 rows affect the final weekly amount by $1 in these scenarios.
They are already identified as ambiguous by the author, so this is an unresolved
policy question rather than a newly established defect in the proposal.
The relevant queue scope remains gated against promotion of those values.

## Verification and limits

**AI hypothesis — Fact candidate (method):** checked dated primary HTML, separately retrieved agency
guidance, compared the unchanged proposal at the pinned merge/main snapshots,
and performed exact arithmetic outside the production engine. No protected
file, production source, test case or regression pin was changed. No external
policy engine was read. Future 2027 rules, payment execution and administrative
income-input precision were not verified by this review.

**AI hypothesis — Fact candidate (method correction):** the root extraction initially missed the couple variant's
separate cost 401 and scratch arithmetic used 400. The displayed derivation
has been corrected to the proposal's actual Scenario; that scratch value is
not a finding against the author.

**AI hypothesis — Fact candidate (input-only cross-check):** a fresh Codex agent received only the six
Scenario descriptions, primary-source locations and existing scope decisions.
It recorded exact arithmetic before opening the proposal or this root review.
That independent derivation agrees with every displayed conditional amount,
including the couple cost 401, and separately identified the incomplete-block
ambiguity and MFTC construction caveat. It subsequently confirmed B1–B3 and
found no additional material defect in this review. This supplies an input-first
derivation of Claude's proposal; it is a same-model supporting check of the
new Codex-authored review document, not Claude's required review of this PR.

**AI hypothesis — Fact candidate (REVIEWER_ERROR correction):** the fresh agent initially described
failed asset eligibility as “no entitlement / zero”. After comparison with
the accepted Poltika contract it recorded the correction explicitly:
`unsupported`, no numeric value. The proposal's case 5 is correct. The frozen
scratch record retains that correction; no protected expectation was changed.

## What Pete decides

- Keep the incomplete-$100 rows parked; request more primary evidence; or
  decide between the expressly stated readings through an interpretation
  artifact. This review does not choose one.
- Retain the WFF decimal rows as caller-asserted formula scenarios, seek an
  administrative precision rule, or restrict future benchmark inputs to a
  separately sourced precision contract.
- Consider promotion of the supported rows only through the protected-value
  process after their complete scenario facts and independent review are
  recorded. MFTC needs an explicit scenario label or a coherent ME 3 derivation.
