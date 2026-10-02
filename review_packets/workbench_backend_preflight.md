# Review Packet: analyst workbench backend (ADR-0018) — 28 September 2026

**Label: author preflight.** Written by the author (Claude Code), who also
wrote the rationale, so it is not an independent or fresh-context review, and
not the GPT/Codex rotation. It does not close any review gate.

## Review inputs

- PR/diff: branch `claude/render-connector-verify-ur97hc` against `main`
  (base `70e77cc`). Changed paths: `src/poltika/api/workbench*.py` (new, five
  files), `src/poltika/api/microsim.py` (a shared helper extracted, no
  behaviour change), `src/poltika/api/main.py` (router included),
  `src/poltika/scenarios/microsim/worked_examples.py` (new),
  `pyproject.toml` and `uv.lock` (`openpyxl`, `types-openpyxl`),
  `tests/unit/api/test_workbench_api.py`,
  `tests/unit/scenarios/microsim/test_worked_examples.py`, `adr/0018-*.md`,
  `REPOSITORY_STRUCTURE.md`, `docs/ORIENTATION.md`, `CHANGELOG.md`.
- Primary sources and source-map paths: none added or changed. The registry
  reads `policy_specs/*/policy.yaml` and `sources.yaml` unmodified.
- Specification paths and clauses: `doctrine/llm_boundaries.md` (not used
  here), `BUILD_PLAN_v0_2.md` (population runs), AS `decisions/DEC-003`
  (no WFF amount enters AS income), WFF and AS `specification.md` calculation
  sequences (untouched).
- Test command and output: see "Commands" below.

## Independent review

Not done. Deferred to the GPT/Codex rotation (see "Deferred Codex audit").

### Expected behaviour (written by the author, who knows the rationale)

- No calculator, loader, parameter file or expected value changes. Every
  amount shown is a `run_population`, `run_combined_household` or
  `analysis.fiscal` result; this code adds only the weighted sums and counts
  in `analysis.py`, a per-household classification against a presentation
  threshold, and rounding to cents once.
- A component that is not calculated is never `0`: it shows `not calculated`
  or its outcome word.
- WFF (per tax year) and AS (per week) are never added or converted. There is
  no total row and no WFF total, because the 2026-27 in-work tax credit is
  `needs_review`.
- An override the engine refuses is refused before any run, with the engine's
  message; `add` and `multiply` results come from `apply_reform`.
- Only `MODELLED_POLICIES` are runnable; another instrument is listed
  read-only.
- The spreadsheet and CSV are written from the same blocks as the page, and
  neither can run a user-chosen label as a formula.
- No server path is returned.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| F1. A missing `sources.yaml` put the server's absolute path in the registry's `error` (`[Errno 2] ... '/tmp/.../sources.yaml'`). | CODE_ERROR | Found by probe. Fixed: OS errors give a fixed message and other messages have the specs path replaced. Test `test_a_broken_instrument_reveals_no_server_path`. |
| F2. Column headers, notes and horizon cells in the workbook bypassed the formula guard, so an option label such as `=HYPERLINK(1)` became a live formula in a header. CSV headers had the same gap. | CODE_ERROR | Found by `test_formula_like_labels_are_written_as_text`. Fixed: every string write goes through `_write_cell`; CSV headers use `_csv_cell`. |
| F3. `test_two_options_are_compared_to_one_status_quo` asserted `len({tuple(...)}) == 1`, which is always true. | TEST_ERROR | Fixed: the status quo column is compared with each run's own baseline from `/microsim/runs`. Code also raises if two options have different baselines. |

Not verified: opening the workbook in Microsoft Excel or LibreOffice (only
`openpyxl` reads it back); run time on the small hosted instance (about 9 s
per option on a development machine with a 2,000-household population); the
page that will render these blocks (not in this PR).

## Author response

- Presentation thresholds (`$52` a tax year, `$1` a week) are settings in
  `workbench_config.py`, not policy. They are not equal by any conversion;
  the config says so. Pete may want different defaults.
- Worked examples reuse the golden households, so their status quo values are
  the same engine results as `/household/calculate` (tested).
- The population is synthetic and every payload says so.
- Later fiscal years are labelled slots only; no estimate is made.
- The run store is in memory (as `/microsim/runs`), so an export of a run
  from before a restart is a 404 and the run must be repeated.

## Resolution

F1-F3 fixed in this PR with regression tests. Nothing escalated. No
interpretation ambiguity arose; no decision artifact is needed.

## Commands

- `uv run --extra dev pytest -q`: 1219 passed, 22 skipped, 2 deselected
  (`installed_artifact`), exit 0, run after fixes F1-F3 on the tree that was
  committed (the 22 skips are existing). Baseline before this PR: 1216 passed.
- `uv run --extra dev ruff check src tests`: all checks passed.
- `uv run --extra dev mypy --strict src`: no issues in 79 source files.
- `ruff format --check` is not enforced in this repo (81 existing files would
  be reformatted) and was not applied.

## Deferred Codex audit

Inspect on return: `workbench_tables.py` (`_measure_changes`, `_classify`:
the threshold rule and the `needs_review`/`unsupported` handling);
`workbench_export.py` (formula guard); `worked_examples.py` (imports the
runner's private `_run`, `_component`, `_delta` so the per-component delta
rules are the runner's own); the `execute_reform`/`stored_run` extraction in
`api/microsim.py`. Open question for Pete: are the default thresholds
acceptable?
