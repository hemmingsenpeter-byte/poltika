# Review packet: delegated decisions and AS rate contract repair

Author: GPT/Codex. Base: `18e1ca5`. Independent reviewer: Claude Code.
Owner authority: Pete's explicit "resolve and proceed" instruction after
the source findings and choices were presented. Not an author-only merge.

## Inputs to check before the author's rationale

- Current AS specification, schema and parameter loader contract.
- PR 46's dated Act/regulations/MSD evidence and independent review.
- PR 48's linked WFF exclusion provisions and independent review.
- PR 41's periods research and selected-date limitations.
- DEC-002/003, the new selector section and scope-resolution record here.

## Expected review focus

- Table entry thresholds are not called exact statutory bases; no invented
  intermediate rounding rule or actual-WFF dependency.
- Four rate-household categories are independent of the unchanged caps.
- Rate subtype and child-age facts cannot default to a calculable row.
- The paragraph (f) legal ambiguity is retained, not declared proven.
- Inputs, trace decision IDs, schema feasibility and policy-version cutover
  are implementable without silently changing the current runtime.
- Dates/reporting are explicit scope choices, not evidence that future
  WFF rates or actual payment schedules are verified.
- Decisions record delegated ownership honestly and do not waive review.

## Validation and limits

No calculator, executable policy, protected expected value or BUILD_PLAN
status changes. Schema/reference checks and the fast suite are run as
documentation/source-catalogue regression checks, not proof that this
unimplemented contract already works. The implementation must supply the
specified negative, boundary, selector and provenance tests before 26a.2.

Claude retains code and ADR ownership. PR 45's integration test finding
is still outstanding at `60556e5`; its standalone green suite is not a
clean combined-tree acceptance. No merges are performed by this packet.

### Actual checks and required test maintenance

- `git diff --check`: passed.
- Current executable AS policy schema/source references: passed, unchanged
  policy version `0.1.0`.
- Fast pytest: **248 passed, 1 failed, 1 deselected**. The failure is
  `tests/unit/engines/assurance/test_provenance.py:144`,
  `test_report_artifacts_are_the_exact_file_hashes`. It hardcodes only
  DEC-001 as a decision artifact. The report correctly includes the newly
  added DEC-002 and DEC-003, so its exact dictionary comparison fails.

Claude-owned test maintenance required before merge: add these two paths
to that test's independent expected-file list, retaining exact hash
comparison (do not weaken it to a subset or copy the report's own list):

```text
decisions/DEC-002-published-thresholds-and-rate-scope.md
decisions/DEC-003-msd-paid-wff-income-exclusion.md
```

This is not a numeric expected-value change or a production hashing bug.
No test file was edited across the agreed ownership boundary. PR remains
draft until the test update and independent contract review are complete.
