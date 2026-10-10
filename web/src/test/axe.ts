import axe from "axe-core";
import { expect } from "vitest";

/** Fails with each violation's rule, impact and nodes. jsdom has no layout or
 *  paint, so colour-contrast is not checkable here and is left off. */
export async function expectNoAxeViolations(container: Element): Promise<void> {
  const { violations } = await axe.run(container, { rules: { "color-contrast": { enabled: false } } });
  const summary = violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.html).join(" | ")}`);
  expect(summary).toEqual([]);
}
