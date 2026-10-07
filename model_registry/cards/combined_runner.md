# Model card: Combined WFF and AS household runner

Generated from `model_registry/registry.yaml` by
`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.

- **Id:** `combined_runner` (runner)
- **Version:** 0.1.0 (package); policy working_for_families 0.1.0; policy accommodation_supplement 0.1.1. Package version in pyproject.toml. The runner has no version of its own. It runs the WFF and AS policy versions the caller requests.
- **Owner:** Pete (accountable model owner and decisions); Claude Code (implementation); GPT/Codex (sources, interpretation, independent review). Assigned under Pete's 5 October 2026 closeout authority; doctrine/model-governance.md.
- **Validation status:** `spec_validated`
- **Computed dependency label:** `spec_validated` (the least mature model it relies on; not yet attached to runtime outputs)

## Purpose

Runs one household through both module entry points, each for its own period, and compares the shared facts under the Task 28.3 interaction contract. There is no combined total and no income coupling. A shared-fact contradiction makes each non-unsupported component needs_review; existing unsupported outcomes are preserved.

## Methods

Entry points:

- `poltika.scenarios.combined.run_combined_household`

Relies on: `wff_engine`, `as_engine`.

Evidence classes consumed: Rule, Scenario, Model output.

Rule and Scenario through the two engines. Model output: it consumes each engine's component results. Its own results are Model output.

## Validation

Passes hand-calculated interaction cases and nine hand-calculated golden households. Claude Code hand-calculated both sets (the same model that wrote the runner). The Claude Task 34.3 review documents the sole_parent_support_beneficiary_consistent interaction case and re-derived all nine golden households; it does not document a re-derivation of all five interaction cases. The GPT/Codex Task 34.3 review re-derived all five interaction cases and golden households g2, g5, g6, g7 and g9 (review_packets/task_28_5_interaction_cases.md, review_packets/task_29_4_golden_households.md). Its least mature dependency is also spec_validated.

Validation cases:

- interaction_spec_cases: `policy_specs/wff_as_interaction/spec_cases.yaml` (5)
- golden_households: `policy_specs/wff_as_interaction/golden_households.yaml` (9)
- golden_snapshot: `tests/fixtures/golden_results_v0_1.json` (9)

Tests:

- `tests/unit/scenarios/test_combined.py`
- `tests/unit/scenarios/test_interaction_spec_cases.py`
- `tests/unit/scenarios/test_golden_households.py`
- `tests/regression/test_wff_as_interaction_leaks.py`
- `tests/regression/test_golden_result_snapshot.py`

Reviews:

- `reviews/2026-10-05-pr164.md`
- `reviews/2026-09-25-task34-3-claude-fresh-context.md`
- `reviews/2026-09-25-task34-3-codex.md`
- `review_packets/task_28_3_interaction_contract.md`
- `review_packets/task_28_5_interaction_cases.md`
- `review_packets/task_29_4_golden_households.md`

Open items:

- none

## Limitations

- Everything in the WFF and AS entries applies. (`docs/releases/V0_1_LIMITATIONS.md`)
- WFF is annual and AS is weekly. They are never added or converted, so there is no combined total. (`docs/releases/V0_1_LIMITATIONS.md`)
- There is no income coupling between the two policies (AS DEC-003). (`docs/releases/V0_1_LIMITATIONS.md`)
- Only a small set of shared facts is compared. The policies' definitions differ, so a disagreement is escalated and never repaired. (`src/poltika/scenarios/combined.py`)

## Known model risks and failure modes

- The shared-fact comparison is deliberately conservative. A legitimate difference between the two policies' definitions can show as needs_review. (`src/poltika/scenarios/combined.py`)

## Change log

| Date | What changed | Why | Evidence | Validation re-run | Approval |
| --- | --- | --- | --- | --- | --- |
| 2026-09-24 | Task 28.4, the combined runner, aligned with the revised Task 28.3 contract (commits 80b92c7, 7be8026). | Implement the Task 28.3 interaction contract, with Pete's accepted decisions. | `policy_specs/wff_as_interaction/spec_cases.yaml` | unknown (recorded before change records existed) | Pete accepted the Task 28.3 decisions (commit 98d3ef4 message) |
| 2026-09-25 | Structured review reasons (commit f8b4b3a). No calculated amount changed (CHANGELOG.md). | v0.1.5 structured needs_review reasons. | `docs/releases/V0_1_5_GATE.md` | tests/acceptance/test_v0_1_5_release_gate.py (gate row "v0.1 results unchanged") | unknown (recorded before change records existed) |
| 2026-10-05 | Registered in the model registry (Task 1.5). No code change. | BUILD_PLAN_PROGRAMME.md Task 1.5. | `model_registry/registry.yaml` | pytest -q, including tests/unit/engines/assurance/test_model_registry.py | Pete, 5 October 2026 closeout instruction to accept the best options; reviews/2026-10-05-pr164.md |
