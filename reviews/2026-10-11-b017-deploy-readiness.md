# B0.1.7 deployment readiness (verification only), 11 October 2026

Reviewer: Claude Code (Sonnet 5.5). Basis: main `b19e764`; PR #194's proposal at
`origin/codex/q11-q15-proposal-20261009`; BUILD_PLAN_B0_1_WEB.md:187-199; PETE_QUEUE Q15. No Render tool was
used, nothing was created or changed, no secret was read, and no Docker build or deployment was attempted
(no Docker on this Mac, decision D21). Focused tests run: `pytest -q tests/unit/api/test_access.py
tests/unit/api/test_web_static.py tests/unit/api/test_hardening.py` gave 78 passed, 1 skipped (the skipped
test needs a built `web/out`, which does not exist in this worktree).

Legend: Ready = evidenced in code or config; Gap = missing or unproven; Pete = needs his decision or action.

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Image builds web export and serves it from one origin | Ready on paper (not built here) | `Dockerfile:8-13` Node stage runs `npm run build`; `Dockerfile:30` copies `/web/out` to `/app/web`; `Dockerfile:51` sets `POLTIKA_WEB_DIR=/app/web`; `web/next.config.mjs:7` `output: "export"`; dev-only rewrites (`:12-23`). `.dockerignore` excludes `web/out`, `web/node_modules`, `.git`, so no local build output or history enters the image. |
| 2 | Web routes and API routing | Ready | `api/web.py` `_UI_ROUTES` (dynamic ids map to the `_` placeholder page); only `GET`/`HEAD` preferring `text/html` get pages, so JSON clients still reach the API; tests in `test_web_static.py` pass (except the one needing a built export). |
| 3 | Password required; unauthenticated gets 401 | Ready | `api/access.py` BasicAuthMiddleware returns 401 on every route except `/healthz`; middleware order `main.py:119-122` puts auth outside the web app, so pages need the password; `test_access.py` passes. |
| 4 | Fail-closed when password unset | Ready | `Dockerfile:52` sets `POLTIKA_REQUIRE_ACCESS_PASSWORD=1`; `main.py:84` calls `configured_credentials()` in the lifespan, which raises `AccessConfigError` on empty password (`access.py:40-45`), so the container does not start; the same check runs per request, so removing the password later gives errors, not open access; `test_required_password_refuses_to_start` (`test_access.py:91-98`) passes. A source checkout without the flag stays open by design. |
| 5 | `/healthz` | Ready | `main.py:125-128` returns `{"status":"ok"}`; open path `access.py` `OPEN_PATHS`; HOSTING.md:77 sets the health check path. It confirms the process only, not database reachability. |
| 6 | Scenario persistence | Ready in design, Gap in proof | Store is PostgreSQL via SQLAlchemy; `scenarios/store.py:125-129` raises when `POLTIKA_DATABASE_URL` is unset, and `/api/v1/scenarios` and `/scenarios` then answer 503 (`v1_scenarios.py:14`). There is no SQLite or file fallback and no state on the container disk, so an ephemeral filesystem loses nothing once Postgres is attached. No automated test restarts the app against the same database (grep for restart tests found none): the "deep link survives a restart" criterion is unproven until the live smoke. |
| 7 | Migrations on deploy | Ready | `deploy/entrypoint.sh:8-10` runs `migrate()` when the URL is set under `set -eu`, so a migration failure stops the container instead of serving a half-schema. Upgrade from the first migration was not exercised here. |
| 8 | Render setup instructions include the database | Gap | `docs/pilot/HOSTING.md:67-77` lists only `POLTIKA_ACCESS_PASSWORD` and `POLTIKA_ACCESS_USER`. Following it gives a service with no database, so stored scenarios return 503. B0.1.7's HOSTING update is still owed (BUILD_PLAN_B0_1_WEB.md:195-196). |
| 9 | `docs/web/FRONTEND.md`, `web/README.md` | Gap | `docs/web/` does not exist (B0.1.7 deliverable, BUILD_PLAN_B0_1_WEB.md:192-195). |
| 10 | Secrets | Ready | Nothing committed: password only via environment; `.env` is gitignored; `compose.yaml:25` refuses to start without the variable (`:?`). Credentials compared in constant time and never logged (`access.py` docstring). The database URL contains a password and must also be set only in Render. |
| 11 | Single shared password, no per-user ownership | Pete (known) | Documented in HOSTING.md on branch `fix/audit-191-hardening-20261011`; PR #194 proposal says synthetic or public data only. Not a deploy blocker for synthetic use. |
| 12 | Concurrency: one worker | Ready | `entrypoint.sh:11` runs a single uvicorn process; the population-run lock is per process (HOSTING.md), consistent with #194's single-worker advice. |
| 13 | HTTPS and proxy headers | Ready | `entrypoint.sh:11` `--proxy-headers --forwarded-allow-ips='*'` is acceptable only because the service is reachable solely through Render's proxy; on a host exposed directly, the wildcard lets a client forge `X-Forwarded-*`. HSTS and CSP are set by `SecurityHeadersMiddleware` (HOSTING.md). |
| 14 | Existing service and workspace | Pete | Which Render workspace holds `poltika.onrender.com`, its runtime and region are unverified (Render access not used here). |
| 15 | PostgreSQL plan and spend | Pete | #194 recommends the smallest paid plan, same region, private connection URL; budget is Pete's. |
| 16 | `web` required check (A6) | Pete | `web` job exists (`tests.yml`); ruleset change is Pete's (Q15). |

## Code fixes

None made. The two real gaps (8, 9) are documentation owed by B0.1.7 itself, and the persistence-restart gap (6)
is best closed with a Postgres-backed test in the web/API lane that other agents are editing, so I did not add a
branch `fix/b017-readiness-20261011`.

## Smallest remaining path to "done when" (BUILD_PLAN_B0_1_WEB.md:197-199)

Pete: confirm the workspace and create the paid database; set `POLTIKA_DATABASE_URL` and
`POLTIKA_ACCESS_PASSWORD` in Render himself. Then: update HOSTING.md steps; write `docs/web/FRONTEND.md` and
`web/README.md`; deploy; smoke: 401 without password, Home/Scenarios/Models/Data with it, create a run, restart
the service, open the run's deep link.
