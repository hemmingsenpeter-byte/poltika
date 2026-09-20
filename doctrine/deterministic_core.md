# Deterministic core

## Rule

External datasets parameterise Poltika's deterministic core; they do not
train it. Source acquisition is decoupled from canonical representation:
simulation engines consume only canonical Poltika variables and must never
directly consume a source-specific format or API (a Stats NZ response, a
CSV structure, an endpoint).

`raw → processed → canonical variables → simulator` — never `raw →
simulator`.

Full detail: [BUILD_PLAN.md's Data Acquisition
Doctrine](../BUILD_PLAN.md#data-acquisition-doctrine-frozen),
[ARCHITECTURE.md's "external statistical data acquisition"
section](../ARCHITECTURE.md#external-statistical-data-acquisition), and the
[dependency boundary in
REPOSITORY_STRUCTURE.md](../REPOSITORY_STRUCTURE.md#the-dependency-boundary).

## Applies to

- `src/poltika/data/`, `src/poltika/semantics/`, `src/poltika/engines/simulator/`
  (target directories — see REPOSITORY_STRUCTURE.md)
- Any code path that reads `data/raw/` or `data/processed/` outside the
  `data/` transformation layer
