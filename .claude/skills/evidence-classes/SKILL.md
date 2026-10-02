---
name: evidence-classes
description: Use whenever a task creates or changes a number, source, parameter, dataset, estimate, assumption, scenario, decision record, explanation or test expectation, or produces any model output. Applies the epistemic constitution (doctrine/epistemic-constitution.md) the same way every time. Name each claim's evidence class, record its provenance fields, apply Pete's seven decisions, and stop and flag any case the constitution does not settle.
---

# Evidence classes

`doctrine/epistemic-constitution.md` (approved by Pete, 2 October 2026) is the
authority for what the evidence classes are and how they apply. This skill
applies it and never extends it. The constitution adds to `CLAUDE.md`'s
ground-truth rules and replaces none of them. This skill restates no class
definition beyond naming them. Read the constitution's tables and "Decisions"
section whenever you classify, because this skill points to them and does not
replace them.

Other skills and doctrine still govern their own areas: `provenance` for
sources and datasets, `new-policy` for onboarding a policy,
`doctrine/test-doctrine.md` for protected expected values.

## When to use it

Any task that creates or changes a number, source, parameter, dataset,
estimate, assumption, scenario, decision record, explanation or test
expectation, and any task that produces a model output. If you are unsure
whether a claim is in scope, it is.

## Procedure

1. **Name each claim's class.** Use the eight classes in the constitution's
   table (Fact, Rule, Estimate, Transferred estimate, Assumption, Scenario,
   Model output, AI hypothesis). For repository concepts, use the
   constitution's mapping table, "Mapping today's concepts to the classes".
   Look the concept up there before reasoning from first principles. A
   source catalogue entry and a canonical variable definition are not claims,
   and a `needs_review` or `unsupported` outcome is not a quantity (it has no
   x-hat). The mapping says what each is instead. A `review_status` of
   `needs_review` and the `needs_review` outcome are calculation gates, not
   evidence classes: the class follows the claim's sources and review.
   Every claim has exactly one class, and a class is never relabelled. The
   constitution leaves two gaps on purpose: validation expectations (decision
   1, deferred to Step 6) and existing decision records (decision 3, classed
   in a later change for Pete's confirmation). Leave those without a class,
   and do not assign one yourself.
2. **Record the eleven fields (value, unit, reference period, geography,
   population, source, method, evidence class, uncertainty, model version,
   dependencies) where the artifact supports them today.** The quantity type
   is planned for Task 2.6. Existing output schemas do not carry all eleven
   yet. Do not invent a schema or a field to hold them. Where the artifact
   has a place for one (a manifest, a `source_id`, a dependencies list, a
   decision record), fill it. A field you cannot fill from a cited source is
   left missing and flagged. It is never defaulted.
3. **Apply the seven decisions by number.** When the claim is one of these,
   write the decision number in your notes and PR text:
   - 1: test expectations (spec cases, benchmarks, golden households, golden
     snapshots) are validation cases with no class of their own until Step 6.
     Their protected-value process is unchanged (`doctrine/test-doctrine.md`).
   - 2: data snapshots are Fact or Estimate, by dataset.
   - 3: new decision records state their own class (Rule or Assumption).
     Existing ones are classed later, for Pete's confirmation.
   - 4: synthetic population: inputs keep their classes, the records are a
     Scenario.
   - 5: an explanation inherits the class of the result it explains.
   - 6: a rate cited from an agency page (rank 3) is a Rule, rank in E_x.
   - 7: an Assumption needs a written value, with who chose it and why.
   Programme decision P2 (caller-asserted facts are Scenario) is in the
   mapping table.
4. **Never turn an unknown into zero, or into an Assumption without a
   written value.** An unknown is reported as unknown (a missing fact gives
   `needs_review`). It becomes an Assumption only when someone writes the
   value down, with who chose it and why (decision 7).
5. **AI-drafted content stays an AI hypothesis until it passes its gate.**
   That includes anything Claude Code or GPT/Codex drafts into the
   repository: a source, a value, an interpretation, an estimate. Do not
   label it Fact or Rule. The constitution fixes the minimum today: no
   AI-generated claim becomes a Fact, a Rule or a model input without a cited
   primary source, independent review and, for protected values and
   interpretations, Pete's decision. The AI gate (Task 1.2) will name the gate
   for each kind of artifact and is not in the constitution yet. Do not
   decide a gate yourself. The qualifier is in the constitution's "Ground
   truth": caller Scenarios, explicit Assumptions and calculated Model outputs
   keep their labels and trace their dependencies, and lacking an independent
   statutory source does not turn them into AI hypotheses.
6. **When a claim seems to fit two classes, it is two claims.** Class each
   on its own. **When the constitution does not settle a case, stop and flag
   it for Pete.** Say what you looked up, which two readings remain, and the
   `file:line` that raised it. Do not pick one.

Two rules from the constitution apply when a number is shown. A single
household's Rule output keeps the precision the law sets, and
estimate-dependent figures show their range (non-negotiable 2; the display
rule is Task 1.3). A Transferred estimate is always labelled as borrowed and
never shown as an Estimate for New Zealand.

## Worked examples

Every path below exists in the repository. Classes come from the
constitution's mapping table and decisions. Values are deliberately not shown.

**1. An approved policy parameter.**
`area_cap_with_dependent_children_area1` in
`policy_specs/accommodation_supplement/policy.yaml`, with `source_id`,
`locator` and `review_status: approved`.
Class: Rule. E_x: the source, locator and review. If the source were an
agency rates page (rank 3), it is still a Rule (decision 6), with the rank
recorded.

**2. A caller-asserted fact.**
`household_eligibility` in `policy_specs/accommodation_supplement/facts.yaml`
(`kind: fact_status`), answered `verified` by the caller.
Class: Scenario (Programme decision P2, in the mapping table), even when marked
`verified`. The caller asserted it. It is an input to a run, never a Fact
about the world. If the caller has not answered, it is unknown and the
component gives `needs_review`.

**3. A survey dataset.**
`data/metadata/datasets/stats_nz_household_income_housing_costs.v1.yaml`.
Class: Estimate (decision 2), because survey figures carry sampling error. An
administrative count would be a Fact. Record the class in the manifest only
where the manifest has a field for it. Step 2 adds one, so until then note
it in the PR.

**4. A decision record.**
`policy_specs/accommodation_supplement/decisions/DEC-001-income-excess-rounding.md`
records the income-excess rounding decision.
Class: not yet assigned. Existing records are classed later, for Pete's
confirmation (decision 3), so don't class this one yourself. The test a new
record applies: a Rule if it chooses between readings of the law's text
(decider and date in E_x), an Assumption if the law is silent (visible and
revisable). A new record states its own class. Never edit a hash-bound
existing record to add one.

**5. A synthetic population record.**
A household drawn by `src/poltika/scenarios/microsim/synthetic.py`, carrying
`SYNTHETIC_LABEL` from `src/poltika/semantics/population.py`.
Class: Scenario (decision 4). The published shares behind it keep their
class (decision 2). The listed assumptions in
`data/metadata/populations/nz_synthetic_development.v1.yaml` are
Assumptions. Never present the records as an estimate for New Zealand.

**6. A calculated result.**
A `ComponentResult` with `outcome == "calculated"`
(`src/poltika/engines/simulator/outcome.py`).
Class: Model output, carrying the classes of its dependencies. Here these
are the Rule parameters and the Scenario facts. Its explanation
(`src/poltika/engines/assurance/explanation.py`) inherits that class
(decision 5). A `needs_review` or `unsupported` outcome is not a quantity and
has no x-hat. Conditional `Bounds` are a Model output with D_x and are never
labelled `calculated`.

## Stop conditions

Stop and report, with `file:line`, if: a claim has no class in the
constitution, other than the two gaps it leaves on purpose (validation
expectations, decision 1; existing decision records, decision 3); a Rule has
no resolvable cited primary source or no independent review; a value was
supplied from memory; an AI-drafted claim is being used as a source,
parameter or model input; or a test expectation would change to make a check
pass.
