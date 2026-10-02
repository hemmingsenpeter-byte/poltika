# Line-by-line checklist

Use this in pass 2 (SKILL.md step 4). Skip whatever the diff can't affect.
Anything in section 2 that the diff breaks is at least a P2, because
those invariants are what makes a Poltika result trustworthy. Each
suspicion still has to be reproduced before it becomes a finding.

1. Correctness and edge cases
2. Poltika invariants
3. Sources, protected values and provenance
4. Tests
5. API, schema and data boundaries
6. Architecture and placement
7. Security and robustness
8. Performance
9. Readability
10. Docs and release notes

## 1. Correctness and edge cases

- **Boundaries.** Periods are `[from, to)`: test the day before `from`, `from`
  itself, the day before `to`, and `to`. Thresholds: does the rule say
  "exceeds", "at least" or "must not exceed"? The Q71-Q140 review found
  AS cash assets compared with `>=` where r 15(1) says "must not exceed"
  (#75).
- **Unknown vs zero vs empty.** `if x:`, `x or 0`, `.get(k, 0)`, `sum()` over
  a list that can hold an unknown, and a default of `Decimal(0)` all turn a
  missing fact into zero. Look for them on every changed input path.
- **Decimal exactness.** No `float` on a money or rate path: `float(...)`,
  true division of ints, `round()` on a float, `pytest.approx`, JSON that
  serialises Decimal as a float. Rounding happens only where the rule
  says, in the direction it says. Where agencies differ there is a
  decision record: AS r 19 rounds the final amount up, and AS `DEC-001`
  settles the income-excess step.
- **Errors.** A broad `except` that swallows a `needs_review`, an error
  mapped to the wrong status, or a message that leaks paths or stack
  traces.
- **Mutation and caching.** A cached object handed out without a copy, a
  mutable default argument, or a cache key that omits something the
  result depends on (#95's parse cache; F11's measure-independent run id).
- **Determinism.** Output, hashes or IDs that depend on dict or set order,
  list order the caller controls (F4), the clock (`date.today()` in engine
  code) or an unseeded random draw.

## 2. Poltika invariants

- A missing fact is never zero. Unknown gives `needs_review` with the fact
  in `missing_facts`; it never gives `calculated` or `0`.
- `unsupported` outranks `needs_review`. One component's unresolved state
  must neither contaminate another component nor be silently dropped
  from the household result.
- IWTC stays `needs_review` while `in_work_base` is gated, so there is no
  WFF total.
- WFF (annual) and AS (weekly) results are never added together.
- Inputs are caller-asserted statuses (`verified`/`excluded`/`unknown`). An
  assertion is never reported as independently verified evidence. The API
  rejects unknown fields and never accepts a caller-supplied policy
  directory.
- Policy ID, version and assessment date are checked at the module
  boundary. A module refuses a date outside its reviewed period. A rate
  that can change mid-year stays `needs_review` until the whole period is
  confirmed.
- Every calculation step is recorded with `record_step` and the correct
  rule ID. Explanations are rendered from the trace, never composed
  separately; `verify()` holds for every result.
- Every new missing-fact ID has a `facts.yaml` entry (ADR-0016). Every
  `unsupported` result has the right category (`evidenced_exclusion` or
  `not_modelled`).
- The LLM layer never calculates (`doctrine/llm_boundaries.md`).

## 3. Sources, protected values and provenance

- **New or changed statutory value** (`policy.yaml`): it cites a
  `source_id` and `locator`; you have checked the source at the version in
  force for the interval; the interval's dates are right; `review_status`
  is honest.
- **Expected values** in `spec_cases.yaml`, `benchmarks.yaml`,
  `golden_households.yaml` or a test: hand-calculate at least one per
  changed rule path yourself, as `reviews/2026-09-27-pr117.md` does. A
  changed expected value needs a sourced reason and review
  (`doctrine/test-doctrine.md`). "Updated to match the code" is a P1.
- **Golden snapshots** (`tests/fixtures/golden_*.json`, regenerated with
  `POLTIKA_UPDATE_GOLDEN_SNAPSHOT=1`): every changed number is explained
  by an intended change. An unexplained change is a regression until
  shown otherwise.
- **Assumptions** (A-numbers) are named and kept distinct from
  source-stated facts.
- **Data.** Committed raw snapshots and manifests are immutable: a
  correction is a new `raw_snapshot_version`. New manifests carry the full
  provenance field list (the `provenance` skill). Transformations are
  versioned and every version a manifest names stays readable (#120).
- No external engine (OpenFisca Aotearoa, PolicyEngine NZ and the like) is
  the source of a rule, value or expected result
  (`doctrine/ip-doctrine.md`).

## 4. Tests

- **Do they bite?** Revert the source change, keep the tests, and run
  them. They should fail (SKILL.md step 5).
- The negative paths are tested directly: `unsupported`, `needs_review`,
  malformed input, both period edges. Not only the happy path.
- Tests use the real approved policy where the production gate matters.
  Synthetic fixtures are labelled as conditional.
- The right class: spec (hand-calculated from the specification),
  benchmark (official worked examples), regression (a known issue, naming
  the finding it pins).
- Assertions are exact: the Decimal amount, the status, the reason code.
  Not `assert result` or a float tolerance on money.
- No new `skip`, `xfail` or deselection to get green. Existing skips have
  a named reason.
- Where `facts.yaml` declares monotonicity, a property test checks it.

## 5. API, schema and data boundaries

- Pydantic request models forbid extra fields. A response shape change is
  deliberate, documented and reflected in the analyst page and examples.
- Invalid input gives 422 with a useful message and no internal detail.
- A stored-run or scenario schema change comes with an Alembic migration,
  and stored runs still replay (`code_replay`).
- Packaged code can find its policy assets (`installed_artifact` tests),
  and new data files are included in the package.
- Imports respect "The dependency boundary" table in
  `REPOSITORY_STRUCTURE.md`. Check with a search, for example:
  `rg -n "^from poltika\.(api|scenarios|data)\b" src/poltika/engines` and
  `rg -n "poltika\.data\b" src --glob '!src/poltika/data/**'`.

## 6. Architecture and placement

- A new file sits where `REPOSITORY_STRUCTURE.md` says. If nothing fits,
  the PR updates that file deliberately.
- No speculative abstraction. Shared patterns are extracted after the
  third policy repeats them, not before (the `new-policy` skill).
- Engine code is pure: no I/O, network, clock, environment reads or LLM.
- Frozen doctrine and accepted ADRs are unchanged unless the PR is itself
  the decision artifact Pete asked for.

## 7. Security and robustness

- User input never becomes a filesystem path, a shell command, a SQL
  string or an `eval`. YAML is read with `safe_load`.
- No secrets, tokens or personal data committed.
- API inputs have bounds (population size, list lengths, string lengths).
- A new dependency is justified, locked in `uv.lock`, and actively
  maintained. `uv sync --locked` still succeeds.

## 8. Performance

Only where it matters: loops over households × components × periods that
repeat a YAML parse or a policy load, quadratic work in population size,
or an API route doing a full population run per request.

## 9. Readability

- Names say what a thing is. Comments explain why, and cite rule IDs
  where the code implements a rule.
- The new code reads like its neighbours: same idioms, same comment
  density.
- No dead code, debug output, or commented-out blocks.
- Not a finding: a preference that ruff doesn't enforce and the code base
  doesn't follow consistently.

## 10. Docs and release notes

- `docs/ORIENTATION.md` and CLAUDE.md's "v0.1 at a glance" are still
  true. CI runs the orientation examples but nothing checks the prose.
- User-visible changes are in `CHANGELOG.md`, and the README coverage
  table and `docs/releases/` limitations are updated where they apply.
- The BUILD_PLAN task records its progress where the plan expects it.
