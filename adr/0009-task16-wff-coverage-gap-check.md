# ADR-0009: Task 16 external coverage-gap check performed for WFF — no named-category gap found

**Date:** 2026-09-22
**Status:** accepted

## Context

BUILD_PLAN.md Task 16 ("External coverage-gap check (OpenFisca test
names, strictly after suite completion) — return to primary sources for
any gap found") could only run once WFF's own test suite was complete
(Tasks 13-15). ADR-0004 additionally requires this check to independently
include both OpenFisca Aotearoa and `PolicyEngine/policyengine-nz` as
comparators, not OpenFisca alone.

Per `doctrine/ip-doctrine.md`'s "Compatibility checks" allowance, this
check inspected only structural naming — directory/file *names* at a
pinned commit, via each repository's public GitHub contents API — never
file contents, test logic, or expected values. Pinned per the same
discipline `docs/research/nz_policy_engines_review.md` (§1) already used,
so this record is independently reproducible/verifiable later:

- **OpenFisca Aotearoa**: `digitalaotearoa/openfisca-aotearoa`, commit
  [`9d77ea7`](https://github.com/digitalaotearoa/openfisca-aotearoa/commit/9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb)
  (2025-05-05T21:40:51Z) — the same repository and commit
  `nz_policy_engines_review.md` §1 already inspected and §11 flagged as
  the likely-but-unverified canonical copy among three related GitHub
  organisations; that uncertainty is inherited here, not re-resolved, and
  does not affect this check's conclusion, since the category names are
  what matters, not which org hosts the canonical repo. Directory listed:
  [`openfisca_aotearoa/tests/income_tax/family_scheme/`](https://github.com/digitalaotearoa/openfisca-aotearoa/tree/9d77ea7ce3c45b6292d4b4eaf3566b2fb00e7ceb/openfisca_aotearoa/tests/income_tax/family_scheme) —
  `best_start.yaml`, `eligibility.yaml`, `family_scheme.yaml`,
  `family_tax_credit.yaml`, `in_work_tax_credit.yaml`,
  `minimum_family_tax_credit.yaml`.
- **PolicyEngine NZ**: `PolicyEngine/policyengine-nz`, commit
  [`fbd186b`](https://github.com/PolicyEngine/policyengine-nz/commit/fbd186bd9a40633d5fc106750838b9cae40e71c3)
  (2026-04-28T00:35:48Z) — the same commit `nz_policy_engines_review.md`
  §1 already pinned; HEAD of `main` has not moved since that review.
  Directories listed:
  [`policyengine_nz/tests/policy/baseline/`](https://github.com/PolicyEngine/policyengine-nz/tree/fbd186bd9a40633d5fc106750838b9cae40e71c3/policyengine_nz/tests/policy/baseline) —
  one consolidated `test_working_for_families.yaml`, plus
  [`tests/validation/`](https://github.com/PolicyEngine/policyengine-nz/tree/fbd186bd9a40633d5fc106750838b9cae40e71c3/policyengine_nz/tests/validation)'s
  separate `test_against_treasury.py`;
  [`policyengine_nz/variables/gov/ird/working_for_families/`](https://github.com/PolicyEngine/policyengine-nz/tree/fbd186bd9a40633d5fc106750838b9cae40e71c3/policyengine_nz/variables/gov/ird/working_for_families) —
  `best_start.py`, `family_tax_credit.py`, `in_work_tax_credit.py`; no
  file separately named for minimum family tax credit was present at
  this path.

## Decision

**No named-category gap was found** — every category named by either
comparator's directory/file structure has a corresponding, independently
primary-source-derived category somewhere in WFF's own test suite:
`spec_cases.yaml`, `benchmarks.yaml`, and
`tests/regression/test_known_historical_issues.py` between them name
family tax credit, in-work tax credit, minimum family tax credit, and
Best Start individually; the household eligibility gate (OpenFisca's
separate `eligibility.yaml` category, collapsed in Poltika's schema into
the single `eligibility_facts` input `policy.yaml` already declares — an
existing, reviewed Task 4/10 design decision, not reopened here); and
partnered/combined-income verification (OpenFisca's and PolicyEngine
NZ's `family_scheme` category, and Poltika's own `VerifiedIncome`/
`PartnerStatus` facts).

This finding is deliberately narrower than "Poltika's coverage is as
deep as, or deeper than, either comparator's." A pinned list of
directory/file *names* establishes only that a *named category* exists or
doesn't — it cannot establish how many test cases live inside a file, how
thoroughly each named category is actually exercised, or any other
depth/completeness measure, without reading file contents, which this
check deliberately does not do (per `doctrine/ip-doctrine.md`'s
structural-only allowance and the same hard-stop discipline
`nz_policy_engines_review.md` §11 already established). PolicyEngine
NZ's single consolidated `test_working_for_families.yaml` is recorded
here as a structural fact — a different filename shape from OpenFisca's
per-component split, and from Poltika's own three-file-class split — not
as evidence about its number of test cases or how minimum family tax
credit is or isn't covered inside it. No comparative depth claim is made
about either comparator, and none should be inferred from this record.

## Consequences

- Task 16 is closed for WFF on the narrow "no named-category gap found"
  basis above. It must be repeated independently for Accommodation
  Supplement once AS's own test suite (its Tasks 13-15 equivalents) is
  complete — this ADR does not cover AS.
- No code, test, schema, or doctrine change follows from this ADR.
- No file contents, test logic, or values from either external project
  were read, copied, or recorded anywhere in this repository — only
  directory/file names, at the pinned commits above.
