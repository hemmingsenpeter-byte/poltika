# Poltika v0.1 Build Plan

This build plan defines the project guardrails for the initial release. The repository is intentionally structured to keep policy interpretation and implementation separate until authoritative sources are captured and reviewed.

## Frozen principles

1. Primary policy sources are authoritative.
2. Policy rules must be derived from cited primary NZ sources.
3. Model memory is never used as authority for rates, thresholds, eligibility, abatement, or effective dates.
4. Ambiguity is recorded as a decision artifact with evidence, rationale, owner, and date.
5. Do not begin WFF or Accommodation Supplement implementation before source grounding and schema agreement.

## Definition of Done

A feature is only considered complete when all of the following are true:

- the relevant policy source pack is attached and reviewed;
- the interpretation is traceable to evidence;
- any interpretation ambiguity encountered has a recorded decision artifact with evidence considered, rationale, decision owner and date;
- the corresponding spec or benchmark is updated and verified;
- the change is tested in the correct class: Spec, Benchmark, or Regression.

## Vertical-slice workflow

1. Source pack
2. Map policy rules from sources
3. External structural check
4. Derive POLICY_SPECS v0.1
5. Repository critique
6. CI guardrail
7. WFF implementation
8. Accommodation Supplement implementation

## Guardrails

- No speculative abstraction before the schema is stable.
- No external implementation code is used as a policy source.
- No policy logic is implemented before the policy-spec structure is checked.
- No ambiguity is silently resolved without an ADR or decision record.
