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

The existing dev-tooling work will add the targets below. This PR does not
contain a Makefile; until that work merges, use the current commands:

```sh
uv sync --locked --extra dev
uv run --extra dev ruff check src tests
uv run --extra dev mypy --strict src
uv run --extra dev pytest -q
uv run --extra dev python -m poltika.engines.assurance.evidence policy_specs/working_for_families policy_specs/accommodation_supplement
```

CI also runs the snapshot/statutory guards, installed-artifact, PostgreSQL,
retained-code replay and pilot-image checks, plus `pip-audit`,
`Bandit (python)`, `zizmor (actions)`, `links` and `source-currency`
(see [SECURITY.md](SECURITY.md)). Inspect their results on the
latest PR commit; the local commands above do not establish all those checks.

Planned Make targets, available only once dev tooling merges:

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
2. `poltika-reviewer`: a fresh-context review of the final head, with no
   unresolved P1 or P2 finding. Record the exact head; any later fix or main
   integration requires a new pass.
3. Independent cross-model review is required for changes to `policy_specs/`,
   `src/poltika/engines/simulator/` or any calculated amount. GPT/Codex reviews
   Claude-authored work; Claude reviews GPT/Codex-authored work. Its row in
   `review_packets/review_queue.md` must be cleared before the PR merges.
   Claude's final-head `poltika-reviewer` pass may meet both gates for
   GPT/Codex-authored work if it independently derives the contract. A same-model
   check cannot clear the cross-model row.

For GPT/Codex-authored PRs touching `policy_specs/`, `engines/simulator/` or a
calculated amount, the single Claude review must be a full `pr-review` pass with
primary-source re-derivation, recorded against the final head.
For mixed authorship, record review coverage by commit; a same-model pass
cannot clear that model's changes. Reconstruction authority: [6 October reconstruction authority](review_packets/pr170_reconstruction_preflight.md).

Independent review uses the other model from the author where practicable.
Same-model review is supporting evidence and cannot clear a cross-model gate.
Author preflight is a separate pass. Every preflight and review records its
exact base and final head SHA. Any later commit, fix, rebase or integration
of main invalidates final-head clearance and requires renewed review. For
mixed authorship, record coverage by semantic change and commit; each model's
changes need the other model's review where cross-model review is required.

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
final-head `poltika-reviewer` pass has no open P1 or P2, and any required
independent cross-model row is cleared. Never use `--admin`, bypass a check or rewrite `main`.

## Releases

Releases follow [docs/releases/RELEASE_CHECKLIST.md](docs/releases/RELEASE_CHECKLIST.md).

## Security

Report vulnerabilities privately. See [SECURITY.md](SECURITY.md).
