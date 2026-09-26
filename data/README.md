# data/

v0.2's data layer (`BUILD_PLAN_v0_2.md`). The pipeline is the Data
Acquisition Doctrine's:

authoritative source → raw snapshot → transformation and validation →
canonical variable → downstream code

| Path | Holds | Edited by hand? |
| --- | --- | --- |
| `raw/<organisation>/<dataset_id>/v<N>/` | Snapshots exactly as published | Added, never edited or deleted |
| `metadata/datasets/<dataset_id>.v<N>.yaml` | One manifest per snapshot (`poltika.data.manifest`) | Added with its snapshot, never edited |
| `metadata/variables/dictionary.yaml` | The canonical variable dictionary (`poltika.semantics.variables`) | Yes, reviewed |

A correction is a new snapshot version with a new manifest. The
`data-snapshot-guard` CI check fails if a committed snapshot or manifest is
modified, renamed or deleted, and a test fails if a snapshot's SHA-256
doesn't match its manifest.

Raw snapshots are committed to git (they are small published tables). A
snapshot too large to commit comfortably, or one whose licence doesn't allow
redistribution, needs a decision before it is added: it must not be
silently gitignored, or the registry can't verify it.

Every manifest field must come from the publication itself. If one can't be
verified, stop and flag it (`.claude/skills/provenance/SKILL.md`).

Nothing outside `src/poltika/data/` reads these files. Everything else asks
`poltika.data.context.DataContext` for canonical variables.
