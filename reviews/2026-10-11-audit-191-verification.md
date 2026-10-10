# PR #191 audit: verification against main b19e764 (11 October 2026)

Author: Claude Code (Sonnet 5.5). Verifies `reviews/2026-10-08-gpt6-audit-handoff.md` and
`reviews/2026-10-09-pr191-dispositions.md` (both on the #191 branch) against current
`origin/main` code and workflow config. Config and code reading only; no secrets, keychain
or Pete's home were touched, and no exploit was attempted. This is not a closeout: no
finding is marked resolved, and Tier C items remain Pete's.

## Workflow facts (all 8 files in `.github/workflows/`)

- Triggers: only `pull_request` (branches: main), `push` (main) and `schedule`. No
  `pull_request_target`, no `workflow_run`.
- Every workflow has top-level `permissions: contents: read`; only `publish-issue`
  (push/schedule only) adds `issues: write`. Every checkout uses `persist-credentials: false`.
  No `secrets.*` are referenced. `${{ }}` in `run:` bodies: none (PR SHAs go through `env:`).
  Actions are pinned by SHA.
- Before this change, every job except `pilot-image` ran on `[self-hosted, poltika]`
  with no fork condition. Fork PRs to a private repo run only if the repository's
  fork-PR setting allows them (a GitHub setting, not visible in the repo).
- `uvx zizmor@1.30.1 --offline --strict-collection .github/workflows`: no findings
  (23 suppressed by default persona, same before the change). `bandit -r src` (CI command,
  1.9.4): 0 high, 0 medium, 37 low.

## Dispositions

| ID | Disposition | Sev | Exploitability | Blocks | Remediation |
| --- | --- | --- | --- | --- | --- |
| A1 runner isolation | Verified (config fact: D21, Q13). Repo-side controls were already least-privilege; one gap closed: fork PRs could reach the runner. Host isolation is unchanged. | P1 for any untrusted code; P2 with collaborator-only trust | Needs write access to a branch (or a fork PR if forks are allowed in repo settings). Impact: Pete's user data. | Nothing now. Blocks adding collaborators, external contributors or any public repo. | Partly fixed: fork guard on all self-hosted jobs plus `fork-pr-gate.yml`. Host change = Pete (`docs/programme/RUNNER_ISOLATION_RUNBOOK.md`). |
| A2 shared login, no ownership | Verified in code. `access.py` is one Basic identity. `v1_scenarios.py:198` lists all scenarios, `:314/:320` open by id, `scenarios.py:96` by id; no owner column or predicate anywhere in `src/poltika/api`. UI already says "synthetic population" (`AppShell.tsx:37`) but nothing says "no personal data / shared login". | P1 before real personal data or multiple users; P3 for synthetic single-operator pilot | Any password holder reads all records. | Blocks real personal data and multi-user use. Does not block synthetic deployment. | Documented boundary added to `docs/pilot/HOSTING.md`. Web banner copy is outside this change (web/ owned elsewhere); authz design is Tier C. |
| A3 stacked PR integration | Out of scope for config; #186, #187 and #188 are now in main history; #189 not found in main log. Not otherwise re-verified here. | P2 | n/a | Merge process only | None here. |
| A4 household/UI contract | Not re-verified (web/ and household code are being edited by others). | P2 | n/a | Task 6 gate | None here. |
| A5 completeness claims | Partly verified: `workbench.py:250` still runs `execute_reform(option.reform, ["family_tax_credit"])`, so reform runs cover FTC only. Home/data copy says synthetic, not an NZ estimate (`HomePage.tsx:128`). No grep hit for "net Crown" or "representative" claims in `web/src` tsx. Tab-level copy and exports not exhaustively read. | P2 | Misreading by users | Blocks external use until copy is checked | None here (web/ and semantics areas excluded). Suggest a negative copy test in the owning PR. |
| A6 web required check | Verified: `tests.yml` has job `web` (name `web`), runs on every PR. The ruleset was not changed; Q15 is Pete's. | P2 | n/a | A failing web job would not block merge | None; ruleset change is Pete's (Q15). |
| A7 sequencing | Strategy, not a defect. Not assessed. | P3 | n/a | None | None. |

## Changes in this branch

- Every self-hosted job now carries `if: github.event_name != 'pull_request' ||
  github.event.pull_request.head.repo.full_name == github.repository` (combined with the
  existing condition in `links` and `image-inputs`). Job names are unchanged, so no required
  context is renamed.
- Caveat: a skipped required check counts as passing. For a fork PR the self-hosted
  checks therefore skip rather than fail. `fork-pr-gate.yml` (hosted, `permissions: {}`,
  runs only for forks) fails red to make that visible. It is not a required check, so it does
  not by itself stop a merge; merging is still Pete's action.
- `docs/programme/RUNNER_ISOLATION_RUNBOOK.md` (Q13 steps and verification) and a data
  classification section in `docs/pilot/HOSTING.md`.

## Not verified / needs the operator

Runner identity, home-directory ACLs, whether the repo allows fork PR workflows, and
who has write access cannot be read from the repository. A1 acceptance (a dummy file
unreadable from CI) needs the runbook executed by Pete.
