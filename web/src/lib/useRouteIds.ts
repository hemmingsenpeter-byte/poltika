"use client";

import { usePathname } from "next/navigation";

export type RouteIds = {
  scenarioId?: string;
  runId?: string;
  modelId?: string;
  datasetId?: string;
};

const ID = "[A-Za-z0-9_.-]{1,128}";
const PATTERNS: readonly { re: RegExp; keys: readonly (keyof RouteIds)[] }[] = [
  { re: new RegExp(`^/scenarios/(${ID})/runs/(${ID})$`), keys: ["scenarioId", "runId"] },
  { re: new RegExp(`^/scenarios/(${ID})$`), keys: ["scenarioId"] },
  { re: new RegExp(`^/models/(${ID})$`), keys: ["modelId"] },
  { re: new RegExp(`^/data/(${ID})$`), keys: ["datasetId"] },
];

/** Static export builds each dynamic page once with a placeholder `_` and
 *  FastAPI serves it for any ID (ADR-0023), so params from the router would
 *  all read `_`. The real IDs are in the URL path. */
export function parseRouteIds(pathname: string): RouteIds {
  const clean = pathname.length > 1 ? pathname.replace(/\/+$/, "") : pathname;
  for (const { re, keys } of PATTERNS) {
    const m = re.exec(clean);
    if (!m) continue;
    const ids: RouteIds = {};
    keys.forEach((key, i) => {
      const value = m[i + 1];
      if (value !== undefined) ids[key] = decodeURIComponent(value);
    });
    return ids;
  }
  return {};
}

export function useRouteIds(): RouteIds {
  return parseRouteIds(usePathname());
}
