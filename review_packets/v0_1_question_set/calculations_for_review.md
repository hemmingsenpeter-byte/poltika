# Poltika v0.1 question-set calculations for review

**Run date:** 26 September 2026  
**Code:** commit `27aa811`, Poltika `0.1.0`  
**Policy periods:** WFF `0.1.0`, lookup 2026-06-01; AS `0.1.1`, week
2026-06-01 to 2026-06-08 (end exclusive)  
**Executable evidence:** `run_current_70.py` and `current_70_results.json`

These are model outputs, not entitlement determinations. “Verified” facts are
caller assertions. A question that omits a required fact does not receive an
invented value. For Q31-Q33 and Q54-Q57, a separately labelled **g2 worked
assumption** is supplied: partnered non-beneficiary household, two children,
Area 1, $2,000 assets, $1,346 weekly income, and $600 weekly qualifying rent.

The deployed WFF policy deliberately leaves `in_work_base` at
`review_status: needs_review`. Therefore any reached IWTC is `needs_review`,
and total WFF is unavailable even when FTC, MFTC and Best Start calculate.

## Working for Families

1. **$7,893.500 FTC.** Gross $7,921; complete-dollar excess
   `45,000 - 44,900 = 100`; abatement `100 x 0.275 = 27.500`; final
   `7,921 - 27.500 = 7,893.500`.

2. **$7,893.225 FTC; $0.275 less than Q1.** Excess $101; abatement
   `$27.775`; final `$7,921 - $27.775 = $7,893.225`.

3. **$14,347.500 FTC.** Gross `7,921 + 6,454 = 14,375`; abatement
   `$27.500`; final `$14,347.500`.

4. **$20,801.500 FTC.** Gross `7,921 + 2 x 6,454 = 20,829`; abatement
   `$27.500`; final `$20,801.500`.

5. **Gross $14,375; abatement $0; final $14,375.000.** Income exactly at
   $44,900 has no positive excess.

6. **Reduction $0.275; final $14,374.725.** One complete dollar above the
   threshold is multiplied by 0.275.

7. **$14,375.000 FTC.** One dollar below the threshold has no abatement.

8. **Gross $14,375; abatement $2,750; final $11,625.000.** The excess is
   $10,000 and `10,000 x 0.275 = 2,750`.

9. **$0 FTC.** The model floors FTC at zero. The executable example uses
   $500,000 income: gross $14,375 and calculated abatement $125,152.50.

10. **No unique age-boundary calculation.** v0.1 accepts a caller assertion
    that a child qualifies for the whole year, not age or date of birth. If
    both children remain qualifying, changing age alone changes FTC by $0.
    If the boundary changes whole-year qualification, this branch cannot
    calculate it from age.

11. **No rate is selected from the birthday.** The API has no birthday
    input. A mid-year qualification transition is outside the ordinary
    whole-year branch and must not be inferred.

12. **Same boundary as Q11.** If whole-year qualification is independently
    verified, the ordinary eldest/additional-child rate applies today. If it
    is not verified, the result is `needs_review`.

13. **Conditional answer.** Date of birth itself is not an FTC input. If the
    missing date means whole-year qualification cannot be verified, every WFF
    component is `needs_review` (the modelled result). If that qualification
    is verified from other evidence, FTC can still calculate.

14. **FTC `needs_review`, value null.** An unverified second child's
    whole-year qualification gates the household; Poltika does not silently
    count one child or two.

15. **$11,597.500 FTC.** Combined verified income is `$55,000 + $0`.
    Gross FTC is $14,375; abatement is
    `(55,000 - 44,900) x 0.275 = 2,777.500`; final $11,597.500.

16. **FTC `needs_review`, value null.** A partnered claimant's missing
    partner income is not treated as zero.

17. **No unique amount.** The question supplies no income figures and MFTC
    needs attested ME 3 net family scheme income, not merely known gross
    incomes. Formula in the supported branch is
    `max(0, 36,604 - verified net family scheme income)`. The executable
    representative with gross $30,000 + $0 but no attested net amount returns
    MFTC `needs_review`.

18. **MFTC `needs_review`, value null.** Partner income is missing.

19. **MFTC `needs_review`, value null.** The run supplies attested net income
    of $30,000 but leaves full-time-earner weeks unknown; Poltika refuses the
    otherwise arithmetical $6,604 top-up.

20. **No.** Failure of the MFTC branch does not block FTC. In the modelled
    case FTC is $7,921.000 while MFTC is `unsupported`.

21. **Best Start `unsupported`, value null.** A child born in 2026 is outside
    v0.1's narrow calculable birth cohort; v0.1 does not prorate this case.

22. **Best Start `unsupported`, value null.** An in-year birth/eligible
    portion is explicitly outside the v0.1 branch.

23. **Best Start `needs_review`, value null.** Unknown date/cohort is not
    treated as no entitlement.

24. **Best Start `needs_review`, value null.** In the executable case the
    mandatory no-disqualifying-payment fact is unknown.

25. **No unique answer from the question alone.** A representative supported
    case at $30,000 with attested net income returns FTC $7,921.000, MFTC
    $6,604 and Best Start $4,041.00. IWTC remains `needs_review`, so total WFF
    is null rather than the partial sum $18,566.

26. **Keep the component results; total WFF is null.** The representative
    run returns FTC $7,921.000 and Best Start $4,041.00, MFTC
    `needs_review`, IWTC `needs_review`, and no total.

27. **$12,500 alone is insufficient to derive an exact change.** Adding an
    ordinary additional qualifying child increases gross FTC by $6,454, but
    final FTC depends on existing abatement and its carry into IWTC. IWTC adds
    $780 only when the new child is beyond the first three. MFTC has no direct
    child-count increment. Best Start changes only if the new child is in its
    supported cohort and passes its component facts.

28. **FTC `needs_review`; no number.** The engine accepts one canonical
    verified income, not competing source records. The conflict must be
    resolved upstream and neither $60,000 nor $75,000 may be preferred
    silently.

29. **FTC `needs_review`; no number.** Conflicting child counts cannot be
    turned into a canonical child list without review.

30. **Every WFF component is `needs_review`, value null.** The executable
    request uses 2025-06-01, outside `[2026-04-01, 2027-04-01)`.

## Accommodation Supplement

31. **Underdetermined as written.** Rent alone does not select claimant,
    household, area, income or asset rows. Under the g2 assumption, AS is
    **$220/week**: `0.7 x (600 - 205) = 276.50`; income reduction
    `0.25 x (1,346 - 1,117) = 57.25`; `ceil(276.50 - 57.25) = 220`.

32. **Under g2, still $220/week; exact change $0.** At $601 rent the
    pre-round amount is `0.7 x 396 - 57.25 = 219.95`, rounded up to $220.

33. **Under g2, $219/week; change from Q31 is -$1.** At $599 rent the
    pre-round amount is `0.7 x 394 - 57.25 = 218.55`, rounded up to $219.

34. **$0/week.** At the applicable entry threshold the positive excess is
    zero. The executable single-Jobseeker Area 1 row uses $93.

35. **$1/week; exact increase $1.** One dollar above the threshold produces
    `0.7 x 1 = 0.70`, rounded up to $1.

36. **The applicable maximum, before any non-beneficiary income reduction.**
    A single childless Jobseeker in Area 1 at $1,000 rent returns $165/week.

37. **No increase once the same cap binds.** Increasing that example's rent
    from $1,000 to $1,100 leaves AS at $165/week.

38. **No unique pair without the two areas and household category.** At high
    rent with no income reduction, the model returns for a childless single:
    Area 1/2/3/4 = `$165/$105/$80/$70`; for a couple with two children:
    `$305/$220/$160/$120`.

39. **Area 1 minus Area 2 maximum:** $85 for the with-dependent-children
    category (`305 - 220`), $80 for a childless couple or sole parent with
    one child (`235 - 155`), and $60 for a childless single (`165 - 105`).

40. **AS `needs_review`, value null.** No statutory area is supplied; the
    model never defaults to Area 4.

41. **AS `needs_review`, value null.** An address is not itself an Area 1-4
    classification.

42. **AS `needs_review`, value null.** The model accepts one canonical area;
    conflicting authoritative classifications must remain unresolved
    upstream.

43. **AS `needs_review`, value null.** v0.1 needs the already-resolved weekly
    qualifying accommodation cost. It cannot assume the whole $700 qualifies.

44. **$650/week enters the formula** (`700 - 50`). Under the g2 assumptions,
    that input yields $248/week, but the question does not supply enough facts
    for a universal final AS amount.

45. **AS `unsupported`, value null.** Homeowner costs under Schedule 4 Part 7
    clauses 4-6 are outside v0.1's rent/board-only branch; no costs are
    silently selected.

46. **AS `unsupported`, value null.** The homeowner branch remains outside
    v0.1 even if a mortgage payment is supplied.

47. **Not eligible in this branch; AS `unsupported`, value null.** Cash assets
    meeting the applicable ceiling fail the asset requirement. The modelled
    childless-single ceiling is $8,100; the other ceiling is $16,200.

48. **Same exclusion as Q47.** One dollar above the ceiling is
    `unsupported`, not a calculated zero.

49. **The asset gate passes one dollar below the ceiling.** Final AS then
    depends on the remaining inputs. The executable childless-single example
    at $8,099 assets calculates $110/week.

50. **AS `needs_review`, value null.** Unknown assets are not zero.

51. **AS `needs_review`, value null.** The AS input is relevant combined cash
    assets; missing Partner B assets means that input is unverified.

52. **No.** Verified $0 assets permits calculation (the representative result
    is $110/week); unknown assets return `needs_review`.

## Interaction And Changes

53. **No income coupling.** Poltika keeps WFF annual and AS weekly. IRD-paid
    WFF is excluded from AS chargeable income in this contract, and AS is not
    added to WFF family scheme income. Each policy uses its own supplied
    income measure.

54. **Underdetermined generally.** Beneficiaries have no separate AS income
    test in this branch; a non-beneficiary below the threshold may also see no
    change. Under g2, income $1 higher changes AS from $220 to $219 because the
    extra $0.25 reduction crosses the final whole-dollar ceiling: **-$1**.

55. **Under g2, -$25/week:** $1,346 income gives $220 AS and $1,446 gives
    $195. The unrounded reduction rises by `100 x 0.25 = 25`. Other claimant
    branches or a zero floor can differ.

56. **Under g2, +$28/week:** rent $600 gives $220; rent $700 gives $248. The
    cost-based amount reaches the $305 Area 1 maximum before the $57.25 income
    reduction, so the household hits the maximum calculation stage.

57. **Underdetermined without origin/destination and category.** Under g2,
    Area 1 to Area 2 changes AS from $220 to $163: **-$57/week**.

58. **AS `needs_review`, value null.** City alone is not enough to assert the
    statutory area.

59. **Yes, policy components remain separate.** In the combined model run,
    missing AS area makes AS `needs_review`, while WFF still returns FTC
    $7,472.500, MFTC $0 and Best Start $0; IWTC retains its independent live
    parameter `needs_review` state.

60. **Yes.** The executable run returns all WFF components `needs_review` for
    unresolved child qualification while AS independently calculates
    $220/week. There is no shared child-count contradiction.

61. **Return FTC $X, Best Start $Y and AS $Z as component values; return MFTC
    `needs_review`; do not publish a WFF total or a combined WFF+AS total.**
    The representative evidence does exactly this (and IWTC is also
    `needs_review`).

62. **Do not assume eligibility.** Unknown bundled household eligibility
    makes every affected WFF component and AS `needs_review`, value null.

63. **Current v0.1 returns `unsupported`, value null, not $0.** An explicitly
    failed mandatory eligibility condition is a known outside-domain case for
    the affected payment.

## Validation And Assurance

64. **Fixed 26 September 2026: the request is now rejected (HTTP 422,
    "Extra inputs are not permitted").** Original observation, kept for the
    record: The API has no date-of-birth field and Pydantic ignores
    the extra `date_of_birth: 2027-01-01`; with `qualifies_whole_year` also
    asserted `verified`, it returns HTTP 200 and FTC $7,893.500. This is a
    silent-input boundary worth classifying before relying on raw birth-date
    submissions.

65. **Rejected with HTTP 422.** `weekly_accommodation_costs` must be at least
    zero; no AS calculation runs.

66. **Rejected with HTTP 422.** “six hundred dollars” is not a valid decimal.

67. **No.** A numeric result without attributable parameter provenance must
    fail assurance; the provenance report requires each used parameter's
    source identifier and locator.

68. **No.** $8,742 and $8,724 are not explanation-equivalent. The explanation
    must use the recorded calculation value.

69. **No.** “Approximately $150” cannot replace the authoritative calculated
    $147/week. It may only be clearly labelled non-authoritative presentation
    alongside the exact recorded value.

70. **One distinct result.** The runner executed the same WFF and AS scenarios
    10,000 times against the same loaded parameters and obtained
    `distinct_results: 1`.

## Review Flags

- **Q64:** classified as a CODE_ERROR and fixed. Every API request model now
  forbids unknown fields (HTTP 422), and `current_70_results.json` was
  regenerated. See `calculations.md`, "Disposition".
- **Q10-Q13, Q21-Q24:** v0.1 models whole-year qualification and a narrow Best
  Start cohort as asserted facts; it does not derive them from dates.
- **Q17, Q25, Q27-Q29, Q31-Q33, Q38, Q43-Q44, Q49, Q54-Q57:** the question as
  written lacks facts needed for one universal number. Worked assumptions are
  labelled and must not be mistaken for facts supplied by the question.
- **All WFF totals:** the live IWTC base remains `needs_review`; partial
  component sums are not total WFF.
