import { getJson } from "../client";
import { MetaSchema } from "../schemas";
import type { Meta } from "@/domain";

export function getMeta(signal?: AbortSignal): Promise<Meta> {
  return getJson("/api/v1/meta", MetaSchema, signal);
}

/** The supported instruments and parameters now live in registryService. */
export { getRegistry } from "./registryService";
