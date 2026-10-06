# Independent Codex recheck — #162 never-build checks, 7 October 2026

## Findings

**Changes requested: one P2 / TEST_ERROR, R1.** The milestone-claim gate accepts
an explicit prohibited claim when an unrelated earlier clause contains “No”.
The #162 follow-up remains open until this is fixed and independently reviewed.
This pass is GPT/Codex cross-model review of Claude-authored tests; it is not
acceptance, author preflight or a waiver of Māori data governance/release gates.

## Review inputs

- [PR #162](https://github.com/hemmingsenpeter-byte/poltika/pull/162): final head
  `e637daaff4e244f3d4345d261409bc7503b8f0be`, base
  `d938cc507590ea4c4ff4a545a02478f79ce64e6a`, squash
  `5a8c17e889d7ffe8b5e9921b0e0c4803da1ff968`.
- Reviewer: GPT/Codex, 7 October 2026. Current main reviewed:
  `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`.
- Complete three-path diff read: `CHANGELOG.md`, `PROGRAMME_STATUS.md`,
  `tests/acceptance/test_v0_3_release_gate.py`. The test file is byte-identical
  from the #162 squash to current main. Read the complete current file and
  relevant API routes, population outputs and grouping/schema contracts.
- Contracts: retained Task 1.6; current Phase A and P5; epistemic constitution's
  “What Poltika never builds”; review/test/IP doctrine and repository boundaries.
  No policy source, protected expected value or calculated amount is changed.
  The `50000` reform override is an explicit synthetic scenario input.
- Not blind: an initial optional preview included historical diffs/messages.
  The expanded contract was then derived from doctrine before additional reads.

## Independently derived contract

Mechanical checks must reject party/plan scoring, false current milestone
claims and ethnicity/iwi disaggregation, while preserving synthetic population
labels. They should inspect actual supported outputs/pages and expose an
unbuilt validation-grade field through a named skip. They enforce existing
constraints; they do not decide governance, attach an empirical grade, or
promote a partial green release-gate run into release acceptance. A negation of
setup or login does not negate a digital-twin claim in the next clause.

## Independent finding

**R1 — P2 / proposed TEST_ERROR.**
`tests/acceptance/test_v0_3_release_gate.py:364` examines any negator within six
preceding words. `_negated` does not establish that it negates the milestone
claim, and `unreached_milestone_claims` does not separate colon/semicolon clauses.
Consequently both these positive claims return an empty violations list:

```text
'No setup required; Poltika is a digital twin.' -> []
'No login required: Poltika is a digital twin.' -> []
```

Expected: a `digital twin` violation, since the current milestone is unreached.
Actual: the unrelated “No” exempts the claim. The gate's own nearby comment says
an unrelated “no” elsewhere in the sentence does not excuse a claim.

Reproduced under the supported Python 3.12 environment by importing the actual
unchanged test module, with no source edits:

```python
import tests.acceptance.test_v0_3_release_gate as gate
print(gate.unreached_milestone_claims(
    "No setup required; Poltika is a digital twin."
))  # []
```

For the consuming-test reproduction, replace `_served_html_pages` **in memory**
with its existing `/analyst` and `/analyst/microsim` outputs, injecting
`<p>No setup required; Poltika is a digital twin.</p>` in `/analyst`. Invoke the
actual `test_no_user_facing_page_claims_an_unreached_milestone((None, None))`:
**it passes**, including its ordinary repository-document scan. The control
with `<p>Poltika is a digital twin.</p>` and the same page map **fails**. Restore
the original helper immediately. This verifies the gate failure, not just a
helper mismatch. No current shipped page was found carrying this false claim.

Impact: a prohibited claim can be added to a served page while this advertised
release-gate check stays green. Suggested fix: bind the permitted negation to
the milestone clause/phrase, then add these preceding-unrelated-negation cases
to the injection test while retaining legitimate absence/future wording.

| ID | Severity / proposed class | Status |
| --- | --- | --- |
| R1 | P2 / TEST_ERROR | Open; route a focused fix to Claude in a follow-up PR |

## Author rationale and verification

The author intends pure, bounded mechanical checks and explicitly names the
validation-grade skip. The original injection test passes, but lacks the two
preceding-clause cases above. That rationale does not remove R1.

Focused current-main command, run under the locked Python 3.12 environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /private/tmp/poltika-codex-closeout-rechecks-20261007/.venv/bin/python -m pytest -q \
  tests/unit/semantics/test_units.py tests/acceptance/test_v0_3_release_gate.py
```

**34 passed, 8 skipped, two existing deprecation warnings, 18.54s** (24 units
cases; 10 release-gate passes). Skips are seven unbuilt phase rows plus the
validation-grade field; none silently waives a release gate. Green tests are
consistent with the missing R1 adversarial cases.

The actual imported `test_the_checks_catch_what_they_are_for` catches five
in-memory mutations: empty results for scoring, ethnicity and milestone
checks; an empty structural-value walker; and `_negated` always returning true.
All originals were restored. The same actual functions and consuming-test
reproduction also ran via an earlier stdlib-only AST extraction while the
supported interpreter was temporarily unavailable; the supported-runtime
reproduction above confirms that result without extraction limitations.

`git diff --exit-code 5a8c17e HEAD -- tests/acceptance/test_v0_3_release_gate.py`
and the original whitespace check pass. GitHub readback confirms the exact
head/squash and seven successful historical workflows, including
[Tests](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37259739577)
and Links. No comments were returned by the historical timeline connector;
no additional reviewer clearance is inferred from that absence.

Root owns broad current-main checks. R1 remains blocking for this scope even
if the broad suite passes. No production/test file was edited, no issue/comment
was posted, and no queue was cleared. The follow-up fix, other-model review of
its final head and subsequent documentation/CI/integration gates remain.
