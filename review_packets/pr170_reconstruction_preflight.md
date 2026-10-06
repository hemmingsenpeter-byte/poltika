# #170 clean reconstruction — author preflight

Date: 6 October 2026. Author: GPT/Codex. This is author preparation, not
independent review. The author has seen the earlier rationale and findings.

Base: `c72c409ac15f78f47691211ba343a3d219f51648`.
Old #170 head inspected: `3449ea881c047481ebcc2dc522ccbef839da4c3e`.
The exact replacement head and check results are recorded in its PR handoff
after this packet is committed, avoiding a self-referential commit SHA.

## Authority and expected contract

Pete's supplied Codex-lane request on 6 October instructs reconstruction of
only #170's still-needed semantic delta on live main. It explicitly requires
other-model review where practicable, same-model review as supporting evidence,
author preflight distinct from independent review, and final-head review
renewed after fixes, rebases or main integration. All Tier A/B/C authorities,
primary-source, protected-value and interpretation gates remain unchanged.
Claude Code owns independent review and final integration. This request is
the authority for the reconstruction, not a claimed historical approval.

## Enumeration and disposition of the old changes

| Old intended change / paths | Reconstruction disposition |
| --- | --- |
| Symmetric other-model review and distinct author preflight: ADR-0020, AGENTS, CLAUDE, CONTRIBUTING, BUILD_PLAN, review doctrine, reviewer agent and preflight skill | Retain; state exact final head and invalidation by any later commit, rebase or integration. Align the existing `pr-review` skill too. |
| Full primary-source single Claude pass and mixed authorship | Retain as the existing review-depth condition; require semantic and commit-specific coverage. |
| Active ruleset prose: ADR-0020, ADR-0007, development doctrine; workflow comments and statutory guard messages | Retain minimal wording correction. Live ruleset 24478578 was read back as active with strict branches, nine checks and no bypass actors. No action version, permission, command or gate behavior changes. |
| PETE_QUEUE / PROGRAMME_STATUS / review_queue reviewer identity | Retain only contradictory review-rule corrections. Clear no source row. |
| #163 acceptance/integration and precision text | #163 merged at `f9c69d8`; use current-main files and update the obsolete open-draft reference in the queue. No constitution rewrite. |
| #166 periods and #169 units history | Already merged at `c72c409` and `240da13`; preserve all current-main code, tests and records. Do not transplant the old waiting-period/entity prose. |
| Tag correction, Pete approvals, closed decisions and programme status | Keep with #167's owned decision/tracker update; do not recreate old release records here. |
| `docs/programme/2026-10-05-closeout-handoff.md`, `2026-10-05-main-ruleset-probe.md`, `2026-10-06-pete-approvals.md` | Exclude broad historical/coordination payload. ADR links to #168's retained GitHub evidence; #167 retains its decision approval artifact. |
| `docs/releases/V0_2_LIMITATIONS.md` | Exclude release-history reconciliation from the review-rule increment. |
| `review_packets/2026-10-05-reviewer-rotation-preflight.md` | Replace with this packet and a new exact-head handoff. Old preflights/reviews are historical, not clearance. |

The old head and history remain available on #170. The replacement uses a
new branch from main, preserving concurrent work without a force push.

## Verification and final gate

Inspect the complete main-to-replacement diff, all governance entry points,
unchanged ADR-0020 tier text, workflow YAML and local links. Run focused
programme-authority, review-queue, orientation, constitution and decision
tests, the default full suite, Ruff, strict mypy, offline lychee with
fragments, offline strict zizmor and `git diff --check` in a separate
detached checkout of the committed replacement head. Record actual commands,
exit statuses, skips and limits in the handoff. Required GitHub checks and
fresh Claude final-head review remain separate gates.

No statutory policy/source/expected-value, calculation, dependency or raw
archive bytes are changed. No source row, policy status or Tier C decision
is cleared by this packet. No unresolved interpretation is decided here.

## Deferred independent review

Claude must review the full replacement diff, confirm scope and rule
consistency, and record the exact base/head with no unresolved P1/P2. If
integration advances the head, renew preflight and review. Claude decides
whether to retire old #170 once the replacement is accepted.
