# Income tax conformance matrix (Phase C Task 12)

Author: Claude Code (Sonnet 5.5), 29 October 2026 NZDT. Base: main `2ac7eff`. Scope: every rule row IT-01 to
IT-08, each step of the calculation sequence, the outcome-precedence rules, the gates and every reason code of
`policy_specs/income_tax/specification.md` and its household mapping, mapped to the tests that exercise them. This is
a test inventory, not a policy review: it did not re-derive any statutory value, interpret any rule, or change any
expected value (`doctrine/test-doctrine.md`). Every income-tax value is draft `needs_review` with
`policy_version: null`, so no test, old or new, asserts a `calculated` result or a statutory amount.

Test classes: **Spec** = `policy_specs/income_tax/spec_cases.yaml` (47 cases, all non-numeric `expected`, 17 with a
`conditional_arithmetic` hand calculation that is a Model output, not an expectation) run by
`test_income_tax_spec_cases.py`; **Benchmark** = `benchmarks.yaml` (empty: `benchmark_status: missing_source`);
**Regression** = none yet for income tax. Income tax is not exposed on the API (the workbench rejects an
`income_tax` reform and `/api/v1/evidence?policy=income_tax` returns 404), so conformance is at engine and household
level. "New" = added by this change in `tests/unit/engines/simulator/test_income_tax_conformance.py` (non-numeric only).
Existing-test names are abbreviated (the `test_` prefix is dropped). Prefixes: `E-` =
`tests/unit/engines/simulator/test_income_tax.py`, `S-` = `test_income_tax_spec_cases.py` (`spec case <id>` for one
case), `H-` = `tests/unit/scenarios/test_household_income_tax.py`, `F-` = `tests/unit/policy/test_fact_catalogs.py`,
`N-` = the new file.

## Rule matrix (spec "Source-linked rule map")

| ID | Rule | Tests | Status |
| --- | --- | --- | --- |
| IT-01 | One natural person, ordinary resident; no joint household assessment | spec cases household_company_or_trust_entity, non_resident, changing_residence, special_residence_regime; E-unsupported_outranks_missing_facts_and_every_gate; H-each_person_maps_on_their_own_facts_and_spells, a_known_exclusion_outranks_a_mapping_refusal, q10_reads_only_the_selected_person; New: N-it01_05_each_known_exclusion... (codes IT_NOT_NATURAL_PERSON, IT_RESIDENCE_NOT_MODELLED), the_exclusion_table_covers_every_out_of_slice_enum_member | Covered (new) |
| IT-02 | Standard 2026-27 year only; amount already allocated, no annualisation or derivation | spec cases non_standard_year, other_standard_year; E-a_date_outside_the_reference_period_is_unsupported, both_reference_period_edges; H-one_whole_year_spell_is_used_as_given_and_parts_are_never_summed, the_asserted_year_and_the_mapped_period_must_agree, the_adapter_refuses_another_years_amount_dated_2026_27, the_adapter_infers_no_year_for_an_unknown_basis; New: N-it01_05_each_known_exclusion... (IT_TAX_YEAR_NOT_MODELLED), it02_a_date_outside_the_period_is_traced..., it02_an_unknown_amount_is_not_a_known_zero_in_the_trace | Covered (new) |
| IT-03 | Ordinary salary/wages only; other CE 1 classes excluded; income supplied, not inferred | spec cases main_benefit_income_deferred, business_or_self_employment, investment_or_rent, foreign_income, unusual_employment_items, schedular_or_pie, other_or_mixed_income; H-taxable_income_is_never_derived_from_earnings_or_another_basis, only_an_unsplit_total_is_taxable_income, q10_ignores_a_straddler_of_another_basis | Covered |
| IT-04 | Gross, deductions, net and losses distinct; no-deduction/no-loss slice only | spec cases deductions_apply, losses_apply, false_taxable_basis_attestation, missing_taxable_basis_attestation; E-a_false_attestation_is_gated_before_any_parameter; H-deductions_and_losses_map_each_to_its_own_field, the_adapter_sets_deductions_and_losses_each_to_its_own_field; New: N-it01_05_each_known_exclusion... (IT_DEDUCTIONS_NOT_MODELLED, IT_LOSSES_NOT_MODELLED) | Covered (new) |
| IT-05 | General Table 1 applies only if no special basic rate; per-dollar band sum, not top rate on all income | spec case special_basic_rate; E-band_sum_on_synthetic_parameters, band_sum_records_each_band_and_the_total, income_on_a_band_boundary_records_no_empty_band, p3_the_band_sum_is_exact_whatever_the_callers_precision (synthetic parameters, no statutory value); S-conditional_arithmetic_matches_the_band_sum (17 hand calculations on the draft candidate values, never a result); New: N-it01_05_each_known_exclusion... (IT_SPECIAL_BASIC_RATE_NOT_MODELLED) | Partial: structure and exclusion covered; the statutory rates and thresholds are unapproved candidates, so no test can assert them (numeric list below) |
| IT-06 | BB 1 annual-authority gate; TAA s 92A kept separate; 2026-27 `needs_review` | E-the_draft_policy_is_never_loaded_as_executable, every_module_result_is_traced...; spec cases (every supported case ends IT_POLICY_NOT_APPROVED); New: N-it06_the_policy_gate_names_the_annual_authority_questions, it06_no_caller_assertion_clears_the_server_gates | Partial: the refusal side is covered; no approved policy exists, so the pass side (assent and application evidenced) cannot be exercised. Whether s 92A supports a different component is DEC-001's open question, not a test gap |
| IT-07 | Component is basic tax, not a completed assessment (credits, PAYE, ACC, terminal tax, refunds, net wages excluded) | E-every_result_from_a_parameter_set_is_traced (component id); New: N-it07_the_component_is_declared_basic_tax_only_with_its_exclusions (policy.yaml output unit, class, `excludes`, one component, outcome precedence) | Partial: declared and pinned, but no input can request PAYE, ACC, credits or terminal tax, so the spec handoff line "such requests are separate unsupported components" has no surface to test. Listed as an escalation |
| IT-08 | Whole-dollar input (Q17 Assumption), no rounding of income; exact band arithmetic kept apart from final output precision (DEC-004) | spec cases fractional_positive_Q17, fractional_below_first_dollar_Q17, negative_income_outside_slice, whole_dollar_decimal_transport; E-band_sum_refuses_non_whole_or_negative_income, non_finite_or_binary_float_income_is_rejected, approved_parameters_still_stop_at_the_output_precision_gate; H-one_whole_year_spell... (amount passes through unrounded), a_typed_straddler_does_not_hide_a_known_numeric_exclusion; New: N-request_validation_rejects_non_decimal_income, it08_fully_approved_synthetic_parameters_still_give_no_amount | Partial: input boundary covered; final-output method is `MISSING_SOURCE` (DEC-004), so no amount or rounding can be tested |

## Calculation sequence (spec "Proposed calculation and trace sequence")

| ID | Step | Tests | Status |
| --- | --- | --- | --- |
| SEQ-1 | Validate identity, year and supported-slice facts; report out-of-scope and missing facts without inventing values | All spec cases through the module; E-missing_facts_are_named_in_scenario_order; F-the_income_tax_catalogue_covers_every_fact_the_engine_emits; New: N-it01_08_each_unknown_fact_is_named_and_no_other_is (9 facts), all_facts_unknown_names_every_fact_in_scenario_order | Covered (new) |
| SEQ-2 | Verify the taxable amount's meaning, year, no deductions/losses, general-rate applicability (attestation) | spec cases missing_/false_taxable_basis_attestation; E-a_false_attestation_is_gated_before_any_parameter | Covered |
| SEQ-3 | Resolve authority and reviewed precision; either pending gate stops a numeric result; Bill 344-1 supplies no rate | E-the_draft_policy_is_never_loaded..., approved_parameters_still_stop_at_the_output_precision_gate, a_needs_review_parameter_gates_the_component; New: N-calculation_step3_every_spec_case_is_gated_with_no_amount_and_no_candidate_value (47 cases: no value, no steps, no parameter value in trace), the_draft_policy_state_gates_every_value, the_loader_refuses_the_draft_policy_as_executable | Covered (new) |
| SEQ-4 | After approval only: apply reviewed table and precision procedure, including known-zero path | E-band_sum tests on synthetic parameters; E-known_zero_income_is_gated_not_zero; spec case known_zero_stays_gated | Partial: the approved path is unimplemented (`NotImplementedError` behind DEC-004), so there is nothing to conform to until the method is sourced and reviewed |
| SEQ-5 | Emit only the basic-tax component with unit, individual, period, Model-output class; trace inputs, policy/version, parameter intervals and review states, sources, rule/decision ids, steps | E-every_module_result_is_traced_with_its_period_and_parameter_provenance, r2_a_draft_result_exports_a_provenance_report, r2_a_changed_bound_artifact_is_detected, r2_policy_yaml_is_read_once_per_run; test_explanation::every_income_tax_step_renders; New: N-calculation_step5_every_refusal_trace_names_the_policy_state_and_caller_assertions, the_trace_identity_follows_the_scenario | Partial: trace is covered on every refusal path; the emitted-component fields (unit, class) are only declared in policy.yaml (IT-07 row) because no result is `calculated` |

## Outcome precedence and refusal ordering

| ID | Rule | Tests | Status |
| --- | --- | --- | --- |
| P-01 | `unsupported` outranks `needs_review` (known exclusion before any missing fact) | spec case unsupported_precedes_missing_income_and_authority; E-unsupported_outranks_missing_facts_and_every_gate; New: N-precedence_each_exclusion_outranks_every_missing_fact (every exclusion against an all-unknown scenario) | Covered (new) |
| P-02 | An `unsupported` parameter outranks an earlier unapproved one | E-r3_an_unsupported_parameter_outranks_an_earlier_unapproved_one | Covered |
| P-03 | A date outside the reference period outranks missing facts; a known exclusion is reported as itself | E-a_date_outside_the_reference_period_is_unsupported; New: N-it02_a_date_outside_the_period_is_traced... (the outranks-missing-facts half; the existing test covers the exclusion half) | Covered |
| P-04 | Known zero is distinct from unknown and still gated; a missing fact is never zero | spec cases known_zero_stays_gated, unknown_income_is_not_zero; E-known_zero_income_is_gated_not_zero; New: N-it02_an_unknown_amount_is_not_a_known_zero_in_the_trace | Covered (new) |
| P-05 | Missing facts named in scenario order; a false attestation names none | E-missing_facts_are_named_in_scenario_order, a_false_attestation_is_gated_before_any_parameter; New: N-all_facts_unknown_names_every_fact_in_scenario_order | Covered (new) |
| P-06 | Household path: a known exclusion is `unsupported` before any mapping refusal | H-a_known_exclusion_outranks_a_mapping_refusal, a_refusal_falls_back_on_the_selected_persons_facts, a_typed_straddler_does_not_hide_a_known_numeric_exclusion; New: N-household_a_known_exclusion_keeps_its_engine_code | Covered (new) |
| P-07 | Policy identity and requested version are checked before any result, refusal paths included | E-a_requested_policy_version_must_match, r1_another_policy_is_refused_even_on_a_refusal_path, r1_an_unsupported_schema_is_refused_before_any_result, another_policys_parameters_are_refused; H-the_run_passes_the_policy_dir_the_modelled_date_and_the_requested_version; New: N-a_version_mismatch_is_raised_before_any_refusal_result (supported, unsupported and missing-fact scenarios) | Covered (new) |

## Gates

| ID | Gate | Tests | Status |
| --- | --- | --- | --- |
| G-01 | Annual assent and application (Q16, DEC-001): policy not approved | E-the_draft_policy_is_never_loaded_as_executable (names Q16); New: N-it06_the_policy_gate_names_the_annual_authority_questions (Q16 and DEC-001, no missing fact) | Covered (new) |
| G-02 | Full-period coverage: intervals complete, never defaulted to zero or current | E-every_module_result_is_traced... (every parameter's interval equals the reference period), a_parameter_with_no_interval_is_unsupported, an_undeclared_parameter_is_unsupported_not_a_key_error; test_loader overlapping-interval refusal (generic); New: N-the_draft_policy_state_gates_every_value | Partial: structural coverage only; "reviewed period-amendment coverage" is a human review gate with no executable form |
| G-03 | DEC-004 output precision: no amount from the exact sum | E-approved_parameters_still_stop_at_the_output_precision_gate; New: N-it08_fully_approved_synthetic_parameters_still_give_no_amount (five synthetic incomes) | Covered (new) |
| G-04 | Protected values and benchmark: none approved, none adopted | S-the_cases_are_complete_unique_and_all_non_numeric; New: N-the_draft_policy_state_gates_every_value (status draft, `policy_version` null, every parameter `needs_review`, benchmarks empty and `missing_source`) | Covered (new) |
| G-05 | Draft policy is never executable; candidate values never reach a result | E-the_draft_policy_is_never_loaded_as_executable; test_loader::unapproved_policy_status_rejected (generic); New: N-the_loader_refuses_the_draft_policy_as_executable, calculation_step3_every_spec_case_is_gated... | Covered (new) |
| G-06 | No caller field can unlock a server gate | New: N-it06_no_caller_assertion_clears_the_server_gates (no authority/precision field in the scenario; best-case assertions still stop) | Partial: the absence check names specific fields, so it would not catch an unlock field added under another name; the best-case stop is the real evidence |
| G-07 | Income tax not exposed on the API before it is conformance-tested | test_workbench_api (an `income_tax` reform is rejected), test_v1_catalogue::evidence_filters_by_policy_and_rejects_an_undeployed_one | Covered |

## Reason codes (engine `IT_*`, household `HOUSEHOLD_*`)

| ID | Code (outcome) | Tests | Status |
| --- | --- | --- | --- |
| C-01 | IT_NOT_NATURAL_PERSON (unsupported) | spec case household_company_or_trust_entity (outcome and category only); New: N-it01_05_each_known_exclusion..., precedence_each_exclusion... | Covered (new) |
| C-02 | IT_RESIDENCE_NOT_MODELLED (unsupported) | E-a_date_outside_the_reference_period_is_unsupported; H-a_known_exclusion_outranks_a_mapping_refusal; New: N-it01_05_each_known_exclusion... (3 members), household_a_known_exclusion_keeps_its_engine_code | Covered |
| C-03 | IT_TAX_YEAR_NOT_MODELLED (unsupported) | spec cases non_standard_year, other_standard_year (outcome and category only); New: N-it01_05_each_known_exclusion..., precedence_each_exclusion... | Covered (new) |
| C-04 | IT_INCOME_COMPOSITION_NOT_MODELLED (unsupported) | E-unsupported_outranks_missing_facts_and_every_gate; New: N-it01_05_each_known_exclusion... (all 7 members) | Covered |
| C-05 | IT_DEDUCTIONS_NOT_MODELLED (unsupported) | spec case deductions_apply (outcome only); New: N-it01_05_each_known_exclusion... | Covered (new) |
| C-06 | IT_LOSSES_NOT_MODELLED (unsupported) | spec case losses_apply (outcome only); New: N-it01_05_each_known_exclusion... | Covered (new) |
| C-07 | IT_SPECIAL_BASIC_RATE_NOT_MODELLED (unsupported) | spec case special_basic_rate (outcome only); New: N-it01_05_each_known_exclusion... | Covered (new) |
| C-08 | IT_NEGATIVE_INCOME_NOT_MODELLED (unsupported) | H-a_typed_straddler_does_not_hide_a_known_numeric_exclusion; New: N-it01_05_each_known_exclusion... | Covered |
| C-09 | IT_FRACTIONAL_INCOME_NOT_MODELLED (unsupported) | H-one_whole_year_spell_is_used_as_given..., a_typed_straddler_does_not_hide...; New: N-it01_05_each_known_exclusion... | Covered |
| C-10 | IT_PARAMETER_UNDECLARED (unsupported) | E-an_undeclared_parameter_is_unsupported_not_a_key_error | Covered |
| C-11 | IT_PARAMETER_NO_INTERVAL (unsupported) | E-a_parameter_with_no_interval_is_unsupported, r3_... | Covered |
| C-12 | IT_DATE_OUTSIDE_REFERENCE_PERIOD (unsupported) | E-a_date_outside_the_reference_period_is_unsupported; H-the_run_passes_the_policy_dir_the_modelled_date...; New: N-it02_a_date_outside_the_period_is_traced... | Covered (new) |
| C-13 | IT_FACTS_UNVERIFIED (needs_review, names the facts) | spec cases unknown_* (9 single-fact cases); E-missing_facts_are_named_in_scenario_order; H-each_person_maps_on_their_own_facts_and_spells; F-the_income_tax_catalogue_covers_every_fact_the_engine_emits; New: N-it01_08_each_unknown_fact_is_named_and_no_other_is | Covered (new) |
| C-14 | IT_TAXABLE_INCOME_NOT_ATTESTED (needs_review, no missing fact) | spec case false_taxable_basis_attestation; E-a_false_attestation_is_gated_before_any_parameter | Covered |
| C-15 | IT_PARAMETER_NOT_APPROVED (needs_review) | E-a_needs_review_parameter_gates_the_component, r3_... | Covered (engine only: unreachable through the draft module path, which stops at C-17) |
| C-16 | IT_OUTPUT_PRECISION_UNRESOLVED (needs_review) | E-approved_parameters_still_stop_at_the_output_precision_gate, known_zero_income_is_gated_not_zero; New: N-it08_fully_approved_synthetic_parameters_still_give_no_amount | Covered (new) |
| C-17 | IT_POLICY_NOT_APPROVED (needs_review) | E-the_draft_policy_is_never_loaded_as_executable, both_reference_period_edges; every supported spec case (S-spec_case asserts the code); H-an_in_slice_person_stops_at_the_draft_policy_gate_with_no_amount | Covered |
| C-18 | HOUSEHOLD_MAPPING_INVALID_FACTS (needs_review) | H-one_whole_year_spell_is_used_as_given_and_parts_are_never_summed, the_asserted_year_and_the_mapped_period_must_agree; New: N-household_several_spells_is_a_traced_needs_review_with_no_amount (through `run_household_income_tax`, trace income unknown) | Covered (new) |
| C-19 | HOUSEHOLD_SPELL_PERIOD_MISMATCH (needs_review) | H-a_spell_past_the_year_is_refused_never_apportioned (traced), q10_reads_only_the_selected_person, q10_refuses_a_spell_ending_past_the_year | Covered |
| C-20 | Every engine code is listed here | New: N-every_engine_reason_code_is_listed_with_its_outcome (source scan: a new `IT_*` code fails until classified) | Covered (new) |

## Household mapping (`to_income_tax`, `run_household_income_tax`, `household_from_income_tax`)

| ID | Rule | Tests | Status |
| --- | --- | --- | --- |
| M-01 | Round trip: every spec case maps back to an identical scenario, result and trace hash | H-every_spec_case_the_year_can_hold_round_trips_through_a_household (45), every_spec_case_asserting_another_year_is_held_at_its_own_period (2), the_round_trip_groups_cover_every_case | Covered |
| M-02 | Each person maps on their own facts and spells; nothing read from partner or family; unasserted facts unknown | H-each_person_maps_on_their_own_facts_and_spells, q10_reads_only_the_selected_person | Covered |
| M-03 | One whole-year spell used as given; several refused, never summed; none or part-year is unknown, never zero | H-one_whole_year_spell_is_used_as_given_and_parts_are_never_summed, a_disjoint_previous_year_spell_does_not_refuse_the_year | Covered |
| M-04 | No apportionment of a spell past the year (Q10) | H-a_spell_past_the_year_is_refused_never_apportioned, q10_* (4) | Covered |
| M-05 | Taxable income never derived from earnings or another policy's basis | H-taxable_income_is_never_derived_from_earnings_or_another_basis, only_an_unsplit_total_is_taxable_income | Covered |
| M-06 | Asserted year and mapped period must agree; run accepts only the policy's reference period | H-the_asserted_year_and_the_mapped_period_must_agree, the_run_takes_only_the_policy_reference_period_and_a_held_person | Covered |
| M-07 | Attestation is a strict boolean; enums carry the engine values plus unknown | H-an_attestation_is_a_strict_boolean, the_household_enums_carry_the_engine_values_plus_unknown, deductions_and_losses_map_each_to_its_own_field | Covered |
| M-08 | Adapter refuses a relabelled year; infers no year; keeps identities | H-the_adapter_refuses_a_period_the_scenario_does_not_assert, the_adapter_refuses_another_years_amount_dated_2026_27, the_adapter_infers_no_year_for_an_unknown_basis, the_adapter_dates_the_spell_to_the_period_it_is_given, the_adapter_keeps_the_given_identities, the_adapter_sets_deductions_and_losses_each_to_its_own_field | Covered |
| M-09 | A household without tax facts keeps its content hash | H-a_household_without_tax_facts_keeps_its_identity | Covered |
| M-10 | A mapping refusal names the missing fact (never-zero reporting) | H-part-year gap names `annual_taxable_income` (one_whole_year_spell...); the two `HOUSEHOLD_*` refusals carry no `missing_facts` | Partial: see escalation 3 below |

## Summary

| Section | Rows | Covered | Covered (new) | Partial | Gap |
| --- | --- | --- | --- | --- | --- |
| Rules IT-01 to IT-08 | 8 | 1 | 3 | 4 | 0 |
| Calculation sequence (5 steps) | 5 | 1 | 2 | 2 | 0 |
| Outcome precedence | 7 | 2 | 5 | 0 | 0 |
| Gates | 7 | 1 | 4 | 2 | 0 |
| Reason codes (17 engine, 2 household, 1 completeness) | 20 | 10 | 10 | 0 | 0 |
| Household mapping | 10 | 9 | 0 | 1 | 0 |
| Total | 57 | 24 | 24 | 9 | 0 |

"Covered (new)" means the row had no test, or only an outcome-and-category check, before this change. Nine Partial
rows are not closable by a non-numeric test: IT-05, IT-06, IT-07, IT-08, SEQ-4, SEQ-5, G-02, G-06 and M-10 (reasons in the
rows). No row is a plain Gap. The new file adds 82 tests (`pytest -q tests/unit/engines/simulator/test_income_tax_conformance.py`);
none asserts a statutory amount or a `calculated` result, and no engine, policy or expected value was changed.

## Numeric cases listed for the test-doctrine process, not written

Each needs an expected value derived independently from a primary source and approved under
`doctrine/test-doctrine.md` before any test is added. None can be written until DEC-004 (final output precision) and
the 2026-27 annual-authority gate (Q16, DEC-001) are decided and the policy is approved.

| Rule | Why | Locator that would derive it |
| --- | --- | --- |
| IT-05 final amount at each band edge and one dollar either side (15,600 / 53,500 / 78,100 / 180,000) | `spec_cases.yaml` holds hand arithmetic as `conditional_arithmetic` (a Model output); `expected` is deliberately non-numeric, so no approved expected amount exists | Schedule 1 Part A cl 1 and Table 1; BC 6(1) as cited in the specification; official benchmark per `benchmarks.yaml` `acceptance_requires` |
| IT-08 sub-cent result (the specification's own example: 15,603 gives a three-decimal exact sum) | How the exact sum becomes a final amount is `MISSING_SOURCE` | DEC-004 once decided; the retained official artifact it asks for |
| SEQ-4 known zero after approval | The zero path is gated today; the approved value and its representation (scale) are unset | BC 6(2); DEC-004 |
| IT-05 non-decreasing tax across the period once amounts exist | The specification states monotonicity within the slice, but it is a property of approved amounts | Table 1 and BC 6 as cited |
| IT-05 parameter values themselves (five rates, four thresholds) | They are `needs_review` candidates; a test asserting them would promote them | `it-income-tax-act-basic-rates`, `it-budget-measures-act-2024` ss 2(5), 37 |
| Large income in the open top band (e.g. above 180,000) | Same gate; the open band is exercised only on synthetic parameters | Table 1 row 5 |

## Findings and escalations

- No defect found; no xfail added; no engine, policy or spec file changed.
- Repository state, not this change: `ruff check .` and `ruff format --check .` over the whole tree fail on `main`
  at `2ac7eff` (16 lint errors in `reviews/*.py` and `review_packets/`, 127 files unformatted). CI runs
  `ruff check src tests`, which passes, and the new file is formatted.
- Escalation 1 (IT-07): the specification handoff says PAYE, ACC, credit, terminal-tax and household-conversion
  requests are "separate unsupported components, never `basic_tax` aliases". No input or entry point can express such
  a request, so there is nothing to refuse. Whether a request surface (or a fact such as "requested output") should
  exist is a specification question for Pete, as W-16 was for WFF.
- Escalation 2 (IT-06): TAA s 92A and whether it supports a different Poltika component is left to a separate decision
  by the specification itself (DEC-001). Noted, not interpreted.
- Escalation 3 (M-10): a household mapping refusal (`HOUSEHOLD_MAPPING_INVALID_FACTS`, `HOUSEHOLD_SPELL_PERIOD_MISMATCH`)
  is `needs_review` with an empty `missing_facts`, while a part-year gap names `annual_taxable_income`. The spec says
  `needs_review` carries named missing facts; the mapping's own reason text names the cause. Whether these refusals
  should name `annual_taxable_income` is a design question, not a defect I could settle (`household_mappings.py`
  `_invalid`, `_q10_refusal`).
- Escalation 4 (request validation): the specification says malformed numeric transport belongs to request
  validation. There is no income-tax request model or route yet, so only the scenario dataclass rejects
  non-`Decimal` and non-finite income. An API-level conformance file is due when income tax is exposed.
- Escalation 5 (G-02): "reviewed period-amendment coverage" is a review gate with no executable form; only interval
  structure is testable.
