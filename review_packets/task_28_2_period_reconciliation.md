# Review Packet: Task 28.2 period research - 2026-09-24

## Review inputs

- Base revision: `499f54d` (merged PR #37).
- Primary sources: the official URLs and locators recorded in the new
  `task_28_2_check` entries in both policies' `sources.yaml` files.
- Approved specifications: both `specification.md` files, WFF's Task 10
  domain and rate-status contract, and AS's Task 22 domain and Task 25 note.
- Plan: BUILD_PLAN.md Task 28.2 and its reserved owner decisions.
- Implementation to inspect: both module validation functions, especially
  AS's `_spans_reference_period()` and `_as_module_validation_failure()`.
- Author research artifact, to read after independent derivation:
  `docs/research/task_28_2_period_reconciliation.md`.
- Validation: both source catalogues parse as YAML; source IDs are unique;
  both unchanged policy files validate and all parameter source references
  resolve. `git diff --check` passes. No numerical fixtures or application
  code changed; no application test suite was required for this research.

## Independent review

Reviewer: Claude Code, independent review on PR #41.
Claude independently checked both AS amending Acts and the MSD table,
then confirmed the research constraints and reproduced the AS validation
finding. WFF MD 3/MF 4 and the IR271 heading were not independently
refetched; their source verification remains the author's.

Author follow-up: removed the obsolete usage-reserve restriction, moved
the research note into the existing docs/research location, and recorded
the additional eligibility-fact check needed for a week on or after
2 November 2026. No dates or reporting mode have been selected.

## Owner decision and acceptance

Pending Pete's assessment-period, lookup-date and reporting decisions,
their recorded follow-up, and final acceptance. Task 26b has not started.
