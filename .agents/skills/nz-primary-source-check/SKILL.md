---
name: nz-primary-source-check
description: Verify a New Zealand WFF or Accommodation Supplement policy claim against dated primary legislation and official IRD/MSD guidance before it enters a Poltika source map, specification, or benchmark. Use for source audits and effective-date checks, not external-engine comparisons.
---

# NZ Primary Source Check

1. Read `BUILD_PLAN.md` and the relevant `policy_specs/<policy>/sources.yaml` and `specification.md`. Identify the precise claim, population, assessment period, and date being modelled.
2. Check the official legislation version in force on that date and pinpoint the provision. Check relevant IRD/MSD operational guidance separately; distinguish guidance, legislation, published examples, and inference. Verify amendments and commencement dates rather than assuming the latest page applies historically.
3. Record a stable source identifier, official URL, provision or page locator, source version, effective period, retrieval date, and the claim it supports in the existing source map. Preserve uncertainty where the source does not settle an interpretation.
4. Flag conflicting or incomplete sources for Pete's ambiguity decision with the competing readings and citations. Do not silently select a rule, statutory value, or benchmark expectation.
5. Treat external policy engines as non-authoritative for policy meaning or expected figures. Follow `doctrine/ip-doctrine.md` and the frozen IP Doctrine in `BUILD_PLAN.md` before any external inspection.
