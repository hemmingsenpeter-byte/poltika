# Poltika

<!-- poltika:master-build-order=BUILD_PLAN_PROGRAMME.md -->

Poltika is a policy-specification and implementation repository for New Zealand support-related policy logic.

It is a deterministic simulator: every rate, threshold and rule comes from a cited primary source. Every result is `calculated`, `needs_review` or `unsupported`; a missing fact is never treated as zero, and each result carries a provenance report.

## Where to start

1. [docs/ORIENTATION.md](docs/ORIENTATION.md) — supported behaviour and runnable examples.
2. [ARCHITECTURE.md](ARCHITECTURE.md) — release, current and long-term architecture.
3. [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) — component locations and dependencies.
4. [BUILD_PLAN_PROGRAMME.md](BUILD_PLAN_PROGRAMME.md) — the single current master build order (ADR-0021).
5. [PROGRAMME_STATUS.md](PROGRAMME_STATUS.md) — live tasks, evidence, owners and blockers.
6. Relevant active lane: [BUILD_PLAN_v0_3.md](BUILD_PLAN_v0_3.md) for the household economic kernel; [BUILD_PLAN_v0_1_6.md](BUILD_PLAN_v0_1_6.md) for statutory maintenance. [BUILD_PLAN_v0_2.md](BUILD_PLAN_v0_2.md) supports release completion only.
7. [PETE_QUEUE.md](PETE_QUEUE.md) — decisions and actions reserved to Pete.
8. `doctrine/` and accepted `adr/` records — governing constraints and decisions.

[ROADMAP.md](ROADMAP.md) summarises direction; it sets no separate backlog.
The [campaign-policy and NZ Budget use-case plan](docs/programme/POLICY_CLAIMS_BUDGET_WORKFLOWS.md) maps
bounded evidence-reviewed proposal intake, optional example-household
pilot, recurring Budget analysis and historical replay to existing programme
gates; **none is implemented merely by this plan**. A public explorer remains
a later, separately gated Phase O capability.
[BUILD_PLAN.md](BUILD_PLAN.md) is the frozen v0.1 record, retained for substantive
doctrine and existing anchors. [docs/archive/](docs/archive/README.md) contains
historical planning and cannot determine current work.

[CHANGELOG.md](CHANGELOG.md), [docs/releases/](docs/releases/V0_1_BASELINE.md),
[the demo](docs/demo/v0_1/README.md) and [the pilot guide](docs/pilot/GUIDE.md)
provide change evidence, measured limitations and runnable workflows.

## Current status

v0.1.0 is released (tag `v0.1.0`; published 26 September 2026). It models Working for Families (2026-27) and the Accommodation Supplement (weekly) inside a scoped domain, plus their interaction for one household. See [CHANGELOG.md](CHANGELOG.md).

As verified on 3 October 2026, evidence/explanation and hosted-pilot capabilities
are implemented, but v0.1.5 is untagged and its external-user gate is outstanding.
The Workbench registry, reform checks, result blocks and CSV/Excel exports exist
as a backend; a complete analyst Workbench interface remains to be built
(ADR-0018 accepted 12 October 2026).

v0.2 (static population microsimulation) is built and its independent review is
recorded in the review queue; Pete’s `v0.2.0` tag is outstanding. It runs the same two engines over a synthetic development population derived from Stats NZ tables (`docs/releases/V0_2_POPULATION_METHODOLOGY.md`), compares its baseline with Inland Revenue and MSD figures (`docs/releases/V0_2_CROSS_VALIDATION.md`), and labels every population result as not an estimate for New Zealand (`docs/releases/V0_2_LIMITATIONS.md`).

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
reviewed domain at a time (`BUILD_PLAN_PROGRAMME.md` Phases B and H). What it
models today:

| Domain | State |
| --- | --- |
| Working for Families (2026-27) | Implemented and reviewed (v0.1); in-work tax credit `needs_review` |
| Accommodation Supplement | Implemented and reviewed (v0.1) |
| Personal income tax | Not started: household lane, Phase B |
| Jobseeker Support, Sole Parent Support, Supported Living Payment | Not started: household lane, Phase B |
| NZ Super, Childcare and OSCAR Subsidies, KiwiSaver interactions, Paid Parental Leave | Deferred: Phase H, order determined by analytical demand |
| Student support, ACC levies and earnings compensation, Temporary Additional Support, Disability Allowance, other MSD assistance, Child Support | Deferred: Phase H, order determined by analytical demand |
| GST, company tax, other tax regimes, selected regulatory costs, Crown revenue and expenditure classifications | Deferred: sourced fiscal/domain requirements in Phases F/H/L |

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
