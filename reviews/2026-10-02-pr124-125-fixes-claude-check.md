# PRs #124 and #125: Claude Code's independent check of the GPT/Codex fixes

- Reviewed commit: `8d7e7b122750fd4e11021380b61894512a9fabe6` ("fix(api):
  address PR124 and PR125 review findings"), merged in #131.
- Findings checked: R2 and R3 in `reviews/2026-09-28-pr122-127.md`.
- Reviewer: a fresh-context Claude Code subagent (Sonnet). It derived the
  expected fixes from the findings and "Expected behaviour" before
  reading the diff, and read "Author response and limits" only after
  reaching its verdict. The orchestrating Claude Code session (Opus) then
  read the code diff itself.
- This is the independent check the review queue asks for. Pete still
  accepts.

## Verdict

Approve. Both findings are fixed. There are no regressions and no new
findings.

## Per finding

- **R2 (#124, `src/poltika/api/access.py:50`): fixed.** The scheme check
  is now `header[:6].lower() != b"basic "`.
  - Bytes `.lower()` is ASCII-only, so no Unicode case-folding applies.
  - Valid credentials are accepted under `Basic`, `basic`, `BASIC` and
    `bAsIc`, and with two spaces after the scheme.
  - Each of these still returns 401: a wrong password (including a
    case-changed one), a wrong user, `Bearer`, `Basicx`, no space, the
    scheme alone, an empty header, a tab separator, a payload with no
    colon, and a missing header.
  - `/healthz` stays open.
  - The user and password comparison is unchanged: case-sensitive,
    through `compare_digest`.
  - Evidence: `tests/unit/api/test_access.py::test_auth_scheme_is_case_insensitive`,
    plus a probe.
- **R3 (#125, `src/poltika/scenarios/intake.py:117`): fixed.**
  `slot_from_label` now refuses a `wff.children.<field>` label without an
  index, with a `ValueError` that the API maps to 422.
  - A probe posted 1,089 label and answer combinations to
    `/household/intake`: every catalogue key under each scope, the
    `children[n].field` form, malformed child labels, and 11 answer
    strings. 38 returned 200, 1,051 returned 422, and none returned 500.
  - Valid indexed labels still work. An out-of-range index still gives
    422.
  - Only the `wff` catalogue has `children.` keys, so the other scopes'
    child labels are already refused as not catalogued.
  - Evidence: the three new parametrised cases in
    `tests/unit/api/test_intake_api.py`, plus the probe.

## Verification

- Targeted tests (access, intake API, intake): 93 passed.
- Full suite: 1196 passed, 22 skipped, 2 deselected.
- `ruff check src tests`: clean. `mypy --strict src`: no issues in 73
  files.
- No policy value or protected expected value changed.
