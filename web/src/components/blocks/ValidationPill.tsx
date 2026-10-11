import { Pill, type PillTone } from "@/components/ui/Pill";
import { humanise } from "@/lib/labels";

/** `levels` runs from least to most validated. The least is flagged; the
 *  rest are shown plainly. A level is never worded as approval. */
export function ValidationPill({ label, levels }: { label: string; levels: readonly string[] }) {
  const tone: PillTone = levels.indexOf(label) <= 0 ? "warn" : "info";
  return <Pill tone={tone}>{humanise(label)}</Pill>;
}
