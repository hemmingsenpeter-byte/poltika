# Review Packet: Working for Families — Task 17 — 22 September 2026

Independent adversarial review (fresh-context, no implementer explanation)
of the complete WFF vertical slice, per `BUILD_PLAN.md` Task 17. This
covers Tasks 11-16 as one assembled result — the calculator, all three test
classes, and the external coverage-gap check — not one incremental PR.

Reviewer: read only the "Review inputs" section below before deriving
expected behaviour independently. The remaining sections of this packet
are intentionally left blank for the reviewer to complete, per
`review_packets/README.md`: no author interpretation, rationale, or
proposed expected result is included here.

## Review inputs

### PRs in scope (Tasks 11-16, all merged to `main`)

| PR | Task | Title |
|---|---|---|
| [#13](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/13) | 11 | Parameter loader |
| [#14](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/14) | 12 | Pure `calculate_wff()` function |
| [#15](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/15) | 13 | Independently hand-calculated spec tests |
| [#16](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/16) | 14 | Benchmark tests against IRD worked examples |
| [#17](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/17) | 15 | Regression tests for known historical issues |
| [#18](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/18) | 16 | External coverage-gap check (ADR-0009) |

Prior context, for the same slice: [#9](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/9), [#10](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/10), [#11](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/11), [#12](https://github.com/hemmingsenpeter-byte/poltika-0.1v/pull/12) (Task 10 source audit and specification approval, precedes Task 11).

### Primary sources

Full inventory: `policy_specs/working_for_families/sources.yaml`. Source ids
cited across the spec and calculator:

- `wff-income-tax-act` — Income Tax Act 2007, Part M (subparts MB-MG)
- `wff-tax-credit-order-2025` — Income Tax (Tax Credit) Order 2025
- `wff-budget-measures-2025` — Taxation (Budget Measures) Act 2025
- `wff-tax-administration-act` — Tax Administration Act 1994, s 80KW
- `wff-budget-measures-2026` — Taxation (Budget Measures) Act 2026
- `wff-iwtc-increase-act-2026` — Taxation (Annual Rates for 2025-26, Compliance Simplification, and Remedial Measures) Act 2026
- `wff-ird-interpretation-2026` — IS 26/12
- `wff-ird-family-income`, `wff-ird-other-income`, `wff-ird-rates-2026`,
  `wff-ird-family-tax-credit`, `wff-ird-in-work-tax-credit`,
  `wff-ird-temporary-increase`, `wff-ird-minimum-family-tax-credit`,
  `wff-ird-best-start`, `wff-ird-government-payments`,
  `wff-ird-shared-care` — IRD guidance and worked examples

### Specification and policy paths

- `policy_specs/working_for_families/specification.md` — see in particular
  "Statutory structure" (line 10), "Approved Task 10 scoped calculation
  contract" (line 104), "Task 12 implementation note" (line 415), "Task 13
  implementation note" (line 524), "Task 14 implementation note" (line 604)
- `policy_specs/working_for_families/policy.yaml` — parameters, components,
  `assessment.unsupported`
- `policy_specs/working_for_families/sources.yaml`
- `policy_specs/working_for_families/spec_cases.yaml` — 23 hand-calculated
  spec cases (Task 13)
- `policy_specs/working_for_families/benchmarks.yaml` — 9 IRD-sourced
  benchmark cases (Task 14)
- `adr/0009-task16-wff-coverage-gap-check.md` — Task 16 result

### Code paths

- `src/poltika/policy/loader.py` — Task 11 parameter loader
- `src/poltika/engines/simulator/wff.py` — Task 12 `calculate_wff()`

### Test paths

- `tests/unit/policy/test_loader_against_wff.py`
- `tests/unit/engines/simulator/test_wff.py`
- `tests/unit/engines/simulator/test_wff_spec_cases.py`
- `tests/unit/engines/simulator/test_wff_benchmarks.py`
- `tests/regression/test_known_historical_issues.py`
- `tests/conftest.py` — shared fixtures/helpers

### Test command and output

```
$ uv run pytest -q
117 passed in 3.55s

$ uv run ruff check src tests
All checks passed!

$ uv run mypy --strict src
Success: no issues found in 11 source files
```

Verified 22 September 2026 against `main` at commit `2d3ed00`.

## Independent review

(reviewer completes — derive expected behaviour from sources and spec
before reading any implementer explanation)

### Independently derived expected behaviour

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| | CODE_ERROR / TEST_ERROR / SPEC_ERROR / SOURCE_CONFLICT / INTERPRETATION_AMBIGUITY / MISSING_SOURCE / ARCHITECTURE_ISSUE / REVIEWER_ERROR | |

## Author response

(add assumptions and rationale only after the independent review is
recorded)

## Resolution

(what happened to each discrepancy — fixed, escalated, recorded as a Pete
decision artifact, etc.)
