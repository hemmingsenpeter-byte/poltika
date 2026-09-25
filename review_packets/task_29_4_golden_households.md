# Review Packet: Task 29.4 golden household hand calculations (24-25 September 2026)

## Review inputs

- **PR/diff:** #59 (merged 24 September 2026), with review notes in
  `b2116bb` and the snapshot refrozen in `c132a5c`. The fixtures were
  corrected by #67 (Task 34.3 F1, 25 September 2026).
- **Households:** `policy_specs/wff_as_interaction/golden_households.yaml`
  (g1-g9), protected by the statutory-value guard.
- **Tests:** `tests/unit/scenarios/test_golden_households.py`;
  `tests/regression/test_golden_result_snapshot.py`, with the frozen
  snapshot `tests/fixtures/golden_results_v0_1.json`.

## Independent review

- **Author and implementer:** the expected values (29.2) came from Claude
  Code's standalone script over the policy files, separate from the
  calculators. Claude Code also implemented 28.4/29.3, so this was
  independent of the code but not of the model.
- **Reviewer:** a Claude Code fresh-context subagent (Task 24.4
  precedent). It recalculated all nine households and approved.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| In g6, the one-child cl 2 cap did not bind as the household claimed to test | TEST_ERROR | g6 rent raised to $600 at the reviewer's request (#59). |
| In g4-g6, main-benefit households asserted the protected credits (MD 14/15, MG 4) do not apply | TEST_ERROR | Found by the Task 34.3 review (F1). g4-g6 now record them as excluded, and g5/g6 FTC, IWTC and Best Start are `unsupported`. Fixed in #67 with Pete's approval. |

## Resolution

Pete accepted Task 29 on 24 September 2026, and accepted the F1
corrections under Task 34.4 on 25 September 2026. No household depends on
DEC-001's convention. The Claude and GPT/Codex Task 34.3 reviews each
re-derived the arithmetic: Claude did all nine households, Codex did g2,
g5, g6, g7 and g9. Neither found a numeric discrepancy.

## Later independent checks

- **Claude fresh-context review (Task 34.3):**
  `reviews/2026-09-25-task34-3-claude-fresh-context.md`.
- **GPT/Codex cross-model review (Task 34.3, 25 September 2026):**
  `reviews/2026-09-25-task34-3-codex.md`. It independently re-derived these
  values; this packet exists because that review's finding C1 asked for
  it.
