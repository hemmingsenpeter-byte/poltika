# Personal income tax — basic annual salary/wage slice

**Programme:** Phase B Task 7; `BUILD_PLAN_v0_3.md` 2.1.
**Author/source check:** GPT/Codex, 8 October 2026, Pacific/Auckland.
**Status:** `draft_pending_review`; no policy version or executable policy.
**Scope commission:** Pete's D11, 5 October 2026. This is the specification
follow-up to source-scope PR #148, called onboarding PR 2 in programme
status. Its content is the `new-policy` skill's sources/specification step;
the skill's separate values/expected-results step is not included.

All proposed statutory interpretations are **AI hypotheses pending promotion
to Rule**, under the Epistemic Constitution. Source observations below carry
their actual authority and check date. D11 approves the slice, not rates,
precision, test expectations or implementation. A source-linked draft is
not a source-approved executable specification. The open decisions in
[decisions/](decisions/DEC-001-annual-authority.md) and
[Pete's queue](../../PETE_QUEUE.md) block promotion of the affected rules.

## Supported scope and component

The proposed component is `basic_annual_income_tax`, per individual natural
person, on ordinary salary/wage taxable income for the **2026–27 tax year**.
The standard year is 1 April 2026 through 31 March 2027 inclusive, represented
as `[2026-04-01, 2027-04-01)`; YE 1(2) supplies those endpoints. Income must
already be classified and allocated to that income year. Full-year ordinary
New Zealand residence, ordinary salary/wages only, no deductible amounts or
available losses, and no special-rate category are the bounded slice's
asserted support conditions. They are deliberate scope limits, not claims
that other taxpayers owe no tax. ([ITA, YE 1, YD 1, CE 1, BC 2–6 and
Schedule 1 Part A cl 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/))
Amendments to CE 1 and CE 1BA in the 2026 annual rates legislation were not
assessed for this slice; CE 1(1)(a) is the only provision relied on.

Basic annual tax is before credits, tax already paid and ACC. It is not
terminal tax, a refund, PAYE, total payroll deductions, net wages or complete
disposable income. BC 8 distinguishes credits and terminal tax; IRD's yearly
calculator confirms this output scope. No missing credit or other component
is set to zero. ([ITA, BC 8](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[IRD yearly-tax calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income))

The 2026–27 annual-authority gate remains `needs_review` under D11 and the
user's instruction. Bill 344-1 is proposed law only, recorded as rank-4
change context. TAA s 92A permits **Commissioner assessments** at basic
rates before an annual taxing Act, with adjustment if annual rates differ.
That provision means lack of enactment does not make every official
assessment invalid; whether it supports a different Poltika component
requires Pete's decision. This draft retains D11 and does not infer that
Poltika performs a Commissioner assessment. ([ITA, BB 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[TAA, s 92A](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/),
[DEC-001](decisions/DEC-001-annual-authority.md))

## Input and outcome contract

These are proposed semantic inputs, not new runtime fields or approved
`facts.yaml` entries. Questions and admissible statuses belong in the later
values/facts PR. A caller's `verified` status remains a **Scenario** assertion.

| Input | Required meaning | Rule grounding |
| --- | --- | --- |
| Individual identity and natural-person status | One identified person; never a household total | IT-01; YD 1; Schedule 1 Part A cls 1–14 |
| Residence/scope assertions | Whole-year ordinary NZ resident; no special/non-resident regime | IT-01; YD 1; explicit D11 slice restriction |
| Income composition | Ordinary salary/wages only, with special employment items excluded | IT-03; CE 1(1)(a) and other CE 1 categories |
| Annual taxable income | Known non-negative exact NZD amount allocated to the specified year, independently established under BC 2–5 and BD 1/3 | IT-02/03/04 |
| Deductions and available losses | Explicit evidence of none for this bounded slice; never inferred from an absent field | IT-04; BC 3–5; DA 2/3 |
| Reference period/requested policy identity | Exact reviewed year and future approved version; neither chosen from today's date | IT-02; YE 1; repository version contract |
| Authority and precision review states | Both approved before any numeric authoritative result | IT-05/06/08; D11; DEC-001/002 |

`gross_household_income`, WFF family-scheme income, AS chargeable weekly
income and take-home pay are not substitutes for annual individual taxable
income. A weekly wage is not annualised here. No shared-household adapter,
benefit-tax input or graph edge is approved by this specification; Tasks
5/6/9 and the interaction onboarding step own those mappings.

Known facts outside the supported slice give `unsupported` / `not_modelled`;
unknown required facts or unresolved authority/precision give `needs_review`
with named missing facts/reasons. `unsupported` outranks `needs_review`.
Known zero income is distinct from unknown income, but **even zero receives
no numeric result while the policy gates remain unresolved**. These are
repository outcome rules, not tax-law eligibility findings. Invalid numeric
transport belongs to request validation; known losses or non-standard years
are declared outside scope rather than coerced to zero/current rates.

## Source-linked rule map

Source IDs resolve in [sources.yaml](sources.yaml). Each legal row cites
rank-1 legislation or amending legislation. Agency guidance is a separate
cross-check, never substitute annual-rate authority.

| ID | Proposed interpretation / boundary | Primary source and locator | Review state |
| --- | --- | --- | --- |
| IT-01 | One natural person in the agreed ordinary resident slice; no residence inference from citizenship/address/age, no joint household assessment | `it-income-tax-act-core`: YD 1; BC 2–6; Schedule 1 Part A cl 1 and special-category cls 2–14 | Draft scope contract; independent review pending |
| IT-02 | Standard 2026–27 tax year only; input is already allocated to that year | `it-income-tax-act-core`: YE 1(1)–(5), BC 2, BD 3(1)–(4) | Draft; no derivation/timing algorithm or annualisation |
| IT-03 | Ordinary salary/wages are employment income; assessable income excludes the classes in BD 1(5) | `it-income-tax-act-core`: CE 1(1)(a), BD 1(1)–(5) | Draft; exemption/timing classification supplied, not inferred |
| IT-04 | Annual gross income, deductions, net income and available losses are distinct. The no-deduction/no-loss slice can use the independently established taxable amount | `it-income-tax-act-core`: BC 2–5; DA 2(4),(7); DA 3(3)–(5) | Draft; express deduction overrides are not denied |
| IT-05 | General basic-rate table applies only to the extent no special basic rate under cls 2–14 applies | `it-income-tax-act-basic-rates`: Schedule 1 Part A cl 1/Table 1; `it-budget-measures-act-2024`: ss 2(5), 37(1),(4) | Table transcribed below; 2026–27 authority remains `needs_review` |
| IT-06 | BB 1 uses annual taxing legislation. TAA s 92A separately permits Commissioner basic-rate assessments and later rate adjustment | `it-income-tax-act-core`: BB 1; `it-tax-administration-act-assessment`: s 92A(1),(2) | `needs_review`; DEC-001, D11 gate retained |
| IT-07 | BC 6 gives basic liability for a filing taxpayer; BC 8 separately uses credits/withholding and determines terminal tax. Statutory non-filing status is not absence of a manual IR3 | `it-income-tax-act-core`: BC 1, BC 6(1),(2), BC 8, YA 1 filing/non-filing definitions; `it-tax-administration-act-assessment`: ss 22I(1),(2), 92 | Draft; component is not a completed assessment |
| IT-08 | No fractional-dollar, intermediate/final rounding or tie convention has been established for this component | `it-income-tax-act-basic-rates`: cl 1/Table 1; `it-tax-administration-act-assessment`: checked provisions do not settle precision | `MISSING_SOURCE` / `needs_review`; DEC-002 |

### Documentary rate table

This is a transcription of **Schedule 1 Part A Table 1**, in the ITA version
dated 4 September 2026, retrieved 3 October 2026 and re-checked 8 October 2026
(`sources.yaml`). It is not a `policy.yaml`, approved
2026–27 parameter set or statutory expected-value fixture. Literal ranges
describe each dollar as the source prints them; this draft does not resolve
fractional dollars between those labels.

| Statutory row | Range of dollar in taxable income (NZD) | Tax rate (fraction) |
| --- | --- | --- |
| 1 | $0–$15,600 | 0.105 |
| 2 | $15,601–$53,500 | 0.175 |
| 3 | $53,501–$78,100 | 0.300 |
| 4 | $78,101–$180,000 | 0.330 |
| 5 | $180,001 upwards | 0.390 |

The source directs application of each dollar's relevant rate, and cl 1
defines the basic rate using total table tax divided by taxable income;
BC 6(1) multiplies taxable income by that rate. It is not a single highest
bracket rate applied to all income. BC 6(2) separately treats zero/negative
calculated liability as zero; implementation must avoid division by zero.
No executable fractional-income formula or rounding rule is adopted here.
([ITA, BC 6 and Schedule 1 Part A cl 1/Table 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/))

Part 4 of the 2024 Budget Measures Act commenced on **1 April 2025** under
s 2(5); s 37(1) replaced Table 1 and s 37(4) applies it for **2025–26 and
later income years**. Applicability is separate from the annual taxing Act
and future amendment coverage. IRD's table labelled “From 1 April 2025”
cross-checks these five rates. No mid-year or full-future-year assurance
follows from a current web page. ([2024 Act, ss 2(5), 37](https://www.legislation.govt.nz/act/public/2024/19/en/2024-06-04/),
[IRD rates](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals))

## Proposed calculation and trace sequence

1. Validate policy identity/year and explicit supported-slice facts. Report
   out-of-scope facts and missing facts without inventing values (IT-01/02).
2. Verify the annual taxable amount's meaning, composition, year, no
   deductions/losses and general-rate applicability (IT-03/04/05).
3. Resolve current period-specific authority and reviewed precision.
   Either pending gate stops a numeric result (IT-06/08). Bill 344-1 never
   supplies an approved statutory rate.
4. **After approval only**, apply the reviewed general-table calculation
   and sourced precision procedure, including the known-zero path (IT-05/07).
   This draft cannot specify that numeric step completely.
5. Emit only this basic-tax component with annual NZD unit, individual,
   reference period and Model-output class. Trace actual input assertions,
   policy/version, parameter intervals/review states, source/locator,
   rule/decision IDs, calculation/rounding steps and retained artifacts.
   Outcome precedence and provenance follow existing repository contracts.

## Explicit exclusions

All these are `unsupported` / `not_modelled` for this first slice, not
findings that the tax law exempts them: main benefits (CF 1/YA 1, deferred
to the interaction step); self-employment/business, rent/investment/foreign
income; non-resident or changing-residence cases; non-standard years;
loss/deduction computation; trusts/companies and special basic rates;
schedular/PIE regimes; unusual employment payments, reimbursements,
accommodation, shares, directors' fees and overpayment adjustments.
Anchors: BC 2–7, CE 1, CF 1, DA 2/3, YD 1, YE 1, Schedule 1 Part A cls 1–14.

PAYE code/pay-period withholding (RD 3), ACC, student loans, KiwiSaver,
IETC/other credits (Parts L/M; LC 13), refunds/terminal tax (BC 8), and
complete disposable income remain separate outputs. Excluding their
calculation does not imply a zero deduction, credit or payment.

## Approval and validation handoff

DEC-001 (s 92A and D11 authority), DEC-002 (precision) and DEC-003 (the IR3G
table discrepancy) are open, linked to Pete's queue. No interpretation is
silently chosen. Independent Claude source/spec review and Pete's decisions
must precede an approved specification. The IRD calculator page is scope
evidence only; no numerical benchmark was executed or retained.

The later values/facts/cases PR must supply source-linked dated parameters,
fact questions, independent spec cases at each bracket and both sides,
known zero versus missing income, fractional amounts and every excluded
case, plus independently retained official benchmarks. Regression coverage
must pin outcome/period/version/authority/precision gates and provenance.
No expected statutory value, engine, schema, API or protected existing
policy artifact is changed by this PR. Tasks 7 and Gate B remain incomplete.
