import { DataTable } from "@/components/ui/DataTable";
import type { MetricBlock } from "@/domain";
import { formatCount, formatMoney, OUTCOME_WORDS } from "@/format";

import { OutcomeMarker } from "@/components/blocks/Outcome";

type Row = MetricBlock["values"][number];

/** The text the API's value gets on screen: the same formatting as the card. */
export function metricText(block: MetricBlock, v: Row): string {
  if (v.value === null) return "Not calculated";
  const { unit, precision } = block;
  if (unit.currency === "NZD") return formatMoney(v.value, { precision, ...(unit.period ? { period: unit.period } : {}) });
  return `${formatCount(v.value, { precision })} ${unit.label}`;
}

/** Bars only for options whose value the API calculated. Bar length is a
 *  display scale of the API's decimal string; nothing is derived or combined. */
export function plottable(block: MetricBlock): { row: Row; n: number }[] {
  const out: { row: Row; n: number }[] = [];
  for (const row of block.values) {
    if (row.outcome !== "calculated" || row.value === null) continue;
    const n = Number(row.value);
    if (Number.isFinite(n)) out.push({ row, n });
  }
  return out;
}

const PATTERNS = ["solid", "diagonal", "dots", "cross"] as const;
const ROW_H = 36;
const LABEL_W = 170;
const BAR_W = 300;
const VALUE_W = 190;

function Defs({ idp }: { idp: string }) {
  return (
    <defs>
      <pattern id={`${idp}-diagonal`} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="var(--color-surface)" />
        <rect width="3" height="6" fill="var(--color-ink)" />
      </pattern>
      <pattern id={`${idp}-dots`} width="6" height="6" patternUnits="userSpaceOnUse">
        <rect width="6" height="6" fill="var(--color-surface)" />
        <circle cx="3" cy="3" r="1.6" fill="var(--color-ink)" />
      </pattern>
      <pattern id={`${idp}-cross`} width="6" height="6" patternUnits="userSpaceOnUse">
        <rect width="6" height="6" fill="var(--color-surface)" />
        <path d="M0 0L6 6M6 0L0 6" stroke="var(--color-ink)" strokeWidth="1" />
      </pattern>
    </defs>
  );
}

function fill(idp: string, i: number): string {
  const p = PATTERNS[i % PATTERNS.length]!;
  return p === "solid" ? "var(--color-ink)" : `url(#${idp}-${p})`;
}

/** A horizontal bar chart of one metric's options (B0.1.6). Each bar has its
 *  own pattern and a printed value, so no meaning rests on colour. Bars share
 *  one zero line and one scale, so lengths compare directly. */
export default function MetricChart({ block }: { block: MetricBlock }) {
  const bars = plottable(block);
  const idp = `chart-${block.id}`;
  const max = Math.max(...bars.map((b) => Math.abs(b.n)), 0);
  const hasNegative = bars.some((b) => b.n < 0);
  const zeroX = LABEL_W + (hasNegative ? BAR_W / 2 : 0);
  const half = hasNegative ? BAR_W / 2 : BAR_W;
  const rows = block.values;
  const height = rows.length * ROW_H + 8;
  const period = block.unit.period === "tax_year" ? "per tax year" : block.unit.period === "week" ? "per week" : null;
  const summary = `${block.label}. ${rows
    .map((r) => `${r.option}: ${r.outcome === "calculated" && r.value !== null ? metricText(block, r) : "not calculated"}`)
    .join("; ")}.`;

  return (
    <figure className="mt-4">
      <figcaption className="text-xs text-muted">
        Unit: {block.unit.label}
        {period && !block.unit.label.includes(period.replace("per ", "")) ? `, ${period}` : ""}
        {block.unit.per ? `, per ${block.unit.per}` : ""}. Source: {block.evidence_class}. {block.context}
      </figcaption>
      {/* The bars need about 36rem to stay legible, so a narrow screen scrolls
          this region sideways; the summary and table below carry the same values. */}
      {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
      <div tabIndex={0} role="region" aria-label={`${block.label} (scrollable chart)`} data-chart-scroller className="mt-2 max-w-3xl overflow-x-auto">
      <svg
        role="img"
        aria-label={summary}
        viewBox={`0 0 ${LABEL_W + BAR_W + VALUE_W} ${height}`}
        className="w-full min-w-[36rem]"
      >
        <Defs idp={idp} />
        <line x1={zeroX} x2={zeroX} y1={0} y2={height} stroke="var(--color-border-strong)" />
        {rows.map((r, i) => {
          const y = i * ROW_H + 4;
          const bar = bars.findIndex((b) => b.row === r);
          const n = bar >= 0 ? bars[bar]!.n : null;
          const w = n !== null && max > 0 ? (Math.abs(n) / max) * half : 0;
          return (
            <g key={r.option}>
              <text x={LABEL_W - 8} y={y + 18} textAnchor="end" fontSize="12" fill="var(--color-ink)">
                {r.option}
              </text>
              {n === 0 ? (
                // An exact zero has no length: an open circle on the zero line
                // marks it, and the printed value says it.
                <circle data-zero cx={zeroX} cy={y + ROW_H / 2 - 2} r={4} fill="var(--color-surface)" stroke="var(--color-ink)" />
              ) : n !== null ? (
                <rect
                  x={n < 0 ? zeroX - w : zeroX}
                  y={y + 4}
                  width={w}
                  height={ROW_H - 12}
                  fill={fill(idp, bar)}
                  stroke="var(--color-ink)"
                />
              ) : null}
              <text x={LABEL_W + BAR_W + 8} y={y + 18} fontSize="12" fill="var(--color-ink)">
                {n !== null ? metricText(block, r) : r.outcome === "calculated" ? "Not calculated" : OUTCOME_WORDS[r.outcome]}
              </text>
            </g>
          );
        })}
      </svg>
      </div>
      <p className="mt-1 text-sm">{summary}</p>
      <details className="mt-2 text-sm">
        <summary className="cursor-pointer text-accent">Show as a table</summary>
        <div className="mt-2">
          <DataTable
            caption={`${block.label}, by option`}
            rows={rows}
            rowKey={(r) => r.option}
            columns={[
              { key: "option", header: "Option", render: (r) => r.option },
              {
                key: "value",
                header: `Value (${block.unit.label})`,
                numeric: true,
                render: (r) =>
                  r.outcome === "calculated" && r.value !== null ? metricText(block, r) : <OutcomeMarker outcome={r.outcome === "calculated" ? "not_calculated" : r.outcome} />,
              },
            ]}
          />
        </div>
      </details>
    </figure>
  );
}
