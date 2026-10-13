/// <reference types="vite/client" />
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MetricCard } from "@/components/blocks/MetricCard";
import { AuditRecord, HorizonStrip, ModelReferences, SourcesList } from "@/components/blocks/OtherBlocks";
import { AppShell } from "@/components/layout/AppShell";
import { DataTable } from "@/components/ui/DataTable";
import { Tabs } from "@/components/ui/Tabs";
import { buttonClasses } from "@/components/ui/Button";
import { DEFAULT_CAPABILITIES } from "@/config/capabilities";
import type { MetricBlock } from "@/domain";
import { ScenariosPage } from "@/features/ScenariosPage";
import { expectNoAxeViolations } from "@/test/axe";
import { BLOCKS } from "@/test/fixtures/workspace";

// jsdom has no layout, so these pin the classes that make the narrow-width
// behaviour (about 360px) rather than measure it. docs/web/FRONTEND.md lists
// what still needs a real browser.
vi.mock("@/api/services/scenarioService", () => ({
  listScenarios: () =>
    Promise.resolve({
      items: [
        {
          scenario_id: "a".repeat(64), kind: "reform", title: "A".repeat(120), description: "",
          runs: 1, created_at: "2026-10-01T00:00:00Z", latest_run_id: null,
        },
      ],
      total: 1,
    }),
}));
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

  it("the data table's scroll region is keyboard-focusable and named (found by axe in a real browser)", () => {
    render(<DataTable caption="Rows" columns={[{ key: "a", header: "A", render: (r: string) => r }]} rows={["x"]} rowKey={(r) => r} />);
    const region = screen.getByRole("region", { name: "Rows (scrollable)" });
    expect(region).toHaveAttribute("tabindex", "0");
    expect(region).toContainElement(screen.getByRole("table"));
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

  it("the horizon strip is a focusable, named scroll region", () => {
    render(
      <HorizonStrip
        block={{ type: "horizon", id: "years", title: "Years", years: [{ label: "2026-27", modelled: true, note: "Modelled." }] }}
      />,
    );
    const region = screen.getByRole("region", { name: "Years (scrollable)" });
    expect(region).toHaveAttribute("tabindex", "0");
    expect(classes(region)).toContain("overflow-x-auto");
  });

  it("a long scenario title wraps instead of widening the list", async () => {
    render(<ScenariosPage />);
    const title = await screen.findByText("A".repeat(120));
    expect(classes(title)).toEqual(expect.arrayContaining(["min-w-0", "break-words"]));
  });

  // WCAG 2.2 SC 2.5.8: targets at least 24 CSS px (class-pinned; jsdom has no layout).
  it("standalone targets are at least 24px: header link, provenance chips, model links", () => {
    render(<AppShell>content</AppShell>);
    expect(classes(screen.getByRole("link", { name: "POLTIKA" }))).toEqual(expect.arrayContaining(["inline-flex", "min-h-[28px]"]));
    const block: MetricBlock = {
      type: "metric", id: "m", title: null, label: "Change",
      unit: { label: "NZD per tax year", currency: "NZD", period: "tax_year", basis: "nominal", per: "population" },
      values: [{ option: "A", value: "10", outcome: "calculated" }],
      precision: "population_estimate", evidence_class: "Model output", context: "",
      provenance: [{ tab: "fiscal", block_id: "fiscal_table" }],
    };
    const { unmount } = render(<MetricCard block={block} />);
    expect(classes(screen.getByRole("button", { name: /Fiscal/ }))).toContain("min-h-[24px]");
    unmount();
    render(<ModelReferences block={{ type: "model_ref", id: "r", title: null, models: [{ id: "wff_engine", name: "WFF engine", version: "0.1.0", label: "spec_validated" }] } as never} />);
    expect(classes(screen.getByRole("link", { name: "WFF engine" }))).toContain("min-h-[24px]");
  });

  it("a source link is at least 24px", () => {
    const sources = BLOCKS.find((b) => b.type === "sources") as Parameters<typeof SourcesList>[0]["block"];
    render(<SourcesList block={sources} />);
    expect(classes(screen.getByRole("link", { name: "IRD Family Tax Credit" }))).toEqual(
      expect.arrayContaining(["inline-flex", "min-h-[24px]"]),
    );
    expect(classes(screen.getByText("Check evidence"))).toContain("min-h-[24px]");
  });

  it("every disclosure summary is at least 24px tall", () => {
    // B0.1.6 real-browser check (13 October 2026): four summaries rendered at
    // 18-19px. Pinned over the source, since most sit behind async state.
    const sources = import.meta.glob("./**/*.tsx", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
    const missing = Object.entries(sources)
      .filter(([file]) => !file.includes(".test.") && !file.startsWith("./test/"))
      .flatMap(([file, text]) => (text.match(/<summary\b(?:=>|[^>])*>/g) ?? []).filter((tag) => !tag.includes("min-h-[24px]")).map((tag) => `${file}: ${tag}`));
    expect(missing).toEqual([]);
  });

  it("an audit note carrying a SHA-256 wraps instead of widening the page", () => {
    const sha = "1aed1c4d".repeat(8);
    render(
      <AuditRecord
        block={{ type: "audit_record", id: "manifest", title: null, fields: [{ label: "Population", value: "synthetic v1", note: `SHA-256 ${sha}` }] } as never}
      />,
    );
    expect(classes(screen.getByText(`SHA-256 ${sha}`))).toContain("break-words");
  });
});
