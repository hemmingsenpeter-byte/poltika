# PR #128 follow-up — author preflight

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex project manager, resolving recorded independent findings.
- Base: `e52f5d35913fbb4b81c7b64c6caf6d446c158759`.
- Original independent review: `reviews/2026-10-03-pr128.md`, findings committed
  before fixes at `03d7bfd`. The original author was Claude Code.
- Mechanical inputs: ADR-0016; `scenarios/conditional.py`; WFF approved exact
  Decimal/presentation contract; outcome categories; original and follow-up
  diffs; existing golden inputs; negative summary probes.
- Label: author preflight; the author knows the fix rationale. Separate
  testing and same-model checks follow. Claude review/acceptance remains pending.

## Contract and scope

The deterministic engine's amount and result identity remain unchanged.
Summary text retains exact amounts, annual/weekly units, conditional assignment,
evidenced exclusions, unsupported coverage, points/bounds and cap limitations.
Verification rejects incomplete or altered fixed text/figure metadata.
No protected amounts, source/spec rules or loader/engine behavior change.
The analyst's existing range strings are aligned with the corrected certainty
limit; DOM construction still uses text nodes. No runtime agent abstraction.

The original review is complete, but confirmed defects keep the assurance row
and release gate open while fixes await review and integration. Historical
cross-model waivers do not extend to this new follow-up.

## Checks observed

- The testing lead's corrected source-path baseline: 233 passed, eight skips
  (seven unbuilt capability rows plus #128's open assurance row).
- An initial wheel-only invocation omitted `PYTHONPATH=src`, so API tests
  looked for unpackaged assets relative to the installed wheel. This is a
  corrected REVIEWER_ERROR, not a product finding or a green original run.
- New selected regressions before fix: 13 failed, three passed. After fix:
  16 passed, 32 deselected. API half-cent test compares text with the engine's
  output rather than introducing a statutory expected number.
- Ruff and strict mypy (80 files) pass. Exact-head adversarial/focused checks,
  final diff inspection and GitHub CI are recorded after they complete.

No release or independent Claude acceptance is claimed by this packet.
