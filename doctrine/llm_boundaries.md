# LLM boundaries

## Rule

The LLM layer never calculates policy outcomes and never memorises or
calculates statutory/external data values. Its job is limited to
translation (natural language → structured `ScenarioRequest`) and
explanation of an already-computed, deterministic result.

Full detail: [ARCHITECTURE.md's "critical architectural rule"
section](../ARCHITECTURE.md#critical-architectural-rule-the-llm-never-calculates-policy-outcomes)
and its ["external statistical data acquisition"
section](../ARCHITECTURE.md#external-statistical-data-acquisition).

## Applies to

- `src/poltika/llm/` (target directory — see REPOSITORY_STRUCTURE.md)
- Any code that builds or consumes a `ScenarioRequest`
- Any prompt, tool definition, or agent instruction that could imply the
  model should produce a number rather than orchestrate/explain one
