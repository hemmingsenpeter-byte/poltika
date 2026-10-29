- Income-tax conformance matrix (Phase C Task 12): `reviews/2026-10-29-income-tax-conformance-matrix.md` maps
  IT-01 to IT-08, the calculation sequence, outcome precedence, the gates and every engine and household reason
  code to the tests that exercise them (57 rows: 24 covered, 24 covered by new tests, 9 partial, 0 gap). The new
  `tests/unit/engines/simulator/test_income_tax_conformance.py` adds 82 non-numeric tests (each exclusion's reason
  code, refusal ordering, version-mismatch ordering, missing-fact names, no amount or candidate value in any
  gated trace, draft-state invariants). Numeric cases are listed for the test-doctrine process, not written; five
  escalations are recorded. Tests and docs only: no calculated amount changed and no protected value was touched.
