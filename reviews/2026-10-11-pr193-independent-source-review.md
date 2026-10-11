# PR #193 independent primary-source review: income-tax salary/wage specification

Reviewer: Claude Code (Sonnet 5.5), independent of the Codex author. Date: 11 October 2026 NZDT.
Reviewed content: branch `origin/codex/income-tax-spec-20261008` at SHA
`2cc00c89b3abbeee80df2d9257eaa799dee65b71` (specification.md, sources.yaml, DEC-001..003, scope note,
source recheck, preflight packet). Base for this record: main `b19e764`.
Method: expected content was derived from the primary sources first (legislation.govt.nz fetched with
curl, retrieved 11 Oct 2026, text extracted and read; IRD pages via WebFetch; IRD IR3G PDF text-extracted),
then compared with the spec. No model memory is used as authority for any number. This review records
verdicts only; it edits no spec, source or value, and is not Pete's acceptance.
Not an approval: the review queue row stays open until GPT/Codex and Pete act.

## Per-claim verdicts

| Claim in spec | Verdict | Source locator (retrieved 2026-10-11) |
| --- | --- | --- |
| Table 1 rows: 0.105 to $15,600; 0.175 to $53,500; 0.300 to $78,100; 0.330 to $180,000; 0.390 above | Matches | ITA 2007 (version 2026-09-04) Sch 1 Pt A cl 1 Table 1; same table in Taxation (Budget Measures) Act 2024 s 37(1) |
| Cl 1 basic rate = tax under table 1 divided by taxable income (per-dollar, not top-bracket) | Matches | ITA Sch 1 Pt A cl 1(a),(b) |
| BC 6(1) liability = taxable income x basic rate; BC 6(2) zero or negative gives zero | Matches | ITA BC 6 |
| 2024 Act Part 4 in force 1 April 2025; table applies 2025-26 and later income years | Matches | 2024 No 19 s 2(5); s 37(4) ("Subsections (1), (2), and (3) apply for the 2025-26 and later income years") |
| ITA records the replacement | Matches | ITA footnote: "Schedule 1 part A table 1: replaced, on 1 April 2025, by section 37(1) ... of the Taxation (Budget Measures) Act 2024" |
| BB 1: income tax imposed at rates fixed by an annual taxing Act | Matches | ITA BB 1 |
| TAA s 92A permits Commissioner basic-rate assessment before the annual Act, adjusted if annual rates differ | Matches | TAA 1994 s 92A(1),(2) |
| Tax year = 1 April to 31 March, identified by two years | Matches | ITA YE 1(2); YE 1(4) standard balance date |
| Salary or wages are employment income | Matches | ITA CE 1(1)(a) |
| Assessable income excludes exempt, excluded and non-residents' foreign-sourced income | Matches | ITA BD 1(5)(a)-(c) |
| BC 1/BC 8 split between liability calculation and credits/terminal tax | Matches in structure (BC 1 text read; BC 8 not read in full) | ITA BC 1, BC 8 |
| IRD rates page shows the same five rates "From 1 April 2025" | Matches. Page has no 2026-27 rates. | IRD "Tax rates for individuals" |
| Annual rates for 2025-26 set by Annual Rates Act 2026 s 3 | Matches (s 3 applies Sch 1 basic rates to 2025-26) | 2026 No 8 s 3 |
| No enacted annual taxing Act exists for 2026-27 in the sources checked | Consistent: only Bill 344-1 (introduction version, 10 Sep 2026) appears. I did not establish its later stage. | Bill 2026 No 344-1 cl 3; ITA version 2026-09-04 still shows the 2025-26 table |
| Bill 344-1 treated as proposed law, not enacted | Correct treatment. No unenacted provision is treated as enacted anywhere I read. | Bill 344-1, introduction version |
| Fractional dollars, intermediate precision, rounding, ties unresolved | Not verifiable either way: I found no governing rule. Searching the TAA text for "nearest dollar", "whole dollar", "nearest cent" gave no hit. The ITA hits concern unrelated provisions (depreciation, instalment uplift, GST percentage). Cl 1 speaks of "number of dollars" in taxable income but does not say how a cent is treated. | TAA 1994 and ITA 2007 text searches |
| YD 1, BC 2-5, DA 2, DA 3, CF 1, CE 1BA scope claims | Headings and existence confirmed; clause-level content not individually read. Not verifiable here beyond that. | ITA |
| IR3G worksheet row ($78,101 / .33 / $15,650.50), DEC-003 | Source observation verified: printed p 43, my own extraction shows exactly those cells, and the neighbouring rows use $53,500 and $180,000 as A. Arithmetic verified: 1,638 + 6,632.50 + 7,380 = 15,650.50 = tax on the first $78,100; so A = $78,101 understates by $0.33. Guide covers 2025-26. | IRD IR3G 2026 guide, PDF p 43 (file page numbering) |

## Findings

| Sev | Class | Finding |
| --- | --- | --- |
| P2 | Authority gap (spec acknowledges) | No enacted 2026-27 annual taxing Act exists in the sources I could see. Table values are enacted law for 2025-26 and later via the 2024 Act s 37, but BB 1 requires an annual taxing Act each year. Bill 344-1 cl 3 would impose 2026-27 tax "at the basic rates specified in Schedule 1", and the explanatory note says the rates stay "at the rates currently specified". Both are proposed, correctly not relied on as enacted. Blocks any numeric `calculated` result until Pete decides (Q16). |
| P2 | MISSING_SOURCE | Precision and rounding have no source (DEC-002). The spec's `needs_review` handling is correct. Blocks fixtures and implementation of fractional-dollar behaviour. |
| P3 | Source conflict, low impact | DEC-003: the IR3G worksheet cell A = $78,101 conflicts with the statutory per-dollar table by $0.33. Rank-3 guidance yields to rank-1 statute. The spec rightly refuses to use it as a benchmark. DEC-003's "$15,650.50 equals the first $78,100" arithmetic is correct. |
| P3 | Completeness | The spec does not quote Bill 344-1 cl 3, the most on-point proposed provision, though sources.yaml records the Bill. Suggest naming it (and its "introduction" status) in DEC-001 as the specific proposed 2026-27 rate clause. Content only, no value changes. |
| P3 | Scope note | The spec says CE 1 / CE 1BA amendments in the 2026 annual rates legislation were not assessed. The Bill's list shows s 7 amending CE 1BA only (heading read); CE 1(1)(a) did not appear amended in the headings, not read clause by clause. |
| none | | No mismatch of any rate, threshold, date or section number found. No unenacted provision is treated as enacted. |

## Questions that need Pete (exact wording)

1. Q16: Until the 2026-27 annual taxing Act is enacted, may Poltika return the basic annual tax as
   `calculated` at the current Schedule 1 rates, labelled "annual rates Act pending (Bill 344-1 cl 3 proposes
   the same rates)", or must it stay `needs_review` until Royal assent? (s 92A authorises the Commissioner,
   not Poltika, so applying it is your decision.)
2. Q17: With no source for fractions of a dollar, which convention do you adopt as a labelled Assumption:
   exact arithmetic to the cent with a stated final rounding rule, or whole-dollar-only inputs with
   anything else `unsupported`? (Name rounding mode and tie rule if the first.)
3. Q18: Confirm the statute-derived bands prevail over the IR3G worksheet cell and the guide is excluded as
   a benchmark, or ask IRD for clarification first. (My arithmetic supports the first.)

## Is Task 7 unblocked for the basic 2026-27 annual salary/wage slice?

Specification-level: yes in substance. Nothing in the source rules or the table contradicts it, and it
treats gates correctly. Implementation: not yet for authoritative numbers. Q16 and Q17 block the values,
cases and engine PR. Work that does not emit numbers (input contract, outcome gating returning
`needs_review`, tests of gating) could start, but I did not verify that the repository permits that
ahead of the gates.

## Limits of this review

Legislation was read from the HTML versions named above, extracted programmatically. YD 1, DA 2/3 and
BC 2-5 were not read clause by clause. Bill 344-1 progress after introduction was not established.
IRD pages carry older "last updated" labels (sources.yaml) and are cross-checks only.
