# Model card: Population runner (static microsimulation)

Generated from `model_registry/registry.yaml` by
`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.

- **Id:** `population_runner` (runner)
- **Version:** 0.1.0. Package version in pyproject.toml. The runner has no version of its own. Each run has a run_id that hashes the population, the reform, the code identity and the policy files (src/poltika/scenarios/microsim/runner.py).
- **Owner:** Pete (accountable model owner and decisions); Claude Code (implementation); GPT/Codex (sources, interpretation, independent review). Assigned under Pete's 5 October 2026 closeout authority; doctrine/model-governance.md.
- **Validation status:** `spec_validated`
- **Computed dependency label:** `spec_validated` (the least mature model it relies on; not yet attached to runtime outputs)

## Purpose

Runs every household of a population twice through the combined runner, under the approved parameters and under a reform's copy, and keeps each component's outcome and delta. There is no other calculation path. Today's population is the synthetic development population.

## Methods

Entry points:

- `poltika.scenarios.microsim.runner.run_population`

Relies on: `combined_runner`.

Evidence classes consumed: Rule, Scenario, Assumption, Fact, Estimate, Model output.

Rule and Scenario through the combined runner. Reform overrides marked scenario_assumption are Scenario. The population's listed assumptions are Assumption. The published shares the generator draws on are Fact or Estimate by dataset (epistemic-constitution decisions 2 and 4). The household records are a Scenario, always labelled synthetic. Results are Model output.

## Validation

The runner's arithmetic passes hand-calculated population cases (the author's, and GPT/Codex's fixed cases). That validates the mechanics on small populations only. The population is synthetic, and the cross-validation against published figures shows scope gaps, none tuned away. There is no empirical validation of a population result.

Validation cases:

- hand_calculated_population_cases: `tests/acceptance/test_v0_2_hand_calculated.py` (unknown)
- independent_population_cases: `tests/acceptance/test_v0_2_independent_population_cases.py` (unknown)
- cross_validation_report: `docs/releases/V0_2_CROSS_VALIDATION.md` (unknown)
- golden_snapshot: `tests/fixtures/golden_results_v0_1.json` (9)

Tests:

- `tests/unit/scenarios/microsim/test_runner.py`
- `tests/unit/scenarios/microsim/test_analysis.py`
- `tests/unit/scenarios/microsim/test_weighting.py`
- `tests/unit/scenarios/microsim/test_crossval.py`
- `tests/acceptance/test_v0_2_release_gate.py`

Reviews:

- `reviews/2026-09-27-pr117.md`
- `reviews/2026-09-27-v0-2-fresh-same-model-check.md`
- `review_packets/review_queue.md`

Open items:

- No empirical national-population validation is claimed. The review queue records #111, #113 and #114 cleared on Pete's 27 September confirmation; V0_2_LIMITATIONS.md's historical pending-review text predates that clearance.

## Limitations

- Every result is for the synthetic development population, not an estimate for New Zealand. (`docs/releases/V0_2_LIMITATIONS.md`)
- Household type, income, tenure, housing cost, region and area are drawn independently, so real correlations are lost. Income is two coarse uniform bands. (`docs/releases/V0_2_LIMITATIONS.md`)
- Everyone is an in-work non-beneficiary (assumption A6). No beneficiary or main-benefit interaction is exercised. (`docs/releases/V0_2_LIMITATIONS.md`)
- Four household types only. The population represents 1.45 million households, not 2.03 million. (`docs/releases/V0_2_LIMITATIONS.md`)
- Static and full take-up. No behavioural response, take-up rate or timing. (`docs/releases/V0_2_LIMITATIONS.md`)
- The 2026-27 in-work tax credit and minimum family tax credit are needs_review for every household, so there is no WFF total. (`docs/releases/V0_2_LIMITATIONS.md`)
- No annual Accommodation Supplement figure and no combined effective marginal tax rate. (`docs/releases/V0_2_LIMITATIONS.md`)
- Deciles rank by gross household income, not equivalised income. (`docs/releases/V0_2_LIMITATIONS.md`)

## Known model risks and failure modes

- Cross-validation reaches about three-quarters of published family tax credit families, a fifth of AS recipients and an eighth of Best Start families. A reader could take the modelled figure for a national estimate. (`docs/releases/V0_2_CROSS_VALIDATION.md`)
- Family tax credit cost is sensitive to where families sit relative to the abatement threshold, and so to the coarse income bands. (`docs/releases/V0_2_LIMITATIONS.md`)

## Change log

| Date | What changed | Why | Evidence | Validation re-run | Approval |
| --- | --- | --- | --- | --- | --- |
| 2026-09-26 | v0.2 Phase 7, the population runner, run identity and spec cache (commit b52e909). | BUILD_PLAN_v0_2.md static microsimulation. | `tests/unit/scenarios/microsim/test_runner.py` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-09-26 | Task 9.1, verified population explanations (commit e6bda2d). | BUILD_PLAN_v0_2.md Task 9.1. | `tests/unit/scenarios/microsim/test_explain.py` | unknown (recorded before change records existed) | unknown (recorded before change records existed) |
| 2026-10-05 | Registered in the model registry (Task 1.5). No code change. | BUILD_PLAN_PROGRAMME.md Task 1.5. | `model_registry/registry.yaml` | pytest -q, including tests/unit/engines/assurance/test_model_registry.py | Pete, 5 October 2026 closeout instruction to accept the best options; reviews/2026-10-05-pr164.md |
