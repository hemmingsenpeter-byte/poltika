"use client";

import { type KeyboardEvent, type ReactNode, useRef } from "react";

import { cn } from "@/lib/cn";

export type TabItem = { id: string; label: string; note?: string | undefined };

/** The ARIA tabs pattern with a roving tabindex: arrow keys, Home and End move
 *  focus and selection together. The tab list scrolls sideways on narrow
 *  screens rather than wrapping. */
export function Tabs({
  tabs,
  selected,
  onSelect,
  label,
  children,
}: {
  tabs: readonly TabItem[];
  selected: string;
  onSelect: (id: string) => void;
  label: string;
  children: ReactNode;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const index = tabs.findIndex((t) => t.id === selected);
    let next = index;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = tabs.length - 1;
    else return;
    event.preventDefault();
    const target = tabs[next];
    if (!target) return;
    onSelect(target.id);
    refs.current[target.id]?.focus();
  }

  return (
    <div>
      {/* Focus is on the tab buttons (roving tabindex), not the tablist. */}
      {/* eslint-disable-next-line jsx-a11y/interactive-supports-focus */}
      <div role="tablist" aria-label={label} onKeyDown={onKeyDown} className="flex overflow-x-auto border-b border-border">
        {tabs.map((t) => {
          const active = t.id === selected;
          return (
            <button
              key={t.id}
              ref={(node) => {
                refs.current[t.id] = node;
              }}
              type="button"
              role="tab"
              id={`tab-${t.id}`}
              aria-selected={active}
              aria-controls={`panel-${t.id}`}
              tabIndex={active ? 0 : -1}
              onClick={() => onSelect(t.id)}
              className={cn(
                "shrink-0 border-b-2 px-4 py-2 text-sm whitespace-nowrap",
                active ? "border-accent font-medium text-ink" : "border-transparent text-muted hover:text-ink",
              )}
            >
              {t.label}
            </button>
          );
        })}
      </div>
      <div role="tabpanel" id={`panel-${selected}`} aria-labelledby={`tab-${selected}`} tabIndex={0} className="pt-4">
        {children}
      </div>
    </div>
  );
}
