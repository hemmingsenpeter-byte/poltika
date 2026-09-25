# Brief for GPT/Codex: Task 34.3 (your half), 34.1 verification, 35.3 wording check

Prepared by Claude Code, 25 September 2026, at Pete's request. Pete has
delegated classification and acceptance to the recommended routes ("do what
you think is best ... accept and proceed"). Your findings still go through
Task 34.4, and nothing below authorises changing protected statutory values
without the test-doctrine process.

**The v0.1.0 tag is blocked on this work.** In the traceability matrix, E5
is the only blocking gap.

## Ground rules

- Work from current `main`. Use `uv run --extra dev ...` and fresh
  worktrees.
- CI (`.github/workflows/tests.yml`) runs:
  - ruff;
  - strict mypy;
  - the full suite with PostgreSQL required;
  - the installed-artifact test;
  - the `code_replay` test.
- Locally, the `postgres` tests need `initdb`/`pg_ctl` on PATH. Without
  them they skip, unless `POLTIKA_REQUIRE_POSTGRES=1` is set.
- Follow `doctrine/review-doctrine.md` for the taxonomy, and CLAUDE.md for
  the ground-truth rules. Never treat model memory as authority for a rate,
  threshold or rule.
- Write your findings to `reviews/2026-09-XX-task34-3-codex.md`. Use the
  same shape as `reviews/2026-09-25-task34-3-claude-fresh-context.md`:
  - id, severity (P1/P2/P3), location, proposed classification,
    reproduction and suggested fix for each finding;
  - then what you checked, and what you could not verify.

## 1. Task 34.3: adversarial review of the Claude Code-authored slices

The slices are:

- **28.4:** the combined runner, `src/poltika/scenarios/combined.py`.
- **29.3:** the golden household runner, the interaction spec-case runner
  and the regression tests (`tests/unit/scenarios/`, `tests/regression/`).
- **30:** `src/poltika/scenarios/record.py`: scenario records, canonical
  ids, code identity and `policy_files_committed`.
- **31 and 31.6:** `src/poltika/engines/simulator/trace.py` and
  `src/poltika/engines/assurance/provenance.py`.
- **32:** `src/poltika/scenarios/store.py`, `migrations/` and ADR-0013.
- **33:** `src/poltika/api/household.py`, `src/poltika/api/scenarios.py`,
  the error mapping in `main.py`, and the installed-artifact probe.

Also review the **Claude fixes for 34.3** (PRs #67 and #68). Under the plan,
a fix touching a reviewer's own authored work needs the other model's
independent check. In particular:

- **F1:** g4-g6 and the Sole Parent Support interaction cases now record
  MD 14/15 and MG 4 as `excluded`. Their FTC, IWTC and Best Start are
  `unsupported`.
- **F2:** the new protected-credit shared-fact gate and its contract row in
  the AS `specification.md`.
- **F3:** the `rent_board_subsidy_rate` parameter.
- **F4:** code identity: startup capture, the running-package check, and
  replay's `code_matches`.
- **F5:** `tests/code_replay/`.
- **F10:** canonical child order in `scenario_id`.

Inspect the whole end-to-end workflow and the shared contracts too, not just
the slice boundaries. Look for:

- silent zeros;
- period mixing;
- contradiction gaps;
- provenance that could describe a different run;
- identity or replay claims stronger than the evidence.

## 2. F11: independent re-derivation

The Claude fresh-context review (F11) found that 28.3, 28.5 and 29.2 were
written and reviewed only within Claude Code. Please independently:

- re-derive the expected values for at least g2, g5, g6, g7 and g9
  (`policy_specs/wff_as_interaction/golden_households.yaml`) and for all
  five interaction spec cases
  (`policy_specs/wff_as_interaction/spec_cases.yaml`), from the cited
  sources and the approved specifications, not from the code;
- check that the 28.3 shared-fact contract in the AS `specification.md`
  (including the new protected-credit row) matches the Task 28.1 research
  (`docs/research/task_28_1_wff_as_interactions.md`);
- record any missing review packets for 28.3, 28.5 and 29.4, or say why
  none is needed.

## 3. Task 34.1: verify each traceability-matrix row

For every row in `review_packets/v0_1_traceability_matrix.md`:

- confirm the cited evidence exists;
- confirm it actually shows what the row claims;
- confirm the status label is justified.

Pay particular attention to D1 (the AS files are now `approved`, F7), D5 (no
unrecorded interpretation left), D6 and E2 (the code-replay claim), and D7.

## 4. Task 35.3: check the demo's limitations wording

Check `docs/demo/v0_1/README.md` against both specifications:

- Is every limitation accurate and complete for this household?
- Is the "does one payment reduce the other" answer correctly sourced?
- Is anything stated more strongly than the specifications support?

The run's evidence is in `docs/demo/v0_1/`:

- `request.json`;
- `response_summary.json`, a stored and replayed run at commit `61564c3`;
- `provenance_report.md`.

## After your review

- Claude Code classifies your findings under 34.4 and routes the fixes: to
  Claude Code for its slices, or to you for yours. Pete confirms.
- Once E5 is closed and Pete accepts v0.1 (34.5), Claude Code tags
  `v0.1.0` (35.4). The CHANGELOG entry is already drafted.
