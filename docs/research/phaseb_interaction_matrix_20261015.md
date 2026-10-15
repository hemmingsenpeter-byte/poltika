# Phase B interaction matrix — 15 October 2026

**Author:** GPT/Codex. **Status:** source-derived candidate handoff, not graph
approval. **Planning base:** `63359fecfe3b6659476528da021ea0ade0023537`.
Scope is Programme Task 9, limited to income tax, Jobseeker Support (JS),
Sole Parent Support (SPS), Supported Living Payment (SLP), WFF and AS.
Claude owns graph implementation and integration; Pete retains reserved
source/interpretation decisions. This note changes no policy, amount or test.

The supported WFF/AS relationship currently comprises income exclusions,
shared factual constraints and dated parameter provenance. It supplies no
direct household-calculated-output dependency. The tax draft is ordinary
salary/wages only, and the three benefit monetary procedures remain
unapproved. Their legal relationships below are candidates with explicit
stop points. They cannot presently demonstrate Gate B's required calculated
output feeding a dependent policy.

## Sources, dates and classification

Primary provisions were read before deriving the mappings, independently of
engine code. Dated official HTML/text was inspected directly where browser
retrieval failed. Retrieval/check date is **15 October 2026**. This is a
bounded source check, not whole-year legislative currency clearance.

| Key | Official authority and exact locators | State in this handoff |
| --- | --- | --- |
| ITA-C | [Income Tax Act 2007, 4 September 2026](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/): CF 1(1)(c); CW 33(1)(a)(i)–(iii). The official retained HTML header identifies version 947_0. | Retained authority; independently reread. AS exemption and taxable main-benefit distinction support retained mappings; no new tax slice approved. |
| ITA-M | [Same Act, Part M, 4 September 2026](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/parts/DLM1518405/): MB 1(1)(a)–(c), MB 2, MB 13(2)(l); MC 6(b)(i); MD 8; MD 14–15; ME 1(2)–(3), ME 3(2)–(3); MG 4. | Retained authority; independently reread from official retrieved text. New executable mappings remain candidates. Statutory MB 1/2 allocation is recorded without implementing a new apportionment rule. |
| SSA | [Social Security Act 2018, 26 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-26/): s 18; ss 338, 349–351; Schedule 2 main benefit; Schedule 3 cls 2–3, 8(1)(a),(l), 11–14; Schedule 4 Part 1 cl 1(g), Part 3 cl 1(d), Part 7. | Current Act index still identifies this consolidation. Independently read; retained legal distinctions plus candidate benefit mappings. |
| SSR | [Social Security Regulations 2018, 1 October 2026](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2018/202/en/2026-10-01/): rr 17(1)–(2), 18(1)–(3), 19, 205(1)–(3); Schedule 6. | New current-version correction: 4 September is superseded. Full body comparison finds only Schedule 1 cl 33(2)'s review-transition change; scoped rr 17–19/205 and Schedule 6 unchanged. This is author evidence pending review. |
| Benefit tax | [IRD DET 24/03](https://www.taxtechnical.ird.govt.nz/-/media/project/ir/tt/pdfs/determinations/miscellaneous/2024/det-24-03.pdf?modified=20240715225311), issued 10 July 2024; operative printed p 1, payments from 2 August 2024; cover 2024–25 onwards. SSA ss 350–351 supplies gross-up/payment treatment. | Newly located authority candidate; exact table application, gross-up and precision remain unreviewed. This is payment tax, distinct from final annual liability. |
| Retained decisions | [AS interaction contract](../../policy_specs/accommodation_supplement/specification.md#task-283-wff-as-interaction-contract), accepted 24 September; [AS DEC-003](../../policy_specs/accommodation_supplement/decisions/DEC-003-msd-paid-wff-income-exclusion.md); [ADR-0017](../../adr/0017-shared-household-model.md); [D32/D37/D38](../decision_log.md), 11–13 October. | Existing recorded acceptance only. DEC-003 retains the identified MSD-paid WFF inference; its TAA 80KN–80KO chain is retained evidence, not a new claim that those sections were reread today. No old acceptance is extended to new graph edges. |

All new AI-authored mappings remain **AI hypotheses** until the constitution's
source, independent-review and applicable Pete gates clear. A caller's
`verified` assertion remains a **Scenario**, not a calculated or agency fact.
Every future result retains the exact person/family, component, period, NZD
unit, source/version/locator, method, review state and dependency identities.

## Mapping matrix

**R** means a retained supported exclusion/fact contract; **C** means a new
candidate mapping; **B** means a blocked amount pathway; **P** means a statutory
parameter relationship. These labels confer no approval. Rows apply only to
the ordinary slices; mixed-benefit couples, relationship/care changes and
exceptional grants keep their existing exclusions. Dates use `[from,to)`.

| ID / state | Producer → consumer | Rule / decision | Period, units and exact mapping |
| --- | --- | --- | --- |
| I01 / R | Identified AS payment → WFF family-scheme-income derivation | ITA-C CW 33(1)(a); SSA Schedule 2 main benefit list; ITA-M MB 13(2)(l); retained AS interaction contract | AS's NZD/week payment is exempt and is not added to WFF annual family-scheme income. Already-correct WFF income is not reduced again. No weekly-to-annual conversion. |
| I02 / R | Identified WFF credit → AS chargeable-income derivation | SSA Schedule 3 cl 8(1)(l); retained DEC-003 and AS interaction contract | Exclude an identified MA–MG/MZ statutory credit from the AS assessment week's chargeable income, whether paid by IRD or MSD under the retained decision. No household WFF annual entitlement is divided into instalments or subtracted from an already-resolved income assertion. |
| I03 / C | Identified WFF credit, AS or other SSA benefit → JS/SPS/SLP income derivation | SSA Schedule 3 cl 8(1)(a),(l), subject to cl 2's ordering/overrides | Exclusions concern the classified income of the identified person over the applicable assessment period. Caller-resolved benefit income must reflect exclusions once; no automatic sum of other policy outputs. SPS/SLP's 52-week default or active r 205 weekly agreement remains explicit. |
| I04 / R factual | Dated JS/SPS/SLP **being-paid status** → AS claimant category | SSR r 17(1), r 18(1); ADR-0017; D37 | A resolved category covering the exact AS week selects the appropriate beneficiary branch. It is a status mapping, not an entitlement-amount mapping. Ordinary r 18 income reduction applies to non-beneficiaries; a computed zero benefit is not proof of non-beneficiary status. |
| I05 / R factual | Dated main-benefit **receipt** → WFF no-benefit/eligibility assertions | ITA-M MC 6(b)(i), MD 8; ADR-0017; D38 Q19(5) | MC 6 refers to the recipient during the relationship period; MD 8 separately covers claimant and spouse/partner. Any established receipt spell intersecting the WFF tax year contradicts a verified whole-year no-benefit assertion under D38, using dates only. Do not infer the year's other days from one week or rescale a benefit amount. |
| I06 / R guard; C monthly mapping | Main-benefit receipt plus monthly family income → WFF protected-credit status | ITA-M MD 14(1)–(2), MD 15; MG 4(1)–(2); retained interaction conservative guards | Receipt alone is insufficient to compute a protected month: month-specific person/relationship and statutory family-income tests also apply. Preserve the existing conservative contradiction check; no annual aggregate or week proves the monthly test false. MD 15 overrides MB 1(1)(a),(b) for its protected-FTC calculation. |
| I07 / B | JS/SPS/SLP gross benefit income → WFF family-scheme income | ITA-C CF 1(1)(c); ITA-M MB 1(1)(b), MB 2; SSA s 351 | The legal candidate is taxable benefit income, including tax paid on the person's account under s 351 where applicable, attributed to its paid-for period before required MB adjustments. It is not net M or bank cash. No `weekly result × 52`, calendar-day division or relationship-period allocation is authorised in this draft. |
| I08 / B | JS/SPS/SLP taxable income → annual income-tax component | ITA-C CF 1(1)(c); SSA ss 349–351; tax D11 slice | Main-benefit payment is a taxable income class, but it is outside the current ordinary salary/wage tax specification. Do not inject a benefit gross result into that salary field. Benefit payment tax under RD 11/DET 24/03 is separate from annual basic liability and final tax. |
| I09 / C, blocked | Reviewed income-tax liability → WFF MFTC adjusted liability | ITA-M ME 3(2),(3)(a),(c)–(e); ME 1(2)–(3) | ME 3 uses tax liability **on its adjusted income treated as net income**, with full-time-earner/relationship-period annualisation and other formula terms. A tax result could be reused only after exact person, tax base, period, coverage and liability meaning are proved equal. An ordinary tax-on-wages result does not establish those equalities. Keep attested net-family-scheme income under the current WFF contract. |
| I10 / exclusion, no amount edge | Income-tax liability / net salary result → JS/SPS/SLP or AS test income | SSA Schedule 3 cl 3; benefit income tests; SSR r 18 | These income tests use the relevant before-tax income definition. Do not subtract computed tax from that input or replace it with after-tax wages. Common earnings are separately classified for each consumer and supplied for its own period. |
| I11 / P, no household-output edge | Statutory JS/benefit maxima and statutory FTC rate → AS base/threshold construction | SSR r 17(2)(a)–(i), r 18(3); SSA Schedule 4 Part 7; retained AS DEC-002/table path | Beneficiary/non-beneficiary categories refer to statutory maximum weekly benefit rates. Parent cases (b),(d),(h) expressly reference maximum annual eldest-child FTC rate divided by 52; (f) instead says annual rate payable. This is parameter provenance, not a possibly abated household FTC output. Retain the approved table path; no recomputation or new interpretation of (f). |
| I12 / R scope guard | Per-person JS/SPS/SLP own-right receipt → concurrent-benefit compatibility | SSA s 18; Schedule 4 Part 1 cl 1(g), Part 3 cl 1(d); D11/D36; D37 | Identify person and overlapping dates. Section 18 restricts concurrent own-right main benefits for one person; separate partners' grants are recognised statutory categories. Their exclusion from the first benefit slices is project coverage, not a household-wide statutory ban. No second benefit amount is aggregated. |

## Propagation, precedence and required review cases

These are **required candidate test descriptions**, not new fixtures or claims
that graph tests have run. Monetary expectations require the protected-value
process and independent derivation. Existing calculated outputs cannot clear
an unresolved source or interpretation gate.

| IDs | Missing/unsupported propagation and asserted-versus-calculated precedence | Required interaction test and known limit |
| --- | --- | --- |
| I01–I03 | Unidentified payment or unresolved derivation gives `needs_review` when needed to establish the consumer's income; known outside-slice composition/period remains `unsupported`. An independently resolved valid consumer input gains no new producer-amount gate. Caller assertion cannot relabel a payment, and absence is never numeric zero. | Add identified AS/WFF to a raw payment inventory and verify the consumer's correctly derived income is unchanged; do not double-exclude an already-correct assertion. Repeat WFF payer IRD/MSD and unidentified-MSD cases. New benefit derivation is still unapproved. |
| I04 | Unknown/gapped status remains unverified; overlap/duplicate spells retain D37 validation refusal. A known unsupported claimant route stays unsupported. Neither grant assertion nor calculated amount overrides being-paid evidence. | Paid JS/SPS/SLP all week selects status; benefit amount zero alone does not. Missing spell, mid-week change and overlapping `NO_BENEFIT`/receipt do not select non-beneficiary income treatment. No mixed-benefit or mid-week legal method is added. |
| I05 | Missing recipient/date facts gate the relevant receipt comparison; monthly income is not required for a demonstrated date-only contradiction. Existing unsupported component takes precedence. Preserve and gate a contradicting whole-year assertion rather than silently overwriting it. | For each benefit, test claimant and partner receipt, one-day year intersection, adjacent outside-year spell and verified whole-year no-benefit contradiction. Omit monthly income and verify that a known date-only contradiction remains identified. |
| I06 | Missing monthly recipient/income facts gate a new protected-month derivation. They neither erase nor add preconditions to the retained receipt-based conservative guard. Existing unsupported component takes precedence. | Test unknown monthly income, relationship changes and MD 15 extra-pay-period treatment as unsupported/unresolved derivation paths. Do not compute protected entitlement from receipt alone or clear an existing contradiction because monthly income is unknown. |
| I07–I08 | Blocked while benefit gross-up/precision, protected values, complete periods or consumer scope remain unresolved. `needs_review`/`unsupported` propagate to the dependent amount without becoming zero; no salary assertion overrides known benefit income. | Net-M versus gross discrimination; tax paid under s 351 retained once; wrong-year and one-week-to-year refusal. Salary-only tax must reject a known benefit-income path even if its numeric amount resembles wages. A full gross benchmark remains missing. |
| I09 | Tax output is authoritative only after its own gate clears and its consumer-specific mapping is reviewed. A matching number alone does not justify precedence. A conflicting asserted tax/net-income amount gates that dependent consumer; blocked tax never supplies zero. | Two equal gross wage amounts with different ME 3 adjustments must not reuse the same tax result blindly. Check missing tax authority, wrong period and tax-on-adjusted-income mismatch. D11/Q16 and final-head review remain separate tax gates. |
| I10 | There is no tax-output dependency. Missing, blocked or contradictory unrelated tax/net-income output does not gate a benefit/AS result whose own before-tax income facts are independently valid. Its own unresolved income definition or period still gates normally. | Preserve valid before-tax JS/SPS/SLP/AS inputs and verify that changing or refusing an unrelated tax output leaves them unchanged. No tax amount is subtracted, overridden or replaced by zero. |
| I11 | Missing/unreviewed statutory parameter or unresolved category gates construction; an unknown household FTC output is not substituted. Approved AS table values retain their source and independent-review gates. | Change household FTC entitlement while retaining the same approved AS table category: AS must not acquire a new dependency on that output. Verify r 17(f) does not silently inherit adjacent maximum wording and r 18(3)'s sole-parent Test 3 counterfactual is not actual JS income-test output. |
| I12 | Contradictory own-person overlapping receipt refuses; the supported-slice exclusion for separate partners stays `unsupported / not_modelled`, before missing facts. No calculated amount proves identity or receipt. | Same person with concurrent different benefits refused; separate partners receiving in their own right identified as outside first-slice coverage without asserting statutory illegality. Adjacent spells preserve distinct dates; no entitlement combining rule invented. |

All rows retain native periods. D32/Q10 requires already-resolved caller
amounts for each policy period and exact tiling where summed; a straddling
spell or gap never licenses apportionment or zero. WFF whole-year children,
AS dependent children, benefit-dependent children and relationship meanings
stay policy-specific under ADR-0017/D38. A shared person ID permits comparison;
it does not establish common eligibility or common income.

## Decision-ready handoff

Retain I01/I02 and the reviewed factual constraints without presenting them
as the new connected computational graph. Claude can review this matrix
against the exact final source/specification heads now. New I03/I06–I09
amount or monthly mappings need their source/scope gates first; I11 needs no
household-output edge on the existing approved table path. Do not choose a
new numerical edge merely to satisfy Gate B.

The next bounded source item is the JS gross-up/table/precision pack in the
existing benefit draft [PR #220](https://github.com/hemmingsenpeter-byte/poltika/pull/220).
After an approved monetary producer exists, select a consumer whose exact
definition and period can be demonstrated, obtain independent mapping review
and Pete's reserved decisions, then hand Claude a protected interaction case.
Gate B still requires a real supported household exercising that calculated
output into a dependent calculation; co-running calculators, exclusions and
asserted-status checks alone do not establish it.

Validation for this source-only handoff: manually checked the 12 mappings
against the cited primary provisions; all 4 relative document links resolve;
`git diff --no-index --check /dev/null` against this file passes. New candidate
and retained decision labels remain separate. No simulator or external
policy engine was used to derive any expected result in this note.
