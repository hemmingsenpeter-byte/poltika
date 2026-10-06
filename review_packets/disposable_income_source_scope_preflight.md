# Disposable-income source scope — current-main author handoff

Date: 6 October 2026, Pacific/Auckland. Author: GPT/Codex.
Label: **author preflight**, with knowledge of the author's rationale;
independent final-head Claude source review remains pending.

Current main was fetched at `c72c409ac15f78f47691211ba343a3d219f51648`
and merged normally into original PR head
`1f538501209e356e5f3f7141fb8ff2287c33e1f7`. The [source note](../docs/research/task_0_4a_disposable_income_source_scope.md)
and [historical review transcription](../reviews/2026-10-06-disposable-income-source-scope.md)
are unchanged. This packet makes their evidence and extraction gaps explicit
for review; it adds no source claim, formula, comparator or D2 decision.
The exact final published SHA and command results are recorded in the PR
after the committed head is checked in a separate worktree.

## Mechanical review inputs

- Programme contract: detailed household lane local 0.4a; Q5 commission in
  [#167](https://github.com/hemmingsenpeter-byte/poltika/pull/167).
- Primary inputs: DI-1–DI-5 in the source note's dated inventory, with official
  Stats NZ/MSD URLs, purpose limits, publication/reference periods and locators.
- Expected author contract: keep complete official definitions, income units,
  component coverage and period/publication vintages distinct; missing evidence
  and unmodelled components never imply numeric zero.

## Candidate-definition evidence map for Claude

This is an index to the existing draft, not an independent re-reading or an
approved definition. An unestablished field stays an explicit source gap.

| Field required for D2 review | Stats NZ HILS candidate, DI-1/DI-2 | Historical MSD candidate, DI-4 | Later MSD candidate, DI-5 |
| --- | --- | --- | --- |
| Source | DI-1 concepts/definitions and DI-2 June 2025 technical appendix; DI-3 is the publication-vintage warning | July 2017 Household Incomes Report; identified PDF/printed pages and footnotes | 1982–2018 landing page only; linked 2019 report body unverified |
| Purpose | Official income/child-poverty statistical definitions and methods | Historical household-income reporting; not assumed identical to current HILS | Later household-income reporting metadata; formula-purpose limits require report-body verification |
| Unit of analysis | Personal disposable income aggregated over household members aged at least 15; household/person weighting and policy families are distinct | Sum of personal disposable incomes; individual/benefit-unit tax estimation and household-composition adjustment are recorded separately | Household-report metadata only; detailed income-sharing/equivalisation units not verified |
| Income components | Source note records earnings, self-employment, investment, pensions, assistance, transfers and specified irregular receipts including inheritance/gifts | Source note records regular/recurring cash-income convention and capital-gains distinction; full component mapping remains for source review | Not established from landing-page metadata; `MISSING_SOURCE` remains |
| Taxes/transfers | WFF/IETC credits, ACC levy and tax payable are expressly indexed in the note; full component coverage requires review | Taxwell/earlier Taxmod estimation method is recorded; complete credits/transfers and cross-vintage reconciliation are not established in this retained note | Report-body tax/transfer formula unverified |
| Housing-cost treatment | Separate subtraction of primary-property costs is indexed; no AHC measure selected | Housing-cost definition/treatment not mapped in the retained note; needs primary-source verification before an AHC candidate is claimed complete | Unverified in report body |
| Equivalisation | Separate operation; no equivalence scale selected | Adjustment for composition is recorded; exact scale/formula remains unverified in this retained note | Unverified in report body |
| Period | From year ended June 2025; preceding twelve months for each interview; tax-year alignment and corrected publication vintages remain explicit gates | Historical 1982–2016 coverage, latest HES 2015–16; interview-year cash resources | Landing page records HES 2017–18 and preceding twelve months; body-method verification remains open |
| Poltika coverage | Existing scoped WFF/AS and proposed tax/benefit slices cover only parts of the candidate; no complete statistical total exists | Existing components do not establish this historical definition or its period alignment | No coverage contract can be inferred from metadata alone |
| Uncovered components | IETC, ACC, broader income classes, complete tax/transfer treatment and household/period mappings remain uncovered or unreviewed | Unmapped components, exact housing/equivalence treatment and historical model/period coverage remain uncovered or unreviewed | All body-defined components/methods remain unverified; report metadata cannot fill them |

Claude must independently read the official sources and assess every field,
including the DI-4 mapping gaps and DI-5 extraction failure, before recommending
an official definition. The comparison does not harmonise vintages or silently
select one candidate. Pete's instruction to adopt one reviewed official
definition whole does not identify that final definition; D2 selection and
coverage decisions remain open. D3 adequacy/replacement measures and Q10's
income/period mapping remain separate gates.

## Verification limits and remaining gates

Final-head author checks cover unchanged research/review bytes, relative links,
programme-authority regression tests and whitespace. No calculator, monetary
benchmark, protected value or primary-source re-verification is claimed by
this mechanical preparation. Historical independent review covers its named
head/source delta only and cannot clear the current final-head gate.

Claude must perform independent source review of the exact published head,
record any discrepancies under the review doctrine, obtain the fresh reviewer
pass and green current CI, and keep D2/coverage and protected gates with Pete.
No review-queue row, source approval status or runtime component is changed.
