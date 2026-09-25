# Review Packet: Task 28.3 WFF-AS interaction contract (24-25 September 2026)

## Review inputs

- **PR/diff:** #55 (contract, merged 24 September 2026), with the
  revision after the fresh-context review in `81d476a`. The
  protected-credit row was added by #67 (Task 34.3 F2, 25 September 2026).
- **Primary sources and source maps:**
  `docs/research/task_28_1_wff_as_interactions.md`;
  `review_packets/task_28_1_interaction_sources.md`; the AS and WFF
  `sources.yaml`.
- **Specification:**
  `policy_specs/accommodation_supplement/specification.md`, "Task 28.3
  WFF-AS interaction contract" (shared-fact checks, outcome on
  disagreement), with a pointer in the WFF specification.
- **Decision:** DEC-003 (WFF credits excluded from AS chargeable income
  whichever agency pays them).

## Independent review

- **Reviewer:** a Claude Code fresh-context subagent, standing in for
  28.6 under Pete's rotation waiver for Task 28 (24 September 2026). It
  was not the cross-model reviewer the plan intended; see "Later
  independent checks".
- **Derived expectations:** no income coupling in either direction;
  native periods; conservative shared-fact gates; an existing
  `unsupported` preserved.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| The partner, MC 6(b) and child checks were stated as certainties | SPEC_ERROR | Rewritten as conservative gates (`81d476a`). |
| DEC-003's limits and r 17(2)(f) were overstated | SPEC_ERROR | DEC-003's limits restored; r 17(2)(f) left unresolved. |
| MD 14/15 and MG 4 main-benefit constraints from the 28.1 research were not carried into the contract | SPEC_ERROR | Found later by the Task 34.3 review (F2); protected-credit row added in #67. |

## Resolution

Pete accepted the contract with three decisions: two scenarios rather
than one merged fact set; the community spouse is not compared; an
existing `unsupported` is kept on a disagreement (24 September 2026). He
accepted the F2 row under Task 34.4 on 25 September 2026.

## Later independent checks

- **Claude fresh-context review (Task 34.3):**
  `reviews/2026-09-25-task34-3-claude-fresh-context.md`.
- **GPT/Codex cross-model review (Task 34.3, 25 September 2026):**
  `reviews/2026-09-25-task34-3-codex.md`. It independently re-derived these
  values; this packet exists because that review's finding C1 asked for
  it.
