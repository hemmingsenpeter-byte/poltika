# Review Packet: Task B0.1.4 scenario experience — 8 October 2026

**Label:** author preflight (briefed Sonnet worker, checked by the orchestrating
session) plus a fresh same-model check (`poltika-reviewer`). This is not the
independent GPT/Codex review. It decides how stored amounts are displayed, so
its review-queue row should clear before merge.

## Review inputs

- Diff: B0.1.4 commits on `prog/b0.1.4-scenarios-ui` (stacked on #188).
- Plan: `BUILD_PLAN_B0_1_WEB.md` B0.1.4; the `api/v1_blocks.py` contract.
- Checks (web): lint, typecheck, Vitest (12 files, 63 tests including the
  copy scan), static build and contract drift all pass. No Python change.

## Independent review

### Expected behaviour

- The frontend computes no amount.
- A missing or not-calculated value shows its outcome, never 0.
- Population metrics show 3 significant figures; household Rule outputs are
  exact; table strings are shown as given.
- The confirmation panel uses only `/workbench/check` data.
- No XSS, and no gated copy.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 (P3): a source link rendered any URL scheme | CODE_ERROR | Fixed: only http(s) become links |
| R2 (P3): an option failing lookup was dropped silently, so Run could enable over a shorter list | CODE_ERROR | Fixed: the review step errors and shows no panel |
| R3 (P3): 3 significant figures go through JS `Number` | — | Display rounding of one value only; accepted |

## Deferred Codex audit

- Check that the metric and table rendering match the backend strings.
- Check that the outcome markers and units read correctly.
- Workbench export is omitted from the workspace, because the stored workspace
  has no in-memory option run ids. Check that this is acceptable until the
  household and export follow-up.
