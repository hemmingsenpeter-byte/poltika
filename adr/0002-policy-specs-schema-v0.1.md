# ADR 0002: Policy Specs schema v0.1

- Status: Proposed
- Date: 2026-09-20

## Context

The policy specification layer needs a stable structure that can capture sources, policy decisions, and benchmark expectations without premature abstraction.

## Decision

The project will begin with a minimal schema and source-first structure under policy_specs/. The schema is intentionally provisional and will be refined only after source review and evidence mapping.

## Consequences

- Policy rules are defined with source evidence first
- Schema changes require explicit review and traceability
- Implementation work waits until the schema is sufficiently stable and grounded
