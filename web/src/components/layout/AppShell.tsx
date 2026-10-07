"use client";

import { Menu, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import Link from "next/link";
import { useState, type ReactNode } from "react";

import { NavList } from "@/components/navigation/NavList";
import { Button } from "@/components/ui/Button";
import { humanise } from "@/lib/labels";

import { MetaProvider, useMeta } from "./MetaProvider";

function PolicyVersions() {
  const { meta } = useMeta();
  if (meta.status !== "ready") return null;
  return (
    <ul aria-label="Policy versions" className="hidden items-center gap-3 text-xs text-muted lg:flex">
      {meta.data.policies.map((p) => (
        <li key={p.policy_id}>
          {humanise(p.policy_id)} <span className="num font-mono">{p.policy_version ?? "unversioned"}</span>
        </li>
      ))}
    </ul>
  );
}

function Header({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="flex h-12 shrink-0 items-center gap-3 border-b border-border bg-surface px-3">
      <Button variant="ghost" size="sm" className="md:hidden" onClick={onMenu} aria-label="Open navigation">
        <Menu aria-hidden="true" className="size-4" />
      </Button>
      <Link href="/" className="font-semibold tracking-[0.18em] text-ink no-underline">
        POLTIKA
      </Link>
      <span className="rounded-sm border border-border-strong bg-surface-muted px-2 py-0.5 text-xs text-ink">
        Pilot · synthetic population
      </span>
      <div className="ml-auto">
        <PolicyVersions />
      </div>
    </header>
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
        <div className="flex min-h-0 flex-1">
          <aside
            aria-label="Sidebar"
            className={`hidden shrink-0 flex-col border-r border-border bg-surface p-2 md:flex ${collapsed ? "w-14" : "w-52"}`}
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

          {drawerOpen ? (
            <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
              <button
                type="button"
                aria-label="Close navigation"
                className="absolute inset-0 bg-ink/40"
                onClick={() => setDrawerOpen(false)}
              />
              <div className="absolute inset-y-0 left-0 w-64 border-r border-border bg-surface p-3 shadow-card">
                <Button variant="ghost" size="sm" onClick={() => setDrawerOpen(false)} aria-label="Close navigation" className="mb-2">
                  <X aria-hidden="true" className="size-4" />
                </Button>
                <NavList onNavigate={() => setDrawerOpen(false)} />
              </div>
            </div>
          ) : null}

          <main id="main-content" tabIndex={-1} className="min-w-0 flex-1 px-4 py-6 md:px-8 outline-none">
            <div className="mx-auto max-w-6xl">{children}</div>
          </main>
        </div>
      </div>
    </MetaProvider>
  );
}
