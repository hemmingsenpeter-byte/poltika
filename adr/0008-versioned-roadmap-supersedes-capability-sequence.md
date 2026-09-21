# ADR-0008: Versioned roadmap supersedes the capability-driven Roadmap Doctrine

**Date:** 2026-09-21
**Status:** accepted (Pete)

## Context

BUILD_PLAN.md's Roadmap Doctrine fixed v0.1/v0.1.5/v0.2, then declared
everything after v0.2 an unordered, non-version-numbered "capability
sequence" (Hypothesis → Assurance → cross-domain Discovery → ...), on the
basis that "actual order may shift based on development and customer
evidence." `ROADMAP.md` was rewritten into a fully versioned v0.2–v0.9+
sequence with defined scope and exit gates per release, and explicitly
flagged itself as proposing a change to that frozen doctrine, not silently
overriding it.

Comparing the two surfaced two apparent contradictions beyond the
version-numbering framing itself:

1. `ROADMAP.md` redefines v0.2 as "Authoritative data foundation" (Stats
   NZ/Treasury connectors), where the old doctrine defined v0.2 as "more
   policies + uncertainty + narrow on-demand Discovery."
2. `ROADMAP.md` pins the Stats NZ API connector to v0.2, where the Data
   Acquisition Doctrine says it "is not a fixed-version item... available
   wherever a later phase needs it."
3. `ROADMAP.md` orders Assurance (v0.5) → Discovery (v0.6) → Hypothesis
   (v0.7); the old doctrine's sequence was Hypothesis → Assurance →
   cross-domain Discovery — a different order, not just different labels.

## Decision

**Adopt `ROADMAP.md`'s versioned sequence. Supersede the Roadmap Doctrine's
capability-sequence framing entirely**, on the basis that tracing actual
dependencies between these capabilities shows the new order is the one that
holds up, not an arbitrary restructuring:

- v0.2 (data) → v0.3 (policy interaction graph) → v0.4 (scenario engine) is
  strictly dependency-ordered: no historical reconstruction or scenario
  comparison is possible without real data and a dependency graph to
  propagate a parameter change through first.
- v0.5 (Assurance) belongs before Discovery/Hypothesis, not after: it
  hardens the deterministic core (backtesting, sensitivity, stress-testing
  the v0.1–v0.4 Simulator/Scenario engine) before anything exploratory or
  uncertain is allowed near it — the same principle as the frozen Scope
  Doctrine's "deterministic correctness before probabilistic
  sophistication," applied one level up.
- v0.6 (Discovery) before v0.7 (Hypothesis) is not a style choice, it is
  forced by logic: a hypothesis cannot be tested before Discovery has
  proposed a candidate relationship to test. `ROADMAP.md`'s own v0.7
  section already states this as an explicit gate:
  `Discovery -> Hypothesis -> evidence -> validation -> human approval -> model specification -> tests -> Simulator`.
  Nothing from Discovery or Hypothesis re-enters the hardened Simulator
  without passing that full gate.
- The old doctrine's Hypothesis → Assurance → Discovery order does not hold
  up against this tracing: it tests hypotheses before Discovery has
  generated candidates and before Assurance has hardened what results would
  feed back into.

On the Stats NZ pinning: this is a resolution of the old doctrine's
deliberate vagueness, not a violation of it. The "not pinned to a version"
language existed because at v0.1 no later phase had been concretely scoped
yet. Now that v0.2 is defined as the data-foundation release, pinning the
connector there is exactly the "later phase needs it" the old text gestured
at without naming.

## Consequences

- BUILD_PLAN.md's Roadmap Doctrine section is rewritten to state
  `ROADMAP.md`'s sequence as the frozen roadmap, with the dependency
  reasoning above included directly in the doctrine text — so a future
  reader does not have to reverse-engineer it, the way arriving at this ADR
  required.
- `ROADMAP.md`'s self-flagged "Planning status" conflict note is resolved
  and removed; `ROADMAP.md` is now operative, not a proposal.
- v0.1/v0.1.5 scope, acceptance criteria, and BUILD_PLAN.md's task list are
  unchanged — this ADR is post-v0.1 sequencing only.
- Later evidence may still justify reordering a specific release (the
  frozen doctrine's original caution about shifting order was reasonable in
  principle); any such change is itself a new decision against this ADR's
  stated dependency reasoning, not a silent drift back to the old sequence.
