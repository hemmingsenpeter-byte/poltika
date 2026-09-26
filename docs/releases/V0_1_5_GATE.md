# v0.1.5 release gate: how each row is checked

Sprint 2, S2.4. Every row of the release gate in `BUILD_PLAN_v0_1_5.md` is a
test in `tests/acceptance/test_v0_1_5_release_gate.py`, which runs in CI. A
run with every test passing and nothing skipped means the gate is met.

| Gate row | Test | Checked by |
| --- | --- | --- |
| v0.1 results unchanged | `test_gate_v0_1_results_unchanged` | Code: the golden results equal the frozen v0.1 snapshot |
| Protected values sourced at the required rank | `test_gate_protected_values_sourced_and_rules_evidence_linked` | Code: evidence coverage finds no problems |
| Calculated-path rules evidence-linked | `test_gate_calculated_path_rules_are_evidence_linked` | Code: every step's rule cites primary legislation |
| Explanation vs result consistent | `test_gate_explanations_consistent_with_results` | Code: golden households and the pilot pack |
| Temporal evidence | `test_gate_temporal_evidence` | Code |
| Missing inputs never defaulted; needs review structured | `test_gate_missing_inputs_never_defaulted_and_needs_review_structured` | Code: the pilot pack |
| Trace for every calculated result | `test_gate_trace_available_for_every_calculated_result` | Code |
| Assumptions surfaced | `test_gate_assumptions_surfaced` | Code |
| Reproducibility | `test_gate_reproducible` | Code |
| No open P0 or P1 | `test_gate_no_open_p0_or_p1_findings` | People record findings; code reads `docs/pilot/V0_1_5_PILOT_FINDINGS.md` |
| At least one external pilot user | `test_gate_external_pilot_user` | People. Skips until the findings record a pilot user |

As of 26 September 2026 every row passes except the external pilot user,
which is waiting on Pete (Sprint 2 S2.7).
