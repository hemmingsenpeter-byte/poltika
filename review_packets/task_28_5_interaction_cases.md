# Review Packet: Task 28.5 WFF-AS interaction spec cases (24-25 September 2026)

## Review inputs

- **PR/diff:** #57 (merged 24 September 2026), with review notes in
  `1968c33`. The expectations were corrected by #67 (Task 34.3 F1/F2, 25
  September 2026).
- **Cases:** `policy_specs/wff_as_interaction/spec_cases.yaml`, which is
  protected by the statutory-value guard.
- **Tests:** `tests/unit/scenarios/test_interaction_spec_cases.py`;
  `tests/regression/test_wff_as_interaction_leaks.py`.
- **Specification:** the 28.3 contract (see `task_28_3_interaction_contract.md`).

## Independent review

- **Author and implementer:** the cases were hand-calculated by Claude
  Code, which also wrote the 28.4 runner; Pete waived the rotation for
  Task 28.
- **Reviewer:** a Claude Code fresh-context subagent (#57). It recalculated
  all five cases independently.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| No case pinned the precedence of an existing `unsupported` over a disagreement | TEST_ERROR | `disagreement_keeps_existing_unsupported_components` added. |
| Leak wording and precondition precedence were unclear | SPEC_ERROR | Clarified in `1968c33`. |
| The Sole Parent Support case asserted that the protected credits (MD 14/15, MG 4) do not apply and expected FTC `calculated` | TEST_ERROR | Found by the Task 34.3 review (F1); now `unsupported`. The main-benefit case now expects 4 disagreements (F2). Fixed in #67 with Pete's approval. |

## Resolution

Pete accepted the cases on 24 September 2026. He accepted the F1/F2
corrections under Task 34.4 on 25 September 2026. The GPT/Codex Task 34.3
review re-derived all five cases and found no discrepancy.

## Later independent checks

- **Claude fresh-context review (Task 34.3):**
  `reviews/2026-09-25-task34-3-claude-fresh-context.md`.
- **GPT/Codex cross-model review (Task 34.3, 25 September 2026):**
  `reviews/2026-09-25-task34-3-codex.md`. It independently re-derived these
  values; this packet exists because that review's finding C1 asked for
  it.
