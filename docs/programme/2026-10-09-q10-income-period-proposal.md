# Q10: canonical income and assessment-period proposal

**Date:** 9 October 2026. **Status:** proposed for Pete; no statutory
transformation or common-period measure is approved by this document.
Decision owner: Pete; specification/source review: GPT/Codex; bounded
implementation: Claude. Existing [Q10](../../PETE_QUEUE.md), D2 definition
and policy review gates remain open.

The existing [#191 recommendation](https://github.com/hemmingsenpeter-byte/poltika/pull/191#issuecomment-6069451786)
has not become an accepted decision. This proposal gives it a bounded
contract for Tasks 5, 6 and 9–11, using [ADR-0017](../../adr/0017-shared-household-model.md),
[ADR-0021](../../adr/0021-economist-first-pilot-programme.md), the existing
WFF/AS interaction contract and the current semantics registries. It adds no
engine, generic national data model or unsourced arithmetic.

## Wording proposed for acceptance

Retain person-level, dated income facts with their asserted status, source
or caller attestation, amount, currency, gross/net meaning and observation
period. Identify the people and applicable family/claimant unit explicitly.
A missing fact stays missing. A caller's assertion remains a Scenario rather
than an independently verified Fact.

Derive separate policy assessment inputs for individual income tax, WFF,
Accommodation Supplement and each main benefit through versioned,
source-backed mappings. Each mapping names the applicable dated provision,
policy version, assessment unit, period, inclusions/exclusions, verification
requirements and rounding/precision gate. Shared storage of facts does not
make different statutory income concepts interchangeable.

Retain native annual and weekly calculation outputs. Never annualise one
observed weekly entitlement automatically or allocate annual income to a
week by an undocumented division. Period containment alone authorises no
conversion. Pro-rating in the parked household draft is unaccepted input
that must pass the same source and interpretation review before reuse.

Consolidated disposable income or EMTR needs an accepted official definition,
explicit common reference period and income path, supported component
coverage and stated allocation/annualisation assumptions. Unknown or
unsupported components do not become zero. Until these gates pass, report
the original per-component outcomes and units; calculate no mixed-period
total or apparent complete EMTR.

## Bounded implementation contract

| Task | Required boundary | Evidence before acceptance |
| --- | --- | --- |
| 5 | Map existing policy/input units to registered unit, period and entity qualifiers; introduce no conversion | Every existing policy unit maps or is refused; calculated values unchanged |
| 6 | Canonical people, relationships and dated income facts; explicit policy-specific adapters | Independently derived source mappings, unknown/conflicting-fact probes, byte-identical existing WFF/AS golden results and scenario identities |
| 9 | Dependency edges only for reviewed policy mappings and interactions | Period/version coverage and unsupported-path tests; no implicit circular or shared-income assumptions |
| 10 | Source-reviewed disposable-income definition and common-period coverage | Pete's D2/Q10 acceptance; all exclusions and uncalculated components visible |
| 11 | EMTR on a precisely declared income perturbation/path and common period | Each rerun uses the same supported coverage; unknowns remain explicit; independently derived conformance and benchmark cases |

Validation proceeds alongside each slice. Preserve the existing
[WFF specification](../../policy_specs/working_for_families/specification.md)
and [AS interaction contract](../../policy_specs/accommodation_supplement/specification.md),
including separate policy definitions, caller-derived income inputs, native
periods and no combined total. This proposal neither revises their rates nor
creates a new income exclusion or entitlement.

## Remaining decisions and effect

Accepting this contract would permit bounded household implementation and
specification work. It would not approve legal transformations, tax precision,
benefit annualisation or a complete disposable-income/EMTR amount. Each new
mapping requires dated NZ primary evidence and independent review; missing
sources or interpretation conflicts stop that mapping and go to Pete.

The smallest next implementation PR is Task 5's policy-unit/period mapping
patch. Task 6 follows its acceptance, reusing only reviewed parked-draft
content. Do not begin new tax or benefit engines under this proposal.
