import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MetricCard } from "@/components/blocks/MetricCard";
import { AppShell } from "@/components/layout/AppShell";
import { DataTable } from "@/components/ui/DataTable";
import { Tabs } from "@/components/ui/Tabs";
import { buttonClasses } from "@/components/ui/Button";
import { DEFAULT_CAPABILITIES } from "@/config/capabilities";
import type { MetricBlock } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

// jsdom has no layout, so these pin the classes that make the narrow-width
// behaviour (about 360px) rather than measure it. docs/web/FRONTEND.md lists
// what still needs a real browser.
vi.mock("next/navigation", () => ({ usePathname: () => "/" }));
vi.mock("@/components/layout/MetaProvider", () => ({
  MetaProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useMeta: () => ({ meta: { status: "loading" }, capabilities: DEFAULT_CAPABILITIES }),
}));

const classes = (el: Element) => el.className.split(/\s+/);

describe("narrow-width structure", () => {
  it("the header wraps rather than overflowing, and the menu button is a touch-sized target", () => {
    render(<AppShell>content</AppShell>);
    const header = screen.getByRole("banner");
    expect(classes(header)).toContain("flex-wrap");
    expect(classes(header)).not.toContain("h-12");
    expect(classes(screen.getByRole("button", { name: "Open navigation" }))).toContain("size-11");
  });

  it("the sidebar is hidden on narrow screens and the drawer is bounded by the viewport and usable", async () => {
    const { container } = render(<AppShell>content</AppShell>);
    expect(classes(screen.getByLabelText("Sidebar"))).toEqual(expect.arrayContaining(["hidden", "md:flex"]));
    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    const dialog = screen.getByRole("dialog", { name: "Navigation" });
    const panel = dialog.querySelector("nav")!.parentElement!;
    expect(classes(panel)).toEqual(expect.arrayContaining(["max-w-[85vw]", "overflow-y-auto"]));
    expect(classes(dialog)).toContain("md:hidden");
    await expectNoAxeViolations(container);
  });

  it("main content can shrink below its content width", () => {
    render(<AppShell>content</AppShell>);
    expect(classes(document.getElementById("main-content")!)).toContain("min-w-0");
  });

  it("the data table scrolls sideways inside its own container", () => {
    render(<DataTable caption="Rows" columns={[{ key: "a", header: "A", render: (r: string) => r }]} rows={["x"]} rowKey={(r) => r} />);
    expect(classes(screen.getByRole("table").parentElement!)).toContain("overflow-x-auto");
  });

  it("workspace tabs scroll sideways, keep their labels on one line and are tall enough to touch", () => {
    render(
      <Tabs label="Sections" selected="a" onSelect={() => undefined} tabs={[{ id: "a", label: "Overview" }, { id: "b", label: "Distribution" }]}>
        body
      </Tabs>,
    );
    expect(classes(screen.getByRole("tablist"))).toContain("overflow-x-auto");
    for (const tab of screen.getAllByRole("tab")) expect(classes(tab)).toEqual(expect.arrayContaining(["shrink-0", "whitespace-nowrap", "min-h-11"]));
  });

  it("buttons are about 40px on touch widths and compact from md up", () => {
    expect(buttonClasses({ size: "md" })).toMatch(/\bh-10\b.*\bmd:h-9\b/);
    expect(buttonClasses({ size: "sm" })).toMatch(/\bh-9\b.*\bmd:h-8\b/);
  });

  it("the chart is in a focusable, labelled scroll region with a minimum width, so labels stay legible", async () => {
    const block: MetricBlock = {
      type: "metric", id: "m", title: null, label: "Change",
      unit: { label: "NZD per tax year", currency: "NZD", period: "tax_year", basis: "nominal", per: "population" },
      values: [{ option: "A", value: "10", outcome: "calculated" }, { option: "B", value: "20", outcome: "calculated" }],
      precision: "population_estimate", evidence_class: "Model output", context: "", provenance: [],
    };
    render(<MetricCard block={block} />);
    const region = await screen.findByRole("region", { name: "Change (scrollable chart)" });
    expect(region).toHaveAttribute("tabindex", "0");
    expect(classes(region)).toContain("overflow-x-auto");
    expect(region.querySelector("svg")!.getAttribute("class")).toContain("min-w-[36rem]");
  });
});
