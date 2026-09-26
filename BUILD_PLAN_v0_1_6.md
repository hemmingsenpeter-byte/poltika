# Poltika v0.1.6 Build Plan: keep v0.1 current

**Date:** 26 September 2026
**Status:** DRAFT for Pete's approval.
**Starts:** after `v0.1.5` ships. The pilot, the GPT/Codex audit and the
release gate come first.
**Hard deadline:** 1 April 2027.

`BUILD_PLAN.md`'s doctrines apply unchanged: primary sources only, the three
test classes, protected expected values changed only through the test
doctrine, and interpretation ambiguity escalated rather than resolved.

## Why this release exists

Every rate Poltika uses stops on 1 April 2027. All 10 Working for Families
and all 38 Accommodation Supplement parameter values end at `2027-04-01`,
as do both policies' reference periods. From that date every household
resolves to "no value for the date", until the 2027-28 year is sourced and
reviewed.

Two things become possible on the same date:

- **The in-work tax credit gap can close.** The 2026-27 year will be
  complete, so whether a reversal Order took effect during it can finally
  be settled. That is what the Task 10.2 rate-status table has held open.
- **Known law changes take effect.** The WFF specification records enacted
  changes to family scheme income adjustments and residence from 1 April
  2027 (`wff-budget-measures-2026`, `wff-ird-interpretation-2026`). These
  are rule changes, not just new rates.

v0.1.6 adds no new policy and no new capability. It keeps v0.1 correct for
the next year and turns keeping it current into a routine.

## Tasks

Owners follow the v0.1 roles: GPT/Codex for sources and interpretation,
Claude Code for implementation, and the other model reviews.

### 1. Close v0.1.5

- **1.1 — Owner by slice.** Fix every finding from the GPT/Codex audit of
  v0.1.5 (`review_packets/v0_1_5_codex_audit.md`), classified under the
  Review Doctrine.
- **1.2 — Pete, then owner by slice.** Triage the pilot's P2-P4 findings
  (`docs/pilot/V0_1_5_PILOT_FINDINGS.md`) into v0.1.6 fixes or the v0.2
  backlog.

### 2. Source currency as a routine

- **2.1 — Claude Code. Scheduled currency report.** A CI job, weekly and on
  demand, runs the Phase 1 evidence report and lists:
  - every source whose last structured check is older than a set age;
  - every parameter interval ending within 90 days;
  - every `needs_review` or open-ended value.

  It opens an issue when anything is due. It reads only the repository;
  fetching sources stays a reviewed human or GPT/Codex step.
- **2.2 — Pete. Network access.** Allow `www.legislation.govt.nz` (and the
  IRD and MSD hosts in the source catalogues) in this environment's network
  settings, so source checks can run here. Until then they run outside it.
- **2.3 — GPT/Codex. Legislation currency check** (carried over from
  v0.1.5 Task 0.5): the Social Security Act and Regulations and the Income
  Tax Act since the last recorded checks, including the claimed September
  2026 Accommodation Supplement legislation.

### 3. Settle the 2026-27 in-work tax credit (after 1 April 2027)

- **3.1 — GPT/Codex. Whole-year Order check.** Check the Taxation (Annual
  Rates for 2025-26, Compliance Simplification, and Remedial Measures) Act
  2026 s 2(43) secondary-legislation record, and the Gazette, for all of
  [2026-04-01, 2027-04-01). Record the result in `sources.yaml` with the
  check date and method.
- **3.2 — Owner per outcome, through the test-doctrine process.**
  - **No Order took effect in the year:** propose `in_work_base` 2026-27 as
    approved. The in-work tax credit and the WFF total become calculable,
    and the README's "no WFF total" limitation is removed.
  - **An Order took effect partway through:** the year is split, which
    the specification's rate-status table makes `unsupported` in this
    branch. Keep it so, and record the Order date.
- **3.3 — Claude Code.** Update the affected spec cases, golden households,
  golden snapshots and explanations through the protected-value process.
  Only the in-work components' expected values change.

### 4. The 2027-28 year

- **4.1 — GPT/Codex. Source the 2027-28 values** for every WFF and
  Accommodation Supplement parameter, once the Orders and MSD's 1 April
  2027 tables are published. Each gets a dated source entry.
- **4.2 — GPT/Codex, with Pete deciding ambiguity. Specification
  update.** Review both specifications against the law in force from
  1 April 2027, including the family scheme income and residence changes
  and the in-work base after the s 105(2) reversal (the specification's
  "on or after 1 April 2027" row). Any interpretation question gets a
  decision record.
- **4.3 — Claude Code. Implement the new year.**
  - Add the 2027-28 values as new intervals in each `policy.yaml`, never
    by editing the 2026-27 ones.
  - Add a new reference period, or make the reference period per year.
  - Implement any rule changes from 4.2.
  - Carry the provenance and explanation layers forward unchanged.
- **4.4 — GPT/Codex. 2027-28 spec cases,** hand-calculated independently
  of the implementation. Claude Code adds benchmark cases if IRD or MSD
  publish 2027-28 worked examples.
- **4.5 — Claude Code. Both years side by side.** Golden households run for
  2026-27 and 2027-28. The 2026-27 results stay byte-identical (the release
  gate's "v0.1 results unchanged" row, applied per year).

### 5. Release

- **5.1 — Claude Code.** Write the CHANGELOG, update
  `docs/releases/` (limitations for 2027-28, and a new baseline), and run
  the release-gate tests. Pete tags `v0.1.6`.

## Sequence

| When | Work |
| --- | --- |
| After v0.1.5 ships | 1.1, 1.2, 2.1, 2.3 |
| When 2027-28 values are published (usually February-March) | 4.1, 4.2, then 4.3 and 4.4 |
| From 1 April 2027 | 3.1-3.3, 4.5, 5.1 |

v0.2 work (`BUILD_PLAN_v0_2.md`) can run in parallel. It touches different
files.

## Exit gate

- Every golden household calculates for both 2026-27 and 2027-28, each from
  approved, sourced values whose intervals cover the year.
- The 2026-27 in-work tax credit is either approved for the whole year or
  recorded as a split year with its Order date.
- The v0.1.5 audit findings and pilot P0/P1 findings are all closed.
- The source-currency report runs in CI.
- Every v0.1.5 release-gate test passes, for both years.

## Open decisions for Pete

- **D1:** Start 4.1 when rates are announced, or wait for the Orders to be
  made? Recommended: prepare as soon as they are announced, and approve
  only once the instrument exists.
- **D2:** One `policy.yaml` with multiple years, or one file per year?
  Recommended: one file with a reference period per year. The loader
  already selects by date.
- **D3:** Network access for this environment (Task 2.2).
