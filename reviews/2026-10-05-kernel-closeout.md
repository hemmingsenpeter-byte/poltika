# Kernel closeout review, 5 October 2026

Reviewer: Codex, independent review of the original Claude-authored changes.
This is not the required fresh-context Claude `poltika-reviewer` pass. That pass
remains pending until it actually runs against the stated final commits.

## Expected behavior derived before comparing the code

- Programme Task 2.2 (now the bounded Phase B Task 5 contract) preserves units,
  price basis and currency during pure rescaling, retaining stored precision.
  Different dimensions/bases/currencies and unavailable named rules refuse.
- Task 2.3 represents explicit half-open periods, a seven-day assessment week,
  point-in-time membership with an exclusive upper edge, and the accepted AS
  week-within-WFF-year relation. Annual/weekly amount conversion remains refused.
- ADR-0021 archives planning history without changing policy behavior. Archive
  snapshots must equal their named source commit; active relative links resolve.

## Findings

**U1 — P2 / CODE_ERROR, original #161 squash
`9e670093ad86445ede546b0acbbc2f110b7f7d9f`,
`src/poltika/semantics/units.py:171`.** `rescale` uses the ambient Decimal context,
so it silently rounds an amount with more significant digits than that context.
For `Decimal("12345678901234567890123456789.123")`, converting
`persons_thousand` to `persons` returns
`1.234567890123456789012345679E+31`, rather than the exact
`12345678901234567890123456789123`. Converting back also loses digits.
This contradicts the exact-rescaling contract. No current production caller
imports `rescale`; the original change has not altered existing statutory results.

**U2 — P2 / CODE_ERROR, original #161, `units.py:77`.** The independent
root Codex review identified that an infinite unit scale passed validation;
exact rescaling to it then leaked an `OverflowError`. This PR requires unit
scales to be finite and positive and tests Infinity, negative Infinity and NaN.

Resolution proposed in this PR: use a local context sufficient for a terminating
Decimal quotient and trap `Inexact`; refuse repeating/nonfinite results instead
of silently rounding. Regression cases exercise high precision, a deliberately
small caller context, unchanged caller precision, exact roundtrip, a non-power-of-
ten terminating scale, and explicit refusals. The fix author is Codex; its own
review is author preflight, not independent review of the fix.

**#166, fixed head `a32f10ed0e9f2704cbe251fb2e451779129579f3`: no
P1/P2 finding.** The named relation agrees with the accepted AS specification's
Task 28.3 period contract. Exact start/end edges, wrong type, unknown IDs,
point-in-time membership and unsupported value conversions behave as required.
The conversion registry remains empty and refuses every amount conversion.

**#144, exact squash `2cdadba87ad1dc6712eadfe17452cde19b4e9a04`: no
new actionable finding in the final relative-link fix.** All active Markdown
file targets in this commit's changed files resolve; all five historical
snapshots are byte-identical to their original paths at
`e52f5d35913fbb4b81c7b64c6caf6d446c158759`. The known staged programme dependency
is resolved by the already merged companion PRs #145-#147. P8 confirmation is a
separate owner decision in the session's closeout record; this audit does not
invent its historical acceptance or a reviewer pass after the link fix.

## Checks run

- Original #166 head: `uv run --offline --extra dev pytest -q
  tests/unit/semantics/test_periods.py tests/unit/data/test_boundary.py` —
  17 passed. Ruff passed; strict mypy passed for 82 source files. The uv cache
  was set to the writable `/private/tmp/poltika-closeout-uv`.
- Unit-fix focused tests (using the existing development virtual environment,
  with `PYTHONPATH=src`): 28 passed. Ruff passed; strict mypy passed for
  81 source files. An independent exact-rational probe of 630 value/scale
  combinations under Decimal precisions 2, 6 and 28 confirmed every result
  or refusal against `fractions.Fraction`.
- `git diff --check` on each original squash: passed.
- #144 archive comparison and active changed-file link-target checks: passed.

No statutory values, policy specifications, protected expected values or data
snapshots are changed. The original #161 defect is an engineering precision
error. GitHub CI and the fresh-context reviewer remain distinct merge gates.
