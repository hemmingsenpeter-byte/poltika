# ADR-0013: Task 32 storage for scenarios and runs

**Date:** 24 September 2026
**Status:** proposed. Pete decides (BUILD_PLAN.md Task 32.1). Drafted by
Claude Code.

## Context

Task 32 needs persistent storage for v0.1's scenarios and runs. The approved
Task 30-32 refinement sets the requirements. The store must handle:

- **Immutable records.** A scenario (household facts, assessment periods,
  requested policy versions) and a run (inputs, artifact manifest, result,
  provenance trace) are written once and never edited in place (32.2).
- **Replay from retained artifacts.** A stored run must replay exactly
  after the current policy, source catalogue, specification or code files
  change. A missing or hash-mismatched artifact fails explicitly (32.4).
  For v0.1, a git commit SHA reachable from protected `main`, with
  `uv.lock`, is an acceptable immutable reference for repository content.
  A separate store is needed only for content not in git (30.1). A run
  from an uncommitted working tree must retain those files or be recorded
  as non-reproducible.
- **Drift reporting.** A re-run against current artifacts creates a new
  run and reports which artifacts changed (32.4).
- **API exposure.** Task 33.2 serves create, fetch and re-run, and the
  ADR-0011 installed-artifact test must cover it (33.4).

v0.1 has one operator, no concurrent writers, and small data: tens to
hundreds of runs, each a few kilobytes of JSON plus references.

ARCHITECTURE.md's recorded long-term stack (commit `21dc905`) names
PostgreSQL with SQLAlchemy 2 and Alembic for "scenarios, parameters,
provenance, datasets, model versions". ADR-0010 set the precedent for the
API: build directly on the recorded target rather than a placeholder that
is later replaced. The stack table also says each component is adopted
"only when the BUILD_PLAN.md task that actually needs it is reached".
Task 32 is the first task that needs a database.

## Options

**(a) PostgreSQL + SQLAlchemy 2 + Alembic now.**

- Tables `scenario`, `run` and `artifact` (content-addressed bytes, for
  anything not referenced by git SHA). Rows are append-only, enforced by
  having no update path in the repository layer. A database-level guard
  (e.g. a trigger or revoked `UPDATE` privilege) can be added if review
  wants it.
- Local development uses Docker Compose. CI adds a Postgres service
  container, and tests run against real Postgres, not SQLite, to avoid
  dialect drift.
- Deployment extends ADR-0011's convention with one more operator-set
  variable, `POLTIKA_DATABASE_URL`. The installed-artifact test gains a
  database dependency.
- **Cost:** new runtime dependencies (`sqlalchemy`, a driver, `alembic`),
  Docker for local development, a CI service container, and a migration
  baseline to maintain. This is roughly a task's worth of infrastructure
  before the first record is stored.
- **Benefit:** no second storage build. Task 33's API and later v0.2+
  work (datasets, parameters) extend the same store.

**(b) Append-only, content-addressed file store now; Postgres later.**

- Runs, scenarios and artifacts are canonical JSON or bytes named by their
  own SHA-256 under one configured directory. A `ScenarioRepository`
  interface sits in front, shaped so its records map one-to-one onto
  option (a)'s future tables.
- No new dependencies, no service in CI, and the installed-artifact test
  needs only a temp directory.
- Immutability comes almost for free: a file named by its hash cannot
  change without changing its name.
- **Cost:** a later migration to Postgres is certain. That is a second
  build of the storage layer plus a data migration, the outcome ADR-0010
  chose to avoid for the API. Querying (e.g. "all runs of scenario X") is
  a directory scan.
- **Benefit:** the smallest v0.1 surface, and the replay and immutability
  requirements are met natively.

## Recommendation (Claude Code, for Pete's decision)

**(a) PostgreSQL now**, for three reasons:

1. Task 32 is the point the stack table says a component should be
   adopted, and ADR-0010 already applied that rule to the API.
2. Option (b)'s saving is real but temporary. Its repository interface and
   migration are work done twice.
3. Pete's recorded preference is a lean v0.1 that builds toward the
   enterprise stack as tasks reach it, not permanent minimalism.

(b) is a sound choice if v0.1's calendar matters more than avoiding the
rebuild. Its content-addressed design is simpler to prove immutable, and
the replay requirements do not favour either option.

Either way, the replay rules in 30.1/32.4 are independent of this choice.
Git-referenced artifacts are resolved from git, and only non-git content is
stored.

## Decision

*Pending Pete.*

## Consequences

*To be completed once decided.* If (a) is chosen: add `sqlalchemy`,
a Postgres driver, and `alembic` to `pyproject.toml`. Add
`docker-compose.yml` and a CI Postgres service. Add `POLTIKA_DATABASE_URL`
to the ADR-0011 deployment convention. Add the new store directory to
`REPOSITORY_STRUCTURE.md` before creating it.
