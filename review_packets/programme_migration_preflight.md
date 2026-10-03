# Programme migration — author preflight

**Date:** 3 October 2026. **Author:** GPT/Codex.
**Label:** author preflight; not independent review, not release acceptance.
**Base:** `e52f5d35913fbb4b81c7b64c6caf6d446c158759`.
**Head:** the four draft-PR heads are pinned in their PR descriptions. Verify
those exact commits after any update; this packet is part of the reference unit.

The author knows the implementation rationale. Review expectations were derived
from Pete's supplied migration brief and the repository's governing instructions.
The [reconciliation](../docs/programme/2026-10-03-reconciliation.md) records
baseline evidence and classification, not independent approval of this work.

## Expected contract

- One active master, with both agent entry points and orientation agreeing.
- All 58 capability tasks and all 33 old steps accounted for; active lanes retain
  useful detail and source/decision/review gates.
- Exact historical snapshots; permanent ADR/review/release evidence preserved.
- ADR-0019 sequencing superseded; compatible principles and ADR-0020 retained.
- ADR-0018 stays proposed; release tags, pilots, representative populations and
  unimplemented models are not invented by status migration.
- No production, policy, protected expected-value, data or API behaviour change.
- Existing source/test/IP/LLM constraints and approved epistemic decisions remain.
- Other workers' files, open PRs, branches and uncommitted work remain untouched.

## Findings and author response

| Finding | Proposed class / severity | Disposition |
| --- | --- | --- |
| Stale operational master order can select the wrong next task | ARCHITECTURE_ISSUE / P1 | Agent guidance, master, status, orientation and active-lane redirects agree on ADR-0021; structural authority checks added. |
| Status overstates v0.1.5 release and misses #139 merge | SPEC_ERROR / P2 | Remote tags/reviews/pilot evidence reconciled; unfinished gates retained. |
| Workbench design acceptance and representative calibration could be inferred from implemented backend/tooling | SPEC_ERROR / P2 | Separate proposed ADR, backend/UI, synthetic/representative and pilot evidence throughout. |
| Partial adoption of the four units produces mixed authority | ARCHITECTURE_ISSUE / P2 | Drafts require integrated review/coordinated activation; no main merge is performed. |
| Fresh same-model doctrine audit found surviving blanket Pete-acceptance wording in both review skills despite the ADR-0020 clarification | ARCHITECTURE_ISSUE / P2 | Replaced the description, introduction, review table and preflight handoff wording with the existing Tier A/B Claude Code and Tier C Pete boundaries; independent review remains required. Final-head recheck is recorded in the PR descriptions. |
| Reused shared Python environment lacks declared openpyxl | Environment limitation | Initial orientation/default-suite attempts failed; isolated locked environment installed. Correct-environment results are recorded below and in PR descriptions. |

## Reproducible verification

Using the isolated worktree's locked Python 3.12 environment:

- `.venv/bin/ruff check src tests`: passed.
- `.venv/bin/mypy --strict src`: passed, 80 source files.
- `.venv/bin/python -m pytest -q tests/acceptance/test_programme_authority.py tests/acceptance/test_orientation_examples.py tests/acceptance/test_review_queue.py`: 15 passed.
- `git diff --check`: passed.
- All five archived files compared to the base blobs byte-for-byte: passed.
- Active local Markdown destinations checked: resolved. Archive bodies retain
  original-relative references intentionally; README documents original-commit
  resolution without rewriting them.
- `src/`, `policy_specs/`, `data/`, existing tests, dependencies and CI files
  compared to base: unchanged. Only the new governance test is added.
- Master/status task IDs 1–58, phases A–P and old-step links 1–33 checked.
- The historical v0.3 Progress table and existing task identifiers are retained.

The full default-suite result and final exact-head audit are recorded in the
PR descriptions. Installed-artifact, retained-code replay, database availability
and Docker checks are not inferred from the focused local checks. CI follows
normal gates when each draft is retargeted to main; stacked PR bases do not
trigger this repository's main-only pull-request workflows.

## Review handoff

A fresh-context same-model audit may support this author preflight, but does
not clear the cross-model reviewer rotation. Independent review and main CI
remain pending before acceptance. The deferred review must inspect each pinned
PR head and the integrated tree, including authority, reserved decisions,
archive hashes, release state and active-lane gate changes. No policy-spec or
calculation review-queue row is cleared by this documentation packet.
