import { ArrowUpRight } from "lucide-react";
import { lazy, Suspense } from "react";

import { Card } from "@/components/ui/Card";
import { Pill } from "@/components/ui/Pill";
import type { MetricBlock } from "@/domain";
import { formatCount, formatMoney } from "@/format";
import { humanise } from "@/lib/labels";

import { OutcomeMarker } from "./Outcome";

// Loaded on demand: only metrics with two or more calculated options draw a chart.
const MetricChart = lazy(() => import("@/components/charts/MetricChart"));

export type OpenBlock = (tab: string, blockId: string) => void;

function MetricValueText({ block, value }: { block: MetricBlock; value: MetricBlock["values"][number] }) {
  if (value.value === null || value.outcome !== "calculated") {
    return <OutcomeMarker outcome={value.outcome === "calculated" ? "not_calculated" : value.outcome} />;
  }
  const { unit, precision } = block;
  if (unit.currency === "NZD") {
    return <span className="num font-display text-2xl font-semibold">{formatMoney(value.value, { precision, ...(unit.period ? { period: unit.period } : {}) })}</span>;
  }
  return (
    <span className="num font-display text-2xl font-semibold">
      {formatCount(value.value, { precision })} <span className="text-sm font-normal text-muted">{unit.label}</span>
    </span>
  );
}

export function MetricCard({ block, onOpen }: { block: MetricBlock; onOpen?: OpenBlock | undefined }) {
  return (
    <Card className="min-w-0">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="text-base font-semibold">{block.label}</h3>
        <Pill tone="neutral">{block.evidence_class}</Pill>
      </div>
      <ul className="mt-4 space-y-2">
        {block.values.map((v) => (
          <li key={v.option} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <span className="text-base text-muted">{v.option}</span>
            <MetricValueText block={block} value={v} />
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-muted">{block.context}</p>
      {block.values.filter((v) => v.outcome === "calculated" && v.value !== null).length >= 2 ? (
        <Suspense fallback={<p role="status" className="mt-4 text-xs text-muted">Loading chart…</p>}>
          <MetricChart block={block} />
        </Suspense>
      ) : null}
      {block.provenance.length > 0 ? (
        <ul className="mt-3 flex flex-wrap gap-2" aria-label="Where this comes from">
          {block.provenance.map((p) => (
            <li key={`${p.tab}/${p.block_id}`}>
              <button
                type="button"
                onClick={() => onOpen?.(p.tab, p.block_id)}
                className="inline-flex min-h-[24px] items-center gap-1 rounded-sm border border-border-strong px-2 py-0.5 text-xs font-semibold text-accent hover:border-accent hover:bg-accent-soft"
              >
                {humanise(p.tab)}: {humanise(p.block_id)}
                <ArrowUpRight aria-hidden="true" className="size-3" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
}
