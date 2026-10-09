import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DEFAULT_CAPABILITIES } from "@/config/capabilities";

import { AppShell } from "./AppShell";

vi.mock("next/navigation", () => ({ usePathname: () => "/" }));
vi.mock("./MetaProvider", () => ({
  MetaProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useMeta: () => ({ meta: { status: "loading" }, capabilities: DEFAULT_CAPABILITIES }),
}));

function open() {
  render(<AppShell>content</AppShell>);
  const menu = screen.getByRole("button", { name: "Open navigation" });
  menu.focus();
  fireEvent.click(menu);
  return menu;
}

describe("AppShell mobile navigation drawer", () => {
  it("moves focus into the dialog when it opens", () => {
    open();
    const dialog = screen.getByRole("dialog", { name: "Navigation" });
    expect(dialog.contains(document.activeElement)).toBe(true);
  });

  it("closes on Escape and returns focus to the menu button", () => {
    const menu = open();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(menu);
  });

  it("keeps Tab and Shift+Tab inside the dialog", () => {
    open();
    const dialog = screen.getByRole("dialog", { name: "Navigation" });
    const items = Array.from(dialog.querySelectorAll<HTMLElement>("a[href], button:not([disabled])")).filter((e) => e.tabIndex >= 0);
    items[items.length - 1]!.focus();
    fireEvent.keyDown(document, { key: "Tab" });
    expect(document.activeElement).toBe(items[0]);
    fireEvent.keyDown(document, { key: "Tab", shiftKey: true });
    expect(document.activeElement).toBe(items[items.length - 1]);
  });
});
