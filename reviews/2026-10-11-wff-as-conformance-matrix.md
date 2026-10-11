# WFF and Accommodation Supplement conformance matrix (Phase C Task 12)

Author: Claude Code (Sonnet 5.5), 11 October 2026 NZDT. Base: main `b19e764`. Scope: every rule in the
calculation sequences and status rules of `policy_specs/working_for_families/specification.md` and
`policy_specs/accommodation_supplement/specification.md` mapped to the tests that exercise it. This is a test
inventory, not a policy review: it did not re-derive any statutory value, and no expected value was changed
(`doctrine/test-doctrine.md`; protected statutory values change only through its process).

Test classes: **Spec** = `policy_specs/*/spec_cases.yaml` run by `test_*_spec_cases.py` and unit tests;
**Benchmark** = `benchmarks.yaml` run by `test_*_benchmarks.py`; **Regression** = `tests/regression/`.
"New" = added by this change in `tests/unit/api/test_wff_as_conformance_api.py` (non-numeric only).
Existing-test names are abbreviated (the `test_` prefix is dropped). `W-` = WFF unit tests in
`tests/unit/engines/simulator/test_wff.py`, `A-` = `test_accommodation_supplement.py`,
`R-` = `test_as_rate_selectors.py`, `C-` = `tests/unit/scenarios/test_combined.py`.

## WFF matrix

| ID | Rule (spec section) | Tests | Status |
| --- | --- | --- | --- |
| W-01 | FTC eldest/additional child amounts (step 2) | W-additional_children_and_family_tax_credit_amounts; spec cases single_ordinary_low_income, single_two_children_no_abatement, single_four_children_base_beyond_three; benchmark ird_ftc_sarah_full_credit | Covered |
| W-02 | Abatement 0.275 on complete dollars of excess over the threshold (step 2) | W-abatement_excess_uses_complete_dollars_not_cents; W-half_cent_abatement_result_preserved_exactly; spec half_cent_precision_exact_decimal_result | Covered |
| W-03 | Abatement FTC first, remainder to IWTC; no negative credit (MD 2) | W-abatement_carries_from_family_credit_to_in_work_credit; W-in_work_credit_floors_at_zero...; W-zero_floor_keeps_the_components_decimal_scale; spec single_high_income_ftc_floors_to_zero; benchmark ird_ftc_iwtc_claire_laura_partnered_abatement_carryover | Covered |
| W-04 | IWTC maximum for 1-3 children plus per-child beyond three (step 3) | W-in_work_additional_child_beyond_three; benchmark ird_iwtc_jaimee_full_credit_beyond_three_children | Covered |
| W-05 | IWTC always `needs_review` on the real policy (in-work base gated, Task 10.2) | W-in_work_base_needs_review_propagates_from_loader; test_wff_api::calculate_returns_needs_review_without_a_collapsed_value; test_household_api (code PARAMETER_NEEDS_REVIEW); New: in_work_tax_credit_is_never_calculated_with_the_real_policy | Covered (API invariant now explicit) |
| W-06 | MFTC = positive difference between the prescribed amount and verified net income; zero at or above (step 4) | W-minimum_family_tax_credit_zero_at_or_above_prescribed_amount; spec mftc_zero_at_prescribed_amount; benchmarks ird_mftc_jeremy_salary_only, ird_mftc_casey_zero_over_income_limit | Covered |
| W-07 | Net income must be ME 3-attested; gross never substituted | W-unattested_net_income_is_needs_review_even_if_a_number_is_present; W-missing_net_family_scheme_income_is_needs_review_only_for_mftc; W-negative_net_family_scheme_income_rejected | Covered |
| W-08 | MFTC: 52 full-time-earner weeks; ME 2 exclusion unsupported | W-me2_employment_exclusion_unsupported_only_for_minimum_family_credit; W-mftc_excluded_full_time_earner_weeks_reason...; spec me2_employment_exclusion_unsupported_only_mftc | Covered |
| W-09 | Best Start: single cohort child, abatement over its threshold, zero floor (step 5) | W-best_start_single_cohort_child_with_abatement; W-best_start_no_cohort_child_is_a_real_calculated_zero; spec best_start_supported_cohort_with_abatement | Covered |
| W-10 | Best Start other/unknown cohort, multiple children, shared care, MC 6(c), MG 4 | W-multiple_best_start_cohort_children_unsupported; W-best_start_other_cohort_child_is_unsupported_not_zero; W-best_start_unknown_cohort_child_is_needs_review_not_zero; W-best_start_genuine_zero_requires_verified_outside_entitlement; W-best_start_shared_care_unsupported_only_for_best_start; W-mg4_...; W-mc6c_...; matching spec cases | Covered |
| W-11 | Family scheme income required; missing is `needs_review`, never zero (WFF-02) | W-missing_family_scheme_income_is_needs_review_not_zero; W-missing_income_propagates_to_in_work_credit_via_md2_ordering; New: in_work_tax_credit_is_never_calculated... (income None variant) | Covered |
| W-12 | Partnered: combined income, partner income required, individual-or-sum caveat | W-partnered_combined_income_used_for_abatement; W-partnered_missing_partner_income_is_needs_review_not_a_number (and for Best Start); W-single_claimant_with_partner_amount_rejected; spec partnered_* ; benchmark ird_ftc_rahui_partnered_combined_income_not_individually_verified | Covered |
| W-13 | Unknown partner status is `needs_review` for FTC/IWTC/MFTC | W-unknown_partner_status_is_needs_review_even_with_a_single_income_figure; W-unknown_partner_status_is_needs_review_for_minimum_family_tax_credit_too; spec unknown_partner_status_blocks_ftc_iwtc_and_mftc | Covered |
| W-14 | Household eligibility excluded is `unsupported`; unknown is `needs_review` | W-household_eligibility_excluded_is_unsupported_for_all_components; W-household_eligibility_unknown_is_needs_review; spec cases of both names | Covered |
| W-15 | Part-year / child not qualifying the whole year is `unsupported` (supported domain) | W-child_not_qualifying_whole_year_is_unsupported_for_whole_household; benchmark ird_faraj_in_year_birth_fails_whole_year_domain; New: part_year_child_makes_every_wff_component_unsupported (API level) | Covered |
| W-16 | Relationship change, shared-care change of caregiver: out of scope (supported domain) | No input field can express a relationship change; the only gate is the caller's `household_eligibility` and the whole-year child flag (W-15). Best Start shared care is tested (W-10). | Partial: no representable fact; documented, not testable without a new input |
| W-17 | MC 6(a)/(b)/(c) per-component exclusions; unknown payment is `needs_review` | W-mc6a_veterans_payment_...; W-mc6b_disqualifying_payment_unsupported_...; W-mc6b_..._unknown_is_needs_review_...; spec cases mc6a/mc6b/mc6c | Covered |
| W-18 | MD 14/15 and MG 4 protected months `unsupported`; unknown `needs_review` | W-md14_15_protected_credit_unsupported_for_ftc_and_iwtc; W-mg4_protected_credit_unsupported_only_for_best_start; spec md14_15_..., mg4_... | Covered |
| W-19 | In-work eligibility excluded affects IWTC only, `unsupported` not `needs_review` | W-in_work_eligibility_excluded_only_affects_in_work_credit; spec in_work_eligibility_excluded_is_unsupported_not_needs_review; benchmark ird_iwtc_brooklyn_direct_abatement_pathway_out_of_scope | Covered |
| W-20 | s 80KW extra-instalment year `unsupported`; unknown `needs_review` | W-extra_instalment_status_applies_is_unsupported_for_all_components; spec s80kw_extra_instalment_is_unsupported; New: extra_instalment_year_is_unsupported_not_the_ordinary_amount (API; also asserts the missing-fact name for unknown) | Covered |
| W-21 | `unsupported` outranks `needs_review` | W-unsupported_takes_precedence_over_needs_review_at_household_gate; W-unsupported_takes_precedence_over_needs_review_within_a_component | Covered |
| W-22 | A missing fact is never zero; reason codes and missing-fact lists | W-* needs_review tests above; test_v0_1_5_explainability; test_wff_api::route_response_carries_an_explanation_per_component | Covered |
| W-23 | No WFF total unless every component calculated; never a partial total (WFF-01/02/07/08) | W-total_is_none_when_any_component_is_not_calculated; W-total_sums_only_when_every_component_is_calculated; New: wff_components_are_reported_separately_never_as_a_sum (API response has no total field) | Covered |
| W-24 | Policy version / modelled date / parameter interval validation | test_wff_module (modelled_date_outside_reference_period..., mismatched_policy_id..., parameter_interval_*, open_ended_parameter_value..., requested_policy_version_mismatch_still_raises); test_wff_api::calculate_maps_policy_version_mismatch_to_409_not_200 | Covered |
| W-25 | Negative incomes rejected | W-negative_claimant_income_rejected; W-negative_partner_income_rejected; W-negative_net_family_scheme_income_rejected | Covered |
| W-26 | Unknown request fields rejected (API) | Before: none for /wff/calculate. New: wff_route_rejects_an_unknown_top_level_field; wff_route_rejects_an_unknown_child_field | Covered (new) |
| W-27 | Malformed body gives 4xx, no 500 detail leak | test_wff_api::calculate_rejects_malformed_request_body; 500_handler_does_not_leak_exception_detail | Covered |

## AS matrix

| ID | Rule (spec section) | Tests | Status |
| --- | --- | --- | --- |
| A-01 | Plain-case qualifying cost (step 2) | A-ordinary_jobseeker_case_no_income_test; spec ordinary_uncapped_jobseeker | Covered |
| A-02 | Entry threshold selected by claimant and rate household; subtracted directly, no 25% multiplication (step 3, Task 26a) | R-formerly_colliding_households_use_different_thresholds_but_the_same_cap; R-threshold_is_subtracted_directly_not_multiplied; R-no_fallback_to_old_base_rate_ids; R-couple_with_exactly_one_child_uses_the_couple_with_children_row; real-policy spec cases | Covered |
| A-03 | 70% of excess, area cap by household category (step 4) | A-area_cap_binds_before_income_reduction; spec ordinary_area_cap_binds; benchmarks msd_nadiya_supported_living_rent, msd_lev_sole_parent_board | Covered |
| A-04 | Non-positive excess is a genuine calculated zero | A-cost_based_amount_at_entry_threshold_is_a_genuine_zero; R-costs_exactly_at_the_published_threshold_are_a_calculated_zero; spec exact_entry_threshold_is_zero | Covered |
| A-05 | Non-beneficiary income reduction, exact unrounded excess (DEC-001) | A-non_beneficiary_income_reduction_unrounded_excess; regression dec001_uses_exact_fractional_income_excess_not_floor_first; spec non_beneficiary_fractional_income_excess_unrounded; benchmark msd_single_non_beneficiary_income_reduction | Covered |
| A-06 | Beneficiary never consults an income level | R-beneficiary_never_consults_an_income_level; R-no_fallback_to_the_claimant_only_income_level_id | Covered |
| A-07 | Reduction cannot make the result negative | A-income_reduction_exceeding_cost_based_amount_floors_to_zero; regression non_beneficiary_reduction_cannot_make_the_result_negative | Covered |
| A-08 | Cash-asset imputation of $1 per complete $100 above the threshold | A-... (assets at/over threshold cases; values 5,400 and 2,700 appear); no case at the per-$100 step edges | Partial: see numeric gaps |
| A-09 | r 15 asset ceiling: exceeded `unsupported`; exactly met passes | A-asset_ceiling_exceeded_is_unsupported_not_zero; A-assets_exactly_at_the_r15_ceiling_meet_the_requirement; spec cases; regression r15_asset_ceiling_preempts_an_unrelated_needs_review_trigger; test_as_api::calculate_real_policy_asset_ceiling_is_unsupported | Covered (single ceiling; couple/dependants ceiling is numeric, see gaps) |
| A-10 | Final amount rounded up once (step 6, r 19) | A-ordinary_jobseeker_case_no_income_test (87.5 to 88); spec asset_ceiling_exactly_met_is_eligible; New: a_calculated_as_amount_is_a_whole_dollar_amount (structural, API, four cost inputs) | Covered (boundary values see gaps) |
| A-11 | Verified $0 accommodation cost is `unsupported`, not a calculated zero | A-zero_accommodation_costs_is_unsupported_not_zero; New: as_scope_and_missing_fact_outcomes (code AS_NO_ACCOMMODATION_COSTS) | Covered |
| A-12 | Household gate: excluded eligibility, pension/veterans, mixed-benefit couple, homeowner, joint tenancy, community spouse, exempt-asset unknown/excluded | A-unsupported_household_gate_triggers (excluded, pension, homeowner, joint tenancy, exempt asset x2); spec mixed_benefit_couple_is_unsupported, community_partner_is_unsupported; New: as_scope_and_missing_fact_outcomes (all, with reason codes, at API level) | Covered |
| A-13 | Unverified fact is `needs_review` and named: eligibility, category, tenure, partner, area, costs, children, assets, non-beneficiary income | A-unverified_facts_are_needs_review_not_a_silent_default; A-non_beneficiary_missing_weekly_income_is_needs_review; spec cases *_unverified; New: as_scope_and_missing_fact_outcomes (codes and missing_facts at API level) | Covered |
| A-14 | Unverified area never defaults to Area 4 | spec area_unverified; New: as_scope_and_missing_fact_outcomes (AS_AREA_UNVERIFIED) | Covered |
| A-15 | Sole Parent Support needs a sole-parent household; parent rows need eldest child under 16 | R-sole_parent_support_without_a_sole_parent_household_is_unsupported; R-parent_rows_require_the_eldest_child_under_16; R-childless_households_do_not_consult_the_child_age_fact; test_as_api::calculate_passes_eldest_child_exclusion_through | Covered |
| A-16 | Ordinary-rate status gate; exclusion precedence over unverified fact | R-ordinary_rate_status_gate; R-ordinary_rate_exclusion_takes_precedence_over_an_unverified_fact; R-omitted_new_facts_default_to_unverified | Covered |
| A-17 | `unsupported` outranks `needs_review` | R-known_unsupported_case_is_not_hidden_behind_unverified_cash_assets; regression r15_...preempts...; New: as_unsupported_outranks_needs_review_through_the_api | Covered |
| A-18 | Real-policy undeclared base rate is `needs_review`, not a crash | A-real_policy_undeclared_base_rate_is_needs_review_not_a_crash; regression real_policy_undeclared_base_rate_and_income_level_need_review | Covered |
| A-19 | Assessment week exactly 7 days; inside reference period; lookup date within the week | test_as_module (assessment_week_must_be_seven_days, week_*_reference_period_*, lookup_date_*, value_changing_inside_the_week...); test_as_api (requires_an_assessment_week, rejects_a_week_that_is_not_seven_days); regression test_as_weekly_validation | Covered |
| A-20 | Requested policy version mismatch (409), pre-repair version refused | test_as_api::calculate_maps_policy_version_mismatch_to_409_not_200, calculate_refuses_the_pre_repair_policy_version | Covered |
| A-21 | Unknown request fields rejected (API) | Before: only /household/calculate. New: as_route_rejects_an_unknown_field (including date_of_birth and age) | Covered (new) |
| A-22 | Negative amounts, malformed body, no 500 leak | test_as_api (rejects_negative_amount_as_422_not_500, rejects_malformed_request_body, 500_handler_does_not_leak_exception_detail) | Covered |
| A-23 | Decimal serialised as string, exact | test_as_api::calculate_serializes_fractional_decimal_value_as_json_string | Covered |

## Cross-policy matrix (AS "Task 28.3 WFF-AS interaction contract")

| ID | Rule | Tests | Status |
| --- | --- | --- | --- |
| X-01 | Native periods; no sum, no conversion; no combined total | C-periods_are_native_and_there_is_no_total; test_household_api (`"total" not in body`); test_wff_as_interaction_leaks | Covered |
| X-02 | No income coupling in either direction | C-no_income_coupling_in_either_direction; regression as_amount_is_not_added_to_wff_family_scheme_income, wff_credit_is_not_added_to_as_chargeable_income, wff_income_change_leaves_as_unchanged | Covered |
| X-03 | Precondition: AS claimant is WFF claimant or partner (unknown: `needs_review`; excluded: `unsupported`) | C-unverified_precondition_flags_every_component; C-excluded_precondition_makes_every_component_unsupported | Covered |
| X-04 | Shared-fact checks (partner status, main benefit x4, dependent children); unknown not compared; community spouse not compared | C-each_disagreement_flags_every_non_unsupported_component; C-main_benefit_names_each_verified_wff_assertion; C-protected_credit_leak_...; C-other_as_couple_forms_...; C-community_spouse_is_not_compared; C-unverified_facts_are_left_to_each_policy | Covered |
| X-05 | AS week must lie inside the WFF year | C-week_outside_the_wff_year_is_a_contradiction; periods.py containment relation | Covered |
| X-06 | Originals preserved; structural errors propagate | C-original_results_are_preserved_alongside_replacements; C-structural_errors_propagate | Covered |
| X-07 | Unknown request fields rejected on the household route | test_household_api::unknown_request_fields_are_rejected_not_ignored; omitted_wff_children_is_a_validation_error_not_no_children | Covered |

## Summary

| | Covered | Partial | Missing |
| --- | --- | --- | --- |
| WFF (27 rows) | 26 | 1 (W-16) | 0 |
| AS (23 rows) | 22 | 1 (A-08) | 0 |
| Cross-policy (7 rows) | 7 | 0 | 0 |
| Total (57 rows) | 55 | 2 | 0 |

Rows that were API-level or explicit-invariant gaps before this change and are now covered by new tests:
W-05 (IWTC invariant at API), W-20 and W-15 (API), W-23 (API shape), W-26 and A-21 (unknown fields on the two
route families), A-10 (structural whole-dollar check), A-11 to A-14 and A-17 (API-level codes and missing-fact
lists). Engine-level coverage of those already existed in the spec cases.

## Numeric gaps for the doctrine process (not written)

Each needs an expected dollar value derived independently from a primary source before any test is added.

| Rule | Why | Locator that would derive it |
| --- | --- | --- |
| A-08 imputation step edges (assets one dollar under and exactly at each $100 step above the threshold; the $2,700 and $5,400 thresholds) | `$1 per complete $100`: no case sits on a step edge | AS spec step 5, "s 423(3)" as cited there; the Act text itself must be fetched for the edge case |
| A-09 couple / dependent-children asset ceiling ($16,200) at, and one cent above, the ceiling | Only the single ceiling has spec cases | AS spec step 1 and r 15 as cited there |
| A-10 r 19 rounding where the pre-round amount is exactly integral, and just above an integer | Existing cases cover 87.5 and 74.90 only | AS spec step 6, r 19 |
| W-09 Best Start abatement at income exactly $79,000 plus $1 and plus $0.99 (complete-dollar excess) | $79,001 appears in no test; $79,000 does | WFF spec step 5; `wff-tax-credit-order-2025` cl 6; ITA MG 3(2)(a) |
| W-02 FTC abatement at $44,900.99 (fractional dollar below the first complete dollar) | The complete-dollar rule is tested at 44,900 and 44,901 but not at the sub-dollar edge | WFF spec step 2; ITA MD 13(3)(a) |
| W-06 MFTC at net income one dollar below, and one cent below, $36,604 | Only "zero at or above" is a case | WFF spec step 4; ITA ME 3 |

## Findings

- No defect found; no xfail added.
- P3 (documentation): the module docstring of `tests/unit/api/test_as_api.py` still says that no request against the
  real policy yields `calculated`. A plain jobseeker request now does, as the spec case
  `asset_ceiling_exactly_met_is_eligible` and the API show. The docstring is stale; I did not edit that existing
  test file.
- A relationship change is not an expressible input (W-16). Whether a "relationship changed in year" fact should
  exist, so that it can return `unsupported`, is a specification question for Pete, not a test gap.
