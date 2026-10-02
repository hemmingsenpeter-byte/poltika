# Contributing to Poltika

Read [CLAUDE.md](CLAUDE.md) (or [AGENTS.md](AGENTS.md) for GPT/Codex) and
[docs/ORIENTATION.md](docs/ORIENTATION.md) first. This file is the short
route through them.

## Work in a worktree

Several sessions can work in the repository at once, and `main` moves. Never
work in the shared checkout. Check the state, then branch off `origin/main`:

```sh
git status -sb && git log --oneline -5 origin/main && git worktree list
git worktree add -b <branch> /private/tmp/poltika-<name> origin/main
```

One bounded task per pull request.

## Make targets

A Makefile gives one name to each routine step:

| Target | What it does |
| --- | --- |
| `make setup` | Install the dependencies |
| `make test` | Run the tests |
| `make lint` | Run Ruff |
| `make typecheck` | Run mypy (strict) |
| `make guards` | Run the repository guards |
| `make serve` | Start the API |
| `make check` | Lint, typecheck, guards and tests: run it before you open a PR |

## Where new files go

[REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) is the map. Read it before
creating a production file, module or directory. If a new component has no
obvious place, update that file deliberately. Do not make an ad-hoc
directory. Add a line to it for every new file.

## Tests

There are three classes: spec, benchmark and regression. Statutory expected
values are protected. Never change one to make a test pass. The process for
a real change is in [doctrine/test-doctrine.md](doctrine/test-doctrine.md).

## Ground truth and prior art

Policy rules come from cited primary NZ sources, never from memory. If a
source is missing or ambiguous, stop and flag it. Interpretation goes to
Pete and is never resolved silently. Do not look at OpenFisca or any other
external implementation for policy logic. See
[CLAUDE.md](CLAUDE.md), [doctrine/ip-doctrine.md](doctrine/ip-doctrine.md)
and [doctrine/review-doctrine.md](doctrine/review-doctrine.md).

## Review

1. Author: run `.claude/skills/pr-review-preflight/SKILL.md` before you open
   or update the PR.
2. `poltika-reviewer`: a fresh-context Sonnet review. It is a same-model
   check and does not clear a review-queue row.
3. GPT/Codex: an independent review is required for changes to
   `policy_specs/`, `src/poltika/engines/simulator/` or any calculated
   amount. Its row in `review_packets/review_queue.md` must be cleared
   before the PR merges.

## Merging and the tiers

[ADR-0020](adr/0020-delegated-acceptance.md) sets who decides what.

- Tier A: engineering, tooling, CI, structure, docs and refactors that
  change no amount. Decide and merge.
- Tier B: a reversible choice the plans leave open. Decide, and log it in
  `docs/decision_log.md`.
- Tier C: statutory values and sources, protected expected values, Māori
  data governance, anything public, spending, tagging releases, deleting
  data. Never decided by an agent. Add it to
  [PETE_QUEUE.md](PETE_QUEUE.md) and route the work around it.

A PR merges with `gh pr merge --squash --auto` when CI is green on its
latest commit, the branch is up to date, the preflight has run, the
`poltika-reviewer` pass has no open P1 or P2, and any required GPT/Codex
row is cleared. Never use `--admin`, bypass a check or rewrite `main`.

## Releases

Releases follow [docs/releases/RELEASE_CHECKLIST.md](docs/releases/RELEASE_CHECKLIST.md).

## Security

Report vulnerabilities privately. See [SECURITY.md](SECURITY.md).
