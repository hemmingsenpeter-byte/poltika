# ADR-0021: Economist-first, pilot-driven programme sequencing

**Date:** 3 October 2026
**Status:** accepted strategic direction. Pete supplied the approved migration
brief and instructed Codex to run it on 3 October 2026. This records that explicit
authority; it does not infer acceptance of other proposed decisions.
**Supersedes:** ADR-0019 for programme sequencing only.

## Context

The ADR-0019 programme scheduled national semantics and infrastructure ahead of
connected household analysis and external use. The repository now has working
WFF/AS engines, provenance, explanations, scenarios and replay, a PostgreSQL
scenario store, data contracts, synthetic microsimulation, weighting statistics,
cross-validation, analyst pages, hosted hardening and a Workbench backend.
Rebuilding these would discard useful work. The shortest rigorous path to
credible economic analysis connects them into complete analytical slices and
tests their usefulness with real analysts.

The reconnaissance preceded all edits. Its durable evidence, classifications,
old-to-new mapping and PR sequence are in
[the reconciliation report](../docs/programme/2026-10-03-reconciliation.md).
Exact pre-migration planning snapshots are in
[the archive](../docs/archive/README.md).

## Decision

1. `BUILD_PLAN_PROGRAMME.md` is the single authoritative current build order.
   It uses capability phases A–P: stabilise; household kernel; assurance and
   analyst product; Pilot 1; representative microsimulation; fiscal/report
   output; Pilot 2; demand-driven coverage; historical validation; behaviour
   and causality; dynamic national model; domain models; digital-twin
   infrastructure; decision intelligence; public/research infrastructure; AI.
2. Build complete analytical vertical slices, validate them, put them in front
   of real users, and generalise infrastructure when multiple real models
   require it. Finish bounded professional-baseline work substantially underway,
   then stop expanding abstract foundations.
3. `BUILD_PLAN_v0_3.md` supplies the household lane; `BUILD_PLAN_v0_1_6.md`
   supplies statutory maintenance. `BUILD_PLAN_v0_2.md` remains a release-closeout
   plan until its tag exists. Releases evidence capabilities; versions do not
   impose a competing programme order.
4. Bring household tax/benefit connections, disposable income, incentive
   measures, legislation conformance and model validation forward. Reuse the
   existing Workbench backend and export contracts as the first analyst product
   surface. Pilot 1 does not require representative national estimates.
5. Representative population validation precedes national claims; direct fiscal
   accounting and an independently challengeable economist report precede
   Pilot 2. Demand and pilot evidence increasingly determine later expansion.
6. Grow the National Variable Registry from actual model contracts. Preserve
   built schemas and current provenance. General evidence/causal graphs, broad
   shared state, federation, ABM and uncertainty machinery are introduced only
   by the later capability that demonstrates their need.
7. Preserve ADR-0019's enduring principles: common semantics, epistemic classes,
   model governance, provenance, validation, explicit uncertainty, model
   composition, human control of objectives, the national-system destination,
   and late AI with no numerical authority. Digital-twin branding requires
   Phase M's validated state-estimation and connected-model gate.
8. Preserve doctrine and ADR-0020. Interpretation, protected values, Māori data
   governance, microdata access, public/IP/licensing decisions, external
   resources, release tags and deletion of history remain within their existing
   authority boundaries. Codex does not acquire Claude Code's delegated merge
   authority through this decision.
9. Historical plans remain recoverable. ADRs, reviews, decision records and
   release evidence stay in their established locations. No production behaviour,
   policy rule, protected value, data snapshot or API semantics changes here.

## Reserved decisions and existing approvals

This direction resolves the strategic first-product question (old P8) in favour
of the Analyst Workbench. It does **not** accept ADR-0018's specific design:
that ADR remains proposed, with the minimum acceptance action in `PETE_QUEUE.md`.
ADR-0017's accepted shared-household decision remains operative. Old P6, P7,
P13, P14, P18 and P20 remain Pete's and are mapped to their new capabilities.
P11's historical horizon is raised when historical work starts. Source-dependent
household slices, disposable-income definitions, annualisation and combined
income measures are not decided by this programme document.

Approved epistemic classifications and the temporary deferral for validation
expectations remain unchanged. References to old Step 6 now lead to Phase C's
validation work; the prediction ledger is separately deferred to Phase I.
Missing facts, unquantified uncertainty and unsupported coverage remain visible.

## Migration and review

The changes are prepared in four bounded review units: decision/archive/report;
master/roadmap/status; operational references; detailed household lane. These
units require coordinated integration: staging an ADR/status change alone is
not completion of the authority migration. Until the companion instructions
and lane are integrated, reviewers must treat the draft stack as incomplete.
The final checkout must expose exactly one active master, with all instructions
agreeing. Author preflight and a same-model subagent audit do not claim the
independent reviewer rotation or authorise merging this stack.

## Consequences

Completed assets and unfinished review/release obligations remain visible.
Household modelling no longer waits for a universal ontology, full graph or
national state schema. External pilots become evidence gates. The long-term
architecture remains in `ARCHITECTURE.md`; this ADR changes implementation order,
not the architecture or numerical ground truth.

A later reorder needs a new recorded decision against this reasoning.
