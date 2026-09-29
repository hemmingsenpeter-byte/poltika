# Poltika

Poltika is a policy-specification and implementation repository for New Zealand support-related policy logic.

It is a deterministic simulator: every rate, threshold and rule comes from a cited primary source. Every result is `calculated`, `needs_review` or `unsupported`; a missing fact is never treated as zero, and each result carries a provenance report.

## Where to start

- [docs/ORIENTATION.md](docs/ORIENTATION.md) — read first: what v0.1 does now, on one page, with runnable examples
- [BUILD_PLAN.md](BUILD_PLAN.md) — what's being built now, in what order, and v0.1 acceptance criteria
- [ARCHITECTURE.md](ARCHITECTURE.md) — how Poltika works, conceptually and technically
- [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) — where every component belongs and the dependency rules between layers
- [BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md) — the programme plan (ADR-0018): Pete's master build order of 33 steps in eight phases, what already exists against each step, tasks, validation gates, month targets and decisions
- [ROADMAP.md](ROADMAP.md) — the master technical roadmap: the question Poltika answers, the north star, the eight phases and their milestones, and the permanent layer
- [BUILD_PLAN_v0_1_5.md](BUILD_PLAN_v0_1_5.md) — the v0.1.5 plan
- [BUILD_PLAN_v0_1_6.md](BUILD_PLAN_v0_1_6.md) — the v0.1.6 plan: keep v0.1 current past 1 April 2027
- [BUILD_PLAN_v0_2.md](BUILD_PLAN_v0_2.md) — the v0.2 plan: static population microsimulation (ADR-0014)
- [ROADMAP_REALIGNMENT.md](ROADMAP_REALIGNMENT.md) and [BUILD_PLAN_v0_3.md](BUILD_PLAN_v0_3.md) — the roadmap realignment (ADR-0015) and the v0.3 plan
- `doctrine/` — decisions that are fixed and not to be re-litigated
- [docs/demo/v0_1/](docs/demo/v0_1/README.md) — one household run end to end through both policies, with its provenance report and limitations
- [CHANGELOG.md](CHANGELOG.md) — what v0.1 contains
- [docs/pilot/GUIDE.md](docs/pilot/GUIDE.md) — run Poltika with Docker and use the analyst page

## Current status

v0.1.0 is released (tag `v0.1.0`, 25 September 2026). It models Working for Families (2026-27) and the Accommodation Supplement (weekly) inside a scoped domain, plus their interaction for one household. See [CHANGELOG.md](CHANGELOG.md).

v0.2 (static population microsimulation) is built and awaiting independent review before `v0.2.0` is tagged. It runs the same two engines over a synthetic development population derived from Stats NZ tables (`docs/releases/V0_2_POPULATION_METHODOLOGY.md`), compares its baseline with Inland Revenue and MSD figures (`docs/releases/V0_2_CROSS_VALIDATION.md`), and labels every population result as not an estimate for New Zealand (`docs/releases/V0_2_LIMITATIONS.md`).

Results are conditional simulations built from caller-asserted facts. They are not entitlement determinations.

**No WFF total yet.** The 2026-27 in-work tax credit base rate is still
`needs_review` in `policy.yaml`: the temporary rate can be reversed early by
Order in Council, so it is not confirmed for the whole year (Task 26b). The
in-work tax credit is therefore never `calculated`, and the WFF total is only
given when all four components are, so v0.1 gives no WFF total for any
household. The other three components are unaffected.

## Policy coverage

Poltika is building a deterministic policy kernel for New Zealand's
household tax-and-transfer system, then firms and government, one
reviewed domain at a time (`BUILD_PLAN_PROGRAMME.md` Step 3). What it
models today:

| Domain | State |
| --- | --- |
| Working for Families (2026-27) | Implemented and reviewed (v0.1); in-work tax credit `needs_review` |
| Accommodation Supplement | Implemented and reviewed (v0.1) |
| Personal income tax | Planned: v0.3, Tier 1 |
| Jobseeker Support, Sole Parent Support, Supported Living Payment | Planned: v0.3, Tier 1 |
| NZ Super, Childcare and OSCAR Subsidies, KiwiSaver interactions, Paid Parental Leave | Planned: Step 3 lane 3C |
| Student support, ACC levies and earnings compensation, Temporary Additional Support, Disability Allowance, other MSD assistance, Child Support | Planned: Step 3 lane 3D |
| GST, company tax, other tax regimes, selected regulatory costs, Crown revenue and expenditure classifications | Planned: Step 3 lane 3E |

Anything not listed as implemented isn't modelled. A household that
depends on it gets `unsupported` or `needs_review` for that part, never a
zero.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```sh
uv sync --extra dev
uv run --extra dev pytest -q                       # spec, benchmark and regression tests
uv run --extra dev uvicorn poltika.api.main:app    # API; see /docs, and /analyst for the page
```

- **Policy files:** the API reads `policy_specs/` from the checkout. Set `POLTIKA_POLICY_SPECS_DIR` to use a mounted copy (ADR-0011).
- **Population runs (v0.2):** the `/microsim` routes and the `/analyst/microsim` page run reforms across the population file named by `POLTIKA_POPULATION_PATH`, for example one written by `python -m poltika.scenarios.microsim.synthetic <spec.yaml> <population.json>`. Without it they return 503. A synthetic population's results are labelled as not an estimate for New Zealand.
- **Stored scenarios:** the `/scenarios` routes need PostgreSQL. Set `POLTIKA_DATABASE_URL`, for example `postgresql+psycopg://user@host/db` (ADR-0013). Without it they return 503; the other routes still work.
- **Database schema:** the API doesn't migrate the database itself. Before first use, and after upgrading, run:

  ```sh
  uv run python -c "import os; from poltika.scenarios.store import migrate; migrate(os.environ['POLTIKA_DATABASE_URL'])"
  ```
- **Store tests:** tests marked `postgres` start a throwaway server when `initdb` and `pg_ctl` are on PATH, and skip otherwise.
- **Slower tests:** `-m installed_artifact` builds and runs the wheel; `-m code_replay` replays a stored run on its original commit. CI runs both.
