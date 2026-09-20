---
name: clean-room-boundary
description: Check Poltika's clean-room and sequencing rules before inspecting OpenFisca Aotearoa, PolicyEngine NZ, or another external policy engine. Use for Task 3 structural review, Task 16 coverage checks, and proposed out-of-window comparative research.
---

# Clean-Room Boundary

1. Read the frozen IP Doctrine in `BUILD_PLAN.md`, `doctrine/ip-doctrine.md`, and `adr/0004-external-review-sequencing-deviation.md`. Check the current task and whether its prerequisite source map or test suite is complete.
2. Task 3 permits only a schema-shape glance at OpenFisca Aotearoa after Task 2 mapping: entity and parameter structure, not policy values, eligibility, abatement, code, tests, or implementation detail. See `docs/research/task_3_structural_glance.md` for the completed inspection.
3. Task 16 occurs only after the WFF suite is complete. Inspect external test names or coverage categories, including both named comparators in ADR-0004; derive every missing case independently from New Zealand primary sources before changing Poltika tests or specifications.
4. For a requested inspection outside those windows, identify the deviation before proceeding. Pete may explicitly authorize bounded research; record its scope and timing in a dated decision artifact. ADR-0004 records one exception, not a standing change to doctrine.
5. Log exactly which external URLs and revisions were viewed, when, and for what structural or coverage purpose. Keep external code, formulas, values, test content, and calculated outputs out of Poltika's policy authority and benchmark chain.
