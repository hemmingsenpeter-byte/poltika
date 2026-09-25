# v0.1 question set: Poltika's answers, for GPT/Codex review

- **Run by:** Claude Code, 26 September 2026, at Pete's request, on `main` after PR #73.
- **Numbers:** every figure below comes from [`results.json`](results.json), which is written by [`run_questions.py`](run_questions.py) running the real engines, the API and the approved policy files. Regenerate with:

  ```sh
  uv run --extra dev python review_packets/v0_1_question_set/run_questions.py
  ```

- **For Codex:** please check each answer against the specifications, and check that the proposed findings (end of file) are classified correctly.

## Read this first: what Poltika v0.1 can answer

- **Modelled:** Working for Families (WFF) for the 2026-27 tax year (FTC, IWTC, MFTC, Best Start), and the Accommodation Supplement.
- **Not modelled: income tax.** There is no tax schedule, source, specification or calculator for it in the repository. Under CLAUDE.md ("never use model memory as authority for statutory rates, thresholds"), I did **not** compute any income tax from memory. Every income tax figure below is **not answerable by Poltika v0.1**, and the parts that depend on it (after-tax income, disposable income, EMTR) are too.
- **IWTC is always `needs_review`:** the 2026-27 `in_work_base` is gated (Task 26b).
- **MFTC** needs the ME 3 *net* family scheme income. That is income after tax, so the caller has to supply and attest it; Poltika can't derive it without a tax module. None of these questions gives a net income, so MFTC is `needs_review` throughout.
- **Standard facts for the WFF runs:** an ordinary in-work, non-beneficiary household, every non-income fact verified, modelled date 1 June 2026. Each child is verified as qualifying for the whole year and outside Best Start unless stated otherwise.
- **Partnered incomes:** where only a combined income is given, it is split between the partners. The WFF result depends only on the combined amount.

## A. Income tax (Q1-Q13, Q25-Q27)

| Q | Answer |
| --- | --- |
| 1-10 (tax at $40,000, $50,000, $15,600/$15,601, $53,500/$53,501, $78,100/$78,101, $180,000/$180,001) | **Not modelled.** Poltika has no income tax schedule. No figure. |
| 11 (Jack, Jill and James) | Not modelled. |
| 12 (Maia) | Gross income $65,000 is the input. Income tax and after-tax income are not modelled. |
| 13 (Ben and Sophie) | Combined gross is $120,000. Tax and after-tax income are not modelled. With no children the household is outside WFF (see Q30). |
| 25-27 ($0, $1, $10,000,000) | Not modelled. |

## B. Working for Families calculations

| Q | Inputs | Poltika result (annual) | Working |
| --- | --- | --- | --- |
| 14 | Aroha: sole parent, 1 child aged 8, income $45,000 | FTC **$7,893.50** calculated. IWTC needs_review, MFTC needs_review, Best Start $0 | Gross $7,921. Abatement 27.5% × $100 (complete dollars over $44,900) = $27.50. |
| 15 | Aroha at $45,001 | FTC **$7,893.225**. Change **−$0.275** | Income tax and disposable income are not modelled, so the only change Poltika can give is FTC. |
| 16 | Wiremu and Hana, $70,000, with 1, 2 and 3 children | FTC **$1,018.50 / $7,472.50 / $13,926.50** | Gross $7,921, $14,375 and $20,829, each less $6,902.50 (27.5% × $25,100). Each additional child adds **$6,454**. |
| 17 | An age boundary | One child, $65,000. Supported Best Start cohort: Best Start **$4,041.00**. Outside that cohort: Best Start **unsupported** (no value). FTC **$2,393.50** in both. | Poltika takes no date of birth. The caller asserts the child's Best Start cohort, and v0.1 calculates one cohort only: children born 1 April 2024 to 31 March 2025. |
| 18 | Sarah and Tom, $65,000, newborn born 1 April 2026 | FTC **$2,393.50**. Best Start **unsupported** | A 2026 birth is outside the one calculable cohort (specification step 5: later birth cohorts "require separate review"). No gross, abatement or final amount. |
| 19 | Q18 with the birth one day earlier (31 March 2026) | **No change**: Best Start is still unsupported | Both dates fall outside the calculable cohort. The boundaries Poltika can distinguish are cohort classifications that the caller asserts. |
| 20 | Couple, 1 child, A $30,000, B $0 verified | FTC **$7,921** (no abatement). MFTC **needs_review** | MFTC needs an attested ME 3 net income, and only gross income was given. |
| 21 | Q20 with B's income unknown | FTC **needs_review**, IWTC needs_review, MFTC **needs_review**, Best Start $0 | Partner income is unverified, so nothing that depends on combined income is calculated. It is never treated as $0. |
| 22 | James, $55,000, 2 children, partner income unknown | FTC, IWTC and MFTC **needs_review**. Best Start **$0** (verified outside entitlement) | Income tax is not modelled. Best Start is the only amount that can be determined. |
| 29 | Couple, 2 children, $60,000 + $30,000, then +$1 to A | FTC **$1,972.50 → $1,972.225 (−$0.275)** | Gross $14,375 − 27.5% × $45,100. Transfer-side marginal rate from FTC abatement: **27.5%**. Tax, disposable income and the full EMTR are not modelled. |
| 30 | $90,000, no children vs 2 children | No children: every WFF component **unsupported** (outside WFF). 2 children: FTC **$1,972.50** | Income tax is not modelled. The family entitlement difference Poltika can state is FTC $1,972.50 (with IWTC and MFTC unresolved). |
| 31 | $53,500 salary + $10,000 other taxable income | Total **$63,500**, if the caller verifies it as family scheme income. Tax not modelled | Poltika does not add incomes itself. Family scheme income is a caller-verified amount. |
| 32 | Additional income unknown | Tax not modelled. For WFF, an unverified income makes every income-dependent component **needs_review** | See Q21. |

## C. Unknown, missing and conflicting facts

| Q | Poltika result |
| --- | --- |
| 33 | One child's qualification (dependency) is unknown: **every WFF component needs_review**. |
| 34 | Three children with no ages or cohorts: **every WFF component needs_review**. |
| 35 | It's unknown whether the child lives with the parent (principal care, household eligibility): **every component needs_review**. |
| 36 | Partnered, no partner record: with no children, every component is **unsupported** (outside WFF). With one child (illustrative), FTC, IWTC and MFTC are **needs_review** and Best Start is $0. |
| 37 | Partner $0 verified, one child (illustrative): FTC **$6,518.50** calculated. **They should not match Q36, and they don't**: a verified $0 is evidence, while a missing partner record is not. With no children the two results do match, because the household is outside WFF before income matters. |
| 38 | **Can't be represented.** Poltika accepts one caller-asserted income, and choosing between sources is the caller's job. The contract rule is never to pick silently. Without a verified figure the outcome is needs_review (as in Q21). |
| 39 | **Can't be represented.** Poltika takes no date of birth. |
| 40 | Tax is not modelled. For WFF, the API rejects a request with no `modelled_date` (**422**, "Field required"). There is no default date. |
| 41 | Modelled date 1 June 2025, with no parameter set loaded: **every component needs_review** ("outside policy 'working_for_families''s reviewed reference_period [2026-04-01, 2027-04-01)"). |
| 42 | In-work eligibility unknown: IWTC **needs_review** ("in-work eligibility unverified"). FTC **$6,518.50** is still calculated, because the unknown fact doesn't affect it. |
| 55-57 | Full-time-earner weeks unknown (it affects MFTC only): FTC **$6,518.50** calculated, MFTC **needs_review**, Best Start $0. **The calculation is not refused.** The household result carries a separate outcome and reason for each component. |
| 58, 59 | A future or negative age **can't be represented**, because there is no date-of-birth or age input. Negative incomes are rejected (Q28). |
| 60 | Possible duplicate children **can't be detected.** The child list is taken as asserted. This is a limitation. |
| 64 | No household composition: **422**, `children` "Field required" (Task 34.3 F8). |
| 65 | If Policy B has an unresolved parameter, that component is needs_review with no value, so **no numerical difference** should be reported. There is no policy-comparison feature in v0.1 (what-if runs are v0.4). |
| 66 | **No.** Contradictory states are escalated to needs_review. Poltika never picks the larger entitlement (see the Task 28.3 shared-fact contract). |

## D. Parameters, dates and inputs

| Q | Poltika result |
| --- | --- |
| 23 | 31 March 2026: **every component needs_review** (no 2025-26 parameter set is loaded). 1 April 2026, $50,000, one child: FTC **$6,518.50**. v0.1 holds one rule set, so a before/after comparison needs the earlier year's parameters to be loaded first. |
| 24 | A required parameter covers 1 April to 30 June 2026 only (tested on a scratch copy): **every component needs_review** ("covers the requested 2026-05-15 but does not span the complete reference period ... a point-in-time match cannot verify a full-year rate"). There is no partial-year amount. |
| 28 | Income −$20,000: **422**, "Input should be greater than or equal to 0". |
| 61 | Income "sixty thousand dollars": **422**, "Input should be a valid decimal". |
| 62 | Rate stored as 27.5 instead of 0.275 (scratch copy): **the file loads and FTC silently becomes $0.** This is a defect; see finding QS-1. |
| 63 | A parameter with no end date (scratch copy) **loads and applies**. After an unloaded replacement it would keep applying the old value; see finding QS-2. |

## E. Thresholds, continuity, determinism

| Q | Poltika result |
| --- | --- |
| 43 | FTC at $44,900.00 and $44,900.01 is **$7,921.000 in both**. At $44,901.00 it is **$7,920.725**. Best Start at $79,000.00 and $79,000.01 is **$4,041.00 in both**, and $4,040.79 at $79,001. **A cent never changes the result.** Both abatements count complete dollars (MD 13(3), MG 3). |
| 44 | **Sweep:** $40,000 to $100,000 in $1 steps, 60,000 steps, with one supported-cohort child. **FTC:** each step is either 0 or −$0.275, except one −$0.175 step. The first change is at $44,901. **Best Start:** each step is either 0 or −$0.21, except one −$0.18 step. The first change is at $79,001. **The odd steps are where each credit reaches its zero floor**: $7,921 is not a whole multiple of $0.275, and $4,041 is not a whole multiple of $0.21, so the last dollar before zero removes less. **No discontinuity is unexplained.** (See QS-3 on how zero values are displayed.) |
| 45 | 10,000 identical runs gave **1 distinct output**. |

## F. Process and assurance questions (answered from doctrine and existing tests)

| Q | Answer |
| --- | --- |
| 46 | **No.** The frozen snapshot (`tests/regression/test_golden_result_snapshot.py`) compares exactly. A one-cent change from unrelated code is a regression to explain (`doctrine/test-doctrine.md`). |
| 47 | Statutory rates live in `policy.yaml`, not in code; the last literal was moved there in Task 34.3 F3. Editing a rate triggers the statutory-value guard warning, and the spec, benchmark and golden tests fail, so **CI goes red.** The guard can't block a merge (ADR-0007), so the rule is not to merge while Tests is red. |
| 48 | The household **exactly at** the threshold. The five-point boundary tests include it (`tests/acceptance/`). |
| 49 | **No.** `test_explanation_values_are_the_recorded_calculation_values` requires the report and the calculation to agree exactly. |
| 50 | **The engine's $5,360.** The LLM never calculates (`doctrine/llm_boundaries.md`), and there is no LLM layer in v0.1. |
| 51 | **Not automatically.** External engines are not policy authority (`doctrine/ip-doctrine.md`). A difference is investigated and classified under the review doctrine. |
| 52 | **No.** A different statutory period is a SOURCE_CONFLICT or scope explanation, not a Poltika failure. |
| 53 | **No.** The loader refuses a parameter whose `source_id` isn't in the catalogue (`_resolve_source_ids`), and the provenance report refuses unresolved ids. |
| 54 | **No, if the convention requires $8,250.00.** The test should fail until Poltika applies the statutory rounding. Note that v0.1 WFF values are annual entitlement *candidates* with no payment rounding (for example $7,893.225, Q15). The specification says they are not payment figures. |
| 67 | **It should not be accepted.** v0.1 checks each **parameter's** effective interval, but it does not check that a cited **provision** was in force for the period. See finding QS-4. |
| 68 | The protected-value process (`doctrine/test-doctrine.md`, ADR-0007): cited source, dated parameter change, visible guard warning, independent review, and a recorded acceptance before the golden fixture is refrozen. |
| 69 | **No.** The frozen snapshot fails, and each changed calculation must be explained and accepted. |
| 70 | **Yes.** Each component carries a trace: inputs read (with the caller as the asserting party), parameters (value, source id, locator, effective interval, review status), calculation and specification rules, decisions and artifact hashes, and a provenance report is built from it. Example for g2's FTC ($7,472.50): parameters `family_tax_credit_eldest_child` 7921, `family_tax_credit_additional_child` 6454, `family_tax_credit_abatement_threshold` 44900 and `family_tax_credit_abatement_rate` 0.275, each with its source and locator (see `results.json` Q70 and `docs/demo/v0_1/provenance_report.md`). |

## Proposed findings (for classification under the review doctrine)

- **QS-1 (proposed P2, CODE_ERROR / ARCHITECTURE_ISSUE): fraction parameters are not range-checked.**
  - **Failure:** a `value_type: fraction` stored as 27.5 instead of 0.275 loads, and FTC silently becomes $0 (Q62).
  - **Current mitigation:** the protected-path guard, plus the spec, benchmark and golden tests, which would catch this in the current files.
  - **Suggested fix:** the schema should reject a fraction outside [0, 1].
- **QS-2 (proposed P3, ARCHITECTURE_ISSUE): open-ended parameter intervals.**
  - **Failure:** `effective_to` is optional (Q63). A parameter without one applies indefinitely, including after a legislative replacement that hasn't been loaded.
  - **Current mitigation:** every current v0.1 value is closed at 1 April 2027. The module also checks coverage of its reference period.
  - **Suggested fix:** either require `effective_to` for statutory values, or treat open-ended values as needs_review beyond a recorded verification date.
- **QS-3 (proposed P3, CODE_ERROR, cosmetic): inconsistent decimal scale.**
  - **Failure:** WFF values are returned at a varying scale: `7921.000` for a positive FTC but `0` once it hits the zero floor, and `4041.00` for Best Start. The values are equal, but the text differs, which makes string comparison in reports and snapshots fragile.
  - **Suggested fix:** normalise the output scale for each component.
- **QS-4 (proposed P3, ARCHITECTURE_ISSUE): provision effectiveness is not verified.**
  - **Failure:** provenance checks parameter intervals and artifact hashes, but not whether a cited provision was in force for the period (Q67).
  - **Suggested fix:** record effective dates for provisions in `sources.yaml`, and check them in the provenance report.
- **Scope limits that are not defects:**
  - no income tax module (a future version);
  - no date-of-birth or age input: cohort and qualification are caller-asserted;
  - no multi-source income reconciliation;
  - no duplicate-child detection;
  - no policy comparison.
