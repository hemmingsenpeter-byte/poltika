# Review Packet: income-tax module branch, author preflight, 2026-10-29

Label: **author preflight** (same model as the author; not an independent
GPT/Codex review). Branch `feat/income-tax-module-20261029` (no PR yet).
Base `origin/main` `2ac7eff`; final head reviewed `e3e98bf`. The record and
record-only fixes below are a later commit, so they are not part of the
reviewed head's code; no code, test or policy file changed after `e3e98bf`.

## Review inputs

- Diff: `git diff 2ac7eff..e3e98bf`, 26 files, +2376/-20. Lanes: (a) conformance
  matrix and 82 tests (`2e23365`, `7d45917`); (b) goldens, release-gate rows,
  limitations, records (`5bb3722`, `f7a23ec`); (c) `POST /income-tax/calculate`
  and `/api/v1/evidence` (`381ed31`, `8edab6b`, D54); (d) merge `e3e98bf`.
- Specification: `policy_specs/income_tax/specification.md`, `policy.yaml`
  (draft_pending_review, `policy_version` null), `golden_households.yaml`.
  No statutory value is introduced or changed by this branch.
- Authorship: I (Claude) did not write the lanes' prose in this session but the
  branch is Claude-authored, so I know the rationale; this pass is not blind.
- Not verified: primary NZ sources (no value changes, so none re-derived);
  GPT/Codex review; the content of golden expectations against the
  specification line by line (covered by lane reviewers).

## Independent review

### Expected behaviour (written from the contract before the rationale)

Every income-tax result is `needs_review` or `unsupported` with a null value;
a missing fact names itself and is never zero; a non-matching requested
version is refused; unknown request fields and numeric (non-string) money are
422; the policy directory is server-owned; docs say only what exists.

### Probes run (TestClient, real approved-draft policy)

float money 422; fractional `"25.5"` 200 `unsupported` IT_FRACTIONAL; negative
200 `unsupported` IT_NEGATIVE (D54); `NaN` and `1e400` 422; extra field
`policy_dir` 422; wrong `requested_policy_version` 409; null attestation 200
`needs_review` naming the fact; string `"true"` attestation 422; null date 422;
2027-04-01 200 `unsupported` date-outside-period; missing income 200
`needs_review`. No value was non-null. No internal path leaked.

### Commands

| Command | Result |
|---|---|
| `git diff --check 2ac7eff..e3e98bf` | exit 0, clean |
| `uv run --extra dev ruff check src tests` | exit 0, all checks passed |
| `uv run --extra dev mypy --strict src` | exit 0, no issues in 109 source files |
| `uv run --extra dev pytest -q -n auto` | 2382 passed, 65 skipped, 0 failed (run started before the record-only edits; those touch no code) |
| web `npm ci`, `npm run typecheck`, `npx vitest run` | typecheck clean; vitest 26 files, 165 tests passed |

### Findings

None at P1 or P2.

| # | Grade | Finding | Classification | Disposition |
|---|---|---|---|---|
| F1 | P3 | `PROGRAMME_STATUS.md` Task 12 row said "income tax is not on the API", false once the route landed. | TEST_ERROR (record) | Fixed here |
| F2 | P3 | `PROGRAMME_STATUS.md` Task 7 row was stale: "Next: the engine", "No engine". | ARCHITECTURE_ISSUE (record) | Fixed here, minimal |
| F3 | P3 | `review_queue.md` row named only the goldens branch and "Claude author preflight not yet run". | REVIEWER_ERROR (record) | Rewritten to this branch and this record |
| F4 | P3 | `changelog.d/income-tax-goldens-release.md` said "no production code changed", contradicting `income-tax-api.md` when read together. | TEST_ERROR (record) | Scoped to the lane |
| F5 | P3 | **CLAUDE.md "v0.1 at a glance"**: "MFTC needs an attested after-tax income. There is no income tax module." is now partly false (a draft engine, household mapping and API route exist; they feed nothing and give no amount). `docs/ORIENTATION.md` was updated; CLAUDE.md was not edited by this pass. | Record drift | **For the human owner**: suggest "There is no derived after-tax income: a draft income-tax module exists but gives no amount and feeds nothing." |
| F6 | P3 | `ARCHITECTURE.md:90` ("no income tax, main-benefit calculators...") is also stale. Not edited (architecture document). | Record drift | For the human owner or the integration owner |
| F7 | nit | 409 for a version mismatch reads "policy.yaml holds 'None'". Accurate, matches the WFF/AS shape, no leak. | n/a | None |

ORIENTATION, README, limitations and REPOSITORY_STRUCTURE agree: draft, never
an amount, feeds nothing, route exists, not in `/meta` or the Workbench. The
three changelog fragments are otherwise consistent. `BUILD_PLAN_v0_3.md`
throughput row still says the matrix and goldens branches are "open, no PR
yet"; true, left as is.

## Author response

No disagreements. The record fixes touch no code, policy, protected value or
decision.

## Deferred Codex audit

GPT/Codex review is outstanding for the whole branch (it touches
`policy_specs/` and adds an API over the income-tax engine). Inspect:
`golden_households.yaml` expectations against `specification.md`;
`src/poltika/api/income_tax.py` and D54 (optional version, no `ge=0`);
the conformance matrix's five escalations; F5 and F6. Renew review after any
later commit.
