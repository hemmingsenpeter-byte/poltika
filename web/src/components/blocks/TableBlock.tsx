import type { BlockOf } from "@/domain";
import { formatCount, formatExact, outcomeOfCell } from "@/format";

import { OutcomeMarker } from "./Outcome";

type Table = BlockOf<"table">;

function Cell({ column, cell }: { column: Table["columns"][number]; cell: string | null }) {
  // An empty numeric cell is a missing value, never a blank that reads as zero.
  if (cell === null || (cell === "" && column.kind !== "text")) return <OutcomeMarker outcome="not_calculated" />;
  const outcome = outcomeOfCell(cell);
  if (outcome) return <OutcomeMarker outcome={outcome} />;
  if (column.kind === "text") return <>{cell}</>;
  return <span className="num">{
    column.precision === "population_estimate"
      ? formatCount(cell, { precision: column.precision })
      : formatExact(cell)
  }</span>;
}

/** A semantic table with column groups, a sticky header and a keyboard-focusable
 *  scroll container. Column precision preserves household rules and parameter
 *  strings while showing population aggregates to three significant figures. */
export function TableBlockView({ block }: { block: Table }) {
  const label = block.title ?? "Table";
  const groups: { name: string | null; span: number }[] = [];
  for (const column of block.columns) {
    const name = column.group ?? null;
    const last = groups[groups.length - 1];
    if (last && last.name === name) last.span += 1;
    else groups.push({ name, span: 1 });
  }
  const grouped = groups.some((g) => g.name !== null);
  return (
    <div>
      <div
        tabIndex={0}
        role="region"
        aria-label={`${label} (scrollable)`}
        className="max-h-[32rem] overflow-auto rounded-md border border-border bg-surface"
      >
        <table className="w-full border-collapse text-left text-sm">
          <caption className="sr-only">{label}</caption>
          <thead className="sticky top-0 z-10 bg-surface-muted text-xs text-muted">
            {grouped ? (
              <tr>
                {groups.map((g, i) => (
                  <th key={i} scope="colgroup" colSpan={g.span} className="px-3 py-1.5 text-center font-medium">
                    {g.name ?? ""}
                  </th>
                ))}
              </tr>
            ) : null}
            <tr>
              {block.columns.map((c) => (
                <th
                  key={c.id}
                  scope="col"
                  className={`px-3 py-2 font-medium ${c.kind === "text" ? "" : "text-right"}`}
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {block.rows.map((row, r) => (
              <tr key={r} className="border-t border-border align-top">
                {block.columns.map((c, i) => {
                  const cell = row[i] ?? null;
                  const className = `px-3 py-2 ${c.kind === "text" ? "" : "num text-right"}`;
                  return i === 0 && c.kind === "text" ? (
                    <th key={c.id} scope="row" className={`${className} font-normal`}>
                      <Cell column={c} cell={cell} />
                    </th>
                  ) : (
                    <td key={c.id} className={className}>
                      <Cell column={c} cell={cell} />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {block.notes.length > 0 ? (
        <ul className="mt-2 space-y-1 text-xs text-muted">
          {block.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
