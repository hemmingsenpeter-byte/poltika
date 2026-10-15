# Phase B economic evidence: mechanical reviewer handoff

Author: GPT/Codex, 15 October 2026 (Pacific/Auckland).
Base: `63359fecfe3b6659476528da021ea0ade0023537`.
Final commit and live CI state are recorded in the PR; this packet cannot
name its own containing commit. **Author preflight** and supporting same-model
checks are not independent Claude clearance or Pete acceptance.

## Inputs and expected contract

- Sole scope: Phase B Tasks 5–11 plus B0.1 amount verification; no implementation.
- Governing sources: BUILD_PLAN_PROGRAMME Phase B, BUILD_PLAN_v0_3,
  BUILD_PLAN_B0_1_WEB, ADR-0017/0020, epistemic/test/review/IP doctrine,
  .claude/skills/new-policy and pr-review-preflight.
- [Source/interaction matrix](../docs/research/phaseb_interaction_matrix_20261015.md):
  exact official Acts/Regulations, source dates/locators and retained decisions
  appear in its input table; derive consumer definitions before comparing rows.
- [Income-method source pack](../docs/research/phaseb_income_methods_20261015.md):
  retained #172 comparison, freshly retrieved HILS/official Treasury definitions,
  source hashes and explicit historical/extraction limits. D2/D3 not selected.
- [Independent method workings](phaseb_income_methods_20261015.py): Decimal only,
  offline by default. Optional official-source retrieval is explicit. No
  simulator import or statutory parameter/fixture approval.
- [Live reconciliation and amount check](../reviews/2026-10-15-phaseb-reconciliation.md):
  observations and reproducible bounded tests at named main/PR heads.
- [Independent #218 review](../reviews/2026-10-15-pr218-independent.md) and
  adjacent three reviewer probe scripts: cover **f1c106a only**; runnable
  scripts require that PR's code, not this documentation branch's main base.

The author knows the rationale. Sources/specifications and literal method
examples were reconstructed independently before examining implementation
claims. Retained reviews are labelled by their own model/context and head.
New mappings and method choices remain candidates. Missing amounts are never
zero; only an actual reviewed dependency propagates a source refusal.
No annual/weekly transformation is introduced, no diagnosis becomes a grant,
and no exclusion/status check is represented as a calculated dependency.

## Checks and review boundaries

Bounded runtime verification already completed on named **unchanged runtime
trees**, not assertions that the new source proposals are executable:

- Main B0.1/household API, Workbench, golden and interaction subset:
  **86 passed, 6 PostgreSQL skips**. Exact command/warnings in reconciliation.
- Frontend format/schema/chart/block subset: **52 passed** after one default
  5-second timeout was retried with one worker and 30-second timeout.
- #218 published head: **290 focused regression tests and 116 adversarial
  cases passed**, Ruff/mypy/evidence/model-card checks pass. Broad full suite
  interrupted honestly; final integration SHA is still required.
- #219/#220 source follow-ups were pushed to their **existing drafts**;
  source/amount gates remain. Their preflights and focused results live in
  those PRs, not an invented cross-model approval here.

New files: offline Decimal reproduction, script Ruff/format check, source
payload publication-date checks, relative-link resolution and whitespace.
A separate checkout of the final committed bundle is checked before handoff;
exact SHA/results are recorded in the PR comment.

Two supporting same-model checks independently examined official source text
and examples. They found and the author corrected: percentage decomposition
units/credit components, next-dollar wording, retained-source retrieval
wording, grouping of unrelated-tax propagation and grouping of monthly
protected-income versus date-only receipt facts. Their checks do not clear
Claude's source/method review. No protected expectation or engine was edited
to satisfy a result.

## Required independent pass / remaining decisions

Claude independently checks the complete source/method delta against the
official dated material and records the exact reviewed final SHA. A fresh
context reviewer pass and current CI also remain before merge. Pete retains
definition/interpretation, protected amounts and gate acceptance; nothing
in this packet promotes a draft or clears a review-queue row.

Concrete next steps: publish and review #218's final integration head;
review latest #219 and #220 sources; settle the remaining JS tax-table/rounding
evidence; then present D2/D3's definition/period/path choices for Pete. Do not
implement a new edge or a complete income/EMTR amount from this draft alone.
