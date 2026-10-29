import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { resolveCapabilities } from "@/config/capabilities";

import { NavList } from "./NavList";

const state = vi.hoisted(() => ({ capabilities: {} as Record<string, boolean> }));
vi.mock("next/navigation", () => ({ usePathname: () => "/models/wff_engine" }));
vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));
vi.mock("@/components/layout/MetaProvider", () => ({
  useMeta: () => ({ meta: { status: "loading" }, capabilities: resolveCapabilities(state.capabilities) }),
}));

describe("NavList", () => {
  it("renders only the enabled items and no text for hidden ones", () => {
    state.capabilities = {};
    const { container } = render(<NavList />);
    expect(screen.getAllByRole("link").map((a) => a.textContent)).toEqual(["Home", "Scenarios", "Models", "Data", "Settings"]);
    for (const hidden of ["Explore", "Evidence", "Assurance", "Admin"]) {
      expect(container).not.toHaveTextContent(hidden);
    }
    expect(screen.getByRole("link", { name: "Models" })).toHaveAttribute("aria-current", "page");
  });

  it("shows an item once its capability is switched on", () => {
    state.capabilities = { evidence_search: true };
    render(<NavList />);
    expect(screen.getByRole("link", { name: "Evidence" })).toHaveAttribute("href", "/evidence");
  });
});
