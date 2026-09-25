# Poltika

Poltika is a policy-specification and implementation repository for New Zealand support-related policy logic.

It is a deterministic simulator: every rate, threshold and rule comes from a cited primary source. Every result is `calculated`, `needs_review` or `unsupported`; a missing fact is never treated as zero, and each result carries a provenance report.

## Where to start

- [BUILD_PLAN.md](BUILD_PLAN.md) — what's being built now, in what order, and v0.1 acceptance criteria
- [ARCHITECTURE.md](ARCHITECTURE.md) — how Poltika works, conceptually and technically
- [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) — where every component belongs and the dependency rules between layers
- [ROADMAP.md](ROADMAP.md) — what comes after v0.1
- [BUILD_PLAN_v0_1_5.md](BUILD_PLAN_v0_1_5.md) — the v0.1.5 plan
- `doctrine/` — decisions that are fixed and not to be re-litigated
- [docs/demo/v0_1/](docs/demo/v0_1/README.md) — one household run end to end through both policies, with its provenance report and limitations
- [CHANGELOG.md](CHANGELOG.md) — what v0.1 contains
- [docs/pilot/GUIDE.md](docs/pilot/GUIDE.md) — run Poltika with Docker and use the analyst page

## Current status

v0.1.0 is released (tag `v0.1.0`, 25 September 2026). It models Working for Families (2026-27) and the Accommodation Supplement (weekly) inside a scoped domain, plus their interaction for one household. See [CHANGELOG.md](CHANGELOG.md).

Results are conditional simulations built from caller-asserted facts. They are not entitlement determinations.

**No WFF total yet.** The 2026-27 in-work tax credit base rate is still
`needs_review` in `policy.yaml`: the temporary rate can be reversed early by
Order in Council, so it is not confirmed for the whole year (Task 26b). The
in-work tax credit is therefore never `calculated`, and the WFF total is only
given when all four components are, so v0.1 gives no WFF total for any
household. The other three components are unaffected.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```sh
uv sync --extra dev
uv run --extra dev pytest -q                       # spec, benchmark and regression tests
uv run --extra dev uvicorn poltika.api.main:app    # API; see /docs, and /analyst for the page
```

- **Policy files:** the API reads `policy_specs/` from the checkout. Set `POLTIKA_POLICY_SPECS_DIR` to use a mounted copy (ADR-0011).
- **Stored scenarios:** the `/scenarios` routes need PostgreSQL. Set `POLTIKA_DATABASE_URL`, for example `postgresql+psycopg://user@host/db` (ADR-0013). Without it they return 503; the other routes still work.
- **Database schema:** the API doesn't migrate the database itself. Before first use, and after upgrading, run:

  ```sh
  uv run python -c "import os; from poltika.scenarios.store import migrate; migrate(os.environ['POLTIKA_DATABASE_URL'])"
  ```
- **Store tests:** tests marked `postgres` start a throwaway server when `initdb` and `pg_ctl` are on PATH, and skip otherwise.
- **Slower tests:** `-m installed_artifact` builds and runs the wheel; `-m code_replay` replays a stored run on its original commit. CI runs both.
