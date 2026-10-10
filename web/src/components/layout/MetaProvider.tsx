"use client";

import { createContext, useContext, type ReactNode } from "react";

import { getMeta } from "@/api/services/metaService";
import { DEFAULT_CAPABILITIES, resolveCapabilities, type Capabilities } from "@/config/capabilities";
import type { Meta } from "@/domain";
import { useAsync, type AsyncState } from "@/lib/useAsync";

type MetaContextValue = { meta: AsyncState<Meta>; capabilities: Capabilities };

const MetaContext = createContext<MetaContextValue>({
  meta: { status: "loading" },
  capabilities: DEFAULT_CAPABILITIES,
});

/** Loads `/api/v1/meta` once; its `capabilities` override the client defaults. */
export function MetaProvider({ children }: { children: ReactNode }) {
  const meta = useAsync(getMeta, "meta");
  const capabilities = resolveCapabilities(meta.status === "ready" ? meta.data.capabilities : undefined);
  return <MetaContext.Provider value={{ meta, capabilities }}>{children}</MetaContext.Provider>;
}

export function useMeta(): MetaContextValue {
  return useContext(MetaContext);
}
