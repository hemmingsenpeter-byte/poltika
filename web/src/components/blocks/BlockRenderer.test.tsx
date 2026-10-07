import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Block } from "@/domain";
import { BLOCKS } from "@/test/fixtures/workspace";

import { BlockRenderer } from "./BlockRenderer";

const byType = (type: string) => BLOCKS.find((b) => b.type === type)!;

describe("BlockRenderer", () => {
  it("renders every block type inside a wrapper with id block-{id}", () => {
    const { container } = render(
      <div>
        {BLOCKS.map((b) => (
          <BlockRenderer key={b.id} block={b} />
        ))}
      </div>,
    );
    for (const b of BLOCKS) expect(container.querySelector(`#block-${b.id}`)).not.toBeNull();
    expect(screen.getByText("Family Tax Credit: change in total entitlement")).toBeInTheDocument();
    expect(screen.getByText("Second limitation.")).toBeInTheDocument();
    expect(screen.getByText("2027-28")).toBeInTheDocument();
    expect(screen.getByText("Synthetic population.")).toBeInTheDocument();
    expect(screen.getByText("Apply the rate.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Population runner" })).toHaveAttribute("href", "/models/population_runner");
  });

  it("shows outcome words for a missing metric value, never 0", () => {
    render(<BlockRenderer block={byType("metric")} />);
    expect(screen.getByText("Not calculated")).toBeInTheDocument();
    expect(screen.getByText("Needs review")).toBeInTheDocument();
    expect(screen.getByText("$123M per tax year")).toBeInTheDocument();
    expect(screen.queryByText(/\$0\b/)).toBeNull();
    expect(screen.queryByText(/^0$/)).toBeNull();
  });

  it("opens the tab and block named by a provenance chip", () => {
    const onOpen = vi.fn();
    render(<BlockRenderer block={byType("metric")} onOpen={onOpen} />);
    fireEvent.click(screen.getByRole("button", { name: /Fiscal: Fiscal components/ }));
    expect(onOpen).toHaveBeenCalledWith("fiscal", "fiscal_components");
  });

  it("renders population table cells to three significant figures with outcome markers", () => {
    render(<BlockRenderer block={byType("table")} />);
    const table = screen.getByRole("table", { name: "Who is affected" });
    expect(within(table).getByText("Who is affected")).toBeInTheDocument();
    for (const header of within(table).getAllByRole("columnheader")) {
      expect(header).toHaveAttribute("scope", expect.stringMatching(/^col(group)?$/));
    }
    expect(within(table).getAllByRole("columnheader", { name: "Measure" })[0]).toHaveAttribute("scope", "col");
    expect(within(table).getByText("1.23M")).toBeInTheDocument();
    expect(within(table).getByText("1.23k")).toBeInTheDocument();
    expect(within(table).getByText("Not calculated")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: /Who is affected/ })).toHaveAttribute("tabindex", "0");
    expect(screen.getByText("Weighted households.")).toBeInTheDocument();
  });

  it("preserves exact household and parameter cells in a table", () => {
    const block = byType("table");
    if (block.type !== "table" || !("columns" in block)) throw new Error("Missing table fixture");
    render(<BlockRenderer block={{
      ...block,
      columns: block.columns.map((column) => ({ ...column, precision: "household_rule" })),
      rows: [["Household rule", "1234567", "1234.567"]],
    }} />);
    expect(screen.getByText("1,234,567")).toBeInTheDocument();
    expect(screen.getByText("1,234.567")).toBeInTheDocument();
  });

  it("shows recorded calculation inputs verbatim without adding units", () => {
    render(<BlockRenderer block={byType("calculation_chain")} />);
    const inputs = screen.getByLabelText("Recorded inputs");
    expect(screen.getByText("amount")).toBeInTheDocument();
    expect(screen.getByText("1234.567")).toBeInTheDocument();
    expect(screen.getByText("365")).toBeInTheDocument();
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
    expect(inputs).not.toHaveTextContent("per week");
  });

  it("renders sources with a safe link, and check evidence in a details element", () => {
    render(<BlockRenderer block={byType("sources")} />);
    const link = screen.getByRole("link", { name: "IRD Family Tax Credit" });
    expect(link).toHaveAttribute("href", "https://example.org/ftc");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noreferrer"));
    expect(screen.getByText("Check evidence").closest("details")).not.toBeNull();
  });

  it.each(["heatmap", "constructor", "toString"])("says %s is unsupported instead of crashing", (type) => {
    const unknown: Block = { type, id: "x" };
    render(<BlockRenderer block={unknown} />);
    expect(screen.getByText(/Unsupported block/)).toBeInTheDocument();
  });
});
