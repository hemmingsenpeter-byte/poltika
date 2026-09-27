# Review Packet: v0.3 Phase 1b and the hosted pilot (PRs #124-#128) — 27 September 2026

Author: Claude Code, under Pete's "Approve all prior work. Proceed with the
build plan" and "Just keep going with the v0.3 build". Each PR merged with
CI green after an author preflight only. This packet hands GPT/Codex the
independent review of the five open implementation rows in
`review_packets/review_queue.md`. The review-debt cap is reached, so no
further implementation merges until rows clear.

## Review inputs

- **PRs:**
  - #124: hosted pilot. `src/poltika/api/access.py` (HTTP Basic, fail-closed
    in the image), `/healthz`, `$PORT`, built-in population in the
    `Dockerfile`, CI smoke test, `docs/pilot/HOSTING.md`.
  - #125: Task 1b.5. `resolution` on `/household/calculate`, stateless
    `POST /household/intake`, `scenarios/intake.py` label helpers, the
    analyst page's "Ask me first".
  - #126: Tasks 1b.2b, 1b.3b-1b.3d. `FactEntry.monotone`,
    `resolve(ranges=...)`, `Bounds.kind`, `assign_number`/`set_value` moved
    into `conditional.py`, property tests.
  - #127: Task 1b.6. `scenarios/microsim/ranges.py`, `fiscal_ranges` on
    `/microsim/runs`, the Fiscal tab.
  - #128: Tasks 1b.2d, 1b.1c. `scenarios/conditional_text.py`,
    `resolution.summary`, `tests/acceptance/test_v0_3_release_gate.py`.
- **Contracts:** ADR-0016; ADR-0011 (operator-set deploy configuration);
  `BUILD_PLAN_v0_3.md` Phase 1b subtasks and their "done when";
  `doctrine/llm_boundaries.md`.
- **Tests:** `tests/unit/api/test_access.py`,
  `tests/unit/api/test_intake_api.py`,
  `tests/unit/scenarios/test_conditional_ranges.py`,
  `tests/unit/scenarios/microsim/test_ranges.py`,
  `tests/unit/scenarios/test_conditional_text.py`,
  `tests/acceptance/test_v0_3_release_gate.py`, and the `pilot-image` CI
  job. Full suite at #128's head: 1188 passed, 22 skipped.
- **Author notes, to read only after your independent section:** each PR
  body's "author preflight" lines.

## Independent review

Complete this section before reading the author notes.

### Independently derived expected behaviour

(reviewer derives from ADR-0016, ADR-0011 and the plan's "done when")

### Questions to answer

1. **Access control (#124).** Can any route other than `/healthz` be
   reached without the password when it is set? Is the comparison
   constant-time for both parts? Can the image start open by mistake (the
   `POLTIKA_REQUIRE_ACCESS_PASSWORD` default, compose, the entrypoint)? Is
   anything about the credentials logged? Does `--proxy-headers
   --forwarded-allow-ips='*'` matter behind the platforms named?
2. **Intake API (#125).** Is every answer typed and refused exactly as
   `apply_answer()` promises (finite domain, attestation yes only,
   ASCII-digit counts, non-negative finite money, claimant income before
   partner)? An answer to a fact already supplied overwrites it, as the
   caller's assertion: acceptable for a stateless API, or should only
   currently missing facts be answerable? Is `calculation` always the
   household with the answers applied?
3. **Conditional answers never calculated (#125, #126, #128).** Is any
   conditional figure labelled `calculated`, or added to a calculated one?
   Does the page write any question or figure of its own?
4. **Ranges and monotonicity (#126).** Is `Bounds.kind == "bounds"` only
   possible when every ranged fact is declared monotone for the component,
   with a rule id? Is the WFF-total rule (components agree in direction)
   right? Are the three fixture declarations in the tests true of the
   engine for the whole domain, not only the sampled ranges? Should
   "increasing" mean non-decreasing, as documented?
5. **Population ranges (#127).** Is a household bounded only when every
   branch is calculated in both runs? Is using the baseline's branching for
   the reform run sound (same assignments)? Do the three figures reconcile
   with the unsupported weight to the run's total, and is nothing added?
   Are `run_id` and `results_sha256` unchanged?
6. **Summary (#128).** Does `verify()` check every figure the text shows?
   Is refusing a failed summary (500) better than omitting it?
7. **Gate (#128).** Does the v0.3 gate skip rather than pass for every row
   whose phase isn't built?

### Findings

(ID, severity, proposed classification under `doctrine/review-doctrine.md`,
reproduction, expected versus actual)

## Deferred for GPT/Codex, not review findings

- **1b.2b declarations:** add `monotone` to the real catalogues only where
  a cited rule implies it. The property test pattern in
  `test_conditional_ranges.py` checks each against the engine.
- **1b.2c candidate values:** a structured `candidates` list on the
  2026-27 `in_work_base` row (7670 and 5070, each with source, locator and
  condition), through `doctrine/test-doctrine.md`.
- **Phase 0:** source-scoping income tax and the three core main benefits.
