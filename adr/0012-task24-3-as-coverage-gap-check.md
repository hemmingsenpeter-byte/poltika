# ADR-0012: Task 24.3 external coverage-gap check for Accommodation Supplement

**Date:** 2026-09-23
**Status:** proposed

## Context

BUILD_PLAN.md Task 24.3 repeats WFF Task 16's post-suite external
coverage-gap check for Accommodation Supplement. The timing requirement in
`doctrine/ip-doctrine.md` and ADR-0004 is satisfied: AS's spec/benchmark
suite (PR #27) and historical regressions (PR #28) are merged to `main`.
This is the ordinary post-suite inspection window, not ADR-0004's earlier
one-off sequencing deviation.

The inspection followed ADR-0009's corrected method. Only repository
directory and file names were listed through GitHub's public commit/tree
metadata at pinned commits. No external file body, test logic, assertion,
formula, rate, threshold, or calculated output was read or used as Poltika
policy authority.

Pinned comparators inspected:

- **OpenFisca Aotearoa:** `digitalaotearoa/openfisca-aotearoa`, commit
  [`9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb`](https://github.com/digitalaotearoa/openfisca-aotearoa/commit/9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb)
  (2025-05-05T21:40:51Z). AS test directory:
  [`openfisca_aotearoa/tests/social_security/accommodation_supplement/`](https://github.com/digitalaotearoa/openfisca-aotearoa/tree/9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb/openfisca_aotearoa/tests/social_security/accommodation_supplement).
  Named files beneath its `1964/` and `2018/` directories were
  `entitled.yaml`, `_benefit_me.yaml`, `accommodation_supplement.yaml`,
  `area.yaml`, `assets.yaml`, `base.yaml`, `beneficiary.yaml`, `costs.yaml`,
  `cutout.yaml`, `exclusion.yaml`, `rate.yaml`, `rebate.yaml`, and
  `situation.yaml`. Corresponding variable filenames were `area.py`,
  `assets.py`, `base.py`, `beneficiary.py`, `costs.py`, `cutout.py`,
  `entitled.py`, `exclusion.py`, `rate.py`, `rebate.py`, and `situation.py`.
- **PolicyEngine NZ:** `PolicyEngine/policyengine-nz`, commit
  [`fbd186bd9a40633d5fc106750838b9cae40e71c3`](https://github.com/PolicyEngine/policyengine-nz/commit/fbd186bd9a40633d5fc106750838b9cae40e71c3)
  (2026-04-28T00:35:48Z). The pinned tree had no AS-named test or variable
  file. Its AS-named directory was the parameter path
  [`policyengine_nz/parameters/gov/msd/accommodation_supplement/`](https://github.com/PolicyEngine/policyengine-nz/tree/fbd186bd9a40633d5fc106750838b9cae40e71c3/policyengine_nz/parameters/gov/msd/accommodation_supplement),
  containing `income_test.yaml` and `payment_rates.yaml`. This absence of
  AS-named tests/variables is recorded only as a structural observation;
  nothing is inferred about unlabelled or indirect coverage.

## Named-category comparison

| Comparator name | Existing Poltika AS suite category | Result |
| --- | --- | --- |
| `accommodation_supplement`, `entitled`, `exclusion` | Whole-calculation cases plus supported, unsupported, and needs-review household gates in `spec_cases.yaml` and `test_accommodation_supplement.py` | Named category represented |
| `area` | Area-cap binding, unverified-area handling, and the one-child cl 2 boundary | Named category represented |
| `assets` | Asset ceiling, exempt-asset outcomes, asset imputation, and r 15/category-cutoff regressions | Named category represented |
| `base` | Entry-threshold/base-rate arithmetic and the real undeclared-base-rate `needs_review` regression | Named category represented; actual dated base rates remain the already-recorded Task 25 schema/source work |
| `beneficiary` | Supported benefit categories, non-beneficiary income reduction, pension/mixed-benefit exclusions, and beneficiary no-income-test behavior | Named category represented |
| `costs` | Entry-threshold, cost-based amount, rent/board benchmark, homeowner and non-plain-cost scope boundaries | Named category represented |
| `rate` | 70% calculation, area caps, income reduction, zero floor, and final rounding | Named category represented |
| PolicyEngine `income_test` | Non-beneficiary income reduction, missing income/input handling, DEC-001 exact-excess regression | Named category represented |
| PolicyEngine `payment_rates` | Area caps, entry/base-rate handling, benchmarks, and the known undeclared-rate guard | Named category represented |
| `_benefit_me`, `cutout`, `rebate`, `situation` | No reliable one-to-one mapping can be derived from these names alone | **Candidate only:** Pete may decide whether primary-source-led follow-up is warranted; not asserted as a gap |

## Decision

**No confirmed named-category gap was found.** Every unambiguous category
name in the pinned external paths maps to a category already named or
exercised by Poltika's AS spec cases, benchmarks, regressions, or calculator
unit tests. The four opaque OpenFisca names above are recorded as candidates,
not treated as missing coverage: determining their meanings would require
reading external implementation/test bodies, which this clean-room check
explicitly forbids.

This conclusion is deliberately no broader than ADR-0009's WFF conclusion.
Path names cannot establish comparative test depth, correctness, or policy
meaning. No claim is made that Poltika's suite is as deep as either external
project's suite.

## Consequences

- Task 24.3 is complete on the narrow name-only basis above, subject to
  independent review and Pete's acceptance of this proposed ADR.
- No code, test, policy specification, schema, source, or doctrine change is
  required by this check. No implementation work was skipped.
- No external contents, logic, values, or formulas entered Poltika's source
  or provenance chain.
- Task 24.4 remains separate and must be performed by the model that did not
  implement Tasks 24.1-24.3. This task does not begin that review.
