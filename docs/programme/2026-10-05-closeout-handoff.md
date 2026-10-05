# Closeout continuation — 5 October 2026

This is a preparation snapshot, not merge or release approval. Root controls
merges sequentially. Existing worktree drafts and the shared checkout's
untracked `docs/repo_closeout_execution.md` were preserved.

## Completed actions and review findings

- Pete's approved first product remains the Analyst Workbench. #167 archives
  the original migration brief verbatim and records Q5 scope/measure choices;
  ADR-0018 design acceptance and Q10 income/period methodology stay open.
- Remote `v0.2.0` is now annotated: tag object `63f5f0d` points to
  `adf40588eb471b824542d3dc13fdaed3239ec0b9`. The explicit approved correction
  used a lease against the previous `2cdadba` target and was read back.
- Negative probe #168 at `fb92c17` failed the required `test` check, while the
  other eight required jobs passed. GitHub reported `mergeStateStatus=BLOCKED`.
  The PR was closed without a merge attempt; the probe never entered main.
- Codex's post-merge #161 audit found precision loss and nonfinite scale
  acceptance. #169 fixes both, with 28 focused tests, Ruff and strict mypy.
  Root independently checked low-context large-value roundtrips. The original
  #144 active links and five archive byte comparisons also passed. These
  local audits do not invent a Claude pass on either squash commit.

## Prepared artifacts

| PR | Published head at this snapshot | Scope and remaining dependency |
| --- | --- | --- |
| #167 | `fefb8c8` | Approved decisions, original brief, tag record and Q5 commission. Nine required checks passed; final Claude cross-model review pending. |
| #170 | See this PR's final head | Separate ADR-0020 rotation amendment and truthful final-head rule. Settings remain outside its commit. Final review and CI required. |
| #163 | `fb9df3e` | AI gate corrected to actual checks, artifact-specific promotion and current phases; final reviewer and current-main integration remain. |
| #164 | `a54c875` | Governance choices, honest arithmetic-only cards and async engine discovery fix; final reviewer and current-main integration remain. |
| #148 | `4e73947` | Tax source scope, unsupported benefit classes and explicit rounding/enactment gaps. Nine required checks passed; final Claude/queue gate pending. |
| #151 | `7418c99` | Benefit source scope, precise future amendments and sourced per-person §3.4 correction. Nine required checks passed; final Claude/queue gate pending. |
| #169 | `5d79da7` | Exact rescaling and finite-positive scales; nine required checks passed; final Claude review pending. |
| #166 | `a32f10e` | Periods; nine required checks passed and Codex audit had no P1/P2. Final Claude pass still required. |
| #171 | `7961862` | Entities recovered in a stacked draft on #166; 67 focused tests, Ruff and strict mypy. Retarget/update after #166 merges, then final integration gates. |
| #172 | `933a416` | Official disposable-income source-scoping draft; definition undecided, MSD 2019 Word-body extraction gap explicit. Final cross-model source review pending. |

## Approval blocks and continuation

Automatic approval review rejected the Claude CLI reviewer call because the
private-repository export destination/scope had not been explicitly approved.
The user was asked to authorise relevant Poltika files, specs, sources, diffs
and tests to Claude Code's Sonnet reviewer for this closeout. No Claude call
was made after that rejection while the answer remained pending.

Automatic approval review also rejected activation of broad persistent shell
permissions. A supplemental review then found cross-repository merge and
additional/force-refspec escapes in the initial wildcard proposal. The draft
was narrowed to exact named branch push and same-repository PR merge commands;
it remains uncommitted at
`/private/tmp/poltika-reviewer-rotation-20261005/.claude/settings.json`.
Only existing per-command permissions are in use. The scope-approval question
remains pending; a preselected UI option is not an answer.

After the required authorization, run fresh-context mechanical-input Claude
reviews, record exact heads and clear applicable queue rows, then merge on
current-main green CI in the approved order. Every main integration or later
fix needs a new final-head pass; do not use earlier comments for a changed head.
No admin bypass or rewrite of main is authorised. Further unsourced numerical
claims, protected values, public deployment and external resource spending
retain their existing gates.
