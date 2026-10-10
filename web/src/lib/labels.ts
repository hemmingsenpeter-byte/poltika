/** "family_tax_credit_rate" -> "Family tax credit rate". Ids are shown
 *  readable; no meaning is added. */
export function humanise(id: string): string {
  const text = id.replace(/_/g, " ").trim();
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** An API `Period` is half-open: it includes `from` and stops before `to`. */
export function periodWords(period: { from: string; to: string }): string {
  return `from ${period.from}, up to but not including ${period.to}`;
}
