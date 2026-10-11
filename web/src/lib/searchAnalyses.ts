import type { Registry } from "@/domain";
import { humanise } from "@/lib/labels";

export type AnalysisMatch = {
  key: string;
  instrumentId: string;
  instrument: string;
  parameterId: string;
  label: string;
  unit: string;
};

/** A plain filter over the supported instruments' parameters by label. It
 *  does not interpret the question: every word must appear in the label or
 *  the instrument's title. */
export function searchAnalyses(registry: Registry, query: string): AnalysisMatch[] {
  const words = query.toLowerCase().split(/\s+/).filter((w) => w.length > 0);
  if (words.length === 0) return [];
  const matches: AnalysisMatch[] = [];
  for (const instrument of registry.instruments) {
    if (!instrument.valid || !instrument.runnable) continue;
    for (const parameter of instrument.parameters) {
      const label = humanise(parameter.id);
      const haystack = `${label} ${instrument.title}`.toLowerCase();
      if (words.every((w) => haystack.includes(w))) {
        matches.push({
          key: `${instrument.id}/${parameter.id}`,
          instrumentId: instrument.id,
          instrument: instrument.title,
          parameterId: parameter.id,
          label,
          unit: parameter.unit_label,
        });
      }
    }
  }
  return matches;
}
