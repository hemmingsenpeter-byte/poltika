# Review Packet: income tax reads the shared household model (#232) — 16 October 2026

**Author preflight**, not independent review. Claude Code wrote the change
and this record, so it knows the rationale. The required GPT/Codex mapping
review is separate (Task 6/7 mappings; ADR-0020).

## Review inputs

- PR/diff: [#232](https://github.com/hemmingsenpeter-byte/poltika/pull/232).
  Base `352c288` (`origin/main`). Heads: `d442f9d` (mapping), `5e83b25`
  (catalogue test and queue row), then the fix commit recorded below.
- Plan: BUILD_PLAN_v0_3.md 2.3 ("`engines/simulator/income_tax.py`, reading
  the household model through a named mapping (1.2)"; "the fact-catalogue
  completeness test extended to income tax"; done when "the catalogue test
  covers every emitted fact"). Programme Task 6 and Task 7 done-when.
- Specification: `policy_specs/income_tax/specification.md` IT-01 (one
  natural person), IT-02 (standard 2026-27 year, input already allocated to
  it), IT-03 (classification "supplied, not inferred"), IT-04/05/08;
  `policy_specs/income_tax/facts.yaml`. No source, value or `policy_specs/`
  file changes, so no primary source was re-read for this PR.
- Household semantics: `src/poltika/semantics/household.py` module
  docstring; ADR-0017; Q10 and v0.2 D8/D9 (no period conversion).

## Expected behaviour (written before probing)

1. One person maps alone: no fact or spell of another person, the family
   or the person's role reaches their scenario.
2. Every fact the person did not assert is unknown (`None` or `UNKNOWN`),
   never a default member and never verified.
3. Taxable income comes only from the person's `it_annual_taxable` spells
   that tile the year exactly. A gap is unknown. A spell past either edge
   is refused (`HOUSEHOLD_SPELL_PERIOD_MISMATCH`), never apportioned.
   Earnings, benefit or another policy's basis never become taxable income.
4. A known exclusion (`unsupported`) outranks a mapping refusal
   (`needs_review`), as in the engine.
5. The run accepts only the policy's reference period; a mapped person's
   result is exactly the engine's result for the same scenario, trace
   included. No result is `calculated` while the draft-policy gate holds.
6. Existing households keep their identity: a person without tax facts
   hashes as before.
7. The catalogue test fails if the engine emits a fact the catalogue lacks,
   or the catalogue lists one the engine never emits.

## Probes and results

| Probe | Result |
| --- | --- |
| All 47 draft spec cases as one-person households: mapped scenario and module result (trace included) equal the direct engine run | Pass |
| Partner with spells and no facts: claimant unaffected; partner all unknown, needs_review with eight missing facts | Pass |
| Two spells tiling the year sum; one half-year spell gives unknown income | Pass |
| Employment earnings and a WFF-basis spell over the whole year give unknown taxable income | Pass |
| Spell from 1 March 2026 to the year end: refused as a period mismatch; with a non-resident assertion the run is `unsupported` `IT_RESIDENCE_NOT_MODELLED` | Pass |
| Amount for 2025-26 while the person asserts the standard 2026-27 year: `HOUSEHOLD_MAPPING_INVALID_FACTS` | Pass |
| Hash of a two-person household without tax facts computed on `352c288` and on the branch | Identical (`b2125ca6…`), pinned in a test |
| Attestation given as `"true"`, `1`, `"no"` or `0` | **Accepted and coerced** at `5e83b25` (finding A1) |

## Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| A1. `IncomeTaxFacts.taxable_income_basis_attestation` was a lax `bool`: pydantic turned `"true"` or `1` into an attestation | CODE_ERROR | P2 by the author's grading: a caller's attestation must be explicit. Fixed with `StrictBool`; regression test over the four values |
| A2. `household_from_income_tax()` defaulted `tax_year` to 2026-27 | CODE_ERROR | P3: the module's convention is no default period. Now required |
| A3. The changelog fragment said "nine questions apart from the amount"; there are eight | TEST_ERROR (record) | P3: wording fixed |
| A5. CI `test` failed at `5e83b25`: `run_household_income_tax` is a public `run_` function with no model-registry classification (3 failures in `tests/unit/engines/assurance/test_model_registry.py`; 2,233 passed) | CODE_ERROR | P2: the registry gate is a required check. Listed under `not_engines` as a wrapper of `income_tax_engine`, as `run_household` wraps `combined_runner`; the 22 registry and card tests pass |
| C1 (CodeRabbit, advisory, `ebcf8b4`). A mapping refusal from `run_household_income_tax` carried no trace | CODE_ERROR | Minor. The refusal now carries the trace of the engine run on the person's facts with income unknown; a test checks policy, period and the unknown income |
| C2 (CodeRabbit, advisory, `ebcf8b4`). `household_from_income_tax` built a household for a period other than an asserted standard 2026-27 year, which `to_income_tax` then refuses | CODE_ERROR | Minor. The adapter raises `AdapterRefused`, as the other adapters do for facts one household cannot hold; test added |
| A4. An `it_annual_taxable` spell of a type other than `unsplit_total` is ignored, so income stays unknown, while the period-mismatch check sees it | Not a defect | Same convention as WFF's own bases; the result is conservative (`needs_review`), never a wrong amount. Recorded, not changed |

## Not verified

- The full suite was not run locally to completion: a parallel run hung
  with idle workers and was stopped. A serial run of `tests/unit/semantics`,
  `tests/unit/scenarios`, `tests/unit/policy`, `tests/unit/engines/simulator`
  and `tests/acceptance` on `5e83b25` gave 1,292 passed and 30 skipped
  (exit 0). It left out `tests/unit/engines/assurance`, which is why CI,
  not this run, found A5. CI runs the full suite on every head.
- The round trip is not vacuous: across the 47 cases every enum member and
  every status value appears, with unknown, negative and fractional amounts.
- Whether a recorded benefit or other-income spell should contradict an
  asserted salary-only composition is interaction I08, a candidate in the
  Phase B matrix; it is out of scope here.

## Author response

The mapping follows `to_wff`: caller-resolved figures enter as spells with
their policy's own basis, and refusals reuse the existing codes. The
`IncomeTaxFacts` block follows the `ChildFacts` precedent, with the
engine's enums repeated in `semantics/`, which cannot import `engines/`.

## Resolution

A1 to A3 and A5 are fixed in `ebcf8b4`, with a regression test for A1; CI was green on that head. C1, C2 and a naming nit in the adapter are fixed in the next commit, with tests.
The fresh-context `poltika-reviewer` pass is recorded on the PR.
