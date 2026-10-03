# Programme verification — 3 October 2026

Testing was performed by a separate GPT/Codex testing lead; no tracked file
in the shared `main` checkout was modified. This record describes observed
checks, not release acceptance or a complete security audit.

## Repository baseline

At `e52f5d35913fbb4b81c7b64c6caf6d446c158759`:

- Ruff passed; strict mypy passed on 80 source files; evidence coverage passed.
- Full default pytest: 1,262 passed, 22 skipped, 2 deselected, one environment
  setup failure. The temporary environment used `--no-install-project`, and
  the identity test's child process clears `PYTHONPATH`; it could not import
  `poltika`. This was a resolved REVIEWER_ERROR, not a code fix.
- The baseline wheel was installed into the isolated environment. Focused
  rerun of `test_identity_is_the_same_in_a_separate_process`: one passed.
  All 1,263 runnable selected tests passed across the run and rerun; the
  original single run is not described as green.
- Thirteen skips: missing local PostgreSQL binaries. Eight: deferred/unbuilt
  v0.3 rows including #128 review. One: missing external pilot. Installed
  artifact/code replay are separately selected, not implied by default pytest.

The locked dev environment fixed stale shared dependencies without changing
main. Docker and PostgreSQL are unavailable locally; their tests require CI.

## Existing hosting PR #140

At exact `ffa05168a34b29192ba1bff08622bd1328fe4c59`, an isolated snapshot's
existing installed-artifact test passed: built wheel installed in a fresh venv,
correct import origin, and WFF, AS and combined-household API probes. Its
PostgreSQL sub-probe was unavailable locally. No actionable finding in the
hosting addition; no CI or acceptance clearance is inferred.

## Security fix and negative probes

At `941cbc18a9c0dc9f4d96bc27726f778d05d56e8b`, separate probes verified:

- All action references immutable; tokens restricted; no checkout credential
  persistence; guard scripts and full-history checkout preserved.
- Read-only PR report; issue-only non-PR publisher without checkout/install
  or repository-code execution; explicit `GH_REPO` outside a git checkout.
- Stub `gh` issue create/update/no-due/list-error paths pass, with no external
  issue writes. Due counts 0/1/12 produce the expected advisory output.
- Bandit retains medium findings and blocks high severity, scanner errors,
  empty scans and malformed reports. An unsafe synthetic workflow makes
  pinned zizmor fail with exit 14. Real workflow scan has zero findings.
- Currency CLI ran without GitHub tokens: AS Due(0), WFF Due(3), exit 0.

Local Bash 3.2 cannot execute Ubuntu's `mapfile`; discovery was inspected
and the exact due/output branch executed separately. Hosted scheduled issue
publication was not exercised. Subsequent `f483fb90` changes only this PR's
review documentation; workflows remain identical to the tested revision.

Latest GitHub head `f483fb90b6bc98c12639b8f35c1caf073ead4ff5` has successful
test, pilot-image, both guards, links, pip-audit, source-currency, Bandit and
zizmor checks. The scheduled external-links and issue-publisher jobs correctly
skip on a PR. The test workflow includes PostgreSQL, installed-artifact and
retained-code replay, covering those local limitations.

## Separate final document checks

Fresh reviewer of #143 `75eb7a9..82990da` and #138 `e34e681..d868564` reports
no actionable findings. Complete diffs, issue YAML/form references, private
visibility/issues enabled, actual tooling, release-gate doctrine, tiers and
promotion safeguards were checked. Both whitespace checks passed. This is
fresh same-model review of GPT/Codex fixes, not independent Claude acceptance.

At the recorded heads, both PRs also have successful test, pilot-image and
guard checks: [#138 test](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37083113350)
and [#143 test](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37083111237).
The workflow includes the PostgreSQL and installed-artifact checks unavailable
locally. Passing CI does not clear delegated acceptance.

The source-scoping draft has its separate dated source check in #148.
All pending cross-model, policy, milestone, pilot and acceptance gates remain.
