# Task 3: structural-only OpenFisca Aotearoa glance

**Date:** 21 September 2026  
**Status:** Complete for Task 3 only; not the post-suite Task 16 coverage check.

## Boundary and sequence

The independent Working for Families and Accommodation Supplement source maps
were completed before this inspection. This is the narrow Week 0 exception in
`BUILD_PLAN.md`: external material may inform only entity and parameter *shape*.
No external policy values, eligibility tests, formulas, implementation code,
test names, or coverage claims were used to derive Poltika policy meaning.

The separate comparative review in `nz_policy_engines_review.md` was performed
before the WFF suite exists. It is **not** this Task 3 evidence record and does
not satisfy Task 16. Its broader conclusions are held apart from Task 4 pending
Pete's decision about the sequencing deviation; no claim is made that both
external touchpoints followed the frozen sequence.

## Structural observations

| Observed concept | External structural reference | Relevance already present in Poltika's source maps |
| --- | --- | --- |
| A person is distinct from group entities; a person can hold a role in a family, tenancy, or ownership group. | [OpenFisca's entity overview](https://openfisca.org/doc/key-concepts/person_entities_role.html) identifies these as Aotearoa model entity categories and roles. | WFF's claimant/partner/child and shared-care periods, and AS's claimant/partner/joint-tenant/owner facts, already require explicit relationships. The exact group types and role names for Poltika must be derived from those NZ sources, not copied from OpenFisca. |
| Variables are associated with a person or group and a period; parameters are not values of a particular household. | [Variables](https://openfisca.org/doc/key-concepts/variables.html) and [parameters](https://openfisca.org/doc/key-concepts/parameters.html). | The Task 2 maps distinguish household facts (income, care, tenure) from dated statutory rates and thresholds. Task 4 should keep these categories separate. |
| Time can be represented with dated instants and periods. | [Periods and instants](https://openfisca.org/doc/key-concepts/periods_instants.html). | Both policies have effective dates and part-period cases. Task 4 must define its own date/period contract from the statutes and use cases. |
| Parameters may be grouped, effective-dated, typed by unit, and linked to a source reference. | [Parameter documentation](https://openfisca.org/doc/coding-the-legislation/legislation_parameters.html). | Poltika already requires effective-dated values, source IDs, and dataset provenance. Task 4 should specify only the fields its two policies need, including value-level authority and effective date. |

## Task 4 handoff

The schema design questions to settle from Poltika's own sources are: which
person-to-group relationships must be explicit, which facts belong to a person
versus an assessment unit or accommodation arrangement, how period-specific
membership is represented, and how parameter units, effective dates, and
source references are recorded. Do not assume that OpenFisca's entity catalogue,
default-value behaviour, parameter tree, or file layout is Poltika's design.
In particular, a missing or unsupported fact must not become a false or zero
entitlement merely because another engine supports variable defaults.

This record contains structural categories only. Task 16's external test-name
coverage check remains strictly after the WFF suite is complete.
