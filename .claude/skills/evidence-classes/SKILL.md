---
name: evidence-classes
description: Use whenever adding or changing anything that produces, stores, shows or publishes a number in Poltika (an engine output, a population table, an API field, a page, a report, a forecast, a baseline or a causal estimate), or when classifying a value as fact, rule, estimate, transferred estimate, assumption, scenario, model output or AI hypothesis. Applies doctrine/epistemic-constitution.md the same way every time.
---

# Evidence classes

`doctrine/epistemic-constitution.md` is the authority. This skill is the
checklist for applying it. If the two disagree, the doctrine wins and this
file is fixed.

## Before you add a number anywhere

1. **Name its class.** Use section 6's mapping table for anything that
   already exists. For something new, ask:
   - Is it read from a published source? `fact`.
   - Is it law, regulation, an accounting identity, or a decided
     interpretation, and `approved`? `rule`.
   - Did a person choose it as a hypothetical (a reform, a described
     household)? `scenario`.
   - Is it stated because we don't know it? `assumption`.
   - Is it estimated from data? `estimate` for New Zealand evidence,
     `transferred_estimate` for another population's, and it must come
     from the causal library (Step 12).
   - Is it calculated from the above? `model_output`, with its
     dependencies.
   - Did a model (Claude Code, GPT/Codex, a runtime LLM) produce it, and
     has it not passed its gate (section 7)? `ai_hypothesis`, and it
     can't enter a calculation.
2. **Fill all eleven fields** (section 2): X = (x̂, D_x, E_x), value,
   uncertainty and evidence. A field that can't apply
   states why, and nothing is defaulted. `unknown` stays unknown and is
   never zero.
3. **Set its uncertainty honestly.** `exact` only for a Rule applied to
   stated inputs. Otherwise use an `interval` (true bounds or points, as
   `Bounds` records), a `distribution`, or `unquantified` with a reason.
4. **Apply the precision rule (P3) when showing it, never when storing
   it.** A single household's statutory result keeps legal precision.
   Population, baseline and estimate-dependent figures are shown to
   three significant figures with their range.
5. **Check the never-build list** (section 5). In particular: no party
   or plan scores, no default objective, no population result without
   its grade, and no wording that claims more than the level of the least
   mature model behind it (for example "digital twin" before Level 7,
   `doctrine/model-governance.md`).

## Before you promote a model-drafted artifact

Find its row in section 7. It leaves `ai_hypothesis` only when that row's
condition holds and its enforcement passes. Model memory is never a
source.

## When classifying is genuinely ambiguous

Stop and flag it for Pete, as with any interpretation ambiguity. Don't
pick the stronger class to make a result look better.
