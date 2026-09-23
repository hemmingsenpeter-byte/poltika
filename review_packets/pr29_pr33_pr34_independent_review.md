# Review Packet: AS Tasks 24.7, 24.8, and 25/26 — 2026-09-23

## Review inputs

- PR/diff: PR #34 at `0666be4ade4642ddc4f275a674e52e3fa990470f`; PR #29 at `0186766387673251302568dff49dd2f467043c11`; PR #33 at `7b7856f2b91c8a679a4f2689e5531f4a66ec46ed`.
- Primary sources and source-map paths: no new statutory values were introduced. Reviewed the accepted AS contract in `policy_specs/accommodation_supplement/specification.md` and the intentionally undeclared-rate note in `policy.yaml`.
- Specification paths and clauses: AS scoped calculation step 3 and Task 25 note; WFF Task 20 precedent in `wff.py`; WFF Task 21 API precedent in `poltika/api/wff.py`; BUILD_PLAN.md Tasks 20-21 and 24.7-26.
- Test commands: `uv run --extra dev pytest -q`; `uv run --extra dev ruff check src tests`; `uv run --extra dev mypy --strict src`; `git diff --check`.
- Exact-head output: PR #34: 202 passed, 1 deselected; PR #29: 195 passed, 1 deselected; PR #33: 211 passed, 1 deselected. Ruff and strict mypy clean for all three.
- Combined-state output: current `main` + PR #34 + PR #33: 211 passed, 1 deselected; Ruff and strict mypy clean.

## Independent review

### Independently derived expected behaviour

1. The AS base-rate key must distinguish both claimant category and the already-verified household category. Computing the category before both the base-rate and area-cap lookups must not bypass the household gate. The real policy must remain free of unverified base-rate values, and the schema must continue accepting IDs without a model revision.
2. `run_as_module()` must require an explicit policy version, reject a foreign policy ID and an out-of-reference-period date, and reject any declared parameter whose selected interval does not span the complete reference period. Every calculator lookup must either pass through `_param_value()` or be guarded from an undeclared-ID `KeyError`.
3. The AS API must use the internally resolved policy directory, validate malformed input as 4xx, preserve generic 500 responses without path leakage, fail startup when either policy directory is absent, and serialize calculated Decimal values as JSON strings.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| PR #33 does not lock fractional `Decimal` response serialization into its test suite. | TEST_ERROR (low) | A direct adversarial probe replacing `run_as_module()` with `ComponentResult(outcome="calculated", value=Decimal("123.4567"))` returned JSON string `"123.4567"`, so current code is correct. Add a route-level regression so the claimed API contract cannot silently drift while the real policy remains unable to produce `calculated`. |
| PR #33's path-leak test names `InvalidSourceCatalogError` but triggers `UnsupportedSchemaVersionError`, so it does not directly exercise the path-bearing exception cited by the test. | TEST_ERROR (low) | A direct probe using a valid schema with a missing source catalog returned the fixed generic 500 detail and did not expose the temporary directory or catalog name. Current handler code is correct; change/add the regression to exercise the actual path-bearing error. |

No CODE_ERROR, SPEC_ERROR, SOURCE_CONFLICT, INTERPRETATION_AMBIGUITY, MISSING_SOURCE, or ARCHITECTURE_ISSUE was found.

### PR-specific conclusions

- **PR #34: clean.** `_base_rate_parameter_id()` includes both dimensions; the category is computed only after the household gate has verified its inputs and is reused unchanged for the area cap. `as_parameters_for_case()` invokes the same category/id helpers as production. The split regression constructs one-child and two-child parameter sets with distinct compound IDs. `ParameterSpec.id` remains a free-form `str`. The `policy.yaml` diff changes comments only; no numeric value was added or changed.
- **PR #29: clean.** Both interval directions and policy/date identity checks match the accepted WFF precedent. Every calculator parameter lookup goes through `_param_value()`, so the deliberate missing-required-ID omission does not expose a `KeyError`. A direct combined-state probe declared `as_base_rate_jobseeker_support_single_no_dependent_children` with an interval ending before the reference period and correctly returned `needs_review` with the full-period reason. The duplicate `policy.yaml` parse is a pre-existing, non-blocking performance nit shared with WFF.
- **PR #33: code clean, two low-severity TEST_ERROR findings above.** Malformed bodies return 422, the real ordinary request returns `needs_review`, the real asset-ceiling request returns `unsupported`, startup checks AS, and direct adversarial probes confirmed string Decimal serialization and generic handling of an actual path-bearing loader error.

## Author response

Pending.

## Resolution

Pending. PR #34 may proceed on this review. PR #29 is already merged and no corrective action is required. PR #33 should add the two focused regressions before acceptance.
