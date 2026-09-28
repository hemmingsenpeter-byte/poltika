# Review Packet: hosted pilot hardening — 2026-09-28

**Label: author preflight** (Claude Code, the author). Not an independent or
cross-model review.

## Review inputs

- PR/diff: branch `fix/hosted-hardening`, base `origin/main` 70e77cc.
  Changed: `src/poltika/api/{hardening,main,microsim}.py`,
  `tests/unit/api/{test_hardening,test_microsim_api}.py`,
  `docs/pilot/HOSTING.md`, `REPOSITORY_STRUCTURE.md`, `CHANGELOG.md`.
- Primary sources: none. No policy value, rule, fixture or protected
  expected value is touched; this is hosting security only.
- Specification: `docs/pilot/HOSTING.md` (password-protected pilot),
  `api/access.py` (existing HTTP Basic protection).
- Trigger: the live Render service answered every route with 200 and no
  password (checked 2026-09-28: `/analyst`, `/docs`, `/openapi.json`).
  `POLTIKA_ACCESS_PASSWORD` was unset and the service was evidently not
  running with the image's `POLTIKA_REQUIRE_ACCESS_PASSWORD=1`.

## Expected behaviour (written by the author, who knew the rationale)

- Every HTTP response, including 401 and 413, carries CSP (no framing, no
  other origins beyond the jsDelivr/Google Fonts assets `/docs` and
  `/redoc` load), `nosniff`, `X-Frame-Options: DENY`, `no-referrer`, HSTS,
  `Permissions-Policy`; no header duplicated.
- A request body over 64 KiB gets 413, whether declared by
  `Content-Length` or seen while streaming; a malformed length is refused;
  a body at the limit reaches the route.
- `POST /microsim/runs` and `GET /microsim/runs/{id}` compute one at a
  time; a concurrent one gets 429 with `Retry-After: 30`; cheap routes are
  unaffected; the lock is released on success and on error.

## Commands and results

- `uv run pytest -q`: 1200 passed, 22 skipped, 2 deselected (exit 0).
- `uv run ruff check src tests`: all checks passed.
- `uv run mypy --strict src`: no issues in 74 source files.
- `git diff --check`: clean.
- Headless Chrome against a local uvicorn: `/docs` (Swagger rendered, 12
  operation groups), `/redoc` (rendered), `/analyst`, `/analyst/microsim`
  (inline script fetched and showed the population id); no CSP violations
  logged.

## Adversarial probes

| Probe | Result |
|---|---|
| Body exactly 64 KiB / 64 KiB + 1 | 422 (reached route) / 413 |
| `Content-Length: -1` | 413 |
| GET with a 64 KiB + 1 body | 413 |
| Chunked 70 KB body through real uvicorn (no length) | 413 with JSON detail |
| Oversized body with wrong credentials | 413 (size checked before credentials; no credential oracle) |
| 401 response | one CSP header, security headers present |
| Lock held, second run / run fetch | 429 + `Retry-After: 30`; `/microsim/population` 200 |
| Measured cost | `POST /microsim/runs` ~25 s, `GET /microsim/runs/{id}` ~2.3 s, others < 0.3 s |

## Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| None found in the author pass | — | — |

## Not verified

- The Render runtime (Docker vs native Python) and the password's value are
  operator settings outside the repository.
- CSP in browsers other than Chrome.

## Author response

- Per-address rate limiting deliberately not added: uvicorn runs with
  `--forwarded-allow-ips='*'`, so a client-supplied `X-Forwarded-For` is
  trusted and a per-IP limit is spoofable. The password gates access; the
  lock bounds the one expensive route.
- `/docs` kept (behind the password): `HOSTING.md` offers it to testers.
- CSP allows `'unsafe-inline'` scripts because both pages are inline HTML;
  moving them to static files would allow a stricter policy later.

## Deferred Codex audit

- Final commit on `fix/hosted-hardening`; questions: Is 64 KiB right for future intake
  payloads? Is a process-wide lock acceptable, or should runs move to a
  queue when the store is in use?

## Revision, 2026-09-28: Render fail-closed dropped

Pete decided to run the hosted service without a password for now. The
first commit also made the app refuse to start on Render without
`POLTIKA_ACCESS_PASSWORD` (via Render's `RENDER` variable); with no password
set, that would have made every later Render deploy fail. That part
(`api/access.py` and its test) is reverted to `main`. Consequence, recorded
here deliberately: **the live service remains open to anyone with the
address.** The headers, body limit and run lock still apply. Requiring a
password on Render again is an open decision for Pete.
