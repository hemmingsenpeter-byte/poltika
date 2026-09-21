# ADR-0009: Task 16 external coverage-gap check performed for WFF — no gap found

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
check inspected only structural naming (test/variable file and directory
names in each project's public repository, at the current commit), never
file contents, test logic, or expected values:

- OpenFisca Aotearoa (`digitalaotearoa/openfisca-aotearoa`, the same
  repository `docs/research/nz_policy_engines_review.md` §11 already
  flagged as the likely-but-unverified canonical copy among three
  related GitHub organisations -- that uncertainty is inherited here, not
  re-resolved, and does not affect this check's conclusion since the
  category names are what matters, not which org hosts the canonical
  repo),
  `openfisca_aotearoa/tests/income_tax/family_scheme/`: `best_start.yaml`,
  `eligibility.yaml`, `family_scheme.yaml`, `family_tax_credit.yaml`,
  `in_work_tax_credit.yaml`, `minimum_family_tax_credit.yaml`.
- PolicyEngine NZ (`PolicyEngine/policyengine-nz`),
  `policyengine_nz/tests/policy/baseline/test_working_for_families.yaml`
  (one consolidated file, plus a separate `tests/validation/
  test_against_treasury.py`); `policyengine_nz/variables/gov/ird/
  working_for_families/`: `best_start.py`, `family_tax_credit.py`,
  `in_work_tax_credit.py` — no separate minimum-family-tax-credit variable
  file was found at this level, a structural observation about that
  project, not a finding about Poltika.

## Decision

No genuine scenario-category gap was found. Every named category from
both comparators maps onto WFF coverage Poltika already has in depth,
independently derived from primary sources across Tasks 12-15:
`spec_cases.yaml` (23 cases), `benchmarks.yaml` (9 cases, all four
components), and `tests/regression/test_known_historical_issues.py` (9
cases) together already exercise family tax credit, in-work tax credit,
minimum family tax credit, and Best Start individually; the household
eligibility gate (OpenFisca's separate `eligibility.yaml` category,
collapsed in Poltika's schema into the single `eligibility_facts` input
`policy.yaml` already declares — an existing, reviewed Task 4/10 design
decision, not reopened here); and partnered/combined-income verification
(OpenFisca and PolicyEngine NZ's `family_scheme` category). No new test,
schema change, or primary-source follow-up is required by this check.

This is a legitimate clean result, not a shortcut: WFF's suite already
covers every component and every known exclusion trigger (MC 6(a)/(b)/(c),
MD 14/15, ME 2(2)-(4), MG 4, s 80KW, shared care) traced to primary
sources across Tasks 12-15's review cycles, several of which are *more*
granular than either external project's own public structure (e.g.
PolicyEngine NZ's apparent absence of a separately named minimum-family-
tax-credit variable file).

## Consequences

- Task 16 is closed for WFF. It must be repeated independently for
  Accommodation Supplement once AS's own test suite (its Tasks 13-15
  equivalents) is complete — this ADR does not cover AS.
- No code, test, schema, or doctrine change follows from this ADR.
- No file contents, test logic, or values from either external project
  were read, copied, or recorded anywhere in this repository — only
  directory/file names, consistent with `doctrine/ip-doctrine.md` and the
  same hard-stop discipline `docs/research/nz_policy_engines_review.md`
  already established (§11: "the hard stop rule for anything that would
  require close implementation study").
