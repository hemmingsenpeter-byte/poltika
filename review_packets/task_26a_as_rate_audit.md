# Review packet: Task 26a rate-source audit

Author: GPT/Codex. Base revision: `18e1ca5`.
Status: source-research handoff; no runtime values or code changed.

## Independent reviewer inputs

- BUILD_PLAN.md Tasks 26a.1-26a.4, approved AS scoped specification.
- Official dated Act and Regulations URLs and provision locators in
  `sources.yaml`'s `task_26a_check` entries.
- MSD tables: the four `as-msd-*-rates-2026` entry-threshold sources,
  `as-msd-rates-2026`, `as-msd-income-2026`, and the main Jobseeker table.
- Income Tax (Tax Credit) Order 2025 clauses 2 and 4(1), (3), and the
  April Act's Income Test 3 and Schedule 4 Part 1 ordinary household rates.
  Recalculate the exact-expression diagnostics independently; they are
  not approved values or payment-prevention thresholds.
- Inspect `_household_category`, `_base_rate_parameter_id`, and the income
  level lookup in `src/poltika/engines/simulator/accommodation_supplement.py`.
- Current `policy.yaml`, `spec_cases.yaml`, `benchmarks.yaml`; distinguish
  real parameters from conditional arithmetic assumptions.
- Derive expected selection and precision from these inputs before reading
  `docs/research/task_26a_as_rate_audit.md` (the author's conclusions).

## Review record

Independent Claude review pending. Author findings do not constitute
independent acceptance. Pete confirms classifications and any decision.
No BUILD_PLAN.md edit is included while PR #42 owns its status update.

## Validation record

- `git diff --check`: passed.
- Source YAML parsing, unique source IDs, policy schema and all parameter
  source references: passed.
- `env PYTHONPATH=src <main-venv>/bin/python -m pytest -q`: 249 passed,
  1 installed-artifact test deselected; existing two deprecation warnings.
- Direct selector diagnostic on `18e1ca5`: reproduced both household
  collisions for Jobseeker, Supported Living and non-beneficiary.
- Dated regulation 17-19 text compared with September text: only link/
  text segmentation differences observed, no substantive rule difference.
- No implementation or protected fixture change; installed-artifact,
  Ruff and mypy are not rerun for this documentation-only slice.
- Follow-up precision evidence: directly fetched the official 2025 Order;
  checked commencement and eldest-child amount; used Python's exact
  `fractions.Fraction` arithmetic for the parent expression and continuous
  income diagnostics. Re-ran YAML/reference validation and diff checking.
