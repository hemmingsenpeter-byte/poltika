import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MetricCard } from "@/components/blocks/MetricCard";
import type { MetricBlock } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

const BLOCK: MetricBlock = {
  type: "metric",
  id: "m1",
  title: null,
  label: "Change in entitlement",
  unit: { label: "NZD per tax year", currency: "NZD", period: "tax_year", basis: "nominal", per: "population" },
  values: [
    { option: "Option A", value: "1200000", outcome: "calculated" },
    { option: "Option B", value: "-300000", outcome: "calculated" },
    { option: "Option C", value: null, outcome: "needs_review" },
  ],
  precision: "population_estimate",
  evidence_class: "Model output",
  context: "Weighted households.",
  provenance: [],
};

describe("MetricChart", () => {
  it("shows unit, source, a text summary, a table alternative, and never a zero for a missing value", async () => {
    const { container } = render(<MetricCard block={BLOCK} />);
    const chart = await screen.findByRole("img", { name: /Change in entitlement\. Option A/ });
    expect(chart).toBeInTheDocument();
    expect(screen.getByText(/Unit: NZD per tax year/)).toHaveTextContent("Source: Model output");
    expect(chart.getAttribute("aria-label")).toMatch(/Option C: not calculated/);
    expect(chart.querySelectorAll("svg > g rect").length).toBe(2); // one bar per calculated option, none for C
    expect(screen.getByRole("table", { name: "Change in entitlement, by option" })).toBeInTheDocument();
    expect(screen.getByText("Needs review", { selector: "text" })).toBeInTheDocument();
    await expectNoAxeViolations(container);
  });

  it("draws no chart when fewer than two options are calculated", () => {
    const one = { ...BLOCK, values: [BLOCK.values[0]!, BLOCK.values[2]!] };
    render(<MetricCard block={one} />);
    expect(screen.queryByRole("img")).toBeNull();
  });
});
