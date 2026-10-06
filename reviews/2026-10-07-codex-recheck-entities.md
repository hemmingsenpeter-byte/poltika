# Independent Codex re-check — #171 entities

## Findings

No actionable finding from the complete merged entity scope. Focused tests
and independent runtime probes passed; Claude-authored entity changes are
eligible for bounded independent clearance at the named merged snapshot. This review covers Claude's entity draft
and restack, not independent acceptance of Codex's recovery/singleton fixes.

## Review inputs

- Reviewer: GPT/Codex, 7 October 2026; independent other-model review of
  Claude-authored changes, with commit-specific mixed-authorship coverage.
- PR: [#171](https://github.com/hemmingsenpeter-byte/poltika/pull/171).
- Merged scope: `b176ddc72eefd1811a0b8317d812dd389e6f3ae7`, final PR head
  `486f37658f7fa99832d6f0a924680b214925986b`.
- Read-only target: main `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`.
- Scope: entities.py, its error types and unit tests, repository map,
  programme status and changelog; restack against current periods.
- Contracts: user's closeout brief, historical programme entity vocabulary,
  ADR-0017 section 1, current population validator and repository boundary.
- Not blind: train coverage and authorship notes were read before this pass.
  These notes are evidence of provenance, not an authority for behaviour.

## Independent review

Expected behaviour: exactly person, family, household, firm, sector, Crown
and New Zealand; household pattern and matching behaviour identical to
population._ID; every unassigned scheme refuses with its reason; Crown and
New Zealand accept only their fixed singleton ID, anchored with `\Z`.

The enum and immutable seven-scheme registry match that contract. Pattern
and reason are mutually exclusive. Unknown entities/schemes have named
errors. Household matching uses the same pattern and re.match as population;
its historical final-newline behaviour is shared, not silently corrected.
The four unassigned schemes carry reasons and never infer IDs from generator
conventions. Both singleton patterns use `\Z`. The restack preserves main's
periods and does not change entity semantics. No policy or amount changes.

| ID | Severity / class | Discrepancy | Disposition |
| --- | --- | --- | --- |
| — | — | No confirmed defect | Bounded independent clearance |

## Author response

None requested. Original authored rationale was visible as disclosed above.

## Resolution and verification

- Full merge-scope diff and current source/tests read; population validator,
  generator convention and callers checked.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -p no:cacheprovider -q tests/unit/semantics/test_entities.py`: **35 passed in 1.00s**.
- The same environment running `/private/tmp/poltika-codex-entities-probe.py`:
  **1,011 household differential cases agree**, four unassigned schemes refuse
  with their exact reasons, singleton/unknown cases pass, and two scratch
  singleton-anchor mutations are caught. No production file was mutated.
- `git rev-parse a8b214f:src HEAD:src a8b214f:tests HEAD:tests` verified
  identical source/test trees despite queue-only commit `854af88`. Source tree
  `9d755281f0c5522f9215f24fd1a760b619227444`; test tree
  `4f2a7ec52d6b9dbf4793ea3c257a6c14d16a42ee`.
- Coordinating global checks are recorded in the scoped handoff; they do not
  substitute for these independent probes.
- No statutory claim was independently re-derived or changed in this scope.
