import { BarChart3, BookCheck, Database, Home, Layers, Search, Settings, ShieldCheck, UserCog, type LucideIcon } from "lucide-react";

import type { Capabilities, CapabilityId } from "./capabilities";

export type NavigationItem = {
  id: string;
  label: string;
  href: string;
  icon: LucideIcon;
  /** The item appears only when this capability is on. */
  capability?: CapabilityId;
};

/** Declarative navigation. Future items are declared now and stay hidden,
 *  rendering no text at all, until their capability is switched on. */
export const NAVIGATION: readonly NavigationItem[] = [
  { id: "home", label: "Home", href: "/", icon: Home },
  { id: "scenarios", label: "Scenarios", href: "/scenarios", icon: Layers },
  { id: "models", label: "Models", href: "/models", icon: BookCheck },
  { id: "data", label: "Data", href: "/data", icon: Database },
  { id: "settings", label: "Settings", href: "/settings", icon: Settings },
  { id: "explore", label: "Explore", href: "/explore", icon: BarChart3, capability: "outcome_explorer" },
  { id: "evidence", label: "Evidence", href: "/evidence", icon: Search, capability: "evidence_search" },
  { id: "assurance", label: "Assurance", href: "/assurance", icon: ShieldCheck, capability: "assurance_dashboard" },
  { id: "admin", label: "Admin", href: "/admin", icon: UserCog, capability: "collaboration" },
];

export function visibleNavigation(
  capabilities: Capabilities,
  items: readonly NavigationItem[] = NAVIGATION,
): NavigationItem[] {
  return items.filter((item) => item.capability === undefined || capabilities[item.capability]);
}

/** True when `pathname` is the item's page or beneath it. */
export function isActive(item: NavigationItem, pathname: string): boolean {
  if (item.href === "/") return pathname === "/";
  return pathname === item.href || pathname.startsWith(`${item.href}/`);
}
