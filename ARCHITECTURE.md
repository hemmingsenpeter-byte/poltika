# Architecture

This repository is organized around a disciplined source-first workflow.

## Core intent

- Capture authoritative policy sources and traceability
- Define policy specifications in a schema-driven format
- Maintain review and discrepancy standards
- Implement policy logic only after source-grounded derivation

## Directory roles

- `doctrine/`: foundational project rules, standards, review expectations, and scope boundaries
- `adr/`: architecture decisions with rationale and context
- `policy_specs/`: policy source packs, schema descriptions, and policy definitions
- `reviews/`: review and discrepancy records

## Design principle

Poltika does not treat model memory or external implementations as authoritative policy sources. Evidence and source packaging come first.
