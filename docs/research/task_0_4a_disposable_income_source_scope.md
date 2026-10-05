# Disposable household income — D2 primary-source scope

Date: 5 October 2026, Pacific/Auckland. Author: GPT/Codex.
Status: source-only draft; independent Claude review and the final D2
definition/coverage decision remain pending. Commission: Q5, detailed
household lane local 0.4a. No formula, parameter, benchmark, statistical
threshold or executable policy specification is approved by this note.

## Dated source inventory

| ID | Official source and version | Locator and bounded use |
| --- | --- | --- |
| DI-1 | [Stats NZ, HILS concepts and definitions](https://www.stats.govt.nz/methods/measuring-child-poverty-in-the-household-income-and-living-survey-concepts-and-definitions/), published 12 February 2026; retrieved 5 October | “Income definitions”; “Child and household definitions”; “Housing costs”. Applies to year ended June 2025 onwards; candidate complete statistical definition, not a tax-law definition |
| DI-2 | [Stats NZ, June 2025 technical appendix](https://www.stats.govt.nz/methods/child-poverty-statistics-year-ended-june-2025-technical-appendix/), published 26 February 2026; retrieved 5 October | “Reference and collection period”; “Steps to create household equivalised disposable income”; “Note on determining income-sharing unit”; WFF administrative-data timing. Method and period limits |
| DI-3 | [Stats NZ, HILS error notification](https://www.stats.govt.nz/reports/error-notification-for-household-income-and-living-survey-hils-data-for-year-ended-june-2025/), published 29 September 2026; retrieved 5 October | “The importance of qualification information”; “Next steps”; “Important information for data users”. Required publication-vintage check before selecting comparators |
| DI-4 | [MSD, Household Incomes Report 2017](https://www.msd.govt.nz/documents/about-msd-and-our-work/publications-resources/monitoring/household-income-report/2017/2017-incomes-report-wed-19-july-2017.pdf), dated 19 July 2017 | “About this report” (PDF page 5, printed page 1); Section A (PDF page 7, printed page 3). Historical cash-income concept; not assumed identical to HILS |
| DI-5 | [MSD, 1982–2018 report landing page](https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/monitoring/household-incomes/household-incomes-1982-to-2018.html), retrieved 5 October; links the 2019 report | “The Incomes Report”; “Documents”. Confirms HES 2017–18 and previous-twelve-month interview reference. Body formula not independently extracted in this pass |

All are primary official statistical/research sources. No external policy
engine implementation was inspected. Retrieval is a dated observation, not
an assertion that the live HTML is an immutable publication snapshot.

## Candidate whole definition and distinct units

DI-1 defines personal disposable income by adding tax credits to total
personal income and deducting ACC levy and tax payable. Credits expressly
include WFF and IETC. Personal income spans earnings, self-employment,
investment, pensions, government assistance, regular transfers and specified
irregular receipts. Its irregular-income list includes inheritance and gifts;
these cannot be dropped from a claimed whole HILS definition without review.
Household disposable income aggregates members aged at least 15. A household
can include unrelated residents sharing facilities. Statistical household,
benefit claimant/partner and WFF family units require separate mappings.

DI-1 also treats equivalisation and subtraction of housing costs as separate
operations. Housing costs concern the primary property and include rent,
mortgage principal/interest/fees, property rates and building insurance.
No equivalence scale or after-housing-cost measure is selected here.

DI-4's historical report uses household after-tax cash resources over the
year preceding interview, then adjusts for household composition. It excludes
capital gains themselves while including income from capital. This does not
establish how every DI-1 irregular receipt should map: classification and
vintage differences remain questions for review, not silently harmonised rules.
No modelled housing service or in-kind transfer is added by this note.

## Time and publication-vintage boundary

DI-2 interviews run July–June, with each household reporting its preceding
twelve months. “Year ended June” therefore labels a survey collection year;
it is not automatically the common April–March tax year. WFF annual records
are apportioned across tax years to align with interview reference periods.
Household income is assigned to people for income-based poverty analysis;
person-weighted thresholds differ from household summary medians. Unrelated
household members can make this statistical unit broader than benefit families.

The v0.3 benefit proposal is an established-grant weekly entitlement at a
specified pre-November date, while the tax proposal is annual 2026–27 basic
tax. Neither alone supplies a rolling-year household record. Before combining
them, a specification must settle a common reference period and source each
annualisation/allocation rule. A convenient weekly multiplication is not
established by these statistical documents.

DI-3 reports qualification errors affecting income imputation and weighting.
Original release pages remain online unchanged; corrected selected measures
are supplied separately, with fuller revisions planned for February 2027.
The notice covers 2024/25–2026/27 survey years. Future comparison artifacts
must identify which original or corrected publication was used. This draft
retains no numerical comparator and changes no protected expected value.

## Coverage questions before a definition can become executable

This table compares the research requirement with the repository's reviewed
capabilities and proposals; it does not assert a person's missing income is zero.

| Component/boundary | Required follow-up for Poltika |
| --- | --- |
| Ordinary earnings | Source gross/net classification and person/period allocation; metadata income is not a verified engine input |
| Three core main benefits | Complete their separate specifications and gross weekly existing-grant scope; preserve grant, entitlement and paid-income distinctions |
| Other income classes in DI-1 | Inventory self-employment, investment, pensions, other transfers and irregular receipts; show unmodelled coverage explicitly |
| WFF | Retain component statuses and paid-for periods. An unresolved IWTC must not become zero or a complete WFF total |
| IETC and ACC levy | Separate unmodelled components requiring sources/specifications; basic annual income tax omits both |
| AS and other assistance | Source recipient and period allocation; an existing scoped AS result does not establish every government-payment category |
| Tax payable versus basic tax | Review the chosen income-tax component's limits, tax credits and assessment path before treating it as the entire statistical deduction |
| Household membership and period | Record source-compatible residents, shared-facility facts and common observation interval; preserve policy-specific families/partners |
| Housing costs/equivalisation | Separate decisions and source maps if an AHC or equivalised result is commissioned; neither is a default disposable-income step |

## Gaps and review handoff

DI-1 supplies a current whole candidate definition; D2 must still record its
chosen publication/version, covered components and treatment of every uncovered
component. This note chooses neither Stats NZ nor MSD as the final contract.

`MISSING_SOURCE`: the 2019 MSD report Word download was retrieved, but the
available converter treated the binary file as plain text. Its body was not
verified; only DI-5's landing-page metadata is relied upon. Obtain a reliable
extraction or official PDF before claiming the later MSD formula is checked.

Independent review should re-read the five sources, verify the reported
locators and income-class coverage, compare the full candidate definitions,
and classify any discrepancy under the review doctrine. Particular questions
are irregular receipts, tax-credit/deduction completeness, income-sharing unit,
annual versus weekly scope and corrected publication vintages. D3 adequacy
measures remain a separate commission; no poverty line is selected here.

Author preflight: official Stats HTML was retrieved using a browser user agent;
content and publication dates were read from the site's `pageViewData` JSON
payload where the web reader returned only a shell. MSD HTML/PDF were read
separately. `git diff --check` and relative-link checks apply to this document
only; no calculation or numerical benchmark was tested. A new final-head
Claude review is required before this draft can be accepted as reviewed sources.
