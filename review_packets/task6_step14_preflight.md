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
  - `pytest -q tests/unit/scenarios/test_household_run.py tests/unit/semantics`: 138 passed.
  - `ruff check src tests`: pass. `mypy --strict src`: no issues in 107 files.
  - `git diff --check 19128cb..HEAD`: clean.
  - Broad run (`tests/unit/semantics tests/unit/scenarios tests/regression`): see the PR description.

## Independent review

### Expected behaviour (from ADR-0017 section 4 and Pete's decisions)

- The pair format (`run_combined_household` and its callers) is unchanged.
- A household input runs both policies with the kept checks only: the AS
  week inside the WFF year; main benefit against in-work eligibility and
  MC 6(b) (refused, Q19 (5)); main benefit against the MD 14/15 and MG 4
  protected months (flagged, conservative).
- Claimant link, partner status and child count are retired for households.
  Partner status and the link cannot be constructed; a child-count
  difference is definitional and reported, not flagged.
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

No P1 or P2 remains.

## Author response

The protected-month flags now fire on a claimant or partner main-benefit
spell anywhere in the WFF year, a superset of the pair's AS-week trigger;
they only withhold amounts. A household refusal does not run AS, where the
pair format flags both results: every `run_household` refusal is a whole-run
refusal. The pair adapter now refuses a single-family pair with a
mixed-benefit couple claimant; no production code calls the adapter.

## Not verified

- No primary source was re-fetched; nothing here reads a statute beyond the
  cited decisions and ADR-0017.
- The household entry point has no API route yet (ADR-0017 answer 3 keeps
  today's request formats).

## Deferred Codex audit

Recheck the final head for: the retired-check ledger (`HOUSEHOLD_CHECKS`,
`RETIRED_FOR_HOUSEHOLD`) against ADR-0017 section 4; whether the
enumeration test supports "cannot be constructed" for partner status and the
claimant link; the widened protected-month flag (D39 (a)); and Q19 (7)'s
household-fact form (D39 (c)).
