# Model card: Basic annual income tax engine (draft, gated)

Generated from `model_registry/registry.yaml` by
`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.

- **Id:** `income_tax_engine` (engine)
- **Version:** 0.1.0 (package). Package version in pyproject.toml. The engine has no version of its own. Its policy, policy_specs/income_tax/policy.yaml, is draft_pending_review with policy_version null, so no policy version is declared here.
- **Owner:** Pete (accountable model owner and decisions); Claude Code (implementation); GPT/Codex (sources, interpretation, independent review). Assigned under Pete's 5 October 2026 closeout authority; doctrine/model-governance.md.
- **Validation status:** `not_validated`
- **Computed dependency label:** `not_validated` (the least mature model it relies on; not yet attached to runtime outputs)

## Purpose

Checks one individual's caller-asserted 2026-27 facts against the D11 ordinary salary and wages slice and returns basic annual income tax as unsupported or needs_review. No result is calculated: the policy is a draft, its 2026-27 rates wait on Royal assent (Q16), and the final-output precision method is unresolved (DEC-004). The exact Table 1 band sum is implemented and tested with synthetic parameters only.

## Methods

Entry points:

- `poltika.engines.simulator.income_tax.calculate_income_tax`
- `poltika.engines.simulator.income_tax.run_income_tax_module`

Relies on: no other registered model.

Evidence classes consumed: Scenario.

Scenario: the caller's asserted facts. No Rule is consumed while every parameter is a needs_review candidate; any future result is Model output.

## Validation

Runs all 47 draft spec cases, none with a numeric expectation, against the draft policy (each with its exact reason code and a trace), and reproduces the 17 hand-calculated conditional arithmetic values with the pure band-sum function. There is no approved value, no official benchmark and no calculated output.

Validation cases:

- spec_cases: `policy_specs/income_tax/spec_cases.yaml` (47)

Tests:

- `tests/unit/engines/simulator/test_income_tax.py`
- `tests/unit/engines/simulator/test_income_tax_spec_cases.py`
- `tests/unit/scenarios/test_household_income_tax.py`

Reviews:

- `review_packets/task7_numeric_packet.md`
- `reviews/2026-10-17-pr232.md`
- `review_packets/pr232_household_income_tax_preflight.md`

Open items:

- Q16 / DEC-001, annual-rate authority until Royal assent and a dated source check.
- DEC-004, final-output precision method and an official period-matched benchmark.
- The shared-household mapping for annual taxable income (#232, v0.3 2.3) exists but is not cleared. Its GPT/Codex final-head review is pending. The specification approves no household adapter itself; ADR-0017 and v0.3 2.3 commission this one, subject to that review (R6 (a)).

## Limitations

- Ordinary salary and wages only, whole-year ordinary NZ residents, no deductions or losses, general basic rates, whole-dollar taxable income (Q17). (`policy_specs/income_tax/specification.md`)
- Taxable income is attested by the caller, never derived; PAYE, ACC, credits and terminal tax are separate components and not modelled. (`policy_specs/income_tax/specification.md`)

## Known model risks and failure modes

- Turning the exact band sum into a final amount needs a sourced method; the sum can carry sub-cent values. (`policy_specs/income_tax/decisions/DEC-004-output-precision-and-benchmark.md`)

## Change log

| Date | What changed | Why | Evidence | Validation re-run | Approval |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | Task 7 engine (new-policy PR 3), non-numeric contract only; stacked on the draft values packet | Implement the specification's outcome contract while the value, authority and precision gates stay closed. | `policy_specs/income_tax/spec_cases.yaml` | tests/unit/engines/simulator/test_income_tax.py and test_income_tax_spec_cases.py | Pending. GPT/Codex engine review and Pete's |
| 2026-10-17 | The engine gains a household input relationship through poltika.scenarios.household_mappings: to_income_tax, run_household_income_tax and household_from_income_tax (#232). Engine code unchanged; no parameter, calculated amount or result id changes. | BUILD_PLAN_v0_3.md 2.3 and ADR-0017 (shared household model). | `tests/unit/scenarios/test_household_income_tax.py` | tests/unit/scenarios/test_household_income_tax.py, tests/unit/policy/test_fact_catalogs.py and tests/unit/engines/assurance/test_model_registry.py | Pending. GPT/Codex final-head mapping review (changes requested at f31a8d3, reviews/2026-10-17-pr232.md), then ADR-0020 acceptance. |
