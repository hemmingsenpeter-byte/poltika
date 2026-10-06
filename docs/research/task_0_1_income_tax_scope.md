# Personal income tax: source scope for Pete's D1 decision

**Programme:** Phase B Task 7; detailed lane `BUILD_PLAN_v0_3.md` local 0.1.
**Author/check date:** GPT/Codex, 3 October 2026, Pacific/Auckland.
**Original base:** prepared programme migration `422b055`.
**Closeout refresh:** reconciled onto `main` at `1e185f7`, 5 October 2026;
reviewer P3 corrections and explicit evidence limitations added.
**Status:** draft source research and scope recommendation. The later
[independent Claude source review](../../reviews/2026-10-03-income-tax-source-scope.md#author-transcription-of-claude-review-6-october-2026)
is recorded, and the final-head cross-model review is in
[reviews/2026-10-06-pr148.md](../../reviews/2026-10-06-pr148.md) (merged as #148).
A reviewed supported-slice specification remains outstanding. The
[Q5 decisions recorded in #167](https://github.com/hemmingsenpeter-byte/poltika/pull/167)
record the later scope commission; they approve no tax parameter or rule.

The [draft catalogue](../../policy_specs/income_tax/sources.yaml) uses the
existing `SourceCatalog` shape. This note prepares the sourcing part of
onboarding PR 1 under the [new-policy skill](../../.claude/skills/new-policy/SKILL.md).
It supplies no approved specification, runtime parameter, expected statutory
test value or new calculation. Task 7 remains incomplete.

## Recommended bounded slice

Propose **basic annual personal income tax for the 2026–27 tax year**, per
resident adult, using separately evidenced ordinary salary/wages and, after
the benefit-source and interaction reviews, the three supported main-benefit
categories. The period is `[2026-04-01, 2027-04-01)` in repository notation;
the Act identifies the April–March tax year in YE 1(2). The proposed first
output is basic tax before credits, tax already withheld and other deductions.
This is a scope proposal, not a final assessment or complete disposable-income
measure. ([Income Tax Act: BC 2–8, YE 1](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[IRD annual-calculator scope](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/work-out-tax-on-your-yearly-income))

The reference year aligns with existing WFF's reviewed period; alignment is
a project choice for Pete, not a legal rule. An ordinary annual taxable-income
amount must be established independently for each person. Gross household
grouping income and WFF family-scheme income cannot stand in for it: BC 2–5
distinguish assessable income, deductions, net income, losses and taxable
income. Today's `PersonRecord` contains id, role and age; its separate
`gross_household_income` field is grouping metadata, not an engine input.
The shared-household task must supply the reviewed mapping before integration.
([Income Tax Act: BC 2–5](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[population contract](../../src/poltika/semantics/population.py),
[current WFF specification](../../policy_specs/working_for_families/specification.md))

## Dated evidence and coverage

The catalogue records retrieval date, source version, pinpoint locator,
review status and limits for every source. NZ Legislation's dated HTML
was read directly when the web reader could not retrieve it; the official
latest Act was also checked and labelled as at 4 September 2026. Agency
page-update dates describe the page, not legal effective dates. Only the
listed provisions were reviewed; this is not a whole-Act or full-future-year audit.

| Scope question | Author-checked evidence | What remains outside this pack |
| --- | --- | --- |
| Ordinary employment income | CE 1(1)(a); DA 2(4), (7); `it-income-tax-act-core` | Full timing/deduction rules; accommodation, employee shares, reimbursements and unusual pay |
| Core main benefits | CF 1(1)(c), YA 1 main benefit (a)–(b); SSA Schedule 2 paragraph (a)(i)–(vii); `it-social-security-act-main-benefit` | Youth payment, young parent payment, emergency benefit and main benefit equivalent assistance are `unsupported` in the proposed first slice. Benefit amounts, gross-up, partner allocation and weekly-to-annual reconciliation remain separate gates; local 0.2–0.3 and D8/D9 |
| Basic rates and applicability | Schedule 1 Part A clause 1/Table 1; 2024 Act ss 2(5), 37(1), (4) | 2026–27 annual-rates enactment and later amendments |
| Annual basis versus PAYE | BC 6/8; RD 3; IRD annual calculator; IR340 April 2026, printed p3 | Tax-code selection, pay-period withholding, refund/square-up, payroll rounding |
| Credits and levies | LC 13; IRD IETC page; annual-calculator exclusions | IETC and other credit calculations, ACC levy, KiwiSaver and student loans |

The two Acts referenced in the table are the [Income Tax Act 2007](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/)
and [Taxation (Budget Measures) Act 2024](https://www.legislation.govt.nz/act/public/2024/19/en/2024-06-04/).
The main-benefit definition is in the [Social Security Act 2018](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/).

## The annual-rates gate

BB 1 requires an annual taxing Act. [Act 2026 No 8, s3](https://www.legislation.govt.nz/act/public/2026/8/en/2026-03-30C/)
sets 2025–26 rates. The retrieved 2026–27 instrument is **Bill 344-1**,
whose clause 3 would set that year's rates. The [IRD status page](https://www.taxpolicy.ird.govt.nz/bills/2026-fbt-simplification-tax-bill)
is dated 15 September; the [Parliament progress page](https://bills.parliament.nz/v/6/ae9d3517-66d6-4a30-c155-08df0eed0d02?Tab=history&lang=en)
published 1 October still shows select committee and no completed Royal
Assent entry. These observations leave enactment unverified; the Bill is
not accepted as policy authority. Parliament lists introduction on
9 September while IRD/NZ Legislation list 10 September; that metadata
difference is recorded without resolving it.

The separate Claude review could not reproduce Parliament's client-rendered
progress content through a plain fetch. That detailed progress claim retains
its initial author-retrieval status; an independent browser retrieval is
still needed. The dated IRD page and official Bill text provide separate
bill-stage evidence, without establishing enactment.

The [Bill's explanatory note and clauses 3 and 133(1), (3)](https://www.legislation.govt.nz/bill/government/2026/344/en/latest/)
were re-read on 5 October 2026. The note proposes retaining the rates currently
specified in Schedule 1 Part A for 2026–27. Clause 133's separate new Part A
clause 18 concerns tax-exempt entities' beneficiary income from 2028–29;
it does not replace the ordinary clause 1 table. This is rank-4 proposed-law
context; the annual-rates gate below remains `needs_review`.

Keep 2026–27 annual-rate approval `needs_review` until the enacted instrument
and applicable amendments are verified and independently reviewed. The
[IRD rates page](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals)
and [2026–27 PAYE table](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-apr-2026.pdf?modified=20260323203256)
do not settle this separate annual-taxing-Act requirement. Preparing sources
and cases is possible; promoting an authoritative annual result is gated.

## Exclusions and unresolved decisions

For the first component, propose excluding business/self-employment profit
derivation, rental and investment classification, overseas/non-resident or
part-year residence cases, non-standard income years, trusts/companies and
special basic-rate cases, losses, deduction computation and schedular/PIE
regimes. The general-rate applicability is limited by Schedule 1 Part A
clause 1; BC 7 has separate schedular rules, YD 1 governs residence and
YE 1 distinguishes income years. An asserted total with unclassified income
does not meet the proposed supported slice. ([Income Tax Act](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[IRD taxable-income guidance](https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/your-taxable-income))

IETC remains a separate unmodelled credit. A basic-tax component may be
reported with its limitation; complete disposable income needs the relevant
credit model or an evidenced exclusion. PAYE withheld is not supplied by
dividing annual tax by weeks: IR340 includes ACC and depends on tax codes.
Missing taxable-income facts, unresolved annualisation, unreviewed rounding,
and unverified period coverage remain visible review gates. Verified
out-of-slice facts should map to `unsupported` / `not_modelled` in the later
specification; missing facts must never become zero. ([LC 13](https://www.legislation.govt.nz/act/public/2007/97/en/2026-09-04/),
[IRD IETC](https://www.ird.govt.nz/ietc),
[IR340, p3](https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-apr-2026.pdf?modified=20260323203256),
[onboarding workflow](../../.claude/skills/new-policy/SKILL.md))

Fractional-dollar treatment and final/intermediate rounding have not been
established. BC 1 distinguishes filing and non-filing taxpayers; the later
specification must source the applicable status and assessment path before
calling a basic-tax component a person's legal assessed liability. No
official calculator result or numerical worked example was
retained: the calculator guidance is scope evidence, not a benchmark. The
later values/expected-results PR must source these and independently review
spec boundaries, benchmark cases and regressions before implementation.

The rounding search in this source pass was limited to BC 6, Schedule 1
Part A clause 1, IRD's yearly-calculator scope page and IR340's cover/printed
page 3. It did not establish a rounding rule. Tax Administration Act
assessment provisions, a published IRD calculation method and retained
official calculator outputs still need a dedicated source check; none is
claimed to have been searched or verified here.

## Concrete D1 options for Pete

| Option | Scope and consequence |
| --- | --- |
| **A — recommended** | Approve preparation of the 2026–27 basic annual-tax slice above; salary/wages first, the named benefit types after their source/interaction reviews. Retain the annual-rates gate and explicit credit/levy exclusions. This keeps the intended household reference year. |
| B — enacted-year component | Start with 2025–26 basic annual tax after a separate historical-period review. It cannot connect to current 2026–27 WFF without separately sourced matching-year coverage. |
| C — withholding first | Specify 2026–27 ordinary payroll PAYE first, including the applicable code/pay-period/levy scope. This adds a different output and additional sourcing; it does not substitute for annual assessment. |

Pete's choice must be recorded before the supported slice is treated as
accepted. Local 0.2–0.4, D8/D9 and the disposable-income/credit choices stay
open. Source preparation can continue in parallel with the shared-household
work; implementation and integration follow the five-PR onboarding gates.
