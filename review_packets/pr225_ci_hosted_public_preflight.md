# Review Packet: CI back on GitHub-hosted runners; public repository (PR #225) — 2026-10-16

Label: **author preflight**, plus one fresh same-model `poltika-reviewer`
pass. Not an independent GPT/Codex review. No `policy_specs/`,
`engines/simulator/` or calculated amount is touched, so ADR-0020 rule 4
(the review-queue row) does not apply.

## Review inputs

- PR/diff: #225, base `origin/main`, reviewed head `5def79f`; fixes in the
  next commit.
- Sources: decision log D21 (its revert path) and D33; the pre-D21
  workflows at `dd2c485^`; ruleset 24478578's ten required contexts.
- Test command and output: CI on `5def79f`, all on `ubuntu-latest`: every
  required check passed (`test` 5m2s, `pilot-image` 6m5s, `web` 1m30s).
  Locally: all workflows parse; `zizmor@1.30.1 --offline
  --strict-collection` no findings; offline lychee v0.24.2 0 errors; the
  four test files that read workflows or repository docs, 40 passed and 16
  skipped.

## Independent review

### Independently derived expected behaviour

The author derived these before writing the diff, so they are not
independent of its rationale.

1. All ten required contexts are still produced, with unchanged names, and
   none can be skipped on a pull request.
2. No job is skipped for a fork; no `pull_request` job sees a secret or a
   write token.
3. Linux steps match the pre-D21 versions proven on Ubuntu.
4. Every changed document is true against the repository settings.

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| R1 P3: `PROGRAMME_STATUS.md` said `pete-mac-1` was deregistered; GitHub still lists it (offline, a stranded job). | SPEC_ERROR | Found by author and reviewer. |
| R2 P3: `PROGRAMME_STATUS.md` said nine required checks; the ruleset has ten. | SPEC_ERROR | Predates #225. |
| R3 P3: `BUILD_PLAN_B0_1_WEB.md` said the `web` job is self-hosted. | SPEC_ERROR | ADR-0023 and review packets are historical and stay. |
| R4 P3: lychee binary no longer pinned. | REVIEWER_ERROR | lychee-action v2.9.0 (SHA-pinned) defaults `lycheeVersion` to v0.24.2, the version D21 pinned. |
| R5 nit: `external-links` reports through `jobSummary`. | — | The pre-D21 form, restored. Runs weekly only. |
| Q24 numbering collides with #223 and #224 (Q24, Q25). | SPEC_ERROR | The licence item is Q26. |

## Author response

The repository settings changed outside the diff are listed in D41 and the
PR body.

## Resolution

R1–R3 and the numbering are fixed in the commit after `5def79f`; R1's
deletion of the registration is a Q20 to-do. R4 and R5 need no change.

## Deferred Codex audit

None required (rule 4 does not apply). If GPT/Codex reviews it later:
the final head of #225, the settings in D41, and whether anything in the
history or `reviews/` should not be public.
