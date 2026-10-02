# Agent Instructions - Poltika

## Before making changes

Read:

- BUILD_PLAN.md
- ARCHITECTURE.md
- REPOSITORY_STRUCTURE.md - before creating any new production file, module, or directory; a proposed component with no obvious location means updating that file deliberately, not creating an ad-hoc directory
- relevant files under doctrine/
- relevant policy specification under policy_specs/

## Ground truth

Policy rules must be derived from cited primary NZ sources.

Never use model memory as authority for:

- statutory rates
- thresholds
- eligibility rules
- abatement rules
- effective dates
- policy interactions

If the source is missing or ambiguous, stop and flag it.

## Implementation

Follow the vertical-slice approach defined in BUILD_PLAN.md.

Do not:

- introduce speculative abstractions
- redesign the architecture without explicit approval
- change statutory expected test values simply to make tests pass
- silently resolve policy interpretation ambiguity

## Tests

Maintain the three test classes:

1. Spec
2. Benchmark
3. Regression

Protected statutory expected values require the process defined in doctrine/test-doctrine.md.

## Review

Use the discrepancy taxonomy in doctrine/review-doctrine.md.

Before publishing or recommending acceptance of an implementation PR, use
`.claude/skills/pr-review-preflight/SKILL.md`. An author preflight is not the
independent reviewer rotation required by BUILD_PLAN.md.

Interpretation ambiguity must be escalated rather than silently resolved.

## External prior art

Follow doctrine/ip-doctrine.md.

OpenFisca or other external implementations must not be used as the source for Poltika policy logic.

## GitHub and Render

The repository remote is `https://github.com/hemmingsenpeter-byte/poltika.git` on branch `main`.

Use the Render MCP server for Render workspace, service, deploy, log, metric, and database operations. Confirm the target Render workspace before creating or changing resources.
