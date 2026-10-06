# ADR-0020 reviewer rotation — author preflight

Updated: 6 October 2026. Author: GPT/Codex. This is an author preflight,
not independent or fresh-context review. Base:
`f9c69d8e3384f0753be482c5ee4a6564cfa5d8ea`.

## Expected contract

Preserve BUILD_PLAN's other-model rotation, all Tier C boundaries,
final-head author preflight and fresh-context reviewer passes, latest-head
green CI, current main and squash merging. GPT/Codex authorship needs Claude
review; Claude authorship needs GPT/Codex review. Same-model checks never
clear cross-model rows. Earlier comments cannot cover a changed head.
This expectation is not blind: the author knows the implementation rationale.

## Findings and fixes

Claude's independent review of `8fbb5519da00e9248f5350aede35f35bfde668fa`
found R1 tracker contradictions (P1), R2 stale CONTRIBUTING rules (P1/P2),
R3 stale Q8 records (P2), R4 inaccurate preflight evidence (P3), and
R5 outdated ADR-0007 enforcement claims and insufficient retained probe
evidence (P3). All five are addressed in this revision. Their proposed
classification is CODE_ERROR for stale operational instructions/records;
no policy interpretation or protected expected value changed.

The next Claude pass on `eee9141767e033225440eaf95bebe6fb8f5a4745`
found a new P2: the queue and handoff still described already-merged #169
as awaiting review/CI. Both now record its `240da13` squash and link the
actual final-head Claude pass, preserving its P3 follow-ups. A P3 offline
verification limit concerned the external preflight record. The final
reviewer receives readback of the exact SHA-bearing comment as a local
mechanical artifact after deriving the contract.

PETE_QUEUE, PROGRAMME_STATUS, CONTRIBUTING, ADR-0020, both agent entry
points, BUILD_PLAN, review/development doctrines and reviewer/preflight
instructions were inspected. Q8 records the named Pete authorisation and
GitHub tag readback; the ruleset evidence preserves the failed probe's check
URLs and distinguishes recorded pre-close BLOCKED from current BEHIND.
Untracked project-permission settings remain an unactivated proposal outside
this PR. No private-repository export permission is inferred.

## Final-head evidence

After committing this packet, run the preflight in a separate detached
worktree and publish the complete immutable head SHA and actual command
results in [the final-head author-preflight comment](https://github.com/hemmingsenpeter-byte/poltika/pull/170#issuecomment-6002434709).
That SHA-bearing author-preflight comment is the final-head record; this
packet does not claim that checks on an earlier commit cover a later one.
The 5 October packet's unnamed final head and blanket consistency claim were
inaccurate and are withdrawn. Final Claude review and required CI remain
separate gates, and a later commit requires both passes again.

## 6 October follow-ups

Pete's dated approval quotations and scopes are now in
`docs/programme/2026-10-06-pete-approvals.md`. The conditional single-pass
rule requires full primary-source re-derivation for Codex-authored policy
and calculation PRs. Mixed authorship retains commit-specific coverage.
The active ruleset/current required checks replace obsolete target prose;
workflow comments and v0.2 review records match observed live evidence.
Claude Code alone merges this train. The older linked preflight comment
covers only its stated SHA; the next exact-head comment must supersede it.

## Integration after #163 merged

The #163 merge changed the legacy tracker row. This revision preserves its
accepted constitution and records the actual `f9c69d8` merge and exact-head
Claude review. Source fixes remain open and require new final-head reviews.
The statutory guard's runtime notices now distinguish reporting changed
values from mandatory successful completion. The queue distinguishes
cleared merged-implementation debt from still-open source/semantic PRs.
No historical review is promoted into clearance of later source heads.
