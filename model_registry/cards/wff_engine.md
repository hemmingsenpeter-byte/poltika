# Model card: Working for Families engine

Generated from `model_registry/registry.yaml` by
`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.

- **Id:** `wff_engine` (engine)
- **Version:** 0.1.0. Package version in pyproject.toml. The engine has no version of its own. Each run records the source commit (src/poltika/scenarios/record.py, CodeIdentity). Policy version working_for_families 0.1.0 (policy_specs/working_for_families/policy.yaml).
- **Owner:** Pete (accountable model owner and decisions); Claude Code (implementation); GPT/Codex (sources, interpretation, independent review). Assigned under Pete's 5 October 2026 closeout authority; doctrine/model-governance.md.
- **Validation status:** `spec_validated`
- **Computed dependency label:** `spec_validated` (the least mature model it relies on; not yet attached to runtime outputs)

## Purpose

Calculates one household's Working for Families components (family tax credit, in-work tax credit, minimum family tax credit, Best Start) for the 2026-27 tax year, from the approved parameters and the caller's asserted facts. A component the facts or parameters cannot settle is needs_review or unsupported, never a guessed number.

## Methods

Entry points:

- `poltika.engines.simulator.wff.calculate_wff`
- `poltika.engines.simulator.wff.run_wff_module`

Relies on: no other registered model.

Evidence classes consumed: Rule, Scenario.

Rule: parameters with review_status approved and a cited source (policy_specs/working_for_families/policy.yaml). Scenario: the caller's asserted household facts (doctrine/epistemic-constitution.md, decision P2). Its results are Model output. The in_work_base parameter is needs_review and gates the in-work tax credit.

## Validation

Passes hand-calculated spec cases and published IRD worked examples for its declared supported domain. It has no empirical estimate and no predictive record. The validation framework (current Phase C; legacy Step 6) does not exist yet.

Validation cases:

- spec_cases: `policy_specs/working_for_families/spec_cases.yaml` (23)
- benchmarks: `policy_specs/working_for_families/benchmarks.yaml` (9)
- golden_households: `policy_specs/wff_as_interaction/golden_households.yaml` (9)
- golden_snapshot: `tests/fixtures/golden_results_v0_1.json` (9)

Tests:

- `tests/unit/engines/simulator/test_wff.py`
- `tests/unit/engines/simulator/test_wff_spec_cases.py`
- `tests/unit/engines/simulator/test_wff_benchmarks.py`
- `tests/unit/engines/simulator/test_wff_module.py`
- `tests/regression/test_known_historical_issues.py`
- `tests/regression/test_golden_result_snapshot.py`

Reviews:

- `reviews/2026-09-25-task34-3-codex.md`
- `review_packets/wff_task17.md`
- `review_packets/review_queue.md`

Open items:

- The in-work tax credit base rate is needs_review, so the in-work tax credit and the WFF total are never calculated (docs/releases/V0_1_LIMITATIONS.md).

## Limitations

- Facts are asserted, not verified. A result is a conditional simulation, not an entitlement decision. (`docs/releases/V0_1_LIMITATIONS.md`)
- Only the 2026-27 tax year is covered. Another period is needs_review or has no rate for the date. (`docs/releases/V0_1_LIMITATIONS.md`)
- Not modelled: relationship change, a child qualifying for part of the year, a birth or third birthday in the year, the MC 9 extension past age 18. (`docs/releases/V0_1_LIMITATIONS.md`)
- Not modelled: shared care, a competing claimant or MC 7 allocation, a residence route other than MC 5(2). (`docs/releases/V0_1_LIMITATIONS.md`)
- Not modelled: MD 14/15 protected family tax credit, the direct-abatement pathway, MG 4 protected Best Start months, a Tax Administration Act s 80KW extra-instalment year. (`docs/releases/V0_1_LIMITATIONS.md`)
- Best Start covers one birth cohort and one child in it. (`docs/releases/V0_1_LIMITATIONS.md`)
- Net family scheme income must be supplied and attested as an ME 3 derivation. Poltika does not derive it. (`docs/releases/V0_1_LIMITATIONS.md`)
- Instalments, overpayments and debts are not modelled. (`docs/releases/V0_1_LIMITATIONS.md`)

## Known model risks and failure modes

- The in-work tax credit base rate for 2026-27 can be reversed early by Order in Council, so the rate is gated and never calculated. (`docs/releases/V0_1_LIMITATIONS.md`)
- Evidenced ineligibility is $0 only where WFF DEC-001 says so. The decision is recorded and was open to the deferred GPT/Codex audit. (`policy_specs/working_for_families/decisions/DEC-001-evidenced-ineligibility-outcome.md`)

## Change log

| Date | What changed | Why | Evidence | Validation re-run | Approval |
| --- | --- | --- | --- | --- | --- |
| 2026-09-21 | Task 12, the pure calculate_wff() function (commit 5a94acd, PR | First implementation of the approved Task 10 scoped contract. | `policy_specs/working_for_families/spec_cases.yaml` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-09-22 | Task 20, the run_wff_module() integration entry point (commit f0566e6, PR | Module entry point over the policy loader and calculator (ARCHITECTURE.md module contract). | `tests/unit/engines/simulator/test_wff_module.py` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-09-25 | Calculation steps in the trace and structured review reasons (commits 0f81e2e, f8b4b3a). No calculated amount changed (CHANGELOG.md). | v0.1.5 explainability and structured needs_review reasons. | `docs/releases/V0_1_5_GATE.md` | tests/acceptance/test_v0_1_5_release_gate.py (gate row "v0.1 results unchanged") | unknown (recorded before change records existed) |
| 2026-10-05 | Registered in the model registry (Task 1.5). No code change. | BUILD_PLAN_PROGRAMME.md Task 1.5. | `model_registry/registry.yaml` | pytest -q, including tests/unit/engines/assurance/test_model_registry.py | Pete, 5 October 2026 closeout instruction to accept the best options; reviews/2026-10-05-pr164.md |
