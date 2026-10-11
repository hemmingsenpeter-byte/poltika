"use client";

import { useSyncExternalStore } from "react";

const subscribe = () => () => undefined;

/** False while rendering the exported HTML and during hydration, true after.
 *  Text built from the real URL ids is shown only once mounted, because the
 *  export was built with the placeholder id `_` (ADR-0023). */
export function useMounted(): boolean {
  return useSyncExternalStore(subscribe, () => true, () => false);
}
