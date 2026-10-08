# GPT-6 independent repository audit: review and remediation handoff

**Observed:** 8 October 2026 (NZ time)
**Baseline:** main at e5d87c3eba19540cfe499bfab86a87a9018d884a
**Author:** independent GPT-6 repository audit
**Status:** OPEN FINDINGS / REVIEW REQUEST — not a verified code fix, merge clearance, source approval, or completed security assessment.

## Purpose and scope

Ask Claude Code to reproduce or falsify the findings below, classify them under the existing discrepancy taxonomy, then prepare bounded remediation PRs, with an independent reviewer for Claude-authored fixes. This PR changes documentation only. Do not interpret its merge as closing any findings.

Live PR stack at this baseline: #183 (stale/conflicting status), #186 (catalogue), #187 (persisted reform scenarios), #188 (web shell), #189 (seven-tab scenario experience). #187 and #189 have existing cross-model review records. Consult the *current* PR head/review queue before making a decision; GitHub status changes rapidly.

Governing authority: ADR-0020 (reviews/delegation), ADR-0021 (economist-first), ADR-0022 (archive boundary), ADR-0023 (single web product surface), doctrine/epistemic-constitution.md, BUILD_PLAN_PROGRAMME.md, BUILD_PLAN_B0_1_WEB.md. Pete retains Tier C authority. Do not rewrite accepted ADRs or move the UI off its approved stack as part of this review.

## A1 — P1 if PR code can reach personal account assets: self-hosted CI isolation

**Observed:** PETE_QUEUE.md Q13 states PR code runs as Pete's macOS login user and could reach his keychain, SSH credentials and personal files. .github/workflows/tests.yml runs Python and npm tooling using [self-hosted, poltika], including untrusted PR-dependency execution (npm ci / lifecycle scripts). This is a privilege/isolation concern, NOT evidence of actual exploitation.

**Claude action:** verify OS process identity, work directory ACLs, access to the owner's non-repo files and keychain, runner trust boundary, network/secret exposures and who can submit executable PR changes. Inspect other workflows on the same runner, not only tests.yml. Do not print or upload credential values while probing.

**Safe remediation:** recommend and implement where locally authorised a dedicated non-admin CI OS user or disposable isolated runner, permissions restricting unrelated paths and keychains, scoped runner credentials, and cleanup between PR runs. Runner setup and permissions changes need the operator/Pete; do not claim a code-only PR isolates an existing host.

**Acceptance:** record runner identity and confinement without revealing secrets; demonstrate that CI cannot read a controlled dummy file placed outside the permitted workspace under the owner's account, and cannot access the owner's keychain/SSH material. Verify legitimate Python/Postgres/npm jobs still execute. Decide with Pete under Q13 before describing exposure as accepted or remediated.

## A2 — P1 before any real personal data or multi-user pilot: scenario access boundaries

**Observed:** src/poltika/api/access.py authenticates a single shared Basic-auth identity (POLTIKA_ACCESS_USER / POLTIKA_ACCESS_PASSWORD). Proposed #187/#189 src/poltika/api/v1_scenarios.py lists stored household/reform scenarios and exposes a retained household-definition endpoint. The inspected request handlers do not establish individual-user ownership or an ownership predicate. A holder of shared pilot credentials may therefore browse or retrieve another holder's records. This is a design/authorisation boundary, not a claim that production is currently storing real personal information. ADR-0023 explicitly approves password-protected pilot access.

**Claude action:** independently verify behavior end-to-end, including scenario list, workspace, definition, create, run, export, rerun, legacy /scenarios routes and any debug endpoints. Check whether opaque IDs mitigate guessing but still permit list enumeration. Check the deploy's allowed data classification and retention policy.

**Minimum near-term response:** enforce SYNTHETIC OR PUBLIC NON-PERSONAL DATA ONLY for the current shared-login pilot; ensure UI, docs and onboarding say so prominently, avoid personally identifying household facts, and do not suggest multi-user privacy isolation is present. Confirm Pete's intended external-user scope.

**Before any real-person household records or analysts sharing the service:** design authenticated principals and per-user or per-workspace authorisation consistently across old and new routes, meaningful retention/deletion/access policy compatible with provenance requirements, and least-privilege database access. Avoid retrofitting a token to only /api/v1 while older endpoints bypass the model. Changes to approved access/product scope go through Tier C where applicable.

**Acceptance:** in an isolated test with two authorised user/workspace identities, user B cannot list/read/clone/export/rerun user A's nonshared scenario or retained household facts; old routes are covered. Until the identities exist, treat the feature as a single shared workspace and use synthetic facts only. Do not claim such a test has passed without running it.

## A3 — P2: stacked web/API PR integration and review gates

**Observed:** #186 → #187 → #188 → #189 are cumulative dependent PRs, not four independently mergeable diffs. #189 touched roughly 129 files against its then main base, much of this generated OpenAPI/types and the predecessor stack. Its reviews/2026-10-08-pr189.md records eight original P2 discrepancies fixed, but states the independent Claude review of the later Codex fix range is NOT complete. review_packets/review_queue.md repeats the pending gate. Green workflow groups do not substitute for that review.

**Claude action:** freeze unrelated changes; clear original Codex-fix review on the exact final implementation head and record it. Merge in dependency order only: #186, #187, #188, #189. For each: update to latest main; inspect incremental semantic delta, artifact/openapi drift, PostgreSQL migration upgrade from v0001, GitHub required checks and final-head cross-model review. After merging a parent, refresh each child and verify new head/CI and inherited review validity rather than copying old review approvals.

**Acceptance:** each PR merged or parked with a traceable disposition and its final SHA, clean main CI, correct database migration and real saved-run restart behavior in the integration smoke. Do not use the cumulative #189 file count as proof of an 129-file independent feature review.

**#183:** separately reconcile its conflicting programme-status docs to live main; do not merge stale branch histories mechanically.

## A4 — P2: canonical household/UI contract mismatch

**Observed:** on main, Task 6 canonical shared household model is not accepted. Proposed web/src/api/services/scenarioService.ts in #189 uses Record<string, unknown> for household create/copy rather than an agreed canonical household frontend schema. The current UI wraps the legacy WFF/AS HouseholdCalculationRequest. ADR-0017's household model and golden parity remain a future integration gate.

**Claude action:** do not block the synthetic WFF/AS UI shell merely because Task 6 is incomplete. Identify and document a versioned request/adaptor seam from legacy household forms to the eventual shared household model. Prefer a typed API boundary and opaque versioned data, not direct policy-component logic in React.

**Acceptance:** existing request round-trip preserves unknown/nulls, WFF/AS dates, partner/child facts and requested law versions; tests protect against stale async confirmation (see #189 review R1), and a written adapter contract defines the migration path. Avoid treating a TypeScript interface as a legal model.

## A5 — P2: UI integrity and absence of a completed economics product

**Observed:** main's engines/simulator directory contains WFF and Accommodation Supplement calculators, not income tax or the three approved first-slice benefit engines. Income-tax and JS/SPS/SLP source catalogues have been merged, but their source-approved specifications, parameter sets, benchmarks and engines are not merged. No accepted Task 6 or Tasks 9–11 household dependency graph/disposable-income/EMTR appears in main. src/poltika/api/workbench.py and proposed #189 create_run still use execute_reform(..., ["family_tax_credit"]) for reform runs. The configured development population is synthetic; no externally validated representative population or full fiscal estimate is established.

**Claude action:** test all frontend copy, headline cards, fiscal/distribution tabs and downloadable artifacts for misleading statements or cross-period arithmetic. Ensure the synthetic population is prominent and "net Crown impact", representative NZ estimates, complete household disposable income and full EMTR are unavailable until separately evidenced. Never present an uncovered component as 0 or an AS-week plus WFF-year total.

**Acceptance:** targeted negative UI/API tests catch unsupported capability claims and unit/period conflation; accessible disclosure survives screen/export and deep links; the model scope is explicit. A short early usability test with synthetic examples is allowed but is not Pilot 1 and not economic validation.

## A6 — P2: branch-protection coverage for web checks

**Observed:** ADR-0023/B0.1 records a new web CI job for npm lint/types/tests/build/contract drift. The current main ruleset requires nine checks but has no web check. PETE_QUEUE Q15 reserves this configuration choice for Pete.

**Claude action:** verify the exact check name and whether it runs on every relevant PR and on a clean branch; prepare an exact one-time ruleset change for Pete to approve, without altering/weakening any of the existing nine contexts. Watch for required checks being skipped on non-web changes, incorrect triggers and first-time branch protection deadlocks.

**Acceptance:** an intentionally failing web test/check blocks merge when applicable; all existing required checks remain enforced; ruleset modification and decision are recorded. Do not claim this requirement is enforced until observed.

## A7 — P2 strategy: validate one vertical slice before parallel benefit engines

**Observed:** BUILD_PLAN_PROGRAMME.md sequences Task 5 semantics, Task 6 household, Task 7 income tax, Task 8 benefits, Task 9 dependency graph, Task 10 disposable income and Task 11 EMTR. The actual source packs and existing review queue identify unresolved assessment basis, partner-income treatment, eligibility, precision and period mapping Q10. A four-agent parallel calculator launch before shared interface/specification gates can multiply incompatible assumptions.

**Claude action:** after B0.1 clean integration, prioritise Task 5's bounded gap and Task 6. Specify and implement 2026–27 income tax and ONE approved, sourced benefit slice, prove one household adapter and downstream interaction under source review, then use that template for the remaining benefit slices. Independent policy specifications can be researched concurrently without competing edits.

**Acceptance:** approved source-first specs, benchmarks, golden/regression parity, named native periods and explicit missing/unsupported statuses; a connected end-to-end case reviewed by an independent model/economics reviewer. Do not move unsupported tax or benefit values out of needs_review.

## What not to do

- Do not silently refactor or amend #186–#189 while their respective owners are still active; coordinate handoffs.
- Do not create a fifth broad implementation PR touching the same files as the four stacked B0.1 PRs.
- Do not weaken ADR-0020, statutory-value guards, the source-archive boundary or TypeScript's no-calculation rule.
- Do not overstate completion because this documentation PR or an author preflight is green.
- Do not mix Phase E national representative modelling, fiscal accounting or advanced AI into the B0.1 integration train.
- Do not delete unmerged branches without Pete's Q12 decision.
- Do not call the product multi-user safe without a verified identity/authorisation model.

## Requested Claude Code response / execution order

1. Recheck live main and PRs; reproduce, reject or reclassify each A1–A7 finding with evidence and P1/P2/P3 labels. Distinguish observed code, code-review hypothesis, configuration fact and Tier C decision.
2. Prioritise safe CI runner isolation (A1) and a *documented single-operator synthetic-data-only* boundary for the shared-login pilot (A2); refer operator/identity decisions to Pete.
3. Complete pending exact-final-head independent review of #189's Codex-authored fixes and sequentially land #186→#189 (A3). Preserve all latest existing reviews; do not self-approve.
4. Close/update #183 by reconciling its actual diff, not overwriting main with stale trackers. Keep #154 parked for its Phase F gate.
5. Confirm A4/A5 invariants through targeted tests on the integrated code; create small separate fixes only where gaps remain, each independently reviewed.
6. Present Q15's web-required-check change with the exact check context for Pete; apply only once authorised.
7. After web stack stabilisation, return to canonical household + first statutory vertical slice (A7). Run an early synthetic usability walkthrough without claiming official Pilot 1.

**For each item, report:** disposition; base/head SHA; exact reproducer/test; code/PR link; independent reviewer; remaining Pete action; whether it blocks development, deployment with synthetic data, deployment with real personal data, or formal Pilot 1.

**Closeout criterion:** this review packet is explicitly linked to independently reviewed remediation PRs and/or documented accepted Tier C risk decisions. A docs-only merge is NOT closeout.
