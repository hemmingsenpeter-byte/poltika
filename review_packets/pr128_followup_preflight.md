# PR #128 follow-up — author preflight

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex project manager, resolving recorded independent findings.
- Base: `e52f5d35913fbb4b81c7b64c6caf6d446c158759`.
- Original independent review: `reviews/2026-10-03-pr128.md`, findings committed
  before fixes at `03d7bfd`. The original author was Claude Code.
- Mechanical inputs: ADR-0016; `scenarios/conditional.py`; WFF approved exact
  Decimal/presentation contract; outcome categories; original and follow-up
  diffs; existing golden inputs; negative summary probes.
- Label: author preflight; the author knows the fix rationale. Separate
  testing, same-model checking and independent Claude review are recorded below.
  Claude delegated acceptance and integration remain pending.

## Contract and scope

The deterministic engine's amount and result identity remain unchanged.
Summary text retains exact amounts, annual/weekly units, conditional assignment,
evidenced exclusions, unsupported coverage, points/bounds and cap limitations.
Verification rejects incomplete or altered fixed text/figure metadata.
No protected amounts, source/spec rules or loader/engine behavior change.
The analyst's existing range strings are aligned with the corrected certainty
limit; DOM construction still uses text nodes. No runtime agent abstraction.

The original review is complete, but confirmed defects keep the assurance row
and release gate open while fixes await review and integration. Historical
cross-model waivers do not extend to this new follow-up.

## Checks observed

- The testing lead's corrected source-path baseline: 233 passed, eight skips
  (seven unbuilt capability rows plus #128's open assurance row).
- An initial wheel-only invocation omitted `PYTHONPATH=src`, so API tests
  looked for unpackaged assets relative to the installed wheel. This is a
  corrected REVIEWER_ERROR, not a product finding or a green original run.
- New selected regressions before fix: 13 failed, three passed. After fix:
  16 passed, 32 deselected. API half-cent test compares text with the engine's
  output rather than introducing a statutory expected number.
- Ruff and strict mypy (80 files) pass. Author inspected the complete fixed
  diff in the separate detached preflight worktree at `948fb24`.
- Separate testing at `948fb243d490a50ef87dc3030904dacf72c15d55`: seven-file
  focused suite 254 passed, eight expected skips; adversarial probes 15/15;
  nine golden calculation payloads/policy hashes/scenario IDs unchanged.
  Result IDs match when CodeIdentity is held constant; actual runtime code
  commits differ, so cross-commit runtime-ID equality is not claimed.
- Actual API half-cent/status transport and tampered-renderer failure pass.
  Server JavaScript ran against seven real-resolution fixtures in a temporary
  Node DOM shim; no browser layout/interaction test is inferred.
- Separate GPT/Codex security/simplification check found no actionable issue;
  it had prior knowledge of the fix direction and is not fresh cross-model review.

## Independent Claude review

An actual local Claude Code session used the repository's `poltika-reviewer`
procedure with model `claude-sonnet-5`, restricted Read/Grep/Glob tools,
no session persistence and no mutation tools. It independently derived the
contract before the diff at `e52f5d3..948fb24`. It returned **Approve**, with
no outstanding finding, after 32 read-only turns and no permission denial.
Exact Decimal, evaluated-branch certainty, exclusion categories, complete
fixed text/figure inventory, caller contracts, test cases, DOM construction
and truthful open-gate records were inspected. It did not execute tests/lint
or audit new statutory sources. Test results support this review separately.

Code/tests remain unchanged after the reviewed SHA. Later commits only record
checks and draft PR #150. Latest-head GitHub CI is checked separately; the
review verdict is input to delegated acceptance, not a merge action.

No release or independent Claude acceptance is claimed by this packet.
