/** A stored ISO timestamp in the reader's locale; the text unchanged if it
 *  does not parse. */
export function formatWhen(value: string | null): string {
  if (value === null) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("en-NZ", { dateStyle: "medium", timeStyle: "short" });
}
