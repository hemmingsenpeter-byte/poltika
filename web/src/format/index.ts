/**
 * Central formatters (ADR-0023). Inputs are the decimal strings the API sends.
 * Arithmetic here is display scaling only (3 significant figures, a percentage
 * point shift); no formatter combines two values. A missing value is never
 * zero: `null` gives the NOT_CALCULATED marker text.
 */

export const NOT_CALCULATED = "Not calculated";
export const NOT_YET_AVAILABLE = "Not yet available";

/** U+2212, so a minus lines up with a plus in tabular figures. */
const MINUS = "−";

export type Precision = "household_rule" | "population_estimate";
export type Period = "tax_year" | "week";

const DECIMAL = /^(-?)(\d+)(?:\.(\d+))?$/;

type Parts = { negative: boolean; whole: string; fraction: string };

function parse(value: string): Parts | null {
  const m = DECIMAL.exec(value.trim());
  if (!m) return null;
  const whole = (m[2] ?? "0").replace(/^0+(?=\d)/, "");
  const fraction = m[3] ?? "";
  const negative = m[1] === "-" && /[1-9]/.test(whole + fraction);
  return { negative, whole, fraction };
}

function group(whole: string): string {
  return whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

const SUFFIXES = [
  { suffix: "k", size: 1e3 },
  { suffix: "M", size: 1e6 },
  { suffix: "B", size: 1e9 },
] as const;

/** 3 significant figures with a k/M/B suffix, from the magnitude of `abs`. */
function threeSignificant(abs: number): string {
  if (abs < 1000) return Number(abs.toPrecision(3)) >= 1000 ? "1.00k" : plain3(abs);
  let index = 0;
  for (let i = SUFFIXES.length - 1; i >= 0; i -= 1) {
    if (abs >= SUFFIXES[i]!.size) {
      index = i;
      break;
    }
  }
  let scaled = abs / SUFFIXES[index]!.size;
  // 999.6k rounds to 1.00M, not 1000k.
  if (Number(scaled.toPrecision(3)) >= 1000 && index < SUFFIXES.length - 1) {
    index += 1;
    scaled = abs / SUFFIXES[index]!.size;
  }
  return `${plain3(scaled)}${SUFFIXES[index]!.suffix}`;
}

function plain3(n: number): string {
  const text = n.toPrecision(3);
  return text.includes("e") ? String(Number(text)) : text;
}

function unit(period: Period | undefined): string {
  return period ? ` ${periodLabel(period)}` : "";
}

export function periodLabel(period: Period): string {
  return period === "tax_year" ? "per tax year" : "per week";
}

export function formatMoney(
  value: string | null,
  options: { precision: Precision; period?: Period },
): string {
  if (value === null) return NOT_CALCULATED;
  const parts = parse(value);
  if (!parts) return value;
  const sign = parts.negative ? MINUS : "";
  if (options.precision === "household_rule") {
    const fraction = parts.fraction ? `.${parts.fraction}` : "";
    return `${sign}$${group(parts.whole)}${fraction}${unit(options.period)}`;
  }
  const abs = Number(`${parts.whole}.${parts.fraction || "0"}`);
  return `${sign}$${threeSignificant(abs)}${unit(options.period)}`;
}

export function formatCount(value: string | null, options: { precision: Precision }): string {
  if (value === null) return NOT_CALCULATED;
  const parts = parse(value);
  if (!parts) return value;
  const sign = parts.negative ? MINUS : "";
  if (options.precision === "household_rule") {
    const fraction = parts.fraction ? `.${parts.fraction}` : "";
    return `${sign}${group(parts.whole)}${fraction}`;
  }
  return `${sign}${threeSignificant(Number(`${parts.whole}.${parts.fraction || "0"}`))}`;
}

/** Shift the decimal point two places right: a fraction becomes a percentage. */
function percentNumber(fraction: string): number | null {
  const parts = parse(fraction);
  if (!parts) return null;
  const digits = (parts.whole + parts.fraction.padEnd(2, "0")).replace(/^0+(?=\d)/, "");
  const scale = parts.fraction.length > 2 ? parts.fraction.length - 2 : 0;
  const magnitude = Number(digits) / 10 ** scale;
  return parts.negative ? -magnitude : magnitude;
}

function signed(n: number, withPlus: boolean): string {
  const text = Math.abs(n).toFixed(1);
  const isZero = Number(text) === 0;
  if (isZero) return text;
  if (n < 0) return `${MINUS}${text}`;
  return withPlus ? `+${text}` : text;
}

/** "-0.012" is -1.2%. */
export function formatPercent(fraction: string | null): string {
  if (fraction === null) return NOT_CALCULATED;
  const n = percentNumber(fraction);
  return n === null ? fraction : `${signed(n, false)}%`;
}

/** Percentage points: "0.021" is "+2.1 pp". */
export function formatPp(fraction: string | null): string {
  if (fraction === null) return NOT_CALCULATED;
  const n = percentNumber(fraction);
  return n === null ? fraction : `${signed(n, true)} pp`;
}
