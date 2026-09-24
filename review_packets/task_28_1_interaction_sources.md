# Review packet: Task 28.1 interaction sources

Author: GPT/Codex. Base revision: `18e1ca5`.
Requested independent reviewer: Claude Code. Pete accepts.

## Mechanical review inputs

- BUILD_PLAN.md Task 28.1(a)-(d), and both approved policy specifications.
- Both `sources.yaml` files, new `task_28_1_check` records and official URLs.
- Income Tax Act 2007, 4 September 2026: CW 33(1)(a), MB 13(2)(l),
  MC 1(2), MC 6(b)(i), MD 8, MD 14-15, MG 4.
- Social Security Act 2018, same version date: Schedule 2 main-benefit
  definition, Schedule 3 clause 8, Schedule 4 Part 7 clause 7.
- Social Security Regulations 2018, same version date: regulations 16-18,
  Schedule 8 Part 1 item 15, Part 21 clauses 36-37.
- Tax Administration Act 1994, same version date: 80KK, 80KN-80KS, 80KU.
- IRD other-income/government-payments guidance, and MSD chargeable-income,
  FTC administration and payer-choice guidance, from the source maps.
- Current WFF component gates and AS parameter lookup in simulator code.
- Author conclusions to read only after source derivation:
  `docs/research/task_28_1_wff_as_interactions.md`.

## Review and acceptance

Independent review pending. This is source research, not Task 28.3's
contract approval, a payer/date decision or an implementation PR.
Unresolved interpretation goes to Pete with the evidence, not to an
author-created accepted DEC. No BUILD_PLAN.md edit while #42 owns it.

## Validation

- Both source catalogues parse; source IDs are unique; unchanged policy
  files validate and every parameter source reference resolves.
- `git diff --check`: passed.
- `env PYTHONPATH=src <main-venv>/bin/python -m pytest -q`: 249 passed,
  1 installed-artifact test deselected; existing two deprecation warnings.
- No implementation or protected fixture change. Installed-artifact,
  Ruff and mypy are not rerun for this documentation-only slice.
