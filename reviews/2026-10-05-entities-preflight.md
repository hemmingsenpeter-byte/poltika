# Entities and identifiers author preflight

Date: 5 October 2026. Reviewer/finisher: Codex. This is author preflight,
not an independent cross-model review of the final change.

The original uncommitted Claude-authored work is retained untouched in
`/private/tmp/poltika-entities` at base `ab56f4c`. The candidate is recovered into
its own worktree. Restacked on 6 October 2026 onto main `c72c409` (which contains
the merged #166, periods); the earlier base `a32f10e` is superseded. `periods.py` and
`test_periods.py` are main's, and `git diff origin/main` on both is empty.
I knew the recovered implementation's rationale when conducting this preflight.

## Expected contract

Programme Task 2.4, retained under current Phase B Task 5, and ADR-0017 section 1
require explicit person/family/household/firm/sector/Crown identities, with New
Zealand also needed by Task 2.1's entity vocabulary. Do not invent an external
identifier scheme or infer a family ID from its one-household association.
Existing household ID shape/uniqueness scope and person uniqueness scope come
from `semantics/population.py`. Other unavailable schemes refuse with reasons.
Fixed Crown/New Zealand IDs are reversible engineering choices, not statutory
or external identifiers. Geography remains explicit text until Task 2.5.

## Finding and correction

**E1 — P2 / CODE_ERROR:** the recovered singleton regexes used `$`, which
accepts a final newline in Python. `validate_identifier("crown_id", "crown\n")`
incorrectly returned a second value despite a one-fixed-ID contract. Change only
the singleton regex end anchors to `\Z`; test rejection for both singleton IDs.
The household scheme deliberately matches its existing population validator,
including the established regex behavior, to preserve that current contract.

## Verification

With `PYTHONPATH=src` and the existing development virtual environment:

- `python -m pytest -q tests/unit/semantics tests/unit/data/test_boundary.py`:
  78 passed on the restacked head (the earlier 67 predates the #166 fixes).
- `ruff check src tests`: passed.
- `mypy --strict src`: 83 source files, passed.
- `git diff --check`: passed.

Real generated household IDs agree with the existing population validator.
Unassigned person/family/firm/sector schemes refuse every value. Unknown scheme
and entity IDs refuse. Registries are read-only; models are frozen and reject
extra fields. No policy rules, amounts, protected expected values, raw snapshots,
production caller paths or existing household validators change.

A fresh-context final-head `poltika-reviewer` pass and final-head green CI remain
merge gates. Do not treat this author preflight as either of those checks.
