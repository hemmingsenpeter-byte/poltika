import { Minus } from "lucide-react";

import { OUTCOME_WORDS, type Outcome } from "@/format";

/** The marker for a value with no number: its outcome in words, never "0". */
export function OutcomeMarker({ outcome }: { outcome: Exclude<Outcome, "calculated"> }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-sm border border-dashed border-border-strong px-1.5 text-xs text-muted">
      <Minus aria-hidden="true" className="size-3" />
      {OUTCOME_WORDS[outcome]}
    </span>
  );
}
