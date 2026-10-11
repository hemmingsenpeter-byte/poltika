# Review Packet: Task B0.1.3 web shell — 8 October 2026

**Label:** author preflight (implementation by a briefed Sonnet worker,
checked by the orchestrating session) plus a fresh same-model check
(`poltika-reviewer`). This is not an independent GPT/Codex review. The shell
displays only API values and adds no amount, so no review-queue row is needed.
The scenario workspace that shows amounts is B0.1.4.

## Review inputs

- Diff: B0.1.3 commits on `prog/b0.1.3-web-shell` (stacked on #187).
- Plan: `BUILD_PLAN_B0_1_WEB.md` B0.1.3; ADR-0023.
- Checks:
  - web: lint, typecheck, Vitest (42) and the static build all pass.
  - Python: ruff and `mypy --strict` are clean; `tests/unit/api` 227 passed;
    `test_web_static.py` 40 passed.
- Deep-link proof: built export served by uvicorn. Playwright Chromium on
  macOS 12 kept `/models/wff_engine`, `/data/{id}` and
  `/scenarios/{id}/runs/{id}` after hydration and rendered the model name,
  with no console errors.

## Independent review

### Expected behaviour

- One origin, with every page behind the password and `/healthz` open.
- API clients keep getting JSON.
- No traversal through the static file route.
- The frontend makes no calculation and never turns a missing value into 0.
- P3 precision, and no gated copy.
- CI actions pinned on the self-hosted runner.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 (P3): Docker Node stage on an end-of-life Node 20 tag | ARCHITECTURE_ISSUE | Fixed: `node:22-slim` |
| R2 (P3): CI relies on the runner's Node, unpinned | ARCHITECTURE_ISSUE | Mitigated: the job fails on Node under 20, and the audit job prints the version |
| R3 (P3): cache headers were `public` behind Basic auth | CODE_ERROR | Fixed: every web cache header is `private`; tests updated |

Not verified locally: the Docker build (no Docker on the Mac). The CI
`pilot-image` job builds it and smoke-tests `/`, `/models` and the 401.
