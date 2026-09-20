---
name: policy-spec-draft
description: Draft or revise Poltika POLICY_SPECS schema and WFF/Accommodation Supplement specifications from independently mapped primary sources. Use for Tasks 4, 10, and 22 when a reviewable source-linked design or policy spec is needed, not for implementation or test coding.
---

# Policy Spec Draft

1. Read `BUILD_PLAN.md`, `policy_specs/SCHEMA.md`, and both policies' `sources.yaml` and `specification.md`. Keep Task 2 source maps distinct from the later reviewed implementation specifications.
2. Derive only the fields and relationships the two policies require: people and assessment units, policy-specific inputs and income definitions, effective-dated parameters, source provenance, and explicit unsupported or unresolved cases. Preserve separate schema, policy, and effective-date versions.
3. For each proposed field, rule, exception, and parameter, give its source-map identifier or mark it as a design inference needing review. Do not let an external engine supply eligibility rules, values, formulas, or benchmark expectations.
4. Surface genuine interpretation choices and their effects as open decisions for Pete. Leave accepted ADRs and frozen doctrine unchanged unless expressly tasked with a new decision artifact.
5. Produce a concise reviewable change and hand off schema feasibility questions to Claude Code for Task 7. Do not treat drafting as approval to implement a policy vertical slice before its Task 10 or 22 review gate.
