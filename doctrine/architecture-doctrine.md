# Architecture doctrine

Architecture should remain minimal while policy logic is still under source review.

## Principles

- Prefer explicit structure over speculative abstractions
- Keep policy schema and implementation distinct
- Preserve traceability to cited rules and sources
- Delay major refactors until the policy model is stable

## Consequences and objectives

Poltika models consequences. Humans choose objectives. The Simulator computes
the consequences of a validated scenario; it does not choose a preferred
policy or encode political preferences in a hidden objective function.
Simulation must be separable from search: any future Policy Search capability
generates scenarios and evaluates results against explicit human-defined
objectives and constraints outside the deterministic policy calculators.
This is an architectural boundary, not a v0.1 feature or a change to the
frozen build-plan sequence.
