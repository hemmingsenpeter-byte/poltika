# Proposal: six WFF and AS boundary cases for the doctrine process, 12 October 2026

Author: Claude Code (Sonnet 5.5). Base: `origin/main` `cef0ed7`. Origin: the "Numeric gaps for the doctrine process"
table in `reviews/2026-10-11-wff-as-conformance-matrix.md`.

**Status: proposal only.** Nothing here is a protected expected value. No test, `spec_cases.yaml`, `benchmarks.yaml` or
golden file was added or changed. `doctrine/test-doctrine.md` prescribes no proposal format, so this file follows the
review-packet convention (`review_packets/README.md`): the reviewer re-derives each value from the sources before reading
the author's figure. Adding any value below to `spec_cases.yaml` is a protected-value change (Tier C, ADR-0020,
`PETE_QUEUE.md`) and needs Pete's approval after that independent derivation.

**Method.** Every value is derived by hand from the cited `specification.md` calculation sequence and the approved
`policy.yaml` parameters. The engine was not run and its output was not read or copied. Parameter values are quoted
from `policy.yaml` with the source ids recorded in each policy's `sources.yaml`. The dated MSD and legislation texts
themselves were not re-fetched (not available in this session); what is cited is what the repository records.

Outcome shown is the one component the case is about. Other components in the same WFF request are not asserted
(IWTC is `needs_review` on the real policy regardless, `specification.md` Task 10.2).

| # | Rule (matrix id) | Status |
| --- | --- | --- |
| 1 | WFF FTC abatement, sub-dollar edge (W-02) | Derivable from recorded sources, with one input caveat (Q1) |
| 2 | WFF Best Start abatement edge (W-09) | Derivable from recorded sources, with one input caveat (Q1) |
| 3 | WFF MFTC just below the prescribed amount (W-06) | Derivable from recorded sources, with one input caveat (Q1) |
| 4 | AS asset-imputation step edges (A-08) | Part derivable; the part-hundred edge is **source ambiguous, flag it** (Q2) |
| 5 | AS asset ceiling for couple or dependent children (A-09) | Derivable from recorded sources |
| 6 | AS r 19 final rounding at an integer (A-10) | Derivable from recorded sources |

## Case 1: FTC abatement just under the first complete dollar (W-02)

Inputs: single claimant, one qualifying child (whole year, all gates `verified`, as in
`half_cent_precision_exact_decimal_result`), modelled date 2026-06-01, policy 0.1.0.
Family scheme income: (a) 44,900.99; (b) 44,901.99.

Sources: `family_tax_credit_eldest_child` 7,921 (`wff-tax-credit-order-2025`, cl 4; ITA s MD 3(4)(a));
`family_tax_credit_abatement_threshold` 44,900 and `_rate` 0.275 (`wff-budget-measures-2025`, s 7; ITA s MD 13(3)(a)(i)).
Specification: "Scoped full-year calculation sequence" step 2 (`specification.md` 240-243):
abatement = `0.275 * floor(max(0, income - 44900))`; line 296: the complete-dollar rule applies to the income excess, not
the credit; no cent rounding in the core.

Derivation:
- (a) excess = 44,900.99 - 44,900 = 0.99; complete dollars = floor(0.99) = 0; abatement = 0.275 x 0 = 0;
  FTC = 7,921 - 0 = **7921**.
- (b) excess = 1.99; complete dollars = 1; abatement = 0.275; FTC = 7,921 - 0.275 = **7920.725**.

Status: derivable from recorded sources. Existing cases cover 44,900 and 44,901 only.

## Case 2: Best Start abatement at and just above $79,000 (W-09)

Inputs: as `best_start_supported_cohort_with_abatement` (one child in the supported cohort, all gates `verified`),
income: (a) 79,001; (b) 79,000.99.

Sources: `best_start_annual_amount` 4,041 (`wff-tax-credit-order-2025`, cl 6; ITA s MG 2);
`best_start_abatement_threshold` 79,000 and `_rate` 0.21 (`wff-income-tax-act`, s MG 3). Specification step 5
(lines 279-281): reduce by 21 cents per complete dollar of income over $79,000, zero floor.

Derivation:
- (a) excess = 1; abatement = 0.21 x 1 = 0.21; Best Start = 4,041 - 0.21 = **4040.79**.
- (b) excess = 0.99; complete dollars = 0; abatement 0; Best Start = **4041**.

Status: derivable from recorded sources. The matrix notes 79,000 is already tested and 79,001 is in no test.

## Case 3: MFTC just below the prescribed amount (W-06)

Inputs: single claimant, 52 verified full-time-earner weeks, ME 3 attestation true, family scheme income 30,000;
net family scheme income: (a) 36,603; (b) 36,603.99.

Sources: `minimum_family_prescribed_amount` 36,604 (`wff-tax-credit-order-2025`, cl 5; ITA s ME 1(3)(a)).
Specification step 4 (Scoped full-year calculation sequence): the all-52-week amount is the positive difference between 36,604 and net
income; at or above gives no top-up; no rounding is introduced in the calculation core (the paragraph after step 5).

Derivation: (a) 36,604 - 36,603 = **1**. (b) 36,604 - 36,603.99 = **0.01**.

Status: derivable from recorded sources. Only the "zero at the prescribed amount" case exists today.

## Case 4: AS asset-income imputation step edges (A-08)

Inputs (all): non-beneficiary, single, no dependent children, Area 1, rent or board, `ordinary_rate_status` verified,
policy 0.1.1, weekly accommodation cost 300, weekly income 700, assets as listed.
Parameters: entry threshold 93 (`as-msd-rates-2026`, Single 16+); cap 165 (cl 3(a)); income level 693
(`as-msd-income-2026`); subsidy 0.7; reduction 0.25; imputation above 2,700, $1 per $100 step (`as-social-security-act`,
s 423(3)(b)); r 15(1)(b) ceiling 8,100 not exceeded. `specification.md` steps 4-6 and DEC-001 (the income excess is not
floored; here it is a whole number, so DEC-001 does not affect the result).

Cost-based amount: 0.7 x (300 - 93) = 144.90 (below the cap).

| Assets | Complete $100 steps over 2,700 | Chargeable income | Excess over 693 | Reduction 25% | Pre-round | r 19 result |
| --- | --- | --- | --- | --- | --- | --- |
| 2,700 | 0 | 700 | 7 | 1.75 | 143.15 | **144** |
| 2,799.99 | 0 (see Q2) | 700 | 7 | 1.75 | 143.15 | **144** |
| 2,800 | 1 | 701 | 8 | 2.00 | 142.90 | **143** |
| 8,100 (ceiling, met) | 54 | 754 | 61 | 15.25 | 129.65 | **130** |

Couple-with-children variant: non-beneficiary, ordinary couple, 1 dependent child (eldest under 16 verified), Area 1,
cost 401, weekly income 1,121, threshold 205, income level 1,117, cap 305, imputation above 5,400 (s 423(3)(a)), subsidy
0.7: cost-based amount 0.7 x 196 = 137.20.

| Assets | Steps over 5,400 | Chargeable income | Excess over 1,117 | Reduction | Pre-round | r 19 result |
| --- | --- | --- | --- | --- | --- | --- |
| 5,400 | 0 | 1,121 | 4 | 1.00 | 136.20 | **137** |
| 5,499.99 | 0 (see Q2) | 1,121 | 4 | 1.00 | 136.20 | **137** |
| 5,500 | 1 | 1,122 | 5 | 1.25 | 135.95 | **136** |

Status: the rows at exactly one full step over the threshold (2,800 and 5,500) and at the threshold (2,700, 5,400)
are derivable from recorded sources. The part-hundred rows (2,799.99 and 5,499.99) and the ceiling row depend on
reading s 423(3) "every $100 of cash assets over" as complete steps. `specification.md` 124-140 says that is "an
inference from the wording, not a quotation of an explicit 'complete hundreds' rule" and asks a fresh-context reviewer
to re-read s 423(3) before it is treated as settled; `sources.yaml` `task_22_check` (lines 28-41) says the same, and
`task_24_1_independent_check` confirmed the amounts ($5,400, $2,700, $100, $1) but not the
part-hundred reading. **Source ambiguous: flag it.** Do not promote the part-hundred rows until that re-read is
recorded.

## Case 5: AS asset ceiling for a couple or a household with dependent children (A-09)

Inputs: Jobseeker Support, ordinary couple, 1 dependent child (eldest under 16 verified), Area 1, rent or board,
`ordinary_rate_status` verified, weekly cost 400, assets: (a) 16,200; (b) 16,200.01. Jobseeker has no asset-income
imputation (see `asset_ceiling_exactly_met_is_eligible`'s derivation, same reasoning).

Sources: `asset_ceiling_relationship_or_dependent_children` 16,200 (`as-social-security-regulations`, r 15(1)(a));
Jobseeker couple-with-children threshold 205 (`as-msd-jobseeker-rates-2026`); Area 1 cap with dependent children 305
(Sched 4 Pt 7 cl 1(a)). `specification.md` 232-235: assets exactly at the ceiling pass (r 15(1) "must not exceed").

Derivation: (a) 16,200 does not exceed 16,200. 0.7 x (400 - 205) = 136.50, under the cap; rounded up: **137**.
(b) exceeds the ceiling: outcome **unsupported** (not zero).

Status: derivable from recorded sources. Mirrors the existing single-person cases at 8,100 and 8,100.01.

## Case 6: AS r 19 rounding at an integer and just above (A-10)

Inputs: Jobseeker Support, single, no dependent children, Area 1, assets 1,000, weekly cost: (a) 103; (b) 103.01.

Sources: Jobseeker single threshold 93 (`as-msd-jobseeker-rates-2026`); subsidy 0.7; cap 165; r 19 "rounded up to the
complete dollar" (`as-social-security-regulations`; DEC-001 records it governs only the final amount;
`specification.md` step 6).

Derivation: (a) 0.7 x (103 - 93) = 7.00, already whole: **7**. (b) 0.7 x 10.01 = 7.007: rounded up: **8**.

Status: derivable from recorded sources. Existing cases cover 87.5 and 74.90 only.

## Questions for Pete

- **Q1 (cases 1-3, the sub-dollar rows):** the repository does not state whether a verified income or net income carries
  cents. Cases 1-3 use cents (44,900.99, 79,000.99, 36,603.99) to test the complete-dollar rule at its edge. If inputs
  are whole dollars by contract, drop the sub-dollar rows. `policy_specs/working_for_families/policy.yaml` defines
  `verified_amount` with no precision, and the Act's complete-dollar text is recorded only as a summary in
  `sources.yaml` (`wff-income-tax-act` `calculation_audit`, line 16, with `verification_status: full_text_review_pending`).
- **Q2 (case 4):** whether s 423(3) counts only complete $100 steps (the spec's inference). Needs an independent re-read
  of the Act as the spec itself requests.

## Not covered

No source is missing for cases 1-3, 5, 6 beyond the status noted. No Act or MSD page was re-fetched here, so each
parameter is as recorded and approved in `policy.yaml`; the doctrine's independent derivation step has not yet been done.
