# Decision log

Every Tier A and Tier B decision Claude Code makes under ADR-0020
(`adr/0020-delegated-acceptance.md`), newest last. Each records the
options, the choice, why, and how to reverse it. Tier C items are never
decided here; they go to `PETE_QUEUE.md`.

An ADR is still written for an architecture decision that warrants one;
its entry here links it.

| # | Date | Tier | Decision | Options considered | Rationale | How to reverse |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | 2026-10-02 | A | Record the delegated authority as ADR-0020 and point CLAUDE.md, AGENTS.md, the review and development doctrines and BUILD_PLAN.md's Roles at it. | An ADR; a CLAUDE.md section only. | An ADR is where this repository records process decisions with their context, and every session reads CLAUDE.md first. | Supersede ADR-0020 and revert its PR. |
| D2 | 2026-10-02 | A | Until the ruleset is active (PETE_QUEUE Q1), merge with `gh pr merge --squash` after checking by hand that every check is green and the branch is up to date. | Wait for Q1 before merging anything; merge by agreement meanwhile. | The merge rules hold either way; waiting would stall all work on a settings change. | Moot once Q1 is done: switch to `--auto`. |
| D3 | 2026-10-02 | B | Code and docs use the constitution's eight evidence classes. Where a brief says "observed", "deterministic", "estimated" or "simulated", read Fact, Rule (or a Model output of Rules), Estimate and Model output (of a Scenario) respectively. | Introduce the four short names as a separate enum; use the constitution's classes. | The constitution is approved doctrine (Task 1.1). A second vocabulary would be two names for one claim. | Add an alias table; nothing stored depends on the names yet. |
