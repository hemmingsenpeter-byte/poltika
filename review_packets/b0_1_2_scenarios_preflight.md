# Review Packet: Task B0.1.2 durable scenarios and workspace view — 8 October 2026

**Label:** author preflight plus a fresh same-model check (`poltika-reviewer`,
Sonnet). This is not the independent GPT/Codex review: this PR decides which
amounts the web app shows, so its review-queue row must clear before merge.

## Review inputs

- Diff: the B0.1.2 commits on `prog/b0.1.2-scenarios` (stacked on B0.1.1, #186).
- Plan: `BUILD_PLAN_B0_1_WEB.md` B0.1.2; ADR-0023; ADR-0018 display invariants.
- Tests: `tests/unit/api/test_v1_scenarios.py` (9, real PostgreSQL), the
  Workbench, store, scenario-route, catalogue and data suites (413 passed);
  ruff and `mypy --strict src` clean.

## Independent review

### Expected behaviour (derived before reading the author's rationale)

- The workspace places only values the engines and Workbench produced.
- WFF (per tax year) and the Accommodation Supplement (per week) are never
  added, there is no WFF total, and a component not calculated is never 0.
- Identities are deterministic and exclude timestamps, and stored rows are
  never mutated.
- Every failure is a coded error.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 (P2): a group with no gainers showed "Mean gain: not calculated" | CODE_ERROR | Fixed: "none" when calculated households had no such change, "not calculated" only when none was calculated; tested |
| R2 (P3): household created time took the oldest-or-undated run, unlike the list | CODE_ERROR | Fixed: earliest dated run in both |
| R3 (P3): database or integrity failures returned uncoded 500/409 | CODE_ERROR | Fixed: coded 503 `scenario_storage_unavailable` and 409 `immutable_record`; tested |
| R4 (P3): listing loads all scenarios, then pages in Python | ARCHITECTURE_ISSUE | Accepted at pilot scale; revisit with Task 14 |

## Deferred Codex audit

Check that `distribution_tables`, `_overview` and `_household_workspace` show
only existing values with their units. Check that the "none" and "not
calculated" wording is right. Check that reform-run retention does not pre-empt
Task 14's counterfactual contract.
