# Independent Codex recheck — #161 units, 7 October 2026

## Findings

**No open actionable finding on pinned main.** This independently rechecks the
Claude-authored #161 vocabulary, compatibility and refusal paths. The original
Decimal rounding defect is historical and already fixed by #169; it is not a
new outstanding finding. This is review evidence, not acceptance, author
preflight, an independently sourced deflator rule or a release gate.

## Review inputs

- Reviewer: GPT/Codex; independent cross-model review of Claude's #161 work.
- [PR #161](https://github.com/hemmingsenpeter-byte/poltika/pull/161): final head
  `f4465d6e785cefddd47c063b37452aa8a5d94edf`, base
  `5a8c17e889d7ffe8b5e9921b0e0c4803da1ff968`, squash
  `9e670093ad86445ede546b0acbbc2f110b7f7d9f`.
- Current implementation reviewed at main
  `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`; its only subsequent units source/test
  change is #169, `240da13838857ee0b2e1686a2fba6f7c8b0b4adc` (Codex authored).
  That fix receives supporting current-behaviour verification here, not a
  same-model claim to independently review it.
- Complete original eight-path diff read: `CHANGELOG.md`, `PROGRAMME_STATUS.md`,
  `REPOSITORY_STRUCTURE.md`, `src/poltika/common/errors.py`,
  `src/poltika/semantics/units.py`, `src/poltika/semantics/variables.py`,
  `tests/unit/semantics/__init__.py`, `tests/unit/semantics/test_units.py`.
  Current implementations, all unit tests and callers were also inspected.
- Contracts: retained old Task 2.2 in the archived ADR-0019 programme; current
  Phase B Task 5; REPOSITORY_STRUCTURE.md's semantics boundary and exact-rescale
  contract; precision, source, review and test doctrine. No statutory value or
  rule enters this diff; no external policy engine was inspected.
- Not blind: an initial optional preview included historical diffs/messages.
  The expanded pass then derived the contract from those governing files
  before further current-main diff/rationale reads.

## Independently derived contract

A unit carries dimension, scale and price basis; money also carries currency.
Pure scaling preserves dimension, price basis and currency and keeps exact
stored Decimal digits, or refuses rather than rounding. Unknown units refuse.
A price-basis conversion needs a named sourced rule, deflator variable and
explicit validity period; no empty registry or unimplemented method may produce
a numerical result. Existing `variables.PriceBasis` callers retain the same
enum values and the re-export is the units enum itself. No dictionary/source
meaning is silently changed, and no price conversion is inferred from memory.

## Review and author rationale

The registry is read-only; source models are frozen and reject extra fields.
The existing dictionary unit strings remain mapped by tests. Dimension, basis
and currency guards precede rescaling. Conversion registration validates its
endpoints and date interval; lookup uses `[valid_from, valid_to)`. `convert`
refuses both an absent rule and a present rule lacking implementation. The
shipped conversion registry has no rule or real-price unit. `PriceBasis` stays
available through `variables.py`; callers and serialization retain its values.

The author's stated intent matches that bounded implementation: a vocabulary
and a deliberate conversion stub, not a sourced deflator or new calculator.
No response or code correction was needed in this reviewer pass.

| Discrepancy | Severity / proposed doctrine class | Resolution |
| --- | --- | --- |
| Original #161 ambient-context rounding in `rescale` | Historical CODE_ERROR, already recorded in #169 | Fixed by `240da13`; current long-value/low-precision, finite-input and repeating-decimal regression tests pass. Not reopened |

## Verification and limits

At exact pinned main, using the locked Python 3.12 development environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /private/tmp/poltika-codex-closeout-rechecks-20261007/.venv/bin/python -m pytest -q \
  tests/unit/semantics/test_units.py tests/acceptance/test_v0_3_release_gate.py
```

**34 passed, 8 skipped, two existing deprecation warnings, 18.54s.** This comprises
24 units cases and 10 release-gate passes. The eight release-gate skips are the
seven unbuilt household/population phases and the absent validation-grade field;
no units case skips.

Direct imported Python 3.12 probes confirm exact long-value scaling and the
roundtrip at context precision 6 while leaving the caller's precision unchanged.
Restoring the original multiplication/division function **in memory only** makes
`test_rescale_preserves_all_digits_independent_of_context(6)` fail. Earlier
stdlib-only execution of unaltered AST-extracted functions passed 25 independent
scaling, refusal, registry and date-boundary assertions; the supported-runtime
suite above supersedes that fallback for normal library execution.

`git diff --exit-code 240da13 HEAD -- src/poltika/semantics/units.py
 tests/unit/semantics/test_units.py` is empty. The complete original diff's
whitespace check passes. GitHub readback confirms the head/squash above and all
seven historical PR workflows succeeded, including
[Tests](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37260314557)
and Links. Current-main broad Ruff/mypy/evidence/full-suite evidence is owned
by the root closeout pass; no broad result is invented here. Pydantic models,
compatibility and refusal cases run in the focused supported-runtime suite.

No production or test file was edited. Full deflator implementation, source
resolution for a future conversion and integration into real model callers
remain later tasks. The new review-documentation head still needs its own
preflight, fresh Claude review and required CI before Claude integrates it.
