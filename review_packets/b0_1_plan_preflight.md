# Review Packet: Task B0.1 plan and governance (B0.1.0) — 7 October 2026

**Label:** author preflight plus a fresh same-model check (`poltika-reviewer`,
Sonnet). This is not an independent GPT/Codex review.

## Review inputs

- PR/diff: `prog/b0.1-web-plan`, base `origin/main` `4c33c63`; reviewed head
  `661d722`, fixes at `357bbbd`.
- Paths: `BUILD_PLAN_B0_1_WEB.md`, `adr/0023-web-frontend-product-surface.md`,
  `BUILD_PLAN_PROGRAMME.md`, `PROGRAMME_STATUS.md`, `PETE_QUEUE.md` (Q15),
  `docs/decision_log.md` (D24, D25), `REPOSITORY_STRUCTURE.md`,
  `ARCHITECTURE.md`.
- Sources: none. This PR records Pete's 7 October 2026 Tier C answers and
  engineering choices. It adds no policy value, rule or source claim.
- Tests: `uv run --extra dev pytest -q tests/acceptance/test_programme_authority.py
  tests/acceptance/test_v0_3_release_gate.py tests/unit/test_epistemic_constitution.py`
  → 22 passed, 8 skipped. `git diff --check` clean. A relative-link script
  over the changed files found no broken links (lychee not installed locally).

## Independent review

### Expected behaviour (derived before reading the author's rationale)

The diff records only Pete's four decisions as Tier C. It keeps ADR-0018
unaccepted, changes no calculated amount, and respects the `data/` and
Source Archive boundaries. It names only files, routes and variables that
exist, and its numbering does not collide with open PRs #183 and #184.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 (P2): the ADR and plan status read as if Pete approved every choice, including the Tier A/B engineering ones | INTERPRETATION_AMBIGUITY | Fixed: decisions 1–4 attributed to Pete (D24), 5–13 to Claude Code (D25) |
| R2 (P3): "existing Workbench run path" — runs are created by `POST /microsim/runs` | SPEC_ERROR | Fixed |
| R3 (P3): the boundary test also forbids naming `data/metadata` outside `data/` | ARCHITECTURE_ISSUE | Fixed: env-var location plus one named `ALLOWED` entry, done in B0.1.1 |
| R4 (P3): persisting reform runs overlaps Task 14 | ARCHITECTURE_ISSUE | Fixed: plan and ADR say Task 14 owns replay and may supersede the tables |
| R5 (P3): the "B0.1." paragraph rendered unlike the task list | SPEC_ERROR | Fixed: bold label, normal block |
| Author-found: the first draft let the dataset endpoint read the Source Archive, which ADR-0022 closes | ARCHITECTURE_ISSUE | Fixed before commit |

Not verified: the `web` CI job and Node behaviour on the runner, which come
in B0.1.3.

## Author response

The engineering choices are recorded with options and reversal in D25.

## Resolution

All findings fixed at `357bbbd`. Deferred Codex audit: none required for a
docs-only PR that shows no amounts. Later B0.1.2 and B0.1.4 get review-queue
rows.
