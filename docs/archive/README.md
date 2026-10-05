# Historical planning archive

These files are historical planning records. They are retained for decision
provenance and must not be used as the current build order. See the root
[BUILD_PLAN_PROGRAMME.md](../../BUILD_PLAN_PROGRAMME.md).

Archiving a plan preserves its scope and reasoning; it does not abandon its
useful code or declare its release complete. Open obligations are carried into
[PROGRAMME_STATUS.md](../../PROGRAMME_STATUS.md).

## Snapshot provenance

Captured on 3 October 2026 from verified GitHub main
`e52f5d35913fbb4b81c7b64c6caf6d446c158759`. Every document below is byte-identical
to its original path at that commit. Dates in filenames identify the historical
plan or status, not a claim about when its final edit occurred.

| Original path | Preserved snapshot |
| --- | --- |
| `BUILD_PLAN_PROGRAMME.md` | [ADR-0019 programme](programmes/2026-09-29-adr0019-master-programme.md) |
| `ROADMAP.md` | [ADR-0019 roadmap](roadmaps/2026-09-29-roadmap-adr0019.md) |
| `PROGRAMME_STATUS.md` | [Pre-migration status](status/2026-10-03-programme-status-adr0019.md) |
| `ROADMAP_REALIGNMENT.md` | [W1–W10 realignment](programmes/2026-09-26-roadmap-realignment.md) |
| `BUILD_PLAN_v0_1_5.md` | [v0.1.5 execution plan](build-plans/2026-09-25-v0-1-5-build-plan.md) |

Snapshot bodies are immutable. Their original relative references describe the
repository at their original location; use the original commit to resolve a
historical link. Current navigation belongs in this README or the live master,
not in rewritten snapshot bodies.

ADRs remain in `adr/`, delegated decisions in `docs/decision_log.md`, release
evidence in `docs/releases/`, and review history in `reviews/` and
`review_packets/`. None is moved or erased by this archive.

`BUILD_PLAN.md` remains at the root as a frozen v0.1 record because substantive
constraints and existing links still depend on its doctrine anchors. Its old
roadmap section cannot determine current sequencing. `BUILD_PLAN_v0_2.md` stays
at the root solely for release completion until `v0.2.0` is tagged.

## Supplied programme authority

[Economist-first migration brief](programmes/2026-10-03-economist-first-migration-brief.md)
is a byte-identical copy of Pete's original supplied text, recovered from the
3 October attachment and archived on 5 October 2026. Unlike the snapshots above,
it records the instruction that led to ADR-0021. Pete reconfirmed the Analyst
Workbench as the first product on 5 October; the detailed design remains Q9.
