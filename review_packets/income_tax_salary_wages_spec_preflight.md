# Review packet — 2026–27 basic annual salary/wage tax specification

**Date:** 8 October 2026. **Label:** author preflight plus a separate fresh
GPT same-model source check; not independent Claude review or Pete acceptance.

## Mechanical review inputs

- PR: https://github.com/hemmingsenpeter-byte/poltika/pull/193.
- Programme Task 7; `BUILD_PLAN_v0_3.md` 2.1; D11 scope commission.
- Base: `26cd8a6` (merged #187). Corrected source head:
  `86f48e1b59519e09c6edabac63eda965b41f13cb`.
- Earlier source head: `389de0d`; source-observation follow-up: `835d771`.
  Earlier source head `8ef7a20` integrated #186. The later conflict-free
  main integration changes no tax-spec content; `aba377e` corrects the
  decision-record template labels, keeping all three decisions open.
- Specification: `policy_specs/income_tax/specification.md`, IT-01–IT-08.
- Primary source catalogue: `policy_specs/income_tax/sources.yaml`; dated
  ITA 4 September 2026, enacted 2024 Budget Measures Act, dated TAA
  4 September 2026; pinpoints in each row. Separate IRD cross-checks.
- Open issues: DEC-001/002/003; PETE_QUEUE Q16/17/18. D11 stays in force.
- Diff: source/specification/decisions plus programme/research/queue records
  only. No executable policy, facts/cases/benchmarks, engine, API, web or
  protected existing statutory artifact.
- This is the specification follow-up to source-scope #148, described in
  programme status as onboarding PR 2. It supplies the skill's sources/spec
  content, not its separate values/expected-results content.

## Expected behavior derived from the sources

The separate GPT reader derived these before reading the draft/rationale.
The author already knew the rationale; that author's pass is not blind.

1. YE 1 gives the April–March year; BD 1/3 and BC 2–5 require classified,
   period-allocated individual taxable income, not household/weekly proxies.
2. CE 1 and DA 2/3 support the narrow ordinary-salary/wage slice while
   preserving express deduction overrides and no inferred losses/deductions.
3. Schedule 1 Part A cl 1/Table 1 and the 2024 Act supply the literal five
   bands/rates and commencement/application. Fractional-dollar/final
   precision is not supplied by those observations.
4. BB 1 and TAA s 92A both matter: Commissioner basic-rate assessments can
   precede annual enactment; Bill 344-1 still cannot supply enacted authority.
   Poltika's D11 promotion gate remains unresolved.
5. Basic tax, credits/withholding, terminal tax and PAYE are distinct.
   YA 1 filing status is not whether the person manually completes an IR3;
   TAA s 22I treats finalised accounts as returns/assessments.
6. Unknown facts are never zero; out-of-slice facts are explicit. Both
   authority and precision gate all numeric results; no protected expected
   values or implementation are adopted in this PR.

## Findings and dispositions

| Item | Proposed class | Disposition |
| --- | --- | --- |
| TAA s 92A newly mapped; older BB 1-only account incomplete | INTERPRETATION_AMBIGUITY | Source statement corrected; DEC-001/Q16 stays open for Poltika authority basis |
| Annual fractional-dollar, intermediate/final/tie precision not established | MISSING_SOURCE | DEC-002/Q17, `needs_review`; no convention selected |
| IR3G earlier-year worksheet threshold appears inconsistent with per-dollar statute | SOURCE_CONFLICT | DEC-003/Q18, no cell corrected or benchmark adopted |
| R1 P1: CI rejected the three new DEC records' owner/date/section labels | SPEC_ERROR (documentation format) | Reproduced with existing decision-record tests: 3 failed, 5 passed. Fixed in `aba377e`; exact-head expanded preflight: 18 passed. No decision, source value or expected fixture changed |

No additional actionable P1/P2 defect in the **gated draft** was found in the
separate GPT check at `389de0d` and exact final source head `8ef7a20`.
That supporting pass missed R1's template-format gap, subsequently found by
CI. Its three failing records are now corrected; independent final-head
review remains required.
The latter reviewer also visually confirmed the IR3G page. These open policy issues prevent approval
as a complete executable specification; a clean draft review does not close
them. The later source-observation pass supplies visual confirmation, not
an interpretation decision.

## Author preflight and exact checks

Skill: `.claude/skills/pr-review-preflight/SKILL.md`.
Separate frozen checkout: `/private/tmp/poltika-codex-income-tax-spec-final-preflight`
at corrected source head `86f48e1`, with explicit source selection:

```sh
PYTHONPATH=/private/tmp/poltika-codex-income-tax-spec-final-preflight/src \
  /Users/peterhemmingsen/Poltika/.venv/bin/python -m pytest -q \
  tests/unit/policy/test_decision_records.py \
  tests/unit/engines/assurance/test_evidence.py \
  tests/acceptance/test_review_queue.py
git diff --check 26cd8a6...HEAD
```

Both exit 0: **18 tests passed**; whitespace clean. The earlier preflight
ran 10 assurance/queue tests and omitted the existing decision-record check.
SourceCatalogue
validation against the committed `sources.yaml` accepts **14 unique
entries**; all rule-map source IDs resolve; all four legislative anchors
have rank 1. A focused path/link probe confirms **37 relative links exist**,
the annual gate is `needs_review`, and no executable/protected-value path
is in the scoped diff. Packet/queue metadata adds no policy claim. Existing
dependencies were reused; no install.

The author read the cited provisions directly in dated official HTML and
cross-checked IRD's rates and yearly-calculator scope independently. PDFKit
rendering of the directly retrieved IR3G confirms the printed p 43 cells.
PDF SHA-256: `4b0f2ffbc831c0aa88235d2c0ce986fa80b234be8f3fb6ac17ee1ab377f71b99`.
This identifies the observed copy; it is not a claim that a URL is immutable.
Only the named provisions were checked, not a whole-year amendment audit.

No full local pytest, mypy/Ruff rerun, engine evidence-coverage claim for
income tax, interactive calculator benchmark or external-engine comparison
was attempted. There is no `policy.yaml` for this draft, so a claim that
it passes an executable policy's coverage/currency gates would be false.
CI and actual independent Claude source review remain pending.

## Independent-review handoff

Review primary legislation first, then IT-01–IT-08 and the exact PR diff.
Independently check the source observations and issue dispositions. Record
Claude model/session/head provenance; a GPT same-model pass cannot clear
its own authored specification. Pete decides Q16–Q18, and enacted-period
authority, precision and subsequent values/benchmarks remain prerequisites
for policy approval and implementation. Tasks 7 and Gate B remain incomplete.

Pete's subsequent “accept and proceed” accepts advancement of this gated
draft; it selects no answer to Q16–Q18 and leaves D11 in force. Actual Claude
review still needs the final PR head, including the corrected records and
packet metadata; neither acceptance nor this author preflight clears it.

_Generated by GPT/Codex._
