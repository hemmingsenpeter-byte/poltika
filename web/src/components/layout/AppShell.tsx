"use client";

import { Menu, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { NavList } from "@/components/navigation/NavList";
import { Button } from "@/components/ui/Button";

import { MetaProvider } from "./MetaProvider";

function Header({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="on-chrome flex min-h-14 shrink-0 flex-wrap items-center gap-x-4 gap-y-1 bg-chrome px-3 py-2 text-chrome-text md:px-6">
      <Button
        variant="ghost"
        size="sm"
        className="size-11 text-chrome-text hover:bg-white/10 md:hidden"
        onClick={onMenu}
        aria-label="Open navigation"
      >
        <Menu aria-hidden="true" className="size-5" />
      </Button>
      <Link
        href="/"
        className="inline-flex min-h-[28px] items-center font-display text-[1.375rem] leading-none font-semibold tracking-tight text-chrome-text no-underline"
      >
        Poltika
      </Link>
      <span className="rounded-sm border border-highlight px-2 py-0.5 text-xs font-semibold text-chrome-text">
        Pilot on a synthetic population
      </span>
    </header>
  );
}

// PETE_QUEUE Q20 (1), docs/pilot/HOSTING.md: the pilot has one shared login
// and no per-user ownership, so every visitor is told what may be entered.
export const DATA_NOTICE =
  "Shared pilot: enter synthetic or public non-personal data only. Anyone with the pilot login can see every stored scenario.";

function DataNotice() {
  return (
    <p className="shrink-0 border-b border-highlight/50 bg-highlight-soft px-3 py-1.5 text-sm text-ink md:px-6">{DATA_NOTICE}</p>
  );
}

const FOCUSABLE = "a[href], button:not([disabled])";

// Modal behaviour for the mobile drawer: focus moves in, Tab stays inside, Escape
// closes, and focus returns to whatever opened it (the menu button).
function NavDrawer({ onClose }: { onClose: () => void }) {
  const panel = useRef<HTMLDivElement>(null);
  const close = useRef(onClose);
  close.current = onClose;

  useEffect(() => {
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    panel.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus();
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        close.current();
        return;
      }
      if (e.key !== "Tab" || !panel.current) return;
      const items = Array.from(panel.current.querySelectorAll<HTMLElement>(FOCUSABLE));
      const first = items[0];
      const last = items[items.length - 1];
      if (!first || !last) return;
      if (!panel.current.contains(document.activeElement)) {
        e.preventDefault();
        first.focus();
      } else if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    // The dialog is md:hidden. Past the md breakpoint it is no longer a modal,
    // so close it rather than keep trapping Tab in a hidden panel.
    const wide = window.matchMedia?.("(min-width: 768px)");
    function onWide(e: MediaQueryListEvent) {
      if (e.matches) close.current();
    }
    wide?.addEventListener("change", onWide);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      wide?.removeEventListener("change", onWide);
      opener?.focus();
    };
  }, []);

  return (
    <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
      <button type="button" aria-label="Close navigation" tabIndex={-1} className="absolute inset-0 bg-ink/40" onClick={onClose} />
      <div ref={panel} className="absolute inset-y-0 left-0 w-64 max-w-[85vw] overflow-y-auto border-r border-border bg-surface p-3 shadow-overlay">
        <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close navigation" className="mb-2 size-11">
          <X aria-hidden="true" className="size-4" />
        </Button>
        <NavList onNavigate={onClose} label="Primary menu" />
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <MetaProvider>
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>
      <div className="flex min-h-screen flex-col">
        <Header onMenu={() => setDrawerOpen(true)} />
        <DataNotice />
        <div className="flex min-h-0 flex-1">
          <aside
            aria-label="Sidebar"
            className={`hidden shrink-0 flex-col border-r border-border bg-surface px-2 py-4 md:flex ${collapsed ? "w-16" : "w-56"}`}
          >
            <NavList collapsed={collapsed} />
            <Button
              variant="ghost"
              size="sm"
              className="mt-auto"
              onClick={() => setCollapsed((c) => !c)}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              aria-expanded={!collapsed}
            >
              {collapsed ? (
                <PanelLeftOpen aria-hidden="true" className="size-4" />
              ) : (
                <>
                  <PanelLeftClose aria-hidden="true" className="size-4" />
                  <span>Collapse</span>
                </>
              )}
            </Button>
          </aside>

          {drawerOpen ? <NavDrawer onClose={() => setDrawerOpen(false)} /> : null}

          <main id="main-content" tabIndex={-1} className="min-w-0 flex-1 px-4 py-8 md:px-10 md:py-10 outline-none">
            <div className="mx-auto max-w-6xl">{children}</div>
          </main>
        </div>
      </div>
    </MetaProvider>
  );
}
