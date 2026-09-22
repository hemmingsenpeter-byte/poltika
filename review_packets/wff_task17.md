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

For the approved 2026-27 full-year branch, first establish one eligible,
stable household and the absence of the s 80KW extra-instalment case. The
scenario must supply documented subpart-MB family-scheme income for the whole
relationship period; MFTC additionally requires an independently verified
ME 3 net-family-scheme-income derivation and 52 qualifying full-time-earner
weeks. The Act's ME 3 adjusted-income item itself starts with family-scheme
income. A missing required amount is `needs_review`, never a zero or an
apparently complete annual entitlement (approved specification, lines
104-218 and 250-290; Income Tax Act 2007, ss ME 1 and ME 3, official Act
version cited in `sources.yaml`).

FTC uses the eldest/additional-child amounts and complete-dollar income
excess; MD 2 passes any abatement remaining after FTC to IWTC. MFTC tops up
verified net income independently of that abatement. Best Start's numeric
branch is limited to one supported-cohort child. Annual arithmetic retains
exact decimals, and no total is reported while a component is unresolved.
The temporary in-work base stays `needs_review` until an official Order check
covers the entire modelled interval. Parameter selection must cover the
*complete assessment period*, not merely a date within it (specification,
scoped calculation sequence, step 1).

I compared those expectations with `loader.py`, `wff.py`, all three fixture
classes, and ADR-0009. The 117 tests, Ruff, and strict mypy pass locally on
22 September 2026. This pass did not independently re-fetch every statutory
provision or every IRD worked example; it relies on the approved source map
for those previously reviewed claims. No new conclusion is drawn from
external-engine code or test logic.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| MFTC can calculate with `family_scheme_income=None` | Proposed CODE_ERROR / TEST_ERROR | `_minimum_family_tax_credit()` in `src/poltika/engines/simulator/wff.py` checks ME 3 attestation and the net amount, but never requires the scenario's separate family-scheme-income input. Reproduced with the real approved WFF parameter set: a verified single-parent scenario with net income 30,000 and `family_scheme_income=None` returns MFTC `calculated: 6,604` while FTC is unresolved. The approved supported-domain paragraph requires a documented family-scheme-income amount for the whole relationship period and *separately* verified net amount for MFTC. Add missing-family-scheme-income and missing-partner-amount tests for MFTC; resolve the contract discrepancy before calling a numeric MFTC result in-scope. This is a scoped-input finding, not a claim that the statutory MFTC formula directly subtracts the separate input. |
| Full-year calculation accepts only point-date parameter resolution | Proposed ARCHITECTURE_ISSUE / CODE_ERROR | `load_policy_parameters()` resolves each row at one `modelled_date`; `calculate_wff()` has no assessment interval and does not validate `parameters.modelled_date`, policy identity/version, or complete-year parameter coverage. The approved sequence explicitly requires selecting law and parameter intervals for the complete assessment period. Current WFF approved numeric rows happen to span 2026-27 and the temporary IWTC base remains gated, so this is not evidence of a wrong current figure. But a later mid-year effective change, or a mismatched parameter set passed by Task 20 integration, could yield an unconditional annual amount from a single-date rate. Add an interval/policy binding at the integration boundary or make the calculator validate it; test a split interval and a mismatched parameter set before exposing annual API results. |

## Author response

Independent review recorded by GPT/Codex 22 September 2026 (`be24947`),
two proposed discrepancies. Both independently re-verified before this
response, per `CLAUDE.md`'s "never trust a review claim blindly."

**1. MFTC input gap (reviewer-proposed CODE_ERROR / TEST_ERROR) —
confirmed.** Fetched the operative ME 3 text directly
(legislation.govt.nz, browser user-agent, since a bare fetch still 403s;
checked 2026-09-22): "adjusted income is— (i) the amount of **the
person's family scheme income** for the tax year ... attributable to the
number of weeks in which the person is a full-time earner, adjusted to an
annualised amount..." Net family scheme income is legally *derived from*
family scheme income, not an independently suppliable figure. The
accepted Task 10.4 contract text (specification.md, "Approved Task 10
scoped calculation contract") lists "a separately verified
family-scheme-income input" as part of the whole accepted v0.1 domain
boundary, not scoped away from MFTC specifically. In code,
`_minimum_family_tax_credit()` (`wff.py` lines 579-618) checks
`net_family_scheme_income_me3_attested` and `net_family_scheme_income`
but never checks `scenario.family_scheme_income is not None`, unlike
`_family_tax_credit()` and `_best_start()`, which both gate on it. Not
hypothetical: `benchmarks.yaml`'s three already-approved MFTC cases
(`ird_mftc_jeremy_salary_only`, `ird_mftc_casey_self_employed_plus_salary`,
`ird_mftc_casey_zero_over_income_limit`) currently supply
`family_scheme_income: null` and still resolve to `calculated`.

Proposed classification: **CODE_ERROR** for `wff.py`'s missing gate, plus
a linked **TEST_ERROR** for the three benchmark cases, which will need
`family_scheme_income` supplied (or an explicit documented reason it's
absent) once the gate exists. Not an INTERPRETATION_AMBIGUITY -- the
statute and the already-accepted specification text agree.

**2. Full-year rate binding (reviewer-proposed ARCHITECTURE_ISSUE /
CODE_ERROR) -- confirmed, latent not live.** `_resolve_parameter()`
(`loader.py` lines 205-247) matches whichever single interval covers
`modelled_date` and returns it as `resolved`, with no check that the
interval spans the full assessment/reference period the calculator's
annual formulas assume. specification.md's accepted contract (calculation
sequence, step 1) requires exactly this ("Select the law and parameter
interval for the complete assessment period... A point-in-time Order
check cannot verify a future full-year rate"), but it is currently
enforced only for `in_work_base` via its `review_status` gate, not
structurally for any parameter via interval coverage. No wrong value
results today: every approved `policy.yaml` parameter's current interval
(2026-04-01 to 2027-04-01) already spans the full 2026-27 reference
period exactly.

Proposed classification: **ARCHITECTURE_ISSUE** -- a genuine design gap,
not a present-day wrong output under the currently approved parameter
set, but needing a structural guard before Task 20/21 integration, where
a mid-year or mismatched parameter interval could otherwise be silently
treated as a full-year result.

Requesting Pete's confirmation of both classifications (per the Roles
section, Pete confirms discrepancy classification) before proceeding to
fix.

## Resolution

Pending Pete's classification confirmation.
