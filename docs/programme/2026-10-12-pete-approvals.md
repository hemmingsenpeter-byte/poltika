# Pete approval record — 12 October 2026

Recorded by Claude Code from Pete's instructions in a Claude Code session on
12 October 2026. Each instruction approved the session's written
recommendations in full. The recommendations are restated below as the
approved decision. This records Pete's decisions. It does not independently
verify a statutory rule, approve a protected expected value, or clear a PR's
review or CI.

## The instructions

1. **"accept and proceed on all - confirm in text when completed"**, on the
   recommendations following PR #211's review:
   - fix the reviewer's P3 R1 and R2 in a follow-up PR (done in #212);
   - leave the nit;
   - change replay so that inputs and results decide `identical` or
     `drifted`, with a code change flagged separately (Q21 (d));
   - do the real-phone check of B0.1.6 (Pete);
   - send the WFF/AS boundary proposal for GPT/Codex review (row added in
     #212);
   - remove local worktrees whose branches are merged and clean, once #211
     merged, and add the five superseded branches to Q12's list (done in
     #212).
2. **"yes approve all and record all"**, on one recommendation for each open
   `PETE_QUEUE.md` question, given below.

## Decisions by question

| Q | Decision | Remaining action |
| --- | --- | --- |
| Q2 | Keep the interim ban on ethnicity- and iwi-disaggregated outputs. Commission dated primary-source research on Māori data governance before naming anyone to engage. The frameworks to start from are the session's suggestions, which the research must source. | Brief commissioned ([briefs](../../review_packets/research_briefs_20261012.md)); Pete names who to engage after reading the result. |
| Q3 | Do not lodge an IDI application yet. Commission the dated, sourced access-route document now. | Lodge once a concrete project needs microdata (Pete). |
| Q4 | Decide no reserved item now. P6: the conformance suite stays internal. P7, P13, P14 and P20 wait for their phases. P18: set acceptance tolerances before the next phase gate is claimed. | P18 tolerances, before the next gate (Pete). |
| Q5 | "One main benefit per household" is a deliberate coverage limit for the first benefit slice, not a legal claim (Social Security Act s 18 limits receipt per person). The plan wording should say so. | No plan change is needed: `BUILD_PLAN_v0_3.md` 3.4 already states the per-person rule and treats a couple with two main benefits as `unsupported`. Pete reviews the disposable-income source pack when ready. |
| Q7 | Defer the historical horizon to Phase I. When it starts, the earliest year is a delegated, reversible choice made from a sourced coverage proposal. | None now. |
| Q9 | Accept ADR-0018 as built (#133; GPT/Codex reviewed; the B0.1 web app runs on it). Later changes go through new ADRs. | None. |
| Q10 | Adopt #195's wording as the interim income and period contract for Tasks 5, 6 and 9. A dated income spell is never apportioned into a policy period: the caller supplies an amount per policy period (D32). Reopen only with a sourced method. | None. |
| Q11 | Name no external pilot participant until B0.1.7 is deployed and the real-phone check passes. Tag v0.1.5 only against its release evidence. | Release-evidence checklist (Claude Code); naming a participant and tagging (Pete). |
| Q12 | Approve deleting the 87 listed merged branches and the branches added on 12 October: four remained, because `feat/b016-responsive-20261011` was already deleted when #209 merged. GitHub keeps each PR head as `refs/pull/N/head`. | Done: Claude Code deleted the 91 branches on 12 October after re-checking that every tip was unchanged ([verification](../../reviews/2026-10-12-q12-branch-verification.md)). |
| Q13 | Move the self-hosted runner to a dedicated non-admin `poltika-ci` macOS user ([runbook](RUNNER_ISOLATION_RUNBOOK.md)). | Pete: the cutover needs an administrator on the Mac. |
| Q14 | Confirm the 50 MiB response cap and the Bandit MEDIUM gate. | None. |
| Q15 | Use a paid PostgreSQL plan with backups, not a free one; make the `web` CI check required. | Claude Code found the Render setup (read-only, 12 October): the "Poltika" workspace holds the `poltika` web service (Docker, Oregon, auto-deploys on commits to `main`, no health-check path set) and the PostgreSQL instance `poltika-db` (plan `0.1c-256mb`, 1 GB, Oregon, version 16). Pete: confirm that this plan includes backups, set `POLTIKA_ACCESS_PASSWORD` and `POLTIKA_DATABASE_URL`, and add `web` to the ruleset's required checks. The Claude Code session's classifier refused that ruleset change. |
| Q16 | Keep D11: the 2026–27 annual income-tax component stays `needs_review` until Royal assent. On assent, switch it to `calculated` after a dated source check. | Watch for assent (Claude Code), then a reviewed PR. |
| Q17 | Income-tax precision: whole-dollar taxable income only; any other input is `unsupported`. This is a labelled Assumption, not a claim about law. Revisit if an official method is found. | Implement with the numeric specification (Claude Code), with GPT/Codex review. |
| Q18 | The statute prevails over the IR3G worksheet's $0.33 discrepancy. The guide is excluded as a benchmark and the issue is recorded as `SOURCE_CONFLICT`. IRD is not contacted for now. | None. |
| Q19 | (3) Synthetic ids are acceptable until real data arrives. (4) Retire the pairwise checks for `Household` inputs only, keeping the pair format, but only after (5) is answered. (6) Once the household is canonical, a disagreeing pair is refused with a 422. (7) Add a "relationship changed in year" fact so that case is `unsupported`. (1), (2) and (5): commission sourced readings with GPT/Codex review. | Sourced readings for (1), (2) and (5), then Pete's review. (6) and (7) are Claude Code tasks. |
| Q20 | (1) The hosted pilot holds synthetic or public non-personal data only, and the web app shows a banner saying so. (2) Workflows from outside collaborators' fork PRs need approval. (3) The fork-PR gate becomes a required check. | (1) The banner ships in the follow-up PR. (2) No change is needed: workflows from fork pull requests are already disabled. (3) Pete adds `fork-pr-blocked` to the ruleset's required checks; the Claude Code session's classifier refused that change. |
| Q21 | (a) Accept rerun-and-compare for now: the synthetic population regenerates exactly from its seeded spec. Write a retention ADR when the first real population arrives. (b) A reform's effective-from date is required, its fiscal year is derived from it, and an announcement date is optional information. (c) Exports follow Q9. (d) Inputs and results decide `identical` or `drifted`; a code change is reported as `code_changed` (implemented with this record). | (b) is a Claude Code task. |
| Q22 | Dismiss Dependabot alert #1 (`braces`) as dev-only with no fix available; revisit when a patch ships. | Done: dismissed on 12 October. |

The real-phone check of B0.1.6 (iOS Safari and Android Chrome) remains
Pete's action; it is tracked as Q23.
