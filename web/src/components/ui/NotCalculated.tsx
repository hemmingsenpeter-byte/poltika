import { Minus } from "lucide-react";

import { formatCount, formatMoney, NOT_CALCULATED, type Period, type Precision } from "@/format";

/** The marker for a value the API did not calculate. Never "0". */
export function NotCalculated() {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-sm border border-dashed border-border-strong px-1.5 text-xs text-muted"
      title="No value was calculated"
    >
      <Minus aria-hidden="true" className="size-3" />
      {NOT_CALCULATED}
    </span>
  );
}

export function Money({
  value,
  precision,
  period,
}: {
  value: string | null;
  precision: Precision;
  period?: Period;
}) {
  if (value === null) return <NotCalculated />;
  return <span className="num">{formatMoney(value, period ? { precision, period } : { precision })}</span>;
}

export function Count({ value, precision }: { value: string | null; precision: Precision }) {
  if (value === null) return <NotCalculated />;
  return <span className="num">{formatCount(value, { precision })}</span>;
}
