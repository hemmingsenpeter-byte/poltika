# Roadmap

## v0.1

- Seed the repository structure
- Stabilize project doctrine and ADRs
- Create the source-first policy schema foundations
- Review and reconcile authoritative sources for WFF and Accommodation Supplement
- Validate the initial policy spec structure
- Acquire and freeze the minimum required external statistical datasets
  (Stats NZ, Treasury, IRD, MSD) as versioned, provenance-tagged raw
  snapshots — manual acquisition, not a live API dependency

## Later

- Implement policy logic using vertical slices
- Add regression protections and benchmark coverage
- Expand policy coverage with reviewed source packs
- Automate external data ingestion (Stats NZ API connector, scheduled
  refreshes, additional government-source connectors, schema-change
  detection, broader dataset coverage) beneath the same canonical-variable
  contract established in v0.1
