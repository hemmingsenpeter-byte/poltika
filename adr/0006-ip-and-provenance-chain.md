# ADR-0006: IP boundary and provenance chain for v0.1

**Date:** 2026-09-21

**Status:** proposed for Pete's acceptance

**Build-plan task:** 8 (GPT draft)

## Context

ADR-0001 records the external-implementation IP boundary. ADR-0003 records
manual acquisition and immutable statistical snapshots. ADR-0004 records a
one-off early comparative review; it does not replace the later Task 16 check.
The frozen IP, Data Acquisition, Test, and Review Doctrines in `BUILD_PLAN.md`
also require a traceable route from New Zealand sources to policy rules,
parameters, independent expected values, and eventual calculation results.
Those records should be connected without rewriting accepted ADRs or turning
external policy engines into authority.

## Decision

1. **Policy authority.** Each policy claim starts with an applicable New
   Zealand primary source. `sources.yaml` supplies a stable source ID and
   official URL; before a rule or value is approved, its operative version,
   commencement/effective date, and pinpoint provision or agency table must
   be checked for the modelled period. `specification.md` links its rule ID
   to that evidence. A conflict or missing source remains `needs_review` and
   goes through the Review Doctrine; neither model silently resolves it.
2. **Parameters and expected values.** A `policy.yaml` parameter value links
   its source ID, locator, unit, legal effective interval, and review status.
   Hand-calculated `spec_cases.yaml` expectations derive from the reviewed
   specification; `benchmarks.yaml` expectations derive from dated official
   worked examples and an independent recalculation. Task 9's PR visibility
   check, as decided in ADR-0007 (superseding ADR-0005), flags changes to
   those files for review before Pete merges; it is not a merge gate.
   A source-map observation is not an approved parameter or test value.
3. **Statistical data.** A frozen raw snapshot has the eleven provenance
   fields listed in the Data Acquisition Doctrine: source organisation,
   dataset/series, source URL/identifier, retrieval date,
   observation/reference period, units, geography/population, retrieval
   method, raw snapshot/version, transformation/version, and canonical
   variable mapping. `manual_download` is the v0.1 retrieval method. A
   transformation version or canonical mapping not yet known at acquisition
   is explicitly pending, never guessed; both are resolved before use as a
   regression fixture or calculator input. The simulator consumes canonical
   variables, not raw snapshots or source-specific formats.
4. **External prior art.** ADR-0001 and the frozen IP Doctrine govern all
   external-project contact. Task 3's structural-only exception is recorded
   in `docs/research/task_3_structural_glance.md`; ADR-0004 separately records
   the one-off wider review. Neither supplies policy rules, values, formulas,
   implementation code, or expected test results. Task 16 still occurs only
   after the WFF test suite is complete: record the inspected URLs/revisions
   and coverage categories, then return to primary sources to derive any
   missing case independently. The required one-line sequence confirmation
   is due when that later touchpoint actually happens, not pre-certified here.

## Consequences

- A calculation's eventual provenance chain can identify the policy source,
  rule, dated parameter, independent test evidence, and, where relevant,
  immutable dataset snapshot and transformation that supplied a canonical
  variable. Task 31 implements the full report; this ADR does not claim it
  exists today.
- Tasks 10 and 22 must strengthen source locators and dated-law checks where
  the Task 2 inventories currently give only a broad URL or coverage note.
  Unsupported or ambiguous cases are not silently mapped to zero entitlement.
- This ADR documents existing frozen decisions and accepted ADRs. It changes
  no IP licence conclusion, review role, task timing, or policy interpretation.
