# Model card: Accommodation Supplement engine

Generated from `model_registry/registry.yaml` by
`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.

- **Id:** `as_engine` (engine)
- **Version:** 0.1.0 (package); policy accommodation_supplement 0.1.1. Package version in pyproject.toml. The engine has no version of its own. Each run records the source commit (src/poltika/scenarios/record.py, CodeIdentity). The policy version comes from policy_specs/accommodation_supplement/policy.yaml.
- **Owner:** Pete (accountable model owner and decisions); Claude Code (implementation); GPT/Codex (sources, interpretation, independent review). Assigned under Pete's 5 October 2026 closeout authority; doctrine/model-governance.md.
- **Validation status:** `spec_validated`
- **Computed dependency label:** `spec_validated` (the least mature model it relies on; not yet attached to runtime outputs)

## Purpose

Calculates one claimant's weekly Accommodation Supplement for an explicit assessment week, from the approved parameters and the caller's asserted facts. A component the facts or parameters cannot settle is needs_review or unsupported, never a guessed number.

## Methods

Entry points:

- `poltika.engines.simulator.accommodation_supplement.calculate_accommodation_supplement`
- `poltika.engines.simulator.accommodation_supplement.run_as_module`

Relies on: no other registered model.

Evidence classes consumed: Rule, Scenario.

Rule: approved parameters with a cited source, including published MSD table values at source rank 3 (policy_specs/accommodation_supplement/policy.yaml, DEC-002; epistemic-constitution decision 6). Scenario: the caller's asserted household facts. Its results are Model output. The class of each AS decision record (DEC-001 to DEC-003) is not yet stated; the constitution leaves existing records to a later change for Pete's confirmation.

## Validation

Passes hand-calculated spec cases and MSD worked examples for its declared supported domain. Most spec cases override the entry thresholds and income levels with synthetic parameter_assumptions (see the file header); the Task 26a.3 cases and the golden households run on the published values. No empirical estimate and no predictive record.

Validation cases:

- spec_cases: `policy_specs/accommodation_supplement/spec_cases.yaml` (26)
- benchmarks: `policy_specs/accommodation_supplement/benchmarks.yaml` (4)
- golden_households: `policy_specs/wff_as_interaction/golden_households.yaml` (9)
- golden_snapshot: `tests/fixtures/golden_results_v0_1.json` (9)

Tests:

- `tests/unit/engines/simulator/test_accommodation_supplement.py`
- `tests/unit/engines/simulator/test_as_spec_cases.py`
- `tests/unit/engines/simulator/test_as_benchmarks.py`
- `tests/unit/engines/simulator/test_as_module.py`
- `tests/unit/engines/simulator/test_as_rate_selectors.py`
- `tests/regression/test_as_known_historical_issues.py`
- `tests/regression/test_as_weekly_validation.py`
- `tests/regression/test_golden_result_snapshot.py`

Reviews:

- `reviews/2026-10-05-pr164.md`
- `reviews/2026-09-25-task34-3-codex.md`
- `review_packets/as_task24_4.md`
- `review_packets/task_26a_as_rate_audit.md`
- `review_packets/review_queue.md`

Open items:

- DEC-001 (income excess rounding) stays at medium confidence: no second published fractional-excess example was found.

## Limitations

- Facts are asserted, not verified. A result is a conditional simulation, not an entitlement decision. (`docs/releases/V0_1_LIMITATIONS.md`)
- Housing not modelled, namely homeowners, social housing, joint tenancy, a community spouse or partner, accommodation income or business use of the home. (`docs/releases/V0_1_LIMITATIONS.md`)
- Claimant categories not modelled: NZ Superannuation, Veteran's Pension, mixed-benefit couples, the protected Jobseeker woman-alone rate, special care and residential rates. (`docs/releases/V0_1_LIMITATIONS.md`)
- Other-funding exclusions and any exempt cash asset are not modelled (the Student Allowance exclusion or exception included). (`docs/releases/V0_1_LIMITATIONS.md`)
- The Statistical Area Unit's Area 1-4 must be verified. It is never inferred or defaulted. (`docs/releases/V0_1_LIMITATIONS.md`)
- Parent rows need the eldest dependent child under 16 for the whole week. Changes within a week are not modelled. (`docs/releases/V0_1_LIMITATIONS.md`)
- Only weeks inside the reference period are covered. Another period is needs_review or has no rate for the date. (`docs/releases/V0_1_LIMITATIONS.md`)

## Known model risks and failure modes

- The income-excess rounding convention (DEC-001) is selected at medium confidence. Whole-dollar excesses give the same result either way. (`policy_specs/accommodation_supplement/decisions/DEC-001-income-excess-rounding.md`)
- Entry thresholds and income levels rest on MSD's published tables (source rank 3), not on an Act or Order (DEC-002). (`policy_specs/accommodation_supplement/decisions/DEC-002-published-thresholds-and-rate-scope.md`)
- The WFF income exclusion from AS chargeable income (DEC-003) is a selected interpretation of the law's text. (`policy_specs/accommodation_supplement/decisions/DEC-003-msd-paid-wff-income-exclusion.md`)

## Change log

| Date | What changed | Why | Evidence | Validation re-run | Approval |
| --- | --- | --- | --- | --- | --- |
| 2026-09-23 | Task 23, the AS calculator, then Task 24.7 run_as_module() (commits 53a4084, 0186766). | First implementation of the approved Task 22 scoped contract and its module entry point. | `policy_specs/accommodation_supplement/spec_cases.yaml` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-09-24 | Task 26a.2/26a.3, the published AS thresholds and income levels added to policy.yaml (commit 2639676); policy version 0.1.1 (DEC-002). | Replace synthetic entry thresholds with the published values. | `policy_specs/accommodation_supplement/decisions/DEC-002-published-thresholds-and-rate-scope.md` | Task 26a.3 spec cases (policy_specs/accommodation_supplement/spec_cases.yaml) | unknown (recorded before change records existed) |
| 2026-09-26 | r 15 "must not exceed" boundary, $0-cost exclusion (commit c5d4ea2). | Findings from the v0.1 question-set review (Q71-Q140). | `review_packets/v0_1_question_set` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-10-05 | Registered in the model registry (Task 1.5). No code change. | BUILD_PLAN_PROGRAMME.md Task 1.5. | `model_registry/registry.yaml` | pytest -q, including tests/unit/engines/assurance/test_model_registry.py | Pete, 5 October 2026 closeout instruction to accept the best options; reviews/2026-10-05-pr164.md |
