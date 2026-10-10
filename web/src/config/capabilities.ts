/** Capabilities (ADR-0023): what this deployment offers. `/api/v1/meta` can
 *  switch them; until it answers, only policy comparison is on. */
export const CAPABILITY_IDS = [
  "policy_comparison",
  "outcome_explorer",
  "evidence_search",
  "assurance_dashboard",
  "collaboration",
  "natural_language_scenarios",
  "monte_carlo",
  "advanced_distributions",
] as const;

export type CapabilityId = (typeof CAPABILITY_IDS)[number];
export type Capabilities = Record<CapabilityId, boolean>;

export const DEFAULT_CAPABILITIES: Capabilities = {
  policy_comparison: true,
  outcome_explorer: false,
  evidence_search: false,
  assurance_dashboard: false,
  collaboration: false,
  natural_language_scenarios: false,
  monte_carlo: false,
  advanced_distributions: false,
};

/** The defaults, overridden by whatever `meta.capabilities` states. Unknown
 *  keys are ignored. */
export function resolveCapabilities(fromMeta?: Readonly<Record<string, boolean>>): Capabilities {
  const resolved: Capabilities = { ...DEFAULT_CAPABILITIES };
  if (!fromMeta) return resolved;
  for (const id of CAPABILITY_IDS) {
    const stated = fromMeta[id];
    if (typeof stated === "boolean") resolved[id] = stated;
  }
  return resolved;
}
