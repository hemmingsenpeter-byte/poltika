# Model governance

**Status:** draft by Claude Code, awaiting Pete's approval (Task 1.5 of
`BUILD_PLAN_PROGRAMME.md`). Items marked "For Pete:" are left to Pete by the
plan, or are choices this draft makes and Pete must confirm.

## Rule

Every model and engine Poltika runs has a registry entry and a model card.
Nothing about a model changes silently. Every output carries the validation
status of the least mature model it relies on. Language follows evidence.

This doctrine states process. It states no rate, threshold or policy value.
Those come from cited primary NZ sources under `policy_specs/`.

## Applies to

- Every engine and runner now: the Working for Families (WFF) engine, the
  Accommodation Supplement (AS) engine, the combined runner and the population
  runner.
- Every later model, from the first line of its code.
- It extends the constitution's fourth non-negotiable (no model expansion
  without tests) and its "no silently changing models" item
  (`doctrine/epistemic-constitution.md`).

## What counts as a model

A model is an engine (it calculates a policy outcome) or a runner (it runs
engines over households). Poltika finds them mechanically, so none is missed:

- A public, module-level function named `run_*` or `calculate_*` anywhere under
  `src/poltika` is an engine entry point.
- Each one found must be an entry point of a registered model, or be listed in
  the registry's `not_engines` with a reason and the model it wraps.
- Each subpackage of `poltika.engines` must hold a registered entry point, or be
  listed in `not_model_packages` with a reason.

`tests/unit/engines/assurance/test_model_registry.py` checks this in CI. A new
engine with no entry fails the build.

For Pete: the discovery rule is by function name. A model whose entry point is
named otherwise would not be found. Confirm the rule, or name another.

## The registry

The registry is `model_registry/registry.yaml`. Its cards are in
`model_registry/cards/`. Both live in a new top-level directory, recorded in
`REPOSITORY_STRUCTURE.md`. The reason: a model is neither a policy source pack
(`policy_specs/`), nor process (`doctrine/`), nor a dataset (`data/metadata/`,
which the data-snapshot guard watches). It is reviewed data, so it is YAML, like
those.

Each entry records:

| Field | Meaning |
| --- | --- |
| `id`, `name`, `kind` | A stable id, a name, and `engine` or `runner`. |
| `version`, `version_basis` | The version, and where it comes from. |
| `owner` | Who owns it. |
| `purpose` | What it does, in one short paragraph. |
| `entry_points` | The functions the discovery rule finds. |
| `depends_on` | The registered models it relies on. |
| `validation` | The level, its basis, and links to the validation cases, tests and reviews, and the open items. |
| `evidence_classes_consumed` | The constitution's classes it consumes, and a note on where each comes from. |
| `limitations` | What it does not do, each with its source file. |
| `model_risks` | Where it could mislead, each with its source file. |
| `change_log` | The change records (below). |

A field the repository does not say is `unknown`. It is never invented. A
validation case count is `unknown` when no file records one.

Version today: no model has a version of its own. The registry records the
package version (`pyproject.toml`) and says so. Each run records the source
commit (`CodeIdentity`) and the policy versions it ran against. For Pete: decide
whether each model should carry its own version. The package version is 0.1.0
although the repository has released later milestones.

Owner today: the repository names roles, not people (`BUILD_PLAN_PROGRAMME.md`,
"Owners"): GPT/Codex for sources, interpretation and independent review, Claude
Code for implementation, Pete for decisions. The registry records those roles.
For Pete: name the owner of each model.

## Validation status

A model's validation status is one level, linked to the cases that support it.
Levels run from least to most mature:

| Level | Meaning |
| --- | --- |
| `not_validated` | No validation case passes. |
| `spec_validated` | It passes hand-calculated spec cases and published worked examples for its declared supported domain. It makes no empirical or predictive claim. |

The four existing models are `spec_validated`. The population runner's level
covers its arithmetic only. Its population is synthetic, and its results are
never an estimate for New Zealand (`docs/releases/V0_2_LIMITATIONS.md`).

Later levels (for example validated against an estimate, then against a
predictive record) come from the validation framework (Step 6) and the ledger.
They are not defined here.

For Pete: approve the two level names and their meaning, and the level given
to each model. Define the later levels at Step 6. The plan sets tolerances
when each milestone is first reached (P18), so this doctrine sets none.

## Model-change controls

Every material change to a rule, parameter, relationship or engine has a change
record in the model's `change_log`, in the same pull request as the change.
Nothing changes silently. A change record states:

1. **What changed.** The files, rules or parameters, and the version.
2. **Why.** The task, decision or finding that required it.
3. **The evidence.** The cited source, decision record or review that supports it.
4. **The validation re-run.** Which validation cases and tests were run, and
   their result.
5. **The approval.** Who approved it, and when.

A change to a protected expected value keeps the process in
`doctrine/test-doctrine.md`. This doctrine adds a change record to it. It does
not replace it. A change made to improve a validation score needs the same
record as any other change (`doctrine/epistemic-constitution.md`).

The first records for each model were written from the repository's history
when it was registered. Where the repository doesn't say what was re-run or
who approved, the record says `unknown (recorded before change records
existed)`. They are not backfilled from memory.

The registry check does not yet fail a change to an entry-point file that has no
change record. For Pete: decide whether CI should require it, and who approves
a change that touches no protected value.

## Model cards

A card states a model's methods, validation, limitations and known failure
modes. It is generated from the registry by
`python -m poltika.engines.assurance.model_cards` and is never edited by hand.
`--check` fails if a card is missing, stale, or has no registry entry, and the
same test runs it in CI.

Cards use the registry's validation section. When the validation framework
(Step 6) produces validation reports, the generator reads them too.

## Validation gates, graduation, demotion, labels and language

These come from "Phases, milestones and validation gates" in
`BUILD_PLAN_PROGRAMME.md`. They are restated here and not changed.

- **Every stage has a validation gate.** Poltika does not move from built to
  trusted because the code works. A phase's milestone is claimed only when
  validation evidence shows Poltika can reliably answer its question.
- **Graduation** to a milestone is a decision by Pete, recorded against the
  validation evidence (Step 6). The tolerances are set when each milestone is
  first reached (P18).
- **Demotion.** A milestone can be lost when the evidence stops supporting it,
  and outputs are relabelled. A model's level is lowered in the registry with a
  change record that cites the evidence.
- **Labels.** Every output carries the validation status of the least mature
  model it relies on. `Registry.label()` computes it from `depends_on`. No
  output schema carries the label yet. That belongs to the mechanical checks
  (Task 1.6) and the validation framework (Step 6).
- **Language follows evidence.** Nothing is described as predictive before the
  ledger's record supports it. Poltika is not called a digital twin before
  Phase 5's milestone.

For Pete: set the demotion triggers (what evidence stops supporting a level).
The plan says a milestone can be lost, and not what triggers it.

## Adding a model

1. Write its tests and validation cases first (non-negotiable 4).
2. Add its registry entry, with every field filled from repository evidence.
3. Run `python -m poltika.engines.assurance.model_cards` and commit the card.
4. Run `pytest -q`. The registry check must pass.

## Hooks for later tasks

| Task | What it adds |
| --- | --- |
| 1.6, mechanical checks | A release-gate row that outputs carry the label, and that no page claims a milestone not reached |
| 6, validation framework | Validation reports for the cards, and the levels beyond `spec_validated` |
| 18, continuous state estimation | Diagnosed updates, recorded as change records (the plan, "Model governance" row) |
