"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useMeta } from "@/components/layout/MetaProvider";
import { isActive, visibleNavigation } from "@/config/navigation";
import { cn } from "@/lib/cn";

/** `label` differs in the mobile drawer so the two navigation landmarks are
 *  distinguishable (axe: landmark-unique) wherever both are in the DOM. */
export function NavList({ collapsed = false, onNavigate, label = "Primary" }: { collapsed?: boolean; onNavigate?: () => void; label?: string }) {
  const pathname = usePathname();
  const { capabilities } = useMeta();
  const items = visibleNavigation(capabilities);

  return (
    <nav aria-label={label}>
      <ul className="flex flex-col gap-1">
        {items.map((item) => {
          const active = isActive(item, pathname);
          const Icon = item.icon;
          return (
            <li key={item.id}>
              <Link
                href={item.href}
                onClick={onNavigate}
                aria-current={active ? "page" : undefined}
                title={collapsed ? item.label : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-base no-underline md:py-2",
                  // The kōwhai bar marks where you are; aria-current says it.
                  active
                    ? "bg-accent-soft font-semibold text-accent shadow-[inset_3px_0_0_var(--color-highlight)]"
                    : "text-ink hover:bg-surface-muted",
                  collapsed && "justify-center",
                )}
              >
                <Icon aria-hidden="true" className="size-4 shrink-0" />
                <span className={collapsed ? "sr-only" : undefined}>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
