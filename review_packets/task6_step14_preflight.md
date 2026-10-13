# Review Packet: Task 6 step 1.4 household runs and Q19 (7) — 13 October 2026

**Label: author preflight, with one fresh same-model check (`poltika-reviewer`).**
Not an independent GPT/Codex review. Claude Code wrote the change and its
rationale, so the author section below was not written blind.

## Review inputs

- Branch `feat/task6-step14-pairwise-retire-20261013`, stacked on #216
  (base `19128cb`, #216's head). Review only the commits after `19128cb`.
- Task: `BUILD_PLAN_v0_3.md` Phase 1 Task 1.4; [ADR-0017](../adr/0017-shared-household-model.md)
  section 4 (which checks retire, which are kept; "a check is retired only
  when a test shows its contradiction can no longer be constructed").
- Pete's decisions: [12 October record](../docs/programme/2026-10-12-pete-approvals.md)
  Q19 (4), (6), (7) (D36); [13 October record](../docs/programme/2026-10-13-pete-approvals.md)
  Q19 (5) (D38). Engineering choices: D39.
- Commands (worktree `.venv`, `uv run --extra dev`):
  - `pytest -q tests/unit/scenarios/test_household_run.py tests/unit/scenarios/test_household_roundtrip.py
    tests/unit/scenarios/test_combined.py tests/unit/semantics`: 241 passed.
  - `ruff check src tests`: pass. `mypy --strict src`: no issues in 107 files.
  - `git diff --check 19128cb..HEAD`: clean.
  - Broad run at `9137244` (`pytest -m "not postgres" tests/unit/semantics tests/unit/scenarios
    tests/regression tests/acceptance`): 756 passed, 9 skipped, 20 deselected (PostgreSQL; CI runs them).
    An earlier broad run caught the mixed-couple round-trip break listed below.

## Independent review

### Expected behaviour (from ADR-0017 section 4 and Pete's decisions)

- The pair format (`run_combined_household` and its callers) is unchanged.
- A household input runs both policies with the kept checks only: the AS
  week inside the WFF year; main benefit against in-work eligibility and
  MC 6(b) (refused, Q19 (5)); main benefit against the MD 14/15 and MG 4
  protected months (flagged, conservative).
- Claimant link and child count are retired for households: the link cannot
  be constructed; a child-count difference is definitional and reported.
  Partner status is retired only if no household can make it fire.
- Q19 (7): a verified relationship change in the WFF year is `unsupported`,
  ahead of any `needs_review`.
- Q19 (6) applies once the household is canonical; not in this change.
- No calculated amount, scenario id, protected value or fixture changes.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1: a carried unknown claimant link (`needs_review`) was returned before a relationship change (`unsupported`) in `run_household` | CODE_ERROR (P2) | Fixed: the relationship refusal runs first; regression test added |
| R2: an unknown relationship fact changes nothing, and an excluded one refuses AS too | INTERPRETATION_AMBIGUITY (P3) | Not a defect; both choices recorded in D39 for Pete to reverse if he wishes |
| R3: `tax_year` was checked only after a run, so a refusal could hide a wrong year | CODE_ERROR (P3) | Fixed: checked against `policy.yaml`'s reference period before anything runs; tested with and without a refusal |
| R4: the "cannot be constructed" test name overstated the child-count case | TEST_ERROR (P3) | Renamed; the mixed-benefit couple case has its own test |
| Author, broad suite: the validator refusing a mixed-benefit couple on a single family broke the AS-only round trip of spec case `mixed_benefit_couple_is_unsupported` (ADR-0017 section 3) | CODE_ERROR (caught by the round-trip test) | Validator and adapter refusal removed; partner status is kept for households, narrowed to that case, and flagged as the pair path flags it |

No P1 or P2 remains from the author preflight.

### GPT/Codex review at `e9fa1ec` (13 October 2026)

[Independent mapping review](https://github.com/hemmingsenpeter-byte/poltika/pull/218#pullrequestreview-5495644121): blocked, no P1.

| Finding | Classification | Fix |
|---|---|---|
| R1 P2: adapter first-N AS markers (Q19 (2): not membership) were treated as per-child facts, clearing the child-count gate; two WFF entries / AS count one gave calculated FTC, MFTC and AS | CODE_ERROR | `Family.as_child_statuses_from_count`, set by the adapter; `run_household` keeps the pair's child-count gate for it and reports a definitional difference only for caller-supplied statuses. "dependent children count" moves from retired to kept (narrowed). Tests for both origins |
| R2 P2: `run_household` unclassified in the model registry; three registry tests failed | CODE_ERROR | Listed as a `combined_runner` wrapper; the runner's purpose and tests record the `checks` hook; card regenerated. Registry suite: 22 passed |
| R3 P3: the named benefit evidence followed tuple order, not the canonical order the content hash uses | CODE_ERROR | Spells are read in canonical order in both the protected-month flag and the Q19 (5) refusal; shuffled-spell test |
| #216 P3 (Codex at `19128cb`, carried here): the Q19 (5) refusal named the first matching spell in tuple order | CODE_ERROR | Covered by R3's canonical order; reversed-order `to_wff` test added, shown to fail without the sort |
| R4 P3: the difference message called unverified WFF entries children "under the WFF definition" | CODE_ERROR | Message counts list entries and how many have verified whole-year qualification; test with an unknown entry |

## Author response

The protected-month flags now fire on a claimant or partner main-benefit
spell anywhere in the WFF year, a superset of the pair's AS-week trigger;
they only withhold amounts. A household refusal does not run AS, where the
pair format flags both results: every `run_household` refusal is a whole-run
refusal. Partner status cannot be retired outright: AS takes a single claimant with
the mixed-benefit couple category (and returns `unsupported`), so a
household must hold it. The kept check is narrowed to that case.

## Not verified

- No primary source was re-fetched; nothing here reads a statute beyond the
  cited decisions and ADR-0017.
- The household entry point has no API route yet (ADR-0017 answer 3 keeps
  today's request formats).

## Deferred Codex audit

Recheck the final head (after the #216 rebase) for R1–R4 above, and for: the retired-check ledger (`HOUSEHOLD_CHECKS`,
`RETIRED_FOR_HOUSEHOLD`) against ADR-0017 section 4, including partner status kept rather than retired; whether the
enumeration test supports "cannot be constructed" for the claimant link and
"only via a mixed couple" for partner status; the widened protected-month flag (D39 (a)); and Q19 (7)'s
household-fact form (D39 (c)).
